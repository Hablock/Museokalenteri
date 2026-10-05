"""Kokoa ajon raportti, merkitse käsitellyt lähteet ja päivitä -auto-metatiedot."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prepare import AUTO, CACHE, KINDS, STATUS_FILE, dump, load, run_date  # noqa: E402

TYPE_LABEL = {"museo": "Museo", "galleria": "Galleria"}


def load_changes():
    merged = {k: [] for k in ("sources", "added", "updated", "uncertain", "needs_user")}
    for f in sorted((CACHE / "changes").glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for k in merged:
            merged[k] += data.get(k, [])
    return merged


def load_usage():
    usage = []
    for f in sorted((CACHE / "usage").glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            usage.append({"batch": f.stem, "error": "ei tulostetta (aikakatkaisu tai kaatuminen)"})
            continue
        u = data.get("usage", {}) or {}
        usage.append({
            "batch": f.stem,
            "turns": data.get("num_turns"),
            "minutes": round((data.get("duration_ms") or 0) / 60000, 1),
            "tokens_in": (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
            + (u.get("cache_creation_input_tokens") or 0),
            "tokens_out": u.get("output_tokens") or 0,
            "cost": data.get("total_cost_usd"),
            "error": data.get("subtype") if data.get("is_error") else "",
        })
    return usage


def mark_processed(worklist, changes, today):
    status = load(STATUS_FILE, {}) or {}
    done = {s.get("name") for s in changes["sources"] if s.get("status") == "processed"}
    for item in worklist:
        if item["name"] not in done:
            continue
        for page in item["pages"]:
            st = status.get(page["url"])
            if st and page["ok"]:
                st["processed_hash"] = st.get("hash")
                st["last_processed"] = today.isoformat()
    dump(STATUS_FILE, status)
    return [w["name"] for w in worklist if w["name"] not in done]


def table(headers, rows):
    if not rows:
        return "_Ei yhtään._\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def main():
    today = run_date()
    removed = load(CACHE / "removed.json", {"removed": [], "renamed": []})
    worklist = load(CACHE / "worklist.json", {"sources": []})["sources"]
    validation = load(CACHE / "validate.json", {"errors": [], "warnings": []})
    changes = load_changes()
    usage = load_usage()
    unprocessed = mark_processed(worklist, changes, today)
    status = load(STATUS_FILE, {}) or {}

    for k in KINDS:
        dump(k["auto"].replace(".json", "_meta.json"), {"createdAt": today.isoformat()})

    rem, add, upd = removed["removed"], changes["added"], changes["updated"]
    unc, need = changes["uncertain"], list(changes["needs_user"])
    for url, st in sorted(status.items()):
        if st.get("consecutive_failures", 0) >= 2:
            need.append({"name": ", ".join(st.get("sources", [])), "url": url,
                         "reason": f"Haku epäonnistunut {st['consecutive_failures']} ajoa peräkkäin "
                                   f"(viimeisin tila {st.get('status')}). Url on todennäköisesti vaihtunut."})

    lines = [f"# Kalenterin automaattipäivitys {today.isoformat()}", "",
             f"**{len(rem)}** poistettu · **{len(add)}** lisätty · **{len(upd)}** korjattu · "
             f"**{len(unc)}** epävarmaa · **{len(need)}** tarvitsee sinua", "",
             f"Käsitellyt lähteet: {len(worklist) - len(unprocessed)}/{len(worklist)} muuttunutta. "
             "Muuttumattomat lähteet ohitettiin.", "",
             "Esikatselu: https://hablock.github.io/Museokalenteri/Museokalenteri-auto.html", ""]
    if unprocessed:
        lines += [f"⚠️ Käsittelemättä jäi: {', '.join(unprocessed)}. Ne yritetään uudelleen seuraavassa ajossa.", ""]
    lines += ["## Tarvitsee sinulta", "",
              table(["Lähde", "Syy", "Url"], [(n.get("name"), n.get("reason"), n.get("url", "")) for n in need]),
              "## Lisätyt", "",
              table(["Tyyppi", "Paikka", "Näyttely", "Ajankohta", "Kuva", "Lähde"],
                    [(TYPE_LABEL.get(a.get("type"), a.get("type")), a.get("name"), a.get("title"),
                      f"{a.get('start')} – {a.get('end')}", a.get("image_type"), a.get("source_url"))
                     for a in add]),
              "## Korjatut", "",
              table(["Paikka", "Näyttely", "Kenttä", "Vanha", "Uusi", "Lähde"],
                    [(u.get("name"), u.get("title"), u.get("field"), u.get("old"), u.get("new"), u.get("source_url"))
                     for u in upd]),
              "## Epävarmat (ei lisätty tai muutettu)", "",
              table(["Paikka", "Näyttely", "Syy", "Lähde"],
                    [(u.get("name"), u.get("title"), u.get("reason"), u.get("source_url", "")) for u in unc]),
              "## Poistetut (päättyneet)", "",
              table(["Paikka", "Näyttely", "Päättyi"], [(r["name"], r["title"], r["end"]) for r in rem])]
    if removed["renamed"]:
        lines += ["## Normalisoidut nimet", "",
                  table(["Vanha", "Uusi", "Näyttely"], [(r["from"], r["to"], r["title"]) for r in removed["renamed"]])]
    if validation["warnings"]:
        lines += ["## Validaattorin varoitukset", ""] + [f"- {w}" for w in validation["warnings"]] + [""]
    lines += ["## Kulutus", "",
              table(["Erä", "Kierroksia", "Kesto (min)", "Tokenit sisään", "Tokenit ulos", "API-vastaava $", "Virhe"],
                    [(u["batch"], u.get("turns"), u.get("minutes"), u.get("tokens_in"), u.get("tokens_out"),
                      u.get("cost"), u.get("error", "")) for u in usage]),
              "_Ajo käyttää Claude-tilausta. API-vastaava hinta on suuntaa-antava vertailuluku, ei laskutettu summa._"]
    body = "\n".join(lines) + "\n"
    report_file = AUTO / "reports" / f"{today.isoformat()}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(body, encoding="utf-8")
    (CACHE / "issue_body.md").write_text(body, encoding="utf-8")
    print(body)


if __name__ == "__main__":
    main()
