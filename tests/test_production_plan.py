from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_production_plan import validate_plan  # noqa: E402


class ProductionPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads((ROOT / "assets" / "production-plan.example.json").read_text(encoding="utf-8"))

    def test_example_plan_is_valid(self) -> None:
        errors, _, summary = validate_plan(self.plan)
        self.assertEqual(errors, [])
        self.assertEqual(summary["mode"], "launch")
        self.assertEqual(summary["duration"], 41.0)

    def test_illustrative_scene_cannot_be_proof(self) -> None:
        self.plan["scenes"][2]["source"] = {
            "type": "generated",
            "truthStatus": "illustrative",
        }
        errors, _, _ = validate_plan(self.plan)
        self.assertTrue(any("illustrative scene as proof" in error for error in errors))

    def test_duration_ceiling_is_enforced(self) -> None:
        self.plan["project"]["maxDuration"] = 20
        errors, _, _ = validate_plan(self.plan)
        self.assertTrue(any("exceeds" in error for error in errors))

    def test_pitch_requires_problem_and_solution(self) -> None:
        self.plan["project"]["mode"] = "pitch"
        errors, _, _ = validate_plan(self.plan)
        self.assertTrue(any("problem" in error and "solution" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
