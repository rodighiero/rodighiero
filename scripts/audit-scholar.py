"""Audit live publication metadata; run `uv run scripts/audit-scholar.py`.

Writes scripts/scholar-audit.md and /tmp/rodighiero-scholar-audit.json.
Checks crawlability and metadata, not inclusion in Scholar's private index.
"""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
import collections
from datetime import datetime
import json
import re
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = yaml.safe_load((ROOT / '_config.yml').read_text())['url']


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
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            self.meta[a.get('name', '').lower()].append(a.get('content', ''))
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'div':
            if self.body_depth:
                self.body_depth += 1
            elif 'body' in a.get('class', '').split():
                self.body_depth = 1

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'div' and self.body_depth:
            self.body_depth -= 1

    def handle_data(self, text):
        if self.in_h1:
            self.h1.append(text)
        if self.body_depth:
            self.body_text.append(text)


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


def audit(item):
    slug, front = item
    url = BASE + '/' + slug
    result = fetch(url)
    row = {'slug': slug, 'title': front['title'], 'type': front['type'],
           'url': url, 'status': result['status'], 'findings': []}
    if result['status'] != 200:
        row['findings'].append('Live response unavailable: ' + result.get('error', 'unexpected status'))
        return row
    p = Page(result['text'])
    row['citation'] = {k: v for k, v in p.meta.items() if k.startswith('citation_')}
    row['bytes'] = result['bytes']
    for field, expected in [('citation_title', [front['title']]),
                            ('citation_author', front.get('author', front.get('editor', '')).split(' and '))]:
        if p.meta[field] != expected:
            row['findings'].append(f'{field} differs from publication source')
    if front['year'] != 'Forthcoming' and p.meta['citation_publication_date'] != [str(front['year'])]:
        row['findings'].append('Missing or inconsistent publication year')
    if front['year'] == 'Forthcoming':
        row['findings'].append('Forthcoming: no publication year supplied')
    if p.canonical != [url]:
        row['findings'].append('Unexpected canonical URL')
    if ''.join(p.h1).strip() != front['title']:
        row['findings'].append('Visible title differs from source')
    directives = ' '.join(p.meta['robots'] + p.meta['googlebot']) + ' ' + result['headers'].get('x-robots-tag', '')
    if re.search(r'\b(noindex|none)\b', directives, re.I):
        row['findings'].append('Indexing blocked by robots directive')
    scripts = re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', result['text'], re.S)
    try:
        work = json.loads(scripts[0])
        abstract = work.get('abstract', '')
        row['abstract_chars'] = len(abstract)
        if not abstract.strip():
            row['findings'].append('No text abstract/lead available')
        visible = re.sub(r'\s+', ' ', ' '.join(p.body_text)).strip()
        if not visible:
            row['findings'].append('No server-rendered text in publication body')
        if result['bytes'] > 5_000_000:
            row['findings'].append('Page exceeds Scholar’s 5 MB limit')
        if '{%' in abstract or '{{' in abstract:
            row['findings'].append('Unrendered template code in abstract')
        row['fulltext_html'] = bool(p.meta['citation_fulltext_html_url'])
    except (ValueError, IndexError):
        row['findings'].append('Invalid or missing work JSON-LD')
    for doi in p.meta['citation_doi']:
        if not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            row['findings'].append('Invalid citation DOI')
    expected_doi = re.fullmatch(r'https?://(?:dx\.)?doi.org/(10\..+)', front.get('doi', ''))
    if expected_doi and not front.get('translation_of') and p.meta['citation_doi'] != [expected_doi[1]]:
        row['findings'].append('Live citation DOI differs from current source (deployment may be pending)')
    for pdf in p.meta['citation_pdf_url']:
        if urlparse(pdf).netloc != urlparse(url).netloc:
            row['findings'].append('citation_pdf_url points outside the site')
    row['pdf_tags'] = p.meta['citation_pdf_url']
    return row


def main():
    publications = [(p.stem, yaml.safe_load(p.read_text().split('---', 2)[1]))
                    for p in sorted((ROOT / '_publications').glob('*.md'))]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(audit, publications))
    shared = {path: fetch(BASE + path) for path in ['/', '/robots.txt', '/sitemap.xml']}
    homepage = Page(shared['/'].get('text', ''))
    home_links = {urljoin(BASE + '/', u).rstrip('/') for u in homepage.links}
    sitemap_urls = set()
    try:
        sitemap = ET.fromstring(shared['/sitemap.xml'].get('text', ''))
        sitemap_urls = {e.text for e in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    except ET.ParseError:
        pass
    for row in rows:
        if row['url'] not in home_links:
            row['findings'].append('No direct HTML link from homepage')
        if row['url'] not in sitemap_urls:
            row['findings'].append('Missing from live sitemap')
    data = {'base': BASE, 'pages': rows, 'shared': {p: {k:v for k,v in r.items() if k != 'text'} for p,r in shared.items()},
            'robots': shared['/robots.txt'].get('text', '')}
    Path('/tmp/rodighiero-scholar-audit.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    checked = datetime.now().astimezone().strftime('%-d %B %Y')
    lines = ['# Google Scholar technical audit', '', f'Checked live pages on {checked}.', '',
             '**Scholar index membership remains unverified.** Scholar search was inaccessible through the available web and browser tools. Ordinary web-search results are not evidence of Scholar inclusion.', '',
             'Guidance: https://scholar.google.com/intl/en/scholar/inclusion.html', '',
             f'Checked {len(rows)} publication URLs. {sum(r["status"] == 200 for r in rows)} returned HTTP 200.',
             f'{sum(r.get("fulltext_html", False) for r in rows)} advertise HTML full text; {sum(bool(r.get("pdf_tags")) for r in rows)} advertise a local PDF.', '',
             '## Live page checks', '', '| Publication | HTTP | Abstract/lead characters | Findings |', '| --- | --- | --- | --- |']
    for row in rows:
        lines.append(f'| [{row["title"]}]({row["url"]}) | {row["status"]} | {row.get("abstract_chars", "—")} | {"; ".join(row["findings"]) or "Core checks passed"} |')
    lines += ['', '## Shared endpoints', '']
    lines += [f'- `{p}`: HTTP {r["status"]}' for p,r in shared.items()]
    lines += ['', '```text', data['robots'].strip(), '```', '',
              '## Interpretation', '',
              '- Core checks compare live citation titles, author lists and publication years with local records, check canonical URLs and visible headings, inspect abstract/lead presence, robots directives, homepage links and sitemap inclusion.',
              '- Abstract/lead presence does not establish that the text is the complete author-written abstract. Publisher comparisons and scholarly eligibility need editorial review.',
              '- Maps, catalogs, magazine pieces and interviews are not automatically eligible scholarly articles. Forthcoming entries lack a real publication year.',
              '- An external publisher or repository PDF is not suitable for this domain’s `citation_pdf_url`: Scholar requires the linked PDF in the same subdirectory as the abstract page. HTML full text can remain indexable without a local PDF.',
              '- Do not infer “not indexed” from inaccessible Scholar results or from missing ordinary search results.', '']
    lines += ['See [publisher and PDF review](scholar-review.md) for verified corrections and source conflicts.', '']
    (ROOT / 'scripts/scholar-audit.md').write_text('\n'.join(lines))
    print(f'Audited {len(rows)} live URLs; {sum(bool(r["findings"]) for r in rows)} have findings. Report: scripts/scholar-audit.md')
    for r in rows:
        if r['findings']:
            print(r['slug'] + ': ' + '; '.join(r['findings']))


if __name__ == '__main__':
    main()
