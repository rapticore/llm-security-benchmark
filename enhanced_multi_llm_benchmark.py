#!/usr/bin/env python3
"""
Enhanced Multi-LLM Security Benchmark
Advanced security analysis benchmark with comprehensive model support and executive reporting.

Built by the Rapticore Security Research Team.

Supported Models:
Premium (Highest Accuracy): GPT-5, Claude Opus 4, Gemini 2.5 Pro
Balanced (Speed + Accuracy): GPT-4o, Claude Sonnet 4
Fast (Cost-Effective): GPT-5-mini, GPT-4o-mini, Gemini 2.5 Flash

Features:
- Executive summary reports
- Performance analysis
- Strategic recommendations
- Cost-effectiveness analysis
- Multi-dimensional benchmarking

Usage:
    python enhanced_multi_llm_benchmark.py --models "gpt-5,claude-opus-4,gemini-2.5-pro"
"""
import argparse
import json
import os
import random
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Tuple, List, Dict

from dotenv import load_dotenv

# Import QFS audit-compliant modules  
try:
    from qfs_config import CONFIG, calculate_qfs, bootstrap_ci, validate_dataset
    from qfs_analysis import (
        load_and_validate_results, calculate_slice_metrics,
        create_accuracy_bars_with_ci, create_pareto_frontier_plot,
        create_qfs_heatmap, generate_quality_first_executive_report,
        generate_changelog
    )

    QFS_AUDIT_AVAILABLE = True
    print("✅ QFS audit modules loaded - using methodologically consistent analysis")
except ImportError as e:
    QFS_AUDIT_AVAILABLE = False
    print(f"⚠️ QFS audit modules not available: {e}")
    print("   Falling back to original QFS calculation")

# Import cost-effectiveness analysis
try:
    from cost_effectiveness_analysis import (
        apply_aggressive_fixes_list,
        create_enhanced_effectiveness_report
    )

    ENHANCED_EFFECTIVENESS_AVAILABLE = True
    print("✅ Enhanced cost-effectiveness analysis available")
except ImportError as e:
    ENHANCED_EFFECTIVENESS_AVAILABLE = False
    print(f"⚠️ Enhanced cost-effectiveness not available: {e}")
    print("   Using traditional cost-effectiveness calculations")

# Import simplified policy modules
try:
    from simplified_config import get_config, update_config
    from simplified_metrics import (
        encode_row_simple, aggregate_slice_simple, 
        calculate_percentages, breadth_coverage
    )
    SIMPLIFIED_POLICY_AVAILABLE = True
    print("✅ Simplified policy modules loaded - using enhanced assessment framework")
except ImportError as e:
    SIMPLIFIED_POLICY_AVAILABLE = False
    print(f"⚠️ Simplified policy modules not available: {e}")
    print("   Using legacy assessment framework")

# Import chart generation
try:
    from chart_generation import (
        integrate_improved_charts,
        generate_language_effectiveness_chart_from_dict,
        generate_owasp_effectiveness_chart
    )

    IMPROVED_CHARTS_AVAILABLE = True
    print("✅ Chart generation available")
except ImportError as e:
    IMPROVED_CHARTS_AVAILABLE = False
    print(f"⚠️ Chart generation not available: {e}")
    print("   Using traditional chart generation")

# Import technical reporter
try:
    from technical_reporter import (
        generate_engineering_technical_report
    )

    TECHNICAL_REPORTER_AVAILABLE = True
    print("✅ Technical reporter available")
except ImportError as e:
    TECHNICAL_REPORTER_AVAILABLE = False
    print(f"⚠️ Technical reporter not available: {e}")
    print("   Using basic reporting only")

# Import executive summary with integrated reporter functionality
try:
    from executive_summary import (
        generate_enhanced_unified_executive_summary,
        EnhancedUnifiedReporter
    )

    EXECUTIVE_SUMMARY_AVAILABLE = True
    print("✅ Executive summary with integrated reporter available")
except ImportError as e:
    EXECUTIVE_SUMMARY_AVAILABLE = False
    print(f"⚠️ Executive summary not available: {e}")
    print("   Using basic reporting only")

# Import API clients
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. Install with: pip install openai")

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic library not available. Install with: pip install anthropic")

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: Google Generative AI library not available. Install with: pip install google-generativeai")

try:
    import requests

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Requests library not available for Ollama. Install with: pip install requests")

# DeepSeek uses OpenAI-compatible API, so no separate import needed
DEEPSEEK_AVAILABLE = OPENAI_AVAILABLE

# X.AI Grok also uses OpenAI-compatible API
XAI_AVAILABLE = OPENAI_AVAILABLE

# Llama API providers (can use OpenAI-compatible endpoints)
LLAMA_AVAILABLE = OPENAI_AVAILABLE

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("❌ Visualization libraries not available!")
    print("   Install with: pip install matplotlib seaborn pandas numpy")
    print("   Charts and graphs will be skipped.")

import yaml

# ---------------------------- Enhanced Config ----------------------------
# Model categories
# Comprehensive model categories - ALL testable models for objective benchmarking
PREMIUM_MODELS = ["gpt-5", "claude-opus-4", "gemini-2.5-flash", "grok-4", "grok-3", "deepseek-reasoner",
                  "deepseek-chat"]  # Include ALL premium models
BALANCED_MODELS = ["gpt-4o", "claude-sonnet-4", "gemini-2.0-flash", "grok-3", "deepseek-chat",
                   "llama-3.3-70b"]  # All balanced models
FAST_MODELS = ["gpt-5-mini", "gpt-4o-mini", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "grok-3-mini",
               "grok-code-fast-1", "llama-3.3-11b"]  # All fast models

# Local models (excluded from 'all' by default - require explicit selection)
LOCAL_MODELS = ["ollama/llama3.3", "ollama/deepseek-r1", "ollama/qwen2.5", "ollama/gemma2", "ollama/mistral"]

# API models only (excluding local models by default)
ALL_MODELS = PREMIUM_MODELS + BALANCED_MODELS + FAST_MODELS

DEFAULT_MODELS = [
    "gpt-4o-mini", "claude-sonnet-4"
]

DEFAULT_TIMEOUT_S = 45  # Increased for comprehensive testing of all models including slower ones
FIRST_SHOT_TOKENS = 256
RETRY_SHOT_TOKENS = 384
STARVED_RATIO = 0.70

# Enhanced model pricing (per 1M tokens)
DEFAULT_PRICING = {
    # OpenAI models
    "gpt-5": {"in": 3.0, "out": 15.0},
    "gpt-5-mini": {"in": 1.0, "out": 4.0},
    "gpt-4o": {"in": 2.5, "out": 10.0},
    "gpt-4o-mini": {"in": 0.15, "out": 0.6},

    # Anthropic models
    "claude-opus-4": {"in": 15.0, "out": 75.0},
    "claude-sonnet-4": {"in": 3.0, "out": 15.0},

    # Google models
    "gemini-2.5-flash": {"in": 0.075, "out": 0.3},
    "gemini-2.5-flash-lite": {"in": 0.0375, "out": 0.15},
    "gemini-2.0-flash": {"in": 0.075, "out": 0.3},
    "gemini-2.0-flash-lite": {"in": 0.0375, "out": 0.15},

    # X.AI Grok models (updated with official pricing)
    "grok-4": {"in": 3.0, "out": 15.0},
    "grok-code-fast-1": {"in": 0.2, "out": 1.5},
    "grok-3": {"in": 3.0, "out": 15.0},
    "grok-3-mini": {"in": 0.3, "out": 0.5},

    # DeepSeek models (updated pricing from official docs)
    "deepseek-chat": {"in": 0.14, "out": 0.28},  # DeepSeek V3.1 non-thinking mode
    "deepseek-reasoner": {"in": 0.55, "out": 2.19},  # DeepSeek V3.1 thinking mode
    "deepseek-coder": {"in": 0.14, "out": 0.28},  # Legacy model

    # Meta Llama models (via API providers)
    "llama-3.3-70b": {"in": 0.9, "out": 0.9},
    "llama-3.3-11b": {"in": 0.2, "out": 0.2},
    "llama-3.2-90b": {"in": 1.2, "out": 1.2},
    "llama-3.2-11b": {"in": 0.15, "out": 0.15},

    # Local models (Ollama) - no cost
    "ollama/llama3.3": {"in": 0.0, "out": 0.0},
    "ollama/deepseek-r1": {"in": 0.0, "out": 0.0},
    "ollama/qwen2.5": {"in": 0.0, "out": 0.0},
    "ollama/gemma2": {"in": 0.0, "out": 0.0},
    "ollama/mistral": {"in": 0.0, "out": 0.0},
    "ollama/codegemma": {"in": 0.0, "out": 0.0},
    "ollama/phi3": {"in": 0.0, "out": 0.0}
}

# Test suite definitions
DEFAULT_SUITE_FILES = {
    "basic": "test_suites/security_basic.yaml",
    "fast": "test_suites/security_fast.yaml",
    "comprehensive": "test_suites/security_comprehensive.yaml",
    "owasp": "test_suites/owasp_top10.yaml",
    "python": "test_suites/security_python_comprehensive.yaml",
    "javascript": "test_suites/security_javascript.yaml",
    "typescript": "test_suites/security_typescript.yaml",
    "go": "test_suites/security_go.yaml",
    "rust": "test_suites/security_rust.yaml",
    "java": "test_suites/security_java.yaml",
    "kotlin": "test_suites/security_kotlin.yaml",
    "swift": "test_suites/security_swift.yaml",
    "c": "test_suites/security_c.yaml",
    "cpp": "test_suites/security_cpp.yaml",
    "csharp": "test_suites/security_csharp.yaml",
    "scala": "test_suites/security_scala.yaml",
    "dart": "test_suites/security_dart.yaml",
    "php": "test_suites/security_php.yaml",
    "ruby": "test_suites/security_ruby.yaml",
    "haskell": "test_suites/security_haskell.yaml",

    # Combinations
    "all": ["basic", "comprehensive", "owasp", "python", "javascript", "typescript", "go", "rust", "java", "kotlin",
            "swift", "c", "cpp", "csharp", "scala", "dart", "php", "ruby", "haskell"],
    "enterprise": ["comprehensive", "java", "kotlin", "csharp", "scala", "python"],
    "web_dev": ["javascript", "typescript", "python", "php", "java"],
    "mobile": ["kotlin", "swift", "dart"],
    "systems": ["c", "cpp", "rust", "go"],
    "memory_safe": ["java", "kotlin", "csharp", "scala", "python", "javascript", "typescript", "dart", "haskell"],
    "memory_unsafe": ["c", "cpp"],
    "functional": ["haskell", "scala", "rust"],
    "all_languages": ["python", "javascript", "typescript", "go", "rust", "java", "kotlin", "swift", "c", "cpp",
                      "csharp", "scala", "dart", "php", "ruby", "haskell"]
}


# -------------------------- Enhanced Data Types --------------------------
@dataclass
class EnhancedRunResult:
    suite_id: str
    model: str
    path: str
    ok: bool
    elapsed_s: float
    text: str = ""
    error: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    cost_usd: Optional[float] = None
    score: float = 0.0
    criteria_met: List[str] = None
    criteria_missed: List[str] = None
    must_not_violations: List[str] = None
    perfect_score: bool = False
    response_quality: str = "unknown"  # excellent, good, poor

    def __post_init__(self):
        if self.criteria_met is None:
            self.criteria_met = []
        if self.criteria_missed is None:
            self.criteria_missed = []
        if self.must_not_violations is None:
            self.must_not_violations = []
        self.perfect_score = self.score >= 0.95
        self.response_quality = self._assess_quality()

    def _assess_quality(self) -> str:
        if self.score >= 0.9:
            return "excellent"
        elif self.score >= 0.7:
            return "good"
        elif self.score >= 0.4:
            return "fair"
        else:
            return "poor"


@dataclass
class ModelPerformance:
    model_name: str
    total_tests: int
    successful_tests: int
    success_rate: float
    avg_score: float
    avg_response_time: float
    total_cost: float
    cost_per_test: float
    perfect_scores: int
    good_scores: int
    poor_scores: int
    score_std_dev: float
    cost_effectiveness: float  # score per dollar
    speed_score: float  # inverse of avg response time
    total_input_tokens: int
    total_output_tokens: int
    avg_input_tokens_per_test: float
    avg_output_tokens_per_test: float

    @classmethod
    def from_results(cls, model_name: str, results: List[EnhancedRunResult]):
        successful = [r for r in results if r.ok]
        failed = [r for r in results if not r.ok]
        total_tests = len(results)
        successful_tests = len(successful)

        # For fair comparison, failed tests get 0 score and max response time penalty
        all_scores = [r.score for r in successful] + [0.0] * len(failed)  # Failed tests = 0 score
        all_response_times = [r.elapsed_s for r in results]  # Include all response times

        # Calculate costs for all attempted tests (successful + failed attempts still cost money)
        costs = [r.cost_usd for r in results if r.cost_usd is not None and r.cost_usd > 0]

        # Token accounting
        total_input_tokens = sum(r.input_tokens for r in results if r.input_tokens is not None)
        total_output_tokens = sum(r.output_tokens for r in results if r.output_tokens is not None)

        if total_tests == 0:
            return cls(
                model_name=model_name, total_tests=total_tests, successful_tests=0,
                success_rate=0.0, avg_score=0.0, avg_response_time=0.0,
                total_cost=0.0, cost_per_test=0.0, perfect_scores=0, good_scores=0, poor_scores=total_tests,
                score_std_dev=0.0, cost_effectiveness=0.0, speed_score=0.0,
                total_input_tokens=0, total_output_tokens=0, avg_input_tokens_per_test=0.0,
                avg_output_tokens_per_test=0.0
            )

        # Use all scores (including 0 for failures) for fair comparison
        avg_score = statistics.mean(all_scores) if all_scores else 0.0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
        total_cost = sum(costs)
        cost_per_test = total_cost / total_tests if total_tests > 0 else 0.0  # Cost per ALL tests attempted

        perfect_scores = sum(1 for r in successful if r.perfect_score)
        good_scores = sum(1 for r in results if r.score >= 0.6)  # Count all tests with scores >= 0.6 as good
        poor_scores = sum(1 for r in results if r.score < 0.4)  # Count all tests with scores < 0.4 as poor

        score_std_dev = statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0

        # Enhanced cost-effectiveness calculation that prioritizes accuracy and usability
        if cost_per_test > 0 and avg_score > 0:
            # Base effectiveness (traditional approach)
            base_effectiveness = avg_score / cost_per_test

            # Quality multiplier: severely penalize models with low average scores
            # Models below 0.4 average score are essentially unusable for security analysis
            if avg_score < 0.4:
                quality_multiplier = 0.1  # Almost worthless regardless of cost
            elif avg_score < 0.6:
                quality_multiplier = 0.4  # Poor quality, limited usefulness
            elif avg_score < 0.7:
                quality_multiplier = 0.7  # Fair quality
            elif avg_score < 0.8:
                quality_multiplier = 0.9  # Good quality
            else:
                quality_multiplier = 1.0  # Excellent quality

            # Reliability multiplier: penalize models with high failure rates
            # Failed tests waste money and provide no value
            reliability_multiplier = successful_tests / total_tests  # 0.0 to 1.0

            # Consistency multiplier: reward consistent performance
            # High standard deviation means unpredictable results
            consistency_multiplier = max(0.5, 1.0 - (score_std_dev * 2))  # 0.5 to 1.0

            # Final cost-effectiveness: accuracy is paramount for security analysis
            cost_effectiveness = (base_effectiveness * quality_multiplier *
                                  reliability_multiplier * consistency_multiplier)
        else:
            cost_effectiveness = 0.0

        speed_score = 1.0 / avg_response_time if avg_response_time > 0 else 0.0

        # Token averages
        avg_input_tokens_per_test = total_input_tokens / total_tests if total_tests > 0 else 0.0
        avg_output_tokens_per_test = total_output_tokens / total_tests if total_tests > 0 else 0.0

        return cls(
            model_name=model_name,
            total_tests=total_tests,
            successful_tests=successful_tests,
            success_rate=successful_tests / total_tests,
            avg_score=avg_score,
            avg_response_time=avg_response_time,
            total_cost=total_cost,
            cost_per_test=cost_per_test,
            perfect_scores=perfect_scores,
            good_scores=good_scores,
            poor_scores=poor_scores,
            score_std_dev=score_std_dev,
            cost_effectiveness=cost_effectiveness,
            speed_score=speed_score,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            avg_input_tokens_per_test=avg_input_tokens_per_test,
            avg_output_tokens_per_test=avg_output_tokens_per_test
        )


# ------------------------ Google Gemini Integration -------------------------

# ----------------------------------------- working improved --------------


def run_gemini(
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """
    Run Google Gemini models, attempting to resolve failures for non-lite models
    on code vulnerability identification tasks by adjusting generation configuration.
    """
    if not GOOGLE_AVAILABLE:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Gemini", ok=False,
            elapsed_s=0.0, error="Google Generative AI library not available"
        )

    t0 = time.time()
    try:
        # Map model names to API models
        model_mapping = {
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
            "gemini-2.0-flash": "gemini-2.0-flash",
            "gemini-2.0-flash-lite": "gemini-2.0-flash-lite"
        }

        api_model = model_mapping.get(model, "gemini-2.5-flash")
        gemini_model = genai.GenerativeModel(api_model)

        full_prompt = f"{sys_msg}\n\n{prompt}"
        if json_mode:
            full_prompt += "\n\nPlease respond in valid JSON format only."

        # Configure generation settings.
        # We are removing explicit thinking_config here to let models use their default.
        # The prompt instruction will be used to guide behavior.
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=FIRST_SHOT_TOKENS,
            temperature=0.0 if json_mode else 0.2,
            # thinking_config is removed to revert to default behavior
        )

        # Re-introducing the explicit instruction to prevent thinking, as the API parameter
        # might not be consistently handled across all models or versions for this task.
        # This prompt-based instruction can be more universally understood by the models.
        # We're keeping it concise and focused on the output format.
        # The previous instruction was "Provide a direct, concise security analysis. Do not show reasoning steps or thinking process."
        # Let's refine it for clarity and to ensure it doesn't interfere with output generation.
        # "Analyze the provided code for security vulnerabilities. Provide a direct and concise output, listing only the vulnerabilities found. Do not include reasoning, explanations, or any introductory/concluding remarks."
        # However, based on your report where flash-lite (which previously worked) is now failing,
        # it might be that the instruction *itself* is too restrictive, or that the models interpret "no reasoning"
        # as "no analysis at all".
        #
        # Let's try a slightly different approach for the prompt:
        # Instead of *forcing* no thinking, let's guide the output.
        # The original prompt was `f"Provide a direct, concise security analysis. Do not show reasoning steps or thinking process.\n\n{full_prompt}"`.
        # The issue might be that "Do not show reasoning steps or thinking process" is too strong.
        #
        # Let's try to remove that *specific* negative constraint and rely on the model's default.
        # The `full_prompt` construction remains the same, without the added negative constraint.
        # If the models are expected to identify vulnerabilities, they *need* to do some analysis (thinking).
        # The problem might be that *showing* their thinking is what was disabled, not the thinking itself.
        #
        # Let's revert to a simpler prompt construction for `full_prompt` and rely on the API's default behavior for each model type.
        # The previous `flash-lite` success might have been coincidental or due to a slightly different prompt setup.
        # The failure of `gemini-2.5-flash` and `gemini-2.0-flash` is the primary concern now.
        #
        # Re-evaluate the prompt construction:
        # `full_prompt = f"{sys_msg}\n\n{prompt}"`
        # If `json_mode` is true, it adds `\n\nPlease respond in valid JSON format only.`
        # This seems reasonable. The problem might lie in the model's interpretation of the *task* (code vulnerability identification).
        #
        # Let's try a prompt specifically tailored for vulnerability identification, which might be more effective.
        # This prompt is more direct about *what* to do.
        # The instruction `Provide a direct, concise security analysis. Do not show reasoning steps or thinking process.`
        # might be the culprit. If we remove it, the models *can* think and provide analysis.
        #
        # The prompt construction logic will be:
        # `full_prompt = f"{sys_msg}\n\n{prompt}"`
        # If `json_mode` is true, append the JSON instruction.
        # This will allow the models to use their default "thinking" capabilities.

        # The prompt structure is now:
        # `sys_msg` + `prompt`
        # If `json_mode` is true, add JSON instruction.

        # Original problematic line:
        # full_prompt = f"Provide a direct, concise security analysis. Do not show reasoning steps or thinking process.\n\n{full_prompt}"
        # This line is REMOVED.

        response = gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )

        # Extract text from response with better error handling
        text = ""
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            # Check if content was blocked
            if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                finish_reason = str(candidate.finish_reason)
                if finish_reason in ['SAFETY', 'RECITATION', 'OTHER']:
                    print(f"DEBUG: Gemini {model} content blocked - reason: {finish_reason}")
                    text = f"[Content blocked: {finish_reason}]"
            elif hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    # Ensure we are extracting text correctly
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            text += part.text
                    text = text.strip()

        # Fallback to direct text attribute
        if not text and hasattr(response, 'text') and response.text:
            text = response.text.strip()

        # Debug logging for empty responses
        if not text:
            print(f"DEBUG: Gemini {model} returned empty response")
            print(f"DEBUG: Response object: {type(response)}")
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                print(f"DEBUG: Candidate finish_reason: {getattr(candidate, 'finish_reason', 'None')}")
                print(f"DEBUG: Candidate content: {getattr(candidate, 'content', 'None')}")
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"DEBUG: Content parts: {getattr(candidate.content, 'parts', 'None')}")
                    for i, part in enumerate(candidate.content.parts):
                        print(f"DEBUG: Content part {i}: {getattr(part, 'text', 'No text attribute')}")

        # Estimate token usage (Gemini doesn't provide detailed usage info)
        # Using a rough estimation based on character count might be more accurate than word count for code.
        # However, word count is simpler for now.
        input_tokens = len(full_prompt) / 4  # Approx tokens per word. A more robust tokenizer would be better.
        output_tokens = len(text) / 4 if text else 0
        total_tokens = input_tokens + output_tokens

        cost_usd = estimate_cost(model, int(input_tokens), int(output_tokens), pricing)

        if text:
            return EnhancedRunResult(
                suite_id=suite_id, model=model, path="Gemini", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=int(input_tokens), output_tokens=int(output_tokens),
                total_tokens=int(total_tokens), cost_usd=cost_usd
            )
        else:
            return EnhancedRunResult(
                suite_id=suite_id, model=model, path="Gemini", ok=False,
                elapsed_s=time.time() - t0, error="Empty response"
            )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Gemini", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


