"""Separate privileged simulator-state trace for acquisition runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class GroundTruthLogger:
    def __init__(self, root: Path, metadata: Dict[str, Any]) -> None:
        self.root = Path(root) / "ground_truth"
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "metadata.json").write_text(json.dumps(metadata, sort_keys=True, indent=2), encoding="utf-8")
        self.states = (self.root / "states.jsonl").open("w", encoding="utf-8")
        self.controls = (self.root / "controls.jsonl").open("w", encoding="utf-8")
        self.collisions = (self.root / "collisions.jsonl").open("w", encoding="utf-8")
        self.triggers = None
        self._closed = False

    def state(self, record: Dict[str, Any]) -> None:
        self.states.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def collision(self, record: Dict[str, Any]) -> None:
        self.collisions.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def control(self, record: Dict[str, Any]) -> None:
        self.controls.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def trigger(self, record: Dict[str, Any]) -> None:
        """A scripted action fired by a privileged trigger (scenario construction only)."""
        if self.triggers is None:
            self.triggers = (self.root / "triggers.jsonl").open("w", encoding="utf-8")
        self.triggers.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def close(self) -> None:
        if not self._closed:
            self.states.close()
            self.controls.close()
            self.collisions.close()
            if self.triggers is not None:
                self.triggers.close()
            self._closed = True
