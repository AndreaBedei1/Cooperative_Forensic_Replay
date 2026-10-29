#!/usr/bin/env python3
"""Small privileged check using GT geometry directly, no reconstruction event functions.

Checks PERFECT oracle onsets before first contact. True oriented bodies, a sampled
outline, explicit cut-in persistence and an independent SAT/braking predicate.
The checker intentionally has no import from cdf.reconstruction or event_oracle.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('CUT_IN_FROM_LEFT_START', 'CUT_IN_FROM_RIGHT_START', 'EGO_PATH_ENTRY', 'CRITICAL_TTC_START')


def records(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def rotation(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s], [s, c]])


def geometry(state):
    tf, ext = state['transform'], state['bbox_extent']
    return np.array([tf['x'], tf['y']]), math.radians(tf['yaw_deg']), np.array([ext['x'], ext['y']])


def outline(centre, yaw, half):
    corners = np.array([[-1,-1],[1,-1],[1,1],[-1,1]]) * half
    points = []
    for a,b in zip(corners, np.roll(corners,-1,axis=0)):
        n = max(2, int(np.linalg.norm(a-b)/0.05)+1)
        points.extend(a+(b-a)*u for u in np.linspace(0,1,n))
    return np.asarray(points) @ rotation(yaw).T + centre


def overlaps(ca, ya, ha, cb, yb, hb):
    """Separating-axis test, vectorised over forecast time."""
    ua, ub = rotation(ya).T, rotation(yb).T
    delta = cb-ca
    good = np.ones(len(delta), dtype=bool)
    for axis in list(ua)+list(ub):
        ra = np.sum(np.abs(ua@axis)*ha)
        rb = np.sum(np.abs(ub@axis)*hb)
        good &= np.abs(delta@axis) <= ra+rb+1e-9
    return good


def travel(speed, acceleration, times):
    if acceleration < 0:
        t = np.minimum(times, speed/max(-acceleration,1e-9))
    else:
        t = times
    return speed*t+0.5*acceleration*t*t


def independent_pair(rows, owner, target, origin, end, cfg):
    events, path, cut_run, cut_active, critical = [], None, None, False, False
    anchor = None
    for frame in rows:
        if owner not in frame or target not in frame:
            continue
        own, other = frame[owner], frame[target]
        t = round(own['timestamp']-origin,4)
        if t >= end or t < 0: continue
        ca, ya, ha = geometry(own)
        cb, yb, hb = geometry(other)
        if anchor is None:
            anchor = (ca.copy(),ya)
        basis = rotation(ya)
        boundary = (outline(cb,yb,hb)-ca)@basis
        d = np.maximum(np.abs(boundary)-ha,0)
        near = boundary[np.argmin(np.sum(d*d,axis=1))]
        va = np.array([own['velocity']['x'],own['velocity']['y']])
        vb = np.array([other['velocity']['x'],other['velocity']['y']])
        speed_a, speed_b = np.linalg.norm(va),np.linalg.norm(vb)
        relative = (vb-va)@basis
        lateral, ahead = float(near[1]),float(near[0]-ha[0])
        # Independently use SAT against a finite rectangle containing the full
        # forward half-strip that could touch this body, rather than its point.
        body_centre=(cb-ca)@basis
        far=max(float(np.max(boundary[:,0]))+1.,ha[0]+1.)
        def in_path(front,half_width):
            centre=np.array([(front+far)/2,0.])
            return bool(np.max(boundary[:,0])>front and overlaps(centre[None],0.,((far-front)/2,half_width),
                                                               body_centre[None],yb-ya,hb)[0])
        inside=in_path(ha[0],cfg['path_half_width_m'])
        outside=not in_path(ha[0]-cfg['path_hysteresis_m'],cfg['path_half_width_m']+cfg['path_hysteresis_m'])
        if path is None: path = inside
        elif not path and inside:
            events.append(dict(type='EGO_PATH_ENTRY',t_local=t)); path=True
        elif path and outside: path=False

        heading = math.atan2(vb[1],vb[0]) if speed_b>1e-6 else yb
        heading_rel = (math.degrees(heading-ya)+180)%360-180
        body = (np.array([[-1,-1],[1,-1],[1,1],[-1,1]])*hb)@rotation(yb).T+cb
        body = (body-ca)@basis
        body_gap = max(float(np.min(body[:,1]))-cfg['path_half_width_m'],
                       -float(np.max(body[:,1]))-cfg['path_half_width_m'],0)
        stable_body=(body@basis.T+ca-anchor[0])@rotation(anchor[1])
        stable_gap=max(float(np.min(stable_body[:,1]))-cfg['path_half_width_m'],
                       -float(np.max(stable_body[:,1]))-cfg['path_half_width_m'],0)
        side = -1 if float(np.mean(stable_body[:,1]))<0 else 1
        target_lateral=float((vb@rotation(anchor[1]))[1])
        toward = -side*target_lateral
        stable_heading=(math.degrees(heading-anchor[1])+180)%360-180
        moving = ahead>0 and abs(stable_heading)<=cfg['cut_in_max_heading_deg'] and speed_b>=cfg['cut_in_min_target_speed_mps']
        if not cut_active:
            if moving and toward>=cfg['cut_in_lateral_speed_mps']:
                if cut_run is None or cut_run[1]!=side: cut_run=(t,side,stable_gap)
                due=stable_gap/toward<=cfg['cut_in_horizon_s']
                if (cut_run[2]>=cfg['cut_in_outside_margin_m'] and
                    cut_run[2]-stable_gap>=cfg['cut_in_min_displacement_m'] and
                    t-cut_run[0]>=cfg['cut_in_persistence_s']-1e-6 and due and stable_gap<=cfg['cut_in_preentry_margin_m']):
                    events.append(dict(type='CUT_IN_FROM_'+('LEFT' if side<0 else 'RIGHT')+'_START',t_local=t));cut_active=True
            else:cut_run=None
        # The subset tests first cut-in onset; no shared release implementation.
        clearance = max(float(np.min(body[:,0]))-ha[0],0)
        same_direction=abs(heading_rel)<=30
        front=bool(np.min(body[:,0])>ha[0] and body_gap<=1e-9)
        entering=body_gap<=cfg['critical_front_lateral_margin_m'] and -(-1 if lateral<0 else 1)*relative[1]>=cfg['critical_front_lateral_speed_mps']+0.05
        table=np.array(cfg['critical_time_gap_table'])
        required=max(speed_a*np.interp(speed_a*3.6,table[:,0],table[:,1]),cfg['critical_min_following_distance_m'])
        unsafe=bool(speed_a>=cfg['critical_forward_min_speed_mps'] and same_direction and (front or entering) and clearance<required)
        times=np.arange(0,cfg['prediction_horizon_s']+1e-9,cfg['prediction_time_step_s'])
        accel=other.get('acceleration',{})
        target_acc=(accel.get('x',0)*vb[0]+accel.get('y',0)*vb[1])/max(speed_b,1e-9)
        target_acc=target_acc if target_acc<=-cfg['target_braking_min_mps2'] else 0
        target_positions=cb+travel(speed_b,target_acc,times)[:,None]*(vb/max(speed_b,1e-9))
        inflated=ha+np.array([cfg['critical_standstill_margin_m'],cfg['critical_lateral_margin_m']])
        course=np.any(overlaps(ca+times[:,None]*va,ya,inflated,target_positions,yb,hb))
        reacted=np.maximum(times-cfg['critical_reaction_time_s'],0)
        dist=speed_a*np.minimum(times,cfg['critical_reaction_time_s'])+travel(speed_a,-cfg['critical_deceleration_mps2'],reacted)
        braking=np.any(overlaps(ca+dist[:,None]*(va/max(speed_a,1e-9)),ya,inflated,target_positions,yb,hb))
        if np.any(overlaps(np.repeat(ca[None],len(times),axis=0),ya,inflated,target_positions,yb,hb)):
            # Rear/side approach: even stopping the observer instantly does not
            # remove the course; test the approaching target's braking instead.
            target_dist=speed_b*np.minimum(times,cfg['critical_reaction_time_s'])+travel(speed_b,-cfg['critical_deceleration_mps2'],reacted)
            braking=np.any(overlaps(ca+times[:,None]*va,ya,inflated,
                                     cb+target_dist[:,None]*(vb/max(speed_b,1e-9)),yb,hb))
        now=bool(unsafe or (course and braking))
        if now and not critical and t>=cfg['critical_min_track_age_s']-1e-6:
            events.append(dict(type='CRITICAL_TTC_START',t_local=t));critical=True
        # First hazard onset only: debounced ends are outside this independent subset.
    return events


def check_run(run, cfg):
    frames={}
    for row in records(run/'ground_truth/states.jsonl'):
        frames.setdefault(row['frame'],{})[row['participant_id']]=row
    all_rows=[frames[f] for f in sorted(frames)]
    contacts=records(run/'ground_truth/collisions.jsonl')
    main=json.loads((run/'reconstruction/evaluation/event_oracle.json').read_text())['events']['PERFECT']
    result=[]
    for vd in sorted((run/'vehicles').iterdir()):
        if not (vd/'ego.jsonl').exists():continue
        owner=vd.name; origin=records(vd/'ego.jsonl')[0]['timestamp']
        end=min([r['timestamp']-origin for r in contacts if r['participant_id']==owner] or [float('inf')])
        for target in sorted({pid for frame in all_rows for pid in frame if pid!=owner}):
            found=independent_pair(all_rows,owner,target,origin,end,cfg)
            for kind in KINDS:
                expected=[e['t_local'] for e in main.get(owner,[]) if e['subject']==target and e['type']==kind and e['t_local']<end]
                actual=[e['t_local'] for e in found if e['type']==kind]
                if not expected and not actual:continue
                a=actual[0] if actual else None;b=expected[0] if expected else None
                result.append(dict(run=run.relative_to(ROOT).as_posix(),observer=owner,target=target,event=kind,
                                   main=b,independent=a,delta=None if a is None or b is None else round(a-b,4)))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',nargs='+',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/audit/event_oracle_independent_check.json')
    args=parser.parse_args()
    cfg=yaml.safe_load((ROOT/'configs/reconstruction.yaml').read_text())['reconstruction']['semantics']
    rows=[r for run in args.runs for r in check_run(run.resolve(),cfg)]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'method':'Independent GT body geometry; PERFECT, pre-contact, first onset per pair/type',
                                     'limitations':'Same true oriented body; no shared event functions; independent SAT/braking and straight forecast instead of yaw-rate arcs; first onsets only',
                                     'rows':rows},indent=2)+'\n',encoding='utf-8')
    lines=['# Independent event-oracle check','',
           'Privileged evaluation only. Direct GT body geometry/control kinematics; no reconstruction event generator.',
           'Comparison: PERFECT oracle, before each observer\'s first contact, first onset per pair/type.','',
           '| run | pair | event | main [s] | independent [s] | delta [s] |','|---|---|---|---|---|---|']
    for r in rows:
        lines.append('| {run} | {observer}→{target} | {event} | {main} | {independent} | {delta} |'.format(**r))
    lines+=['','Checker differences are diagnostic: same true oriented body, independent SAT/braking test,',
            'straight forecasts instead of yaw-rate arcs, first onsets only. No definitions are changed to force agreement.','']
    args.output.with_suffix('.md').write_text('\n'.join(lines),encoding='utf-8')
    print(len(rows),'onsets checked')


if __name__=='__main__':main()
