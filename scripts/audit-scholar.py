"""Audit publication metadata; run `uv run scripts/audit-scholar.py`.

Writes scripts/scholar-audit.md and /tmp/rodighiero-scholar-audit.json.
Use --site-dir _site --strict for an offline pre-deployment check.
Checks crawlability and metadata, not inclusion in Scholar's private index.

Every finding carries one of four categories, so the report never mixes them:
  scholar     a requirement Google Scholar's inclusion guidelines actually state
  source      the rendered page disagrees with its own _publications/ front matter
  convention  a citation-export convention this site keeps (citation_abstract,
              citation_editor, the search description), not a Scholar requirement
  note        editorial and advisory; never fails --strict
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlparse
from urllib.robotparser import RobotFileParser
import collections
from datetime import datetime
import json
import re
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = yaml.safe_load((ROOT / '_config.yml').read_text())['url']
TYPES = yaml.safe_load((ROOT / '_data/publication_types.yml').read_text())
CATEGORIES = ('scholar', 'source', 'convention', 'note')
# Below this many visible words outside the abstract, a full-text claim is not credible.
FULLTEXT_MIN_WORDS = 100

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'source', 'track', 'wbr'}
HIDING_CLASSES = {'hidden', 'visually-hidden', 'sr-only', 'screen-reader-text'}


class Page(HTMLParser):
    """Collects the tags the audit reads, plus text split by where it sits.

    Hiding is judged from markup alone: the `hidden` attribute, aria-hidden="true",
    an inline display:none / visibility:hidden, a hiding utility class, <template>
    or <noscript>, and the body of a closed <details>. Stylesheets and scripts are
    not evaluated, so 'not hidden' here means 'not hidden by markup', nothing more.
    """

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.meta = collections.defaultdict(list)
        self.links = []
        self.canonical = []
        self.alternates = {}
        self.h1 = []
        self.stack = []
        self.abstract_seen = False
        self.abstract_hidden = False
        self.body_seen = False
        self.body_hidden = False
        self.abstract_text = []   # everything inside div.abstract
        self.body_visible = []    # visible text anywhere inside div.body
        self.rest_visible = []    # visible text inside div.body but outside div.abstract
        self.feed(text)

    def _top(self):
        return self.stack[-1] if self.stack else {'hidden': False, 'abstract': False,
                                                  'body': False, 'h1': False, 'closed_details': False}

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else '') for k, v in attrs}
        if tag == 'meta':
            self.meta[a.get('name', '').lower()].append(a.get('content', ''))
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang'):
            self.alternates[a['hreflang']] = a.get('href')
        if tag in VOID:
            return
        parent = self._top()
        classes = set(a.get('class', '').split())
        style = a.get('style', '').replace(' ', '').lower()
        own_hidden = ('hidden' in a or a.get('aria-hidden', '').lower() == 'true'
                      or 'display:none' in style or 'visibility:hidden' in style
                      or bool(classes & HIDING_CLASSES) or tag in {'template', 'noscript'}
                      or (parent['closed_details'] and tag != 'summary'))
        hidden = parent['hidden'] or own_hidden
        is_abstract = tag == 'div' and 'abstract' in classes and not parent['abstract']
        is_body = tag == 'div' and 'body' in classes and not parent['body']
        if is_abstract:
            self.abstract_seen, self.abstract_hidden = True, hidden
        if is_body:
            self.body_seen, self.body_hidden = True, hidden
        self.stack.append({'tag': tag, 'hidden': hidden,
                           'abstract': parent['abstract'] or is_abstract,
                           'body': parent['body'] or is_body,
                           'h1': parent['h1'] or tag == 'h1',
                           'closed_details': tag == 'details' and 'open' not in a})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1]['tag'] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        # Pop back to the matching element; a stray end tag with no match is ignored.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                return

    def handle_data(self, text):
        top = self._top()
        visible = not (top['hidden'] or top['closed_details'])
        if top['h1']:
            self.h1.append(text)
        if top['abstract']:
            self.abstract_text.append(text)
        if top['body'] and visible:
            self.body_visible.append(text)
            if not top['abstract']:
                self.rest_visible.append(text)


def names(front, role):
    return [name.strip() for name in (front.get(role) or '').split(' and ') if name.strip()]


def page_range(pages):
    """The Python twin of publication_decoder.rb's `page_range` filter."""
    parts = [part.strip() for part in re.split(r'[-–—]', str(pages))]
    first, last = parts[0], parts[-1]
    if len(parts) < 2:
        return [first]
    if len(last) < len(first):
        last = first[:len(first) - len(last)] + last
    return [first, last]


