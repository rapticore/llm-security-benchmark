@echo off
REM LLM Security Benchmark Runner with Virtual Environment
REM Built by the Rapticore Security Research Team

echo 🚀 Starting LLM Security Benchmark with Virtual Environment...
echo ==============================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please create one first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo 🔧 Activating virtual environment...

REM Activate virtual environment and run benchmark
call venv\Scripts\activate.bat

echo 🐍 Python version:
python --version
echo 📦 Running benchmark with consolidated modules...
echo.

REM Run the benchmark with all arguments passed through
python enhanced_multi_llm_benchmark.py %*

echo.
echo 🎉 Benchmark completed!
echo 📁 Check the benchmark_results/ directory for outputs
pause
