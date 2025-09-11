#!/usr/bin/env python3
"""
enhanced_multi_llm_benchmark.py
Benchmark multiple LLM models (OpenAI GPT + Anthropic Claude) over a suite of security prompts.

Built by the Rapticore Security Research Team.

- Loads OPENAI_API_KEY and ANTHROPIC_API_KEY from .env
- OpenAI: GPT-5 / 5-mini: Responses API → Chat fallback, GPT-4o / 4o-mini: Chat Completions
- Anthropic: Claude Sonnet 4: Messages API
- Records per-run: model, path used, elapsed, tokens (in/out/reasoning), optional $cost, correctness score
- Enhanced output: Shows actual responses in console + detailed scoring breakdown
- Outputs: JSON (raw+results), CSV, and Markdown summary in ./benchmark_results/<timestamp>/

Usage examples:
  python3 enhanced_multi_llm_benchmark.py
  python3 enhanced_multi_llm_benchmark.py --json      # enforce JSON outputs in prompts
  python3 enhanced_multi_llm_benchmark.py --models gpt-5,claude-sonnet-4,gpt-4o
  python3 enhanced_multi_llm_benchmark.py --suite prompts.json
  python3 enhanced_multi_llm_benchmark.py --pricing "gpt-4o:in=0.0025,out=0.01;claude-sonnet-4:in=0.003,out=0.015"
  python3 enhanced_multi_llm_benchmark.py --show-responses  # Show full responses in console
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Tuple, List, Dict

from dotenv import load_dotenv

# Import both OpenAI and Anthropic
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

# ---------------------------- Config ----------------------------
DEFAULT_MODELS = ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini", "claude-sonnet-4"]
DEFAULT_TIMEOUT_S = 25
FIRST_SHOT_TOKENS = 512
RETRY_SHOT_TOKENS = 768
STARVED_RATIO = 0.70  # ≥70% output tokens used as reasoning + no text → "starved"

# Default test suites - references to external files and language-specific suites
DEFAULT_SUITE_FILES = {
    "basic": "test_suites/security_basic.yaml",
    "comprehensive": "test_suites/security_comprehensive.yaml",
    "owasp": "test_suites/owasp_top10.yaml",

    # Language-specific test suites
    "go": "test_suites/security_go.yaml",
    "cpp": "test_suites/security_cpp.yaml",
    "java": "test_suites/security_java.yaml",
    "csharp": "test_suites/security_csharp.yaml",
    "c": "test_suites/security_c.yaml",
    "ruby": "test_suites/security_ruby.yaml",
    "php": "test_suites/security_php.yaml",
    "rust": "test_suites/security_rust.yaml",
    "haskell": "test_suites/security_haskell.yaml",
    "python": "test_suites/security_python.yaml",
    "javascript": "test_suites/security_javascript.yaml",

    # Language combinations
    "web_languages": ["basic", "javascript", "php", "ruby", "python", "java", "csharp"],
    "systems_languages": ["c", "cpp", "rust", "go"],
    "memory_safe": ["java", "csharp", "ruby", "python", "javascript", "haskell"],
    "memory_unsafe": ["c", "cpp"],
    "dynamic_languages": ["python", "javascript", "ruby", "php"],
    "functional": ["haskell", "rust"],
    "enterprise": ["java", "csharp", "comprehensive"],
    "all_languages": ["basic", "go", "cpp", "java", "csharp", "c", "ruby", "php", "rust", "haskell", "python",
                      "javascript"]
}

# Enhanced BUILTIN_SUITE for Comprehensive Security Testing
BUILTIN_SUITE = [
    # =================== INJECTION ATTACKS ===================
    {
        "id": "sql_injection_simple",
        "prompt": "Analyze this code for security issues: SELECT * FROM users WHERE id = 123'",
        "criteria": [
            r"sql\s*injection",
            r"parameter|prepared",
            r"select\s*\*",
            r"sanitize|validation",
            r"least\s*privilege|privilege"
        ],
        "must_not": [r"\bno\s+issues\b"],
        "json": False
    },
    {
        "id": "sql_injection_complex",
        "prompt": """Analyze this Python Flask code for vulnerabilities:

@app.route('/search')
def search():
    query = request.args.get('q')
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' AND active = 1"
    results = db.execute(sql).fetchall()
    return jsonify(results)""",
        "criteria": [
            r"sql\s*injection",
            r"parameterized|prepared\s*statement",
            r"f-string|string\s*formatting",
            r"escape|sanitize|validate",
            r"LIKE.*%.*%"
        ],
        "must_not": [r"\bsafe\b", r"\bno\s+vulnerabilities\b"],
        "json": False
    },
    {
        "id": "command_injection",
        "prompt": """Analyze this code for security vulnerabilities:

import subprocess
import os

def backup_file(filename):
    # User provides filename via web form
    command = f"tar -czf backup.tar.gz {filename}"
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout""",
        "criteria": [
            r"command\s*injection",
            r"shell=True",
            r"subprocess|os\.system|exec",
            r"sanitize|validate|escape",
            r"shell\s*escape|shlex"
        ],
        "must_not": [r"\bsecure\b"],
        "json": False
    },
    {
        "id": "broken_access_control",
        "prompt": """Review this user profile endpoint:

@app.route('/user/<int:user_id>')
@login_required
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'ssn': user.ssn,
            'salary': user.salary
        })
    return 404""",
        "criteria": [
            r"access\s*control|authorization",
            r"vertical\s*privilege|horizontal\s*privilege",
            r"ownership\s*check|permission\s*check",
            r"ssn|salary|sensitive",
            r"current_user|session"
        ],
        "must_not": [r"\bauthorized\b", r"\baccess\s*controlled\b"],
        "json": False
    },
    {
        "id": "hardcoded_secrets",
        "prompt": """Analyze this database connection code:

import psycopg2

def connect_to_db():
    conn = psycopg2.connect(
        host="prod-db.example.com",
        database="userdata",
        user="admin",
        password="SuperSecret123!",
        sslmode="disable"
    )
    return conn

API_KEY = "sk_live_51234567890abcdef"
JWT_SECRET = "my_super_secret_key_2023\"""",
        "criteria": [
            r"hardcoded|hard.*coded",
            r"secret|password|key",
            r"environment\s*variable|env\s*var|vault",
            r"rotate|revoke",
            r"sslmode.*disable|ssl.*false"
        ],
        "must_not": [r"\bsecure\b"],
        "json": False
    },
    {
        "id": "insecure_deserialization",
        "prompt": """Review this data processing code:

import pickle
import yaml

def load_user_preferences(data):
    # Load user preferences from uploaded file
    prefs = pickle.loads(data)
    return prefs

def load_config(config_string):
    # Parse YAML configuration
    config = yaml.load(config_string, Loader=yaml.Loader)
    return config""",
        "criteria": [
            r"insecure\s*deserialization|pickle\.loads",
            r"yaml\.load.*Loader|unsafe.*load",
            r"code\s*execution|remote\s*code",
            r"SafeLoader|restricted\s*loader",
            r"serialize|deserialize"
        ],
        "must_not": [r"\bsafe\b"],
        "json": False
    },
    {
        "id": "ssrf_basic",
        "prompt": "Explain SSRF and provide two mitigations in bullet points.",
        "criteria": [
            r"\bSSRF\b|server[-\s]*side request forgery",
            r"allowlist|denylist|egress|outbound",
            r"metadata|169\.254\.169\.254|imds"
        ],
        "must_not": [],
        "json": False
    },
    {
        "id": "reflected_xss",
        "prompt": """Check this search results page:

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_database(query)

    html = f'''
    <h2>Search Results for: {query}</h2>
    <div class="results">
        {generate_results_html(results)}
    </div>
    '''
    return html""",
        "criteria": [
            r"XSS|cross.*site.*scripting",
            r"reflected.*xss|stored.*xss",
            r"escape|sanitize|encode",
            r"html.*injection|script.*injection",
            r"CSP|content.*security.*policy"
        ],
        "must_not": [r"\bsafe\b"],
        "json": False
    },
    {
        "id": "owasp_top3",
        "prompt": "Return the top 3 OWASP Top 10 (2021) items with id,name,risk as a JSON array.",
        "criteria": [
            r"A0?1|Broken Access Control",
            r"A0?2|Cryptographic Failures",
            r"A0?3|Injection",
            r"High"  # risk hint
        ],
        "must_not": [],
        "json": True
    },
    {
        "id": "csrf_vulnerability",
        "prompt": """Analyze this password change endpoint:

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    user = get_current_user()
    if verify_password(current_password, user.password_hash):
        user.password_hash = hash_password(new_password)
        db.session.commit()
        return "Password changed successfully"

    return "Invalid current password", 400""",
        "criteria": [
            r"CSRF|cross.*site.*request.*forgery",
            r"csrf.*token|anti.*csrf",
            r"referer.*check|origin.*check",
            r"state.*changing|sensitive.*operation",
            r"same.*site.*cookie"
        ],
        "must_not": [r"\bprotected\b"],
        "json": False
    }
]