def people(node):
    """Names from a JSON-LD person-valued property: one node or a list of them."""
    if not node:
        return []
    nodes = node if isinstance(node, list) else [node]
    return [n.get('name', '') if isinstance(n, dict) else str(n) for n in nodes]


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def load(url, site_dir=None):
    if site_dir is None:
        return fetch(url)
    path = unquote(urlparse(url).path).lstrip('/')
    candidates = [site_dir / path] if path else [site_dir / 'index.html']
    if path and not Path(path).suffix:
        candidates += [site_dir / (path + '.html'), site_dir / path / 'index.html']
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve().is_relative_to(site_dir.resolve()):
            body = candidate.read_bytes()
            return {'status': 200, 'url': url, 'headers': {},
                    'text': body.decode('utf-8'), 'bytes': len(body)}
    return {'status': 404, 'url': url, 'error': 'Missing from local build'}


def fetch(url):
    try:
        with urlopen(Request(url, headers={'User-Agent': 'RodighieroMetadataAudit/1.0'}), timeout=25) as r:
            body = r.read(6_000_000)
            return {'status': r.status, 'url': r.url, 'headers': {k.lower(): v for k, v in r.headers.items()},
                    'text': body.decode('utf-8', errors='replace'), 'bytes': len(body)}
    except HTTPError as e:
        return {'status': e.code, 'url': url, 'error': str(e)}
    except Exception as e:
        return {'status': None, 'url': url, 'error': str(e)}


def translation_sets(publications):
    """Expected hreflang map per slug, derived from translation_of alone.

    A set is an original plus every entry whose translation_of names it. Each member
    lists every member by language plus x-default on the original; an entry outside
    any set lists no alternates at all.
    """
    groups = collections.defaultdict(list)
    for slug, front in publications:
        groups[front.get('translation_of') or slug].append((slug, front))
    expected = {}
    for root, members in groups.items():
        if len(members) < 2:
            continue
        alternates = {front.get('lang', 'en'): f'{BASE}/{slug}' for slug, front in members}
        alternates['x-default'] = f'{BASE}/{root}'
        for slug, _ in members:
            expected[slug] = alternates
    return expected


