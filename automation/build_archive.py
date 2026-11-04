"""Kokoa päättyneiden näyttelyiden arkisto git-historiasta (kertaluonteinen täyttö).

Käyttö: python3 automation/build_archive.py [--today YYYY-MM-DD] [--review review.md]

Lukee kaikkien commitien näyttelytiedostot, yhdistää saman näyttelyn versiot
(paikka + samankaltainen nimi + päällekkäiset päivät, tai sama nimi) ja ottaa
kustakin uusimman tuotantoversion. Jos näyttely ei koskaan päätynyt
tuotantoon, käytetään uusinta -auto-versiota. Arkistoon tulevat vain
näyttelyt, joiden uusin versio on päättynyt ennen ajopäivää.

Tulos: museonayttelyt-arkisto.json ja gallerianayttelyt-arkisto.json
(samat kentät kuin tuotannossa) sekä tarkistuslista epäselvistä tapauksista.
"""
import argparse
import difflib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["title", "start", "end", "description", "Link", "Image"]
KEY = {"museo": "museum", "galleria": "gallery"}
OUT = {"museo": "museonayttelyt-arkisto.json", "galleria": "gallerianayttelyt-arkisto.json"}

# Historiassa käytetyt vanhat nimet -> nykyinen nimi lähdetiedostossa.
ALIASES = {
    "HAM": "HAM Helsingin taidemuseo",
    "HAM Helsinki": "HAM Helsingin taidemuseo",
    "Taidehalli": "Helsingin Taidehalli",
    "EMMA – Espoon modernin taiteen museo": "EMMA",
    "Designmuseo": "AD-museo",  # yhdistyi AD-museoksi, sama osoite
}
# Tarkistetut virherivit: varhaisen datan englanninkieliset tai väärin päivätyt
# tuplat, joille on oikea suomenkielinen rivi arkistossa.
EXCLUDE = {
    ("EMMA", "Arte Povera – A New Chapter"),        # = Arte Povera – Uusi luku, väärät päivät
    ("EMMA", "Social Fabric"),                      # = Muodinmuutos
    ("EMMA", "Mohamed Bourouissa: The Genealogy of Violence"),  # = Väkivallan syntyhistoria
    ("Villa Gyllenberg", "Poetic Reality"),         # = Runollinen todellisuus
    # Käyttäjän vahvistamat (2026-11-04): sama näyttely kahdella nimellä.
    ("EMMA", "InCollection: Antti Laitinen"),       # = Antti Laitinen: Helisevä metsä
    ("Didrichsenin taidemuseo", "Pro Arte – Antrei Hartikainen"),  # = SYY – Antrei Hartikainen
    ("Villa Gyllenberg", "Wilhelm Gyllenberg ja moderni taide"),  # poistui ennen alkua, ei pidetty
}
# Käyttäjän vahvistamat (2026-11-04): poistuivat datasta kesken, mutta pidettiin.
CONFIRMED = {
    ("Suomen valokuvataiteen museo", "Salamata Mboup"),
    ("Suomen valokuvataiteen museo", "Vinayak"),
    ("EMMA", "Mohamed Bourouissa: Riou"),
    ("EMMA", "Rashaad Newsome: Untitled (New Way)"),
}
PATH_RE = re.compile(r"^(archive/)?(museo|galleria)nayttelyt(-auto|[_-]\d{4}[\d_-]*)?\.json$")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


# Vanhassa datassa on tekoälytyökalun viitejäänteitä, esim. ":contentReference[oaicite:1]{index=1}".
CITATION = re.compile(r":?contentReference\[oaicite:\d+\]\{index=\d+\}")


def clean(s):
    s = CITATION.sub("", (s or "").replace("\u00a0", " ").replace("\u2011", "-"))
    return re.sub(r"\s+", " ", s).strip()


def norm(t):
    return re.sub(r"[^a-z0-9åäö]+", "", clean(t).lower())


def iso(s):
    s = clean(s)
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", s)
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else s[:10]


STOP = {"ja", "och", "and", "the", "of", "näyttely", "valokuvia", "maalauksia"}


def tokens(t):
    # Sanan alku riittää taivutusmuotojen yhdistämiseen (Gyllenbergin/Gyllenbergissä).
    return {w[:6] for w in re.findall(r"[a-z0-9åäöéüðþ]+", clean(t).lower()) if len(w) > 2 and w not in STOP}


