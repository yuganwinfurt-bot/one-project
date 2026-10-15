"""恢复本机 RAG 后端，并让服务独立于本次工具调用存活。"""
from pathlib import Path
import os
import subprocess
import httpx

root=Path(__file__).resolve().parents[2]
try:
    response=httpx.get('http://127.0.0.1:8000/api/health',timeout=3,trust_env=False)
    response.raise_for_status()
    print('后端已运行')
except httpx.HTTPError:
    env=os.environ.copy()
    env['NO_PROXY']='127.0.0.1,localhost,::1'
    env['PYTHONUTF8']='1'
    startup=subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=0
    out=(root/'logs/backend.jibot-import.stdout.log').open('ab')
    err=(root/'logs/backend.jibot-import.stderr.log').open('ab')
    child=subprocess.Popen(
        [str(root/'backend/.venv/Scripts/python.exe'),'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'],
        cwd=root/'backend',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
        startupinfo=startup,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_BREAKAWAY_FROM_JOB,
    )
    print('后端进程已启动：',child.pid)