def audit(item, site_dir=None, expected_alternates=None):
    slug, front, body_source = item
    url = BASE + '/' + slug
    lang = front.get('lang', 'en')
    result = load(url, site_dir)
    row = {'slug': slug, 'title': front['title'], 'type': front['type'],
           'url': url, 'status': result['status'], 'findings': []}

    def finding(category, message):
        row['findings'].append((category, message))

    if result['status'] != 200:
        finding('scholar', 'Publication unavailable: ' + result.get('error', 'unexpected status'))
        return row
    p = Page(result['text'])
    row['citation'] = {k: v for k, v in p.meta.items() if k.startswith('citation_')}
    row['bytes'] = result['bytes']

    # Scholar's required tags: title, at least one author, a publication date.
    if not p.meta['citation_title']:
        finding('scholar', 'Missing citation_title')
    elif p.meta['citation_title'] != [front['title']]:
        finding('source', 'citation_title differs from publication source')
    if names(front, 'author'):
        if not p.meta['citation_author']:
            finding('scholar', 'Missing citation_author')
        elif p.meta['citation_author'] != names(front, 'author'):
            finding('source', 'citation_author differs from publication source')
    else:
        finding('note', 'Editor-only work: no actual author supplied for Scholar')
    if front['year'] == 'Forthcoming':
        finding('note', 'Forthcoming: no publication year supplied')
        if p.meta['citation_publication_date']:
            finding('source', 'Forthcoming entry claims a publication date')
    elif not p.meta['citation_publication_date']:
        finding('scholar', 'Missing citation_publication_date')
    elif p.meta['citation_publication_date'] != [str(front['year'])]:
        finding('source', 'citation_publication_date differs from publication source')
    if p.meta['citation_editor'] != names(front, 'editor'):
        finding('convention', 'citation_editor differs from publication source')

    if p.canonical != [url]:
        finding('source', 'Unexpected canonical URL')
    if normalize(''.join(p.h1)) != front['title']:
        finding('source', 'Visible title differs from source')
    if len(p.meta['description']) != 1 or not p.meta['description'][0].strip():
        finding('convention', 'Missing or duplicate search description')
    if p.meta['citation_abstract_html_url'] != [url]:
        finding('source', 'Abstract URL does not match canonical URL')

    venue_tag = TYPES[front['type']].get('citation_venue')
    expected_fields = {venue_tag: front['venue']} if venue_tag else {}
    expected_fields.update({'citation_' + field: front[field]
                            for field in ('volume', 'issue', 'issn', 'isbn') if front.get(field) is not None})
    for field, expected in expected_fields.items():
        if p.meta[field] != [str(expected)]:
            finding('source', f'{field} differs from publication source')

    # Pagination: both tags must be exactly what the source range expands to.
    if front.get('pages'):
        pages = page_range(front['pages'])
        if p.meta['citation_firstpage'] != pages[:1]:
            finding('source', f'citation_firstpage is {p.meta["citation_firstpage"] or "missing"}, source gives {pages[0]}')
        if len(pages) > 1 and p.meta['citation_lastpage'] != pages[1:]:
            finding('source', f'citation_lastpage is {p.meta["citation_lastpage"] or "missing"}, source gives {pages[1]}')
        if len(pages) == 1 and p.meta['citation_lastpage']:
            finding('source', 'citation_lastpage present for a single-page source')
    elif p.meta['citation_firstpage'] or p.meta['citation_lastpage']:
        finding('source', 'Page tags present but the source has no pages')

    # Language alternates: the exact set translation_of implies, no more, no fewer.
    want = (expected_alternates or {}).get(slug, {})
    if p.alternates != want:
        missing = sorted(set(want) - set(p.alternates))
        extra = sorted(set(p.alternates) - set(want))
        wrong = sorted(k for k in set(want) & set(p.alternates) if want[k] != p.alternates[k])
        detail = '; '.join(part for part in [
            missing and 'missing ' + ', '.join(missing),
            extra and 'unexpected ' + ', '.join(extra),
            wrong and 'wrong URL for ' + ', '.join(wrong)] if part)
        finding('source', 'hreflang alternates differ from the translation set: ' + detail)

    directives = ' '.join(p.meta['robots'] + p.meta['googlebot']) + ' ' + result['headers'].get('x-robots-tag', '')
    if re.search(r'\b(noindex|none)\b', directives, re.I):
        finding('scholar', 'Indexing blocked by robots directive')
    if result['bytes'] > 5_000_000:
        finding('scholar', 'Page exceeds Scholar’s 5 MB limit')

    # The abstract has to be on the page, readable without interaction.
    visible = normalize(''.join(p.body_visible))
    lead = normalize(''.join(p.abstract_text))
    if not p.body_seen or not visible:
        finding('scholar', 'No visible server-rendered text in publication body')
    if p.body_hidden:
        finding('scholar', 'Publication body is hidden in markup')
    if p.abstract_hidden:
        finding('scholar', 'Abstract is hidden in markup')

    scripts = re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', result['text'], re.S)
    try:
        work = json.loads(scripts[0])
        for script in scripts[1:]:
            json.loads(script)
    except (ValueError, IndexError):
        finding('source', 'Invalid or missing work JSON-LD')
        work = None
    if work is not None:
        abstract = work.get('abstract', '')
        row['abstract_chars'] = len(abstract)
        if not abstract.strip():
            finding('scholar', 'No text abstract/lead available')
        if lead and normalize(abstract) != lead:
            finding('source', 'Structured abstract differs from visible abstract')
        if p.meta['citation_abstract'] != [abstract]:
            finding('convention', 'citation_abstract differs from the complete structured abstract')
        if abstract and normalize(abstract) not in visible:
            finding('scholar', 'Abstract is not visible in the server-rendered body')
        if '{%' in abstract or '{{' in abstract:
            finding('source', 'Unrendered template code in abstract')
        # The work node must describe this page's own work.
        schema = TYPES[front['type']].get('schema', 'ScholarlyArticle')
        checks = [('@type', work.get('@type'), schema),
                  ('@id', work.get('@id'), url),
                  ('url', work.get('url'), url),
                  ('headline', work.get('headline'), front['title']),
                  ('name', work.get('name'), front['title']),
                  ('inLanguage', work.get('inLanguage'), lang),
                  ('author', people(work.get('author')), names(front, 'author')),
                  ('editor', people(work.get('editor')), names(front, 'editor')),
                  ('datePublished', work.get('datePublished'),
                   None if front['year'] == 'Forthcoming' else str(front['year'])),
                  ('sameAs', work.get('sameAs'), front.get('doi')),
                  ('pagination', work.get('pagination'),
                   str(front['pages']) if front.get('pages') else None)]
        if front.get('translation_of'):
            checks.append(('translationOfWork', (work.get('translationOfWork') or {}).get('@id'),
                           f'{BASE}/{front["translation_of"]}'))
        for field, got, expected in checks:
            if got != expected:
                finding('source', f'JSON-LD {field} differs from publication source')

    # Full text: the claim must follow the source, and the page must carry the text.
    claims = bool(p.meta['citation_fulltext_html_url'])
    row['fulltext_html'] = claims
    should_claim = '<!--more-->' in body_source and front.get('fulltext') is not False
    if claims != should_claim:
        finding('source', 'citation_fulltext_html_url ' + ('present' if claims else 'absent')
                + ' against the source (<!--more--> and fulltext flag)')
    if claims:
        if p.meta['citation_fulltext_html_url'] != [url]:
            finding('scholar', 'citation_fulltext_html_url does not point at this page')
        rest_words = len(normalize(''.join(p.rest_visible)).split())
        row['fulltext_words'] = rest_words
        if not lead:
            finding('scholar', 'Full-text claim without a separate abstract')
        if rest_words < FULLTEXT_MIN_WORDS:
            finding('scholar', f'Full-text claim but only {rest_words} visible words follow the abstract')

    for doi in p.meta['citation_doi']:
        if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            finding('source', 'Invalid citation DOI')
    expected_doi = re.fullmatch(r'https?://(?:dx\.)?doi.org/(10\..+)', front.get('doi') or '')
    if p.meta['citation_doi'] != ([expected_doi[1]] if expected_doi else []):
        finding('source', 'citation_doi differs from publication source')
    for pdf in p.meta['citation_pdf_url']:
        parsed = urlparse(pdf)
        directory = urlparse(url).path.rsplit('/', 1)[0] + '/'
        if (parsed.scheme not in {'http', 'https'} or parsed.netloc != urlparse(url).netloc
                or not parsed.path.startswith(directory)):
            finding('scholar', 'citation_pdf_url is not an absolute URL in the abstract’s own directory')
    row['pdf_tags'] = p.meta['citation_pdf_url']
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--site-dir', type=Path, help='Audit a Jekyll build without network requests')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero on any scholar, source or convention finding (notes stay advisory)')
    parser.add_argument('--report', type=Path, help='Markdown report destination')
    parser.add_argument('--snapshot', type=Path, help='Detailed JSON snapshot destination')
    args = parser.parse_args()
    report = args.report or (Path('/tmp/rodighiero-scholar-build-audit.md') if args.site_dir else ROOT / 'scripts/scholar-audit.md')
    snapshot = args.snapshot or Path('/tmp/rodighiero-scholar-build-audit.json' if args.site_dir else '/tmp/rodighiero-scholar-audit.json')
    publications = []
    for path in sorted((ROOT / '_publications').glob('*.md')):
        _, front_text, body = path.read_text().split('---', 2)
        publications.append((path.stem, yaml.safe_load(front_text), body))
    expected_alternates = translation_sets([(slug, front) for slug, front, _ in publications])
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item: audit(item, args.site_dir, expected_alternates), publications))
    shared = {path: load(BASE + path, args.site_dir) for path in ['/', '/robots.txt', '/sitemap.xml']}
    homepage = Page(shared['/'].get('text', ''))
    home_links = {urljoin(BASE + '/', u).rstrip('/') for u in homepage.links}
    sitemap_urls = set()
    try:
        sitemap = ET.fromstring(shared['/sitemap.xml'].get('text', ''))
        sitemap_urls = {e.text for e in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    except ET.ParseError:
        pass
    robots = RobotFileParser()
    robots.parse(shared['/robots.txt'].get('text', '').splitlines())
    shared_errors = [f'{path}: HTTP {r["status"]}' for path, r in shared.items() if r['status'] != 200]
    if not sitemap_urls:
        shared_errors.append('Missing or invalid sitemap')
    if BASE + '/' not in sitemap_urls:
        shared_errors.append('Homepage absent from sitemap')
    if homepage.canonical != [BASE + '/']:
        shared_errors.append('Homepage canonical URL is incorrect')
    if re.search(r'\b(noindex|none)\b', ' '.join(homepage.meta['robots'] + homepage.meta['googlebot']), re.I):
        shared_errors.append('Homepage blocks indexing')
    if not robots.can_fetch('Googlebot', BASE + '/'):
        shared_errors.append('robots.txt blocks homepage discovery')
    for row in rows:
        if row['url'] not in home_links:
            row['findings'].append(('scholar', 'No direct HTML link from homepage'))
        if row['url'] not in sitemap_urls:
            row['findings'].append(('source', 'Missing from sitemap'))
        if not robots.can_fetch('Googlebot', row['url']):
            row['findings'].append(('scholar', 'robots.txt blocks Googlebot'))
        row['errors'] = [f for f in row['findings'] if f[0] != 'note']
    data = {'base': BASE, 'pages': rows, 'shared': {p: {k: v for k, v in r.items() if k != 'text'} for p, r in shared.items()},
            'robots': shared['/robots.txt'].get('text', ''), 'shared_errors': shared_errors}
    snapshot.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    counts = collections.Counter(category for row in rows for category, _ in row['findings'])
    checked = datetime.now().astimezone().strftime('%-d %B %Y')
    scope = f'local build `{args.site_dir}`' if args.site_dir else 'live pages'
    available = sum(r['status'] == 200 for r in rows)
    availability = (f'Found {available} of {len(rows)} publication HTML files in the build.' if args.site_dir
                    else f'Checked {len(rows)} publication URLs. {available} returned HTTP 200.')
    lines = ['# Google Scholar technical audit', '', f'Checked {scope} on {checked}.', '',
             '**Scholar index membership remains unverified.** This script checks technical readiness; it does not query Scholar’s index. Ordinary web-search results are not evidence of Scholar inclusion.', '',
             'Guidance: https://scholar.google.com/intl/en/scholar/inclusion.html', '',
             availability,
             f'{sum(r.get("fulltext_html", False) for r in rows)} advertise HTML full text; {sum(bool(r.get("pdf_tags")) for r in rows)} advertise a local PDF.', '',
             'Findings by category: ' + ', '.join(f'{c} {counts[c]}' for c in CATEGORIES) + '.', '',
             '## Page checks', '', '| Publication | Status | Abstract characters | Findings |', '| --- | --- | --- | --- |']
    for row in rows:
        status = ('Present' if row['status'] == 200 else 'Missing') if args.site_dir else f'HTTP {row["status"]}'
        text = '; '.join(f'**{c}**: {m}' for c, m in row['findings']) or 'No findings'
        lines.append(f'| [{row["title"]}]({row["url"]}) | {status} | {row.get("abstract_chars", "—")} | {text} |')
    lines += ['', '## Shared endpoints', '']
    lines += [f'- `{p}`: ' + (('present' if r['status'] == 200 else 'missing') if args.site_dir else f'HTTP {r["status"]}') for p, r in shared.items()]
    lines += [f'- ERROR: {error}' for error in shared_errors]
    lines += ['', '```text', data['robots'].strip(), '```', '',
              '## Interpretation', '',
              '- **scholar** findings break a requirement Scholar’s inclusion guidelines state: the citation_title, citation_author and citation_publication_date tags, an abstract visible on the page, a full-text claim backed by text on the page, the 5 MB limit, the PDF-directory rule, and crawlability.',
              '- **source** findings mean the page disagrees with its own `_publications/` front matter: venue, volume, issue, ISSN, ISBN, pages, DOI, the hreflang set implied by `translation_of`, and the work JSON-LD (type, id, headline, language, people, date, sameAs, pagination, translationOfWork).',
              '- **convention** findings concern tags this site emits for citation export (Zotero and others): `citation_abstract`, `citation_editor`, the search description. Scholar does not require them.',
              '- **note** findings are editorial and never fail `--strict`.',
              f'- “No findings” is not proof of visibility or completeness. Hiding is judged from markup only (the `hidden` attribute, `aria-hidden`, inline `display:none`, hiding classes, closed `<details>`, `<template>`, `<noscript>`); stylesheets and scripts are not evaluated. A full-text claim needs {FULLTEXT_MIN_WORDS}+ visible words after the abstract, which shows that text exists, not that the work is complete; the `fulltext: false` flag records that judgment.',
              '- An external publisher or repository PDF is not suitable for this domain’s `citation_pdf_url`: Scholar requires the linked PDF in the same subdirectory as the abstract page. HTML full text can remain indexable without a local PDF.',
              '- Do not infer “not indexed” from inaccessible Scholar results or from missing ordinary search results.', '']
    lines += ['See [publisher and PDF review](scholar-review.md) for verified corrections and source conflicts.', '']
    report.write_text('\n'.join(lines))
    error_count = len(shared_errors) + sum(len(r.get('errors', r['findings'])) for r in rows)
    print(f'Audited {len(rows)} publication URLs; {error_count} errors '
          f'(scholar {counts["scholar"]}, source {counts["source"]}, convention {counts["convention"]}); '
          f'{counts["note"]} notes. Report: {report}')
    for error in shared_errors:
        print('ERROR: ' + error)
    for r in rows:
        if r['findings']:
            print(r['slug'] + ': ' + '; '.join(f'[{c}] {m}' for c, m in r['findings']))
    if args.strict and error_count:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
