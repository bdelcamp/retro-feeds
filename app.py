#!/usr/bin/env python3
import re
import copy
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, Response, jsonify
from typing import Dict, Pattern, Optional
from os import environ,getenv

app = Flask(__name__)

def get_filtered_feeds(
    auth_key: str,
    slug: str,
    image_url: Optional[str] = None
) -> Dict[str, str]:
    """
    Fetch the full Patreon RSS for `slug` and split it into multiple
    RSS feeds based on per‐slug regex mappings. Everything that
    doesn’t match goes into 'Miscellaneous'.

    If image_url is provided, override the channel's <itunes:image>.
    Returns a dict: { show_name: rss_xml_string, ... }
    """
    # 1) Per‐slug show → regex
    show_patterns_map = {
        'Retro Warriors': {
            'Main': r'Retro Warriors(?! Uncut)',
            'Uncut': r'Uncut',
            'Talking Wizards': r'Talking Wizard',
            'Read Along': r'Read Along',
            'Cinema Rogues': r'^Cinema Rogues',
            'Classic Corner': r'Classic Corner',
        },
        # ← add other slugs here if needed
    }
    slug_key = slug
    if slug_key not in show_patterns_map:
        raise ValueError(f"No patterns defined for slug '{slug}'")
    raw_patterns = show_patterns_map[slug_key]
    patterns: Dict[str, Pattern] = {
        name: re.compile(rx, re.IGNORECASE)
        for name, rx in raw_patterns.items()
    }

    # 2) Download the master feed
    url = f"https://www.patreon.com/rss/{slug}?auth={auth_key}"
    resp = requests.get(url)
    resp.raise_for_status()

    # 3) Parse XML
    root = ET.fromstring(resp.content)
    channel = root.find('channel')
    if channel is None:
        raise RuntimeError("Malformed RSS: missing <channel>")

    # Extract metadata (everything but <item>)
    meta = [e for e in channel if e.tag != 'item']
    items = list(channel.findall('item'))

    # Determine the itunes:image namespace-qualified tag, if any
    itunes_qname = None
    for e in meta:
        if e.tag.lower().endswith('}image'):
            itunes_qname = e.tag
            break

    def build_feed(item_list, feed_name: str):
        rss = ET.Element(root.tag, root.attrib)
        ch  = ET.SubElement(rss, 'channel')

        # deep-copy metadata so we don't mutate the originals
        new_meta = [copy.deepcopy(e) for e in meta]

        # Override channel title to match the feed_name
        for m in new_meta:
            if m.tag == 'title':
                m.text = f"{slug} - {feed_name}"

        # override cover art if requested
        if image_url and itunes_qname:
            new_meta = [e for e in new_meta if e.tag != itunes_qname]
            new_img = ET.Element(itunes_qname, {'href': image_url})
            new_meta.append(new_img)

        # attach metadata then items
        for m in new_meta:
            ch.append(m)
        for it in item_list:
            ch.append(it)

        # serialize with XML declaration
        return ET.tostring(rss, encoding='utf-8', xml_declaration=True).decode()

    # 4) Bucket items by regex
    feeds: Dict[str, str] = {}
    matched_ids = set()
    for show_name, pattern in patterns.items():
        matched_items = [it for it in items
                            if pattern.search((it.findtext('title') or ''))]
        for it in matched_items:
            matched_ids.add(id(it))
        feeds[show_name] = build_feed(matched_items, show_name)

    # 5) Miscellaneous
    misc_items = [it for it in items if id(it) not in matched_ids]
    feeds['Miscellaneous'] = build_feed(misc_items, 'Miscellaneous')
    return feeds

@app.route('/rss', methods=['GET'])
def rss_endpoint():

    auth_key  = request.args.get('auth_key') or getenv('PATREON_AUTH_KEY')
    if not auth_key:
        return jsonify({"error": "Missing required param: auth_key"}), 400
    slug      = request.args.get('slug')
    show_q    = request.args.get('show')
    image_url = request.args.get('image_url')

    if not auth_key or not slug:
        return jsonify({'error': 'Missing required params: auth_key and slug'}), 400

    try:
        feeds = get_filtered_feeds(auth_key, slug, image_url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if show_q:
        lookup = { name.lower(): name for name in feeds }
        key = show_q.lower()
        if key not in lookup:
            return jsonify({
                'error': f"Unknown show '{show_q}'",
                'available': list(feeds.keys())
            }), 404
        xml = feeds[lookup[key]]
        return Response(xml, mimetype='application/rss+xml')

    # no `show` → list available feeds
    return jsonify({'available_feeds': list(feeds.keys())})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=(getenv('APP_PORT') or 5000), debug=(getenv('DEBUG').lower() in ('true', '1', 'yes', 'y', 'on')) or False)
