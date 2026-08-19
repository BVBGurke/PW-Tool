@echo off
setlocal
set ROOT=%~dp0
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% -m venv "%ROOT%.venv"
"%ROOT%.venv\Scripts\python.exe" -m pip install --upgrade pip
"%ROOT%.venv\Scripts\python.exe" -m pip install -r "%ROOT%backend\requirements.txt"
pnpm --dir "%ROOT%frontend" install
pnpm --dir "%ROOT%website" install
"%ROOT%.venv\Scripts\python.exe" "%ROOT%scripts\init_config.py" --path "%ROOT%.pwtool.local.json"
echo Einrichtung abgeschlossen. Starte lokal mit start.bat
