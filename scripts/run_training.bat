@echo off
echo 🚀 Starting ML Training Pipeline...

REM Activate virtual environment
call trading_env\Scripts\activate.bat

REM Check if data exists
if not exist "data\training\mt5_historical_data.h5" (
    echo ❌ Training data not found!
    echo Please run data collection first
    pause
    exit /b 1
)

REM Run training
echo 🧠 Running Windows-optimized training...
python ml_training\windows_optimized_training_pipeline.py

echo 🎉 Training completed!
pause