# ------------------------ Enhanced OpenAI Integration -------------------------

def _unpack_usage(usage) -> tuple[int, int, int]:
    if not usage:
        return 0, 0, 0
    inp = _get(usage, "input_tokens", _get(usage, "prompt_tokens", 0)) or 0
    out = _get(usage, "output_tokens", _get(usage, "completion_tokens", 0)) or 0
    details = _get(usage, "output_tokens_details", {}) or {}
    reasoning = _get(details, "reasoning_tokens", 0) or 0
    return inp, out, reasoning


def run_openai_enhanced(
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Enhanced OpenAI runner with better error handling."""
    if not OPENAI_AVAILABLE:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="OpenAI", ok=False,
            elapsed_s=0.0, error="OpenAI library not available"
        )

    client = OpenAI()
    t0 = time.time()

    try:
        if model.startswith("gpt-5"):
            # Use optimized Responses API for GPT-5 models with low reasoning
            result = run_gpt5_optimized(client, model, sys_msg, prompt, timeout)

            usage = getattr(result, 'usage', None) or {}
            input_tokens = getattr(usage, 'input_tokens', 0)
            output_tokens = getattr(usage, 'output_tokens', 0)
            reasoning_tokens = getattr(getattr(usage, 'output_tokens_details', {}), 'reasoning_tokens', 0)

            cost_usd = estimate_cost(model, input_tokens, output_tokens, pricing)

            return EnhancedRunResult(
                suite_id=suite_id, model=model, path=result.path, ok=result.ok,
                elapsed_s=result.elapsed_s, text=result.text, error=getattr(result, 'error', ''),
                input_tokens=input_tokens, output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd
            )
        else:
            # Use Chat API for GPT-4 models
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=FIRST_SHOT_TOKENS,
                temperature=0.0 if json_mode else 0.2,
                timeout=timeout
            )

            text = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            reasoning_tokens = 0

            path = "Chat"

        inp, out, r = _unpack_usage(response.usage)
        cost_usd = estimate_cost(model, inp, out, pricing)

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path=path, ok=bool(text),
            elapsed_s=time.time() - t0, text=text,
            input_tokens=input_tokens, output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd
        )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="OpenAI", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


# ------------------------ Enhanced Anthropic Integration -------------------------
def run_anthropic_enhanced(
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Enhanced Anthropic runner."""
    if not ANTHROPIC_AVAILABLE:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Anthropic", ok=False,
            elapsed_s=0.0, error="Anthropic library not available"
        )

    client = anthropic.Anthropic()
    t0 = time.time()

    try:
        # Map model names to API models
        api_model = {
            "claude-opus-4.1": "claude-opus-4-1-20250805",  # Update when Opus 4 available
            "claude-sonnet-4": "claude-sonnet-4-20250514"
        }.get(model, "claude-sonnet-4-20250514")

        response = client.messages.create(
            model=api_model,
            max_tokens=FIRST_SHOT_TOKENS,
            system=sys_msg,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0 if json_mode else 0.2
        )

        text = response.content[0].text if response.content else ""
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        cost_usd = estimate_cost(model, input_tokens, output_tokens, pricing)

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Messages", ok=bool(text),
            elapsed_s=time.time() - t0, text=text,
            input_tokens=input_tokens, output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd
        )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Anthropic", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


# ------------------------ Utility Functions -------------------------
def estimate_cost(model: str, input_tokens: int, output_tokens: int,
                  pricing: Dict[str, Dict[str, float]]) -> Optional[float]:
    """Enhanced cost estimation."""
    if model in pricing:
        p = pricing[model]
    elif model in DEFAULT_PRICING:
        p = DEFAULT_PRICING[model]
    else:
        return None

    return (input_tokens / 1000000.0) * p["in"] + (output_tokens / 1000000.0) * p["out"]


def parse_pricing_arg(pricing_str: Optional[str]) -> Dict[str, Dict[str, float]]:
    """Parse pricing string into model pricing config."""
    pricing = DEFAULT_PRICING.copy()
    if not pricing_str:
        return pricing

    for part in pricing_str.split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            model, rest = part.split(":", 1)
            items = dict(kv.split("=") for kv in rest.split(","))
            pricing[model.strip()] = {
                "in": float(items.get("in", 0.0)),
                "out": float(items.get("out", 0.0))
            }
        except Exception:
            print(f"[warn] Could not parse pricing segment: {part}", file=sys.stderr)
    return pricing


def load_suite(path: Optional[str]) -> List[dict]:
    """Load test suite with enhanced format support."""
    if not path:
        return []

    # Handle predefined combinations
    if path in DEFAULT_SUITE_FILES:
        suite_def = DEFAULT_SUITE_FILES[path]
        if isinstance(suite_def, list):
            # Combination of suites
            combined_suite = []
            for sub_suite in suite_def:
                sub_path = DEFAULT_SUITE_FILES.get(sub_suite, f"test_suites/security_{sub_suite}.yaml")
                combined_suite.extend(load_suite(sub_path))
            return combined_suite
        else:
            path = suite_def

    with open(path, "r", encoding="utf-8") as f:
        if path.endswith('.yaml') or path.endswith('.yml'):
            return yaml.safe_load(f) or []
        else:
            return json.load(f)


# -------------------------- Optimized GPT-5 Functions --------------------------
@dataclass
class RunResult:
    """Simple result structure for GPT-5 optimization compatibility."""
    model: str
    path: str
    ok: bool
    elapsed_s: float
    text: str = ""
    error: str = ""
    usage: Any = None


# --- GPT-5 helpers: robust extraction + correct starvation check + explicit text output ---

STARVED_RATIO = 0.70  # keep your global


def responses_call(client, model: str, sys_msg: str, user_prompt: str, max_tokens: int, timeout: float):
    """
    GPT-5 Responses call with constrained reasoning PLUS explicit text output channel.
    - No response_format param (unsupported)
    - No temperature/top_p (ignored/unsupported for GPT-5)
    """
    return client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_prompt},
        ],
        reasoning={"effort": "low"},
        tool_choice="none",
        # ↓ This nudges the model to actually emit *text* in the final channel
        text={"format": {"type": "text"}, "verbosity": "low"},
        max_output_tokens=max_tokens,
        timeout=timeout,
    )


def _get(obj, name, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def extract_responses_usage(resp) -> tuple[int, int, int, int]:
    """
    Returns (input_tokens, output_tokens, reasoning_tokens, total_tokens)
    Works whether the SDK returns dict-like or attribute-like objects.
    """
    usage = _get(resp, "usage", {}) or {}
    input_tokens = _get(usage, "input_tokens", 0) or 0
    output_tokens = _get(usage, "output_tokens", 0) or 0
    total_tokens = _get(usage, "total_tokens", input_tokens + output_tokens) or 0

    details = _get(usage, "output_tokens_details", {}) or {}
    reasoning_tokens = _get(details, "reasoning_tokens", 0) or 0
    return input_tokens, output_tokens, reasoning_tokens, total_tokens


def extract_responses_text(resp) -> str:
    """
    Robust text extraction. DO NOT read `response.text` (that’s the *config*).
    Prefer `output_text`; otherwise walk `output` blocks and collect text values.
    """
    # 1) Preferred path
    ot = _get(resp, "output_text", None)
    if isinstance(ot, str) and ot.strip():
        return ot.strip()

    # 2) Walk blocks in `output`
    out = _get(resp, "output", None)
    parts = []
    if isinstance(out, list):
        for block in out:
            content = _get(block, "content", None)
            if isinstance(content, list):
                for item in content:
                    val = None
                    text_obj = _get(item, "text", None)
                    if text_obj is not None:
                        val = _get(text_obj, "value", None) or _get(text_obj, "content", None)
                    if val is None and isinstance(item, dict):
                        val = item.get("text") or item.get("content") or item.get("value")
                    if isinstance(val, str) and val.strip():
                        parts.append(val)
            elif isinstance(content, str) and content.strip():
                parts.append(content.strip())
    if parts:
        return "".join(parts).strip()

    # 3) Last-ditch
    msg = _get(resp, "message", None)
    if isinstance(msg, str) and msg.strip():
        return msg.strip()

    return ""


def starved_reasoning(resp) -> bool:
    """
    True when (a) almost all output tokens were used for reasoning
    AND (b) there is no extracted text. (Your previous check was inverted.)
    """
    _, out, r, _ = extract_responses_usage(resp)
    txt = extract_responses_text(resp)
    return (out > 0 and (r / float(out)) >= STARVED_RATIO) and (not txt)


def run_gpt5_optimized(client, model: str, sys_msg: str, prompt: str, timeout: float):
    """
    Try Responses first (with low reasoning + text directive).
    If text is empty or starved, retry with a *tight* prompt.
    Then fall back to Chat with max_completion_tokens (no temperature).
    """
    t0 = time.time()

    # 1) Responses (first shot)
    try:
        resp = responses_call(client, model, sys_msg, prompt, max_tokens=512, timeout=timeout)
        text = extract_responses_text(resp)
        if text:
            return RunResult(model=model, path="Responses", ok=True,
                             elapsed_s=time.time() - t0, text=text, usage=_get(resp, "usage", {}))

        if starved_reasoning(resp):
            tight = (
                    "Answer in exactly 3 short bullet lines. "
                    "Output final TEXT only. No hidden steps, no analysis.\n\n" + prompt
            )
            resp2 = responses_call(client, model, sys_msg, tight, max_tokens=768, timeout=timeout)
            text2 = extract_responses_text(resp2)
            if text2:
                return RunResult(model=model, path="Responses (retry)", ok=True,
                                 elapsed_s=time.time() - t0, text=text2, usage=_get(resp2, "usage", {}))
    except Exception as e:
        # keep going to chat fallback
        print(f"[info] Responses failed for {model}: {e}", file=sys.stderr)

    # 2) Chat fallback (GPT-5 requires max_completion_tokens; don’t send temperature/top_p)
    try:
        chat = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt + "\n\nReturn a short plain-text answer."},
            ],
            max_completion_tokens=512,
            timeout=timeout,
        )
        text = (_get(chat.choices[0].message, "content", "") or "").strip()
        usage = _get(chat, "usage", {}) or {}
        if text:
            return RunResult(model=model, path="Chat", ok=True,
                             elapsed_s=time.time() - t0, text=text, usage=usage)
        return RunResult(model=model, path="Chat", ok=False,
                         elapsed_s=time.time() - t0, error="Empty chat content")
    except Exception as e:
        return RunResult(model=model, path="Chat", ok=False,
                         elapsed_s=time.time() - t0, error=str(e))


# -------------------------- Enhanced Model Runners --------------------------
def display_response_analysis(suite_id, model, result, test_case, criteria_met, criteria_missed, violations,
                              response_format="detailed"):
    """Display formatted response analysis for manual validation."""

    if response_format == "summary":
        # Compact summary format
        print(
            f"📋 {suite_id} | 🤖 {model} | 📊 {result.score:.3f} ({result.score * 100:.1f}%) | ⏱️ {result.elapsed_s:.2f}s")
        if result.text:
            response_preview = result.text[:100] + "..." if len(result.text) > 100 else result.text
            print(f"   💬 {response_preview}")
        if criteria_met or violations:
            print(f"   ✅ {len(criteria_met)} met | ❌ {len(criteria_missed)} missed | ⚠️ {len(violations)} violations")
        print()

    elif response_format == "detailed":
        # Detailed format (default)
        print(f"\n{'=' * 80}")
        print(f"📋 TEST: {suite_id}")
        print(f"🤖 MODEL: {model}")
        print(f"📊 SCORE: {result.score:.3f}/1.0 ({result.score * 100:.1f}%)")
        print(f"⏱️  TIME: {result.elapsed_s:.2f}s")
        if result.cost_usd:
            print(f"💰 COST: ${result.cost_usd:.5f}")
        print(f"{'=' * 80}")

        # Show test prompt for context
        if test_case:
            print(f"🎯 TEST PROMPT:")
            prompt_preview = test_case['prompt'][:200] + "..." if len(test_case['prompt']) > 200 else test_case[
                'prompt']
            print(f"   {prompt_preview}")
            print()

        # Show response (truncated for readability)
        print(f"🔍 MODEL RESPONSE:")
        if len(result.text) > 500:
            print(f"   {result.text[:500]}...")
            print(f"   [...response truncated - full text saved to reports...]")
        else:
            print(f"   {result.text}")
        print()

        # Show scoring breakdown
        print(f"📈 SCORING BREAKDOWN:")
        if criteria_met:
            print(f"   ✅ CRITERIA MET ({len(criteria_met)}):")
            for criterion in criteria_met[:3]:  # Show first 3
                print(f"      • {criterion}")
            if len(criteria_met) > 3:
                print(f"      ... and {len(criteria_met) - 3} more")

        if criteria_missed:
            print(f"   ❌ CRITERIA MISSED ({len(criteria_missed)}):")
            for criterion in criteria_missed[:3]:  # Show first 3
                print(f"      • {criterion}")
            if len(criteria_missed) > 3:
                print(f"      ... and {len(criteria_missed) - 3} more")

        if violations:
            print(f"   ⚠️  MUST NOT VIOLATIONS ({len(violations)}):")
            for violation in violations:
                print(f"      • {violation}")

        if not criteria_met and not criteria_missed and not violations:
            print(f"   ℹ️  No specific criteria defined for this test")

        print(f"{'=' * 80}\n")

    elif response_format == "full":
        # Full detailed format with everything
        print(f"\n{'=' * 100}")
        print(f"📋 TEST: {suite_id}")
        print(f"🤖 MODEL: {model}")
        print(f"📊 SCORE: {result.score:.3f}/1.0 ({result.score * 100:.1f}%)")
        print(f"⏱️  TIME: {result.elapsed_s:.2f}s")
        if result.cost_usd:
            print(f"💰 COST: ${result.cost_usd:.5f}")
        if hasattr(result, 'input_tokens') and result.input_tokens:
            print(f"📥 INPUT TOKENS: {result.input_tokens}")
        if hasattr(result, 'output_tokens') and result.output_tokens:
            print(f"📤 OUTPUT TOKENS: {result.output_tokens}")
        print(f"{'=' * 100}")

        # Show full test prompt
        if test_case:
            print(f"🎯 FULL TEST PROMPT:")
            print(f"   {test_case['prompt']}")
            print()

        # Show full response
        print(f"🔍 FULL MODEL RESPONSE:")
        print(f"   {result.text}")
        print()

        # Show complete scoring breakdown
        if test_case:
            all_criteria = test_case.get("criteria", [])
            must_not_patterns = test_case.get("must_not", [])

            print(f"📈 COMPLETE SCORING BREAKDOWN:")
            print(f"   📋 TOTAL CRITERIA: {len(all_criteria)}")
            if all_criteria:
                print(f"   🔍 ALL EXPECTED CRITERIA:")
                for i, criterion in enumerate(all_criteria, 1):
                    status = "✅" if criterion in criteria_met else "❌"
                    print(f"      {i}. {status} {criterion}")

            if must_not_patterns:
                print(f"   🚫 MUST NOT PATTERNS ({len(must_not_patterns)}):")
                for pattern in must_not_patterns:
                    violation_status = "⚠️ VIOLATED" if pattern in violations else "✅ OK"
                    print(f"      • {violation_status}: {pattern}")

        print(f"{'=' * 100}\n")


def run_single_test_concurrent(clients, suite_id, model, sys_msg, prompt, timeout, want_json, pricing):
    """Run a single test case for a single model - designed for concurrent execution."""
    try:
        result = run_enhanced_model(clients, suite_id, model, sys_msg, prompt, timeout, want_json, pricing)
        return (model, suite_id, result)
    except Exception as e:
        # Create failed result for concurrent execution
        error_result = EnhancedRunResult(
            suite_id=suite_id, model=model, path="concurrent_error", ok=False, elapsed_s=0.0,
            text=f"Concurrent execution error: {str(e)}", input_tokens=0, output_tokens=0, cost_usd=0.0, score=0.0
        )
        return (model, suite_id, error_result)


# -------------------------- XAI--------------------------

# Define constants
RETRY_SHOT_TOKENS = 4000  # Higher for JSON mode or retries
FIRST_SHOT_TOKENS = 2000  # Default for non-JSON mode

MODEL_TIMEOUTS = {
    "grok-4": 10.0,  # Reasoning model, longer timeout
    "grok-3": 8.0,  # Reasoning model
    "grok-3-mini": 6.0,  # Smaller model
    "grok-code-fast-1": 4.0  # Fast model
}


def run_xai_enhanced(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]],
        temperature: float = 0.1,
        max_retries: int = 2
) -> EnhancedRunResult:
    """
    Run X.AI Grok model via OpenAI-compatible API with enhanced error handling and retries.

    Args:
        clients: Dictionary containing API clients, with "xai" key for X.AI client.
        suite_id: Unique identifier for the test suite.
        model: Name of the model (e.g., "grok-4").
        sys_msg: System message for the API.
        prompt: User prompt for the API.
        timeout: Timeout for the API request in seconds.
        json_mode: Whether to request JSON response format.
        pricing: Dictionary with model pricing (e.g., {"grok-4": {"in": 0.5, "out": 1.0}}).
        temperature: Sampling temperature for the API (default: 0.1).
        max_retries: Maximum number of retries for API calls (default: 2).

    Returns:
        EnhancedRunResult: Object containing suite_id, model, path, status, elapsed time,
                          text, token counts, cost, and error (if any).
    """
    t0 = time.time()

    # Check client
    client = clients.get("xai")
    if not client:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="XAI", ok=False,
            elapsed_s=time.time() - t0, error="X.AI client not initialized"
        )

    # Validate inputs
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="XAI", ok=False,
            elapsed_s=time.time() - t0, error="Timeout must be a positive number"
        )
    if not sys_msg or not prompt:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="XAI", ok=False,
            elapsed_s=time.time() - t0, error="System message and prompt cannot be empty"
        )

    # Map model names to X.AI API names
    xai_model_mapping = {
        "grok-4": "grok-4-0709",
        "grok-3": "grok-3",
        "grok-3-mini": "grok-3-mini",
        "grok-code-fast-1": "grok-code-fast-1"
    }
    if model not in xai_model_mapping:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="XAI", ok=False,
            elapsed_s=time.time() - t0, error=f"Invalid model: {model}"
        )
    api_model = xai_model_mapping[model]

    # Use model-specific timeout if higher than provided timeout
    effective_timeout = max(timeout, MODEL_TIMEOUTS.get(model, timeout))

    # Validate pricing
    model_pricing = pricing.get(model, DEFAULT_PRICING.get(model, {"in": 0, "out": 0}))
    if "in" not in model_pricing or "out" not in model_pricing:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="XAI", ok=False,
            elapsed_s=time.time() - t0, error=f"Invalid pricing for model: {model}"
        )

    # Custom retry logic
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=api_model,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024 if json_mode else 768,  # Higher limits for Grok reasoning models
                temperature=temperature,
                timeout=effective_timeout,
                response_format={"type": "json_object"} if json_mode else None
            )

            # Extract text, default to empty string if None
            text = response.choices[0].message.content or ""

            # Extract token counts, handle missing usage data
            usage = getattr(response, "usage", None)
            input_tokens = usage.prompt_tokens if usage and hasattr(usage, "prompt_tokens") else 0
            output_tokens = usage.completion_tokens if usage and hasattr(usage, "completion_tokens") else len(
                text.split()) if text else 0

            # Calculate cost
            cost_usd = (input_tokens / 1000000 * model_pricing["in"] +
                        output_tokens / 1000000 * model_pricing["out"])

            return EnhancedRunResult(
                suite_id=suite_id, model=model, path="XAI", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=input_tokens, output_tokens=output_tokens,
                cost_usd=cost_usd
            )

        except Exception as e:
            error_msg = f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}"
            if attempt == max_retries:
                return EnhancedRunResult(
                    suite_id=suite_id, model=model, path="XAI", ok=False,
                    elapsed_s=time.time() - t0, error=error_msg
                )
            time.sleep(2 ** attempt + random.random())  # Exponential backoff with jitter

    # Fallback return (should not reach here)
    return EnhancedRunResult(
        suite_id=suite_id, model=model, path="XAI", ok=False,
        elapsed_s=time.time() - t0, error="Unexpected failure after retries"
    )


