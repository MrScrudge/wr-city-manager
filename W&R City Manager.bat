@echo off
chcp 65001 >nul
setlocal
rem W-and-R City Manager launcher: finds Python 3.10+ (installs it if missing), installs the packages once, starts the program.
rem Python + PySide6, numpy, pillow, openpyxl; pipette: rapidocr-onnxruntime
set "PY="
set "PYW="

call :find
if defined PY goto have

echo.
echo   Python 3.10+ не знайдено. Встановлюю (один раз, потрібен інтернет)...
echo   Python 3.10+ not found. Installing it (once, internet required)...
where winget >nul 2>nul
if errorlevel 1 goto nowinget
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
call :find
if defined PY goto have
for %%D in ("%LOCALAPPDATA%\Programs\Python\Python312" "%LOCALAPPDATA%\Programs\Python\Python313" "%LOCALAPPDATA%\Programs\Python\Python311") do (
  if not defined PY if exist "%%~D\python.exe" (
    set "PY=%%~D\python.exe"
    set "PYW=%%~D\pythonw.exe"
  )
)
if defined PY goto have

:nowinget
echo.
echo   UA: Не вдалося встановити Python автоматично. Встанови його з https://www.python.org/downloads/ (познач "Add python.exe to PATH") і запусти цей файл знову.
echo   EN: Could not install Python automatically. Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH") and run this file again.
start "" https://www.python.org/downloads/
pause
exit /b 1

:have
"%PY%" -c "import PySide6, numpy, PIL, openpyxl" >nul 2>nul
if errorlevel 1 (
  echo   Встановлюю потрібні модулі - один раз, кілька хвилин...
  echo   Installing the required modules - once, a few minutes...
  "%PY%" -m pip install PySide6 numpy pillow openpyxl
  if errorlevel 1 goto failed
)
"%PY%" -c "import rapidocr_onnxruntime, cv2" >nul 2>nul
if errorlevel 1 (
  echo   Встановлюю модуль розпізнавання для піпетки - один раз, близько хвилини...
  echo   Installing the recognition module for the pipette - once, about a minute...
  "%PY%" -m pip install rapidocr-onnxruntime
)
if not defined PYW set "PYW=%PY%"
start "" "%PYW%" "%~dp0wr_calc.py" --setup
exit /b 0

:failed
echo.
echo   UA: Не вдалося встановити модулі. Перевір інтернет і запусти файл ще раз.
echo   EN: Could not install the modules. Check your internet connection and run this file again.
pause
exit /b 1

:find
for %%C in (py python) do (
  if not defined PY (
    %%C -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set "PY=%%C"
  )
)
if /i "%PY%"=="py" (set "PYW=pyw") else if defined PY (set "PYW=pythonw")
exit /b 0
