@echo off
title CivicSense Web App Server
echo ====================================================
echo Starting CivicSense Web Server on http://localhost:5000
echo ====================================================
start http://localhost:5000
py app.py
pause
