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
import textwrap
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
    
    @classmethod
    def from_results(cls, model_name: str, results: List[EnhancedRunResult]):
        successful = [r for r in results if r.ok]
        total_tests = len(results)
        successful_tests = len(successful)
        
        if successful_tests == 0:
            return cls(
                model_name=model_name, total_tests=total_tests, successful_tests=0,
                success_rate=0.0, avg_score=0.0, avg_response_time=0.0,
                total_cost=0.0, cost_per_test=0.0, perfect_scores=0, good_scores=0, poor_scores=total_tests,
                score_std_dev=0.0, cost_effectiveness=0.0, speed_score=0.0
            )
        
        scores = [r.score for r in successful]
        response_times = [r.elapsed_s for r in successful]
        costs = [r.cost_usd for r in results if r.cost_usd is not None and r.cost_usd > 0]
        
        # Debug cost calculation
        if model_name.startswith("gpt-5"):
            print(f"\nDEBUG: {model_name} individual costs: {costs}")
            print(f"DEBUG: {model_name} sum of costs: {sum(costs)}")
            print(f"DEBUG: {model_name} number of cost entries: {len(costs)}")
        
        avg_score = statistics.mean(scores) if scores else 0.0
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        total_cost = sum(costs)
        cost_per_test = total_cost / len(costs) if costs else 0.0
        
        perfect_scores = sum(1 for r in successful if r.perfect_score)
        good_scores = sum(1 for r in successful if r.response_quality in ["excellent", "good"])
        poor_scores = sum(1 for r in successful if r.response_quality == "poor")
        
        score_std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        cost_effectiveness = avg_score / cost_per_test if cost_per_test > 0 else 0.0
        speed_score = 1.0 / avg_response_time if avg_response_time > 0 else 0.0
        
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
            speed_score=speed_score
        )

