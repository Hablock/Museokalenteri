"""Tarkista -auto-tiedostot ja Clauden muutoslistat. Virheet -> exit 1.

Käyttö: python3 automation/validate.py [--check-urls]
"""
import json
import re
import sys
import warnings
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prepare import CACHE, KINDS, ROOT, load, run_date  # noqa: E402

warnings.filterwarnings("ignore")
REQUIRED = ["title", "start", "end", "description", "Link", "Image"]
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
UNSAFE = re.compile(r"[<>]|javascript:", re.I)


def norm_title(t):
    return re.sub(r"[^a-z0-9åäö]+", "", (t or "").lower())


def check_rows(today):
    errors, warns, index = [], [], {}
    for k in KINDS:
        rows = load(k["auto"])
        if not isinstance(rows, list):
            errors.append(f"{k['auto']}: ei ole JSON-lista")
            continue
        names = {s["nimi"] for s in load(k["sources"], [])}
        seen = {}
        for i, row in enumerate(rows):
            where = f"{k['auto']}[{i}] {row.get(k['key'])} / {row.get('title')}"
            missing = [f for f in [k["key"]] + REQUIRED if f not in row]
            if missing:
                errors.append(f"{where}: puuttuvat kentät {missing}")
                continue
            if row[k["key"]] not in names:
                errors.append(f"{where}: nimi ei vastaa {k['sources']}-tiedostoa")
            for f in [k["key"]] + REQUIRED:
                v = row[f]
                if not isinstance(v, str):
                    errors.append(f"{where}: kenttä {f} ei ole merkkijono")
                elif v != v.strip():
                    errors.append(f"{where}: kentässä {f} ylimääräisiä välilyöntejä")
                elif UNSAFE.search(v) and f not in ("Link", "Image"):
                    errors.append(f"{where}: kentässä {f} HTML-merkkejä tai javascript:")
            if not (ISO.match(row["start"]) and ISO.match(row["end"])):
                errors.append(f"{where}: päivämäärä ei ole muotoa YYYY-MM-DD")
                continue
            try:
                start, end = date.fromisoformat(row["start"]), date.fromisoformat(row["end"])
            except ValueError:
                errors.append(f"{where}: virheellinen päivämäärä")
                continue
            if start > end:
                errors.append(f"{where}: alkaa ({start}) päättymisen ({end}) jälkeen")
            if end < today:
                errors.append(f"{where}: päättynyt {end}")
            if (end - start).days > 3 * 365:
                warns.append(f"{where}: kesto yli 3 vuotta, onko pysyvä?")
            if not row["Link"].startswith(("http://", "https://")):
                errors.append(f"{where}: Link ei ole http(s)-osoite")
            if row["Image"] and not row["Image"].startswith(("http://", "https://")):
                errors.append(f"{where}: Image ei ole http(s)-osoite")
            if not row["Image"]:
                warns.append(f"{where}: ei kuvaa")
            key = (row[k["key"]], norm_title(row["title"]))
            if key in seen:
                errors.append(f"{where}: duplikaatti (sama kuin rivi {seen[key]})")
            seen[key] = i
            index[(k["kind"], row[k["key"]], row["title"])] = row
    return errors, warns, index


def check_changes(index):
    errors, touched = [], []
    for f in sorted((CACHE / "changes").glob("*.json")):
        try:
            ch = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            errors.append(f"{f.name}: virheellinen JSON ({e})")
            continue
        for item in ch.get("added", []) + ch.get("updated", []):
            key = (item.get("type"), item.get("name"), item.get("title"))
            if key not in index:
                errors.append(f"{f.name}: muutoslistan rivi {key} puuttuu datasta")
            if not str(item.get("evidence", "")).strip():
                errors.append(f"{f.name}: rivillä {key} ei ole lähdelainausta (evidence)")
            if key in index:
                touched.append(index[key])
    return errors, touched


def check_urls(rows):
    import fetch_page
    import requests

    warns = []
    for row in rows:
        for field in ("Link", "Image"):
            url = row.get(field)
            if not url:
                continue
            try:
                r = requests.get(url, headers=fetch_page.HEADERS, timeout=20, verify=False, stream=True)
                ok = r.status_code < 400
                r.close()
            except Exception as e:  # noqa: BLE001
                ok, r = False, type(e).__name__
            if not ok:
                code = getattr(r, "status_code", r)
                warns.append(f"{row.get('title')}: {field} ei vastaa ({code}) {url}")
    return warns


def main():
    today = run_date()
    errors, warns, index = check_rows(today)
    change_errors, touched = check_changes(index)
    errors += change_errors
    if "--check-urls" in sys.argv:
        warns += check_urls(touched)
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "validate.json").write_text(
        json.dumps({"errors": errors, "warnings": warns}, ensure_ascii=False, indent=2), encoding="utf-8")
    for e in errors:
        print(f"VIRHE: {e}")
    for w in warns:
        print(f"varoitus: {w}")
    print(f"Validointi: {len(errors)} virhettä, {len(warns)} varoitusta.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
