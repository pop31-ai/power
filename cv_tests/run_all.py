"""CV Tests — main runner. Запуск всех тестов для 3 игр."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from tests.cosmic_bubbles import run_all as run_cb
from tests.shatter_zone import run_all as run_sz
from tests.rig_master import run_all as run_rm


GAMES = {
    "cosmic_bubbles": ("Cosmic Bubbles", run_cb),
    "shatter_zone":   ("Shatter Zone",   run_sz),
    "rig_master":     ("Rig Master",     run_rm),
}


def main():
    parser = argparse.ArgumentParser(description="CV Test Runner")
    parser.add_argument("--game", "-g", choices=list(GAMES.keys()),
                        help="Запуск только одной игры (по умолчанию все)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  CV Test Runner — Cosmic Bubbles + Shatter Zone + Rig Master")
    print("=" * 60)
    print("\n  Dependencies:")
    print("    pip install opencv-python pytesseract numpy Pillow pyautogui")
    print("    + Tesseract OCR (https://github.com/tesseract-ocr/tesseract)")
    print()

    all_results = {}
    targets = {args.game: GAMES[args.game]} if args.game else GAMES

    for key, (name, run_fn) in targets.items():
        print(f"\n--- {name} ---")
        try:
            summary = run_fn()
            all_results[name] = summary
        except Exception as e:
            print(f"  ERROR running {name}: {e}")
            all_results[name] = {"error": str(e)}

    if len(targets) > 1:
        print("\n" + "=" * 60)
        print("  COMBINED REPORT")
        print("=" * 60)
        total = passed = failed = skipped = 0
        for name, s in all_results.items():
            if "error" in s:
                print(f"  {name}: ERROR — {s['error']}")
                continue
            t = s.get("total", 0)
            p = s.get("passed", 0)
            f = s.get("failed", 0)
            sk = s.get("skipped", 0)
            total += t
            passed += p
            failed += f
            skipped += sk
            rate = s.get("pass_rate", "N/A")
            print(f"  {name}: {t} total | {p} passed | {f} failed | {sk} skipped | rate: {rate}")
        print(f"\n  TOTAL: {total} tests | {passed} passed | {failed} failed | {skipped} skipped")
        if total:
            print(f"  OVERALL PASS RATE: {passed/total*100:.1f}%")
        print("=" * 60)


if __name__ == "__main__":
    main()
