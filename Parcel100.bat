@echo off
cd /d "%~dp0"
py -3 Parcel100.py
if errorlevel 1 pause