def similar(a, b):
    """Sama näyttely eri kirjoitusasulla: välimerkkiero, alaotsikko lisätty tai sanajärjestys vaihtunut."""
    na, nb = norm(a), norm(b)
    if not (na and nb):
        return False
    if na in nb or nb in na or difflib.SequenceMatcher(None, na, nb).ratio() > 0.85:
        return True
    ta, tb = tokens(a), tokens(b)
    return bool(ta and tb) and len(ta & tb) / min(len(ta), len(tb)) >= 0.75


def contains(a, b):
    """Toinen nimi sisältää toisen (alaotsikko lisätty). Tiukempi kuin similar:
    saman taiteilijan eri näyttelyt eivät mene tästä läpi."""
    na, nb = norm(a), norm(b)
    return bool(na and nb) and (na in nb or nb in na)


def overlap(a, b):
    return a["start"] <= b["end"] and b["start"] <= a["end"]


def near(a, b, days=120):
    """Sama nimi eri päivillä on sama näyttely vain, jos alut ovat lähellä
    (päivämääräkorjaus). Muuten kyse on toistuvasta näyttelystä, esim. joulu."""
    try:
        return abs((date.fromisoformat(a["start"]) - date.fromisoformat(b["start"])).days) <= days
    except ValueError:
        return False


def collect():
    """Palauta kaikki rivit: versio per (commit, polku), vanhimmasta uusimpaan."""
    versions, seen_blobs = {}, {}
    commits = [c.split() for c in git("log", "--all", "--format=%H %ad", "--date=short").splitlines() if c]
    commits.reverse()
    for order, (sha, day) in enumerate(commits):
        for entry in git("ls-tree", "-r", sha).splitlines():
            meta, path = entry.split("\t")
            m = PATH_RE.match(path)
            if not m:
                continue
            blob = meta.split()[2]
            if blob not in seen_blobs:
                try:
                    data = json.loads(git("cat-file", "-p", blob))
                except (ValueError, subprocess.CalledProcessError):
                    data = []
                seen_blobs[blob] = data if isinstance(data, list) else []
            # Lähteen luotettavuus: 2 = elävä tuotantotiedosto, 1 = päivätty
            # tilannekuva (archive/ tai vanha juuritiedosto), 0 = -auto.
            # Tilannekuvat pysyvät mukana kaikissa myöhemmissä commiteissa, joten
            # niiden "uusin esiintymä" ei kerro mitään: käytä tiedostonimen päivää.
            kind, suffix = m[2], m[3]
            rank = 0 if suffix == "-auto" else 2 if suffix is None else 1
            snap_day = None
            if rank == 1:
                d = re.findall(r"\d+", suffix)
                snap_day = f"{d[0]}-{int(d[1]):02d}-{int(d[2]):02d}" if len(d) >= 3 else day
            prod = rank > 0
            for r in seen_blobs[blob]:
                if not isinstance(r, dict):
                    continue
                venue = clean(r.get(KEY[kind]) or r.get("museum") or r.get("gallery"))
                row = {KEY[kind]: ALIASES.get(venue, venue)}
                for f in FIELDS:
                    v = r.get(f, r.get(f.lower(), ""))
                    row[f] = iso(v) if f in ("start", "end") else clean(v)
                if not (row["title"] and row["start"] and row["end"]):
                    continue
                # Sama rivi toistuu jokaisessa commitissa: pidä yksi per sisältö,
                # ja muista sen uusin esiintymä.
                key = (kind, rank, json.dumps(row, sort_keys=True))
                v = versions.get(key)
                if v is None:
                    versions[key] = {"kind": kind, "prod": prod, "rank": rank, "order": order,
                                     "day": snap_day or day, "row": row}
                elif rank != 1 and order > v["order"]:
                    v["order"], v["day"] = order, day
    return list(versions.values()), [day for _, day in commits]


