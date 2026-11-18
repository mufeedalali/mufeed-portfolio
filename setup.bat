@echo off
REM Setup script for RAG Pipeline on Windows

echo Setting up RAG Pipeline...

REM Check Python version
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vector_db" mkdir data\vector_db
if not exist "logs" mkdir logs

REM Create .env file from example if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created. Please update with your settings if needed.
)

echo Setup complete!
echo.
echo To start the development server:
echo   venv\Scripts\activate.bat
echo   uvicorn app.api.main:app --reload
echo.
echo To run the CLI:
echo   python -m cli.main --help
echo.
echo To run tests:
echo   pytest
pause
