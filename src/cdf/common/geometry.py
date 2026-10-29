"""Planar geometry helpers for fixed CARLA routes and controllers."""

from __future__ import annotations

import math

__all__ = ["angle_diff_deg", "distance"]


def angle_diff_deg(a: float, b: float) -> float:
    """Return the signed shortest difference ``a-b`` in degrees."""
    return (float(a) - float(b) + 180.0) % 360.0 - 180.0


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(float(x2) - float(x1), float(y2) - float(y1))
