#!/usr/bin/env python3
"""Regenerate derived analysis of saved runs only; never acquire CARLA or call providers."""
import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def refresh(name):
    from cdf.reconstruction.pipeline import reconstruct_run
    from cdf.reconstruction.config import load_config
    from cdf.evaluation.reconstruction import evaluate_run
    from cdf.evaluation.fusion_metrics import evaluate_fusion
    from cdf.evaluation.event_oracle import compare_run
    from cdf.evaluation.run_metrics import run_metrics
    from cdf.evaluation.provenance import provenance
    run=ROOT/name
    start=time.monotonic()
    reconstruct_run(run)
    rec_time=round(time.monotonic()-start,2)
    evaluation=evaluate_run(run,clock_shift_check=name.startswith('traces/'))
    fusion=evaluate_fusion(run)
    semantic=compare_run(run,load_config())
    (run/'reconstruction/evaluation/event_oracle.json').write_text(json.dumps(semantic,indent=1)+'\n',encoding='utf-8')
    metrics=run_metrics(run,evaluation,fusion)
    prov=provenance(load_config().to_dict(),[name])
    fusion.pop('_raw',None)
    return {'run':name,'metrics':metrics,'fusion':fusion,'semantic':semantic,'provenance':prov,
            'wall_s':round(time.monotonic()-start,2)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope',choices=['canonical'],default='canonical')
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--output',type=Path,default=ROOT/'scratch/hardening_refresh.json')
    args=parser.parse_args()
    runs=[]
    runs+=sorted((ROOT/'traces').glob('S*/run_*'))
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(refresh,p.relative_to(ROOT).as_posix()):p for p in runs}
        for future in concurrent.futures.as_completed(futures):
            row=future.result();rows.append(row)
            print(row['run'],row['wall_s'],'s',row['metrics']['merges_false'],'false merges',flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(sorted(rows,key=lambda r:r['run']),indent=1)+'\n',encoding='utf-8')
    print(len(rows),'saved runs refreshed')


if __name__=='__main__':main()
