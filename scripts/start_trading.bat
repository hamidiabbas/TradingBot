@echo off
echo 🤖 Starting Enhanced Trading Bot...

REM Activate virtual environment
call trading_env\Scripts\activate.bat

REM Check if models exist
if not exist "models\windows_training_summary.json" (
    echo ⚠️ No trained models found!
    echo Please run training first
    pause
    exit /b 1
)

REM Start the trading system
echo 🚀 Launching trading system...
python core\bot_engine.py

pause
