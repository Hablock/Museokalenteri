"""Hae sivu sanatarkkana tekstinä. Käyttö: python3 automation/fetch_page.py URL [--browser]"""
import json
import re
import sys
import time
import warnings
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8",
}
TIMEOUT = 25
BROWSER_TIMEOUT = 45
MIN_TEXT = 400
MAX_TEXT = 20000
MAX_LINKS = 150
MAX_IMAGES = 15
ASSET_RE = re.compile(r"\.(jpe?g|png|gif|webp|svg|pdf|zip|mp4|mp3)(\?|$)", re.I)


def _requests_get(url):
    """requests-haku TLS-varmenteen kierrolla ja https->http -fallbackilla."""
    attempts = [(url, True), (url, False)]
    if url.startswith("https://"):
        attempts.append(("http://" + url[len("https://"):], False))
    last_error = None
    for target, verify in attempts:
        try:
            r = requests.get(target, headers=HEADERS, timeout=TIMEOUT, verify=verify, allow_redirects=True)
            note = "" if verify else "tls-varmennetta ei tarkistettu"
            return r.status_code, r.url, r.text, note
        except requests.exceptions.SSLError as e:
            last_error = e
            continue
        except requests.exceptions.RequestException as e:
            last_error = e
            if verify:
                time.sleep(3)
                continue
            break
    raise RuntimeError(f"{type(last_error).__name__}: {last_error}")


def _browser_get(url):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(user_agent=HEADERS["User-Agent"], locale="fi-FI", ignore_https_errors=True)
        page = ctx.new_page()
        resp = page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT * 1000)
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        html = page.content()
        status = resp.status if resp else 0
        final = page.url
        browser.close()
    return status, final, html


def _clean_text(soup):
    for tag in soup(["script", "style", "noscript", "template", "svg", "iframe", "nav", "form"]):
        tag.decompose()
    for el in soup.select('[class*="cookie"], [id*="cookie"], [class*="consent"], [id*="consent"]'):
        el.decompose()
    text = soup.get_text("\n")
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in text.splitlines()]
    out, blank = [], False
    for ln in lines:
        if not ln:
            if not blank:
                out.append("")
            blank = True
            continue
        out.append(ln)
        blank = False
    return "\n".join(out).strip()


def _meta(soup, base):
    def content(**attrs):
        tag = soup.find("meta", attrs=attrs)
        return tag.get("content", "").strip() if tag else ""

    og_image = content(property="og:image") or content(name="og:image") or content(name="twitter:image")
    return {
        "og_title": content(property="og:title"),
        "og_image": urljoin(base, og_image) if og_image else "",
        "description": content(property="og:description") or content(name="description"),
    }


def _json_ld_events(soup):
    events = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if "@graph" in item:
                    stack.extend(item["@graph"] if isinstance(item["@graph"], list) else [item["@graph"]])
                if item.get("startDate") or item.get("endDate"):
                    events.append({k: item.get(k) for k in ("name", "startDate", "endDate", "url", "image") if item.get(k)})
            elif isinstance(item, list):
                stack.extend(item)
    return events


def _links(soup, base):
    host = urlparse(base).netloc.replace("www.", "")
    seen, links = set(), []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(base, href).split("#")[0]
        if urlparse(absolute).netloc.replace("www.", "") != host or ASSET_RE.search(absolute):
            continue
        if absolute in seen or absolute.rstrip("/") == base.rstrip("/"):
            continue
        seen.add(absolute)
        label = re.sub(r"\s+", " ", a.get_text(" ")).strip()[:120]
        links.append((label, absolute))
        if len(links) >= MAX_LINKS:
            break
    return links


def _images(soup, base):
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        if not src or src.startswith("data:"):
            continue
        images.append((img.get("alt", "").strip()[:100], urljoin(base, src)))
        if len(images) >= MAX_IMAGES:
            break
    return images


def fetch(url, force_browser=False, allow_browser=True):
    """Palauttaa dictin: ok, status, final_url, method, note, text, meta, events, links, images, error.
    allow_browser=False palauttaa needs_browser=True selainta vaativille sivuille selainta käynnistämättä."""
    result = {"url": url, "ok": False, "status": 0, "final_url": url, "method": "", "note": "",
              "text": "", "meta": {}, "events": [], "links": [], "images": [], "error": "",
              "needs_browser": False}
    if urlparse(url).scheme not in ("http", "https"):
        result["error"] = "vain http(s)-osoitteet sallittu"
        return result
    html = None
    if not force_browser:
        try:
            status, final, html, note = _requests_get(url)
            result.update(status=status, final_url=final, method="requests", note=note)
        except RuntimeError as e:
            result["error"] = str(e)
    needs_browser = force_browser or html is None or result["status"] >= 400
    if html is not None and not needs_browser:
        if len(_clean_text(BeautifulSoup(html, "html.parser"))) < MIN_TEXT:
            needs_browser = True
    if needs_browser and not allow_browser:
        result["needs_browser"] = True
        needs_browser = False
    if needs_browser:
        try:
            status, final, bhtml = _browser_get(url)
            if html is None or status < 400 or result["status"] >= 400:
                html = bhtml
                result.update(status=status, final_url=final, method="playwright", error="")
        except Exception as e:
            result["error"] = (result["error"] + " | " if result["error"] else "") + f"playwright: {e}"[:300]
    if html is None:
        return result
    soup = BeautifulSoup(html, "html.parser")
    base = result["final_url"]
    result["meta"] = _meta(soup, base)
    result["events"] = _json_ld_events(soup)
    result["links"] = _links(soup, base)
    result["images"] = _images(soup, base)
    result["text"] = _clean_text(soup)
    result["ok"] = result["status"] < 400 and len(result["text"]) >= 50
    return result


def render(r):
    lines = [
        f"URL: {r['url']}",
        f"LOPULLINEN URL: {r['final_url']}",
        f"TILA: {r['status']} | MENETELMÄ: {r['method']}{' | ' + r['note'] if r['note'] else ''}",
    ]
    if r["error"]:
        lines.append(f"VIRHE: {r['error']}")
    meta = r["meta"] or {}
    lines += [f"OG:TITLE: {meta.get('og_title', '')}", f"OG:IMAGE: {meta.get('og_image', '')}",
              f"KUVAUS: {meta.get('description', '')}"]
    if r["events"]:
        lines.append("JSON-LD-TAPAHTUMAT: " + json.dumps(r["events"], ensure_ascii=False)[:2000])
    text = r["text"]
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + f"\n[... katkaistu, {len(r['text'])} merkkiä yhteensä]"
    lines += ["", "=== TEKSTI (sanatarkka) ===", text, "", "=== KUVAT (alt -> url) ==="]
    lines += [f"- {alt} -> {src}" for alt, src in r["images"]]
    lines += ["", "=== LINKIT (teksti -> url) ==="]
    lines += [f"- {label} -> {href}" for label, href in r["links"]]
    return "\n".join(lines)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("Käyttö: python3 automation/fetch_page.py URL [--browser]")
    print(render(fetch(args[0], force_browser="--browser" in sys.argv)))