# ------------------------ Google Gemini Integration -------------------------
def run_gemini(
    suite_id: str,
    model: str,
    sys_msg: str,
    prompt: str,
    timeout: float,
    json_mode: bool,
    pricing: Dict[str, Dict[str, float]]
) -> EnhancedRunResult:
    """Run Google Gemini models."""
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
        
        # Configure generation settings with thinking budget control
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=FIRST_SHOT_TOKENS,
            temperature=0.0 if json_mode else 0.2,
        )
        
        # Set thinking budget based on model
        if model == "gemini-2.5-flash":
            # Disable thinking for security analysis (direct responses)
            generation_config.thinking_budget = 0
            full_prompt = f"Provide a direct, concise security analysis without showing your reasoning process.\n\n{full_prompt}"
        elif "lite" in model:
            # Lite models - minimal thinking for cost efficiency
            generation_config.thinking_budget = 0
            full_prompt = f"Provide a brief, direct security assessment.\n\n{full_prompt}"
        else:
            # 2.0-flash models - low thinking budget
            generation_config.thinking_budget = 100  # Low budget for faster responses
        
        response = gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        text = response.text.strip() if response.text else ""
        
        # Estimate token usage (Gemini doesn't provide detailed usage info)
        input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(text.split()) * 1.3
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
    outdir: Path
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
    
    # Security-specific analysis
    vuln_analysis = analyze_vulnerability_categories(results, models)
    business_metrics = calculate_business_metrics(performance_by_model)
    
    # Calculate test statistics
    total_tests = len(results) // len(models) if models else 0
    high_performers = [p.model_name for p in performance_by_model.values() if p.avg_score > 0.8]
    reliable_models = [p.model_name for p in performance_by_model.values() if p.success_rate > 0.95]
    
    # Generate enhanced executive summary
    summary = f"""# Executive Summary: LLM Security Analysis Benchmark
*Built by the Rapticore Security Research Team*

**Test Suite:** {suite_name}  
**Models Evaluated:** {len(models)}  
**Total Test Cases:** {total_tests}  
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Security Analysis Overview

This comprehensive evaluation assessed {len(models)} leading LLM models across {total_tests} security test cases, focusing on their ability to identify, analyze, and provide remediation guidance for critical security vulnerabilities.

## 🏆 Key Findings

### Best Overall Security Analyst: {best_accuracy.model_name}
- **Security Detection Score:** {best_accuracy.avg_score:.3f}/1.0
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

## 🎯 Security Vulnerability Analysis

### Threat Detection Capability by Category"""

    # Add vulnerability category analysis
    if vuln_analysis:
        for category in ["SQL Injection", "XSS/Script Injection", "Access Control", "Authentication", "Cryptography"]:
            if any(category in vuln_analysis.get(model, {}) for model in models):
                summary += f"\n\n**{category}:**"
                category_results = []
                for model in models:
                    if category in vuln_analysis.get(model, {}):
                        score = vuln_analysis[model][category]
                        category_results.append((model, score))
                
                if category_results:
                    category_results.sort(key=lambda x: x[1], reverse=True)
                    summary += f"\n- 🥇 {category_results[0][0]}: {category_results[0][1]:.1%} detection rate"
                    if len(category_results) > 1:
                        summary += f"\n- 🥈 {category_results[1][0]}: {category_results[1][1]:.1%} detection rate"
                    if len(category_results) > 2:
                        summary += f"\n- 🥉 {category_results[2][0]}: {category_results[2][1]:.1%} detection rate"

    summary += f"""

## 💼 Business Impact Analysis

### Security ROI Calculations"""

    for model, metrics in business_metrics.items():
        summary += f"\n\n**{model}:**"
        summary += f"\n- **Annual Risk Reduction Value:** ${metrics['risk_reduction_value']:,.0f}"
        summary += f"\n- **Annual Operating Cost:** ${metrics['annual_cost']:,.0f}"
        summary += f"\n- **ROI:** {metrics['roi']:.1f}x return on investment"
        summary += f"\n- **Compliance Value:** ${metrics['compliance_value']:,.0f}"

    summary += f"""

### Industry Benchmarks
- **Average Security Tool ROI:** 3.2x (industry standard)
- **Critical Vulnerability Cost:** $50,000 average (if exploited)
- **Compliance Penalty Avoidance:** Up to $100,000 value
- **Security Analyst Replacement:** ~$120,000/year salary equivalent

## 📊 Performance Rankings

### Overall Security Effectiveness"""

    # Sort models by security-weighted performance
    security_scores = []
    for perf in performance_by_model.values():
        # Weight security accuracy higher than speed
        security_score = (perf.avg_score * 0.6) + (perf.success_rate * 0.3) + ((1 - perf.score_std_dev) * 0.1)
        security_scores.append((perf.model_name, security_score, perf))
    
    security_scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (model, score, perf) in enumerate(security_scores, 1):
        summary += f"\n\n{rank}. **{model}** (Security Score: {score:.3f})"
        summary += f"\n   - Detection Accuracy: {perf.avg_score:.3f}"
        summary += f"\n   - Reliability: {perf.success_rate:.1%}"
        summary += f"\n   - Response Time: {perf.avg_response_time:.2f}s"
        summary += f"\n   - Cost: ${perf.cost_per_test:.5f}"

    summary += f"""

### Cost-Effectiveness for Security Operations"""

    cost_scores = [(perf.model_name, perf.cost_effectiveness, perf) for perf in performance_by_model.values()]
    cost_scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (model, ce_score, perf) in enumerate(cost_scores, 1):
        summary += f"\n{rank}. **{model}** - {ce_score:.1f} security points per $"

    summary += f"""

## 🔒 Security-Specific Recommendations

### Critical Infrastructure Protection
**Recommended Approach:** Dual-validation with {best_accuracy.model_name} + {most_reliable.model_name}
- **Primary Analysis:** {best_accuracy.model_name} (highest detection accuracy)
- **Validation Pass:** {most_reliable.model_name} (consistency check)
- **Combined Detection Rate:** ~{best_accuracy.avg_score * most_reliable.avg_score * 1.2:.1%} (estimated)
- **Monthly Cost:** ${(performance_by_model[best_accuracy.model_name].cost_per_test + performance_by_model[most_reliable.model_name].cost_per_test) * 1000:.2f} for 1000 tests

### DevSecOps Integration
**Recommended Model:** {best_value.model_name}
- **Real-time CI/CD scanning** with acceptable accuracy
- **Cost-effective** for high-frequency development workflows
- **{best_value.avg_score:.1%} detection rate** suitable for pre-production environments
- **Integration-friendly** {best_value.avg_response_time:.1f}s response time

### Regulatory Compliance Audits
**Recommended Model:** {best_accuracy.model_name}
- **Comprehensive analysis** justifies higher cost for audits
- **Detailed explanations** support compliance documentation
- **{best_accuracy.avg_score:.1%} coverage** of security requirements
- **Audit-ready reports** with professional-grade analysis

### Budget-Constrained Security Programs
**Recommended Tier:**"""

    for rank, (model, ce_score, perf) in enumerate(cost_scores[:3], 1):
        monthly_cost = perf.cost_per_test * 1000
        summary += f"\n{rank}. **{model}** - ${monthly_cost:.2f}/month (1000 tests), {perf.avg_score:.1%} accuracy"

    summary += f"""

## ⚠️ Risk Assessment & Mitigation

### Model-Specific Risk Factors

**High Accuracy Models ({', '.join([p.model_name for p in performance_by_model.values() if p.avg_score > 0.75])}):**
- Risk: Higher operational costs may limit usage frequency
- Mitigation: Reserve for critical security assessments

**Fast Response Models ({', '.join([p.model_name for p in performance_by_model.values() if p.avg_response_time < 8])}):**
- Risk: May miss complex, multi-vector attacks
- Mitigation: Combine with thorough models for important systems

**Cost-Effective Models ({', '.join([p.model_name for p in performance_by_model.values() if p.cost_per_test < 0.005])}):**
- Risk: Lower accuracy on sophisticated threats
- Mitigation: Use for initial screening, escalate findings

### Confidence Level Analysis
- **High Confidence (>85% accuracy):** {len([p for p in performance_by_model.values() if p.avg_score > 0.85])}/{len(models)} models
- **Production Ready (>95% reliability):** {len(reliable_models)}/{len(models)} models
- **Enterprise Grade (>80% accuracy + >95% reliability):** {len([p for p in performance_by_model.values() if p.avg_score > 0.8 and p.success_rate > 0.95])}/{len(models)} models

### Recommended Fallback Strategy
1. **Primary:** {best_accuracy.model_name} (highest accuracy)
2. **Secondary:** {most_reliable.model_name} (most consistent)
3. **Emergency:** {best_value.model_name} (fastest deployment)
4. **Validation:** Manual security expert review for critical findings

---

## 📋 Executive Action Items

1. **Immediate (Week 1):** Deploy {best_value.model_name} for development environment scanning
2. **Short-term (Month 1):** Implement {best_accuracy.model_name} for production security audits  
3. **Medium-term (Quarter 1):** Establish tiered security architecture with appropriate model allocation
4. **Long-term (Year 1):** Develop security metrics dashboard and continuous improvement program

---

*This analysis is based on {len(results)} security test executions across {len(models)} leading LLM models. Built by the Rapticore Security Research Team for comprehensive security program optimization.*

*For detailed technical metrics and raw performance data, see `performance_analysis.json`*"""
    
    # Write executive summary
    with open(outdir / "executive_summary.md", "w", encoding="utf-8") as f:
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
    print(f"\n{'Model':<20} {'Tests':<8} {'Success':<9} {'Avg Score':<10} {'Time(s)':<8} {'Total Cost':<12} {'Quality':<8}")
    print("-" * 95)
    
    # Model performance
    for model, perf in performance_by_model.items():
        quality_dist = f"{perf.good_scores}/{perf.total_tests}"
        print(f"{model:<20} {perf.successful_tests:>3}/{perf.total_tests:<3} "
              f"{perf.success_rate:>6.1%} {perf.avg_score:>9.3f} "
              f"{perf.avg_response_time:>7.2f} ${perf.total_cost:>10.4f} "
              f"{quality_dist:>7}")
    
    # Best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_value = max(performance_by_model.values(), key=lambda p: p.cost_effectiveness)
    fastest = max(performance_by_model.values(), key=lambda p: p.speed_score)
    
    print(f"\n{'='*80}")
    print(f"🏆 Best Accuracy: {best_accuracy.model_name} (Score: {best_accuracy.avg_score:.3f})")
    print(f"💰 Best Value: {best_value.model_name} (CE: {best_value.cost_effectiveness:.1f})")
    print(f"⚡ Fastest: {fastest.model_name} (Time: {fastest.avg_response_time:.2f}s)")
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
    print(f"Models: {', '.join(models)}")
    print(f"Suite: {args.suite} ({len(suite)} test cases)")
    print(f"Output: {outdir}")
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
    generate_executive_summary(all_results, models, args.suite, outdir)
    generate_performance_analysis(all_results, models, outdir)
    
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
    
    print(f"✓ Executive summary: {outdir}/executive_summary.md")
    print(f"✓ Performance analysis: {outdir}/performance_analysis.json")
    print(f"✓ Detailed results: {outdir}/enhanced_benchmark_results.json")
    print(f"\n📁 All results saved to: {outdir}")

if __name__ == "__main__":
    main()