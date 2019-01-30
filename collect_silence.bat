if not "%~1"=="p" start /min cmd.exe /c %0 p&exit
@echo off 
python collect_silence.py
