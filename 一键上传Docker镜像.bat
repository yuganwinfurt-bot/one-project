@echo off
setlocal
title one-project Docker image publisher
set "PUBLISH_SCRIPT=%~dp0docker\publish-images.ps1"
if not exist "%PUBLISH_SCRIPT%" (
    echo Missing file: "%PUBLISH_SCRIPT%"
    pause
    exit /b 1
)
echo Opening the Docker image publisher...
echo Keep this console open until the publisher window closes.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -STA -ExecutionPolicy RemoteSigned -File "%PUBLISH_SCRIPT%"
set "PUBLISH_EXIT_CODE=%ERRORLEVEL%"
if not "%PUBLISH_EXIT_CODE%"=="0" (
    echo.
    echo Publisher could not start or exited with an error. Read the message above.
    pause
)
exit /b %PUBLISH_EXIT_CODE%
