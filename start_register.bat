@echo off
chcp 65001 >NUL
title Codex AI Suite - 仅启动自动注册脚本
echo ===================================================
echo   [1/1] 正在启动 Codex 自动注册打工脚本...
echo ===================================================
cd /d d:\AI\PythonProject\Codex\
start /b "" cmd /c "conda activate Customer_Service_Model && python codex_auto_register/codex/protocol_keygen.py"

echo ===================================================
echo   [成功] 自动注册脚本已启动！
echo   日志会在终端中显示。
echo   停止脚本请按 Ctrl+C 或关闭终端窗口。
echo ===================================================