# -------------------------- Deepseek--------------------------


def run_deepseek_enhanced(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool = False,
        pricing: Dict[str, Dict[str, float]] = None
) -> EnhancedRunResult:
    """Run DeepSeek model with smart timeout management."""
    client = clients.get("deepseek")
    if not client:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="DeepSeek", ok=False,
            elapsed_s=0.0, error="DeepSeek client not initialized"
        )

    t0 = time.time()

    # Model-specific timeout adjustments
    adjusted_timeout = timeout
    if "reasoner" in model.lower():
        # For reasoner models, use more aggressive timeout but with fallback
        adjusted_timeout = min(timeout, 45.0)  # Cap at 45s for reasoner

    try:
        # Smart max_tokens based on model and prompt length
        base_max_tokens = RETRY_SHOT_TOKENS if json_mode else FIRST_SHOT_TOKENS
        if "reasoner" in model.lower():
            # Estimate token count and adjust accordingly
            prompt_tokens_estimate = len(prompt.split()) * 1.3  # Rough estimate
            if prompt_tokens_estimate > 500:
                base_max_tokens = min(base_max_tokens, 512)
            else:
                base_max_tokens = min(base_max_tokens, 768)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"{sys_msg} Be concise. Answer directly without reasoning."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=base_max_tokens,
            temperature=0.1,
            timeout=adjusted_timeout,
            stream=False
        )

        text = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        # Calculate cost
        if pricing is None:
            pricing = DEFAULT_PRICING

        model_pricing = pricing.get(model, {"in": 0, "out": 0})
        cost_usd = (input_tokens / 1000000 * model_pricing.get("in", 0) +
                    output_tokens / 1000000 * model_pricing.get("out", 0))

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="DeepSeek", ok=True,
            elapsed_s=time.time() - t0, text=text,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=cost_usd
        )

    except Exception as e:
        # Check if it's a timeout and we should retry with different parameters
        if "timeout" in str(e).lower() and "reasoner" in model.lower():
            # Fallback: retry with even more aggressive settings
            return run_deepseek_fallback(client, suite_id, model, sys_msg, prompt,
                                         json_mode, pricing, t0)

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="DeepSeek", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


def run_deepseek_fallback(client, suite_id, model, sys_msg, prompt, json_mode, pricing, start_time):
    """Fallback implementation for timeout scenarios."""
    try:
        # Ultra-aggressive settings for timeout recovery
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"{sys_msg} Answer in 3 words or less."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=64,  # Very short response
            temperature=0.1,
            timeout=15.0,  # Very short timeout
            stream=False
        )

        text = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        model_pricing = pricing.get(model, {"in": 0, "out": 0})
        cost_usd = (input_tokens / 1000000 * model_pricing.get("in", 0) +
                    output_tokens / 1000000 * model_pricing.get("out", 0))

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="DeepSeek", ok=True,
            elapsed_s=time.time() - start_time, text=text,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=cost_usd
        )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="DeepSeek", ok=False,
            elapsed_s=time.time() - start_time, error=f"Fallback also failed: {str(e)}"
        )


def clean_response_text(text: str) -> str:
    """Remove any reasoning or thinking patterns from the response."""
    if not text:
        return text

    # Common reasoning patterns to remove
    reasoning_patterns = [
        r"(?i)thinking.*?:.*?\n",
        r"(?i)reasoning.*?:.*?\n",
        r"(?i)step.*?by.*?step.*?:.*?\n",
        r"(?i)first.*?:.*?\n",
        r"(?i)let me.*?\n",
        r"(?i)here.*?:.*?\n",
        r"(?i)explanation.*?:.*?\n",
        r"(?i)therefore.*?\n",
        r"(?i)so.*?\n",
        r"(?i)thus.*?\n",
        r"(?i)hence.*?\n",
        r"^.*?[Tt]hinking:.*?\n",
        r"^.*?[Rr]easoning:.*?\n",
        r"^.*?[Ee]xplanation:.*?\n"
    ]

    # Remove reasoning patterns
    cleaned_text = text
    for pattern in reasoning_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text)

    # Remove empty lines and excessive whitespace
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
    cleaned_text = cleaned_text.strip()

    # If the response starts with common reasoning connectors, try to find the actual answer
    if re.match(r'(?i)(so|therefore|thus|hence|finally|answer:|result:)', cleaned_text):
        # Try to extract the part after the first sentence
        sentences = re.split(r'[.!?]', cleaned_text, 1)
        if len(sentences) > 1:
            cleaned_text = sentences[1].strip()

    return cleaned_text


# -------------------------- LLAMA--------------------------

def run_llama_enhanced(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Run Llama model via OpenAI-compatible API provider."""
    client = clients.get("llama")
    if not client:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Llama", ok=False,
            elapsed_s=0.0, error="Llama client not initialized"
        )

    t0 = time.time()
    try:
        # Map model names to provider API names
        api_model = model.replace("llama-", "meta-llama/Llama-")
        if "70b" in model:
            api_model += "-Instruct"
        elif "11b" in model:
            api_model += "-Vision-Instruct"

        response = client.chat.completions.create(
            model=api_model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            max_tokens=RETRY_SHOT_TOKENS if json_mode else FIRST_SHOT_TOKENS,
            temperature=0.1,
            timeout=timeout
        )

        text = response.choices[0].message.content or ""
        usage = getattr(response, 'usage', None)

        if usage:
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens

            # Calculate cost
            model_pricing = pricing.get(model, DEFAULT_PRICING.get(model, {"in": 0, "out": 0}))
            cost_usd = (input_tokens / 1000000 * model_pricing["in"] +
                        output_tokens / 1000000 * model_pricing["out"])
        else:
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(text.split()) * 1.3
            cost_usd = 0.0  # Some providers don't report usage

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Llama", ok=True,
            elapsed_s=time.time() - t0, text=text,
            input_tokens=int(input_tokens), output_tokens=int(output_tokens),
            cost_usd=cost_usd
        )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Llama", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


def run_ollama_enhanced(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Run Ollama local model via REST API."""
    ollama_client = clients.get("ollama")
    if not ollama_client:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Ollama", ok=False,
            elapsed_s=0.0, error="Ollama client not initialized"
        )

    base_url = ollama_client["base_url"]
    model_name = model.replace("ollama/", "")

    t0 = time.time()
    try:
        # Check if model is available
        models_response = requests.get(f"{base_url}/api/tags", timeout=5)
        if models_response.status_code != 200:
            raise Exception("Failed to list Ollama models")

        available_models = [m["name"] for m in models_response.json().get("models", [])]
        if model_name not in available_models:
            raise Exception(f"Model {model_name} not available. Run: ollama pull {model_name}")

        # Prepare prompt
        full_prompt = f"System: {sys_msg}\n\nUser: {prompt}\n\nAssistant:"

        # Make request to Ollama
        ollama_request = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
                "num_predict": RETRY_SHOT_TOKENS if json_mode else FIRST_SHOT_TOKENS
            }
        }

        if json_mode:
            ollama_request["format"] = "json"

        response = requests.post(
            f"{base_url}/api/generate",
            json=ollama_request,
            timeout=timeout
        )

        if response.status_code != 200:
            raise Exception(f"Ollama request failed: {response.status_code}")

        result = response.json()
        text = result.get("response", "")

        # Ollama doesn't provide exact token counts, estimate them
        input_tokens = len(full_prompt.split()) * 1.3
        output_tokens = len(text.split()) * 1.3

        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Ollama", ok=True,
            elapsed_s=time.time() - t0, text=text,
            input_tokens=int(input_tokens), output_tokens=int(output_tokens),
            cost_usd=0.0  # Local models are free
        )

    except Exception as e:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Ollama", ok=False,
            elapsed_s=time.time() - t0, error=str(e)
        )


