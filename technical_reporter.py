#!/usr/bin/env python3
"""
technical_reporter.py — Rapticore Security Research Team
Drop-in replacement with security-focused rigor and rapid-decision profiles.

What's new (highlights):
- Use-case profiles:
  - RAPID_RESPONSE (time-sensitive: rapid vuln detection in code/PRs, AoC, malware triage)
  - IN_DEPTH (batch, full codebase understanding, metrics/measurements)
- Gates per profile (accuracy, reliability, P95 latency) + clear Go/No-Go
- Statistical rigor:
  - Wilson CI for proportions (success, "correct >= threshold")
  - Bootstrap CI for mean accuracy/latency with n-safeguards
  - Sample-size adequacy flags per model and per category
- Security-aware scoring:
  - Supports optional TP/FP/FN/TN, severity weights if the result provides them
  - Penalty-adjusted quality (failed/timeouts) and severity-weighted utility
- Reproducibility:
  - Captures model params if present (version, region, temperature, seed, max_tokens)
  - Explicit metric definitions in JSON export
- Clear throughput semantics (per worker, theoretical)

Inputs: list of Result-like objects with attrs we already use:
  model, suite_id, ok, score, elapsed_s, cost_usd, input_tokens, output_tokens, total_tokens, text
Optional attrs (used if present): tp, fp, fn, tn, severity_weight, model_version, region, temperature, seed, max_tokens

Exports:
- enhanced_executive_summary.md
- technical_analysis_report.md
- comprehensive_analysis.json
"""

import csv
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np


# -------------------------------
# Utility: Statistics
# -------------------------------

def _classify_complexity(r) -> str:
    """
    Heuristic complexity:
      - Prefer explicit tags in suite_id: 'simple', 'moderate|medium', 'complex|repo|arch'
      - Else based on tokens (input+output):
          <= 400   -> simple
          401-1200 -> moderate
          > 1200   -> high
    """
    sid = (getattr(r, 'suite_id', '') or '').lower()
    if any(k in sid for k in ('complex', 'repo', 'architecture', 'full_codebase', 'deep')):
        return 'high'
    if any(k in sid for k in ('moderate', 'medium', 'batch')):
        return 'moderate'
    if 'simple' in sid or 'diff' in sid or 'pr_' in sid or 'rapid' in sid:
        return 'simple'

    tok = int(getattr(r, 'input_tokens', 0) or 0) + int(getattr(r, 'output_tokens', 0) or 0)
    if tok <= 400:
        return 'simple'
    if tok <= 1200:
        return 'moderate'
    return 'high'


def _summarize_time_sensitive(results: List, models: List[str]) -> Dict[str, Dict[str, Any]]:
    # Only consider time-sensitive use-cases by heuristic (PR/diff/rapid/etc.)
    def _is_time_sensitive(r):
        sid = (getattr(r, 'suite_id', '') or '').lower()
        return any(k in sid for k in ('pr_', 'pull_request', 'diff', 'triage', 'incident', 'rapid', 'aoc', 'malware'))

    buckets = {'simple': [], 'moderate': [], 'high': []}
    for r in results:
        if _is_time_sensitive(r):
            buckets[_classify_complexity(r)].append(r)

    out = {}
    for k, rs in buckets.items():
        if not rs:
            out[k] = {}
            continue
        per_model = {m: [] for m in models}
        for r in rs:
            m = getattr(r, 'model', '')
            if m in per_model:
                per_model[m].append(r)

        tbl = {}
        for m, rlist in per_model.items():
            if not rlist:
                continue
            oks = [bool(getattr(x, 'ok', False)) for x in rlist]
            succ = sum(oks)
            n = len(rlist)
            scores = [float(getattr(x, 'score', 0.0) or 0.0) for x in rlist]
            lats = [float(getattr(x, 'elapsed_s', 0.0) or 0.0) for x, ok in zip(rlist, oks) if ok]
            costs = [float(getattr(x, 'cost_usd', 0.0) or 0.0) for x in rlist if getattr(x, 'cost_usd', None) is not None]
            tbl[m] = {
                'n': n,
                'success': succ / n if n else 0.0,
                'acc': float(np.mean(scores)) if scores else 0.0,
                'p95': float(np.percentile(lats, 95)) if lats else 0.0,
                'cost/test': float(np.mean(costs)) if costs else 0.0
            }
        out[k] = tbl
    return out

