@echo off
cd /d "%~dp0"
echo ==========================================
echo JARVIS V10.5 - BACKTEST ENGINE
echo ==========================================
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist "data\sample_M15.csv" python backtest_engine.py --generate-sample
python backtest_engine.py --csv data\sample_M15.csv --symbol XAUUSDm
echo.
echo Relatorios salvos em:
echo %~dp0reports
pause
