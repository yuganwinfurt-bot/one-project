@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHON_EXE=D:\Python\python.exe"
if exist "D:\node\npm.cmd" set "PATH=D:\node;%PATH%"

if not exist "%PYTHON_EXE%" (
  echo 没找到 Python：%PYTHON_EXE%
  goto failed
)
where.exe npm.cmd >nul 2>nul
if errorlevel 1 (
  echo 没找到 npm，请先安装 Node.js。
  goto failed
)

if exist "D:\Ollama\ollama.exe" (
  echo 正在检查 Ollama...
  curl.exe --silent --fail --noproxy "*" --max-time 1 "http://127.0.0.1:11434/api/tags" >nul 2>nul
  if errorlevel 1 (
    echo Ollama 未运行，正在启动本机 Ollama...
    start "Ollama" /b "D:\Ollama\ollama.exe" serve
    timeout /t 8 /nobreak >nul
  )
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo 正在创建独立 Python 环境...
  "%PYTHON_EXE%" -m venv "backend\.venv"
  if errorlevel 1 goto failed
)
echo 正在检查后端依赖...
"backend\.venv\Scripts\python.exe" -c "import fastapi, uvicorn, langchain, langgraph, langchain_chroma, langchain_ollama, langchain_community, langchain_text_splitters, httpx, multipart, dotenv, pypdf, docx2txt, PIL, rapidocr" >nul 2>nul
if errorlevel 1 (
  echo 正在安装后端依赖，首次启动需要等待一会儿...
  "backend\.venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
  if errorlevel 1 goto failed
)
if not exist "frontend\node_modules\.bin\vite.cmd" (
  echo 正在安装前端依赖...
  call npm.cmd install --prefix "frontend" --no-audit --no-fund
  if errorlevel 1 goto failed
)
if not exist "backend\.env" copy "backend\.env.example" "backend\.env" >nul
if /i "%~1"=="--prepare-only" exit /b 0

rem 两个服务共用当前终端，不再额外弹出两个窗口。
start "RAG Backend" /b /D "%~dp0backend" "%ComSpec%" /d /c ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "RAG Frontend" /b /D "%~dp0frontend" "%ComSpec%" /d /c "npm.cmd run dev"
"backend\.venv\Scripts\python.exe" "wait_ready.py"
if errorlevel 1 goto failed
start "" "http://127.0.0.1:4173"
echo 页面已就绪：http://127.0.0.1:4173
echo 前端和后端已在当前终端中运行，请保持这个窗口打开。
echo 按任意键关闭本启动窗口。
pause >nul
exit /b 0

:failed
echo.
echo 启动失败，请保留上方报错，或查看 RAG Backend 和 RAG Frontend 窗口。
if /i "%~1"=="--prepare-only" exit /b 1
pause
exit /b 1
