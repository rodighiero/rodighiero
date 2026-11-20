"""Carry significant publication metadata changes into the deployed modification dates."""
import argparse
from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


class Metadata(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.fields = []
        self.buffer = None
        self.feed(source.partition('</head>')[0])

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            key = attrs.get('name') or attrs.get('property')
            if key and key not in {'article:modified_time', 'theme-color', 'viewport', 'color-scheme'}:
                self.fields.append((key, attrs.get('content', '')))
        elif tag == 'link' and attrs.get('rel') in {'canonical', 'alternate'}:
            self.fields.append(('link', sorted(attrs.items())))
        elif tag == 'title' or (tag == 'script' and attrs.get('type') == 'application/ld+json'):
            self.buffer = []

    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.buffer is None or tag not in {'title', 'script'}:
            return
        content = ''.join(self.buffer)
        self.buffer = None
        if tag == 'script':
            content = json.loads(content)
            content.pop('dateModified', None)
        self.fields.append((tag, content))


def signature(source):
    fields = Metadata(source).fields
    # Preserve repeated author tags in byline order; ignore JSON object key order.
    serialized = json.dumps(sorted(fields, key=lambda field: field[0]), sort_keys=True)
    return sha256(serialized.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('previous', type=Path, nargs='?',
                        help='last published snapshot; omitted, every page keeps its commit date')
    args = parser.parse_args()
    previous = {}
    if args.previous:
        try:
            previous = json.loads(args.previous.read_text())
        except (OSError, ValueError) as error:
            print(f'warning: unreadable snapshot ({error}); using commit dates', file=sys.stderr)
    revision = subprocess.check_output(['git', 'show', '-s', '--format=%cI', 'HEAD'], text=True).strip()
    sitemap = args.site / 'sitemap.xml'
    tree = ET.parse(sitemap)
    state = {}
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
    for entry in tree.findall('{*}url'):
        path = urlsplit(entry.findtext('{*}loc')).path
        if path == '/':
            continue
        page = args.site / (path.lstrip('/') + '.html')
        source = page.read_text()
        digest = signature(source)
        stamp = entry.find('{*}lastmod')
        dates = [stamp.text]
        if path in previous:
            prior_digest, prior_date = previous[path]
            dates.append(prior_date)
            if digest != prior_digest:
                dates.append(revision)
        modified = max(dates, key=datetime.fromisoformat)
        if modified != stamp.text:
            for template in ['"dateModified": "{}"', 'property="article:modified_time" content="{}"']:
                old = template.format(stamp.text)
                if source.count(old) != 1:
                    raise ValueError(f'{path}: expected one {old}')
                source = source.replace(old, template.format(modified))
            page.write_text(source)
            stamp.text = modified
        state[path] = [digest, modified]
    tree.write(sitemap, encoding='utf-8', xml_declaration=True)
    (args.site / 'publication-lastmod.json').write_text(json.dumps(state, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
