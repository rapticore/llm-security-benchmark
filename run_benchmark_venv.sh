#!/bin/bash

# LLM Security Benchmark Runner with Virtual Environment
# Built by the Rapticore Security Research Team

echo "🚀 Starting LLM Security Benchmark with Virtual Environment..."
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run benchmark
echo "✅ Virtual environment found"
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🐍 Python version: $(python --version)"
echo "📦 Running benchmark with consolidated modules..."
echo ""

# Run the benchmark with all arguments passed through
python enhanced_multi_llm_benchmark.py "$@"

echo ""
echo "🎉 Benchmark completed!"
echo "📁 Check the benchmark_results/ directory for outputs"
