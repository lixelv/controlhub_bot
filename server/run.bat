@echo off
start /B pythonw bot.py
start uvicorn main:app --host 0.0.0.0 --reload