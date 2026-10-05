"""Automaattiajon valmistelu: alusta -auto-tiedostot, poista päättyneet, hae lähteet, muodosta työlista.

Ei käytä Claudea. Ympäristömuuttujat: RUN_DATE=YYYY-MM-DD (testaukseen), FULL_RUN=1 (käsittele kaikki lähteet).
"""
import hashlib
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AUTO = ROOT / "automation"
CACHE = AUTO / "cache"
PAGES = CACHE / "pages"
BATCHES = CACHE / "batches"
STATUS_FILE = AUTO / "state" / "status.json"
BATCH_SIZE = 6
REPROCESS_AFTER_DAYS = 60

KINDS = [
    {"kind": "museo", "sources": "museot.json", "base": "museonayttelyt.json",
     "auto": "museonayttelyt-auto.json", "key": "museum", "later": "tulevat"},
    {"kind": "galleria", "sources": "galleriat.json", "base": "gallerianayttelyt.json",
     "auto": "gallerianayttelyt-auto.json", "key": "gallery", "later": "tulevanayttelysivu"},
]


def run_date():
    return date.fromisoformat(os.environ["RUN_DATE"]) if os.environ.get("RUN_DATE") else date.today()


def load(path, default=None):
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def dump(path, data):
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slug(url):
    s = re.sub(r"^https?://(www\.)?", "", url)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:80]
    return f"{s}-{hashlib.sha1(url.encode()).hexdigest()[:6]}"


VOLATILE = re.compile(r"\b(avoinna|auki|suljettu|aukiolo|tänään|huomenna|open|closed|today)\b", re.I)


def text_hash(text):
    """Tunniste sivun sisällölle. Päivittäin vaihtuvat aukiolorivit ohitetaan, ellei niissä ole vuosilukua."""
    lines = [ln for ln in text.splitlines() if not (VOLATILE.search(ln) and not re.search(r"20\d\d", ln))]
    return hashlib.sha1(re.sub(r"\s+", " ", " ".join(lines)).strip().encode("utf-8")).hexdigest()


def canonical_name(name, source_names):
    """Korjaa lyhyet nimet (esim. 'HAM') lähdetiedoston nimeksi, jos vastaavuus on yksiselitteinen."""
    if name in source_names:
        return name
    matches = [n for n in source_names if n.startswith(name + " ") or n.lower() == name.lower()]
    return matches[0] if len(matches) == 1 else name


def seed_and_prune(today):
    removed, renamed = [], []
    for k in KINDS:
        source_names = [s["nimi"] for s in load(k["sources"], [])]
        if not (ROOT / k["auto"]).exists():
            shutil.copyfile(ROOT / k["base"], ROOT / k["auto"])
        rows = load(k["auto"], [])
        kept = []
        for row in rows:
            for field, value in row.items():
                if isinstance(value, str):
                    row[field] = value.strip()
            fixed = canonical_name(row.get(k["key"], ""), source_names)
            if fixed != row.get(k["key"]):
                renamed.append({"type": k["kind"], "from": row[k["key"]], "to": fixed, "title": row.get("title")})
                row[k["key"]] = fixed
            try:
                ended = date.fromisoformat(row["end"]) < today
            except (KeyError, ValueError):
                ended = False
            if ended:
                removed.append({"type": k["kind"], "name": row[k["key"]], "title": row.get("title"), "end": row.get("end")})
            else:
                kept.append(row)
        dump(k["auto"], kept)
    return removed, renamed


def collect_sources(overrides):
    sources = []
    for k in KINDS:
        for s in load(k["sources"], []):
            ov = overrides.get(s["nimi"], {})
            urls = [u for u in [s.get("nayttelysivu"), s.get(k["later"])] + ov.get("extra_urls", []) if u]
            urls = list(dict.fromkeys(urls))
            sources.append({"type": k["kind"], "name": s["nimi"], "kotisivu": s.get("kotisivu", ""),
                            "urls": urls, "overrides": ov})
    return sources