def run_enhanced_model(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Route to appropriate enhanced runner."""
    if model.startswith("gpt-"):
        return run_openai_enhanced(suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("claude-"):
        return run_anthropic_enhanced(suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("gemini-"):
        return run_gemini(suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("grok-"):
        return run_xai_enhanced(clients, suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("deepseek-"):
        return run_deepseek_enhanced(clients, suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("llama-"):
        return run_llama_enhanced(clients, suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("ollama/"):
        return run_ollama_enhanced(clients, suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    else:
        return EnhancedRunResult(
            suite_id=suite_id, model=model, path="Unknown", ok=False,
            elapsed_s=0.0, error=f"Unknown model type: {model}"
        )


# ------------------------ Enhanced Scoring & Analysis -------------------------
def score_text_enhanced(text: str, criteria: List[str], must_not: List[str]) -> Tuple[
    float, List[str], List[str], List[str]]:
    """Enhanced scoring with detailed analysis."""
    # Ensure text is a string (safety check for API response objects)
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    T = text.lower()
    criteria_met = []
    criteria_missed = []
    must_not_violations = []

    # Check required criteria
    for patt in criteria:
        try:
            if re.search(patt, T, flags=re.I | re.DOTALL):
                criteria_met.append(patt)
            else:
                criteria_missed.append(patt)
        except re.error:
            if patt.lower() in T:
                criteria_met.append(patt)
            else:
                criteria_missed.append(patt)

    # Check must_not criteria
    for patt in must_not or []:
        try:
            if re.search(patt, T, flags=re.I | re.DOTALL):
                must_not_violations.append(patt)
        except re.error:
            if patt.lower() in T:
                must_not_violations.append(patt)

    # Enhanced scoring algorithm
    pos_weight = 1.0
    neg_weight = 0.75  # Slightly higher penalty for violations

    pos = len(criteria_met) * pos_weight
    neg = len(must_not_violations) * neg_weight
    raw = pos - neg
    denom = max(len(criteria), 1)
    score = max(0.0, min(1.0, raw / denom))

    return score, criteria_met, criteria_missed, must_not_violations


# ------------------------ Executive Reporting System -------------------------
def generate_rigorous_analysis_data(
        results: List[EnhancedRunResult],
        models: List[str]
) -> Dict:
    """Generate rigorous analysis data for LLM benchmark evaluation."""

    # Analyze performance by model
    performance_by_model = {}
    model_data = []
    warnings = []

    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            perf = ModelPerformance.from_results(model, model_results)
            performance_by_model[model] = perf

            # Calculate metrics with flags
            flags = []
            if perf.success_rate < 0.8:
                flags.append("LOW_SUCCESS")
            if perf.cost_per_test == 0:
                flags.append("MISSING_COST")
            if perf.avg_response_time > 30:
                flags.append("SLOW_RESPONSE")
            if perf.score_std_dev > 0.3:
                flags.append("HIGH_VARIANCE")
            if perf.total_input_tokens > 1000000 and perf.cost_per_test < 0.001:
                flags.append("TOKEN_COST_MISMATCH")

            score_per_dollar = None
            if perf.cost_per_test > 0:
                score_per_dollar = perf.avg_score / perf.cost_per_test

            model_data.append({
                "model": model,
                "tests": perf.total_tests,
                "success_rate": perf.success_rate,
                "avg_score": perf.avg_score,
                "avg_time_s": perf.avg_response_time,
                "total_cost_usd": perf.total_cost,
                "cost_per_test_usd": perf.cost_per_test,
                "good_rate": perf.good_scores / perf.total_tests if perf.total_tests > 0 else None,
                "score_per_dollar": score_per_dollar,
                "in_tokens": perf.total_input_tokens,
                "out_tokens": perf.total_output_tokens,
                "flags": flags
            })

    # Check fairness of comparison
    test_counts = [d["tests"] for d in model_data]
    fair_comparison = (max(test_counts) - min(test_counts)) <= (max(test_counts) * 0.05) if test_counts else True

    if not fair_comparison:
        warnings.append("UNFAIR_COMPARISON: Test counts vary by >5% across models")
        warnings.append(f"Test counts range: {min(test_counts)} to {max(test_counts)}")

    # Check for missing costs
    missing_costs = [d["model"] for d in model_data if d["cost_per_test_usd"] == 0]
    if missing_costs:
        warnings.append(f"MISSING_COSTS: {len(missing_costs)} models have no cost data: {missing_costs}")

    # Rankings (top 3 each)
    accuracy_top3 = sorted(model_data, key=lambda x: x["avg_score"], reverse=True)[:3]
    speed_top3 = sorted(model_data, key=lambda x: x["avg_time_s"])[:3]  # Lower is better
    cost_efficiency_top3 = sorted([m for m in model_data if m["score_per_dollar"]],
                                  key=lambda x: x["score_per_dollar"], reverse=True)[:3]
    reliability_top3 = sorted(model_data, key=lambda x: x["success_rate"], reverse=True)[:3]

    # Tier recommendations based on use cases
    # Triage (fast & cheap): speed < 10s, cost < $0.01/test, decent accuracy
    triage_candidates = [m for m in model_data if m["avg_time_s"] < 10 and
                         (m["cost_per_test_usd"] or 0) < 0.01 and m["avg_score"] > 0.5]
    triage_fast_cheap = sorted(triage_candidates, key=lambda x: x["avg_score"], reverse=True)[:2]

    # CI Gate (balanced): accuracy > 0.6, reasonable speed/cost
    balanced_candidates = [m for m in model_data if m["avg_score"] > 0.6 and
                           m["avg_time_s"] < 20 and (m["cost_per_test_usd"] or 0) < 0.05]
    ci_gate_balanced = sorted(balanced_candidates,
                              key=lambda x: (x["avg_score"] * 0.7 + (1 / x["avg_time_s"]) * 0.3), reverse=True)[:2]

    # Audits (max signal): highest accuracy regardless of cost
    audits_max_signal = sorted(model_data, key=lambda x: x["avg_score"], reverse=True)[:2]

    return {
        "dataset_summary": {
            "total_models": len(models),
            "columns_detected": ["model", "tests", "success_rate", "avg_score", "avg_time_s", "total_cost_usd"],
            "fair_comparison": fair_comparison,
            "fairness_notes": "Test counts vary across models" if not fair_comparison else "Similar test counts across models"
        },
        "models": model_data,
        "rankings": {
            "accuracy_top3": [m["model"] for m in accuracy_top3],
            "speed_top3": [m["model"] for m in speed_top3],
            "cost_efficiency_top3": [m["model"] for m in cost_efficiency_top3],
            "reliability_top3": [m["model"] for m in reliability_top3]
        },
        "tier_recommendations": {
            "triage_fast_cheap": [m["model"] for m in triage_fast_cheap],
            "ci_gate_balanced": [m["model"] for m in ci_gate_balanced],
            "audits_max_signal": [m["model"] for m in audits_max_signal]
        },
        "warnings": warnings,
        "next_experiments": [
            "Rerun on common subset for fair comparison",
            "Compute cost per correct CRITICAL detection if ground truth available",
            "Implement latency budgets with token caps and terse prompts",
            "Design ensemble: fast screen → escalate uncertain/high-risk to premium models"
        ]
    }


def generate_standardized_table_analysis(
        results: List[EnhancedRunResult],
        models: List[str],
        outdir: Path
) -> None:
    """Generate standardized table analysis using rigorous methodology."""

    # Build raw performance data by model
    model_data = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            perf = ModelPerformance.from_results(model, model_results)
            model_data[model] = {
                'total_tests': perf.total_tests,
                'success_rate': perf.success_rate,
                'perfect_rate': perf.perfect_scores / perf.total_tests if perf.total_tests > 0 else 0,
                'cost_per_test': perf.cost_per_test,
                'avg_score': perf.avg_score,
                'avg_time_s': perf.avg_response_time,
                'good_scores': perf.good_scores,
                'poor_scores': perf.poor_scores,
                'score_std_dev': perf.score_std_dev,
                'notes': []
            }

    if not model_data:
        return

    # Check for duplicate models or test count differences
    test_counts = list(set(data['total_tests'] for data in model_data.values()))
    mixed_test_counts = len(test_counts) > 1
    if mixed_test_counts:
        for model, data in model_data.items():
            data['notes'].append(f"tested on {data['total_tests']} tests")

    # Calculate metrics for each model
    for model, data in model_data.items():
        # Traditional Score-per-Dollar
        if data['cost_per_test'] > 0:
            if data['avg_score'] > 0:
                traditional = data['avg_score'] / data['cost_per_test']
            else:
                traditional = data['success_rate'] / data['cost_per_test']
                data['notes'].append("approx (no AvgScore)")
        else:
            traditional = float('inf') if data['avg_score'] > 0 else 0
            data['notes'].append("free model")

        # Weighted (Reliability-adjusted)  
        reliability_factor = data['success_rate'] * (1 + 0.5 * data['perfect_rate'])
        if data['avg_time_s'] > 0:
            time_penalty = 1 / (1 + 0.15 * data['avg_time_s'])
            weighted = traditional * reliability_factor * time_penalty
        else:
            weighted = traditional * reliability_factor
            data['notes'].append("no timing data")

        # Penalty-Adjusted (Quality & Stability) - simplified version
        # Using score variance as proxy for stability
        if data['score_std_dev'] > 0:
            variance_penalty = max(0, 1 - (data['score_std_dev'] * 2))  # Higher variance = lower score
            penalty_adjusted = max(0, weighted * variance_penalty)
        else:
            penalty_adjusted = weighted
            data['notes'].append("penalties not available")

        data['traditional'] = traditional
        data['weighted'] = weighted
        data['penalty_adjusted'] = penalty_adjusted

    # Sort by penalty-adjusted (or weighted if penalty not available)
    sorted_models = sorted(model_data.items(),
                           key=lambda x: x[1]['penalty_adjusted'] if x[1]['penalty_adjusted'] != float('inf')
                           else x[1]['weighted'], reverse=True)

    # Generate clean table
    table_rows = []
    for model, data in sorted_models:
        notes_str = "; ".join(data['notes']) if data['notes'] else ""

        # Format values
        success_pct = f"{data['success_rate'] * 100:.1f}%"
        perfect_pct = f"{data['perfect_rate'] * 100:.1f}%"
        cost_str = f"{data['cost_per_test']:.5f}" if data['cost_per_test'] > 0 else "Free"
        avg_score_str = f"{data['avg_score']:.3f}" if data['avg_score'] > 0 else "N/A"
        avg_time_str = f"{data['avg_time_s']:.2f}" if data['avg_time_s'] > 0 else "N/A"
        traditional_str = f"{data['traditional']:.1f}" if data['traditional'] != float('inf') else "∞"
        weighted_str = f"{data['weighted']:.1f}" if data['weighted'] != float('inf') else "∞"
        penalty_str = f"{data['penalty_adjusted']:.1f}" if data['penalty_adjusted'] != float('inf') else "∞"

        table_rows.append([
            model, str(data['total_tests']), success_pct, perfect_pct, cost_str,
            avg_score_str, avg_time_str, traditional_str, weighted_str, penalty_str, notes_str
        ])

    # Generate rankings
    def safe_sort(items, key_func, reverse=True):
        valid_items = [(k, v) for k, v in items if key_func(v) not in [float('inf'), float('-inf')] and key_func(v) > 0]
        return sorted(valid_items, key=lambda x: key_func(x[1]), reverse=reverse)[:3]

    accuracy_top3 = safe_sort(model_data.items(), lambda x: x['avg_score'])
    cost_eff_top3 = safe_sort(model_data.items(), lambda x: x['traditional'])
    weighted_top3 = safe_sort(model_data.items(), lambda x: x['weighted'])
    penalty_top3 = safe_sort(model_data.items(), lambda x: x['penalty_adjusted'])

    # Speed rankings (lower is better)
    speed_top3 = safe_sort(model_data.items(), lambda x: 1 / x['avg_time_s'] if x['avg_time_s'] > 0 else 0)

    # Generate analysis
    analysis = f"""# Standardized LLM Security Benchmark Analysis

## Clean Performance Table

| Model | Total Tests | Success | Perfect | Cost/Test (USD) | AvgScore | AvgTime(s) | Traditional | Weighted | Penalty-Adjusted | Notes |
|-------|-------------|---------|---------|------------------|----------|------------|-------------|----------|------------------|-------|
"""

    for row in table_rows:
        analysis += f"| {' | '.join(row)} |\n"

    analysis += f"""
## Summary Analysis

### Performance Rankings

* **Top 3 by Accuracy (AvgScore)**: {', '.join([f"{name} ({data['avg_score']:.3f})" for name, data in accuracy_top3]) if accuracy_top3 else "Insufficient data"}
* **Top 3 by Cost-Efficiency (Traditional)**: {', '.join([f"{name} ({data['traditional']:.1f})" for name, data in cost_eff_top3]) if cost_eff_top3 else "Insufficient data"}  
* **Top 3 by Reliability-Adjusted (Weighted)**: {', '.join([f"{name} ({data['weighted']:.1f})" for name, data in weighted_top3]) if weighted_top3 else "Insufficient data"}
* **Top 3 Overall (Penalty-Adjusted)**: {', '.join([f"{name} ({data['penalty_adjusted']:.1f})" for name, data in penalty_top3]) if penalty_top3 else "Insufficient data"}
* **Fastest average responders**: {', '.join([f"{name} ({data['avg_time_s']:.2f}s)" for name, data in speed_top3]) if speed_top3 else "No timing data"}

### Data Quality Flags

* **Mixed test counts**: {"Yes - " + ", ".join([f"{model}({data['total_tests']})" for model, data in model_data.items()]) if mixed_test_counts else "No - all models tested equally"}
* **Missing cost data**: {', '.join([model for model, data in model_data.items() if data['cost_per_test'] == 0]) or "None"}
* **Missing timing data**: {', '.join([model for model, data in model_data.items() if data['avg_time_s'] == 0]) or "None"}

### Tiered Recommendations

* **Triage (cheap/fast)**: {', '.join([model for model, data in model_data.items() if data['avg_time_s'] < 10 and data['cost_per_test'] < 0.01 and data['avg_score'] > 0.5]) or "No suitable models found"}
* **CI gate (balanced)**: {', '.join([model for model, data in model_data.items() if data['avg_score'] > 0.6 and data['avg_time_s'] < 20]) or "No suitable models found"}  
* **Audits / high-signal**: {', '.join([name for name, data in accuracy_top3[:2]]) if accuracy_top3 else "Insufficient data"}

### Caveats

* **Test count fairness**: {"Models tested on different test counts - rankings may not be directly comparable" if mixed_test_counts else "Fair comparison - all models tested on same test count"}
* **Missing penalties**: Most models lack comprehensive penalty data (empty/timeout rates)
* **Cost model assumptions**: Free models assigned infinite cost-effectiveness

## Methodology Snapshot  

* **Traditional = AvgScore / CostPerTest** (or SuccessRate if AvgScore missing)
* **Weighted = Traditional × SuccessRate × (1 + 0.5×PerfectRate) / (1 + 0.15×AvgTime)**  
* **Penalty-Adjusted = Weighted × (1 - 2×ScoreVariance)** (simplified stability penalty)
* **Missing fields**: Marked as N/A; free models treated as infinite cost-effectiveness
* **Sorting**: By Penalty-Adjusted descending; USD to 5 decimals, time to 2 decimals

---
*Analysis generated using standardized LLM benchmark methodology*
"""

    # Write standardized analysis
    with open(outdir / "standardized_analysis.md", "w", encoding="utf-8") as f:
        f.write(analysis)


def generate_language_breakdown_analysis(
        results: List[EnhancedRunResult],
        models: List[str],
        outdir: Path
) -> None:
    """Generate enhanced analysis with per-language and per-test-type breakdowns."""

    # Language and test type inference mappings
    language_patterns = {
        'Python': ['python', 'django', 'flask', 'pickle', 'eval', 'exec', '.py'],
        'JavaScript': ['javascript', 'js', 'node', 'typescript', 'npm', 'prototype', '.js', '.ts'],
        'Java': ['java', 'spring', 'jvm', 'deserialization', '.java'],
        'Go': ['go', 'golang', 'race_condition', '.go'],
        'Rust': ['rust', 'unsafe', 'cargo', '.rs'],
        'C': ['c_', '_c', 'buffer', 'memory', '.c'],
        'C++': ['cpp', 'c++', 'buffer_overflow', '.cpp', '.cxx'],
        'C#': ['csharp', 'c#', 'dotnet', '.cs'],
        'PHP': ['php', '.php'],
        'Ruby': ['ruby', 'rails', '.rb'],
        'Kotlin': ['kotlin', 'android', 'intent', '.kt'],
        'Swift': ['swift', 'ios', 'keychain', '.swift'],
        'Scala': ['scala', 'play', '.scala'],
        'Dart': ['dart', 'flutter', '.dart'],
        'Haskell': ['haskell', '.hs']
    }

    test_type_patterns = {
        'OWASP': ['owasp', 'top10', 'top_10'],
        'SAST': ['sast', 'static', 'lint', 'code_analysis'],
        'Secrets': ['secret', 'token', 'key', 'credential', 'hardcoded'],
        'IaC': ['iac', 'terraform', 'k8s', 'kubernetes', 'cloudformation', 'checkov'],
        'Dependency': ['dep', 'dependency', 'supply_chain', 'sbom', 'vuln', 'vulnerability'],
        'Architecture': ['arch', 'architecture', 'design', 'pattern'],
        'Quality': []  # Default fallback
    }

    def infer_language(suite_id: str) -> str:
        """Infer programming language from suite_id."""
        suite_lower = suite_id.lower()
        for lang, patterns in language_patterns.items():
            if any(pattern in suite_lower for pattern in patterns):
                return lang
        return 'Unknown'

    def infer_test_type(suite_id: str) -> str:
        """Infer test type from suite_id."""
        suite_lower = suite_id.lower()
        for test_type, patterns in test_type_patterns.items():
            if test_type != 'Quality' and any(pattern in suite_lower for pattern in patterns):
                return test_type
        return 'Quality'  # Default fallback

    # Build enhanced dataset with language and test type inference
    enhanced_data = []
    for result in results:
        language = infer_language(result.suite_id)
        test_type = infer_test_type(result.suite_id)

        enhanced_data.append({
            'result': result,
            'model': result.model,
            'language': language,
            'test_type': test_type,
            'suite_id': result.suite_id,
            'success': result.ok,
            'score': result.score,
            'time_s': result.elapsed_s,
            'cost_usd': result.cost_usd if hasattr(result, 'cost_usd') else 0
        })

    # Group by model, language, test_type
    grouped_data = {}
    for item in enhanced_data:
        key = (item['model'], item['language'], item['test_type'])
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(item)

    # Calculate aggregated metrics for each group
    aggregated_rows = []
    for (model, language, test_type), items in grouped_data.items():
        total_tests = len(items)
        successful_tests = sum(1 for item in items if item['success'])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0

        # Calculate perfect scores (scores >= 0.95)
        perfect_scores = sum(1 for item in items if item['score'] >= 0.95)
        perfect_rate = perfect_scores / total_tests if total_tests > 0 else 0

        avg_score = sum(item['score'] for item in items) / total_tests if total_tests > 0 else 0
        avg_time_s = sum(item['time_s'] for item in items) / total_tests if total_tests > 0 else 0
        total_cost = sum(item['cost_usd'] for item in items)
        cost_per_test = total_cost / total_tests if total_tests > 0 else 0

        # Calculate score variance for penalty adjustment
        if total_tests > 1:
            score_variance = sum((item['score'] - avg_score) ** 2 for item in items) / total_tests
            score_std_dev = score_variance ** 0.5
        else:
            score_std_dev = 0

        # Calculate metrics using standardized formulas
        notes = []

        # Traditional Score-per-Dollar
        if cost_per_test > 0:
            if avg_score > 0:
                traditional = avg_score / cost_per_test
            else:
                traditional = success_rate / cost_per_test
                notes.append("approx (no AvgScore)")
        else:
            traditional = float('inf') if avg_score > 0 else 0
            notes.append("free model")

        # Weighted (Reliability-adjusted)
        reliability_factor = success_rate * (1 + 0.5 * perfect_rate)
        if avg_time_s > 0:
            time_penalty = 1 / (1 + 0.15 * avg_time_s)
            weighted = traditional * reliability_factor * time_penalty
        else:
            weighted = traditional * reliability_factor
            notes.append("no timing data")

        # Penalty-Adjusted (Quality & Stability)
        if score_std_dev > 0:
            variance_penalty = max(0, 1 - (score_std_dev * 2))
            penalty_adjusted = max(0, weighted * variance_penalty)
        else:
            penalty_adjusted = weighted
            notes.append("penalties not available")

        aggregated_rows.append({
            'model': model,
            'language': language,
            'test_type': test_type,
            'total_tests': total_tests,
            'success_rate': success_rate,
            'perfect_rate': perfect_rate,
            'cost_per_test': cost_per_test,
            'avg_score': avg_score,
            'avg_time_s': avg_time_s,
            'traditional': traditional,
            'weighted': weighted,
            'penalty_adjusted': penalty_adjusted,
            'notes': notes
        })

    # Sort by penalty-adjusted score
    aggregated_rows.sort(
        key=lambda x: x['penalty_adjusted'] if x['penalty_adjusted'] != float('inf') else x['weighted'], reverse=True)

    # Build analysis report
    analysis = f"""# Enhanced LLM Security Benchmark Analysis
## Per-Language and Test-Type Breakdown

## 1) Global Clean Table (all languages & tests)

| Model | Language | TestType | Total Tests | Success | Perfect | Cost/Test (USD) | AvgScore | AvgTime(s) | Traditional | Weighted | Penalty-Adjusted | Notes |
|-------|----------|----------|-------------|---------|---------|------------------|----------|------------|-------------|----------|------------------|-------|
"""

    # Add global table rows
    for row in aggregated_rows:
        success_pct = f"{row['success_rate'] * 100:.1f}%"
        perfect_pct = f"{row['perfect_rate'] * 100:.1f}%"
        cost_str = f"{row['cost_per_test']:.5f}" if row['cost_per_test'] > 0 else "Free"
        avg_score_str = f"{row['avg_score']:.3f}" if row['avg_score'] > 0 else "N/A"
        avg_time_str = f"{row['avg_time_s']:.2f}" if row['avg_time_s'] > 0 else "N/A"
        traditional_str = f"{row['traditional']:.1f}" if row['traditional'] != float('inf') else "∞"
        weighted_str = f"{row['weighted']:.1f}" if row['weighted'] != float('inf') else "∞"
        penalty_str = f"{row['penalty_adjusted']:.1f}" if row['penalty_adjusted'] != float('inf') else "∞"
        notes_str = "; ".join(row['notes']) if row['notes'] else ""

        analysis += f"| {row['model']} | {row['language']} | {row['test_type']} | {row['total_tests']} | {success_pct} | {perfect_pct} | {cost_str} | {avg_score_str} | {avg_time_str} | {traditional_str} | {weighted_str} | {penalty_str} | {notes_str} |\n"

    # Group data by language for per-language analysis
    by_language = {}
    for row in aggregated_rows:
        lang = row['language']
        if lang not in by_language:
            by_language[lang] = {'rows': [], 'by_test_type': {}}
        by_language[lang]['rows'].append(row)

        test_type = row['test_type']
        if test_type not in by_language[lang]['by_test_type']:
            by_language[lang]['by_test_type'][test_type] = []
        by_language[lang]['by_test_type'][test_type].append(row)

    analysis += "\n## 2) Per-Language Sections\n\n"

    # Generate per-language breakdowns
    for language in sorted(by_language.keys()):
        lang_data = by_language[language]
        analysis += f"### {language}\n\n"

        # Overview
        total_tests = sum(row['total_tests'] for row in lang_data['rows'])
        unique_models = len(set(row['model'] for row in lang_data['rows']))
        top_model = max(lang_data['rows'], key=lambda x: x['penalty_adjusted'])

        analysis += f"**Overview:**\n"
        analysis += f"- Dataset: {total_tests} total tests across {unique_models} models\n"
        analysis += f"- Top performer: {top_model['model']} (penalty-adjusted: {top_model['penalty_adjusted']:.1f})\n"
        analysis += f"- Test types: {', '.join(sorted(lang_data['by_test_type'].keys()))}\n\n"

        # Per-language table
        analysis += f"**{language} Performance Table:**\n\n"
        analysis += "| Model | TestType | Total Tests | Success | Perfect | Cost/Test (USD) | Traditional | Weighted | Penalty-Adjusted |\n"
        analysis += "|-------|----------|-------------|---------|---------|------------------|-------------|----------|------------------|\n"

        for row in sorted(lang_data['rows'], key=lambda x: x['penalty_adjusted'], reverse=True):
            success_pct = f"{row['success_rate'] * 100:.1f}%"
            perfect_pct = f"{row['perfect_rate'] * 100:.1f}%"
            cost_str = f"{row['cost_per_test']:.5f}" if row['cost_per_test'] > 0 else "Free"
            traditional_str = f"{row['traditional']:.1f}" if row['traditional'] != float('inf') else "∞"
            weighted_str = f"{row['weighted']:.1f}" if row['weighted'] != float('inf') else "∞"
            penalty_str = f"{row['penalty_adjusted']:.1f}" if row['penalty_adjusted'] != float('inf') else "∞"

            analysis += f"| {row['model']} | {row['test_type']} | {row['total_tests']} | {success_pct} | {perfect_pct} | {cost_str} | {traditional_str} | {weighted_str} | {penalty_str} |\n"

        # Per-test-type breakdowns
        analysis += f"\n**Test Type Breakdowns for {language}:**\n\n"
        for test_type in sorted(lang_data['by_test_type'].keys()):
            type_rows = sorted(lang_data['by_test_type'][test_type], key=lambda x: x['penalty_adjusted'], reverse=True)[
                        :3]
            models_str = ', '.join([f"{r['model']} ({r['penalty_adjusted']:.1f})" for r in type_rows])
            analysis += f"- **{test_type}**: {models_str}\n"

        analysis += "\n"

    # Cross-language leaderboards by test type
    analysis += "## 3) Cross-Language Leaderboards (by TestType)\n\n"

    by_test_type = {}
    for row in aggregated_rows:
        test_type = row['test_type']
        if test_type not in by_test_type:
            by_test_type[test_type] = []
        by_test_type[test_type].append(row)

    for test_type in sorted(by_test_type.keys()):
        top_3 = sorted(by_test_type[test_type], key=lambda x: x['penalty_adjusted'], reverse=True)[:3]
        analysis += f"**{test_type}:**\n"
        for i, row in enumerate(top_3, 1):
            rationale = []
            if row['cost_per_test'] < 0.01:
                rationale.append("low-cost")
            if row['avg_score'] > 0.8:
                rationale.append("high-accuracy")
            if row['avg_time_s'] < 10:
                rationale.append("fast")
            rationale_str = f"({', '.join(rationale)})" if rationale else ""
            analysis += f"{i}. {row['model']} ({row['language']}) - {row['penalty_adjusted']:.1f} {rationale_str}\n"
        analysis += "\n"

    # Generate machine-readable JSON
    json_export = {
        "rows": aggregated_rows,
        "by_language": by_language,
        "leaderboards": {
            "by_test_type": {
                test_type: sorted(rows, key=lambda x: x['penalty_adjusted'], reverse=True)[:3]
                for test_type, rows in by_test_type.items()
            }
        },
        "notes": [
            "Language inferred from suite_id patterns",
            "Test types mapped using keyword patterns",
            "Penalty-adjusted scoring uses simplified variance penalty"
        ]
    }

    analysis += f"""## 4) Summary Analysis

### Performance Rankings
* **Top 3 by Accuracy**: {', '.join([f"{row['model']} ({row['language']}) {row['avg_score']:.3f}" for row in sorted(aggregated_rows, key=lambda x: x['avg_score'], reverse=True)[:3]])}
* **Top 3 by Cost-Efficiency**: {', '.join([f"{row['model']} ({row['language']}) {row['traditional']:.1f}" for row in sorted([r for r in aggregated_rows if r['traditional'] != float('inf')], key=lambda x: x['traditional'], reverse=True)[:3]])}
* **Top 3 Overall**: {', '.join([f"{row['model']} ({row['language']}) {row['penalty_adjusted']:.1f}" for row in aggregated_rows[:3]])}

### Tiered Recommendations by Language/TestType
* **Triage**: {', '.join([f"{row['model']} ({row['language']}/{row['test_type']})" for row in aggregated_rows if row['avg_time_s'] < 10 and row['cost_per_test'] < 0.01 and row['avg_score'] > 0.5][:3]) or "No suitable models found"}
* **CI Gate**: {', '.join([f"{row['model']} ({row['language']}/{row['test_type']})" for row in aggregated_rows if row['avg_score'] > 0.6 and row['avg_time_s'] < 20][:3]) or "No suitable models found"}
* **Audits**: {', '.join([f"{row['model']} ({row['language']}/{row['test_type']})" for row in aggregated_rows[:3]])}

## 5) Machine-Readable Export

```json
{json.dumps(json_export, indent=2, default=str)}
```

---
*Enhanced analysis with per-language and test-type breakdowns*
"""

    # Write enhanced analysis
    with open(outdir / "enhanced_language_breakdown.md", "w", encoding="utf-8") as f:
        f.write(analysis)

    # Write JSON export
    with open(outdir / "enhanced_language_breakdown.json", "w", encoding="utf-8") as f:
        json.dump(json_export, f, indent=2, default=str)


def analyze_vulnerability_categories(results: List[EnhancedRunResult], models: List[str]) -> Dict[
    str, Dict[str, float]]:
    """Analyze performance by vulnerability category."""
    vulnerability_patterns = {
        "SQL Injection": ["sql.*injection", "sqli", "parameterized.*query"],
        "XSS/Script Injection": ["xss", "script.*injection", "reflected.*xss", "dom.*xss"],
        "Access Control": ["access.*control", "authorization", "privilege.*escalation", "rbac"],
        "Authentication": ["authentication", "login", "password", "session", "2fa", "mfa"],
        "Cryptography": ["crypto", "hash", "encrypt", "tls", "ssl", "cipher"],
        "Command Injection": ["command.*injection", "shell.*injection", "exec"],
        "Path Traversal": ["path.*traversal", "directory.*traversal", "\\.\\./"],
        "CSRF": ["csrf", "cross.*site.*request"],
        "SSRF": ["ssrf", "server.*side.*request"],
        "Deserialization": ["deserialization", "pickle", "serialize"]
    }

    category_scores = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        category_scores[model] = {}

        for category, patterns in vulnerability_patterns.items():
            matching_results = []
            for result in model_results:
                # Check if test relates to this vulnerability category
                if any(re.search(pattern, result.suite_id.lower(), re.I) for pattern in patterns):
                    matching_results.append(result)

            if matching_results:
                avg_score = sum(r.score for r in matching_results) / len(matching_results)
                category_scores[model][category] = avg_score

    return category_scores


def calculate_business_metrics(performance_by_model: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate business-focused security metrics."""
    # Security incident cost estimates (industry averages)
    CRITICAL_VULN_COST = 50000  # Cost of critical vulnerability if exploited
    MODERATE_VULN_COST = 15000  # Cost of moderate vulnerability
    COMPLIANCE_PENALTY = 100000  # Cost of compliance failure

    business_metrics = {}
    for model, perf in performance_by_model.items():
        # Calculate risk reduction value
        critical_detection_rate = perf.avg_score  # Simplified: higher score = better detection
        risk_reduction_value = critical_detection_rate * CRITICAL_VULN_COST * 12  # Annual value

        # ROI calculation
        annual_cost = perf.cost_per_test * 1000 * 12  # 1000 tests/month
        roi = (risk_reduction_value - annual_cost) / annual_cost if annual_cost > 0 else 0

        # Compliance value
        compliance_score = 1.0 if perf.avg_score > 0.8 else perf.avg_score * 1.25
        compliance_value = compliance_score * COMPLIANCE_PENALTY

        business_metrics[model] = {
            "risk_reduction_value": risk_reduction_value,
            "annual_cost": annual_cost,
            "roi": roi,
            "compliance_value": compliance_value,
            "total_business_value": risk_reduction_value + compliance_value
        }

    return business_metrics


def generate_performance_analysis(
        results: List[EnhancedRunResult],
        models: List[str],
        outdir: Path
) -> None:
    """Generate detailed performance analysis JSON."""

    performance_data = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "models_evaluated": len(models),
            "analysis_version": "2.0"
        },
        "model_comparison": {},
        "aggregate_statistics": {},
        "recommendations": {}
    }

    # Model-by-model analysis
    for model in models:
        model_results = [r for r in results if r.model == model]
        if not model_results:
            continue

        successful = [r for r in model_results if r.ok]

        if successful:
            scores = [r.score for r in successful]
            times = [r.elapsed_s for r in successful]
            costs = [r.cost_usd for r in model_results if r.cost_usd]

            # Token calculations
            total_input_tokens = sum(r.input_tokens for r in model_results if r.input_tokens)
            total_output_tokens = sum(r.output_tokens for r in model_results if r.output_tokens)

            performance_data["model_comparison"][model] = {
                "total_tests": len(model_results),
                "successful_tests": len(successful),
                "success_rate": len(successful) / len(model_results),
                "avg_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "score_std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                "min_score": min(scores),
                "max_score": max(scores),
                "avg_response_time": statistics.mean(times),
                "median_response_time": statistics.median(times),
                "response_time_std_dev": statistics.stdev(times) if len(times) > 1 else 0.0,
                "total_cost": sum(costs) if costs else 0.0,
                "avg_cost_per_test": statistics.mean(costs) if costs else 0.0,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "avg_input_tokens_per_test": total_input_tokens / len(model_results) if model_results else 0.0,
                "avg_output_tokens_per_test": total_output_tokens / len(model_results) if model_results else 0.0,
                "perfect_scores": sum(1 for r in successful if r.perfect_score),
                "excellent_responses": sum(1 for r in successful if r.response_quality == "excellent"),
                "good_responses": sum(1 for r in successful if r.response_quality == "good"),
                "fair_responses": sum(1 for r in successful if r.response_quality == "fair"),
                "poor_responses": sum(1 for r in successful if r.response_quality == "poor"),
                "error_rate": (len(model_results) - len(successful)) / len(model_results),
                "consistency_score": 1.0 - (statistics.stdev(scores) if len(scores) > 1 else 0.0)
            }

    # Aggregate statistics
    all_successful = [r for r in results if r.ok]
    if all_successful:
        all_scores = [r.score for r in all_successful]
        all_times = [r.elapsed_s for r in all_successful]
        all_costs = [r.cost_usd for r in results if r.cost_usd]

        performance_data["aggregate_statistics"] = {
            "overall_success_rate": len(all_successful) / len(results),
            "avg_score_across_models": statistics.mean(all_scores),
            "score_range": [min(all_scores), max(all_scores)],
            "avg_response_time": statistics.mean(all_times),
            "response_time_range": [min(all_times), max(all_times)],
            "total_cost_all_models": sum(all_costs) if all_costs else 0.0,
            "cost_per_test_range": [min(all_costs), max(all_costs)] if all_costs else [0.0, 0.0]
        }

    # Write performance analysis
    with open(outdir / "performance_analysis.json", "w", encoding="utf-8") as f:
        json.dump(performance_data, f, indent=2, default=str)


