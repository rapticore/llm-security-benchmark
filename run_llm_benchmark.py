#!/usr/bin/env python3
"""
LLM Security Benchmark - Main Entry Point
Built by the Rapticore Security Research Team

This is the main entry point for running the LLM Security Benchmark.
All the actual implementation is in the src/ package.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function
if __name__ == "__main__":
    from run_llm_benchmark import main
    main()