def cluster(versions):
    groups = {}
    for v in versions:
        groups.setdefault((v["kind"], v["row"][KEY[v["kind"]]]), []).append(v)
    clusters = []
    for (kind, venue), vs in groups.items():
        cs = []
        for v in vs:
            r = v["row"]
            match = next((c for c in cs if any(
                (norm(r["title"]) == norm(o["row"]["title"]) and (overlap(r, o["row"]) or near(r, o["row"])))
                or (similar(r["title"], o["row"]["title"]) and overlap(r, o["row"])) for o in c)), None)
            if match is None:
                cs.append([v])
            else:
                match.append(v)
        clusters += cs
    return clusters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--review", default=None)
    args = ap.parse_args()

    versions, commit_days = collect()
    last_order = len(commit_days) - 1
    # Arkiston omat paikat (kalenterista poistuneet) täydentävät nykyisiä lähdetiedostoja.
    known = {k: {s["nimi"] for f in files if (ROOT / f).exists()
                 for s in json.loads((ROOT / f).read_text(encoding="utf-8"))}
             for k, files in (("museo", ("museot.json", "museot-arkisto.json")),
                              ("galleria", ("galleriat.json", "galleriat-arkisto.json")))}
    # Tuotannossa yhä käynnissä olevat: saman paikan ja alkupäivän vanha versio
    # (esim. nimi ja loppupäivä muuttuneet) ei ole päättynyt näyttely.
    # Myös saman nimen aiempi arvaus eri päivillä (alku alle 200 pv päässä) on
    # vanha versio; vuoden välein toistuvat (esim. joulu) jäävät arkistoon.
    running = [(kind, r) for kind, f in (("museo", "museonayttelyt.json"), ("galleria", "gallerianayttelyt.json"))
               for r in json.loads((ROOT / f).read_text(encoding="utf-8"))
               if r.get("end", "") >= args.today]

    def is_stale(kind, row):
        return any(k == kind and r[KEY[k]] == row[KEY[kind]] and (
            r["start"] == row["start"] or (contains(r["title"], row["title"]) and near(r, row, 200)))
            for k, r in running)
    out = {"museo": [], "galleria": []}
    review = {"stale": [], "auto_only": [], "removed_early": [], "same_dates": [], "unknown_venue": [], "titles": []}

    for c in cluster(versions):
        prod = [v for v in c if v["prod"]]
        live = [v for v in c if v["rank"] == 2]
        best = max(c, key=lambda v: (v["rank"], v["day"], v["order"]))
        kind, row = best["kind"], best["row"]
        if row["end"] >= args.today:
            continue
        venue = row[KEY[kind]]
        if (venue, row["title"]) in EXCLUDE:
            continue
        if is_stale(kind, row):
            review["stale"].append(f"{venue} / {row['title']} ({row['start']} – {row['end']})")
            continue
        label = f"{venue} / {row['title']} ({row['start']} – {row['end']})"
        if not prod:
            review["auto_only"].append(label)
        if live:
            # Poistettu kesken: ensimmäinen commit, jossa riviä ei enää ole, on
            # ennen loppupäivää (tavallisesti päättynyt poistuu vasta myöhemmin).
            last = max(v["order"] for v in live)
            if last < last_order and commit_days[last + 1] < row["end"] and (venue, row["title"]) not in CONFIRMED:
                review["removed_early"].append(
                    f"{label}, poistui {commit_days[last + 1]} (viimeksi datassa {commit_days[last]})")
        if venue not in known[kind]:
            review["unknown_venue"].append(label)
        titles = sorted({v["row"]["title"] for v in c})
        if len(titles) > 1:
            review["titles"].append(f"{label} ← {' | '.join(t for t in titles if t != row['title'])}")
        out[kind].append(row)

    for kind, rows in out.items():
        seen = {}
        for r in rows:
            seen.setdefault((r[KEY[kind]], r["start"], r["end"]), []).append(r["title"])
        review["same_dates"] += [f"{v} ({s} – {e}): {' | '.join(ts)}" for (v, s, e), ts in seen.items() if len(ts) > 1]
        rows.sort(key=lambda r: (r["end"], r["start"], r[KEY[kind]]), reverse=True)
        (ROOT / OUT[kind]).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{OUT[kind]}: {len(rows)} näyttelyä")

    if args.review:
        heads = {
            "stale": "Jätetty pois: vanha versio tuotannossa yhä käynnissä olevasta näyttelystä",
            "removed_early": "Poistuivat datasta ennen päättymistään (virheellisiä tai peruttuja?)",
            "auto_only": "Eivät koskaan päätyneet tuotantoon (vain -auto)",
            "unknown_venue": "Paikka puuttuu museot.json/galleriat.json-tiedostosta",
            "same_dates": "Sama paikka ja samat päivät, eri nimet (eri näyttelyitä vai kieliversioita?)",
            "titles": "Yhdistetyt nimiversiot (arkistoon valittu nimi ← muut)",
        }
        lines = [f"# Arkiston tarkistuslista ({args.today})", ""]
        for k, h in heads.items():
            lines += [f"## {h} ({len(review[k])})", ""] + [f"- {x}" for x in sorted(review[k])] + [""]
        Path(args.review).write_text("\n".join(lines), encoding="utf-8")
        print("Tarkistuslista:", args.review, {k: len(v) for k, v in review.items()})


if __name__ == "__main__":
    main()
