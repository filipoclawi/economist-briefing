#!/usr/bin/env python3
import re,subprocess,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];server=subprocess.Popen([sys.executable,'-m','http.server','8767'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
EXPECTED={'':4,'editions/2026-07-17/':5,'editions/2026-07-24/':8,'editions/2026-07-31/':6,'editions/2026-08-07/':4}
WATCH={'':1,'editions/2026-07-17/':1,'editions/2026-07-24/':1,'editions/2026-07-31/':2,'editions/2026-08-07/':1}
try:
 time.sleep(1)
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True);errors=[]
  for path,count in EXPECTED.items():
   page=b.new_page(viewport={'width':1440,'height':950});page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('http://127.0.0.1:8767/'+path,wait_until='networkidle');page.wait_for_function("document.documentElement.dataset.ready === 'true'")
   assert page.locator('.item-card').count()==count;assert page.locator('.item-card.video').count()==WATCH[path]
   assert page.locator('.item-card.video .play').count()==WATCH[path];assert page.locator('.edition-inner a,.edition-inner span').count()==4
   assert page.locator('.open-link').count()==count and page.locator('.duration').count()==count
   hrefs=page.locator('.open-link').evaluate_all("a=>a.map(x=>x.href)");assert all(x.startswith('https://') and 'economist.com' in x and '?' not in x for x in hrefs)
   assert all('min watch' in x.lower() for x in page.locator('.item-card.video .duration').all_text_contents())
   text=page.locator('body').text_content() or '';assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text);assert not any(x in text for x in ['/home/','messageId','Label_','icloud.com'])
   assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
   if path=='':page.screenshot(path=str(ROOT/'test-results-desktop.png'),full_page=True)
   if path=='editions/2026-07-31/':page.screenshot(path=str(ROOT/'test-results-video-edition.png'),full_page=True)
   page.close()
  mob=b.new_page(viewport={'width':390,'height':844});mob.goto('http://127.0.0.1:8767',wait_until='networkidle');mob.wait_for_function("document.documentElement.dataset.ready === 'true'");assert mob.locator('.item-card.video').count()==1;assert mob.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth');mob.screenshot(path=str(ROOT/'test-results-mobile.png'),full_page=True);mob.close();b.close();assert not errors,errors
 print('Economist UI smoke passed: 4 editions, 23 direct links, 5 visually flagged videos, durations, privacy, desktop/mobile')
finally:server.terminate();server.wait(timeout=5)