# ------------------------- Pricing Helpers ----------------------
def parse_pricing_arg(pricing_str: Optional[str]) -> Dict[str, Dict[str, float]]:
    """Parse pricing string into model pricing config."""
    pricing: Dict[str, Dict[str, float]] = {}
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
                "out": float(items.get("out", 0.0)),
            }
        except Exception:
            print(f"[warn] Could not parse pricing segment: {part}", file=sys.stderr)
    return pricing


def estimate_cost(model: str, input_tokens: int, output_tokens: int, pricing: Dict[str, Dict[str, float]]) -> Optional[
    float]:
    """Estimate cost based on token usage and pricing."""
    p = pricing.get(model)
    if not p:
        return None
    return (input_tokens / 1000.0) * p["in"] + (output_tokens / 1000.0) * p["out"]


# -------------------------- Data Types --------------------------
@dataclass
class RunResult:
    suite_id: str
    model: str
    path: str  # "Responses", "Responses (retry)", "Chat", "Messages"
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

    def __post_init__(self):
        if self.criteria_met is None:
            self.criteria_met = []
        if self.criteria_missed is None:
            self.criteria_missed = []
        if self.must_not_violations is None:
            self.must_not_violations = []


# --------------------- OpenAI API helpers --------------------
def extract_responses_text(resp: Any) -> str:
    """Robust text extraction from Responses API object."""
    if not OPENAI_AVAILABLE:
        return ""

    txt = getattr(resp, "output_text", None)
    if isinstance(txt, str) and txt.strip():
        return txt.strip()

    out = getattr(resp, "output", None) or []
    parts: List[str] = []
    try:
        for block in out:
            content = getattr(block, "content", None)
            if isinstance(content, list):
                for item in content:
                    text_obj = getattr(item, "text", None)
                    val = getattr(text_obj, "value", None) if text_obj is not None else None
                    if not val:
                        val = getattr(item, "content", None)
                    if not val and isinstance(item, dict):
                        val = item.get("text") or item.get("content") or item.get("value")
                    if isinstance(val, str):
                        parts.append(val)
            elif isinstance(content, str):
                parts.append(content)
    except Exception:
        pass
    return "".join(parts).strip()


def extract_responses_usage(resp: Any) -> Tuple[int, int, int, int]:
    """Returns (input_tokens, output_tokens, reasoning_tokens, total_tokens)."""
    if not OPENAI_AVAILABLE:
        return 0, 0, 0, 0

    usage = getattr(resp, "usage", None) or {}
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens) or 0

    details = getattr(usage, "output_tokens_details", None) or {}
    reasoning_tokens = getattr(details, "reasoning_tokens", 0) or 0
    return input_tokens, output_tokens, reasoning_tokens, total_tokens


def starved_reasoning(resp: Any) -> bool:
    """Check if response was starved by reasoning tokens."""
    if not OPENAI_AVAILABLE:
        return False

    try:
        input_tokens, output_tokens, reasoning_tokens, _ = extract_responses_usage(resp)
        txt = extract_responses_text(resp)
        return (output_tokens > 0 and reasoning_tokens / float(output_tokens) >= STARVED_RATIO) and (not txt)
    except Exception:
        return False


