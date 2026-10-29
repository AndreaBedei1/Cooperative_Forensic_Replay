"""Absolute and relative pose error of injected GNSS against recorded poses.

Evaluation only: the recorded CARLA pose is the exact reference in this study.
Pairwise errors compare simultaneous vectors, so a common translation cancels.
"""
import json
import math
from pathlib import Path
import numpy as np
from ..reconstruction.common_frame import RecordedPoseSource


def _stats(values):
    a = np.asarray(values, dtype=float)
    return {'samples': len(a), 'rms': float(np.sqrt(np.mean(a*a))) if len(a) else None,
            'median': float(np.median(a)) if len(a) else None,
            'p50': float(np.percentile(a, 50)) if len(a) else None,
            'p95': float(np.percentile(a, 95)) if len(a) else None,
            'p99': float(np.percentile(a, 99)) if len(a) else None,
            'p995': float(np.percentile(a, 99.5)) if len(a) else None,
            'max': float(np.max(a)) if len(a) else None}


def pose_errors(run_dir: Path, pose_factory=None):
    sources, errors, by_recorder, yaw, velocity, absolute = {}, {}, {}, [], [], []
    for path in sorted((Path(run_dir)/'vehicles').glob('*/ego.jsonl')):
        records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        origin = float(records[0]['timestamp'])
        base = RecordedPoseSource(records,origin)
        source = pose_factory(path.parent,origin) if pose_factory else base
        sources[path.parent.name] = (origin,base,source)
        d = np.hypot(source.x - base.x, source.y - base.y)
        heading = np.degrees(np.abs((source.yaw - base.yaw + np.pi) % (2 * np.pi) - np.pi))
        speed = np.hypot(source.vx - base.vx, source.vy - base.vy)
        absolute.extend(d.tolist())
        yaw.extend(heading.tolist())
        velocity.extend(speed.tolist())
        errors[path.parent.name] = _stats(d)
        by_recorder[path.parent.name] = {'absolute_position_m': _stats(d), 'heading_deg': _stats(heading),
                                         'velocity_mps': _stats(speed)}
    pairs, relative = {}, []
    names = sorted(sources)
    for i,a in enumerate(names):
        ao,ab,ap = sources[a]
        for b in names[i+1:]:
            bo,bb,bp = sources[b]
            begin,end = max(ao+ab.start,bo+bb.start),min(ao+ab.end,bo+bb.end)
            ts = np.arange(begin,end+1e-6,.1)
            ax,ay,_ = ap.poses_at(ts-ao);bx,by,_ = bp.poses_at(ts-bo)
            tx,ty,_ = ab.poses_at(ts-ao);ux,uy,_ = bb.poses_at(ts-bo)
            d = np.hypot((bx-ax)-(ux-tx),(by-ay)-(uy-ty))
            relative.extend(d.tolist());pairs[a+'/'+b] = _stats(d)
    return {'absolute_position_m': _stats(absolute), 'relative_position_m': _stats(relative),
            'heading_deg': _stats(yaw), 'velocity_mps': _stats(velocity), 'recorders': errors,
            'by_recorder': by_recorder, 'pairs': pairs,
            'reference':'recorded exact CARLA poses, evaluation only; simultaneous recorder pairs'}
