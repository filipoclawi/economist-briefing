#!/usr/bin/env python3
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "editions.json").read_text())
editions = manifest["editions"]
latest = manifest["latest"]
expected = {"": next(e["count"] for e in editions if e["end"] == latest)}
expected.update({e["href"]: e["count"] for e in editions})
expected_additions = {
    "editions/2026-08-14/": {
        "How dementia is being defeated",
        "The US in Brief: Trump appoints a new top legal adviser",
        "Inside Tech: The man putting self-driving cars on Britain’s streets",
        "The US in Brief: Trump attacks childhood vaccination",
        "The US in Brief: An upset in Wisconsin",
        "The Insider: Is it time to talk to the Taliban?",
        "The US in Brief: Trump renews attack on mail-in ballots",
        "The Taliban are vile. Democracies must still engage with them",
        "The US in Brief: Doing the aircraft-carrier shuffle",
    },
    "editions/2026-08-21/": {
        "The US in Brief: Todd Blanche declares non-independence",
        "Inside Economics: Could Japan bring down the world economy?",
        "The US in Brief: “Inane, haphazard” and helping Russia",
        "The US in Brief: Some primary surprises",
        "The Insider: Our interview with Yuval Noah Harari",
        "The US in Brief: Dismay at $40trn in debt",
        "Could AIs become conscious?",
        "The US in Brief: The USS Abraham Lincoln relieved",
    },
}
server = subprocess.Popen(
    [sys.executable, "-m", "http.server", "8767"],
    cwd=ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    time.sleep(1)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        errors = []
        total_archive_cards = 0
        total_archive_videos = 0
        for path, count in expected.items():
            page = browser.new_page(viewport={"width": 1440, "height": 950})
            page.on("console", lambda m: errors.append(f"{path}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(f"{path}: {e}"))
            page.goto("http://127.0.0.1:8767/" + path, wait_until="networkidle")
            page.wait_for_function("document.documentElement.dataset.ready === 'true'")
            cards = page.locator(".item-card")
            videos = page.locator(".item-card.video")
            assert cards.count() == count, (path, cards.count(), count)
            assert page.locator(".edition-inner a,.edition-inner span").count() == len(editions)
            assert page.locator(".open-link").count() == count
            assert page.locator(".duration").count() == count
            assert videos.count() == page.locator('.item-card[data-mode="watch"]').count()
            assert videos.count() == page.locator(".item-card.video .play").count()
            for card in cards.all():
                title = card.locator("h3").inner_text()
                text = card.inner_text()
                href = card.locator(".open-link").get_attribute("href")
                assert href
                parsed = urlsplit(href)
                assert parsed.scheme == "https" and parsed.hostname and parsed.hostname.endswith("economist.com")
                assert not parsed.query and not parsed.fragment
                assert "economist.com" in text and "min" in text
                if title.startswith("The US in Brief"):
                    assert "Related analysis" in text
                if re.match(r"^(The Insider|Inside Defence|Inside Economics|Inside Geopolitics)\b", title):
                    assert "video" in (card.get_attribute("class") or "") and card.get_attribute("data-mode") == "watch"
                    assert "min watch" in text.lower()
            text = page.locator("body").inner_text()
            assertion_path = f"editions/{latest}/" if path == "" else path
            if assertion_path in expected_additions:
                titles = set(page.locator(".item-card h3").all_inner_texts())
                assert expected_additions[assertion_path] == titles
                assert "Sign up to your personalised newsletter" not in titles
                assert "Continue watching your Insider episode" not in titles
            assert "🔴" not in text
            assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
            private_markers = ["/" + "home/", "message" + "Id", "thread" + "Id", "Label" + "_", "icloud" + ".com"]
            assert not any(secret in text for secret in private_markers)
            assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
            if path.startswith("editions/"):
                total_archive_cards += count
                total_archive_videos += videos.count()
            if path == "":
                page.screenshot(path=str(ROOT / "test-results-desktop.png"), full_page=True)
            if path == "editions/2026-08-14/":
                page.screenshot(path=str(ROOT / "test-results-video-edition.png"), full_page=True)
            page.close()

        for path in expected:
            mobile = browser.new_page(viewport={"width": 390, "height": 844})
            mobile.goto("http://127.0.0.1:8767/" + path, wait_until="networkidle")
            mobile.wait_for_function("document.documentElement.dataset.ready === 'true'")
            assert mobile.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
            if path == "":
                mobile.screenshot(path=str(ROOT / "test-results-mobile.png"), full_page=True)
            mobile.close()
        browser.close()
        assert not errors, errors
    print(
        f"Economist UI smoke passed: {len(editions)} editions, "
        f"{total_archive_cards} cards, {total_archive_videos} videos, clean direct links, "
        "visible destinations/times, privacy, console, desktop/mobile overflow"
    )
finally:
    server.terminate()
    server.wait(timeout=5)