def _wilson_ci(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a proportion."""
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + (z ** 2) / n
    center = p + (z ** 2) / (2 * n)
    margin = z * np.sqrt((p * (1 - p) + (z ** 2) / (4 * n)) / n)
    lower = (center - margin) / denom
    upper = (center + margin) / denom
    return (max(0.0, lower), min(1.0, upper))


def _bootstrap_ci(values: List[float], ci: float = 0.95, iters: int = 1000, seed: int = 1337) -> Tuple[float, float]:
    """Bootstrap CI for mean with small-n safeguards and deterministic seed."""
    if not values:
        return (0.0, 0.0)
    if len(values) < 2:
        m = float(np.mean(values))
        return (m, m)

    # Use deterministic RNG
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)

    # Adjust iterations based on sample size
    actual_iters = 200 if n >= 50 else 100

    idx = rng.integers(0, n, size=(actual_iters, n))
    means = np.mean(arr[idx], axis=1)
    alpha = (1 - ci) / 2
    return (float(np.quantile(means, alpha)), float(np.quantile(means, 1 - alpha)))


def _norm(x: float, lo: float, hi: float) -> float:
    """Normalize value to [0,1] range with bounds."""
    if hi <= lo:
        return 0.0
    x = max(lo, min(hi, x))
    return (x - lo) / (hi - lo)


# -------------------------------
# Use-case profiles & thresholds
# -------------------------------

@dataclass
class UseCaseProfile:
    name: str
    # Gates
    min_accuracy: float
    min_success_rate: float
    max_p95_latency_s: float
    max_cost_per_test: Optional[float] = None
    # Decision weights (how to rank models for this profile)
    weight_accuracy: float = 0.6
    weight_latency: float = 0.25
    weight_cost: float = 0.15
    # Recommended minimum sample size per model
    min_n: int = 30


RAPID_RESPONSE = UseCaseProfile(
    name="RAPID_RESPONSE",
    # time-sensitive security work: PR reviews, rapid vuln detection, AoC/IR triage
    min_accuracy=0.70,  # realistic for speed-sensitive workflows
    min_success_rate=0.95,
    max_p95_latency_s=20.0,  # slightly more forgiving for real-world use
    max_cost_per_test=0.0020,   # $0.002/test (example cap)
    weight_accuracy=0.5,
    weight_latency=0.35,
    weight_cost=0.15,
    min_n=30
)

IN_DEPTH = UseCaseProfile(
    name="IN_DEPTH",
    # batch / extended analysis: whole codebase understanding, metrics & measurements
    min_accuracy=0.75,  # higher bar for thorough analysis
    min_success_rate=0.97,
    max_p95_latency_s=45.0,  # more forgiving latency for depth
    weight_accuracy=0.7,
    weight_latency=0.1,
    weight_cost=0.2,
    min_n=50
)


# -------------------------------
# Data classes
# -------------------------------

@dataclass
class EnhancedMetrics:
    total_tests: int
    successful_tests: int
    failed_tests: int

    perfect_scores: int
    excellent_scores: int
    good_scores: int
    fair_scores: int
    poor_scores: int

    total_cost: float
    cost_per_test: float
    cost_per_correct_answer: float
    cost_per_partial_answer: float

    traditional_effectiveness: float
    quality_weighted_effectiveness: float
    penalty_adjusted_effectiveness: float

    # New: severity-aware and FP/FN aware (if supplied)
    severity_weighted_score: float = 0.0
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


@dataclass
class ModelPerformance:
    model: str
    total_tests: int
    passed_tests: int
    avg_score: float
    avg_time_s: float
    total_cost_usd: float
    cost_per_test: float
    success_rate: float
    perfect_rate: float
    score_variance: float
    enhanced_metrics: Optional[EnhancedMetrics] = None

    # CI & latency dist
    accuracy_ci: Tuple[float, float] = (0.0, 0.0)
    success_ci: Tuple[float, float] = (0.0, 0.0)
    latency_ci: Tuple[float, float] = (0.0, 0.0)
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    latency_std: float = 0.0

    # Quality indicators
    reliability_score: float = 0.0
    meets_profile_gate: Dict[str, bool] = None
    decision_score_by_profile: Dict[str, float] = None

    # Optional: captured config
    model_versions: Counter = None
    regions: Counter = None
    temperatures: Counter = None
    seeds: Counter = None
    max_tokens_set: Counter = None

    # Token metrics
    avg_input_tokens: int = 0
    avg_output_tokens: int = 0
    total_tokens: int = 0

    @classmethod
    def from_results(cls, model: str, results: List, accuracy_threshold: float = 0.70) -> "ModelPerformance":
        if not results:
            return cls(
                model=model, total_tests=0, passed_tests=0, avg_score=0.0,
                avg_time_s=0.0, total_cost_usd=0.0, cost_per_test=0.0,
                success_rate=0.0, perfect_rate=0.0, score_variance=0.0,
                meets_profile_gate={}, decision_score_by_profile={},
                model_versions=Counter(), regions=Counter(), temperatures=Counter(),
                seeds=Counter(), max_tokens_set=Counter()
            )

        # Basic fields - consistent accuracy calculation (include all results)
        scores = [float(getattr(r, 'score', 0.0) or 0.0) for r in results]
        times = [float(getattr(r, 'elapsed_s', 0.0)) for r in results if getattr(r, 'elapsed_s', None) is not None]
        costs = [float(getattr(r, 'cost_usd', 0.0)) for r in results if getattr(r, 'cost_usd', None) is not None]
        oks = [bool(getattr(r, 'ok', False)) for r in results]

        passed = sum(1 for ok in oks if ok)
        perfect = sum(1 for s in scores if s >= 1.0)

        avg_score = float(np.mean(scores)) if scores else 0.0
        avg_time = float(np.mean(times)) if times else 0.0
        total_cost = float(np.sum(costs)) if costs else 0.0
        cost_per_test = (total_cost / len(results)) if results else 0.0
        success_rate = (passed / len(results)) if results else 0.0
        perfect_rate = (perfect / len(results)) if results else 0.0

        # CIs
        acc_ci = _bootstrap_ci(scores, ci=0.95)
        suc_ci = _wilson_ci(passed, len(results))
        lat_ci = _bootstrap_ci(times, ci=0.95)

        # Latency distribution
        p95 = float(np.percentile(times, 95)) if times else 0.0
        p99 = float(np.percentile(times, 99)) if times else 0.0
        lat_std = float(np.std(times)) if times else 0.0

        # Enhanced metrics (includes FP/FN if present)
        enhanced = _calculate_enhanced_metrics(results)

        # Improved reliability score: success stability + latency stability
        cv_latency = (lat_std / avg_time) if avg_time > 0 else 0.0
        reliability = success_rate * (1.0 - min(1.0, cv_latency))
        reliability = max(0.0, min(1.0, reliability))

        # Config capture if present
        versions = Counter([getattr(r, 'model_version', None) for r in results if getattr(r, 'model_version', None)])
        regions = Counter([getattr(r, 'region', None) for r in results if getattr(r, 'region', None)])
        temps = Counter([getattr(r, 'temperature', None) for r in results if getattr(r, 'temperature', None)])
        seeds = Counter([getattr(r, 'seed', None) for r in results if getattr(r, 'seed', None)])
        max_tokens = Counter([getattr(r, 'max_tokens', None) for r in results if getattr(r, 'max_tokens', None)])

        # Token metrics
        input_tokens = [int(getattr(r, 'input_tokens', 0) or 0) for r in results]
        output_tokens = [int(getattr(r, 'output_tokens', 0) or 0) for r in results]
        avg_in = int(np.mean(input_tokens)) if input_tokens else 0
        avg_out = int(np.mean(output_tokens)) if output_tokens else 0
        total_tok = int(np.sum(input_tokens) + np.sum(output_tokens))

        perf = cls(
            model=model,
            total_tests=len(results),
            passed_tests=passed,
            avg_score=avg_score,
            avg_time_s=avg_time,
            total_cost_usd=total_cost,
            cost_per_test=cost_per_test,
            success_rate=success_rate,
            perfect_rate=perfect_rate,
            score_variance=float(np.var(scores)) if scores else 0.0,
            enhanced_metrics=enhanced,
            accuracy_ci=acc_ci,
            success_ci=suc_ci,
            latency_ci=lat_ci,
            p95_latency=p95,
            p99_latency=p99,
            latency_std=lat_std,
            reliability_score=reliability,
            meets_profile_gate={},
            decision_score_by_profile={},
            model_versions=versions,
            regions=regions,
            temperatures=temps,
            seeds=seeds,
            max_tokens_set=max_tokens,
            avg_input_tokens=avg_in,
            avg_output_tokens=avg_out,
            total_tokens=total_tok
        )

        # Compute gate pass + decision scores for supported profiles
        for profile in (RAPID_RESPONSE, IN_DEPTH):
            cost_ok = True if profile.max_cost_per_test is None else (perf.cost_per_test <= profile.max_cost_per_test)
            meets = (
                    perf.avg_score >= profile.min_accuracy and
                    perf.success_rate >= profile.min_success_rate and
                    perf.p95_latency <= profile.max_p95_latency_s and
                    cost_ok
            )
            perf.meets_profile_gate[profile.name] = meets

            # Normalized decision score components
            lat = perf.p95_latency or perf.avg_time_s or 0.0

            # Define reasonable bounds for normalization
            LAT_BOUNDS = (1.0, max(profile.max_p95_latency_s, 60.0))
            COST_BOUNDS = (0.00005, 0.05)  # $0.00005 to $0.05 per test

            acc_term = perf.avg_score  # already 0..1
            lat_term = 1.0 - _norm(lat, *LAT_BOUNDS)  # lower latency -> higher score
            cost_term = 1.0 - _norm(perf.cost_per_test or 0.0, *COST_BOUNDS)  # cheaper -> higher

            decision = (
                    profile.weight_accuracy * acc_term +
                    profile.weight_latency * lat_term +
                    profile.weight_cost * cost_term
            )
            perf.decision_score_by_profile[profile.name] = float(decision)

        return perf


# -------------------------------
# Classification helpers
# -------------------------------

def _classify_language(test_id: str) -> str:
    t = (test_id or "").lower()
    if 'python' in t or 'py_' in t:
        return 'Python'
    if 'javascript' in t or 'js_' in t or 'node' in t:
        return 'JavaScript'
    if 'java' in t and 'javascript' not in t:
        return 'Java'
    if 'go_' in t or 'golang' in t:
        return 'Go'
    if 'rust' in t:
        return 'Rust'
    if 'csharp' in t or 'dotnet' in t:
        return 'C#'
    if 'c_' in t or 'cpp_' in t:
        return 'C/C++'
    if 'php' in t:
        return 'PHP'
    if 'ruby' in t:
        return 'Ruby'
    if 'haskell' in t:
        return 'Haskell'
    return 'General Security'


def _classify_owasp(test_id: str) -> str:
    t = (test_id or "").lower()
    if 'sql' in t or 'injection' in t:
        return 'A03: Injection'
    if 'xss' in t or 'cross site' in t or 'cross-site' in t:
        return 'A03: Injection (XSS)'
    if 'access' in t or 'rbac' in t or 'authz' in t or 'broken' in t:
        return 'A01: Broken Access Control'
    if 'secret' in t or 'hardcoded' in t or 'crypto' in t:
        return 'A02: Cryptographic Failures'
    if 'csrf' in t:
        return 'A01: Broken Access Control (CSRF)'
    if 'deserialization' in t or 'supply chain' in t:
        return 'A08: Software and Data Integrity Failures'
    if 'ssrf' in t:
        return 'A10: Server-Side Request Forgery'
    return 'General Security'


# -------------------------------
# Enhanced metrics calculator
# -------------------------------

CORRECT_THRESH = 0.8  # Configurable threshold for "correct" answers


def _calculate_enhanced_metrics(results: List) -> EnhancedMetrics:
    # ok means request completed; score is [0..1]
    successful = [r for r in results if bool(getattr(r, 'ok', False))]
    failed = [r for r in results if not bool(getattr(r, 'ok', False))]

    scores = [float(getattr(r, 'score', 0.0) or 0.0) for r in successful]
    costs = [float(getattr(r, 'cost_usd', 0.0) or 0.0) for r in results if getattr(r, 'cost_usd', None) is not None]
    total_cost = float(np.sum(costs)) if costs else 0.0
    cost_per_test = (total_cost / len(results)) if results else 0.0

    # Score distribution thresholds
    perfect_scores = sum(1 for s in scores if s >= 1.0)
    excellent_scores = sum(1 for s in scores if s >= 0.8)
    good_scores = sum(1 for s in scores if 0.6 <= s < 0.8)
    fair_scores = sum(1 for s in scores if 0.4 <= s < 0.6)
    poor_scores = sum(1 for s in scores if s < 0.4)

    avg_score = float(np.mean(scores)) if scores else 0.0
    traditional_effectiveness = (avg_score / cost_per_test) if cost_per_test > 0 else 0.0

    # Quality weights (tuned for security triage)
    qw = {'perfect': 1.0, 'excellent': 0.9, 'good': 0.7, 'fair': 0.5, 'poor': 0.2}
    n_succ = max(1, len(successful))
    weighted = (
                       (perfect_scores * qw['perfect']) +
                       ((excellent_scores - perfect_scores) * qw['excellent']) +
                       (good_scores * qw['good']) +
                       (fair_scores * qw['fair']) +
                       (poor_scores * qw['poor'])
               ) / n_succ

    quality_weighted_effectiveness = (weighted / cost_per_test) if cost_per_test > 0 else 0.0

    # Penalty for failed attempts/timeouts
    penalty = len(failed) * 0.5  # tune if needed
    penalty_adjusted_effectiveness = ((max(0.0, weighted - penalty)) / cost_per_test) if cost_per_test > 0 else 0.0

    # Optional detection metrics if provided (TP/FP/FN)
    tp = sum(int(getattr(r, 'tp', 0) or 0) for r in results)
    fp = sum(int(getattr(r, 'fp', 0) or 0) for r in results)
    fn = sum(int(getattr(r, 'fn', 0) or 0) for r in results)
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else None
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else None
    f1 = (2 * precision * recall / (precision + recall)) if precision not in (None, 0) and recall not in (None,
                                                                                                          0) else None

    # Optional severity weighting if provided per result
    sev_sum = 0.0
    sev_count = 0
    for r in results:
        s = getattr(r, 'score', None)
        w = getattr(r, 'severity_weight', None)
        if s is not None and w is not None:
            sev_sum += float(s) * float(w)
            sev_count += 1
    severity_weighted_score = (sev_sum / sev_count) if sev_count > 0 else 0.0

    return EnhancedMetrics(
        total_tests=len(results),
        successful_tests=len(successful),
        failed_tests=len(failed),
        perfect_scores=perfect_scores,
        excellent_scores=excellent_scores,
        good_scores=good_scores,
        fair_scores=fair_scores,
        poor_scores=poor_scores,
        total_cost=total_cost,
        cost_per_test=cost_per_test,
        cost_per_correct_answer=(total_cost / perfect_scores) if perfect_scores > 0 else 0.0,
        cost_per_partial_answer=cost_per_test,
        traditional_effectiveness=traditional_effectiveness,
        quality_weighted_effectiveness=quality_weighted_effectiveness,
        penalty_adjusted_effectiveness=penalty_adjusted_effectiveness,
        severity_weighted_score=severity_weighted_score,
        f1_score=f1,
        precision=precision,
        recall=recall
    )


# -------------------------------
# Reporter (language/OWASP rollups + exports)
# -------------------------------

class EnhancedUnifiedReporter:
    def __init__(self, accuracy_threshold: float = 0.70):
        self.accuracy_threshold = accuracy_threshold

    def analyze_by_language(self, results: List) -> Dict[str, Dict[str, Any]]:
        buckets = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})
        for r in results:
            if not bool(getattr(r, 'ok', False)):
                continue
            lang = _classify_language(getattr(r, 'suite_id', ''))
            buckets[lang]['results'].append(r)
            buckets[lang]['scores'].append(float(getattr(r, 'score', 0.0) or 0.0))
            c = getattr(r, 'cost_usd', None)
            if c is not None:
                buckets[lang]['costs'].append(float(c))

        out = {}
        for lang, data in buckets.items():
            if not data['results']:
                continue
            scores = data['scores']
            costs = data['costs']
            models = defaultdict(lambda: {'scores': [], 'costs': []})
            for r in data['results']:
                m = getattr(r, 'model', 'unknown')
                models[m]['scores'].append(float(getattr(r, 'score', 0.0) or 0.0))
                c = getattr(r, 'cost_usd', None)
                if c is not None:
                    models[m]['costs'].append(float(c))
            model_metrics = {
                m: {
                    'avg_score': float(np.mean(md['scores'])) if md['scores'] else 0.0,
                    'avg_cost': float(np.mean(md['costs'])) if md['costs'] else 0.0,
                    'test_count': len(md['scores'])
                } for m, md in models.items()
            }
            avg_cost = float(np.mean(costs)) if costs else 0.0
            out[lang] = {
                'total_tests': len(data['results']),
                'avg_score': float(np.mean(scores)),
                'success_rate': len(scores) / len(data['results']),
                'avg_cost': avg_cost,
                'effectiveness': (float(np.mean(scores)) / avg_cost) if avg_cost > 0 else 0.0,
                'models': model_metrics,
                'ci_score': _bootstrap_ci(scores, 0.95)
            }
        return out

    def analyze_by_owasp_category(self, results: List) -> Dict[str, Dict[str, Any]]:
        buckets = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})
        for r in results:
            if not bool(getattr(r, 'ok', False)):
                continue
            cat = _classify_owasp(getattr(r, 'suite_id', ''))
            buckets[cat]['results'].append(r)
            buckets[cat]['scores'].append(float(getattr(r, 'score', 0.0) or 0.0))
            c = getattr(r, 'cost_usd', None)
            if c is not None:
                buckets[cat]['costs'].append(float(c))

        out = {}
        for cat, data in buckets.items():
            scores = data['scores']
            costs = data['costs']
            models = defaultdict(lambda: {'scores': [], 'costs': []})
            for r in data['results']:
                m = getattr(r, 'model', 'unknown')
                models[m]['scores'].append(float(getattr(r, 'score', 0.0) or 0.0))
                c = getattr(r, 'cost_usd', None)
                if c is not None:
                    models[m]['costs'].append(float(c))
            model_metrics = {
                m: {
                    'avg_score': float(np.mean(md['scores'])) if md['scores'] else 0.0,
                    'avg_cost': float(np.mean(md['costs'])) if md['costs'] else 0.0,
                    'test_count': len(md['scores'])
                } for m, md in models.items()
            }
            avg_cost = float(np.mean(costs)) if costs else 0.0
            out[cat] = {
                'total_tests': len(data['results']),
                'avg_score': float(np.mean(scores)) if scores else 0.0,
                'success_rate': len(scores) / len(data['results']) if data['results'] else 0.0,
                'avg_cost': avg_cost,
                'effectiveness': (float(np.mean(scores)) / avg_cost) if avg_cost > 0 else 0.0,
                'models': model_metrics,
                'ci_score': _bootstrap_ci(scores, 0.95)
            }
        return out

    # ---------- Exports ----------
    def export_to_csv(self, results: List, models: List[str], performance_by_model: Dict, outdir: Path) -> str:
        csv_path = outdir / "detailed_results.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow([
                'model', 'suite_id', 'ok', 'score', 'elapsed_s', 'cost_usd',
                'input_tokens', 'output_tokens', 'total_tokens',
                'tp', 'fp', 'fn', 'tn', 'severity_weight',
                'model_version', 'region', 'temperature', 'seed', 'max_tokens'
            ])
            for r in results:
                w.writerow([
                    getattr(r, 'model', ''),
                    getattr(r, 'suite_id', ''),
                    getattr(r, 'ok', False),
                    getattr(r, 'score', 0.0),
                    getattr(r, 'elapsed_s', 0.0),
                    getattr(r, 'cost_usd', 0.0),
                    getattr(r, 'input_tokens', 0),
                    getattr(r, 'output_tokens', 0),
                    getattr(r, 'total_tokens', 0),
                    getattr(r, 'tp', ''),
                    getattr(r, 'fp', ''),
                    getattr(r, 'fn', ''),
                    getattr(r, 'tn', ''),
                    getattr(r, 'severity_weight', ''),
                    getattr(r, 'model_version', ''),
                    getattr(r, 'region', ''),
                    getattr(r, 'temperature', ''),
                    getattr(r, 'seed', ''),
                    getattr(r, 'max_tokens', ''),
                ])

        # Model summary
        summary_path = outdir / "model_summary.csv"
        with open(summary_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow([
                'model', 'total_tests', 'successful_tests', 'avg_score',
                'total_cost', 'cost_per_test', 'quality_weighted_effectiveness',
                'penalty_adjusted_effectiveness', 'success_rate',
                'accuracy_ci_low', 'accuracy_ci_high', 'success_ci_low', 'success_ci_high',
                'p95_latency', 'p99_latency', 'latency_std',
                'meets_RAPID_RESPONSE', 'meets_IN_DEPTH'
            ])
            for m in models:
                perf: ModelPerformance = performance_by_model.get(m)
                if not perf or not perf.enhanced_metrics:
                    continue
                em = perf.enhanced_metrics
                w.writerow([
                    m, perf.total_tests, perf.passed_tests, perf.avg_score,
                    perf.total_cost_usd, perf.cost_per_test,
                    em.quality_weighted_effectiveness, em.penalty_adjusted_effectiveness,
                    perf.success_rate,
                    perf.accuracy_ci[0], perf.accuracy_ci[1],
                    perf.success_ci[0], perf.success_ci[1],
                    perf.p95_latency, perf.p99_latency, perf.latency_std,
                    perf.meets_profile_gate.get('RAPID_RESPONSE', False),
                    perf.meets_profile_gate.get('IN_DEPTH', False),
                ])
        return str(csv_path)

    def export_to_json(
            self,
            results: List,
            models: List[str],
            performance_by_model: Dict,
            language_results: Dict,
            owasp_results: Dict,
            outdir: Path
    ) -> str:
        def _defs() -> Dict[str, Any]:
            return {
                "metrics_definitions": {
                    "score": "Normalized [0..1] correctness/quality for the task.",
                    "success_rate": "Proportion of requests that returned an OK (non-error) response.",
                    "avg_score_ci": "Bootstrap 95% CI of mean score.",
                    "success_rate_ci": "Wilson 95% CI for success proportion.",
                    "latency": "Elapsed seconds (end-to-end).",
                    "p95_latency": "95th percentile of elapsed_s per model.",
                    "reliability_score": "0..1 composite: success rate weighted by latency stability.",
                    "quality_weighted_effectiveness": "Weighted quality per $ (weights tuned for security triage).",
                    "penalty_adjusted_effectiveness": "Quality/$ penalized by failed attempts.",
                    "decision_score_by_profile": "Composite ranking per profile (accuracy, latency, cost).",
                    "severity_weighted_score": "Mean(score * severity_weight) when provided.",
                    "precision/recall/F1": "Computed when TP/FP/FN are supplied."
                },
                "profiles": {
                    RAPID_RESPONSE.name: asdict(RAPID_RESPONSE),
                    IN_DEPTH.name: asdict(IN_DEPTH),
                }
            }

        json_data = {
            'metadata': {
                'analysis_date': datetime.utcnow().isoformat() + 'Z',
                'total_models': len(models),
                'total_tests': sum(p.total_tests for p in performance_by_model.values()),
                'analysis_type': 'security_benchmark_enhanced'
            },
            'model_analysis': {},
            'language_analysis': language_results,
            'owasp_analysis': owasp_results,
            'enhanced_metrics': {},
            'definitions': _defs()
        }

        for m in models:
            perf: ModelPerformance = performance_by_model.get(m)
            if not perf:
                continue
            json_data['model_analysis'][m] = {
                'total_tests': perf.total_tests,
                'successful_tests': perf.passed_tests,
                'avg_score': perf.avg_score,
                'avg_response_time': perf.avg_time_s,
                'p95_latency': perf.p95_latency,
                'p99_latency': perf.p99_latency,
                'total_cost': perf.total_cost_usd,
                'cost_per_test': perf.cost_per_test,
                'success_rate': perf.success_rate,
                'accuracy_ci': perf.accuracy_ci,
                'success_ci': perf.success_ci,
                'latency_ci': perf.latency_ci,
                'reliability_score': perf.reliability_score,
                'meets_profile_gate': perf.meets_profile_gate,
                'decision_score_by_profile': perf.decision_score_by_profile,
                'token_stats': {
                    'avg_input_tokens': perf.avg_input_tokens,
                    'avg_output_tokens': perf.avg_output_tokens,
                    'total_tokens': perf.total_tokens
                }
            }
            if perf.enhanced_metrics:
                json_data['enhanced_metrics'][m] = asdict(perf.enhanced_metrics)

        json_path = outdir / "comprehensive_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        return str(json_path)


# -------------------------------
# Executive summaries (kept compatible)
# -------------------------------

def _build_performance(per_model_results: Dict[str, List], accuracy_threshold: float) -> Dict[str, ModelPerformance]:
    perf_by_model: Dict[str, ModelPerformance] = {}
    for model, rlist in per_model_results.items():
        perf_by_model[model] = ModelPerformance.from_results(model, rlist, accuracy_threshold)
    return perf_by_model


def _partition_results_by_model(results: List, models: List[str]) -> Dict[str, List]:
    per_model = {m: [] for m in models}
    for r in results:
        m = getattr(r, 'model', '')
        if m in per_model:
            per_model[m].append(r)
    return per_model


def generate_unified_executive_summary(
        results: List,
        models: List[str],
        suite_name: str,
        outdir: Path,
        charts: Optional[Dict[str, str]] = None,
        enhanced_metrics: Optional[Dict] = None,
        language_results: Optional[Dict] = None,
        owasp_results: Optional[Dict] = None,
        total_cost: float = 0.0,
        active_profile: UseCaseProfile = RAPID_RESPONSE,
) -> str:
    """
    Unified executive summary with profile-aware recommendations.
    """
    accuracy_threshold = active_profile.min_accuracy
    reporter = EnhancedUnifiedReporter(accuracy_threshold)

    # Build per-model performance
    per_model_results = _partition_results_by_model(results, models)
    performance_by_model = _build_performance(per_model_results, accuracy_threshold)
    if not performance_by_model:
        return "No valid results to analyze"

    # Stratified analyses
    language_results = language_results or reporter.analyze_by_language(results)
    owasp_results = owasp_results or reporter.analyze_by_owasp_category(results)

    # Decisioning
    qualified = [p for p in performance_by_model.values() if p.meets_profile_gate.get(active_profile.name, False)]
    disqualified = [p for p in performance_by_model.values() if
                    not p.meets_profile_gate.get(active_profile.name, False)]

    # Rank by decision score for the active profile
    ranked = sorted(performance_by_model.values(),
                    key=lambda p: p.decision_score_by_profile.get(active_profile.name, 0.0),
                    reverse=True)

    best_for_profile = ranked[0] if ranked else None

    # Aggregates
    total_tests = sum(p.total_tests for p in performance_by_model.values())
    models_count = len(performance_by_model)
    avg_cost_per_test = (total_cost / total_tests) if total_tests > 0 else 0.0
    overall_completion = (
                sum(p.passed_tests for p in performance_by_model.values()) / total_tests) if total_tests else 0.0

    # Compose summary
    date_s = datetime.now().strftime('%B %d, %Y')
    summary = f"""# Security Benchmark Executive Summary ({active_profile.name})

**Suite:** {suite_name} | **Models Tested:** {models_count} | **Total Security Tests:** {total_tests} | **Date:** {date_s} | **Total Investment:** ${total_cost:.4f}

**Active Profile:** **{active_profile.name}**  
Gates: accuracy ≥ {active_profile.min_accuracy:.0%}, success ≥ {active_profile.min_success_rate:.0%}, P95 latency ≤ {active_profile.max_p95_latency_s:.0f}s

## Key Findings

• **Qualified for {active_profile.name}:** {len(qualified)}/{models_count}  
• **Overall Success Rate:** {overall_completion:.1%}
"""

    if best_for_profile:
        summary += f"• **Top Pick for {active_profile.name}:** {best_for_profile.model}  \n"
        summary += f"  (Accuracy {best_for_profile.avg_score:.1%}, P95 {best_for_profile.p95_latency:.1f}s, Cost/Test ${best_for_profile.cost_per_test:.5f})\n"

    # Table
    summary += """
## Profile-Aware Model Comparison

| Model | Tests | Success | Acc (95% CI) | P95 Lat (s) | Cost/Test | Meets Gate |
|------|------:|--------:|:-------------|------------:|----------:|:----------|"""
    for p in sorted(performance_by_model.values(), key=lambda x: x.avg_score, reverse=True):
        acc_ci = f"{p.avg_score:.1%} [{p.accuracy_ci[0]:.2f}, {p.accuracy_ci[1]:.2f}]"
        meets = "✅" if p.meets_profile_gate.get(active_profile.name, False) else "❌"
        summary += f"\n| {p.model} | {p.total_tests} | {p.success_rate:.1%} | {acc_ci} | {p.p95_latency:.1f} | ${p.cost_per_test:.5f} | {meets} |"

    # Recommendations tuned to both Rapid and In-Depth
    summary += f"""

## Deployment Recommendations

### For **Rapid Response** (PR reviews, rapid vuln checks, AoC/malware triage)
- Gate: accuracy ≥ {RAPID_RESPONSE.min_accuracy:.0%}, success ≥ {RAPID_RESPONSE.min_success_rate:.0%}, P95 ≤ {RAPID_RESPONSE.max_p95_latency_s:.0f}s
- Pick the highest **decision score** under RAPID_RESPONSE.
- Architecture: low-latency path, response caching for repeat patterns, concurrency >= CPU cores, circuit-breaking.

### For **In-Depth Analysis** (full repo, metrics/measurements)
- Gate: accuracy ≥ {IN_DEPTH.min_accuracy:.0%}, success ≥ {IN_DEPTH.min_success_rate:.0%}, P95 ≤ {IN_DEPTH.max_p95_latency_s:.0f}s
- Prefer highest accuracy and quality-weighted effectiveness.
- Architecture: batch queues, offline enrichment, RAG/analysis caching, weekly drift canaries.

"""
    # Save
    path = outdir / "enhanced_executive_summary.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary)

    # Exports
    reporter.export_to_csv(results, models, performance_by_model, outdir)
    reporter.export_to_json(results, models, performance_by_model, language_results, owasp_results, outdir)

    return str(path)


def generate_enhanced_unified_executive_summary(
        results: List,
        models: List[str],
        suite_name: str,
        outdir: Path,
        charts: Optional[Dict[str, str]] = None,
        enhanced_metrics: Optional[Dict] = None,
        language_results: Optional[Dict] = None,
        owasp_results: Optional[Dict] = None,
        total_cost: float = 0.0,
        accuracy_threshold: float = 0.70,
        active_profile: UseCaseProfile = RAPID_RESPONSE
) -> str:
    # Keep alias; accuracy_threshold is superseded by active_profile.min_accuracy for gates,
    # but we pass it through to keep backward compatibility expectations.
    return generate_unified_executive_summary(
        results=results,
        models=models,
        suite_name=suite_name,
        outdir=outdir,
        charts=charts,
        enhanced_metrics=enhanced_metrics,
        language_results=language_results,
        owasp_results=owasp_results,
        total_cost=total_cost,
        active_profile=active_profile
    )


# Backward-compat wrappers
def generate_basic_executive_summary(results: List, models: List[str], suite_name: str, outdir: Path, **kwargs) -> str:
    return generate_unified_executive_summary(results, models, suite_name, outdir, **kwargs)


def generate_quality_first_executive_summary(results: List, models: List[str], suite_name: str, outdir: Path,
                                             **kwargs) -> str:
    return generate_unified_executive_summary(results, models, suite_name, outdir, **kwargs)


def generate_comprehensive_executive_summary(results: List, models: List[str], suite_name: str, outdir: Path,
                                             **kwargs) -> str:
    return generate_unified_executive_summary(results, models, suite_name, outdir, **kwargs)


def replace_multiple_executive_summaries(results: List, models: List[str], suite_name: str, outdir: Path,
                                         **kwargs) -> str:
    return generate_unified_executive_summary(results=results, models=models, suite_name=suite_name, outdir=outdir,
                                              **kwargs)


# -------------------------------
# Engineering Technical Report (improved)
# -------------------------------

def generate_engineering_technical_report(
        results: List,
        models: List[str],
        suite_name: str,
        outdir: Path,
        total_cost: float = 0.0,
        active_profile: UseCaseProfile = RAPID_RESPONSE
) -> str:
    """
    Engineering report with Wilson/Bootstrap CIs, realistic gates per use-case, and
    explicit throughput semantics (per-worker theoretical).
    """
    per_model = _partition_results_by_model(results, models)
    technical_metrics: Dict[str, Dict[str, Any]] = {}
    for m in models:
        if per_model[m]:
            technical_metrics[m] = _calculate_technical_metrics(m, per_model[m])

    if not technical_metrics:
        return "No valid results for technical analysis"

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    total_tests = sum(tm['total_tests'] for tm in technical_metrics.values())

    # Build report with more actionable structure
    report = f"""# LLM Security Benchmark — Technical Analysis Report

**Generated:** {timestamp}  
**Suite:** {suite_name}  
**Models Analyzed:** {len(models)}  
**Total Tests:** {total_tests}  
**Total Investment:** ${total_cost:.4f}

## Objective
Security-focused evaluation for both **{RAPID_RESPONSE.name}** (time-sensitive) and **{IN_DEPTH.name}** (deep) use-cases.

- Performance: latency distribution, reliability
- Statistical rigor: Wilson CIs (proportions), Bootstrap CIs (means), sample-size adequacy
- Cost efficiency: token utilization, cost per correct
- Gates: per-use-case thresholds and Go/No-Go

## TL;DR Recommendations

"""

    # Add actionable recommendations at the top
    qualified_rapid = []
    qualified_indepth = []
    for m, mt in technical_metrics.items():
        rr_cost_ok = True if RAPID_RESPONSE.max_cost_per_test is None else (mt['avg_cost'] <= RAPID_RESPONSE.max_cost_per_test)
        if (mt['avg_accuracy'] >= RAPID_RESPONSE.min_accuracy and
                mt['success_rate'] >= RAPID_RESPONSE.min_success_rate and
                mt['p95_latency'] <= RAPID_RESPONSE.max_p95_latency_s and
                rr_cost_ok):
            qualified_rapid.append(m)
        if (mt['avg_accuracy'] >= IN_DEPTH.min_accuracy and
                mt['success_rate'] >= IN_DEPTH.min_success_rate and
                mt['p95_latency'] <= IN_DEPTH.max_p95_latency_s):
            qualified_indepth.append(m)

    if qualified_rapid:
        report += f"**For Rapid Response:** {', '.join(qualified_rapid)}\n"
    else:
        # Find best candidates that nearly meet criteria
        near_candidates = sorted(
            [(m, mt) for m, mt in technical_metrics.items()],
            key=lambda x: (x[1]['avg_accuracy'], -x[1]['p95_latency']),
            reverse=True
        )[:3]
        report += f"**For Rapid Response (best candidates):** {', '.join([m for m, _ in near_candidates])}\n"

    if qualified_indepth:
        report += f"**For In-Depth Analysis:** {', '.join(qualified_indepth)}\n"
    else:
        best_accuracy = sorted(
            [(m, mt) for m, mt in technical_metrics.items()],
            key=lambda x: x[1]['avg_accuracy'],
            reverse=True
        )[:2]
        report += f"**For In-Depth Analysis (highest accuracy):** {', '.join([m for m, _ in best_accuracy])}\n"

    report += """
## Model Performance Summary

| Model | n | Success (95% CI) | Avg Acc (95% CI) | P95 Lat (s) | Cost/Test | Avg Tokens |
|------|--:|-------------------|------------------|------------:|----------:|----------:|"""

    for m, mt in sorted(technical_metrics.items(), key=lambda x: x[1]['avg_accuracy'], reverse=True):
        s_lo, s_hi = mt['success_ci']
        a_lo, a_hi = mt['acc_ci']
        report += f"\n| {m} | {mt['total_tests']} | {mt['success_rate']:.1%} [{s_lo:.2f}, {s_hi:.2f}] | {mt['avg_accuracy']:.1%} [{a_lo:.2f}, {a_hi:.2f}] | {mt['p95_latency']:.2f} | ${mt['avg_cost']:.5f} | {mt['avg_tokens']:,} |"

    report += """

### Latency Distribution

| Model | Mean | Median | P95 | P99 | Std Dev | Theoretical Throughput/Worker (req/h) |
|------|-----:|------:|---:|---:|------:|-------------------------------------:|"""

    for m, mt in technical_metrics.items():
        tput = (3600.0 / mt['avg_latency']) if mt['avg_latency'] > 0 else 0.0
        report += f"\n| {m} | {mt['avg_latency']:.2f}s | {mt['median_latency']:.2f}s | {mt['p95_latency']:.2f}s | {mt['p99_latency']:.2f}s | {mt['latency_std']:.2f}s | {tput:.0f} |"

    # ---- Detailed time-sensitive analysis (by complexity) ----
    tsa = _summarize_time_sensitive(results, models)
    def _fmt_row(m, row):
        return f"| {m} | {row['n']} | {row['success']:.1%} | {row['acc']:.1%} | {row['p95']:.2f} | ${row['cost/test']:.5f} |"

    report += "\n\n## Detailed Time-Sensitive Analysis"
    for bucket in ('simple', 'moderate', 'high'):
        report += f"\n\n### {bucket.title()} Complexity"
        report += "\n\n| Model | n | Success | Acc | P95 (s) | Cost/Test |"
        report += "\n|------|--:|--------:|----:|--------:|----------:|"
        rows = tsa.get(bucket, {})
        # Rank: high acc, then low P95, then low cost
        for m in sorted(rows.keys(), key=lambda k: (-rows[k]['acc'], rows[k]['p95'], rows[k]['cost/test'])):
            report += "\n" + _fmt_row(m, rows[m])

    report += f"""

## Gates & Readiness (per-use-case)

**{RAPID_RESPONSE.name} Gate:** Acc ≥ {RAPID_RESPONSE.min_accuracy:.0%}, Success ≥ {RAPID_RESPONSE.min_success_rate:.0%}, P95 ≤ {RAPID_RESPONSE.max_p95_latency_s:.0f}s{f", Cost/Test ≤ ${RAPID_RESPONSE.max_cost_per_test:.4f}" if RAPID_RESPONSE.max_cost_per_test else ""}  
**{IN_DEPTH.name} Gate:** Acc ≥ {IN_DEPTH.min_accuracy:.0%}, Success ≥ {IN_DEPTH.min_success_rate:.0%}, P95 ≤ {IN_DEPTH.max_p95_latency_s:.0f}s

| Model | Rapid Response | Margin | In-Depth | Margin |
|------|:--------------:|:------:|:--------:|:------:|"""

    for m, mt in technical_metrics.items():
        rr_acc = mt['avg_accuracy'] >= RAPID_RESPONSE.min_accuracy
        rr_succ = mt['success_rate'] >= RAPID_RESPONSE.min_success_rate
        rr_lat = mt['p95_latency'] <= RAPID_RESPONSE.max_p95_latency_s
        rr_cost = True if RAPID_RESPONSE.max_cost_per_test is None else (mt['avg_cost'] <= RAPID_RESPONSE.max_cost_per_test)
        rr_pass = rr_acc and rr_succ and rr_lat and rr_cost
        
        rr_margin_bits = [f"acc {mt['avg_accuracy'] - RAPID_RESPONSE.min_accuracy:+.1%}",
                          f"p95 {RAPID_RESPONSE.max_p95_latency_s - mt['p95_latency']:+.1f}s"]
        if RAPID_RESPONSE.max_cost_per_test is not None:
            rr_margin_bits.append(f"cost {(RAPID_RESPONSE.max_cost_per_test - mt['avg_cost']):+.5f}")
        rr_margin = ", ".join(rr_margin_bits)

        id_acc = mt['avg_accuracy'] >= IN_DEPTH.min_accuracy
        id_succ = mt['success_rate'] >= IN_DEPTH.min_success_rate
        id_lat = mt['p95_latency'] <= IN_DEPTH.max_p95_latency_s
        id_pass = id_acc and id_succ and id_lat
        id_margin = f"acc {mt['avg_accuracy'] - IN_DEPTH.min_accuracy:+.1%}"

        # Detailed failure reasons
        rr_bits = []
        rr_bits.append("acc✅" if rr_acc else "acc❌")
        rr_bits.append("p95✅" if rr_lat else "p95❌")
        if RAPID_RESPONSE.max_cost_per_test is not None:
            rr_bits.append("cost✅" if rr_cost else "cost❌")
        rr_status = " ".join(rr_bits) if not rr_pass else "✅"
        
        id_status = "✅" if id_pass else "❌"

        report += f"\n| {m} | {rr_status} | {rr_margin} | {id_status} | {id_margin} |"

    report += """

## Cost & Token Utilization

| Model | Total Cost | Cost/Test | Cost/Correct (Acc≥0.8) | Token Efficiency (Acc/AvgTokens) |
|------|-----------:|----------:|-----------------------:|----------------------------------:|"""

    for m, mt in sorted(technical_metrics.items(), key=lambda x: x[1]['cost_efficiency'], reverse=True):
        te = (mt['avg_accuracy'] / mt['avg_tokens']) if mt['avg_tokens'] > 0 else 0.0
        report += f"\n| {m} | ${mt['total_cost']:.4f} | ${mt['avg_cost']:.5f} | ${mt['cost_per_correct']:.5f} | {te:.6f} |"

    # Methodology & next steps
    report += f"""

## Methodology Notes
- **Success** = non-error response (schema-valid)  
- **Accuracy** = normalized score [0..1] consistently calculated across all results
- **Latency** = end-to-end elapsed_s per request  
- **CIs**: Wilson (proportions), Bootstrap (means, deterministic seed)
- **Throughput** reported as theoretical per worker (no concurrency factor)

**Sample Size Adequacy**
- Rapid Response recommended n ≥ {RAPID_RESPONSE.min_n} per model
- In-Depth recommended n ≥ {IN_DEPTH.min_n} per model

## Deployment Recommendations
- **Rapid path**: Choose models meeting RAPID_RESPONSE gates; implement response caching; pre-tokenize common patterns
- **In-depth**: Choose highest accuracy models for batch processing; implement RAG on repo indexes; schedule weekly drift monitoring
- **Cost optimization**: Consider a low-cost, high-throughput model for high-volume, lower-criticality screening
- **Ops**: Pin model versions; implement circuit breakers; monitor P95 latency closely

---
Generated by the Rapticore Technical Analysis Engine.
"""

    tech_path = outdir / "technical_analysis_report.md"
    with open(tech_path, "w", encoding="utf-8") as f:
        f.write(report)
    return str(tech_path)


def _calculate_technical_metrics(model: str, results: List) -> Dict[str, Any]:
    total_tests = len(results)
    oks = [bool(getattr(r, 'ok', False)) for r in results]
    successful_tests = sum(oks)
    success_rate = (successful_tests / total_tests) if total_tests > 0 else 0.0
    success_ci = _wilson_ci(successful_tests, total_tests)

    # Consistent accuracy calculation (all results, including failures as 0.0)
    scores_all = [float(getattr(r, 'score', 0.0) or 0.0) for r in results]
    avg_accuracy = float(np.mean(scores_all)) if scores_all else 0.0
    acc_ci = _bootstrap_ci(scores_all, 0.95) if scores_all else (0.0, 0.0)
    median_accuracy = float(np.median(scores_all)) if scores_all else 0.0
    accuracy_std = float(np.std(scores_all)) if scores_all else 0.0

    # Latency (only on successful requests)
    successful = [r for r, ok in zip(results, oks) if ok]
    latencies = [float(getattr(r, 'elapsed_s', 0.0) or 0.0) for r in successful]
    avg_latency = float(np.mean(latencies)) if latencies else 0.0
    median_latency = float(np.median(latencies)) if latencies else 0.0
    p95_latency = float(np.percentile(latencies, 95)) if latencies else 0.0
    p99_latency = float(np.percentile(latencies, 99)) if latencies else 0.0
    latency_std = float(np.std(latencies)) if latencies else 0.0

    # Cost
    costs = [float(getattr(r, 'cost_usd', 0.0) or 0.0) for r in results if getattr(r, 'cost_usd', None) is not None]
    total_cost = float(np.sum(costs)) if costs else 0.0
    avg_cost = (total_cost / total_tests) if total_tests else 0.0

    # "Correct" threshold for cost/correct
    correct_results = sum(1 for s in scores_all if s >= CORRECT_THRESH)
    cost_per_correct = (total_cost / correct_results) if correct_results > 0 else float('inf')
    cost_efficiency = (correct_results / total_cost) if total_cost > 0 else 0.0

    # Tokens
    in_tok = [int(getattr(r, 'input_tokens', 0) or 0) for r in results]
    out_tok = [int(getattr(r, 'output_tokens', 0) or 0) for r in results]
    avg_input_tokens = int(np.mean(in_tok)) if in_tok else 0
    avg_output_tokens = int(np.mean(out_tok)) if out_tok else 0
    total_tokens = int(np.sum(in_tok) + np.sum(out_tok))
    avg_tokens = avg_input_tokens + avg_output_tokens

    return {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'success_rate': success_rate,
        'success_ci': success_ci,
        'avg_accuracy': avg_accuracy,
        'acc_ci': acc_ci,
        'median_accuracy': median_accuracy,
        'accuracy_std': accuracy_std,
        'avg_latency': avg_latency,
        'median_latency': median_latency,
        'p95_latency': p95_latency,
        'p99_latency': p99_latency,
        'latency_std': latency_std,
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'cost_per_correct': cost_per_correct,
        'cost_efficiency': cost_efficiency,
        'avg_input_tokens': avg_input_tokens,
        'avg_output_tokens': avg_output_tokens,
        'total_tokens': total_tokens,
        'avg_tokens': avg_tokens,
    }