@echo off
echo 🚀 Setting up Trading Bot Windows Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv trading_env

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call trading_env\Scripts\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing requirements...
pip install -r requirements-windows.txt

REM Create necessary directories
echo 📁 Creating directories...
mkdir models\lstm 2>nul
mkdir models\random_forest 2>nul
mkdir models\svm 2>nul
mkdir models\ensemble 2>nul
mkdir data\training 2>nul
mkdir data\processed 2>nul
mkdir logs 2>nul

echo ✅ Setup completed successfully!
echo 🎯 To activate the environment, run: trading_env\Scripts\activate.bat
echo 🚀 To start training, run: python ml_training\windows_optimized_training_pipeline.py
pause
