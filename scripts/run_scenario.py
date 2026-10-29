#!/usr/bin/env python3
"""Acquire one raw CARLA scenario run."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.common.config import available_scenarios, load_run_config
from cdf.simulation.carla_client import client_from_config
from cdf.simulation.runner import run_scenario
from cdf.simulation.scenario_base import ScenarioSpec


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire raw CARLA data for one scenario")
    parser.add_argument("--scenario", required=True, help="scenario id, for example S01")
    parser.add_argument("--variant", default=None, help="configured scenario variant")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", default="traces")
    parser.add_argument("--sensor-profile", default=None)
    parser.add_argument("--override", action="append", default=[])
    parser.add_argument("--no-autostart", action="store_true", help="do not start a local CARLA process")
    parser.add_argument("--without-participant", action="append", default=[], metavar="ID",
                        help="privileged counterfactual: run the scenario without this participant "
                             "(a trigger aimed at it never fires); use a scratch --output")
    parser.add_argument("--disable-action", action="append", default=[], metavar="ACTION_ID",
                        help="privileged counterfactual: never play this scripted action")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cfg = load_run_config(args.scenario, sensor_profile=args.sensor_profile, overrides=args.override)
    spec = ScenarioSpec.from_config(cfg, variant=args.variant)
    counterfactual = bool(args.without_participant or args.disable_action)
    if counterfactual and Path(args.output).resolve() == (ROOT / "traces").resolve():
        parser.error("a counterfactual run would overwrite the campaign run: pass a scratch --output")
    if args.without_participant:
        spec = spec.without(args.without_participant)
    for action_id in args.disable_action:
        matches = [a for p in spec.participants for a in p.actions if a.action_id == action_id]
        if not matches:
            parser.error("no action {0!r} in {1}".format(action_id, spec.scenario_id))
        for action in matches:
            action.enabled = False
    client = client_from_config(cfg, autostart=not args.no_autostart)
    path = run_scenario(client, cfg, spec, args.seed, output_root=args.output)
    if counterfactual:
        (path / "ground_truth" / "counterfactual.json").write_text(json.dumps({
            "note": "privileged offline counterfactual, not a campaign run",
            "without_participants": list(args.without_participant),
            "disabled_actions": list(args.disable_action)}, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