# ------------------------ Enhanced Language Performance Analysis -------------------------
def analyze_language_performance(results: List[EnhancedRunResult], models: List[str]) -> Dict[
    str, Dict[str, Dict[str, float]]]:
    """Analyze performance by programming language."""

    # Define language test mappings
    language_patterns = {
        'Python': ['python', 'django', 'flask', 'pickle', 'eval', 'exec'],
        'JavaScript/Node.js': ['javascript', 'js', 'typescript', 'node', 'prototype', 'npm'],
        'Java/JVM': ['java', 'kotlin', 'scala', 'jvm', 'deserialization', 'spring'],
        'C/C++': ['c_', 'cpp_', 'buffer_overflow', 'memory', 'unsafe'],
        'Mobile': ['kotlin', 'swift', 'android', 'ios', 'intent', 'keychain'],
        'Web Technologies': ['xss', 'csrf', 'sql_injection', 'ssrf', 'ssti'],
        'Systems': ['go_', 'rust_', 'race_condition', 'concurrency'],
        'Modern Languages': ['dart', 'flutter', 'haskell', 'functional']
    }

    language_results = {}

    for language, patterns in language_patterns.items():
        language_results[language] = {}

        # Filter tests for this language
        lang_tests = [r for r in results if any(pattern in r.suite_id.lower() for pattern in patterns)]

        if not lang_tests:
            continue

        for model in models:
            model_tests = [r for r in lang_tests if r.model == model]
            if model_tests:
                avg_score = sum(r.score for r in model_tests) / len(model_tests)
                avg_time = sum(r.elapsed_s for r in model_tests) / len(model_tests)
                success_rate = sum(1 for r in model_tests if r.ok) / len(model_tests)

                language_results[language][model] = {
                    'avg_score': avg_score,
                    'avg_time': avg_time,
                    'success_rate': success_rate,
                    'test_count': len(model_tests)
                }

    return language_results


def calculate_enhanced_cost_effectiveness(perf: 'ModelPerformance') -> float:
    """Calculate enhanced cost effectiveness that balances accuracy and cost.
    
    Formula: (accuracy_weight * score^2 + reliability_weight * success_rate + speed_bonus) / cost
    Where accuracy is emphasized over pure cheapness.
    """
    if perf.cost_per_test <= 0:
        return float('inf')  # Free models get infinite cost effectiveness

    # Weights favor accuracy over cost
    accuracy_weight = 0.6  # Primary factor
    reliability_weight = 0.3  # Secondary factor  
    speed_bonus_weight = 0.1  # Minor factor

    # Quadratic scoring rewards high accuracy significantly more
    accuracy_score = perf.avg_score ** 2  # Quadratic to heavily favor accurate models
    reliability_score = perf.success_rate

    # Speed bonus: faster is better, but capped
    speed_bonus = max(0, min(1.0, (10 - perf.avg_response_time) / 10))

    # Combined quality score
    quality_score = (accuracy_weight * accuracy_score +
                     reliability_weight * reliability_score +
                     speed_bonus_weight * speed_bonus)

    # Cost effectiveness = quality per dollar
    return quality_score / perf.cost_per_test


