@echo off
chcp 65001 >NUL
title Codex AI Suite - 全部启动
echo ===================================================
echo   [1/3] 正在启动 CLI Proxy API 反代后端...
echo ===================================================
echo ===================================================
echo   [预处理] 正在清理已失效的认证文件...
echo ===================================================
cd /d d:\AI\PythonProject\Codex
python clean_expired_auth_files.py

cd /d d:\AI\PythonProject\Codex
start /b "" cli-proxy-api.exe

PING localhost -n 3 >NUL

echo ===================================================
echo   [2/3] 正在启动前端 Web 管理面板...
echo ===================================================
cd /d d:\AI\PythonProject\Codex\Cli-Proxy-API-Management-Center-1.7.7\
start /b "" cmd /c "npm run dev"

PING localhost -n 3 >NUL

echo ===================================================
echo   [3/3] 正在启动 Codex 自动注册打工脚本...
echo ===================================================
cd /d d:\AI\PythonProject\Codex\
start /b "" cmd /c "conda activate Customer_Service_Model && python codex_auto_register/codex/protocol_keygen.py"

echo ===================================================
echo   [成功] 所有服务已在当前终端启动！
echo   日志会在这里交替打印。
echo   停止服务请运行: stop_all.bat
echo ===================================================
