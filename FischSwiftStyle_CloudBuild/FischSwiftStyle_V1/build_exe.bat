@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name FischSwiftStyle main.py
echo EXE should be in dist\FischSwiftStyle.exe
pause
