@echo off
title JARVIS V10 WHATSAPP - SERVER CORRETO
color 0A
cd /d "%~dp0"

echo Matando servidor antigo...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 >nul

echo [1/3] Tentando abrir MT5...
if exist "C:\Program Files\MetaTrader 5\terminal64.exe" start "" "C:\Program Files\MetaTrader 5\terminal64.exe"
if exist "C:\Program Files\Exness MT5\terminal64.exe" start "" "C:\Program Files\Exness MT5\terminal64.exe"
if exist "C:\Program Files\MetaTrader 5 Terminal\terminal64.exe" start "" "C:\Program Files\MetaTrader 5 Terminal\terminal64.exe"
if exist "C:\Program Files\Doo Prime MT5\terminal64.exe" start "" "C:\Program Files\Doo Prime MT5\terminal64.exe"

echo [2/3] Iniciando JARVIS V10 WHATSAPP CONSERVADORA em segundo plano...
start /min "" cmd /c "title JARVIS SERVER 5000 - V10 WHATSAPP 12H & python server.py"

echo [3/3] Aguardando servidor subir...
timeout /t 4 >nul

echo Abrindo navegador em http://127.0.0.1:5000
start "" http://127.0.0.1:5000

echo.
echo ==============================================
echo  JARVIS V10 WHATSAPP - RODANDO
echo  Server: http://127.0.0.1:5000
echo  WhatsApp: 5511954677471 todo dia 12h
echo  SL -15/+25 e -25/+45 - Fecha SO no SL/TP
echo  Grafico + MARKET GUARD + HTF + MACD + IGNICAO
echo ==============================================
echo.
echo Pode minimizar esta janela, NAO FECHE!
echo.
pause