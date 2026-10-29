from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]

SCENARIOS: Dict[str, Tuple[str, ...]] = {
    "S01": ("crash",),
    "S02": ("crash",),
    "S03": ("crash",),
    "S04": ("a_front_pushed", "b_rear_first"),
    "S05": ("crash",),
    "S06": ("crash",),
    "S07": ("merge_conflict",),
    "S08": ("rolls_through",),
    "S09": ("near_simultaneous",),
    "S10": ("deflected_into_c",),
    "S11": ("consequential",),
    "S12": ("crash",),
    "S13": ("abreast", "platoon", "passing"),
    "S14": ("surrounded",),
    "S15": ("dense_platoon",),
    "S16": ("overtaking",),
    "S17": ("occlusion_reappearance",),
    "S18": ("collision_ambiguity",),
    "S19": ("highway_curve",),
}


def scenario_runs(traces_root: Optional[Path] = None) -> List[Path]:
    root = Path(traces_root) if traces_root is not None else ROOT / "traces"
    return [root / scenario / ("run_0_" + variant)
            for scenario in sorted(SCENARIOS)
            for variant in SCENARIOS[scenario]]
