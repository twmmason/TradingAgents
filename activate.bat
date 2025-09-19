@echo off

REM TradingAgents Environment Setup Script for Windows
REM This script sets up and activates the virtual environment for TradingAgents

echo ================================================
echo      TradingAgents Environment Setup
echo ================================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo Dependencies installed/updated

REM Check for .env file
if not exist ".env" (
    echo.
    echo Warning: No .env file found!
    echo.
    echo Creating .env file from template...
    if exist ".env.template" (
        copy .env.template .env
        echo Created .env file from template
        echo.
        echo Please edit .env and add your API keys:
        echo    - FINNHUB_API_KEY
        echo    - GOOGLE_API_KEY
    ) else (
        REM Create a basic .env file
        echo # TradingAgents Configuration > .env
        echo FINNHUB_API_KEY=your_finnhub_api_key_here >> .env
        echo GOOGLE_API_KEY=your_google_api_key_here >> .env
        echo Created basic .env file
        echo.
        echo Please edit .env and add your API keys
    )
) else (
    echo.
    echo API keys configuration status:
    findstr /C:"FINNHUB_API_KEY=your_finnhub_api_key_here" .env >nul
    if %errorlevel%==0 (
        echo Warning: FINNHUB_API_KEY not configured in .env
    ) else (
        echo FINNHUB_API_KEY configured
    )
    
    findstr /C:"GOOGLE_API_KEY=your_google_api_key_here" .env >nul
    if %errorlevel%==0 (
        echo Warning: GOOGLE_API_KEY not configured in .env
    ) else (
        echo GOOGLE_API_KEY configured
    )
)

echo.
echo ================================================
echo Environment setup complete!
echo.
echo You are now in the TradingAgents virtual environment.
echo.
echo To run the CLI interface:
echo   python -m cli.main
echo.
echo To run a basic test:
echo   python main.py
echo.
echo To deactivate the environment:
echo   deactivate
echo ================================================