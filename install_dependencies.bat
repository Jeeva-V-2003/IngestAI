@echo off
cd /d "%~dp0"
echo 📦 Installing Python packages...
pip install -r requirements.txt

echo 🧭 Installing Playwright browser support...
playwright install

echo 🚀 Launching SmartWebAI-Synth UI...
python main_ui.py

pause