def responses_call(client, model: str, sys_msg: str, user_prompt: str, max_tokens: int, timeout: float):
    """GPT-5 Responses call with constrained reasoning + short answer requirement."""
    if not OPENAI_AVAILABLE:
        raise Exception("OpenAI library not available")

    return client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_prompt},
        ],
        reasoning={"effort": "low"},
        tool_choice="none",
        max_output_tokens=max_tokens,
        timeout=timeout,
    )


# -------------------------- Runners -----------------------------
def run_gpt5_like(
        client,
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        pricing: Dict[str, Dict[str, float]],
) -> RunResult:
    """Run GPT-5 models with Responses API + Chat fallback."""
    if not OPENAI_AVAILABLE:
        return RunResult(
            suite_id=suite_id, model=model, path="OpenAI", ok=False,
            elapsed_s=0.0, error="OpenAI library not available"
        )

    t0 = time.time()
    # 1) Responses
    try:
        resp = responses_call(client, model, sys_msg, prompt, FIRST_SHOT_TOKENS, timeout)
        text = extract_responses_text(resp)
        inp, out, r, tot = extract_responses_usage(resp)
        if text:
            return RunResult(
                suite_id=suite_id, model=model, path="Responses", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=inp, output_tokens=out, reasoning_tokens=r, total_tokens=tot,
                cost_usd=estimate_cost(model, inp, out, pricing),
            )

        if starved_reasoning(resp):
            tight = (
                    "Answer in exactly 3 short bullet lines. "
                    "Output final TEXT only. No hidden steps, no analysis.\n\n" + prompt
            )
            resp2 = responses_call(client, model, sys_msg, tight, RETRY_SHOT_TOKENS, timeout)
            text2 = extract_responses_text(resp2)
            inp2, out2, r2, tot2 = extract_responses_usage(resp2)
            if text2:
                return RunResult(
                    suite_id=suite_id, model=model, path="Responses (retry)", ok=True,
                    elapsed_s=time.time() - t0, text=text2,
                    input_tokens=inp2, output_tokens=out2, reasoning_tokens=r2, total_tokens=tot2,
                    cost_usd=estimate_cost(model, inp2, out2, pricing),
                )
    except Exception as e:
        print(f"[info] Responses failed for {model}: {e}", file=sys.stderr)

    # 2) Chat fallback
    try:
        chat = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt + "\n\nReturn a short plain-text answer."},
            ],
            max_completion_tokens=FIRST_SHOT_TOKENS,
            timeout=timeout,
        )
        text = (chat.choices[0].message.content or "").strip()
        usage = getattr(chat, "usage", None) or {}
        inp = getattr(usage, "prompt_tokens", 0) or 0
        out = getattr(usage, "completion_tokens", 0) or 0
        tot = getattr(usage, "total_tokens", inp + out) or 0
        if text:
            return RunResult(
                suite_id=suite_id, model=model, path="Chat", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=inp, output_tokens=out, reasoning_tokens=0, total_tokens=tot,
                cost_usd=estimate_cost(model, inp, out, pricing),
            )
        return RunResult(suite_id=suite_id, model=model, path="Chat", ok=False, elapsed_s=time.time() - t0,
                         error="Empty chat content")
    except Exception as e:
        return RunResult(suite_id=suite_id, model=model, path="Chat", ok=False, elapsed_s=time.time() - t0,
                         error=str(e))


def run_gpt4_like(
        client,
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]],
) -> RunResult:
    """Run GPT-4 models with Chat Completions."""
    if not OPENAI_AVAILABLE:
        return RunResult(
            suite_id=suite_id, model=model, path="OpenAI", ok=False,
            elapsed_s=0.0, error="OpenAI library not available"
        )

    t0 = time.time()
    try:
        chat = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
            max_tokens=FIRST_SHOT_TOKENS,
            temperature=0.0 if json_mode else 0.2,
            top_p=1.0,
            timeout=timeout,
        )
        text = (chat.choices[0].message.content or "").strip()
        usage = getattr(chat, "usage", None) or {}
        inp = getattr(usage, "prompt_tokens", 0) or 0
        out = getattr(usage, "completion_tokens", 0) or 0
        tot = getattr(usage, "total_tokens", inp + out) or 0
        if text:
            return RunResult(
                suite_id=suite_id, model=model, path="Chat", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=inp, output_tokens=out, reasoning_tokens=0, total_tokens=tot,
                cost_usd=estimate_cost(model, inp, out, pricing),
            )
        return RunResult(suite_id=suite_id, model=model, path="Chat", ok=False, elapsed_s=time.time() - t0,
                         error="Empty chat content")
    except Exception as e:
        return RunResult(suite_id=suite_id, model=model, path="Chat", ok=False, elapsed_s=time.time() - t0,
                         error=str(e))