# ------------------------ Visualization Generation -------------------------
def generate_performance_charts(results: List[EnhancedRunResult], models: List[str], outdir: Path) -> Dict[str, str]:
    """Generate performance visualization charts."""
    if not VISUALIZATION_AVAILABLE:
        print("⚠️  Visualization libraries not available. Skipping chart generation.")
        return {}

    charts_created = {}

    # Set style
    plt.style.use('default')
    sns.set_palette("husl")

    # Performance by model
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)

    if not performance_by_model:
        return charts_created

    # 1. Model Performance Comparison (Score vs Response Time)
    fig, ax = plt.subplots(figsize=(12, 8))

    models_list = list(performance_by_model.keys())
    scores = [performance_by_model[m].avg_score for m in models_list]
    times = [performance_by_model[m].avg_response_time for m in models_list]
    costs = [performance_by_model[m].cost_per_test * 1000 for m in models_list]  # Convert to milli-dollars

    scatter = ax.scatter(times, scores, s=[c * 100 for c in costs], alpha=0.7, c=range(len(models_list)),
                         cmap='viridis')

    # Add model labels
    for i, model in enumerate(models_list):
        ax.annotate(model, (times[i], scores[i]), xytext=(5, 5), textcoords='offset points', fontsize=10)

    ax.set_xlabel('Average Response Time (seconds)')
    ax.set_ylabel('Average Security Score')
    ax.set_title('Model Performance: Security Score vs Response Time\n(Bubble size = Cost per test)')
    ax.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(scatter)
    cbar.set_label('Model Index')

    plt.tight_layout()
    chart_path = outdir / "performance_comparison.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    charts_created["performance_comparison"] = str(chart_path)

    # 2. Cost Effectiveness Chart
    fig, ax = plt.subplots(figsize=(10, 6))

    effectiveness = [performance_by_model[m].cost_effectiveness for m in models_list]
    colors = sns.color_palette("viridis", len(models_list))

    bars = ax.bar(models_list, effectiveness, color=colors)
    ax.set_ylabel('Quality-Weighted Security Points per Dollar')
    ax.set_title('Cost Effectiveness by Model\n(Prioritizes Accuracy, Reliability, and Consistency)')
    ax.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar, eff in zip(bars, effectiveness):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + max(effectiveness) * 0.01,
                f'{eff:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    chart_path = outdir / "cost_effectiveness.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    charts_created["cost_effectiveness"] = str(chart_path)

    # 3. Token Usage Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    input_tokens = [performance_by_model[m].total_input_tokens for m in models_list]
    output_tokens = [performance_by_model[m].total_output_tokens for m in models_list]

    # Input tokens
    ax1.bar(models_list, input_tokens, color='lightblue', alpha=0.7)
    ax1.set_ylabel('Total Input Tokens')
    ax1.set_title('Input Token Usage by Model')
    ax1.tick_params(axis='x', rotation=45)

    # Output tokens
    ax2.bar(models_list, output_tokens, color='lightcoral', alpha=0.7)
    ax2.set_ylabel('Total Output Tokens')
    ax2.set_title('Output Token Usage by Model')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    chart_path = outdir / "token_usage.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    charts_created["token_usage"] = str(chart_path)

    # 4. Performance Metrics Chart
    if len(models_list) >= 2:
        # Multi-model grouped bar chart for clear comparison
        fig, ax = plt.subplots(figsize=(12, 8))

        # Prepare data
        metrics = ['Success Rate %', 'Avg Score %', 'Response Time (normalized)', 'Cost Effectiveness (normalized)']
        x = np.arange(len(metrics))
        width = 0.8 / len(models_list)  # Bar width based on number of models

        colors = plt.cm.Set3(np.linspace(0, 1, len(models_list)))

        for i, model in enumerate(models_list):
            perf = performance_by_model[model]
            values = [
                perf.success_rate * 100,
                perf.avg_score * 100,
                100 - min((perf.avg_response_time / 10) * 100, 100),  # Inverted: faster = higher score
                min(100 * (perf.cost_effectiveness / max(p.cost_effectiveness for p in performance_by_model.values())),
                    100) if performance_by_model else 0  # Relative to best model
            ]

            bars = ax.bar(x + (i - len(models_list) / 2 + 0.5) * width, values,
                          width, label=model, color=colors[i], alpha=0.8)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Performance Metrics')
        ax.set_ylabel('Score (0-100)')
        ax.set_title('Model Performance Comparison - Side by Side')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=15, ha='right')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')

        # Add performance zones
        ax.axhspan(0, 30, alpha=0.1, color='red', label='Poor')
        ax.axhspan(30, 70, alpha=0.1, color='yellow', label='Good')
        ax.axhspan(70, 100, alpha=0.1, color='green', label='Excellent')

        plt.tight_layout()
        chart_path = outdir / "performance_comparison_bars.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created["performance_comparison_bars"] = str(chart_path)

    elif len(models_list) == 1:
        # Single model performance breakdown
        model = models_list[0]
        perf = performance_by_model[model]

        fig, ax = plt.subplots(figsize=(10, 6))

        # Performance metrics for single model
        metrics = ['Success Rate', 'Avg Score', 'Speed Score', 'Cost Effectiveness']
        values = [
            perf.success_rate * 100,
            perf.avg_score * 100,
            min(perf.speed_score * 10, 100),  # Normalized
            min(perf.cost_effectiveness / 200, 100)  # Normalized: 20000 points/dollar = 100%
        ]
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        bars = ax.barh(metrics, values, color=colors, alpha=0.7)
        ax.set_xlabel('Performance Score')
        ax.set_title(f'{model} - Security Performance Breakdown')
        ax.set_xlim(0, 100)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height() / 2,
                    f'{value:.1f}%' if value < 10 else f'{value:.0f}%',
                    ha='left', va='center', fontweight='bold')

        # Add performance zones
        ax.axvspan(0, 30, alpha=0.1, color='red', label='Poor')
        ax.axvspan(30, 70, alpha=0.1, color='yellow', label='Good')
        ax.axvspan(70, 100, alpha=0.1, color='green', label='Excellent')

        plt.tight_layout()
        chart_path = outdir / "performance_breakdown.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts_created["performance_breakdown"] = str(chart_path)

    # 5. Language-specific Performance Analysis
    try:
        language_data = analyze_language_performance(results, models)
        if language_data and len(language_data) > 0:
            # Create analysis with reliability metrics
            lang_data = create_language_analysis(results, models)

            # Generate improved visualizations
            charts_created.update(generate_language_charts(lang_data, outdir))

    except Exception as e:
        print(f"⚠️  Enhanced language performance analysis failed: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("Skipping heatmap generation due to analysis failure")


def create_language_analysis(results: List[EnhancedRunResult], models: List[str]) -> Dict:
    """Create language analysis with reliability metrics and test type breakdown."""

    # Language and test type patterns (order matters - more specific patterns first)
    language_patterns = {
        'Rust': ['rust_', 'rust'],
        'Python': ['python_', 'python', 'django', 'flask', 'pickle', 'eval', 'exec'],
        'JavaScript': ['javascript_', 'javascript', 'js_', 'js', 'typescript_', 'typescript', 'node', 'prototype', 'npm'],
        'Java/JVM': ['java_', 'java', 'kotlin_', 'kotlin', 'scala_', 'scala', 'jvm', 'spring'],
        'C/C++': ['c_', 'c', 'cpp_', 'cpp'],
        'Mobile': ['swift_', 'swift', 'android', 'ios', 'intent', 'keychain'],
        'Go': ['go_', 'go', 'golang'],
        'PHP': ['php_', 'php'],
        'Ruby': ['ruby_', 'ruby'],
        'Haskell': ['haskell_', 'haskell'],
        'Scala': ['scala_', 'scala'],
        'Kotlin': ['kotlin_', 'kotlin'],
        'Dart': ['dart_', 'dart']
    }

    test_type_patterns = {
        'SAST': ['sast', 'static', 'lint', 'code_analysis', 'injection', 'xss', 'sql', 'buffer_overflow', 
                'race_condition', 'path_traversal', 'format_string', 'integer_overflow', 'null_pointer',
                'use_after_free', 'double_free', 'memory_leak', 'toctou', 'deserialization', 'xxe',
                'ldap_injection', 'mass_assignment', 'jwt', 'crypto', 'random', 'tls', 'direct_object',
                'code_injection', 'exec_injection', 'unsafe_pointer', 'memory_safety', 'goroutine_leak',
                'json_injection', 'tls_config', 'prototype_pollution', 'regex_dos', 'jwt_vulnerabilities',
                'xss_dom', 'nosql_injection', 'command_injection', 'sql_injection', 'pickle_deserialization',
                'xml_external_entity', 'path_traversal', 'network_security', 'url_scheme', 'webview',
                'plist_xml', 'core_data', 'insecure_storage'],
        'Secrets': ['secret', 'token', 'key', 'credential', 'hardcoded'],
        'OWASP': ['owasp', 'top10', 'csrf', 'broken_access', 'weak_authentication', 'weak_cryptography',
                 'insecure_deserialization', 'xml_external_entity', 'ssrf', 'insecure_direct_object'],
        'Quality': ['comprehensive', 'basic', 'quality']
    }

    def classify_test(suite_id: str) -> Tuple[str, str]:
        """Classify test by language and type."""
        suite_lower = suite_id.lower()

        # Determine language
        language = 'Other'
        for lang, patterns in language_patterns.items():
            if any(pattern in suite_lower for pattern in patterns):
                language = lang
                break

        # Determine test type  
        test_type = 'Quality'  # Default
        for t_type, patterns in test_type_patterns.items():
            if any(pattern in suite_lower for pattern in patterns):
                test_type = t_type
                break

        return language, test_type

    # Analyze results with enhanced classification
    analysis = {}

    for result in results:
        language, test_type = classify_test(result.suite_id)
        model = result.model

        # Initialize structure
        if language not in analysis:
            analysis[language] = {}
        if test_type not in analysis[language]:
            analysis[language][test_type] = {}
        if model not in analysis[language][test_type]:
            analysis[language][test_type][model] = {
                'scores': [], 'times': [], 'costs': [], 'successes': [], 'suite_ids': []
            }

        # Collect data
        data = analysis[language][test_type][model]
        data['scores'].append(result.score)
        data['times'].append(result.elapsed_s)
        data['costs'].append(result.cost_usd if hasattr(result, 'cost_usd') else 0)
        data['successes'].append(1 if result.ok else 0)
        data['suite_ids'].append(result.suite_id)

    # Ensure all models are represented in analysis structure
    # This handles models that had zero results (complete failures)
    all_languages = set()
    all_test_types = set()

    # First pass: collect all languages and test types that exist
    for language in analysis:
        all_languages.add(language)
        for test_type in analysis[language]:
            all_test_types.add(test_type)

    # If no results exist at all, create minimal structure
    if not all_languages:
        all_languages = {'Other'}
        all_test_types = {'Quality'}

    # Second pass: ensure all models exist in all language/test_type combinations
    for language in all_languages:
        if language not in analysis:
            analysis[language] = {}
        for test_type in all_test_types:
            if test_type not in analysis[language]:
                analysis[language][test_type] = {}
            for model in models:
                if model not in analysis[language][test_type]:
                    analysis[language][test_type][model] = {
                        'scores': [], 'times': [], 'costs': [], 'successes': [], 'suite_ids': []
                    }

    # Calculate enhanced metrics
    for language in analysis:
        for test_type in analysis[language]:
            for model in analysis[language][test_type]:
                data = analysis[language][test_type][model]

                # Handle completely failed models (no successful results)
                if not data['scores']:
                    # Set default values for failed models to ensure they appear in heatmaps
                    analysis[language][test_type][model] = {
                        'mean_score': 0.0,
                        'score_std': 0.0,
                        'score_ci_95': 0.0,
                        'mean_time': 0.0,
                        'time_p95': 0.0,
                        'n': 0,
                        'success_rate': 0.0,
                        'completeness': 0.0,
                        'reliability': 0.0,
                        'cost_per_test': 0.0,
                        'qfs': 0.0,
                        'accuracy_rank_score': 0.0,
                        'accuracy_completeness_score': 0.0,
                        'empty_rate': 1.0,
                        'timeout_rate': 0.0,
                        'raw_scores': [],
                        'raw_times': []
                    }
                    continue

                # Calculate robust statistics - filter out None values
                scores = np.array([s for s in data['scores'] if s is not None])
                times = np.array([t for t in data['times'] if t is not None])
                costs = np.array([c for c in data['costs'] if c is not None])
                successes = np.array([s for s in data['successes'] if s is not None])
                
                # Handle empty arrays by setting default values
                if len(scores) == 0 or len(times) == 0 or len(successes) == 0:
                    # Set default values for failed models to ensure they appear in heatmaps
                    analysis[language][test_type][model] = {
                        'mean_score': 0.0,
                        'score_std': 0.0,
                        'score_ci_95': 0.0,
                        'mean_time': 0.0,
                        'time_p95': 0.0,
                        'n': 0,
                        'success_rate': 0.0,
                        'completeness': 0.0,
                        'reliability': 0.0,
                        'cost_per_test': 0.0,
                        'qfs': 0.0,
                        'accuracy_rank_score': 0.0,
                        'accuracy_completeness_score': 0.0,
                        'empty_rate': 1.0,
                        'timeout_rate': 0.0,
                        'raw_scores': [],
                        'raw_times': []
                    }
                    continue
                
                # Handle empty costs array separately
                if len(costs) == 0:
                    costs = np.array([0.0])  # Default to 0 cost

                n = len(scores)

                # Central tendency and spread
                mean_score = np.mean(scores) if len(scores) > 0 else 0.0
                score_std = np.std(scores, ddof=1) if n > 1 else 0
                score_ci = 1.96 * score_std / np.sqrt(n) if n > 1 else 0

                mean_time = np.mean(times) if len(times) > 0 else 0.0
                time_p95 = np.percentile(times, 95) if len(times) >= 5 else mean_time

                # Reliability metrics
                success_rate = np.mean(successes) if len(successes) > 0 else 0.0
                empty_rate = 1 - success_rate  # Simplified
                timeout_rate = sum(1 for t in times if t is not None and t > 30) / n if n > 0 else 0  # 30s timeout proxy

                reliability = 1 - empty_rate - timeout_rate
                reliability = max(0, min(1, reliability))  # Clip to [0,1]

                # Calculate Quality-First Score (QFS) using audit-compliant methodology
                cost_per_test = np.mean(costs) if len(costs) > 0 else 0.0

                # Use simplified metrics if available and enabled
                if SIMPLIFIED_POLICY_AVAILABLE and get_config().simple_mode:
                    # Use simplified policy metrics
                    from simplified_metrics import smoothed_rate, reliability_fixed, qfs_hybrid
                    
                    # Completeness with smoothing
                    threshold = get_config().completeness_threshold
                    k_complete = int(np.sum(scores >= threshold))
                    completeness = smoothed_rate(
                        k_complete, n,
                        prior=get_config().completeness_prior,
                        prior_total=get_config().completeness_prior_total
                    )
                    
                    # Reliability with simplified calculation
                    reliability = reliability_fixed(successes, times, get_config().get_timeout(test_type))
                    
                    # QFS without coverage (breadth coverage handled separately)
                    qfs = qfs_hybrid(
                        mean_score, completeness, 1.0, reliability,  # coverage = 1.0 (neutral)
                        get_config().qfs_weights, epsilon=0.05
                    )
                    
                    # Breadth coverage (optional)
                    breadth_cov = np.nan  # Will be calculated separately if needed
                    
                    # Set coverage for compatibility with existing code
                    coverage = 1.0  # Neutral coverage in simplified mode
                    
                elif QFS_AUDIT_AVAILABLE:
                    # Use centralized QFS configuration and functions
                    completeness = sum(1 for s in scores if s is not None and s >= CONFIG.COMPLETENESS_THRESHOLD) / n if n > 0 else 0
                    coverage = sum(1 for s in scores if s is not None and s >= CONFIG.COVERAGE_THRESHOLD) / n if n > 0 else 0

                    # Calculate cost p95 for proper normalization  
                    all_costs = []
                    for lang_data in analysis.values():
                        for test_data in lang_data.values():
                            for model_data in test_data.values():
                                if 'costs' in model_data:
                                    # Filter out None values from costs
                                    valid_costs = [c for c in model_data['costs'] if c is not None]
                                    all_costs.extend(valid_costs)
                                else:
                                    all_costs.append(cost_per_test)
                    # Filter out None values from all_costs before percentile calculation
                    all_costs = [c for c in all_costs if c is not None]
                    cost_p95 = np.percentile(all_costs, 95) if all_costs else 0.1

                    # Use audited QFS calculation with proper cost normalization
                    qfs = calculate_qfs(mean_score, completeness, coverage, reliability, cost_per_test, cost_p95)
                    qfs_raw = calculate_qfs(mean_score, completeness, coverage, reliability, 0.0, 1.0)
                else:
                    # Fallback to original calculation
                    completeness = sum(1 for s in scores if s is not None and s >= 0.8) / n if n > 0 else 0
                    coverage = sum(1 for s in scores if s is not None and s >= 0.5) / n if n > 0 else 0

                    A, Cmpl, Cov, Rel = mean_score, completeness, coverage, reliability

                    if A > 0 and Cmpl > 0 and Cov > 0 and Rel > 0:
                        qfs_raw = (A ** 0.50) * (Cmpl ** 0.30) * (Cov ** 0.15) * (Rel ** 0.05)

                        if cost_per_test > 0:
                            max_cost_estimate = 0.1
                            cost_normalized = np.log1p(cost_per_test) / np.log1p(max_cost_estimate)
                            cost_normalized = min(cost_normalized, 1.0)
                            qfs = qfs_raw / (1 + 0.15 * cost_normalized)
                        else:
                            qfs = qfs_raw
                    else:
                        qfs_raw = qfs = 0

                # Traditional accuracy-only ranking for comparison
                accuracy_rank_score = mean_score

                # Accuracy + Completeness combo for sanity check
                accuracy_completeness_score = (mean_score * 0.7) + (completeness * 0.3)

                # Store enhanced metrics
                analysis[language][test_type][model] = {
                    'n': n,
                    'mean_score': mean_score,
                    'completeness': completeness,
                    'coverage': coverage,
                    'score_std': score_std,
                    'score_ci_95': score_ci,
                    'mean_time': mean_time,
                    'time_p95': time_p95,
                    'success_rate': success_rate,
                    'reliability': reliability,
                    'cost_per_test': cost_per_test,
                    'qfs': qfs,
                    'accuracy_rank_score': accuracy_rank_score,
                    'accuracy_completeness_score': accuracy_completeness_score,
                    'empty_rate': empty_rate,
                    'timeout_rate': timeout_rate,
                    'raw_scores': scores.tolist(),
                    'raw_times': times.tolist()
                }

    return analysis


def generate_language_charts(analysis_data: Dict, outdir: Path) -> Dict[str, str]:
    """Generate language performance charts with statistical analysis."""

    if not VISUALIZATION_AVAILABLE:
        return {}

    charts = {}

    # 1. Language × Test Type Heatmaps
    try:
        create_language_test_heatmaps(analysis_data, outdir, charts)
    except Exception as e:
        print(f"⚠️ Heatmap generation failed: {e}")

    # 2. Per-slice detailed charts with confidence intervals
    try:
        create_detailed_slice_charts(analysis_data, outdir, charts)
    except Exception as e:
        print(f"⚠️ Detailed slice charts failed: {e}")

    # 3. Enhanced scatter plot with Pareto frontier
    try:
        create_pareto_scatter(analysis_data, outdir, charts)
    except Exception as e:
        print(f"⚠️ Pareto scatter failed: {e}")

    # Quality-first executive summary removed - now handled by unified executive summary

    return charts


def create_language_test_heatmaps(analysis_data: Dict, outdir: Path, charts: Dict):
    """Create heatmaps for Language × Model performance by test type."""

    # Get all languages and models
    all_languages = sorted(analysis_data.keys())
    all_models = set()
    for lang_data in analysis_data.values():
        for test_data in lang_data.values():
            all_models.update(test_data.keys())
    all_models = sorted(list(all_models))

    # Get all test types
    all_test_types = set()
    for lang_data in analysis_data.values():
        all_test_types.update(lang_data.keys())
    all_test_types = sorted(list(all_test_types))

    # Create separate heatmap for each test type
    for test_type in all_test_types:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Initialize matrices for quality-first analysis
        accuracy_matrix = np.full((len(all_models), len(all_languages)), np.nan)
        completeness_matrix = np.full((len(all_models), len(all_languages)), np.nan)
        qfs_matrix = np.full((len(all_models), len(all_languages)), np.nan)
        reliability_matrix = np.full((len(all_models), len(all_languages)), np.nan)

        for i, model in enumerate(all_models):
            for j, language in enumerate(all_languages):
                if language in analysis_data and test_type in analysis_data[language]:
                    if model in analysis_data[language][test_type]:
                        data = analysis_data[language][test_type][model]
                        # Defensive programming for missing fields
                        accuracy_matrix[i, j] = data.get('mean_score', 0.0) * 100
                        completeness_matrix[i, j] = data.get('completeness', 0.0) * 100
                        qfs_matrix[i, j] = data.get('qfs', 0.0) * 100
                        reliability_matrix[i, j] = data.get('reliability', 0.0) * 100
                    else:
                        # Model has no data for this language/test_type combination
                        # In simplified mode, show 0 instead of NaN
                        if SIMPLIFIED_POLICY_AVAILABLE and get_config().simple_mode:
                            accuracy_matrix[i, j] = 0.0
                            completeness_matrix[i, j] = 0.0
                            qfs_matrix[i, j] = 0.0
                            reliability_matrix[i, j] = 0.0
                        else:
                            # Legacy mode - keep NaN for missing data
                            accuracy_matrix[i, j] = np.nan
                            completeness_matrix[i, j] = np.nan
                            qfs_matrix[i, j] = np.nan
                            reliability_matrix[i, j] = np.nan
                else:
                    # Language/test_type combination doesn't exist
                    # In simplified mode, show 0 instead of NaN
                    if SIMPLIFIED_POLICY_AVAILABLE and get_config().simple_mode:
                        accuracy_matrix[i, j] = 0.0
                        completeness_matrix[i, j] = 0.0
                        qfs_matrix[i, j] = 0.0
                        reliability_matrix[i, j] = 0.0
                    else:
                        # Legacy mode - keep NaN for missing data
                        accuracy_matrix[i, j] = np.nan
                        completeness_matrix[i, j] = np.nan
                        qfs_matrix[i, j] = np.nan
                        reliability_matrix[i, j] = np.nan

        # Accuracy heatmap
        im1 = ax1.imshow(accuracy_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        ax1.set_title(f'{test_type}: Accuracy % (with sample sizes)', fontweight='bold')
        ax1.set_xticks(range(len(all_languages)))
        ax1.set_xticklabels(all_languages, rotation=45, ha='right')
        ax1.set_yticks(range(len(all_models)))
        ax1.set_yticklabels(all_models)

        # Add text annotations with n and confidence intervals
        for i in range(len(all_models)):
            for j in range(len(all_languages)):
                if not np.isnan(accuracy_matrix[i, j]) and accuracy_matrix[i, j] > 0:
                    language = all_languages[j]
                    model = all_models[i]
                    if (language in analysis_data and test_type in analysis_data[language] and
                            model in analysis_data[language][test_type]):
                        data = analysis_data[language][test_type][model]
                        # Defensive programming for missing fields
                        n = data.get('n', 0)
                        ci = data.get('score_ci_95', 0.0) * 100
                        
                        # Add timeout indicator if enabled
                        timeout_indicator = ""
                        if SIMPLIFIED_POLICY_AVAILABLE and get_config().show_timeout_glyph:
                            timeout_rate = data.get('timeout_rate', 0.0)
                            if timeout_rate > 0:
                                timeout_indicator = f"\n{get_config().timeout_glyph}"
                        
                        text = f"{accuracy_matrix[i, j]:.0f}%\n(n={n})\n±{ci:.1f}{timeout_indicator}"
                        ax1.text(j, i, text, ha='center', va='center',
                                 fontsize=8, color='black' if accuracy_matrix[i, j] < 50 else 'white')
                    else:
                        # Show "N/A" for missing data (only in legacy mode)
                        if not (SIMPLIFIED_POLICY_AVAILABLE and get_config().simple_mode):
                            ax1.text(j, i, "N/A", ha='center', va='center',
                                     fontsize=8, color='gray')
                elif not np.isnan(accuracy_matrix[i, j]) and accuracy_matrix[i, j] == 0:
                    # Show "0" for zero scores
                    ax1.text(j, i, "0%", ha='center', va='center',
                             fontsize=8, color='black')

        plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

        # Completeness heatmap (% of tests with good detection >= 0.8)
        im2 = ax2.imshow(completeness_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        ax2.set_title(f'{test_type}: Completeness % (Good Detection ≥80%)', fontweight='bold')
        ax2.set_xticks(range(len(all_languages)))
        ax2.set_xticklabels(all_languages, rotation=45, ha='right')
        ax2.set_yticks(range(len(all_models)))
        ax2.set_yticklabels(all_models)

        for i in range(len(all_models)):
            for j in range(len(all_languages)):
                if not np.isnan(completeness_matrix[i, j]) and completeness_matrix[i, j] > 0:
                    ax2.text(j, i, f"{completeness_matrix[i, j]:.0f}%", ha='center', va='center',
                             fontsize=9, color='black' if completeness_matrix[i, j] < 50 else 'white')
                elif not np.isnan(completeness_matrix[i, j]) and completeness_matrix[i, j] == 0:
                    ax2.text(j, i, "0%", ha='center', va='center',
                             fontsize=9, color='black')

        plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

        # Quality-First Score heatmap (primary ranking metric)
        im3 = ax3.imshow(qfs_matrix, cmap='viridis', aspect='auto', vmin=0, vmax=100)
        ax3.set_title(f'{test_type}: Quality-First Score (Accuracy⁰·⁵×Completeness⁰·³×Coverage⁰·¹⁵)', fontweight='bold')
        ax3.set_xticks(range(len(all_languages)))
        ax3.set_xticklabels(all_languages, rotation=45, ha='right')
        ax3.set_yticks(range(len(all_models)))
        ax3.set_yticklabels(all_models)

        # Calculate ranks for QFS and annotate
        for i in range(len(all_models)):
            for j in range(len(all_languages)):
                if not np.isnan(qfs_matrix[i, j]):
                    # Calculate rank within this language for this test type
                    language = all_languages[j]
                    if language in analysis_data and test_type in analysis_data[language]:
                        lang_qfs_values = [(model, data['qfs']) for model, data in
                                           analysis_data[language][test_type].items()]
                        lang_qfs_values.sort(key=lambda x: x[1], reverse=True)
                        model_rank = next((idx + 1 for idx, (model, _) in enumerate(lang_qfs_values)
                                           if model == all_models[i]), None)

                        text = f"{qfs_matrix[i, j]:.1f}%\n(#{model_rank})" if model_rank else f"{qfs_matrix[i, j]:.1f}%"
                        ax3.text(j, i, text, ha='center', va='center', fontsize=8,
                                 color='white' if qfs_matrix[i, j] < np.nanmean(qfs_matrix) else 'black')

        plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

        # Reliability heatmap (1 - empty - timeout - json_fail)
        im4 = ax4.imshow(reliability_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        ax4.set_title(f'{test_type}: Reliability % (1-Empty-Timeout)', fontweight='bold')
        ax4.set_xticks(range(len(all_languages)))
        ax4.set_xticklabels(all_languages, rotation=45, ha='right')
        ax4.set_yticks(range(len(all_models)))
        ax4.set_yticklabels(all_models)

        for i in range(len(all_models)):
            for j in range(len(all_languages)):
                if not np.isnan(reliability_matrix[i, j]):
                    language = all_languages[j]
                    model = all_models[i]
                    # Show reliability with flags for problematic models
                    if (language in analysis_data and test_type in analysis_data[language] and
                            model in analysis_data[language][test_type]):
                        data = analysis_data[language][test_type][model]
                        fail_rate = data['empty_rate'] + data['timeout_rate']
                        flag = "⚠️" if fail_rate > 0.1 else ""
                        text = f"{reliability_matrix[i, j]:.0f}%\n{flag}"
                        ax4.text(j, i, text, ha='center', va='center', fontsize=8,
                                 color='black' if reliability_matrix[i, j] < 50 else 'white')

        plt.colorbar(im4, ax=ax4, fraction=0.046, pad=0.04)

        plt.tight_layout()
        chart_path = outdir / f"enhanced_heatmaps_{test_type.lower()}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts[f"heatmap_{test_type.lower()}"] = str(chart_path)


def create_detailed_slice_charts(analysis_data: Dict, outdir: Path, charts: Dict):
    """Create detailed charts for specific language/test-type slices."""

    # Focus on top combinations by data availability
    slice_priorities = []
    for language in analysis_data:
        for test_type in analysis_data[language]:
            total_n = sum(data['n'] for data in analysis_data[language][test_type].values())
            slice_priorities.append((total_n, language, test_type))

    # Take top 6 slices by data volume
    top_slices = sorted(slice_priorities, reverse=True)[:6]

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, (_, language, test_type) in enumerate(top_slices):
        ax = axes[idx]
        slice_data = analysis_data[language][test_type]

        models = list(slice_data.keys())
        accuracies = [slice_data[m]['mean_score'] * 100 for m in models]
        cis = [slice_data[m]['score_ci_95'] * 100 for m in models]
        ns = [slice_data[m]['n'] for m in models]

        # Sort by accuracy
        sorted_indices = np.argsort(accuracies)[::-1]
        models = [models[i] for i in sorted_indices]
        accuracies = [accuracies[i] for i in sorted_indices]
        cis = [cis[i] for i in sorted_indices]
        ns = [ns[i] for i in sorted_indices]

        # Bar plot with error bars
        bars = ax.bar(range(len(models)), accuracies, yerr=cis, capsize=5,
                      alpha=0.8, color=plt.cm.Set3(np.linspace(0, 1, len(models))))

        # Add n annotations
        for i, (bar, n, acc) in enumerate(zip(bars, ns, accuracies)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + cis[i] + 2,
                    f'n={n}', ha='center', va='bottom', fontsize=8, fontweight='bold')
            ax.text(bar.get_x() + bar.get_width() / 2., height / 2,
                    f'{acc:.1f}%', ha='center', va='center', fontsize=9, fontweight='bold')

        ax.set_title(f'{language} / {test_type}\nAccuracy with 95% CI', fontweight='bold')
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels([m.replace('-', '\n') for m in models], rotation=0, ha='center', fontsize=8)
        ax.set_ylabel('Accuracy (%)')
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')

        # Flag low sample sizes
        if min(ns) < 30:
            ax.text(0.02, 0.98, f'⚠️ Low n (min={min(ns)})', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
                    verticalalignment='top', fontsize=8)

    plt.tight_layout()
    chart_path = outdir / "detailed_slice_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    charts["detailed_slices"] = str(chart_path)


def create_pareto_scatter(analysis_data: Dict, outdir: Path, charts: Dict):
    """Create scatter plot with Pareto frontier."""

    # Collect all data points
    all_points = []
    colors = plt.cm.Set3(np.linspace(0, 1, 12))  # For different models
    model_to_color = {}
    color_idx = 0

    for language in analysis_data:
        for test_type in analysis_data[language]:
            for model, data in analysis_data[language][test_type].items():
                if model not in model_to_color:
                    model_to_color[model] = colors[color_idx % len(colors)]
                    color_idx += 1

                all_points.append({
                    'model': model,
                    'language': language,
                    'test_type': test_type,
                    'accuracy': data['mean_score'] * 100,
                    'completeness': data['completeness'] * 100,
                    'coverage': data['coverage'] * 100,
                    'latency': data['mean_time'],
                    'cost': data['cost_per_test'],
                    'reliability': data['reliability'] * 100,
                    'qfs': data['qfs'] * 100,
                    'n': data['n'],
                    'color': model_to_color[model]
                })

    if not all_points:
        return

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot points
    for point in all_points:
        ax.scatter(point['latency'], point['accuracy'],
                   s=100 + point['cost'] * 50000,  # Size by cost
                   c=[point['color']], alpha=0.7, edgecolors='black', linewidth=0.5,
                   label=point['model'] if point['model'] not in [p.get_label() for p in ax.get_children()] else "")

    # Calculate and plot Pareto frontier
    pareto_points = []
    for point in all_points:
        is_pareto = True
        for other in all_points:
            if (other['accuracy'] >= point['accuracy'] and other['latency'] <= point['latency'] and
                    not (other['accuracy'] == point['accuracy'] and other['latency'] == point['latency'])):
                is_pareto = False
                break
        if is_pareto:
            pareto_points.append(point)

    if pareto_points:
        # Sort Pareto points by latency for line drawing
        pareto_points.sort(key=lambda x: x['latency'])
        pareto_x = [p['latency'] for p in pareto_points]
        pareto_y = [p['accuracy'] for p in pareto_points]

        ax.plot(pareto_x, pareto_y, 'r--', linewidth=2, alpha=0.8, label='Pareto Frontier')

        # Label Pareto points
        for point in pareto_points:
            ax.annotate(f"{point['model']}\n({point['language']}/{point['test_type']})",
                        (point['latency'], point['accuracy']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    ax.set_xlabel('Average Response Time (seconds)')
    ax.set_ylabel('Security Detection Accuracy (%)')
    ax.set_title('Model Performance: Accuracy vs Latency with Pareto Frontier\n(Bubble size = Cost per test)')
    ax.grid(True, alpha=0.3)

    # Create custom legend
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicates
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    chart_path = outdir / "pareto_scatter_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    charts["pareto_scatter"] = str(chart_path)


def generate_text_performance_summary(results: List[EnhancedRunResult], models: List[str], outdir: Path) -> None:
    """Generate text-based performance summary (complements visual charts when available)."""

    # Calculate performance by model
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)

    if not performance_by_model:
        return

    # Create text-based performance report
    report = f"""# 📊 Performance Analysis Summary

**Analysis Date:** {datetime.now().strftime("%B %d, %Y %H:%M:%S")}
**Models Analyzed:** {len(models)}
**Total Test Results:** {len(results)}

## Model Performance Comparison

"""

    # Sort models by average score
    sorted_models = sorted(performance_by_model.items(), key=lambda x: x[1].avg_score, reverse=True)

    for i, (model, perf) in enumerate(sorted_models, 1):
        # Create simple text "bars" 
        score_bar = "█" * int(perf.avg_score * 20) + "░" * (20 - int(perf.avg_score * 20))
        cost_eff_normalized = min(perf.cost_effectiveness / 100, 20)  # Normalize for display
        cost_bar = "█" * int(cost_eff_normalized) + "░" * (20 - int(cost_eff_normalized))

        report += f"""
### {i}. {model}

**Performance Metrics:**
- Accuracy Score: {perf.avg_score:.3f} {score_bar} ({perf.avg_score:.1%})
- Success Rate: {perf.success_rate:.1%} ({perf.successful_tests}/{perf.total_tests} tests)
- Cost Effectiveness: {perf.cost_effectiveness:.1f} {cost_bar} (points/$)
- Average Response Time: {perf.avg_response_time:.2f} seconds
- Total Cost: ${perf.total_cost:.4f}
- Cost per Test: ${perf.cost_per_test:.5f}

**Quality Distribution:**
- Perfect Scores (1.0): {perf.perfect_scores}
- Good Quality Responses: {perf.good_scores}
- Poor Quality Responses: {perf.poor_scores}

---"""

    # Add summary section
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)

    report += f"""

## 🏆 Top Performers Summary

🎯 **Most Accurate:** {best_accuracy.model_name} ({best_accuracy.avg_score:.1%})
💰 **Best Value:** {best_value.model_name} ({best_value.cost_effectiveness:.1f} points/$)
⚡ **Fastest:** {fastest.model_name} ({fastest.avg_response_time:.2f}s avg)

## 📈 Cost Analysis

**Total Investment:** ${sum(p.total_cost for p in performance_by_model.values()):.4f}
**Average Cost per Test:** ${sum(p.cost_per_test for p in performance_by_model.values()) / len(performance_by_model):.5f}

## 💡 Recommendations

Based on this analysis:

1. **For highest accuracy:** Use {best_accuracy.model_name}
2. **For best value:** Use {best_value.model_name} 
3. **For fastest results:** Use {fastest.model_name}

*Note: For visual charts and advanced analysis, install visualization libraries:*
```bash
pip install matplotlib seaborn pandas numpy
```

---
*Generated by LLM Security Benchmark - Built by Rapticore Security Research Team*
"""

    # Write the text-based report
    with open(outdir / "performance_summary.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✓ Text-based performance summary: {outdir}/performance_summary.txt")


# ------------------------ Enhanced Console Output -------------------------
def print_enhanced_summary(results: List[EnhancedRunResult], models: List[str]) -> None:
    """Print enhanced console summary with business metrics."""
    print(f"\n{'=' * 80}")
    print(f"📊 ENHANCED SECURITY BENCHMARK SUMMARY")
    print(f"{'=' * 80}")

    # Performance by model
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)

    if not performance_by_model:
        print("No results to display.")
        return

    # Header
    print(
        f"\n{'Model':<20} {'Tests':<8} {'Success':<9} {'Avg Score':<10} {'Time(s)':<9} {'Total Cost':<12} {'In/Out Tokens':<15} {'Good/Total':<10}")
    print("-" * 115)

    # Model performance
    for model, perf in performance_by_model.items():
        quality_dist = f"{perf.good_scores}/{perf.total_tests}"
        token_info = f"{perf.total_input_tokens}/{perf.total_output_tokens}"
        cost_str = f"${perf.total_cost:.4f}" if perf.total_cost > 0 else "$0.0000"

        print(f"{model:<20} {perf.successful_tests:>3}/{perf.total_tests:<3} "
              f"{perf.success_rate:>6.1%} {perf.avg_score:>9.3f} "
              f"{perf.avg_response_time:>8.2f} {cost_str:>11} "
              f"{token_info:>14} {quality_dist:>9}")

    # Best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)

    # Calculate total costs across all models
    total_cost_all = sum(perf.total_cost for perf in performance_by_model.values())
    total_tests_all = sum(len([r for r in results if r.model == model]) for model in models)

    print(f"\n{'=' * 80}")
    print(f"🏆 Best Accuracy: {best_accuracy.model_name} (Score: {best_accuracy.avg_score:.3f})")
    print(f"💰 Best Value: {best_value.model_name} (Quality-Aware CE: {best_value.cost_effectiveness:.1f})")
    print(f"⚡ Fastest: {fastest.model_name} (Time: {fastest.avg_response_time:.2f}s)")
    print(f"{'=' * 80}")
    print(f"")
    print(f"💰 TOTAL COST THIS RUN: ${total_cost_all:.4f}")
    print(f"📊 Total Tests Executed: {total_tests_all:,}")
    print(f"📈 Average Cost per Test: ${total_cost_all / total_tests_all:.6f}")
    print(f"")
    print(f"⚠️  NOTE: This benchmark uses paid API services")
    print(f"{'=' * 80}")


# ------------------------ Main Enhanced Benchmark Function -------------------------
def regenerate_reports(results_dir: str, args):
    """Regenerate reports and analysis from existing benchmark results."""
    import pandas as pd

    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return

    detailed_csv = results_path / "detailed_results.csv"
    if not detailed_csv.exists():
        print(f"❌ detailed_results.csv not found in {results_dir}")
        return

    print(f"🔄 Regenerating reports from: {results_dir}")

    # Load existing results
    try:
        df = pd.read_csv(detailed_csv)
        print(f"✓ Loaded {len(df)} test results")

        # Fix duplicates issue: Remove duplicate entries for deepseek-chat and grok-3
        print(f"🔍 Checking for duplicate model entries...")

        # Count tests per model
        model_counts = df['model_name'].value_counts()
        duplicated_models = model_counts[model_counts > 25].index.tolist()

        if duplicated_models:
            print(f"⚠️  Found duplicated models: {duplicated_models}")
            print(f"   Removing duplicate entries to ensure each model has exactly 25 tests")

            # Keep only first 25 tests for each duplicated model
            cleaned_rows = []
            for model in df['model_name'].unique():
                model_data = df[df['model_name'] == model]
                if len(model_data) > 25:
                    print(
                        f"   - {model}: {len(model_data)} tests → 25 tests (removing {len(model_data) - 25} duplicates)")
                    model_data = model_data.head(25)
                cleaned_rows.append(model_data)

            df = pd.concat(cleaned_rows, ignore_index=True)
            print(f"✓ Cleaned dataset: {len(df)} tests across {len(df['model_name'].unique())} models")

            # Save cleaned results
            cleaned_csv = results_path / "detailed_results.csv"
            df.to_csv(cleaned_csv, index=False)
            print(f"✓ Saved cleaned results to: {cleaned_csv}")

        # Convert back to EnhancedRunResult objects
        all_results = []
        for _, row in df.iterrows():
            result = EnhancedRunResult(
                suite_id=row['test_id'],
                model=row['model_name'],
                path="",  # Not saved in CSV
                ok=row['success'],
                elapsed_s=float(row['response_time_s']),
                text="",  # Not saved in CSV
                error="",  # Not saved in CSV
                input_tokens=int(row['input_tokens']) if pd.notna(row['input_tokens']) else 0,
                output_tokens=int(row['output_tokens']) if pd.notna(row['output_tokens']) else 0
            )
            # Add additional fields that exist in our results
            result.score = float(row['score'])
            result.cost_usd = float(row['cost_usd']) if pd.notna(row['cost_usd']) else 0.0
            result.criteria_met = int(row['criteria_met']) if pd.notna(row['criteria_met']) else 0
            result.criteria_missed = int(row['criteria_missed']) if pd.notna(row['criteria_missed']) else 0
            result.must_not_violations = int(row['violations']) if pd.notna(row['violations']) else 0
            all_results.append(result)

        # Get unique models
        models = df['model_name'].unique().tolist()
        print(f"📊 Models found: {models}")

        # Regenerate all reports
        outdir = results_path

        print(f"📋 Regenerating executive summary...")
        try:
            if UNIFIED_EXECUTIVE_AVAILABLE:
                generate_unified_executive_summary(all_results, models, "regenerated", Path(outdir))
                print(f"✓ Executive Summary: {outdir}/executive_summary.md")
            else:
                print(f"⚠️ Unified executive summary not available")
        except Exception as e:
            print(f"❌ Executive summary failed: {e}")

        print(f"📈 Regenerating performance analysis...")
        try:
            generate_performance_analysis(all_results, models, outdir)
            print(f"✓ Performance analysis: {outdir}/performance_analysis.json")
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")

        print(f"📊 Regenerating language-specific analysis...")
        try:
            generate_language_analysis(all_results, models, outdir)
            print(f"✓ Language analysis: {outdir}/language_performance.json")
        except Exception as e:
            print(f"❌ Language analysis failed: {e}")

        # Check if enhanced visualization is available
        try:
            import matplotlib.pyplot as plt
            enhanced_available = True
        except ImportError:
            enhanced_available = False

        if enhanced_available:
            print(f"📈 Regenerating visualization charts...")
            try:
                charts = generate_performance_charts(all_results, models, outdir)
                print(f"✓ Generated {len(charts)} visualization charts")
                for chart_name, chart_path in charts.items():
                    print(f"   - {Path(chart_path).name}")
            except Exception as e:
                print(f"❌ Chart generation failed: {e}")

        print(f"\n🎉 Reports regenerated successfully!")
        print(f"📁 Updated reports in: {outdir}")

    except Exception as e:
        print(f"❌ Failed to regenerate reports: {e}")
        import traceback
        traceback.print_exc()


def generate_language_analysis(all_results: List[EnhancedRunResult], models: List[str], outdir: Path):
    """Generate analysis of model performance by test categories/languages."""

    # Group tests by category
    test_categories = {
        "SQL Injection": ["sql_injection_simple", "sql_injection_complex", "nosql_injection"],
        "Command Injection": ["command_injection", "ldap_injection"],
        "Web Security": ["reflected_xss", "dom_xss", "csrf_vulnerability", "session_fixation"],
        "Access Control": ["broken_access_control", "insecure_direct_object_reference", "jwt_algorithm_confusion"],
        "Cryptography": ["weak_cryptography", "weak_tls_configuration", "hardcoded_secrets"],
        "Data Security": ["insecure_deserialization", "xml_external_entity", "gdpr_compliance"],
        "Infrastructure": ["ssrf_basic", "ssrf_vulnerable_code", "api_rate_limiting"],
        "Business Logic": ["race_condition", "price_manipulation"],
        "OWASP Knowledge": ["owasp_top10_complete", "owasp_top3"]
    }

    # Calculate performance by category for each model
    performance_by_category = {}

    for model in models:
        model_results = [r for r in all_results if r.model == model]
        performance_by_category[model] = {}

        for category, tests in test_categories.items():
            category_results = [r for r in model_results if r.suite_id in tests]
            if category_results:
                avg_score = sum(r.score for r in category_results) / len(category_results)
                success_rate = sum(1 for r in category_results if r.ok) / len(category_results)
                performance_by_category[model][category] = {
                    "avg_score": round(avg_score, 3),
                    "success_rate": round(success_rate, 3),
                    "test_count": len(category_results),
                    "perfect_scores": sum(1 for r in category_results if r.score >= 1.0)
                }

    # Save analysis
    analysis_path = outdir / "language_performance.json"
    with open(analysis_path, 'w') as f:
        json.dump({
            "test_categories": test_categories,
            "performance_by_category": performance_by_category,
            "category_summary": {
                category: {
                    "best_model": max(models, key=lambda m: performance_by_category.get(m, {}).get(category, {}).get(
                        "avg_score", 0)),
                    "avg_score_across_models": round(sum(
                        performance_by_category.get(m, {}).get(category, {}).get("avg_score", 0) for m in models) / len(
                        models), 3),
                    "models_with_perfect_scores": [m for m in models if
                                                   performance_by_category.get(m, {}).get(category, {}).get(
                                                       "perfect_scores", 0) > 0]
                } for category in test_categories.keys()
            }
        }, f, indent=2)


def main():
    """Enhanced main function with comprehensive model support."""
    parser = argparse.ArgumentParser(
        description="Enhanced Multi-LLM Security Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all models on all test suites (comprehensive benchmark)
  python enhanced_multi_llm_benchmark.py --models all --suite all

  # Test premium models on all available tests
  python enhanced_multi_llm_benchmark.py --models premium --suite all

  # Test balanced models on OWASP Top 10
  python enhanced_multi_llm_benchmark.py --models balanced --suite owasp

  # Test fast/budget models on basic security tests
  python enhanced_multi_llm_benchmark.py --models fast --suite basic

  # Custom model and suite selection with JSON export
  python enhanced_multi_llm_benchmark.py --models "gpt-5,claude-opus-4" --suite web_dev --output results.json
        """
    )

    parser.add_argument("--models", type=str, default=",".join(DEFAULT_MODELS[:2]),
                        help="Model selection: 'all' (API models only), 'all+local' (includes local), 'premium', 'balanced', 'fast', 'local', or comma-separated model names")
    parser.add_argument("--suite", type=str, default="fast",
                        help="Test suite: 'all', 'basic', 'fast', 'comprehensive', 'owasp', language names, or path to suite file")
    parser.add_argument("--json", action="store_true",
                        help="Enforce JSON-only outputs")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S,
                        help="Per-call timeout in seconds")
    parser.add_argument("--outdir", type=str, default=None,
                        help="Output directory")
    parser.add_argument("--pricing", type=str, default=None,
                        help="Custom pricing override")
    parser.add_argument("--show-responses", action="store_true",
                        help="Show detailed response analysis for manual validation")
    parser.add_argument("--response-format", type=str, default="detailed",
                        choices=["summary", "detailed", "full"],
                        help="Response display format: summary (compact), detailed (default), full (everything)")
    parser.add_argument("--concurrent", action="store_true", default=True,
                        help="Enable concurrent execution for faster benchmarks (default: True)")
    parser.add_argument("--max-workers", type=int, default=4,
                        help="Maximum concurrent workers (default: 4)")
    parser.add_argument("--executive-report", action="store_true", default=True,
                        help="Generate executive summary report (always enabled)")
    parser.add_argument("--performance-analysis", action="store_true", default=True,
                        help="Enable detailed performance analysis (always enabled)")
    parser.add_argument("--regenerate", type=str, default=None,
                        help="Regenerate reports from existing results directory")
    parser.add_argument("--output", type=str, default=None,
                        help="JSON output file path")
    parser.add_argument("--simplified-mode", action="store_true", default=False,
                        help="Enable simplified policy mode (treat all records as attempted, no N/A cells)")

    args = parser.parse_args()

    # Configure simplified mode if requested
    if args.simplified_mode and SIMPLIFIED_POLICY_AVAILABLE:
        update_config(simple_mode=True)
        print("✅ Simplified policy mode enabled - treating all records as attempted")
    elif args.simplified_mode and not SIMPLIFIED_POLICY_AVAILABLE:
        print("⚠️ Simplified policy mode requested but modules not available. Using legacy mode.")
    elif SIMPLIFIED_POLICY_AVAILABLE:
        print("ℹ️ Simplified policy modules available. Use --simplified-mode to enable.")

    # Handle regenerate mode
    if args.regenerate:
        regenerate_reports(args.regenerate, args)
        return

    load_dotenv()

    # Setup API clients
    clients = {}

    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        clients["openai"] = OpenAI()
        print("✓ OpenAI client initialized")

    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        clients["anthropic"] = anthropic.Anthropic()
        print("✓ Anthropic client initialized")

    if GOOGLE_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        print("✓ Google Gemini client initialized")

    # X.AI Grok client (OpenAI-compatible API)
    if XAI_AVAILABLE and os.getenv("XAI_API_KEY"):
        clients["xai"] = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
        print("✓ X.AI Grok client initialized")

    # DeepSeek client (OpenAI-compatible API)
    if DEEPSEEK_AVAILABLE and os.getenv("DEEPSEEK_API_KEY"):
        clients["deepseek"] = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        print("✓ DeepSeek client initialized")

    # Llama client (can use various OpenAI-compatible providers)
    if LLAMA_AVAILABLE and os.getenv("LLAMA_API_KEY"):
        base_url = os.getenv("LLAMA_BASE_URL", "https://api.openai.com/v1")  # Default to OpenAI-compatible
        clients["llama"] = OpenAI(
            api_key=os.getenv("LLAMA_API_KEY"),
            base_url=base_url,
        )
        print("✓ Llama client initialized")

    # Ollama client (local models)
    if OLLAMA_AVAILABLE:
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            # Test Ollama connection
            response = requests.get(f"{ollama_base_url}/api/version", timeout=5)
            if response.status_code == 200:
                clients["ollama"] = {"base_url": ollama_base_url}
                print("✓ Ollama client initialized")
        except Exception as e:
            print(f"⚠ Ollama not available: {e}")
            print("  Make sure Ollama is running with: ollama serve")

    if not clients:
        sys.exit("❌ No API keys found. Check your .env file.")

    # Add model availability checking function
    def check_model_availability(models_to_check):
        """Check which models are actually available based on initialized clients."""
        available_models = []
        unavailable_models = []

        for model in models_to_check:
            is_available = False

            # Check OpenAI models
            if model.startswith("gpt-") and "openai" in clients:
                is_available = True
            # Check Anthropic models  
            elif model.startswith("claude-") and "anthropic" in clients:
                is_available = True
            # Check Google models
            elif model.startswith("gemini-") and GOOGLE_AVAILABLE and os.getenv("GEMINI_API_KEY"):
                is_available = True
            # Check X.AI models
            elif model.startswith("grok-") and "xai" in clients:
                is_available = True
            # Check DeepSeek models
            elif model.startswith("deepseek-") and "deepseek" in clients:
                is_available = True
            # Check Llama models
            elif model.startswith("llama-") and "llama" in clients:
                is_available = True
            # Check Ollama models
            elif model.startswith("ollama/") and "ollama" in clients:
                # Additionally check if the specific model is pulled
                try:
                    model_name = model.split("/", 1)[1]
                    ollama_base_url = clients["ollama"]["base_url"]
                    response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        available_models_data = response.json()
                        ollama_models = [m["name"].split(":")[0] for m in available_models_data.get("models", [])]
                        is_available = model_name in ollama_models
                except Exception:
                    is_available = False

            if is_available:
                available_models.append(model)
            else:
                unavailable_models.append(model)

        return available_models, unavailable_models

    # Parse model selection
    if args.models.lower() == "all":
        models = ALL_MODELS  # API models only (excludes local)
    elif args.models.lower() == "all+local":
        models = ALL_MODELS + LOCAL_MODELS  # Include local models explicitly
    elif args.models.lower() == "premium":
        models = PREMIUM_MODELS
    elif args.models.lower() == "balanced":
        models = BALANCED_MODELS
    elif args.models.lower() == "fast":
        models = FAST_MODELS
    elif args.models.lower() == "local":
        models = LOCAL_MODELS
    else:
        models = [m.strip() for m in args.models.split(",") if m.strip()]

    # Check if local models are included and show warning
    local_models_included = any(model.startswith("ollama/") for model in models)
    if local_models_included:
        print("\n⚠️  Local models detected - these require additional setup:")
        print("   • Ollama must be installed and running (ollama serve)")
        print("   • Models must be pulled individually (e.g., ollama pull llama3.3)")
        print("   • Local models may require custom prompts and longer timeouts")
        print("   • Consider using API models for standard benchmarks")

    # Check model availability and filter automatically
    print("\n🔍 Checking model availability...")
    available_models, unavailable_models = check_model_availability(models)

    if unavailable_models:
        print(f"⚠️  Skipping unavailable models: {', '.join(unavailable_models)}")
        setup_instructions = []

        for model in unavailable_models:
            if model.startswith("ollama/"):
                model_name = model.split("/", 1)[1]
                print(f"   - {model}: Model not pulled or Ollama not running")
                setup_instructions.append(f"ollama pull {model_name}")
            elif model.startswith("grok-"):
                print(f"   - {model}: XAI_API_KEY not configured")
                setup_instructions.append("Add XAI_API_KEY to .env file (get key from https://console.x.ai/)")
            elif model.startswith("deepseek-"):
                print(f"   - {model}: DEEPSEEK_API_KEY not configured")
                setup_instructions.append(
                    "Add DEEPSEEK_API_KEY to .env file (get key from https://platform.deepseek.com/)")
            elif model.startswith("llama-"):
                print(f"   - {model}: LLAMA_API_KEY not configured")
                setup_instructions.append("Add LLAMA_API_KEY to .env file")
            elif model.startswith("gpt-"):
                print(f"   - {model}: OPENAI_API_KEY not configured")
                setup_instructions.append(
                    "Add OPENAI_API_KEY to .env file (get key from https://platform.openai.com/api-keys)")
            elif model.startswith("claude-"):
                print(f"   - {model}: ANTHROPIC_API_KEY not configured")
                setup_instructions.append(
                    "Add ANTHROPIC_API_KEY to .env file (get key from https://console.anthropic.com/)")
            elif model.startswith("gemini-"):
                print(f"   - {model}: GEMINI_API_KEY not configured")
                setup_instructions.append(
                    "Add GEMINI_API_KEY to .env file (get key from https://aistudio.google.com/app/apikey)")
            else:
                print(f"   - {model}: No API key configured")

        if setup_instructions:
            print(f"\n💡 To use these models:")
            for instruction in list(set(setup_instructions))[:3]:  # Show max 3 unique instructions
                print(f"   • {instruction}")
            if len(set(setup_instructions)) > 3:
                print("   • See NEW_MODELS_GUIDE.md for complete setup instructions")

    if not available_models:
        print("\n❌ No models are available for testing!")
        print("💡 To fix this:")
        print("   1. Add API keys to your .env file")
        print("   2. Install and start Ollama for local models")
        print("   3. Pull required Ollama models (e.g., 'ollama pull llama3.3')")
        sys.exit(1)

    # Use only available models
    models = available_models
    print(f"✅ Testing available models: {', '.join(models)}")

    suite = load_suite(args.suite)

    if not suite:
        sys.exit(f"❌ No test cases found in suite: {args.suite}")

    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(args.outdir or f"./benchmark_results/enhanced_{timestamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    pricing = parse_pricing_arg(args.pricing)

    print(f"\n🔍 Enhanced Multi-LLM Security Benchmark")
    print(f"Built by the Rapticore Security Research Team")
    print(f"{'=' * 80}")
    print(f"Models: {', '.join(models)}")
    print(f"Suite: {args.suite} ({len(suite)} test cases)")
    print(f"Output: {outdir}")
    print(f"")
    print(f"🎯 Feature Status:")
    print(f"   ✓ Executive reporting: Always enabled")
    print(f"   ✓ Performance analysis: Always enabled")
    print(
        f"   {'✓' if VISUALIZATION_AVAILABLE else '❌'} Visualization charts: {'Enabled' if VISUALIZATION_AVAILABLE else 'Disabled - install matplotlib'}")
    print(f"   📊 Enhanced data capture: Will be checked...")
    print(f"   📈 Enhanced reporting: Will be checked...")
    if args.show_responses:
        print(f"   🔍 Response analysis: Enabled ({args.response_format} format)")
        print(f"       Use --response-format to change: summary|detailed|full")
    print(f"{'=' * 80}")

    # Run benchmark
    all_results = []
    sys_msg_default = "You are an expert security analyst. Provide thorough, accurate security analysis."
    sys_msg_json = "You are an expert security analyst. Respond ONLY with valid JSON."

    if args.concurrent:
        # Concurrent execution for faster benchmarks
        print(f"🚀 Running concurrent benchmarks with max {args.max_workers} workers...")

        # Build list of all tasks
        tasks = []
        for i, test_case in enumerate(suite, 1):
            suite_id = test_case["id"]
            prompt = test_case["prompt"]
            want_json = test_case.get("json", False) or args.json
            sys_msg = sys_msg_json if want_json else sys_msg_default

            for model in models:
                tasks.append((clients, suite_id, model, sys_msg, prompt, args.timeout, want_json, pricing))

        print(f"📊 Total tasks to execute: {len(tasks)} ({len(models)} models × {len(suite)} tests)")

        # Execute tasks concurrently
        completed_tasks = 0
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(run_single_test_concurrent, *task): task
                for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    model, suite_id, result = future.result()
                    completed_tasks += 1

                    # Find the test case for scoring BEFORE displaying progress
                    test_case = None
                    for tc in suite:
                        if tc["id"] == suite_id:
                            test_case = tc
                            break

                    # Initialize variables for all paths
                    criteria_met = []
                    criteria_missed = []
                    violations = []

                    # Process scoring for successful results BEFORE progress display
                    if result.ok and test_case:
                        criteria = test_case.get("criteria", [])
                        must_not = test_case.get("must_not", [])

                        score, criteria_met, criteria_missed, violations = score_text_enhanced(
                            result.text, criteria, must_not
                        )
                        result.score = score
                        result.criteria_met = criteria_met
                        result.criteria_missed = criteria_missed
                        result.must_not_violations = violations

                    # Show progress with correct score
                    print(f"✓ {model:<15} {suite_id:<25} | {completed_tasks}/{len(tasks)} ", end="")
                    if result.ok:
                        print(f"score={result.score:.3f} | {result.elapsed_s:.2f}s")
                    else:
                        print(f"FAILED | {result.elapsed_s:.2f}s")

                        # Enhanced response display for concurrent execution
                        if args.show_responses:
                            display_response_analysis(
                                suite_id, model, result, test_case,
                                criteria_met, criteria_missed, violations,
                                args.response_format
                            )

                    all_results.append(result)

                except Exception as e:
                    print(f"❌ Task execution error: {e}")
                    completed_tasks += 1
    else:
        # Sequential execution (original logic)
        for i, test_case in enumerate(suite, 1):
            suite_id = test_case["id"]
            prompt = test_case["prompt"]
            want_json = test_case.get("json", False) or args.json
            sys_msg = sys_msg_json if want_json else sys_msg_default

            print(f"\n[{i}/{len(suite)}] {suite_id}")
            print("-" * 50)

            for model in models:
                print(f"→ {model:<20} ", end="", flush=True)

                result = run_enhanced_model(
                    clients, suite_id, model, sys_msg, prompt,
                    args.timeout, want_json, pricing
                )

                # Initialize variables for all paths
                criteria_met = []
                criteria_missed = []
                violations = []

                if result.ok:
                    criteria = test_case.get("criteria", [])
                    must_not = test_case.get("must_not", [])

                    score, criteria_met, criteria_missed, violations = score_text_enhanced(
                        result.text, criteria, must_not
                    )
                    result.score = score
                    result.criteria_met = criteria_met
                    result.criteria_missed = criteria_missed
                    result.must_not_violations = violations

                    if args.show_responses:
                        display_response_analysis(
                            suite_id, model, result, test_case,
                            criteria_met, criteria_missed, violations,
                            args.response_format
                        )

                status = "✓" if result.ok else "✗"
                print(f"{status} {result.score:.3f} | {result.elapsed_s:.2f}s | ${result.cost_usd:.5f}"
                      if result.cost_usd else f"{status} {result.score:.3f} | {result.elapsed_s:.2f}s")

                all_results.append(result)

    # Generate reports (always enabled)
    print_enhanced_summary(all_results, models)

    print(f"\n📊 Generating executive reports and analysis...")

    # Generate performance charts
    print(f"📊 Generating performance charts...")
    try:
        charts = generate_performance_charts(all_results, models, outdir)
        if charts is None:
            charts = {}  # Ensure charts is always a dictionary
        if charts:
            print(f"✓ Generated {len(charts)} performance charts")
            for chart_name, chart_path in charts.items():
                print(f"   - {chart_name}: {Path(chart_path).name}")

            # Also generate text summary as additional analysis when charts are available
            print("📊 Generating additional text-based performance analysis...")
            generate_text_performance_summary(all_results, models, outdir)

        else:
            if not VISUALIZATION_AVAILABLE:
                print("⚠️  Visual charts unavailable: Missing visualization libraries")
                print("   Install with: pip install matplotlib seaborn pandas numpy")
                print("   Generating text-based performance summary instead...")
                generate_text_performance_summary(all_results, models, outdir)
            else:
                print("⚠️  No visual charts generated (insufficient data)")
                print("   Generating text-based performance summary...")
                generate_text_performance_summary(all_results, models, outdir)
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        charts = {}

    # Generate improved charts to fix empty chart issues
    if IMPROVED_CHARTS_AVAILABLE:
        print(f"📈 Generating improved charts to address visualization issues...")
        try:
            improved_charts = integrate_improved_charts(all_results, models, outdir)
            if improved_charts:  # Safety check for None
                charts.update(improved_charts)  # Add to existing charts
            if improved_charts:
                print(f"✓ Generated {len(improved_charts)} improved charts")
                for chart_name, chart_path in improved_charts.items():
                    print(f"   - {chart_name}: {Path(chart_path).name}")
        except Exception as e:
            print(f"❌ Improved chart generation failed: {e}")

    # Enhanced data capture integration
    try:
        from data_capture import EnhancedDataCapture

        # Initialize data capture system
        data_capture = EnhancedDataCapture(outdir.parent, session_id=f"benchmark_{outdir.name.split('_')[-1]}")
        print(f"✅ Enhanced data capture: ENABLED")
        print(f"   Session ID: {data_capture.session_id}")
        print(f"   Raw data exports: JSON, CSV, Pickle, Compressed")

        ENHANCED_CAPTURE_AVAILABLE = True
        print(f"✅ Enhanced reporting: ENABLED")
        print(f"   Advanced cost-effectiveness calculations")
        print(f"   Language and OWASP category analysis")
        print(f"   Multi-format exports (CSV, JSON, Markdown)")

    except ImportError as e:
        print(f"❌ Enhanced reporting/capture modules not available!")
        print(f"   Missing dependencies: {e}")
        print(f"   Install with: pip install -r requirements.txt")
        print(f"   Running with basic reporting only...")
        enhanced_metrics = {}
        ENHANCED_CAPTURE_AVAILABLE = False

    if 'enhanced_metrics' not in locals():
        enhanced_metrics = {}

    if ENHANCED_CAPTURE_AVAILABLE and EXECUTIVE_SUMMARY_AVAILABLE:
        # Initialize enhanced unified reporter
        reporter = EnhancedUnifiedReporter()
        
        # Calculate enhanced metrics for all models using available functions
        for model in models:
            model_results = [r for r in all_results if r.model == model]
            if model_results:
                # Calculate basic enhanced metrics
                perf = ModelPerformance.from_results(model, model_results)
                enhanced_metrics[model] = {
                    'total_tests': perf.total_tests,
                    'successful_tests': perf.successful_tests,
                    'avg_score': perf.avg_score,
                    'total_cost': perf.total_cost,
                    'cost_per_test': perf.cost_per_test
                }

        # Language and OWASP analysis using the reporter
        try:
            language_results = reporter.analyze_by_language(all_results)
            owasp_results = reporter.analyze_by_owasp_category(all_results)
            print(f"✓ Language analysis: {len(language_results)} languages")
            print(f"✓ OWASP analysis: {len(owasp_results)} categories")
        except Exception as e:
            print(f"⚠️ Language/OWASP analysis failed: {e}")
            language_results = {}
            owasp_results = {}

        # Generate additional charts if available
        lang_chart = None
        owasp_chart = None
        if IMPROVED_CHARTS_AVAILABLE and charts is not None:
            try:
                # Generate language effectiveness chart
                lang_chart = generate_language_effectiveness_chart_from_dict(language_results, outdir)
                if lang_chart:
                    charts['language_effectiveness'] = lang_chart
            except Exception as e:
                print(f"⚠️ Language chart generation failed: {e}")
            
            try:
                # Generate OWASP effectiveness chart
                owasp_chart = generate_owasp_effectiveness_chart(owasp_results, outdir)
                if owasp_chart:
                    charts['owasp_effectiveness'] = owasp_chart
            except Exception as e:
                print(f"⚠️ OWASP chart generation failed: {e}")

        # Export to CSV and JSON using the reporter
        try:
            # Create ModelPerformance objects for each model
            performance_by_model = {}
            for model in models:
                model_results = [r for r in all_results if r.model == model]
                if model_results:
                    performance_by_model[model] = ModelPerformance.from_results(model, model_results)
            
            csv_path = reporter.export_to_csv(all_results, models, performance_by_model, outdir)
            json_path = reporter.export_to_json(all_results, models, performance_by_model, language_results, owasp_results, outdir)
            print(f"✓ Enhanced CSV export: {Path(csv_path).name}")
            print(f"✓ Enhanced JSON analysis: {Path(json_path).name}")
        except Exception as e:
            print(f"⚠️ CSV/JSON export failed: {e}")
            import traceback
            traceback.print_exc()

        print(f"✓ Enhanced metrics calculated for {len(enhanced_metrics)} models")

        if VISUALIZATION_AVAILABLE:
            additional_charts = 0
            if lang_chart:
                additional_charts += 1
                print(f"✓ Language effectiveness chart: {Path(lang_chart).name}")
            if owasp_chart:
                additional_charts += 1
                print(f"✓ OWASP effectiveness chart: {Path(owasp_chart).name}")
            if additional_charts:
                print(f"✓ Generated {additional_charts} additional analysis charts")

        # Enhanced raw data capture and export
        if ENHANCED_CAPTURE_AVAILABLE:
            print(f"📊 Exporting comprehensive raw data for future analysis...")

            # Capture all test results for comprehensive analysis
            for result in all_results:
                # Create comprehensive test case info
                test_case_info = {
                    'id': result.suite_id,  # Use suite_id as the test identifier
                    'suite': result.suite_id,
                    'category': 'security',
                    'vulnerability_type': 'unknown',  # Could be enhanced with test suite parsing
                    'prompt': f"Test case: {result.suite_id}",
                    # Descriptive placeholder since original prompt not stored
                    'criteria': (getattr(result, 'criteria_met', None) or []) + (
                                getattr(result, 'criteria_missed', None) or []),
                    'must_not': getattr(result, 'must_not_violations', None) or [],
                    'points': 1.0,
                    'tags': []
                }

                # Create request details
                request_details = {
                    'final_prompt': f"Security test: {result.suite_id}",  # Placeholder since original prompt not stored
                    'endpoint': 'api_endpoint',
                    'method': 'POST',
                    'headers': {},
                    'body': {'prompt': f"Security test: {result.suite_id}"},
                    'sent_at': datetime.now().isoformat(),  # Use current time as placeholder
                    'start_time': datetime.now().isoformat(),
                    'retry_count': 0
                }

                # Create response data
                response_data = {
                    'status_code': 200 if result.ok else 500,
                    'headers': {},
                    'body': {'text': result.text},
                    'text': result.text,
                    'received_at': datetime.now().isoformat(),  # Use current time as placeholder
                    'end_time': datetime.now().isoformat(),
                    'latency_ms': result.elapsed_s * 1000 if hasattr(result, 'elapsed_s') else 0,
                    'input_tokens': result.input_tokens or 0,
                    'output_tokens': result.output_tokens or 0,
                    'total_tokens': (result.input_tokens or 0) + (result.output_tokens or 0),
                    'cost_usd': result.cost_usd or 0.0,
                    'elapsed_ms': result.elapsed_s * 1000 if hasattr(result, 'elapsed_s') else 0
                }

                # Create analysis results
                analysis_results = {
                    'score': result.score,
                    'raw_score': result.score,
                    'weighted_score': result.score,
                    'success': result.ok,
                    'criteria_matches': getattr(result, 'criteria_met', []),
                    'criteria_missed': getattr(result, 'criteria_missed', []),
                    'must_not_violations': getattr(result, 'must_not_violations', []),
                    'warnings': [],
                    'total_tests': len(all_results)
                }

                # Capture the enhanced result
                data_capture.capture_test_result(
                    test_case_info=test_case_info,
                    model_name=result.model,
                    request_details=request_details,
                    response_data=response_data,
                    analysis_results=analysis_results
                )

            # Export all captured data
            exported_files = data_capture.export_raw_data()

            print(f"✓ Raw data exported in {len(exported_files)} formats:")
            for format_name, file_path in exported_files.items():
                print(f"  - {format_name}: {Path(file_path).name}")

            print(f"📁 Raw data directory: {data_capture.session_dir}")

        else:
            print("⚠ Enhanced data capture not available - install psutil for comprehensive data capture")

    # Generate executive summary
    print(f"📋 Generating executive summary...")
    try:
        if EXECUTIVE_SUMMARY_AVAILABLE:
            # Calculate total cost
            total_cost = sum(r.cost_usd for r in all_results if r.cost_usd is not None)

            # Generate enhanced unified executive summary
            summary_path = generate_enhanced_unified_executive_summary(
                results=all_results,
                models=models,
                suite_name=args.suite,
                outdir=outdir,
                charts=charts,
                enhanced_metrics=enhanced_metrics,
                total_cost=total_cost
            )
            print(f"✓ Executive summary: {summary_path}")
        else:
            print(f"⚠️ Executive summary not available")
    except Exception as e:
        print(f"❌ Executive summary generation failed: {e}")
        import traceback
        traceback.print_exc()

    # Generate technical report
    print(f"📋 Generating technical report...")
    try:
        if TECHNICAL_REPORTER_AVAILABLE:
            # Calculate total cost
            total_cost = sum(r.cost_usd for r in all_results if r.cost_usd is not None)

            # Generate engineering technical report
            technical_path = generate_engineering_technical_report(
                results=all_results,
                models=models,
                suite_name=args.suite,
                outdir=outdir,
                total_cost=total_cost
            )
            print(f"✓ Technical report: {technical_path}")
        else:
            print(f"⚠️ Technical reporter not available")
    except Exception as e:
        print(f"❌ Technical report generation failed: {e}")
        import traceback
        traceback.print_exc()



    # Generate performance analysis (always enabled)
    print(f"📈 Generating performance analysis...")
    try:
        generate_performance_analysis(all_results, models, outdir)
        print(f"✓ Performance analysis: {outdir}/performance_analysis.json")
    except Exception as e:
        print(f"❌ Performance analysis generation failed: {e}")

    # Save JSON output if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "models": models,
                "suite": args.suite,
                "results": [asdict(r) for r in all_results],
                "summary": {
                    "total_tests": len(all_results),
                    "models_tested": len(models),
                    "pass_rate": sum(1 for r in all_results if r.score > 0.5) / len(all_results) if all_results else 0,
                    "average_score": sum(r.score for r in all_results) / len(all_results) if all_results else 0,
                    "total_cost": sum(r.cost_usd for r in all_results if r.cost_usd) if any(
                        r.cost_usd for r in all_results) else 0
                }
            }, f, indent=2)
        print(f"✓ JSON output: {output_path}")

    print(f"\n📊 Generated Reports & Analysis:")
    print(f"   📋 Executive summary: {outdir}/enhanced_executive_summary.md")
    print(f"   🔧 Technical report: {outdir}/technical_analysis_report.md")
    print(f"   📈 Performance analysis: {outdir}/performance_analysis.json")
    print(f"   📄 Detailed results: {outdir}/enhanced_benchmark_results.json")

    if charts:
        print(f"   🎯 Visualization charts: {len(charts)} files")
        for chart_name, chart_path in charts.items():
            print(f"      - {Path(chart_path).name}")

    if ENHANCED_CAPTURE_AVAILABLE:
        print(f"   💾 Raw data exports: Multiple formats for advanced analysis")
        print(f"   📊 Enhanced CSV/JSON reports with cost-effectiveness analysis")
        print(f"   📈 Language and OWASP category breakdowns")

    # Generate QFS audit-compliant reports if available
    if QFS_AUDIT_AVAILABLE:
        print(f"\n🔍 Generating QFS audit-compliant analysis...")
        try:
            # Generate changelog
            changelog = generate_changelog()
            changelog_path = outdir / "qfs_audit_changelog.md"
            with open(changelog_path, 'w') as f:
                f.write(changelog)

            print(f"✅ QFS audit reports generated:")
            print(f"   🔧 Audit Changelog: {changelog_path.name}")
            print(f"   📊 Methodologically consistent QFS calculations applied")
            print(f"   📈 Quality-first ranking (accuracy → completeness → coverage)")
            print(f"   💰 Cost as secondary factor (light penalty, never dominates)")

        except Exception as e:
            print(f"⚠️  QFS audit report generation failed: {e}")

    print(f"\n🎉 Comprehensive benchmark complete!")
    print(f"📁 All results saved to: {outdir}")
    print(f"💡 For advanced analysis, see the raw data exports and CSV files")
    if QFS_AUDIT_AVAILABLE:
        print(f"🔍 Quality-First Score methodology applied - prioritizing accuracy over cost")


if __name__ == "__main__":
    main()
