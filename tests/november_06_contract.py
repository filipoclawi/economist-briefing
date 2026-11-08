#!/usr/bin/env python3
"""November release: email-only previews, duplicate review and partial rollover."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'editions.json').read_text())
assert manifest['latest']=='2026-11-13'
expected={
 '2026-11-06': {
 'The quality you should most wish for your children',
 'The US in Brief: A November surprise',
 'Inside Economics: Has Trumponomics delivered?',
 'The US in Brief: What to look out for tonight',
 'The US in Brief: A blue tsunami',
 'The Insider: Is this the end of the Trump era?',
 'The US in Brief: Republicans crumble',
 'Donald Trump’s humiliation offers America an opportunity',
 'The US in Brief: After the tsunami',
 },
 '2026-11-13': {'Nannying for the ultra-rich is increasingly lucrative'},
}
for end,titles in expected.items():
 cov=json.loads((ROOT/'editions'/end/'coverage.json').read_text())
 soup=BeautifulSoup((ROOT/'editions'/end/'index.html').read_text(),'html.parser')
 assert {c['title'] for c in cov['cards']}==titles
 assert len(cov['cards'])==len(titles)
 assert cov['reviewedSources']==cov['editorialSources']+cov['nonEditorialSources']
 assert cov['reviewedSources']==(10 if end=='2026-11-06' else 1)
 assert cov['duplicatePromotions']==(1 if end=='2026-11-06' else 0)
 assert cov['attentionSources']==0
 assert cov['status']==('completed' if end=='2026-11-06' else 'week-to-date')
 assert ('completed' if end=='2026-11-06' else 'week to date') in soup.get_text().lower()
 for c in cov['cards']:
  card=soup.find(id=c['id']); assert card and card.h3.get_text()==c['title']
  assert card.select_one('.preview').get_text()==c['preview']
  assert card.select_one('.open-link')['href']==c['canonical']
  assert card.select_one('.duration').get_text()==c['duration']
  if c['mode']=='read': assert c['duration']=='Read time not supplied'
  else:
   assert c['duration']==('43 min watch' if c['title'].startswith('Inside Economics:') else '45 min watch')
   assert 'video' in card['class'] and c['cta']=='Watch briefing'
complete=json.loads((ROOT/'editions/2026-11-06/coverage.json').read_text())
assert sum(c['mode']=='watch' for c in complete['cards'])==2
assert 'duplicate catch-up promotion reviewed with no new card' in (ROOT/'editions/2026-11-06/index.html').read_text()
root=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
archive=BeautifulSoup((ROOT/'editions/2026-11-13/index.html').read_text(),'html.parser')
assert [str(c) for c in root.select('.item-card')]==[str(c) for c in archive.select('.item-card')]
assert '07 Nov 2026, 12:54 CET' in root.get_text()
assert len(manifest['editions'])==18
print('November contract passed: 10 new cards, 2 sourced video runtimes, 11 reviewed sources, duplicate zero-card accounting, completed/partial separation, root mirror and 18 preserved editions')
