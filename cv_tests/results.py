"""Test results — результаты CV-тестов."""

import json
import os
from datetime import datetime


class TestResult:
    def __init__(self, test_id, game, description):
        self.test_id = test_id
        self.game = game
        self.description = description
        self.passed = None
        self.details = ""
        self.screenshot = None

    def ok(self, details=""):
        self.passed = True
        self.details = details
        return self

    def fail(self, details=""):
        self.passed = False
        self.details = details
        return self

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "game": self.game,
            "description": self.description,
            "passed": self.passed,
            "details": self.details,
            "timestamp": datetime.now().isoformat(),
        }


class TestSuite:
    def __init__(self, game_name):
        self.game = game_name
        self.results = []

    def add(self, result):
        self.results.append(result)

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed is True)
        failed = sum(1 for r in self.results if r.passed is False)
        skipped = total - passed - failed
        return {
            "game": self.game,
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{passed/total*100:.1f}%" if total else "N/A",
        }

    def save(self, path="results/report.json"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        report = {
            "game": self.game,
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary(),
            "tests": [r.to_dict() for r in self.results],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def print_report(self):
        s = self.summary()
        print(f"\n{'='*60}")
        print(f"  {self.game} — CV Test Report")
        print(f"{'='*60}")
        for r in self.results:
            icon = "✅" if r.passed else ("❌" if r.passed is False else "⬜")
            print(f"  {icon} {r.test_id}: {r.description}")
            if r.details:
                print(f"      → {r.details}")
        print(f"\n  Total: {s['total']} | Passed: {s['passed']} | Failed: {s['failed']} | Rate: {s['pass_rate']}")
        print(f"{'='*60}\n")
