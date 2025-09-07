@echo off
python %* 2>error.tmp
if %errorlevel% neq 0 (
    echo.
    echo 🦜 Popat detected an error! Let me help...
    .\target\debug\popat.exe analyze --file error.tmp --language python
    echo.
    echo --- Original Error ---
    type error.tmp
    del error.tmp
) else (
    del error.tmp 2>nul
)