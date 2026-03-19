@echo off
chcp 65001 >NUL
title 停止所有 Codex 服务
echo ===================================================
echo   正在停止所有 Codex 服务...
echo ===================================================

echo [1/3] 正在停止代理后端 (cli-proxy-api.exe)...
taskkill /F /IM cli-proxy-api.exe /T > NUL 2>&1

echo [2/3] 正在停止前端面板服务 (node.exe)...
taskkill /F /IM node.exe /T > NUL 2>&1

echo [3/3] 正在停止自动打工脚本 (python.exe)...
taskkill /F /IM python.exe /T > NUL 2>&1

echo ===================================================
echo   [成功] 所有后台服务已被彻底停止。
echo ===================================================
pause
