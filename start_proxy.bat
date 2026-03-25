@echo off
chcp 65001 >NUL
title Codex AI Suite - 仅启动反代 + 前端
echo ===================================================
echo   [1/2] 正在启动 CLI Proxy API 反代后端...
echo ===================================================
cd /d d:\AI\PythonProject\Codex
start /b "" cli-proxy-api.exe

PING localhost -n 3 >NUL

echo ===================================================
echo   [2/2] 正在启动前端 Web 管理面板...
echo ===================================================
cd /d d:\AI\PythonProject\Codex\Cli-Proxy-API-Management-Center-1.7.7\
start /b "" cmd /c "npm run dev"

echo ===================================================
echo   [成功] 反代后端 + 前端面板已启动！
echo   - 反代 API 地址: http://127.0.0.1:9544
echo   - 管理面板地址: http://127.0.0.1:9533
echo   注意: 未启动自动注册脚本。
echo   停止服务请运行: stop_all.bat
echo ===================================================
