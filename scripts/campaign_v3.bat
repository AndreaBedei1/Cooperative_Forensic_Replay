@echo off
rem Campaign v3 (docs/CAMPAIGN_V3.md), run from the worktree of the tag campaign-v3, independent of any chat session.
rem   scripts\campaign_v3.bat start      verify the freeze against the manifest, then start detached
rem   scripts\campaign_v3.bat status     progress, concurrency, resources, estimated remaining time
rem   scripts\campaign_v3.bat pause      no new jobs; running jobs finish and are recorded; then the controller exits
rem   scripts\campaign_v3.bat stop-now   terminate running jobs now (not recorded, pending again); then exit
rem   scripts\campaign_v3.bat resume     verify the freeze and continue (completed jobs are skipped)
rem   scripts\campaign_v3.bat workers 12 fixed concurrency while RAM, page file and disk hold (workers auto: adaptive)
rem Results: results\robustness\campaign_v3\ of this worktree (jobs.jsonl, control\); scratch copies: CDF_CAMPAIGN_WORK.
setlocal
cd /d "%~dp0.."
set PY=%USERPROFILE%\.conda\envs\carla\python.exe
if not exist "%PY%" set PY=python
if "%CARLA_ROOT%"=="" set CARLA_ROOT=F:\Carla9_15\WindowsNoEditor
set CDF_CAMPAIGN_VERSION_TAG=campaign-v3
set CDF_CAMPAIGN_RESULTS=%CD%\results\robustness\campaign_v3
set CDF_CAMPAIGN_MANIFEST=%CD%\results\robustness\campaign_v3\manifest.json
if "%CDF_CAMPAIGN_WORK%"=="" set CDF_CAMPAIGN_WORK=F:\CarlaGraph_campaign_v3_work
if "%CDF_CAMPAIGN_START_WORKERS%"=="" set CDF_CAMPAIGN_START_WORKERS=10
set FAMILIES=baseline,gnss,radar_v3,radar_asym,radar_gnss_v3,radar_asym_gnss
if "%~1"=="" (
  "%PY%" scripts\campaign_controller.py status
) else if /i "%~1"=="start" (
  "%PY%" scripts\campaign_controller.py start --families %FAMILIES%
) else if /i "%~1"=="resume" (
  "%PY%" scripts\campaign_controller.py resume --families %FAMILIES%
) else (
  "%PY%" scripts\campaign_controller.py %*
)
endlocal
