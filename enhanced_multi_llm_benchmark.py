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

import os
import sys
import re
import time
import json
import csv
import argparse
import statistics
from dataclasses import dataclass, asdict
from typing import Optional, Any, Tuple, List, Dict
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

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
PREMIUM_MODELS = ["gpt-5", "claude-opus-4", "gemini-2.5-flash"]
BALANCED_MODELS = ["gpt-4o", "claude-sonnet-4", "gemini-2.0-flash"]
FAST_MODELS = ["gpt-5-mini", "gpt-4o-mini", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
ALL_MODELS = PREMIUM_MODELS + BALANCED_MODELS + FAST_MODELS

DEFAULT_MODELS = [
    "gpt-5", "claude-opus-4", "gemini-2.5-flash",
    "claude-sonnet-4", "gpt-4o", "gemini-2.0-flash"
]

DEFAULT_TIMEOUT_S = 30
FIRST_SHOT_TOKENS = 512
RETRY_SHOT_TOKENS = 768
STARVED_RATIO = 0.70

# Enhanced model pricing (per 1M tokens)
DEFAULT_PRICING = {
    "gpt-5": {"in": 3.0, "out": 15.0},
    "gpt-5-mini": {"in": 1.0, "out": 4.0},
    "gpt-4o": {"in": 2.5, "out": 10.0},
    "gpt-4o-mini": {"in": 0.15, "out": 0.6},
    "claude-opus-4": {"in": 15.0, "out": 75.0},
    "claude-sonnet-4": {"in": 3.0, "out": 15.0},
    "gemini-2.5-flash": {"in": 0.075, "out": 0.3},
    "gemini-2.5-flash-lite": {"in": 0.0375, "out": 0.15},
    "gemini-2.0-flash": {"in": 0.075, "out": 0.3},
    "gemini-2.0-flash-lite": {"in": 0.0375, "out": 0.15}
}

# Test suite definitions
DEFAULT_SUITE_FILES = {
    "basic": "test_suites/security_basic.yaml",
    "comprehensive": "test_suites/security_comprehensive.yaml",
    "owasp": "test_suites/owasp_top10.yaml",
    "python": "test_suites/security_python.yaml",
    "javascript": "test_suites/security_javascript.yaml",
    "go": "test_suites/security_go.yaml",
    "rust": "test_suites/security_rust.yaml",
    "java": "test_suites/security_java.yaml",
    "c": "test_suites/security_c.yaml",
    "cpp": "test_suites/security_cpp.yaml",
    "csharp": "test_suites/security_csharp.yaml",
    "php": "test_suites/security_php.yaml",
    "ruby": "test_suites/security_ruby.yaml",
    "haskell": "test_suites/security_haskell.yaml",

    # Combinations
    "all": ["basic", "comprehensive", "owasp", "python", "javascript", "go", "rust", "java", "c", "cpp", "csharp", "php", "ruby", "haskell"],
    "enterprise": ["comprehensive", "java", "csharp", "python"],
    "web_dev": ["javascript", "python", "php", "java"],
    "systems": ["c", "cpp", "rust", "go"],
    "all_languages": ["python", "javascript", "go", "rust", "java", "c", "cpp", "csharp", "php", "ruby", "haskell"]
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
                total_input_tokens=0, total_output_tokens=0, avg_input_tokens_per_test=0.0, avg_output_tokens_per_test=0.0
            )

        # Use all scores (including 0 for failures) for fair comparison
        avg_score = statistics.mean(all_scores) if all_scores else 0.0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
        total_cost = sum(costs)
        cost_per_test = total_cost / total_tests if total_tests > 0 else 0.0  # Cost per ALL tests attempted

        perfect_scores = sum(1 for r in successful if r.perfect_score)
        good_scores = sum(1 for r in successful if r.response_quality in ["excellent", "good"])
        poor_scores = sum(1 for r in successful if r.response_quality == "poor")

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
# def run_gemini(
#     suite_id: str,
#     model: str,
#     sys_msg: str,
#     prompt: str,
#     timeout: float,
#     json_mode: bool,
#     pricing: Dict[str, Dict[str, float]]
# ) -> EnhancedRunResult:
#     """Run Google Gemini models."""
#     if not GOOGLE_AVAILABLE:
#         return EnhancedRunResult(
#             suite_id=suite_id, model=model, path="Gemini", ok=False,
#             elapsed_s=0.0, error="Google Generative AI library not available"
#         )
#
#     t0 = time.time()
#     try:
#         # Map model names to API models
#         model_mapping = {
#             "gemini-2.5-flash": "gemini-2.5-flash",
#             "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
#             "gemini-2.0-flash": "gemini-2.0-flash",
#             "gemini-2.0-flash-lite": "gemini-2.0-flash-lite"
#         }
#
#         api_model = model_mapping.get(model, "gemini-2.5-flash")
#         gemini_model = genai.GenerativeModel(api_model)
#
#         full_prompt = f"{sys_msg}\n\n{prompt}"
#         if json_mode:
#             full_prompt += "\n\nPlease respond in valid JSON format only."
#
#         # Configure generation settings to disable thinking for all models
#         generation_config = genai.types.GenerationConfig(
#             max_output_tokens=FIRST_SHOT_TOKENS,
#             temperature=0.0 if json_mode else 0.2,
#         )
#
#         # Add explicit instruction to prevent thinking mode for all Gemini models
#         full_prompt = f"Provide a direct, concise security analysis. Do not show reasoning steps or thinking process.\n\n{full_prompt}"
#
#         response = gemini_model.generate_content(
#             full_prompt,
#             generation_config=generation_config
#         )
#
#         # Extract text from response with better error handling
#         text = ""
#         if hasattr(response, 'candidates') and response.candidates:
#             candidate = response.candidates[0]
#             # Check if content was blocked
#             if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
#                 finish_reason = str(candidate.finish_reason)
#                 if finish_reason in ['SAFETY', 'RECITATION', 'OTHER']:
#                     print(f"DEBUG: Gemini {model} content blocked - reason: {finish_reason}")
#                     text = f"[Content blocked: {finish_reason}]"
#             elif hasattr(candidate, 'content') and candidate.content:
#                 if hasattr(candidate.content, 'parts') and candidate.content.parts:
#                     text = candidate.content.parts[0].text.strip()
#
#         # Fallback to direct text attribute
#         if not text and hasattr(response, 'text') and response.text:
#             text = response.text.strip()
#
#         # Debug logging for empty responses
#         if not text:
#             print(f"DEBUG: Gemini {model} returned empty response")
#             print(f"DEBUG: Response object: {type(response)}")
#             if hasattr(response, 'candidates') and response.candidates:
#                 candidate = response.candidates[0]
#                 print(f"DEBUG: Candidate finish_reason: {getattr(candidate, 'finish_reason', 'None')}")
#                 print(f"DEBUG: Candidate content: {getattr(candidate, 'content', 'None')}")
#                 if hasattr(candidate, 'content') and candidate.content:
#                     print(f"DEBUG: Content parts: {getattr(candidate.content, 'parts', 'None')}")
#
#         # Estimate token usage (Gemini doesn't provide detailed usage info)
#         input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
#         output_tokens = len(text.split()) * 1.3
#         total_tokens = input_tokens + output_tokens
#
#         cost_usd = estimate_cost(model, int(input_tokens), int(output_tokens), pricing)
#
#         if text:
#             return EnhancedRunResult(
#                 suite_id=suite_id, model=model, path="Gemini", ok=True,
#                 elapsed_s=time.time() - t0, text=text,
#                 input_tokens=int(input_tokens), output_tokens=int(output_tokens),
#                 total_tokens=int(total_tokens), cost_usd=cost_usd
#             )
#         else:
#             return EnhancedRunResult(
#                 suite_id=suite_id, model=model, path="Gemini", ok=False,
#                 elapsed_s=time.time() - t0, error="Empty response"
#             )
#
#     except Exception as e:
#         return EnhancedRunResult(
#             suite_id=suite_id, model=model, path="Gemini", ok=False,
#             elapsed_s=time.time() - t0, error=str(e)
#         )

#----------------------------------------- working improved --------------


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
def generate_executive_summary(
    results: List[EnhancedRunResult],
    models: List[str],
    suite_name: str,
    outdir: Path,
    charts: Optional[Dict[str, str]] = None,
    enhanced_metrics: Optional[Dict] = None
) -> None:
    """Generate executive summary report for business stakeholders."""

    # Analyze performance by model
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)

    if not performance_by_model:
        return

    # Find best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)
    most_reliable = min(performance_by_model.values(), key=lambda p: p.score_std_dev)

    # Calculate test statistics
    total_tests = len(results) // len(models) if models else 0

    # Build enhanced metrics section if available
    enhanced_section = ""
    if enhanced_metrics:
        # Find best performers using enhanced metrics
        best_weighted = max(enhanced_metrics.items(), key=lambda x: x[1].weighted_effectiveness)
        best_penalty_adjusted = max(enhanced_metrics.items(), key=lambda x: x[1].penalty_adjusted_effectiveness)
        most_perfect = max(enhanced_metrics.items(), key=lambda x: x[1].perfect_scores)

        enhanced_section = f"""
### 🔍 Enhanced Cost-Effectiveness Analysis

#### Quality-Weighted Performance: {best_weighted[0]}
- **Quality-Weighted Effectiveness:** {best_weighted[1].weighted_effectiveness:.1f} points/$
- **Perfect Scores:** {best_weighted[1].perfect_scores}
- **Score Distribution:** P:{best_weighted[1].perfect_scores} | E:{best_weighted[1].excellent_scores} | G:{best_weighted[1].good_scores} | F:{best_weighted[1].fair_scores} | Poor:{best_weighted[1].poor_scores}

#### Penalty-Adjusted Performance: {best_penalty_adjusted[0]}
- **Penalty-Adjusted Effectiveness:** {best_penalty_adjusted[1].penalty_adjusted_effectiveness:.1f} points/$
- **Wrong Answer Penalty Impact:** {best_penalty_adjusted[1].wrong_answer_penalty:.1%}
- **Failed Tests:** {best_penalty_adjusted[1].failed_tests}

#### Most Accurate Performer: {most_perfect[0]}
- **Perfect Scores:** {most_perfect[1].perfect_scores} / {most_perfect[1].total_tests}
- **Cost per Perfect Answer:** ${most_perfect[1].cost_per_correct_answer:.5f}
- **Partial Credit Value:** {most_perfect[1].partial_credit_value:.2f}

*Enhanced metrics consider partial correctness, apply quality weighting, and penalize wrong/missed answers.*
"""

    # Build chart section
    chart_section = ""
    if charts:
        if "performance_comparison" in charts:
            chart_section += f"- **Performance Comparison Chart:** `{Path(charts['performance_comparison']).name}` - Scatter plot showing security score vs response time with cost indicators\n"
        if "cost_effectiveness" in charts:
            chart_section += f"- **Cost Effectiveness Chart:** `{Path(charts['cost_effectiveness']).name}` - Quality-weighted cost effectiveness (penalizes inaccurate and unreliable models)\n"
        if "token_usage" in charts:
            chart_section += f"- **Token Usage Analysis:** `{Path(charts['token_usage']).name}` - Input and output token consumption by model\n"
        if "performance_comparison_bars" in charts:
            chart_section += f"- **Multi-Model Comparison Chart:** `{Path(charts['performance_comparison_bars']).name}` - Side-by-side performance metrics comparison\n"
        if "performance_breakdown" in charts:
            chart_section += f"- **Performance Breakdown Chart:** `{Path(charts['performance_breakdown']).name}` - Detailed metrics analysis for single model\n"
        if "language_effectiveness" in charts:
            chart_section += f"- **Language Effectiveness Chart:** `{Path(charts['language_effectiveness']).name}` - Performance comparison across programming languages\n"
        if "owasp_effectiveness" in charts:
            chart_section += f"- **OWASP Category Chart:** `{Path(charts['owasp_effectiveness']).name}` - Effectiveness against OWASP Top 10 categories\n"
    else:
        chart_section = "*Charts not available - install matplotlib and seaborn for visual analysis*"

    # Calculate total costs for summary
    total_cost_all = sum(r.cost_usd for r in results if r.cost_usd)
    avg_cost_per_test = total_cost_all / len(results) if results else 0

    # Build complete executive summary
    summary = f"""# 🛡️ LLM Security Benchmark Executive Summary

**Suite:** {suite_name} | **Models Tested:** {len(models)} | **Total Security Tests:** {total_tests}
**Analysis Date:** {datetime.now().strftime("%B %d, %Y")}

## 💰 Cost Overview

**⚠️ COST NOTICE:** This benchmark uses paid API services and incurred costs.

- **Total Cost This Run:** ${total_cost_all:.4f}
- **Average Cost per Test:** ${avg_cost_per_test:.6f}
- **Total API Calls:** {len(results):,}

*Premium models (Claude Opus 4, GPT-5) cost significantly more than budget models (Gemini Flash, GPT-4o-mini)*

## 🎯 Executive Overview

This comprehensive security assessment evaluated {len(models)} leading AI models across {total_tests} security scenarios, analyzing their capability to identify vulnerabilities, provide appropriate recommendations, and demonstrate security knowledge alignment with industry standards.

### Key Security Findings

🏆 **Highest Security Accuracy:** {best_accuracy.model_name} achieved {best_accuracy.avg_score:.1%} detection rate
💰 **Best Value (Quality-Aware):** {best_value.model_name} delivers {best_value.cost_effectiveness:.1f} quality-weighted points per dollar
⚡ **Fastest Response Time:** {fastest.model_name} averages {fastest.avg_response_time:.2f}s per analysis
🎯 **Most Consistent Performance:** {most_reliable.model_name} shows {most_reliable.score_std_dev:.3f} variance in scoring

## 📊 Strategic Model Analysis

### Premium Security Models (Highest Accuracy):
{best_accuracy.model_name}
- **Security Detection Rate:** {best_accuracy.avg_score:.3f}/1.0 ({best_accuracy.avg_score:.1%})
- **Reliability:** {best_accuracy.success_rate:.1%} success rate
- **Response Time:** {best_accuracy.avg_response_time:.2f}s average
- **Cost Efficiency:** ${best_accuracy.cost_per_test:.5f} per analysis
- **Perfect Assessments:** {best_accuracy.perfect_scores}/{best_accuracy.total_tests}

### Most Cost-Effective: {best_value.model_name}
- **Value Score:** {best_value.cost_effectiveness:.1f} security points per dollar
  - *Formula: average_score ÷ cost_per_test*
  - *Higher values indicate better cost-effectiveness for security analysis*
- **Detection Accuracy:** {best_value.avg_score:.3f}/1.0
- **Operational Cost:** ${best_value.cost_per_test:.5f} per test
- **Success Rate:** {best_value.success_rate:.1%}

### Fastest Response: {fastest.model_name}
- **Average Response Time:** {fastest.avg_response_time:.2f}s
- **Security Accuracy:** {fastest.avg_score:.3f}/1.0
- **Speed Score:** {fastest.speed_score:.3f}

### Most Consistent: {most_reliable.model_name}
- **Score Consistency:** {most_reliable.score_std_dev:.3f} standard deviation
- **Average Detection:** {most_reliable.avg_score:.3f}/1.0
- **Reliability:** {most_reliable.success_rate:.1%}

{enhanced_section}

## 📊 Performance Visualizations

The following charts provide visual insights into model performance and comparisons:

{chart_section}

---

*This analysis is based on {len(results)} security test executions across {len(models)} leading LLM models. Built by the Rapticore Security Research Team for comprehensive security program optimization.*

*For detailed technical metrics and raw performance data, see `performance_analysis.json`*"""

    # Write executive summary
    with open(outdir / "executive_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)

def generate_basic_executive_summary(
    results: List[EnhancedRunResult],
    models: List[str], 
    suite_name: str,
    outdir: Path
) -> None:
    """Generate basic executive summary when enhanced features aren't available."""
    
    # Calculate basic performance metrics
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)
    
    if not performance_by_model:
        return
    
    # Find best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)
    
    # Calculate totals
    total_tests = len(results) // len(models) if models else 0
    total_cost = sum(r.cost_usd for r in results if r.cost_usd)
    avg_cost_per_test = total_cost / len(results) if results else 0
    
    # Generate basic summary
    summary = f"""# 🛡️ LLM Security Benchmark - Basic Summary

**Suite:** {suite_name} | **Models Tested:** {len(models)} | **Total Tests:** {total_tests}
**Analysis Date:** {datetime.now().strftime("%B %d, %Y")}

## 💰 Cost Overview

- **Total Cost This Run:** ${total_cost:.4f}
- **Average Cost per Test:** ${avg_cost_per_test:.6f}
- **Total API Calls:** {len(results):,}

## 🏆 Top Performers

**🎯 Most Accurate:** {best_accuracy.model_name}
- Average Security Score: {best_accuracy.avg_score:.1%}
- Success Rate: {best_accuracy.success_rate:.1%}
- Total Cost: ${best_accuracy.total_cost:.4f}

**💰 Best Cost-Effectiveness:** {best_value.model_name}
- Cost-Effectiveness Score: {best_value.cost_effectiveness:.1f} points per dollar
- Average Score: {best_value.avg_score:.3f}
- Cost per Test: ${best_value.cost_per_test:.5f}

**⚡ Fastest Response:** {fastest.model_name}
- Average Response Time: {fastest.avg_response_time:.2f} seconds
- Speed Score: {fastest.speed_score:.2f}

## 📊 Model Comparison

| Model | Tests | Success Rate | Avg Score | Response Time | Total Cost | Cost/Test |
|-------|--------|-------------|-----------|---------------|------------|-----------|"""

    for model, perf in performance_by_model.items():
        summary += f"\n| {model} | {perf.total_tests} | {perf.success_rate:.1%} | {perf.avg_score:.3f} | {perf.avg_response_time:.2f}s | ${perf.total_cost:.4f} | ${perf.cost_per_test:.5f} |"

    summary += f"""

## 📋 Summary

This security assessment evaluated {len(models)} AI models across {total_tests} security test scenarios. 

**Key Findings:**
- Highest accuracy: {best_accuracy.avg_score:.1%} by {best_accuracy.model_name}
- Best value: {best_value.cost_effectiveness:.1f} points/$ by {best_value.model_name}
- Total investment: ${total_cost:.4f}

**Note:** This is a basic summary. For enhanced analysis with visualizations and detailed cost-effectiveness metrics, install the complete requirements:
```bash
pip install -r requirements.txt
```

---

*Built by the Rapticore Security Research Team*
"""
    
    # Write basic executive summary
    with open(outdir / "basic_executive_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)

def analyze_vulnerability_categories(results: List[EnhancedRunResult], models: List[str]) -> Dict[str, Dict[str, float]]:
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
    COMPLIANCE_PENALTY = 100000 # Cost of compliance failure

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

    scatter = ax.scatter(times, scores, s=[c*100 for c in costs], alpha=0.7, c=range(len(models_list)), cmap='viridis')

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
        ax.text(bar.get_x() + bar.get_width()/2., height + max(effectiveness)*0.01,
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
                min(100 * (perf.cost_effectiveness / max(p.cost_effectiveness for p in performance_by_model.values())), 100) if performance_by_model else 0  # Relative to best model
            ]

            bars = ax.bar(x + (i - len(models_list)/2 + 0.5) * width, values,
                         width, label=model, color=colors[i], alpha=0.8)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
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
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
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

    return charts_created

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
    print(f"\n{'='*80}")
    print(f"📊 ENHANCED SECURITY BENCHMARK SUMMARY")
    print(f"{'='*80}")

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
    print(f"\n{'Model':<20} {'Tests':<8} {'Success':<9} {'Avg Score':<10} {'Time(s)':<8} {'Total Cost':<12} {'In/Out Tokens':<15} {'Quality':<8}")
    print("-" * 110)

    # Model performance
    for model, perf in performance_by_model.items():
        quality_dist = f"{perf.good_scores}/{perf.total_tests}"
        token_info = f"{perf.total_input_tokens:>5}/{perf.total_output_tokens:<5}"
        print(f"{model:<20} {perf.successful_tests:>3}/{perf.total_tests:<3} "
              f"{perf.success_rate:>6.1%} {perf.avg_score:>9.3f} "
              f"{perf.avg_response_time:>7.2f} ${perf.total_cost:>10.4f} "
              f"{token_info:>14} {quality_dist:>7}")

    # Best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)

    # Calculate total costs across all models
    total_cost_all = sum(perf.total_cost for perf in performance_by_model.values())
    total_tests_all = sum(len([r for r in results if r.model == model]) for model in models)

    print(f"\n{'='*80}")
    print(f"🏆 Best Accuracy: {best_accuracy.model_name} (Score: {best_accuracy.avg_score:.3f})")
    print(f"💰 Best Value: {best_value.model_name} (Quality-Aware CE: {best_value.cost_effectiveness:.1f})")
    print(f"⚡ Fastest: {fastest.model_name} (Time: {fastest.avg_response_time:.2f}s)")
    print(f"{'='*80}")
    print(f"")
    print(f"💰 TOTAL COST THIS RUN: ${total_cost_all:.4f}")
    print(f"📊 Total Tests Executed: {total_tests_all:,}")
    print(f"📈 Average Cost per Test: ${total_cost_all/total_tests_all:.6f}")
    print(f"")
    print(f"⚠️  NOTE: This benchmark uses paid API services")
    print(f"{'='*80}")

# ------------------------ Main Enhanced Benchmark Function -------------------------
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

    parser.add_argument("--models", type=str, default=",".join(DEFAULT_MODELS[:4]),
                        help="Model selection: 'all', 'premium', 'balanced', 'fast', or comma-separated model names")
    parser.add_argument("--suite", type=str, default="basic",
                        help="Test suite: 'all', 'basic', 'comprehensive', 'owasp', language names, or path to suite file")
    parser.add_argument("--json", action="store_true",
                        help="Enforce JSON-only outputs")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S,
                        help="Per-call timeout in seconds")
    parser.add_argument("--outdir", type=str, default=None,
                        help="Output directory")
    parser.add_argument("--pricing", type=str, default=None,
                        help="Custom pricing override")
    parser.add_argument("--show-responses", action="store_true",
                        help="Show full response text in console")
    parser.add_argument("--executive-report", action="store_true", default=True,
                        help="Generate executive summary report (always enabled)")
    parser.add_argument("--performance-analysis", action="store_true", default=True,
                        help="Enable detailed performance analysis (always enabled)")
    parser.add_argument("--output", type=str, default=None,
                        help="JSON output file path")

    args = parser.parse_args()

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

    if not clients:
        sys.exit("❌ No API keys found. Check your .env file.")

    # Parse model selection
    if args.models.lower() == "all":
        models = ALL_MODELS
    elif args.models.lower() == "premium":
        models = PREMIUM_MODELS
    elif args.models.lower() == "balanced":
        models = BALANCED_MODELS
    elif args.models.lower() == "fast":
        models = FAST_MODELS
    else:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
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
    print(f"{'='*80}")
    print(f"Models: {', '.join(models)}")
    print(f"Suite: {args.suite} ({len(suite)} test cases)")
    print(f"Output: {outdir}")
    print(f"")
    print(f"🎯 Feature Status:")
    print(f"   ✓ Executive reporting: Always enabled")
    print(f"   ✓ Performance analysis: Always enabled") 
    print(f"   {'✓' if VISUALIZATION_AVAILABLE else '❌'} Visualization charts: {'Enabled' if VISUALIZATION_AVAILABLE else 'Disabled - install matplotlib'}")
    print(f"   📊 Enhanced data capture: Will be checked...")
    print(f"   📈 Enhanced reporting: Will be checked...")
    print(f"{'='*80}")

    # Run benchmark
    all_results = []
    sys_msg_default = "You are an expert security analyst. Provide thorough, accurate security analysis."
    sys_msg_json = "You are an expert security analyst. Respond ONLY with valid JSON."

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

            if result.ok:
                criteria = test_case.get("criteria", [])
                must_not = test_case.get("must_not", [])

                # Debug output for GPT-5 models
                if model.startswith("gpt-5") and args.show_responses:
                    print(f"\nDEBUG {model} response length: {len(result.text)}")
                    print(f"DEBUG {model} response preview: {repr(result.text[:200])}")

                score, criteria_met, criteria_missed, violations = score_text_enhanced(
                    result.text, criteria, must_not
                )
                result.score = score
                result.criteria_met = criteria_met
                result.criteria_missed = criteria_missed
                result.must_not_violations = violations

                # Show responses if requested
                if args.show_responses:
                    print(f"\n--- {model} Response ---")
                    print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
                    print(f"Score: {score:.3f} | Criteria met: {len(criteria_met)}/{len(criteria)}")
                    print("---")

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

    # Enhanced reporting integration
    try:
        from enhanced_reporting import (
            calculate_enhanced_cost_effectiveness, analyze_by_language,
            analyze_by_owasp_category, generate_language_effectiveness_chart,
            generate_owasp_effectiveness_chart, export_to_csv, export_to_json,
            generate_enhanced_markdown_report
        )

        # Enhanced data capture integration
        from enhanced_data_capture import EnhancedDataCapture

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

    if ENHANCED_CAPTURE_AVAILABLE:
        # Calculate enhanced metrics for all models
        for model in models:
            enhanced_metrics[model] = calculate_enhanced_cost_effectiveness(all_results, model)

        # Language and OWASP analysis
        language_results = analyze_by_language(all_results)
        owasp_results = analyze_by_owasp_category(all_results)

        # Generate additional charts
        if VISUALIZATION_AVAILABLE:
            lang_chart = generate_language_effectiveness_chart(language_results, outdir)
            owasp_chart = generate_owasp_effectiveness_chart(owasp_results, outdir)
            if lang_chart:
                charts['language_effectiveness'] = lang_chart
            if owasp_chart:
                charts['owasp_effectiveness'] = owasp_chart

        # Export to multiple formats
        csv_path = export_to_csv(all_results, models, enhanced_metrics, outdir)
        json_path = export_to_json(all_results, models, enhanced_metrics, language_results, owasp_results, outdir)
        md_path = generate_enhanced_markdown_report(all_results, models, enhanced_metrics,
                                                   language_results, owasp_results, outdir)

        print(f"✓ Enhanced CSV export: {Path(csv_path).name}")
        print(f"✓ Enhanced JSON analysis: {Path(json_path).name}")
        print(f"✓ Enhanced markdown report: {Path(md_path).name}")

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
                    'prompt': f"Test case: {result.suite_id}",  # Descriptive placeholder since original prompt not stored
                    'criteria': (getattr(result, 'criteria_met', None) or []) + (getattr(result, 'criteria_missed', None) or []),
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

    # Generate executive summary (always enabled)
    print(f"📋 Generating executive summary...")
    try:
        generate_executive_summary(all_results, models, args.suite, outdir, charts, enhanced_metrics)
        print(f"✓ Executive summary: {outdir}/executive_summary.md")
    except Exception as e:
        print(f"❌ Executive summary generation failed: {e}")
        print(f"   Attempting to generate basic executive summary...")
        try:
            # Generate basic executive summary without enhanced features
            generate_basic_executive_summary(all_results, models, args.suite, outdir)
            print(f"✓ Basic executive summary: {outdir}/basic_executive_summary.md")
        except Exception as e2:
            print(f"❌ Basic executive summary also failed: {e2}")
    
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
                    "total_cost": sum(r.cost_usd for r in all_results if r.cost_usd) if any(r.cost_usd for r in all_results) else 0
                }
            }, f, indent=2)
        print(f"✓ JSON output: {output_path}")

    print(f"\n📊 Generated Reports & Analysis:")
    print(f"   📋 Executive summary: {outdir}/executive_summary.md")
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
    
    print(f"\n🎉 Comprehensive benchmark complete!")
    print(f"📁 All results saved to: {outdir}")
    print(f"💡 For advanced analysis, see the raw data exports and CSV files")

if __name__ == "__main__":
    main()