def run_claude(
        client,
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]],
) -> RunResult:
    """Run Anthropic Claude models with Messages API."""
    if not ANTHROPIC_AVAILABLE:
        return RunResult(
            suite_id=suite_id, model=model, path="Anthropic", ok=False,
            elapsed_s=0.0, error="Anthropic library not available"
        )

    t0 = time.time()
    try:
        # Map model names to Anthropic API model names
        api_model = model
        if model == "claude-sonnet-4":
            api_model = "claude-3-5-sonnet-20241022"  # Update this to latest Claude Sonnet 4 when available
        elif model.startswith("claude-"):
            # Handle other Claude models
            pass

        response = client.messages.create(
            model=api_model,
            max_tokens=FIRST_SHOT_TOKENS,
            system=sys_msg,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0 if json_mode else 0.2,
        )

        text = ""
        if response.content and len(response.content) > 0:
            text = response.content[0].text.strip()

        # Extract usage information
        usage = getattr(response, "usage", None)
        inp = getattr(usage, "input_tokens", 0) if usage else 0
        out = getattr(usage, "output_tokens", 0) if usage else 0
        tot = inp + out

        if text:
            return RunResult(
                suite_id=suite_id, model=model, path="Messages", ok=True,
                elapsed_s=time.time() - t0, text=text,
                input_tokens=inp, output_tokens=out, reasoning_tokens=0, total_tokens=tot,
                cost_usd=estimate_cost(model, inp, out, pricing),
            )
        return RunResult(suite_id=suite_id, model=model, path="Messages", ok=False, elapsed_s=time.time() - t0,
                         error="Empty response content")
    except Exception as e:
        return RunResult(suite_id=suite_id, model=model, path="Messages", ok=False, elapsed_s=time.time() - t0,
                         error=str(e))


