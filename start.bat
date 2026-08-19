@echo off
setlocal
set ROOT=%~dp0
set COMPONENT=%1
if "%COMPONENT%"=="" set COMPONENT=stack
if not exist "%ROOT%.venv\Scripts\python.exe" (echo Bitte zuerst setup.bat ausfuehren.& exit /b 1)
if not exist "%ROOT%.pwtool.local.json" (echo Lokale Konfiguration fehlt. Bitte setup.bat ausfuehren.& exit /b 1)
set HOST=127.0.0.1
set BIND_MODE=local
if /I "%PWTOOL_BIND%"=="lan" set BIND_MODE=lan
if /I "%PWTOOL_BIND%"=="lan" if /I not "%COMPONENT%"=="backend" (
  echo LAN-Modus startet nur das lokale Backend fuer einen TLS-Reverse-Proxy. Nutze: set PWTOOL_BIND=lan ^& start.bat backend
  exit /b 2
)
set PYTHONPATH=%ROOT%backend
"%ROOT%.venv\Scripts\python.exe" "%ROOT%scripts\validate_runtime.py" --config "%ROOT%.pwtool.local.json" --bind %BIND_MODE%
if errorlevel 1 exit /b 1
if /I "%COMPONENT%"=="backend" goto backend
if /I "%COMPONENT%"=="frontend" goto frontend
if /I "%COMPONENT%"=="stack" goto stack
echo Nutzung: start.bat [backend^|frontend^|stack]
exit /b 2
:backend
set PWTOOL_CONFIG=%ROOT%.pwtool.local.json
set PYTHONPATH=%ROOT%backend
"%ROOT%.venv\Scripts\python.exe" -m uvicorn main:app --app-dir "%ROOT%backend" --host %HOST% --port 8000
exit /b %ERRORLEVEL%
:frontend
pnpm --dir "%ROOT%frontend" dev
exit /b %ERRORLEVEL%
:stack
start "PW-Tool Backend" cmd /c "%~f0 backend"
goto frontend
