import unittest

from scripts.scenarios import ROOT, SCENARIOS, scenario_runs


class ScenarioTests(unittest.TestCase):
    def test_registry_matches_all_recorded_scenario_runs(self):
        self.assertEqual(set(SCENARIOS), {
            "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10",
            "S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19",
        })
        selected = {path.relative_to(ROOT / "traces").as_posix() for path in scenario_runs()}
        recorded = {
            path.relative_to(ROOT / "traces").as_posix()
            for path in (ROOT / "traces").glob("S*/run_*")
            if path.is_dir()
        }
        self.assertEqual(selected, recorded)
        self.assertEqual(len(selected), 22)


if __name__ == "__main__":
    unittest.main()
