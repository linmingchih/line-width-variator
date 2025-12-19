@echo off
setlocal EnableDelayedExpansion

echo Checking for uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv not found. Installing uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Try to add likely install locations to PATH for this session
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    ) else if exist "%LOCALAPPDATA%\bin\uv.exe" (
        set "PATH=%LOCALAPPDATA%\bin;%PATH%"
    )
)

REM Verify uv is now accessible
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv is still not found in PATH.
    echo Please restart your terminal or add uv to your PATH manually.
    pause
    exit /b 1
)

echo Syncing Python environment...
call uv sync
if %errorlevel% neq 0 (
    echo Failed to sync environment.
    pause
    exit /b 1
)

echo Starting Line Width Variator...
call uv run app.py

if %errorlevel% neq 0 (
    echo Application exited with error code %errorlevel%.
    pause
)

endlocal