def run_one(
        clients: Dict[str, Any],
        suite_id: str,
        model: str,
        sys_msg: str,
        prompt: str,
        timeout: float,
        json_mode: bool,
        pricing: Dict[str, Dict[str, float]],
) -> RunResult:
    """Route to appropriate runner based on model type."""
    if model.startswith("gpt-5"):
        return run_gpt5_like(clients.get("openai"), suite_id, model, sys_msg, prompt, timeout, pricing)
    elif model.startswith("gpt-4"):
        return run_gpt4_like(clients.get("openai"), suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    elif model.startswith("claude-"):
        return run_claude(clients.get("anthropic"), suite_id, model, sys_msg, prompt, timeout, json_mode, pricing)
    else:
        return RunResult(suite_id=suite_id, model=model, path="Unknown", ok=False, elapsed_s=0.0,
                         error=f"Unknown model type: {model}")


# ------------------------ Enhanced Scoring ----------------------
def score_text_detailed(text: str, criteria: List[str], must_not: List[str]) -> Tuple[
    float, List[str], List[str], List[str]]:
    """Enhanced scoring with detailed breakdown of what was matched/missed."""
    T = text.lower()
    criteria_met = []
    criteria_missed = []
    must_not_violations = []

    # Check required criteria
    for patt in criteria:
        try:
            if re.search(patt, T, flags=re.I):
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
            if re.search(patt, T, flags=re.I):
                must_not_violations.append(patt)
        except re.error:
            if patt.lower() in T:
                must_not_violations.append(patt)

    # Calculate score
    pos = len(criteria_met)
    neg = len(must_not_violations) * 0.5
    raw = pos - neg
    denom = max(len(criteria), 1)
    score = max(0.0, min(1.0, raw / denom))

    return score, criteria_met, criteria_missed, must_not_violations


# --------------------------- I/O Utils --------------------------
def load_suite(path: Optional[str]) -> List[dict]:
    if not path:
        return BUILTIN_SUITE

    with open(path, "r", encoding="utf-8") as f:
        if path.endswith('.yaml') or path.endswith('.yml'):
            import yaml
            return yaml.safe_load(f) or []
        else:
            return json.load(f)


def ensure_outdir(base: Optional[str]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(base or "./benchmark_results") / ts
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_results(outdir: Path, results: List[RunResult], raw_dump: List[dict], models: List[str], suite_name: str):
    # CSV
    csv_path = outdir / "results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "suite_id", "model", "path", "ok", "elapsed_s",
            "input_tokens", "output_tokens", "reasoning_tokens", "total_tokens",
            "cost_usd", "score", "criteria_met", "criteria_missed", "must_not_violations", "text"
        ])
        for r in results:
            w.writerow([
                r.suite_id, r.model, r.path, int(r.ok), f"{r.elapsed_s:.2f}",
                r.input_tokens, r.output_tokens, r.reasoning_tokens, r.total_tokens,
                (f"{r.cost_usd:.6f}" if r.cost_usd is not None else ""),
                f"{r.score:.3f}",
                "|".join(r.criteria_met),
                "|".join(r.criteria_missed),
                "|".join(r.must_not_violations),
                r.text.replace("\n", "\\n")[:4000]
            ])

    # JSON
    with open(outdir / "results.json", "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    with open(outdir / "raw_responses.json", "w", encoding="utf-8") as f:
        json.dump(raw_dump, f, indent=2, default=str)

    # Enhanced Markdown summary
    md = []
    md.append(f"# LLM Security Benchmark Results\n")
    md.append(f"**Models:** {', '.join(models)}\n")
    md.append(f"**Suite:** {suite_name}\n")
    md.append(f"**Timestamp:** {datetime.now().isoformat()}\n")

    # Overall statistics
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.ok)
    avg_score = sum(r.score for r in results if r.ok) / max(successful_tests, 1)
    md.append(f"**Total Tests:** {total_tests}\n")
    md.append(f"**Successful:** {successful_tests} ({successful_tests / total_tests * 100:.1f}%)\n")
    md.append(f"**Average Score:** {avg_score:.3f}\n\n")

    # Per-suite analysis
    by_suite: Dict[str, List[RunResult]] = {}
    for r in results:
        by_suite.setdefault(r.suite_id, []).append(r)

    for sid, runs in by_suite.items():
        best = max(runs, key=lambda x: (x.score, -x.elapsed_s))
        md.append(f"## {sid}\n")
        md.append(f"**Best:** `{best.model}` via {best.path} (score {best.score:.3f})\n\n")

        # Results table
        md.append("| Model | OK | Score | Time(s) | Tokens In/Out | Cost | Path |\n")
        md.append("|-------|----:|------:|--------:|---------------|------|------|\n")

        for r in sorted(runs, key=lambda x: (-x.ok, -x.score, x.elapsed_s)):
            cost_str = f"${r.cost_usd:.6f}" if r.cost_usd is not None else "n/a"
            md.append(
                f"| {r.model} | {'✓' if r.ok else '✗'} | {r.score:.3f} | {r.elapsed_s:.2f} | {r.input_tokens}/{r.output_tokens} | {cost_str} | {r.path} |\n")

        md.append("\n")

        # Show best response
        if best.ok and best.text:
            md.append(f"**Best Response ({best.model}):**\n")
            md.append("```\n")
            md.append(best.text[:1000] + ("..." if len(best.text) > 1000 else ""))
            md.append("\n```\n\n")

    with open(outdir / "summary.md", "w", encoding="utf-8") as f:
        f.write("".join(md))

    print(f"\n📁 Results written to: {outdir}")
    print(f"   - CSV:  {csv_path}")
    print(f"   - JSON: {outdir / 'results.json'}")
    print(f"   - RAW:  {outdir / 'raw_responses.json'}")
    print(f"   - MD:   {outdir / 'summary.md'}")


