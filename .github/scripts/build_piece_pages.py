#!/usr/bin/env python3
"""Write work/<slug>/index.html for every published lightbox piece.

Each page carries that piece's title, description and thumbnail as Open Graph
tags (so links shared by text, email or Slack preview the piece itself), then
redirects to the site at #category/slug, which opens the piece.

Usage: build_piece_pages.py <site_dir>
"""
import html
import json
import os
import re
import sys


def youtube_id(url):
    m = re.search(r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})', url or '')
    return m.group(1) if m else None


def absolute(base, path):
    if not path or re.match(r'^https?://', path):
        return path or ''
    return f"{base}/{path.lstrip('/')}" if base else path


def main(site_dir):
    with open(os.path.join(site_dir, 'site.json'), encoding='utf-8') as f:
        site = json.load(f)
    with open(os.path.join(site_dir, 'projects.json'), encoding='utf-8') as f:
        projects = json.load(f)

    base = (site.get('website') or '').rstrip('/')
    owner = site.get('ownerName') or ''
    owner_title = site.get('ownerTitle') or ''
    byline = ', '.join(x for x in (owner, owner_title) if x)
    favicon = site.get('favicon') or ''
    cats = {c['id'] for c in site.get('categories', [])
            if c.get('published') is not False and c.get('type') != 'gallery'}

    written = set()
    for p in projects:
        slug = p.get('slug') or str(p.get('id', ''))
        if not slug or slug in written or p.get('published') is False or p.get('category') not in cats:
            continue
        written.add(slug)

        title = p.get('title') or owner
        parts = [x for x in (p.get('client'), p.get('award')) if x]
        desc = p.get('description') or ' · '.join(parts + ([byline] if byline else []))
        yt = youtube_id(p.get('url'))
        image = (absolute(base, p.get('thumbnail'))
                 or (f'https://img.youtube.com/vi/{yt}/hqdefault.jpg' if yt else '')
                 or absolute(base, site.get('ogImage')))
        page_url = f'{base}/work/{slug}/' if base else ''
        target = f"../../#{p['category']}/{slug}"

        e = lambda s: html.escape(s or '', quote=True)
        head = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '  <meta charset="UTF-8" />',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
            f'  <title>{e(title)}{" — " + e(owner) if owner else ""}</title>',
            f'  <meta name="description" content="{e(desc)}" />',
            '  <meta property="og:type" content="video.other" />',
            f'  <meta property="og:title" content="{e(title)}" />',
            f'  <meta property="og:description" content="{e(desc)}" />',
            f'  <meta property="og:site_name" content="{e(owner)}" />' if owner else '',
            f'  <meta property="og:image" content="{e(image)}" />' if image else '',
            f'  <meta property="og:url" content="{e(page_url)}" />' if page_url else '',
            '  <meta name="twitter:card" content="summary_large_image" />',
            f'  <meta name="twitter:image" content="{e(image)}" />' if image else '',
            f'  <link rel="canonical" href="{e(page_url)}" />' if page_url else '',
            f'  <link rel="icon" href="../../{e(favicon)}" />' if favicon else '',
            f'  <meta http-equiv="refresh" content="0; url={e(target)}" />',
            f'  <script>location.replace({json.dumps(target)});</script>',
            '</head>',
            '<body style="background:#111;color:#ccc;font-family:sans-serif">',
            f'  <p><a href="{e(target)}" style="color:inherit">{e(title)}</a></p>',
            '</body>',
            '</html>',
        ]
        out_dir = os.path.join(site_dir, 'work', slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(line for line in head if line) + '\n')

    print(f'Wrote {len(written)} piece pages to {os.path.join(site_dir, "work")}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
