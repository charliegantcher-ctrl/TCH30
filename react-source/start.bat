@echo off
rem Starts the TCH30 React site using the portable Node in ..\tools\node (no install needed).
setlocal
cd /d "%~dp0"
set "NODE_DIR=%~dp0..\tools\node"
if not exist "%NODE_DIR%\node.exe" (
  echo Portable Node not found at %NODE_DIR%
  echo Download the "Windows Binary (.zip)" from https://nodejs.org/en/download and unzip it there.
  pause
  exit /b 1
)
set "PATH=%NODE_DIR%;%PATH%"
if not exist node_modules (
  echo Installing dependencies, first run only...
  call npm.cmd install --no-fund --no-audit || (pause & exit /b 1)
)
echo.
echo  TCH30 is starting - your browser will open by itself.
echo  Keep this window open while you use the site. Close it to stop.
echo.
call npm.cmd run dev -- --open
pause
