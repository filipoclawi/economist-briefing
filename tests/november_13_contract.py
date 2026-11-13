#!/usr/bin/env python3
"""Exact November 13 finalization contract; no private source identifiers."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
cov=json.loads((R/'editions/2026-11-13/coverage.json').read_text())
expected={
 'Nannying for the ultra-rich is increasingly lucrative',
 'The US in Brief: A “hard yes” on impeaching Hegseth',
 'Inside Defence: What’s next for Ukraine?',
 'The US in Brief: Wealth tax fails in California',
 'The US in Brief: Pete Hegseth will fight another day',
 'The Insider: Are we on the cusp of an AI market bust?',
 'The US in Brief: A historic Democratic win in Mississippi',
 'Why you should expect an AI crash',
 'The US in Brief: Huang and Lutnick called to testify',
}
assert {c['title'] for c in cov['cards']}==expected
assert len(cov['cards'])==cov['reviewedSources']==cov['editorialSources']==9
assert cov['status']=='completed' and cov['nonEditorialSources']==0
assert cov['duplicatePromotions']==0
assert sum(c['mode']=='watch' for c in cov['cards'])==2
assert len({c['canonical'] for c in cov['cards']})==9
for path in ['index.html','editions/2026-11-13/index.html']:
 s=BeautifulSoup((R/path).read_text(),'html.parser')
 assert 'week to date' not in s.title.get_text()
 assert 'checked 13 Nov 2026' in s.get_text()
 assert 'HTTP 403' in s.get_text()
 for c in cov['cards']:
  a=s.find(id=c['id']);assert a and a.h3.get_text()==c['title']
  assert a.select_one('.preview').get_text()==c['preview']
  assert a.select_one('.open-link')['href']==c['canonical']
  assert c['duration'] in a.select_one('.open-link').get_text()
  assert 'economist.com' in a.select_one('.open-link').get_text()
  if c['mode']=='watch':
   assert 'video' in a['class'] and a['data-mode']=='watch' and a.select_one('.play')
   if c['title'].startswith('Inside Defence:'):
    assert c['duration']=='37 min watch'
    assert c['canonical'].endswith('/inside-defence/ukraine-what-next')
   else:
    assert c['duration']=='45 min watch'
    assert c['canonical'].endswith('/the-insider/are-we-on-the-cusp-of-an-ai-market-bust')
  else: assert c['duration']=='~5 min read (est.)'
  if c['title'].startswith('The US in Brief:'):assert c['cta']=='Related analysis'
print('November 13 contract passed: 8 additions + 1 retained, 9 sources, 2 videos (37/45 minutes), completed edition, source limitations and link reconciliation')