def fetch_all(sources):
    unique = {}
    for s in sources:
        if s["overrides"].get("inactive"):
            continue
        for u in s["urls"]:
            unique.setdefault(u, {"browser": False})
            unique[u]["browser"] |= bool(s["overrides"].get("browser"))
    results = {}

    def light(u):
        return u, fetch_page.fetch(u, force_browser=False, allow_browser=False)

    light_urls = [u for u, o in unique.items() if not o["browser"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for u, r in pool.map(light, light_urls):
            results[u] = r
            print(f"  {r['status']:>3} {r['method'] or '-':9} {u}", flush=True)
    for u, o in unique.items():
        if o["browser"] or results.get(u, {}).get("needs_browser"):
            r = fetch_page.fetch(u, force_browser=True)
            results[u] = r
            print(f"  {r['status']:>3} {'playwright':9} {u}", flush=True)
    return results


def update_status(sources, results, today):
    status = load(STATUS_FILE, {}) or {}
    for s in sources:
        for u in s["urls"]:
            if u not in results:
                continue
            r = results[u]
            st = status.setdefault(u, {"consecutive_failures": 0})
            st["sources"] = sorted(set(st.get("sources", [])) | {s["name"]})
            st["last_checked"] = today.isoformat()
            st["status"] = r["status"]
            st["method"] = r["method"]
            st["error"] = r["error"][:300]
            if r["ok"]:
                st["last_ok"] = today.isoformat()
                st["consecutive_failures"] = 0
                st["hash"] = text_hash(r["text"])
            elif st.get("_counted") != today.isoformat():
                st["consecutive_failures"] = st.get("consecutive_failures", 0) + 1
            st["_counted"] = today.isoformat()
    for st in status.values():
        st.pop("_counted", None)
    dump(STATUS_FILE, status)
    return status


def build_worklist(sources, results, status, today, full):
    worklist = []
    for s in sources:
        if s["overrides"].get("inactive"):
            continue
        pages, changed, any_ok = [], False, False
        for u in s["urls"]:
            r = results.get(u)
            if r is None:
                continue
            cache_file = PAGES / f"{slug(u)}.txt"
            cache_file.write_text(fetch_page.render(r), encoding="utf-8")
            st = status.get(u, {})
            is_changed = r["ok"] and st.get("hash") != st.get("processed_hash")
            stale = (st.get("last_processed") or "1970-01-01") < (today - timedelta(days=REPROCESS_AFTER_DAYS)).isoformat()
            changed |= is_changed or (r["ok"] and stale)
            any_ok |= r["ok"]
            pages.append({"url": u, "cache_file": str(cache_file.relative_to(ROOT)), "ok": r["ok"],
                          "status": r["status"], "changed": is_changed})
        if full or changed or not any_ok:
            worklist.append({"type": s["type"], "name": s["name"], "kotisivu": s["kotisivu"],
                             "pages": pages, "all_failed": not any_ok, "overrides": s["overrides"]})
    return worklist


def make_batches(worklist):
    """Ryhmittele erät niin, että samaa urlia jakavat lähteet ovat samassa erässä."""
    groups = {}
    for item in worklist:
        key = tuple(sorted(p["url"] for p in item["pages"])) or (item["name"],)
        groups.setdefault(key, []).append(item)
    batches, current = [], []
    for group in groups.values():
        if current and len(current) + len(group) > BATCH_SIZE:
            batches.append(current)
            current = []
        current.extend(group)
    if current:
        batches.append(current)
    return batches


def main():
    today = run_date()
    full = os.environ.get("FULL_RUN") == "1"
    if CACHE.exists():
        shutil.rmtree(CACHE)
    PAGES.mkdir(parents=True)
    BATCHES.mkdir(parents=True)

    removed, renamed = seed_and_prune(today)
    dump(CACHE / "removed.json", {"removed": removed, "renamed": renamed})
    print(f"Ajopäivä {today}: poistettu {len(removed)} päättynyttä, normalisoitu {len(renamed)} nimeä.")

    overrides = load(AUTO / "sources.json", {}).get("sources", {})
    sources = collect_sources(overrides)
    print(f"Haetaan {sum(len(s['urls']) for s in sources)} urlia {len(sources)} lähteestä...")
    results = fetch_all(sources)
    status = update_status(sources, results, today)
    worklist = build_worklist(sources, results, status, today, full)
    batches = make_batches(worklist)
    dump(CACHE / "worklist.json", {"run_date": today.isoformat(), "full_run": full, "sources": worklist})
    for i, batch in enumerate(batches, 1):
        dump(BATCHES / f"batch-{i:02d}.json", {"run_date": today.isoformat(), "batch": i, "sources": batch})

    failed = [w["name"] for w in worklist if w["all_failed"]]
    print(f"Työlista: {len(worklist)} lähdettä, {len(batches)} erää. Kokonaan epäonnistuneet: {failed or '-'}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"batches={len(batches)}\n")


if __name__ == "__main__":
    main()
