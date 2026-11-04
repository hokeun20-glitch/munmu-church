@echo off
chcp 65001 > nul
echo ========================================================
echo   육군학생군사학교 문무대교회 웹 플랫폼을 시작합니다.
echo ========================================================
cd /d "C:\Users\369rental\Desktop\종교시설 홈페이지"
start http://localhost:8000
py -3.11 run.py
pause
