#!/usr/bin/env python3
"""Regression contract: additive weekly update, source counts and times."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ADDED = {
    'Inside Geopolitics: Should we fear Trump-Putin-Xi collusion?',
    'The US in Brief: Here we Comey again',
    'The US in Brief: Crude politics in Texas',
    'The Insider: Will the midterms make the world more dangerous?',
    'The US in Brief: A fishy campaign in Alaska',
    'The Americans changing politics for the better',
    "The US in Brief: California's voter-fraud showdown",
}
RETAINED = {
    'The US in Brief: Barack Obama v Donald Trump',
    'Sexually transmitted infections are surging in Europe',
}
manifest = json.loads((ROOT / 'editions.json').read_text())
coverage = json.loads((ROOT / 'editions/2026-10-30/coverage.json').read_text())
assert {c['title'] for c in coverage['cards']} == ADDED | RETAINED
assert coverage['reviewedSources'] == coverage['editorialSources'] == 9
assert coverage['nonEditorialSources'] == 0
assert sum(c['mode'] == 'watch' for c in coverage['cards']) == 2
for c in coverage['cards']:
    assert re.search(r'\d+ min (read|watch)', c['duration'])
    if c['title'].startswith('The Insider:'):
        assert c['duration'] == '45 min watch'
    elif c['mode'] == 'watch':
        assert c['duration'] == '~45 min watch (est.)'
prior = json.loads((ROOT / 'editions/2026-10-23/coverage.json').read_text())
assert (prior['reviewedSources'], prior['editorialSources'], prior['nonEditorialSources']) == (8, 7, 1)
for e in manifest['editions']:
    soup = BeautifulSoup((ROOT / e['href'] / 'index.html').read_text(), 'html.parser')
    cards = soup.select('.item-card')
    assert len(cards) == e['count']
    keys = [(a.h3.get_text().casefold(), a.select_one('.open-link')['href']) for a in cards]
    assert len(keys) == len(set(keys))
    for card in cards:
        url = urlsplit(card.select_one('.open-link')['href'])
        assert url.scheme == 'https' and url.hostname == 'www.economist.com'
        assert not url.query and not url.fragment
        duration = card.select_one('.duration').get_text()
        # Older archives retain their explicit unknown-time disclosure.
        assert re.search(r'\d+ min (read|watch)', duration) or (e['end'] < '2026-10-23' and duration == 'Read time not supplied')
        assert 'economist.com' in card.select_one('.open-link').get_text()
    assert len(soup.select('.edition-inner a,.edition-inner span')) == len(manifest['editions'])
# Scan every deployed HTML/data/asset file, not only rendered text.
public = [ROOT / 'index.html', ROOT / 'editions.json', *ROOT.glob('editions/**/*.html'), *ROOT.glob('editions/**/*.json'), *ROOT.glob('assets/*')]
for path in public:
    text = path.read_text()
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text), path
    forbidden = ['/' + 'home/', 'message' + 'Id', 'thread' + 'Id', 'Label' + '_', 'click.e.' + 'economist.com', 'skyward' + '_photons', 'Ar' + 'min', 'Töbeli' + 'weg', 'gh' + 'p_', 'gh' + 'o_']
    assert not any(s in text for s in forbidden), path
    assert '🔴' not in text, path
print('October 30 contract passed: seven exact additions, two retained, two videos; historical service not double-counted; all editions and public files scanned')
