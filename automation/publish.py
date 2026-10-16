"""Siirrä tarkistettu -auto-data tuotantoon. Ajetaan vain käyttäjän käskystä, ei koskaan automaattisesti.

Käyttö: python3 automation/publish.py
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prepare import KINDS, ROOT, load, run_date  # noqa: E402
from validate import check_rows  # noqa: E402


def main():
    errors, _, _ = check_rows(run_date())
    if errors:
        print("Julkaisu keskeytetty, -auto-datassa on virheitä:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    for k in KINDS:
        prod = k["base"]
        before = {(r[k["key"]], r["title"]) for r in load(prod, [])}
        after = {(r[k["key"]], r["title"]) for r in load(k["auto"], [])}
        shutil.copyfile(ROOT / k["auto"], ROOT / prod)
        auto_meta = load(k["auto"].replace(".json", "_meta.json"), {})
        if auto_meta.get("createdAt"):
            (ROOT / prod.replace(".json", "_meta.json")).write_text(
                json.dumps({"createdAt": auto_meta["createdAt"]}, indent=2) + "\n", encoding="utf-8")
        print(f"{prod}: {len(before)} -> {len(after)} näyttelyä "
              f"(+{len(after - before)} uutta, -{len(before - after)} poistunutta), "
              f"päivitetty {auto_meta.get('createdAt', '?')}")


if __name__ == "__main__":
    main()
