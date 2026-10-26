#!/usr/bin/env python3
"""Public regression contract for the October catch-up and rollover."""
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    '2026-10-23': {
        'The US in Brief: An Ohio attack-ad goes national',
        'The agony of liberal Europe',
        'The US in Brief: Psephological shenanigans',
        'The US in Brief: Battle of the billionaires',
        'The US in Brief: Preaching to the converted',
        'Inside Economics: Will France blow up the euro zone?',
        'The US in Brief: Putin fuel on the fire',
    },
    '2026-10-30': {
        'The US in Brief: Barack Obama v Donald Trump',
        'Sexually transmitted infections are surging in Europe',
    },
}

manifest = json.loads((ROOT / 'editions.json').read_text())
for end, titles in EXPECTED.items():
    coverage = json.loads((ROOT / 'editions' / end / 'coverage.json').read_text())
    assert coverage['editorialSources'] >= len(titles)
    assert coverage['reviewedSources'] == coverage['editorialSources'] + coverage['nonEditorialSources']
    cards = coverage['cards']
    assert titles <= {c['title'] for c in cards}
    assert len(cards) == len({c['title'] for c in cards})
    html = (ROOT / 'editions' / end / 'index.html').read_text()
    for c in cards:
        assert c['title'].replace('&', '&amp;') in html
        assert c['canonical'] in html
        url = urlsplit(c['canonical'])
        assert url.scheme == 'https' and url.hostname == 'www.economist.com'
        assert not url.query and not url.fragment
        if c['mode'] == 'watch':
            assert c['type'] == 'insider' and c['cta'] == 'Watch briefing'
            assert c['duration'] == 'Watch time not supplied' or 'min watch' in c['duration']
        if c['title'].startswith('The US in Brief:'):
            assert c['cta'] == 'Related analysis'
    if coverage['status'] == 'week-to-date':
        assert 'week to date' in html.lower()
        cutoff = datetime.fromisoformat(coverage['dataThrough'])
        assert cutoff >= datetime.fromisoformat('2026-10-26T12:08:07+01:00')
        assert cutoff.strftime('%d %b %Y, %H:%M') in html
    assert 'Important information about your subscription' not in html
    assert '$289' not in html

# A previous episode mentioned as a promotion must not acquire a second card,
# and an unrelated episode's stated runtime must not overwrite its old value.
previous = (ROOT / 'editions/2026-10-16/index.html').read_text()
assert previous.count('an-interview-with-alice-weidel') == 1
assert '40 min watch' in previous
print('Catch-up contract passed: nine substantive sources, service exclusion, source state, video time, partial cutoff and prior episode preservation')
