@echo off
rem Windows: find a suitable Python and hand over to install.py.
rem All the work is in install.py; this file only looks for the interpreter.
rem Messages are in English on purpose: cmd shows non-ASCII text as garbage
rem unless the code page happens to match.
setlocal
set "HERE=%~dp0"
set "CHECK=import sys; sys.exit(sys.version_info < (3, 10))"
set "CODE=2"

py -3 -c "%CHECK%" >nul 2>&1
if not errorlevel 1 (
    py -3 "%HERE%install.py" %*
    goto finished
)

python -c "%CHECK%" >nul 2>&1
if not errorlevel 1 (
    python "%HERE%install.py" %*
    goto finished
)

echo Python 3.10 or newer was not found.
echo.
echo Install it with:
echo     winget install Python.Python.3.12
echo or from https://www.python.org/downloads/ - tick "Add python.exe to PATH".
echo Then open this file again.
goto leave

:finished
set "CODE=%ERRORLEVEL%"

:leave
rem Started by double click: keep the window, or the result vanishes with it.
if "%~1"=="" (
    echo.
    pause
)
exit /b %CODE%
