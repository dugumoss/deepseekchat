@echo off
cls
start "D:\Program Files (x86)\Tencent\QQBrowser" "http://127.0.0.1:5000"
cmd /k  ".\venv\Scripts\activate && .\venv\Scripts\python.exe app.py"

