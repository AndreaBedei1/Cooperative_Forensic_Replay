@echo off
rem Manual review menu of the 22 canonical runs. Run from an activated environment: conda activate carla
cd /d "%~dp0.."
rem The replays use the CARLA 0.9.15 server already running on port 2000 (another port: --port N).
python scripts\review_canonical_runs.py --port 2000 %*
