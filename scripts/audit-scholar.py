"""Audit publication metadata; run `uv run scripts/audit-scholar.py`.

Writes scripts/scholar-audit.md and /tmp/rodighiero-scholar-audit.json.
Use --site-dir _site --strict for an offline pre-deployment check.
Checks crawlability and metadata, not inclusion in Scholar's private index.
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


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.meta = collections.defaultdict(list)
        self.links = []
        self.canonical = []
        self.h1 = []
        self.in_h1 = False
        self.body_depth = 0
        self.body_text = []
        self.abstract_depth = 0
        self.abstract_text = []
        self.alternates = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            self.meta[a.get('name', '').lower()].append(a.get('content', ''))
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang'):
            self.alternates[a['hreflang']] = a.get('href')
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'div':
            if self.abstract_depth:
                self.abstract_depth += 1
            elif 'abstract' in a.get('class', '').split():
                self.abstract_depth = 1
            if self.body_depth:
                self.body_depth += 1
            elif 'body' in a.get('class', '').split():
                self.body_depth = 1

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'div' and self.body_depth:
            self.body_depth -= 1
        if tag == 'div' and self.abstract_depth:
            self.abstract_depth -= 1

    def handle_data(self, text):
        if self.in_h1:
            self.h1.append(text)
        if self.body_depth:
            self.body_text.append(text)
        if self.abstract_depth:
            self.abstract_text.append(text)


def names(front, role):
    return [name.strip() for name in front.get(role, '').split(' and ') if name.strip()]


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


def audit(item, site_dir=None):
    slug, front = item
    url = BASE + '/' + slug
    result = load(url, site_dir)
    row = {'slug': slug, 'title': front['title'], 'type': front['type'],
           'url': url, 'status': result['status'], 'findings': []}
    if result['status'] != 200:
        row['findings'].append('Publication unavailable: ' + result.get('error', 'unexpected status'))
        return row
    p = Page(result['text'])
    row['citation'] = {k: v for k, v in p.meta.items() if k.startswith('citation_')}
    row['bytes'] = result['bytes']
    for field, expected in [('citation_title', [front['title']]),
                            ('citation_author', names(front, 'author')),
                            ('citation_editor', names(front, 'editor'))]:
        if p.meta[field] != expected:
            row['findings'].append(f'{field} differs from publication source')
    if front['year'] != 'Forthcoming' and p.meta['citation_publication_date'] != [str(front['year'])]:
        row['findings'].append('Missing or inconsistent publication year')
    if front['year'] == 'Forthcoming':
        row['findings'].append('Forthcoming: no publication year supplied')
        if p.meta['citation_publication_date']:
            row['findings'].append('Forthcoming entry claims a publication date')
    if not names(front, 'author'):
        row['findings'].append('Editor-only work: no actual author supplied for Scholar')
    if front['type'] in {'map', 'magazine', 'interview'}:
        row['findings'].append('Editorial review: scholarly eligibility is not established by publication type')
    if p.canonical != [url]:
        row['findings'].append('Unexpected canonical URL')
    if ''.join(p.h1).strip() != front['title']:
        row['findings'].append('Visible title differs from source')
    if len(p.meta['description']) != 1 or not p.meta['description'][0].strip():
        row['findings'].append('Missing or duplicate search description')
    if p.meta['citation_abstract_html_url'] != [url]:
        row['findings'].append('Abstract URL does not match canonical URL')
    venue_tag = TYPES[front['type']].get('citation_venue')
    expected_fields = {venue_tag: front['venue']} if venue_tag else {}
    expected_fields.update({'citation_' + field: front[field]
                            for field in ('volume', 'issue', 'issn', 'isbn') if front.get(field) is not None})
    for field, expected in expected_fields.items():
        if p.meta[field] != [str(expected)]:
            row['findings'].append(f'{field} differs from publication source')
    if front.get('pages'):
        if not p.meta['citation_firstpage']:
            row['findings'].append('Page range lacks citation_firstpage')
        elif p.meta['citation_lastpage']:
            first, last = p.meta['citation_firstpage'][0], p.meta['citation_lastpage'][0]
            if first.isdigit() and last.isdigit() and int(last) < int(first):
                row['findings'].append('Citation page range runs backwards')
    if p.alternates and p.alternates.get(front.get('lang', 'en')) != url:
        row['findings'].append('Translation alternates omit the page itself')
    directives = ' '.join(p.meta['robots'] + p.meta['googlebot']) + ' ' + result['headers'].get('x-robots-tag', '')
    if re.search(r'\b(noindex|none)\b', directives, re.I):
        row['findings'].append('Indexing blocked by robots directive')
    scripts = re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', result['text'], re.S)
    try:
        work = json.loads(scripts[0])
        for script in scripts[1:]:
            json.loads(script)
        abstract = work.get('abstract', '')
        row['abstract_chars'] = len(abstract)
        if not abstract.strip():
            row['findings'].append('No text abstract/lead available')
        visible = re.sub(r'\s+', ' ', ''.join(p.body_text)).strip()
        if not visible:
            row['findings'].append('No server-rendered text in publication body')
        normalize = lambda text: re.sub(r'\s+', ' ', text).strip()
        lead = normalize(''.join(p.abstract_text))
        if lead and normalize(abstract) != lead:
            row['findings'].append('Structured abstract differs from visible abstract')
        if p.meta['citation_abstract'] != [abstract]:
            row['findings'].append('Citation abstract differs from complete structured abstract')
        if abstract and normalize(abstract) not in visible:
            row['findings'].append('Abstract is not present in server-rendered body')
        if result['bytes'] > 5_000_000:
            row['findings'].append('Page exceeds Scholar’s 5 MB limit')
        if '{%' in abstract or '{{' in abstract:
            row['findings'].append('Unrendered template code in abstract')
        row['fulltext_html'] = bool(p.meta['citation_fulltext_html_url'])
        if p.meta['citation_fulltext_html_url'] and (p.meta['citation_fulltext_html_url'] != [url] or not lead):
            row['findings'].append('HTML full-text claim lacks a matching URL and separate abstract')
    except (ValueError, IndexError):
        row['findings'].append('Invalid or missing work JSON-LD')
    for doi in p.meta['citation_doi']:
        if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            row['findings'].append('Invalid citation DOI')
    expected_doi = re.fullmatch(r'https?://(?:dx\.)?doi.org/(10\..+)', front.get('doi', ''))
    if expected_doi and not front.get('translation_of') and p.meta['citation_doi'] != [expected_doi[1]]:
        row['findings'].append('Live citation DOI differs from current source (deployment may be pending)')
    for pdf in p.meta['citation_pdf_url']:
        parsed = urlparse(pdf)
        directory = urlparse(url).path.rsplit('/', 1)[0] + '/'
        if (parsed.scheme not in {'http', 'https'} or parsed.netloc != urlparse(url).netloc
                or not parsed.path.startswith(directory)):
            row['findings'].append('citation_pdf_url is not an absolute URL in the abstract’s own directory')
    row['pdf_tags'] = p.meta['citation_pdf_url']
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, help='Audit a Jekyll build without network requests')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero on technical errors (editorial notes remain advisory)')
    parser.add_argument('--report', type=Path, help='Markdown report destination')
    parser.add_argument('--snapshot', type=Path, help='Detailed JSON snapshot destination')
    args = parser.parse_args()
    report = args.report or (Path('/tmp/rodighiero-scholar-build-audit.md') if args.site_dir else ROOT / 'scripts/scholar-audit.md')
    snapshot = args.snapshot or Path('/tmp/rodighiero-scholar-build-audit.json' if args.site_dir else '/tmp/rodighiero-scholar-audit.json')
    publications = [(p.stem, yaml.safe_load(p.read_text().split('---', 2)[1]))
                    for p in sorted((ROOT / '_publications').glob('*.md'))]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item: audit(item, args.site_dir), publications))
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
            row['findings'].append('No direct HTML link from homepage')
        if row['url'] not in sitemap_urls:
            row['findings'].append('Missing from sitemap')
        if not robots.can_fetch('Googlebot', row['url']):
            row['findings'].append('robots.txt blocks Googlebot')
        row['errors'] = [f for f in row['findings'] if not f.startswith(('Forthcoming:', 'Editor-only work:', 'Editorial review:'))]
    data = {'base': BASE, 'pages': rows, 'shared': {p: {k:v for k,v in r.items() if k != 'text'} for p,r in shared.items()},
            'robots': shared['/robots.txt'].get('text', ''), 'shared_errors': shared_errors}
    snapshot.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
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
             '## Page checks', '', '| Publication | Status | Abstract/lead characters | Findings |', '| --- | --- | --- | --- |']
    for row in rows:
        status = ('Present' if row['status'] == 200 else 'Missing') if args.site_dir else f'HTTP {row["status"]}'
        lines.append(f'| [{row["title"]}]({row["url"]}) | {status} | {row.get("abstract_chars", "—")} | {"; ".join(row["findings"]) or "Core checks passed"} |')
    lines += ['', '## Shared endpoints', '']
    lines += [f'- `{p}`: ' + (('present' if r['status'] == 200 else 'missing') if args.site_dir else f'HTTP {r["status"]}') for p,r in shared.items()]
    lines += [f'- ERROR: {error}' for error in shared_errors]
    lines += ['', '```text', data['robots'].strip(), '```', '',
              '## Interpretation', '',
              '- Core checks compare citation titles, author/editor roles, publication years and venue metadata with source records, check canonical URLs and visible headings, compare complete abstracts with visible text, and inspect robots directives, homepage links and sitemap inclusion.',
              '- Abstract/lead presence does not establish that the text is the complete author-written abstract. Publisher comparisons and scholarly eligibility need editorial review.',
              '- citation_abstract and citation_editor checks enforce this site’s citation-export contract; these tags are not additional Scholar inclusion requirements.',
              '- Maps, catalogs, magazine pieces and interviews are not automatically eligible scholarly articles. Forthcoming entries lack a real publication year.',
              '- An external publisher or repository PDF is not suitable for this domain’s `citation_pdf_url`: Scholar requires the linked PDF in the same subdirectory as the abstract page. HTML full text can remain indexable without a local PDF.',
              '- Do not infer “not indexed” from inaccessible Scholar results or from missing ordinary search results.', '']
    lines += ['See [publisher and PDF review](scholar-review.md) for verified corrections and source conflicts.', '']
    report.write_text('\n'.join(lines))
    error_count = len(shared_errors) + sum(len(r.get('errors', r['findings'])) for r in rows)
    print(f'Audited {len(rows)} publication URLs; {error_count} technical errors. Report: {report}')
    for error in shared_errors:
        print('ERROR: ' + error)
    for r in rows:
        if r['findings']:
            print(r['slug'] + ': ' + '; '.join(r['findings']))
    if args.strict and error_count:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
