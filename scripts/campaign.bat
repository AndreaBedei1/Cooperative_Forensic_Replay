@echo off
rem Frozen robustness campaign: status / pause / stop-now / resume / start (works without the chat session).
rem   scripts\campaign.bat status     progress, concurrency, resources, estimated remaining time
rem   scripts\campaign.bat pause      no new jobs; running jobs finish and are recorded; then the controller exits
rem   scripts\campaign.bat stop-now   terminate running jobs now (not recorded, pending again); then exit
rem   scripts\campaign.bat resume     verify the frozen version and continue (completed jobs are skipped)
rem   scripts\campaign.bat workers 20 fixed concurrency while RAM, page file and disk hold (workers auto: adaptive)
setlocal
cd /d "%~dp0.."
set PY=%USERPROFILE%\.conda\envs\carla\python.exe
if not exist "%PY%" set PY=python
if "%~1"=="" (
  "%PY%" scripts\campaign_controller.py status
) else (
  "%PY%" scripts\campaign_controller.py %*
)
endlocal
