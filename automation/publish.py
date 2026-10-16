"""Siirrä tarkistettu -auto-data tuotantoon. Ajetaan vain käyttäjän käskystä, ei koskaan automaattisesti.

Käyttö: python3 automation/publish.py
"""
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
        auto_meta, prod_meta = k["auto"].replace(".json", "_meta.json"), prod.replace(".json", "_meta.json")
        if not (ROOT / auto_meta).exists():
            sys.exit(f"Julkaisu keskeytetty: {auto_meta} puuttuu.")
        shutil.copyfile(ROOT / k["auto"], ROOT / prod)
        shutil.copyfile(ROOT / auto_meta, ROOT / prod_meta)
        print(f"{k['auto']} -> {prod}: {len(before)} -> {len(after)} näyttelyä "
              f"(+{len(after - before)} uutta, -{len(before - after)} poistunutta)")
        print(f"{auto_meta} -> {prod_meta}: päivitetty {load(prod_meta, {}).get('createdAt', '?')}")


if __name__ == "__main__":
    main()
