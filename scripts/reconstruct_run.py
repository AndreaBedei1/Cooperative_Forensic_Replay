from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.reconstruction.config import load_config
from cdf.reconstruction.pipeline import reconstruct_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Local graphs -> global graph for recorded runs")
    parser.add_argument("run_dirs", nargs="+", type=Path, help="run directories such as traces/S01/run_0_crash")
    parser.add_argument("--config", type=Path, default=None, help="reconstruction YAML (default configs/reconstruction.yaml)")
    parser.add_argument("--evaluate", action="store_true",
                        help="afterwards, compare the written reconstruction with ground_truth/ (privileged)")
    args = parser.parse_args()
    cfg = load_config(args.config)
    for run_dir in args.run_dirs:
        result = reconstruct_run(run_dir, cfg)
        print("{0}: {1}".format(run_dir, result.output_dir))
        for local in result.locals:
            print("  local {0}: {1} trace frames, {2} graph nodes, {3} edges, {4} radar track(s)".format(
                local.owner, len(local.trace), len(local.graph.nodes), len(local.graph.edges), len(local.tracks)))
        for name, clock in sorted(result.alignment.graphs.items()):
            print("  clock {0}: {1} offset_to_global={2}".format(name, clock.status, clock.offset_to_global))
        for item in result.associations:
            print("  track {0}:{1} -> {2} ({3}, confidence {4})".format(
                item.local_graph, item.local_track, item.global_entity, item.status, item.confidence))
        for entity in result.road_users.entities if result.road_users else []:
            print("  road user {0}: {1} ({2})".format(entity["id"], ", ".join(entity["source_tracks"]),
                                                     entity["fusion_method"]))
        print("  global: {0} nodes, {1} edges".format(len(result.graph.nodes), len(result.graph.edges)))
        if args.evaluate:
            from cdf.evaluation.reconstruction import evaluate_run
            evaluation = evaluate_run(run_dir)
            print("  evaluation: {0}".format(evaluation["headline"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
