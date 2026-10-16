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


def suggest_state_changes(galleries, status, today):
    """Sääntö: sivusto ei vastaa (2+ ajoa) eikä tulevia näyttelyitä -> ei-aktiivinen; vastaa taas -> aktiivinen."""
    rows = load("gallerianayttelyt-auto.json", [])
    out = []
    for g in galleries:
        urls = [u for u in dict.fromkeys([g.get("nayttelysivu"), g.get("tulevanayttelysivu")]) if u]
        sts = [status[u] for u in urls if u in status]
        if not sts:
            continue
        down = all(st.get("consecutive_failures", 0) >= 2 and not 200 <= (st.get("status") or 0) < 400 for st in sts)
        responds_now = any(st.get("last_ok") == today.isoformat() for st in sts)
        upcoming = any(r.get("gallery") == g["nimi"] and r.get("end", "") >= today.isoformat() for r in rows)
        if g.get("aktiivinen") != "ei-aktiivinen" and down and not upcoming:
            out.append((g["nimi"], "aktiivinen → ei-aktiivinen",
                        "Sivusto ei ole vastannut kahteen ajoon, eikä tulevia näyttelyitä ole."))
        elif g.get("aktiivinen") == "ei-aktiivinen" and responds_now:
            out.append((g["nimi"], "ei-aktiivinen → aktiivinen", "Sivusto vastaa taas. Tarkista näyttelyt."))
    return out


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
    galleries = load("galleriat.json", [])
    inactive = {g["nimi"] for g in galleries if g.get("aktiivinen") == "ei-aktiivinen"}
    state_changes = suggest_state_changes(galleries, status, today)
    for url, st in sorted(status.items()):
        if st.get("sources") and set(st["sources"]) <= inactive:
            continue
        if st.get("consecutive_failures", 0) >= 2:
            code = st.get("status") or 0
            if 200 <= code < 400:
                cause = "Sivu vastaa, mutta siitä ei saatu tekstiä (todennäköisesti JavaScript-sivu)."
            elif code:
                cause = "Url on todennäköisesti vaihtunut."
            else:
                cause = "Palvelin ei vastaa (sivusto alhaalla tai estää pilvipalvelimet)."
            need.append({"name": ", ".join(st.get("sources", [])), "url": url,
                         "reason": f"Haku epäonnistunut {st['consecutive_failures']} ajoa peräkkäin "
                                   f"(viimeisin tila {code}). {cause}"})

    lines = [f"# Kalenterin automaattipäivitys {today.isoformat()}", "",
             f"**{len(rem)}** poistettu · **{len(add)}** lisätty · **{len(upd)}** korjattu · "
             f"**{len(unc)}** epävarmaa · **{len(need)}** tarvitsee sinua", "",
             f"Käsitellyt lähteet: {len(worklist) - len(unprocessed)}/{len(worklist)} muuttunutta. "
             "Muuttumattomat lähteet ohitettiin.", "",
             "Esikatselu: https://hablock.github.io/Museokalenteri/Museokalenteri-auto.html", ""]
    if unprocessed:
        lines += [f"⚠️ Käsittelemättä jäi: {', '.join(unprocessed)}. Ne yritetään uudelleen seuraavassa ajossa.", ""]
    lines += ["## Tarvitsee sinulta", "",
              table(["Lähde", "Syy", "Url"], [(n.get("name"), n.get("reason"), n.get("url", "")) for n in need])]
    if state_changes:
        lines += ["## Ehdotetut tilamuutokset (galleriat.json, kenttä aktiivinen)", "",
                  table(["Galleria", "Muutos", "Peruste"], state_changes)]
    lines += [
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
