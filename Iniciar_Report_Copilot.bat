@echo off
title Siemens SAT Report Copilot
chcp 65001 > nul
cls
echo ===================================================================
echo             SIEMENS SAT REPORT COPILOT (FASTAPI + IA GEMINI)
echo ===================================================================
echo.
cd /d "%~dp0"

REM 1. Procurar um Python REAL no computador (IGNORANDO o atalho da Microsoft Store / WindowsApps)
set "REAL_PY="

REM Verificar se o comando py existe e funciona
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -c "import sys" >nul 2>nul
    if %errorlevel% equ 0 (
        set "REAL_PY=py"
        goto FOUND_PYTHON
    )
)

REM Procurar em 'where python', filtrando o atalho falso da Microsoft Store
for /f "delims=" %%I in ('where python 2^>nul') do (
    echo %%I | findstr /i "WindowsApps" >nul
    if errorlevel 1 (
        "%%I" -c "import sys" >nul 2>nul
        if %errorlevel% equ 0 (
            if not defined REAL_PY set "REAL_PY=%%I"
        )
    )
)
if defined REAL_PY goto FOUND_PYTHON

REM Procurar em pastas padrao de instalacao do Python
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "REAL_PY=%LocalAppData%\Programs\Python\Python311\python.exe" & goto FOUND_PYTHON
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "REAL_PY=%LocalAppData%\Programs\Python\Python312\python.exe" & goto FOUND_PYTHON
if exist "%ProgramFiles%\Python311\python.exe" set "REAL_PY=%ProgramFiles%\Python311\python.exe" & goto FOUND_PYTHON
if exist "%ProgramFiles%\Python312\python.exe" set "REAL_PY=%ProgramFiles%\Python312\python.exe" & goto FOUND_PYTHON

REM 2. Se nao encontrou nenhum Python real, instalar 100% automaticamente
echo [INFO] O Python ainda nao se encontra instalado neste computador.
echo [INFO] A iniciar instalacao 100%% automatica (sem necessidade de Administrador)...
echo.

if exist "%~dp0Instalador_Python_3.11.exe" (
    echo [INFO] A executar o Instalador oficial do Python 3.11 incluido na pasta...
    set "INSTALLER=%~dp0Instalador_Python_3.11.exe"
) else (
    echo [INFO] A descarregar o Instalador oficial do Python 3.11...
    set "INSTALLER=%TEMP%\python_installer.exe"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', $env:INSTALLER)"
)

echo.
echo ===================================================================
echo  A INSTALAR PYTHON 3.11 (Aguarde a barra de progresso terminar)...
echo ===================================================================
echo.
"%INSTALLER%" /passive PrependPath=1 Include_pip=1 Include_test=0 SimpleInstall=1

REM Aguardar alguns segundos para o sistema registar o executavel
timeout /t 4 >nul

REM Localizar o executavel acabado de instalar
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "REAL_PY=%LocalAppData%\Programs\Python\Python311\python.exe"
    set "PATH=%LocalAppData%\Programs\Python\Python311;%LocalAppData%\Programs\Python\Python311\Scripts;%PATH%"
    goto FOUND_PYTHON
)
if exist "%ProgramFiles%\Python311\python.exe" (
    set "REAL_PY=%ProgramFiles%\Python311\python.exe"
    set "PATH=%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts;%PATH%"
    goto FOUND_PYTHON
)

REM Caso o instalador tenha concluido mas precise de reabrir
echo.
echo [INFO] A instalacao do Python 3.11 foi concluida!
echo Se o servidor nao arrancar agora, basta voltar a clicar duas vezes neste BAT.
echo.

:FOUND_PYTHON
echo.
echo [1/2] A verificar dependencias necessarias (fastapi, uvicorn, cryptography)...
"%REAL_PY%" -c "import fastapi, uvicorn, cryptography" >nul 2>nul
if %errorlevel% equ 0 goto START_SERVER

echo [INFO] A primeira execucao requer instalar as bibliotecas.
echo A instalar dependencias via pip (fastapi, uvicorn, cryptography)...
echo Por favor aguarde cerca de 15 a 30 segundos...
echo.
"%REAL_PY%" -m pip install -r requirements.txt

:START_SERVER
echo.
echo [2/2] A iniciar o servidor e abrir o Copilot no navegador...
echo Interface: http://127.0.0.1:5050
echo.
"%REAL_PY%" server.py
if %errorlevel% neq 0 (
    echo.
    echo Ocorreu um erro ao executar o servidor.
    pause
)
