@echo off
chcp 65001 >NUL
title Codex AI Suite - 清理失效认证文件
echo ===================================================
echo   正在清理已失效的认证文件...
echo ===================================================
cd /d d:\AI\PythonProject\Codex
python clean_expired_auth_files.py

echo ===================================================
echo   [成功] 清理完成！
echo ===================================================
pause