def print_response_details(result: RunResult, show_full: bool = False):
    """Print detailed response information."""
    print(f"    Score Breakdown:")
    print(f"      - Criteria Met: {len(result.criteria_met)}/{len(result.criteria_met) + len(result.criteria_missed)}")
    if result.criteria_met:
        print(f"        ✓ {', '.join(result.criteria_met[:3])}{'...' if len(result.criteria_met) > 3 else ''}")
    if result.criteria_missed:
        print(f"        ✗ {', '.join(result.criteria_missed[:3])}{'...' if len(result.criteria_missed) > 3 else ''}")
    if result.must_not_violations:
        print(f"        ⚠ Violations: {', '.join(result.must_not_violations)}")

    if show_full and result.text:
        print(f"    Response Text:")
        response_lines = result.text.split('\n')
        for i, line in enumerate(response_lines[:10]):  # Show first 10 lines
            print(f"      {line}")
        if len(response_lines) > 10:
            print(f"      ... ({len(response_lines) - 10} more lines)")
    elif result.text:
        # Show just the first line
        first_line = result.text.split('\n')[0]
        print(f"    Response: {first_line[:100]}{'...' if len(first_line) > 100 else ''}")


# ------------------------------ Main ----------------------------
def main():
    ap = argparse.ArgumentParser(description="Benchmark multiple LLM models over a suite of security prompts.")
    ap.add_argument("--models", type=str, default=",".join(DEFAULT_MODELS),
                    help="Comma-separated models (default: gpt-5,gpt-5-mini,gpt-4o,gpt-4o-mini,claude-sonnet-4)")
    ap.add_argument("--suite", type=str, default=None, help="Path to JSON suite file. If omitted, uses built-in suite.")
    ap.add_argument("--json", action="store_true", help="Enforce JSON-only outputs in system message.")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, help="Per-call timeout seconds (default: 25).")
    ap.add_argument("--outdir", type=str, default=None, help="Base output dir (default: ./benchmark_results/<ts>)")
    ap.add_argument("--pricing", type=str, default=None,
                    help='Pricing override, e.g. "gpt-4o:in=0.0025,out=0.01;claude-sonnet-4:in=0.003,out=0.015"')
    ap.add_argument("--show-responses", action="store_true", help="Show full response text in console output")
    args = ap.parse_args()

    load_dotenv()

    # Setup API clients
    clients = {}

    # OpenAI setup
    if OPENAI_AVAILABLE:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            clients["openai"] = OpenAI(api_key=openai_api_key)
            print("✓ OpenAI client initialized")
        else:
            print("⚠ OPENAI_API_KEY not found")

    # Anthropic setup
    if ANTHROPIC_AVAILABLE:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            clients["anthropic"] = anthropic.Anthropic(api_key=anthropic_api_key)
            print("✓ Anthropic client initialized")
        else:
            print("⚠ ANTHROPIC_API_KEY not found")

    if not clients:
        sys.exit("❌ No API keys found. Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY in .env file")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    suite = load_suite(args.suite)
    outdir = ensure_outdir(args.outdir)
    pricing = parse_pricing_arg(args.pricing)

    # Determine suite name for reporting
    if args.suite:
        if args.suite in DEFAULT_SUITE_FILES:
            suite_name = f"{args.suite} (predefined)"
        else:
            suite_name = Path(args.suite).name
    else:
        suite_name = "basic (default)"

    sys_msg_default = "You are a helpful security analyst. Be thorough and specific in identifying vulnerabilities."
    sys_msg_json = "You are a helpful security analyst. Output ONLY valid JSON; no extra text or explanations."

    all_results: List[RunResult] = []
    raw_dump: List[dict] = []

    print(f"\n🔍 Running security benchmark on {len(models)} models with {len(suite)} test cases")
    print(f"📋 Test Suite: {suite_name}")
    print(f"📁 Results will be saved to: {outdir}")
    print()

    for i, item in enumerate(suite, 1):
        sid = item["id"]
        prompt = item["prompt"]
        want_json = bool(item.get("json", False) or args.json)
        sys_msg = sys_msg_json if want_json else sys_msg_default

        print("=" * 120)
        print(f"Test {i}/{len(suite)}: {sid}")
        print("=" * 120)
        prompt_preview = prompt.replace('\n', ' ')[:200] + ("..." if len(prompt) > 200 else "")
        print(f"Prompt: {prompt_preview}")
        print()

        for model in models:
            print(f"→ {model:<15} ... ", end="", flush=True)
            result = run_one(clients, sid, model, sys_msg, prompt, args.timeout, want_json, pricing)

            # Enhanced scoring with details
            if result.ok:
                crit = item.get("criteria", [])
                must_not = item.get("must_not", [])
                score, criteria_met, criteria_missed, violations = score_text_detailed(result.text, crit, must_not)
                result.score = score
                result.criteria_met = criteria_met
                result.criteria_missed = criteria_missed
                result.must_not_violations = violations

            status = "✓ OK " if result.ok else "✗ ERR"
            print(
                f"{status:6} | score={result.score:.3f} | {result.elapsed_s:.2f}s | {result.input_tokens:4d}→{result.output_tokens:4d} tokens")

            # Show detailed breakdown if requested
            if args.show_responses:
                print_response_details(result, show_full=True)
            else:
                print_response_details(result, show_full=False)

            all_results.append(result)

            # Keep raw for debugging
            raw_dump.append({
                "suite_id": sid,
                "model": model,
                "path": result.path,
                "ok": result.ok,
                "elapsed_s": result.elapsed_s,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "reasoning_tokens": result.reasoning_tokens,
                "total_tokens": result.total_tokens,
                "cost_usd": result.cost_usd,
                "score": result.score,
                "criteria_met": result.criteria_met,
                "criteria_missed": result.criteria_missed,
                "must_not_violations": result.must_not_violations,
                "text": result.text[:5000],  # cap raw text
                "error": result.error
            })
        print()

    write_results(outdir, all_results, raw_dump, models, suite_name)

    # Print quick summary
    print(f"\n📊 Summary:")
    by_model = {}
    for r in all_results:
        if r.model not in by_model:
            by_model[r.model] = {"total": 0, "success": 0, "avg_score": 0.0, "total_cost": 0.0}
        by_model[r.model]["total"] += 1
        if r.ok:
            by_model[r.model]["success"] += 1
            by_model[r.model]["avg_score"] += r.score
        if r.cost_usd:
            by_model[r.model]["total_cost"] += r.cost_usd

    # Print summary table
    print(f"\n{'Model':<20} {'Tests':<8} {'Success':<10} {'Avg Score':<12} {'Total Cost':<12}")
    print("-" * 75)

    for model, stats in by_model.items():
        success_rate = stats["success"] / stats["total"] * 100
        avg_score = stats["avg_score"] / max(stats["success"], 1)
        cost_str = f"${stats['total_cost']:.4f}" if stats["total_cost"] > 0 else "n/a"
        print(f"{model:<20} {stats['total']:>3}/{len(suite):<3} {success_rate:>6.1f}% {avg_score:>9.3f} {cost_str:>11}")

    # Find and announce best performers
    if by_model:
        best_accuracy = max(by_model.keys(), key=lambda m: by_model[m]["avg_score"] / max(by_model[m]["success"], 1))
        best_value = None
        if any(stats["total_cost"] > 0 for stats in by_model.values()):
            best_value = max(
                [m for m, stats in by_model.items() if stats["total_cost"] > 0],
                key=lambda m: (by_model[m]["avg_score"] / max(by_model[m]["success"], 1)) / (
                        by_model[m]["total_cost"] / by_model[m]["total"])
            )

        print(f"\n🏆 Best Accuracy: {best_accuracy}")
        if best_value:
            print(f"💰 Best Value: {best_value}")

        print(f"\n📁 Comprehensive reports generated in: {outdir}")
        print(f"   📋 Executive Summary: executive_summary.md")
        print(f"   📊 Performance Analysis: performance_analysis.json")
        print(f"   📈 Detailed Results: summary.md")


if __name__ == "__main__":
    main()
