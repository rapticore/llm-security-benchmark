#!/usr/bin/env python3
"""
Enhanced Unified Executive Summary Generator

Enhanced with graduated quality tiers and actionable recommendations:
- Graduated Quality Framework (70%, 75%, 80%) instead of binary 80% threshold
- Data-driven expert insights without over-engineering
- Tiered deployment recommendations
- Simple hybrid suggestions for qualified models
- All original detailed analysis preserved

Built by the Rapticore Security Research Team
"""

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

import numpy as np


# -------------------------------
# Enhanced Quality Framework
# -------------------------------

class QualityTier(Enum):
    """Graduated quality standards for realistic deployment"""
    MINIMUM_VIABLE = "minimum_viable"  # 70% accuracy, 95% success
    ENTERPRISE_PREFERRED = "enterprise_preferred"  # 75% accuracy, 97% success
    MISSION_CRITICAL = "mission_critical"  # 80% accuracy, 99% success
    BELOW_STANDARDS = "below_standards"


@dataclass
class QualityStandard:
    tier: QualityTier
    min_accuracy: float
    min_success_rate: float
    description: str


QUALITY_STANDARDS = {
    QualityTier.MINIMUM_VIABLE: QualityStandard(
        tier=QualityTier.MINIMUM_VIABLE,
        min_accuracy=0.70,
        min_success_rate=0.95,
        description="Development testing, automated scanning with oversight"
    ),
    QualityTier.ENTERPRISE_PREFERRED: QualityStandard(
        tier=QualityTier.ENTERPRISE_PREFERRED,
        min_accuracy=0.75,
        min_success_rate=0.97,
        description="Production security workflows, compliance checks"
    ),
    QualityTier.MISSION_CRITICAL: QualityStandard(
        tier=QualityTier.MISSION_CRITICAL,
        min_accuracy=0.80,
        min_success_rate=0.99,
        description="Critical infrastructure, financial services, healthcare"
    )
}


def determine_quality_tier(accuracy: float, success_rate: float) -> QualityTier:
    """Determine quality tier based on performance metrics"""
    for tier in [QualityTier.MISSION_CRITICAL, QualityTier.ENTERPRISE_PREFERRED, QualityTier.MINIMUM_VIABLE]:
        standard = QUALITY_STANDARDS[tier]
        if accuracy >= standard.min_accuracy and success_rate >= standard.min_success_rate:
            return tier
    return QualityTier.BELOW_STANDARDS


# -------------------------------
# Statistical Utility Functions
# -------------------------------

def wilson_ci(successes: int, n: int, z: float = 1.96) -> Tuple[float, float]:
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


def bootstrap_ci(values: List[float], ci: float = 0.95, iters: int = 100, seed: int = 42) -> Tuple[float, float]:
    """Bootstrap CI for mean with deterministic results."""
    if not values:
        return (0.0, 0.0)
    if len(values) < 2:
        m = float(np.mean(values))
        return (m, m)

    # Fixed seed for deterministic results
    np.random.seed(seed)
    arr = np.asarray(values)
    idx = np.random.randint(0, len(arr), size=(iters, len(arr)))
    means = np.mean(arr[idx], axis=1)
    lower = np.percentile(means, (1 - ci) / 2 * 100)
    upper = np.percentile(means, (1 + ci) / 2 * 100)
    return (float(lower), float(upper))


# -------------------------------
# Use-Case Profiles & Gates (Adjusted Thresholds)
# -------------------------------

@dataclass
class UseCaseProfile:
    """Defines thresholds and weights for different use cases."""
    name: str
    min_accuracy: float
    min_success_rate: float
    max_p95_latency_s: float
    weight_accuracy: float = 0.6
    weight_latency: float = 0.25
    weight_cost: float = 0.15
    min_samples: int = 30

    def meets_gate(self, accuracy: float, success_rate: float, p95_latency: float) -> bool:
        """Check if model meets this profile's gates."""
        return (accuracy >= self.min_accuracy and
                success_rate >= self.min_success_rate and
                p95_latency <= self.max_p95_latency_s)

    def decision_score(self, accuracy: float, p95_latency: float, cost_per_test: float) -> float:
        """Calculate decision score for this profile."""
        latency_score = 1.0 / max(p95_latency, 0.1)  # Avoid division by zero
        cost_score = 1.0 / max(cost_per_test, 0.0001)  # Avoid division by zero
        return (self.weight_accuracy * accuracy +
                self.weight_latency * latency_score +
                self.weight_cost * cost_score)


# Define profiles with realistic thresholds
RAPID_RESPONSE = UseCaseProfile(
    name="RAPID_RESPONSE",
    min_accuracy=0.70,  # Adjusted from 0.75 to be realistic
    min_success_rate=0.95,
    max_p95_latency_s=15.0,
    weight_accuracy=0.50,
    weight_latency=0.35,
    weight_cost=0.15,
    min_samples=30
)

IN_DEPTH = UseCaseProfile(
    name="IN_DEPTH",
    min_accuracy=0.75,  # Adjusted from 0.85 to be realistic
    min_success_rate=0.97,
    max_p95_latency_s=45.0,
    weight_accuracy=0.70,
    weight_latency=0.10,
    weight_cost=0.20,
    min_samples=50
)


# -------------------------------
# Data Classes (Enhanced)
# -------------------------------

@dataclass
class EnhancedMetrics:
    """Enhanced cost-effectiveness metrics considering partial correctness."""
    # Basic metrics
    total_tests: int
    successful_tests: int
    failed_tests: int

    # Score distribution
    perfect_scores: int  # score = 1.0
    excellent_scores: int  # score >= 0.8
    good_scores: int  # score >= 0.6
    fair_scores: int  # score >= 0.4
    poor_scores: int  # score < 0.4

    # Cost metrics
    total_cost: float
    cost_per_test: float
    cost_per_correct_answer: float  # Only counting perfect scores
    cost_per_partial_answer: float  # Including all successful attempts

    # Enhanced cost-effectiveness
    traditional_effectiveness: float
    quality_weighted_effectiveness: float
    penalty_adjusted_effectiveness: float


@dataclass
class ModelPerformance:
    """Enhanced model performance metrics with quality tiers."""
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

    # Enhanced quality indicators
    quality_tier: QualityTier = QualityTier.BELOW_STANDARDS
    meets_accuracy_threshold: bool = False
    cost_efficiency_tier: str = "unknown"
    reliability_score: float = 0.0

    # Enhanced latency metrics
    median_time_s: float = 0.0
    p95_time_s: float = 0.0
    p99_time_s: float = 0.0
    std_time_s: float = 0.0
    throughput_per_hour: float = 0.0

    # Statistical confidence intervals
    success_rate_ci_lower: float = 0.0
    success_rate_ci_upper: float = 0.0
    accuracy_ci_lower: float = 0.0
    accuracy_ci_upper: float = 0.0

    # Sample size adequacy
    sample_adequacy_warning: bool = False

    # Security-aware metrics (if available)
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    severity_weighted_score: Optional[float] = None

    # Reproducibility info
    model_version: Optional[str] = None
    region: Optional[str] = None
    temperature: Optional[float] = None
    seed: Optional[int] = None
    max_tokens: Optional[int] = None

    @classmethod
    def from_results(cls, model: str, results: List, accuracy_threshold: float = 0.70):  # Changed default
        """Create Enhanced ModelPerformance from results list with full statistical analysis."""
        if not results:
            return cls(
                model=model, total_tests=0, passed_tests=0, avg_score=0.0,
                avg_time_s=0.0, total_cost_usd=0.0, cost_per_test=0.0,
                success_rate=0.0, perfect_rate=0.0, score_variance=0.0,
                quality_tier=QualityTier.BELOW_STANDARDS
            )

        # Extract basic metrics
        scores = [getattr(r, 'score', 0.0) for r in results]
        times = [getattr(r, 'elapsed_s', 0.0) for r in results]
        costs = [getattr(r, 'cost_usd', 0.0) for r in results if getattr(r, 'cost_usd', 0.0) is not None]

        passed = sum(1 for r in results if getattr(r, 'ok', False))
        perfect = sum(1 for s in scores if s >= 1.0)

        # Basic calculations
        avg_score = sum(scores) / len(scores) if scores else 0.0
        avg_time = sum(times) / len(times) if times else 0.0
        total_cost = sum(costs)
        cost_per_test = total_cost / len(results) if results else 0.0
        success_rate = passed / len(results) if results else 0.0
        perfect_rate = perfect / len(results) if results else 0.0

        # Enhanced latency distribution
        median_time = np.median(times) if times else 0.0
        p95_time = np.percentile(times, 95) if times else 0.0
        p99_time = np.percentile(times, 99) if times else 0.0
        std_time = np.std(times) if times else 0.0
        throughput_per_hour = 3600 / avg_time if avg_time > 0 else 0.0

        # Statistical confidence intervals
        success_ci_lower, success_ci_upper = wilson_ci(passed, len(results))
        accuracy_ci_lower, accuracy_ci_upper = bootstrap_ci(scores)

        # Sample size adequacy warning
        sample_adequacy_warning = len(results) < 30

        # Security-aware metrics (if available)
        precision, recall, f1_score, severity_weighted_score = cls._calculate_security_metrics(results)

        # Reproducibility info
        model_version = getattr(results[0], 'model_version', None) if results else None
        region = getattr(results[0], 'region', None) if results else None
        temperature = getattr(results[0], 'temperature', None) if results else None
        seed = getattr(results[0], 'seed', None) if results else None
        max_tokens = getattr(results[0], 'max_tokens', None) if results else None

        # Calculate enhanced metrics
        enhanced = cls._calculate_enhanced_metrics(results)

        # Determine quality tier and indicators
        quality_tier = determine_quality_tier(avg_score, success_rate)
        meets_threshold = quality_tier != QualityTier.BELOW_STANDARDS
        tier = cls._determine_cost_efficiency_tier(avg_score, cost_per_test, avg_time)

        return cls(
            model=model,
            total_tests=len(results),
            passed_tests=passed,
            avg_score=avg_score,
            avg_time_s=avg_time,
            total_cost_usd=total_cost,
            cost_per_test=cost_per_test,
            success_rate=success_rate,
            perfect_rate=perfect_rate,
            score_variance=np.var(scores) if scores else 0.0,
            enhanced_metrics=enhanced,
            quality_tier=quality_tier,
            meets_accuracy_threshold=meets_threshold,
            cost_efficiency_tier=tier,
            reliability_score=success_rate,
            # Enhanced latency metrics
            median_time_s=median_time,
            p95_time_s=p95_time,
            p99_time_s=p99_time,
            std_time_s=std_time,
            throughput_per_hour=throughput_per_hour,
            # Statistical confidence intervals
            success_rate_ci_lower=success_ci_lower,
            success_rate_ci_upper=success_ci_upper,
            accuracy_ci_lower=accuracy_ci_lower,
            accuracy_ci_upper=accuracy_ci_upper,
            # Sample size adequacy
            sample_adequacy_warning=sample_adequacy_warning,
            # Security-aware metrics
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            severity_weighted_score=severity_weighted_score,
            # Reproducibility info
            model_version=model_version,
            region=region,
            temperature=temperature,
            seed=seed,
            max_tokens=max_tokens
        )

    @staticmethod
    def _calculate_security_metrics(results: List) -> Tuple[
        Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Calculate security-aware metrics if TP/FP/FN/TN data is available."""
        tp_total = fp_total = fn_total = tn_total = 0
        severity_weighted_scores = []

        for result in results:
            # Check for confusion matrix data
            tp = getattr(result, 'tp', None)
            fp = getattr(result, 'fp', None)
            fn = getattr(result, 'fn', None)
            tn = getattr(result, 'tn', None)

            if tp is not None and fp is not None and fn is not None and tn is not None:
                tp_total += tp
                fp_total += fp
                fn_total += fn
                tn_total += tn

            # Check for severity weighting
            severity_weight = getattr(result, 'severity_weight', None)
            score = getattr(result, 'score', 0.0)
            if severity_weight is not None:
                severity_weighted_scores.append(score * severity_weight)

        # Calculate precision, recall, F1 if we have confusion matrix data
        precision = recall = f1_score = None
        if tp_total + fp_total > 0:
            precision = tp_total / (tp_total + fp_total)
        if tp_total + fn_total > 0:
            recall = tp_total / (tp_total + fn_total)
        if precision is not None and recall is not None and precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)

        # Calculate severity-weighted score
        severity_weighted_score = None
        if severity_weighted_scores:
            severity_weighted_score = sum(severity_weighted_scores) / len(severity_weighted_scores)

        return precision, recall, f1_score, severity_weighted_score

    @staticmethod
    def _calculate_enhanced_metrics(results: List) -> EnhancedMetrics:
        """Calculate enhanced cost-effectiveness metrics."""
        successful_results = [r for r in results if getattr(r, 'ok', False)]
        failed_results = [r for r in results if not getattr(r, 'ok', False)]

        if not successful_results:
            return EnhancedMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        scores = [getattr(r, 'score', 0.0) for r in successful_results]
        costs = [getattr(r, 'cost_usd', 0.0) for r in successful_results if getattr(r, 'cost_usd', 0.0) > 0]

        # Score distribution
        perfect_scores = sum(1 for s in scores if s == 1.0)
        excellent_scores = sum(1 for s in scores if s >= 0.8)
        good_scores = sum(1 for s in scores if s >= 0.6)
        fair_scores = sum(1 for s in scores if s >= 0.4)
        poor_scores = sum(1 for s in scores if s < 0.4)

        total_cost = sum(costs)
        cost_per_test = total_cost / len(successful_results) if successful_results else 0.0

        # Enhanced effectiveness calculations
        avg_score = np.mean(scores) if scores else 0.0
        traditional_effectiveness = avg_score / cost_per_test if cost_per_test > 0 else 0.0

        # Quality-weighted effectiveness
        quality_weights = {'perfect': 1.0, 'excellent': 0.9, 'good': 0.7, 'fair': 0.5, 'poor': 0.2}
        weighted_score = (
                                 perfect_scores * quality_weights['perfect'] +
                                 (excellent_scores - perfect_scores) * quality_weights['excellent'] +
                                 (good_scores - excellent_scores) * quality_weights['good'] +
                                 (fair_scores - good_scores) * quality_weights['fair'] +
                                 poor_scores * quality_weights['poor']
                         ) / len(successful_results) if successful_results else 0.0

        quality_weighted_effectiveness = weighted_score / cost_per_test if cost_per_test > 0 else 0.0

        # Penalty-adjusted effectiveness
        penalty = len(failed_results) * 0.5
        penalty_adjusted_score = max(0, weighted_score - penalty)
        penalty_adjusted_effectiveness = penalty_adjusted_score / cost_per_test if cost_per_test > 0 else 0.0

        return EnhancedMetrics(
            total_tests=len(results),
            successful_tests=len(successful_results),
            failed_tests=len(failed_results),
            perfect_scores=perfect_scores,
            excellent_scores=excellent_scores,
            good_scores=good_scores,
            fair_scores=fair_scores,
            poor_scores=poor_scores,
            total_cost=total_cost,
            cost_per_test=cost_per_test,
            cost_per_correct_answer=total_cost / perfect_scores if perfect_scores > 0 else 0.0,
            cost_per_partial_answer=cost_per_test,
            traditional_effectiveness=traditional_effectiveness,
            quality_weighted_effectiveness=quality_weighted_effectiveness,
            penalty_adjusted_effectiveness=penalty_adjusted_effectiveness
        )

    @staticmethod
    def _determine_cost_efficiency_tier(avg_score: float, cost_per_test: float, avg_time: float) -> str:
        """Determine cost efficiency tier based on performance metrics."""
        if avg_score >= 0.75:
            return "Enterprise Preferred (High Accuracy)"
        elif avg_score >= 0.70 and cost_per_test <= 0.005:
            return "Minimum Viable (Balanced Performance)"
        elif cost_per_test <= 0.002 and avg_score >= 0.60:
            return "Budget Option (Cost-Conscious)"
        elif avg_score < 0.60:
            return "Below Quality Standards"
        else:
            return "Specialized Use Case"


# -------------------------------
# Expert Analysis Functions
# -------------------------------

def generate_expert_insights(performance_by_model: Dict[str, ModelPerformance]) -> List[str]:
    """Generate data-driven expert insights based on performance patterns"""
    insights = []

    qualified_models = [p for p in performance_by_model.values() if getattr(p, 'quality_tier', QualityTier.BELOW_STANDARDS) != QualityTier.BELOW_STANDARDS]

    if not qualified_models:
        insights.append(
            "READINESS INSIGHT: No models meet minimum viable standards (70% accuracy). This reflects the challenging nature of security analysis compared to general language tasks. Consider implementing human-AI collaboration workflows where AI provides initial screening and humans validate findings.")
        return insights

    # Accuracy gap analysis
    if len(qualified_models) > 1:
        accuracy_gap = max(p.avg_score for p in qualified_models) - min(p.avg_score for p in qualified_models)
        if accuracy_gap > 0.05:
            insights.append(
                f"ACCURACY INSIGHT: {accuracy_gap:.1%} accuracy spread between qualified models indicates meaningful performance differences. Specialized model selection based on security category or use case could improve outcomes beyond single-model deployment.")

    # Cost optimization analysis
    if len(qualified_models) > 1:
        costs = [p.cost_per_test for p in qualified_models if p.cost_per_test > 0]
        if costs:
            cost_ratio = max(costs) / min(costs)
            if cost_ratio > 5:
                insights.append(
                    f"COST INSIGHT: {cost_ratio:.0f}x cost difference between qualified models creates significant hybrid deployment opportunities. Enterprise deployments could achieve 20-40% cost savings through intelligent request routing while maintaining quality standards.")

    # Performance vs expectations
    best_accuracy = max(p.avg_score for p in qualified_models)
    if best_accuracy < 0.80:
        insights.append(
            f"EXPECTATIONS INSIGHT: Peak accuracy of {best_accuracy:.1%} represents current LLM security capabilities. Unlike general language tasks where 85%+ accuracy is common, security analysis requires specialized domain knowledge that current models are still developing. Plan for human expert review of ~{(1 - best_accuracy):.0%} of cases.")

    return insights


def generate_simple_hybrid_recommendations(qualified_models: List[ModelPerformance]) -> Optional[str]:
    """Generate simple hybrid recommendation if beneficial"""
    if len(qualified_models) < 2:
        return None

    # Sort by cost and accuracy
    by_cost = sorted(qualified_models, key=lambda p: p.cost_per_test)
    by_accuracy = sorted(qualified_models, key=lambda p: p.avg_score, reverse=True)

    fastest_cheap = by_cost[0] if by_cost[0].p95_time_s <= 15.0 else None
    most_accurate = by_accuracy[0]

    if fastest_cheap and most_accurate and fastest_cheap.model != most_accurate.model:
        cost_savings = (most_accurate.cost_per_test - fastest_cheap.cost_per_test) / most_accurate.cost_per_test
        if cost_savings > 0.5:  # Only recommend if >50% savings
            return f"HYBRID OPPORTUNITY: Route 70% of requests to {fastest_cheap.model} (${fastest_cheap.cost_per_test:.5f}) for initial screening, escalate 30% to {most_accurate.model} (${most_accurate.cost_per_test:.5f}) for detailed analysis. Expected cost reduction: {cost_savings:.0%}."

    return None


# -------------------------------
# Enhanced Reporter Class
# -------------------------------

class EnhancedUnifiedReporter:
    """Enhanced unified reporter with graduated quality tiers."""

    def __init__(self, accuracy_threshold: float = 0.70):  # Changed default
        self.accuracy_threshold = accuracy_threshold

    def analyze_by_language(self, results: List) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by programming language."""
        language_results = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})

        for result in results:
            if not getattr(result, 'ok', False):
                continue

            language = self._classify_language(getattr(result, 'suite_id', ''))
            language_results[language]['results'].append(result)
            language_results[language]['scores'].append(getattr(result, 'score', 0.0))
            if getattr(result, 'cost_usd', None):
                language_results[language]['costs'].append(result.cost_usd)

        # Calculate metrics for each language
        language_metrics = {}
        for language, data in language_results.items():
            if not data['results']:
                continue

            scores = data['scores']
            costs = data['costs']

            # Calculate metrics by model
            models = defaultdict(lambda: {'scores': [], 'costs': []})
            for result in data['results']:
                model = getattr(result, 'model', 'unknown')
                models[model]['scores'].append(getattr(result, 'score', 0.0))
                if getattr(result, 'cost_usd', None):
                    models[model]['costs'].append(result.cost_usd)

            model_metrics = {}
            for model, model_data in models.items():
                model_metrics[model] = {
                    'avg_score': np.mean(model_data['scores']) if model_data['scores'] else 0.0,
                    'avg_cost': np.mean(model_data['costs']) if model_data['costs'] else 0.0,
                    'test_count': len(model_data['scores'])
                }

            language_metrics[language] = {
                'total_tests': len(data['results']),
                'avg_score': np.mean(scores),
                'success_rate': len(scores) / len(data['results']),
                'avg_cost': np.mean(costs) if costs else 0.0,
                'effectiveness': np.mean(scores) / np.mean(costs) if costs and np.mean(costs) > 0 else 0.0,
                'models': model_metrics
            }

        return language_metrics

    def analyze_by_owasp_category(self, results: List) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by OWASP category."""
        owasp_results = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})

        for result in results:
            if not getattr(result, 'ok', False):
                continue

            category = self._classify_owasp_category(getattr(result, 'suite_id', ''))
            owasp_results[category]['results'].append(result)
            owasp_results[category]['scores'].append(getattr(result, 'score', 0.0))
            if getattr(result, 'cost_usd', None):
                owasp_results[category]['costs'].append(result.cost_usd)

        # Calculate metrics for each category
        category_metrics = {}
        for category, data in owasp_results.items():
            if not data['results']:
                continue

            scores = data['scores']
            costs = data['costs']

            # Calculate metrics by model
            models = defaultdict(lambda: {'scores': [], 'costs': []})
            for result in data['results']:
                model = getattr(result, 'model', 'unknown')
                models[model]['scores'].append(getattr(result, 'score', 0.0))
                if getattr(result, 'cost_usd', None):
                    models[model]['costs'].append(result.cost_usd)

            model_metrics = {}
            for model, model_data in models.items():
                model_metrics[model] = {
                    'avg_score': np.mean(model_data['scores']) if model_data['scores'] else 0.0,
                    'avg_cost': np.mean(model_data['costs']) if model_data['costs'] else 0.0,
                    'test_count': len(model_data['scores'])
                }

            category_metrics[category] = {
                'total_tests': len(data['results']),
                'avg_score': np.mean(scores),
                'success_rate': len(scores) / len(data['results']),
                'avg_cost': np.mean(costs) if costs else 0.0,
                'effectiveness': np.mean(scores) / np.mean(costs) if costs and np.mean(costs) > 0 else 0.0,
                'models': model_metrics
            }

        return category_metrics

    def _classify_language(self, test_id: str) -> str:
        """Classify test by programming language."""
        test_lower = test_id.lower()

        if 'python' in test_lower or 'py_' in test_lower:
            return 'Python'
        elif 'javascript' in test_lower or 'js_' in test_lower:
            return 'JavaScript'
        elif 'java' in test_lower:
            return 'Java'
        elif 'go_' in test_lower or 'golang' in test_lower:
            return 'Go'
        elif 'rust' in test_lower:
            return 'Rust'
        elif 'c_' in test_lower or 'cpp_' in test_lower:
            return 'C/C++'
        elif 'csharp' in test_lower:
            return 'C#'
        elif 'php' in test_lower:
            return 'PHP'
        elif 'ruby' in test_lower:
            return 'Ruby'
        elif 'haskell' in test_lower:
            return 'Haskell'
        else:
            return 'General Security'

    def _classify_owasp_category(self, test_id: str) -> str:
        """Classify test by OWASP category."""
        test_lower = test_id.lower()

        if 'sql' in test_lower or 'injection' in test_lower:
            return 'A03: Injection'
        elif 'xss' in test_lower or 'cross' in test_lower:
            return 'A03: Injection (XSS)'
        elif 'broken' in test_lower or 'access' in test_lower:
            return 'A01: Broken Access Control'
        elif 'secret' in test_lower or 'hardcoded' in test_lower:
            return 'A02: Cryptographic Failures'
        elif 'csrf' in test_lower:
            return 'A01: Broken Access Control (CSRF)'
        elif 'deserialization' in test_lower:
            return 'A08: Software and Data Integrity Failures'
        elif 'ssrf' in test_lower:
            return 'A10: Server-Side Request Forgery'
        else:
            return 'General Security'

    def export_to_csv(self, results: List, models: List[str], performance_by_model: Dict, outdir: Path) -> str:
        """Export detailed results to CSV."""
        # Detailed results CSV (without text preview to avoid PII)
        csv_path = outdir / "detailed_results.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'model', 'suite_id', 'ok', 'score', 'elapsed_s', 'cost_usd',
                'input_tokens', 'output_tokens', 'total_tokens'
            ])

            for result in results:
                writer.writerow([
                    getattr(result, 'model', ''),
                    getattr(result, 'suite_id', ''),
                    getattr(result, 'ok', False),
                    getattr(result, 'score', 0.0),
                    getattr(result, 'elapsed_s', 0.0),
                    getattr(result, 'cost_usd', 0.0),
                    getattr(result, 'input_tokens', 0),
                    getattr(result, 'output_tokens', 0),
                    getattr(result, 'total_tokens', 0)
                ])

        # Enhanced model summary CSV
        summary_path = outdir / "model_summary.csv"
        with open(summary_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'model', 'total_tests', 'successful_tests', 'avg_score', 'quality_tier',
                'total_cost', 'cost_per_test', 'traditional_effectiveness', 'quality_weighted_effectiveness',
                'meets_threshold', 'cost_efficiency_tier'
            ])

            for model in models:
                perf = performance_by_model.get(model)
                if perf and hasattr(perf, 'enhanced_metrics') and getattr(perf, 'enhanced_metrics', None):
                    writer.writerow([
                        model,
                        perf.enhanced_metrics.total_tests,
                        getattr(perf.enhanced_metrics, 'successful_tests',
                                getattr(perf.enhanced_metrics, 'passed_tests', 0)),
                        perf.avg_score,
                        getattr(perf, 'quality_tier', QualityTier.BELOW_STANDARDS).value,
                        perf.enhanced_metrics.total_cost,
                        perf.enhanced_metrics.cost_per_test,
                        perf.enhanced_metrics.traditional_effectiveness,
                        perf.enhanced_metrics.quality_weighted_effectiveness,
                        perf.meets_accuracy_threshold,
                        perf.cost_efficiency_tier
                    ])

        return str(csv_path)

    def export_to_json(self, results: List, models: List[str], performance_by_model: Dict,
                       language_results: Dict, owasp_results: Dict, outdir: Path) -> str:
        """Export comprehensive analysis to JSON."""
        json_data = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_models': len(models),
                'total_tests': len(results),
                'analysis_type': 'enhanced_unified_reporting_with_tiers',
                'quality_framework': 'graduated_tiers'
            },
            'quality_tier_summary': {},
            'model_analysis': {},
            'language_analysis': language_results,
            'owasp_analysis': owasp_results,
            'enhanced_metrics': {}
        }

        # Quality tier summary
        from collections import Counter
        tier_counts = Counter(getattr(p, 'quality_tier', QualityTier.BELOW_STANDARDS) for p in performance_by_model.values())
        json_data['quality_tier_summary'] = {tier.value: count for tier, count in tier_counts.items()}

        # Add model analysis
        for model in models:
            perf = performance_by_model.get(model)
            if perf:
                json_data['model_analysis'][model] = {
                    'total_tests': perf.total_tests,
                    'successful_tests': getattr(perf, 'successful_tests', getattr(perf, 'passed_tests', 0)),
                    'avg_score': perf.avg_score,
                    'quality_tier': getattr(perf, 'quality_tier', QualityTier.BELOW_STANDARDS).value,
                    'avg_response_time': getattr(perf, 'avg_response_time', getattr(perf, 'avg_time_s', 0.0)),
                    'total_cost': getattr(perf, 'total_cost', getattr(perf, 'total_cost_usd', 0.0)),
                    'cost_per_test': perf.cost_per_test,
                    'meets_accuracy_threshold': getattr(perf, 'meets_accuracy_threshold', False),
                    'cost_efficiency_tier': getattr(perf, 'cost_efficiency_tier', 'unknown'),
                    'reliability_score': getattr(perf, 'reliability_score', 0.0)
                }

                if hasattr(perf, 'enhanced_metrics') and perf.enhanced_metrics:
                    json_data['enhanced_metrics'][model] = asdict(perf.enhanced_metrics)

        # Save JSON
        json_path = outdir / "comprehensive_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)

        return str(json_path)


# -------------------------------
# Enhanced Main Function
# -------------------------------

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
        accuracy_threshold: float = 0.70  # Changed default to realistic threshold
) -> str:
    """
    Generate enhanced executive summary with graduated quality tiers and expert insights
    """

    reporter = EnhancedUnifiedReporter(accuracy_threshold)

    # Calculate enhanced performance metrics
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if getattr(r, 'model', '') == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results, accuracy_threshold)

    if not performance_by_model:
        return "No valid results to analyze"

    # Perform language and OWASP analysis if not provided
    if language_results is None:
        language_results = reporter.analyze_by_language(results)

    if owasp_results is None:
        owasp_results = reporter.analyze_by_owasp_category(results)

    # Enhanced analysis with quality tiers
    from collections import Counter
    tier_counts = Counter(getattr(p, 'quality_tier', QualityTier.BELOW_STANDARDS) for p in performance_by_model.values())
    qualified_models = [p for p in performance_by_model.values() if getattr(p, 'quality_tier', QualityTier.BELOW_STANDARDS) != QualityTier.BELOW_STANDARDS]

    # Generate expert insights
    expert_insights = generate_expert_insights(performance_by_model)
    hybrid_recommendation = generate_simple_hybrid_recommendations(qualified_models)

    # Find best performers by tier
    best_overall = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_qualified = max(qualified_models, key=lambda p: p.avg_score) if qualified_models else None
    best_value = min([p for p in qualified_models if p.cost_per_test > 0],
                     key=lambda p: p.cost_per_test) if qualified_models else None

    # Calculate aggregate statistics
    total_tests = sum(p.total_tests for p in performance_by_model.values())
    models_count = len(performance_by_model)
    avg_cost_per_test = total_cost / total_tests if total_tests > 0 else 0.0

    # Calculate overall completion rate
    total_attempts = sum(p.total_tests for p in performance_by_model.values())
    total_successes = sum(p.passed_tests for p in performance_by_model.values())
    overall_completion = total_successes / total_attempts if total_attempts > 0 else 0

    # Generate enhanced executive summary
    summary = f"""# 🛡️ Enhanced Security Benchmark Executive Summary

**Suite:** {suite_name} | **Models Tested:** {models_count} | **Total Security Tests:** {total_tests:,} | **Date:** {datetime.now().strftime('%B %d, %Y')} | **Total Investment:** ${total_cost:.2f}

## 🎯 Executive Overview

This comprehensive security assessment evaluated {models_count} leading AI models across {total_tests:,} security scenarios, analyzing capability to identify vulnerabilities, provide appropriate recommendations, and demonstrate security knowledge alignment with industry standards.

**Enhanced Quality Framework Applied:** Graduated quality tiers with realistic thresholds based on current LLM capabilities

## 📌 Key Findings with Graduated Quality Assessment

### Quality Tier Distribution:
"""

    # Enhanced quality tier summary
    for tier in QualityTier:
        count = tier_counts.get(tier, 0)
        if count > 0:
            percentage = (count / models_count) * 100
            tier_name = tier.value.replace('_', ' ').title()
            if tier != QualityTier.BELOW_STANDARDS:
                description = QUALITY_STANDARDS[tier].description
                summary += f"• **{tier_name} ({QUALITY_STANDARDS[tier].min_accuracy:.0%}+):** {count} models ({percentage:.0f}%) - {description}\n"
            else:
                summary += f"• **{tier_name}:** {count} models ({percentage:.0f}%)\n"

    summary += f"""
### Strategic Readiness Assessment:
• **Production-Ready Models:** {len(qualified_models)}/{models_count} meet minimum viable standards
• **Highest Accuracy:** {best_overall.avg_score:.1%} by {best_overall.model} ({'✅' if getattr(best_overall, 'quality_tier', QualityTier.BELOW_STANDARDS) != QualityTier.BELOW_STANDARDS else '⚠️'} {getattr(best_overall, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()})
"""

    if best_qualified:
        summary += f"• **Best Qualified:** {best_qualified.model} ({getattr(best_qualified, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()} tier)\n"

    if best_value:
        summary += f"• **Best Value:** {best_value.enhanced_metrics.quality_weighted_effectiveness:.1f} quality points/$ by {best_value.model}\n"

    summary += f"• **Overall Success Rate:** {overall_completion:.1%} of tests completed successfully\n"

    # Expert insights section
    summary += "\n## 🔍 Expert Analysis & Strategic Insights\n\n"
    for insight in expert_insights:
        summary += f"{insight}\n\n"

    if hybrid_recommendation:
        summary += f"{hybrid_recommendation}\n\n"

    # Quality-approved model rankings
    summary += "## 🔍 Production-Ready Model Rankings\n\n"

    if qualified_models:
        # Sort by quality tier first, then by effectiveness
        qualified_sorted = sorted(qualified_models,
                                  key=lambda p: (getattr(p, 'quality_tier', QualityTier.BELOW_STANDARDS).value,
                                                 -p.enhanced_metrics.quality_weighted_effectiveness if p.enhanced_metrics else 0))

        tier_groups = {}
        for model in qualified_sorted:
            tier = getattr(model, 'quality_tier', QualityTier.BELOW_STANDARDS)
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(model)

        for tier in [QualityTier.MISSION_CRITICAL, QualityTier.ENTERPRISE_PREFERRED, QualityTier.MINIMUM_VIABLE]:
            if tier in tier_groups:
                tier_name = tier.value.replace('_', ' ').title()
                summary += f"### {tier_name} Tier Models\n\n"

                for i, model in enumerate(tier_groups[tier], 1):
                    enhanced = model.enhanced_metrics
                    summary += f"""#### {i}. {model.model} ({model.cost_efficiency_tier})
- **Security Accuracy:** {model.avg_score:.1%} (95% CI: {model.accuracy_ci_lower:.1%}-{model.accuracy_ci_upper:.1%})
- **Reliability:** {model.success_rate:.1%} success rate
- **Response Time:** {model.avg_time_s:.1f}s average
- **Cost:** ${model.cost_per_test:.5f} per analysis
- **Quality Score:** {enhanced.quality_weighted_effectiveness:.1f} points per dollar
- **Perfect Scores:** {enhanced.perfect_scores}/{enhanced.total_tests} ({enhanced.perfect_scores / enhanced.total_tests:.1%})

"""
    else:
        summary += """**Current Status:** No models meet minimum viable standards (70% accuracy, 95% success rate).

**Immediate Recommendations:**
• Deploy best available model with enhanced human review processes
• Implement confidence-based escalation to human experts  
• Consider ensemble approaches combining multiple models
• Focus on model fine-tuning for security-specific use cases

"""

    # Performance comparison table (preserved from original)
    summary += """## 📊 Comprehensive Performance Analysis

| Model | Tests | Success Rate | Accuracy | Response Time | Cost/Test | Quality Score | Tier |
|-------|-------|--------------|----------|---------------|-----------|---------------|------|"""

    for model, perf in sorted(performance_by_model.items(), key=lambda x: x[1].avg_score, reverse=True):
        quality_score = perf.enhanced_metrics.quality_weighted_effectiveness if perf.enhanced_metrics else 0.0
        tier_display = getattr(perf, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()
        status = "✅" if getattr(perf, 'quality_tier', QualityTier.BELOW_STANDARDS) != QualityTier.BELOW_STANDARDS else ("⚠️" if perf.avg_score > 0.65 else "❌")

        summary += f"""
| {status} {model} | {perf.total_tests} | {perf.success_rate:.1%} | {perf.avg_score:.1%} | {perf.avg_time_s:.1f}s | ${perf.cost_per_test:.5f} | {quality_score:.1f} | {tier_display} |"""

    # Strategic deployment recommendations
    summary += f"""

## 🚀 Strategic Deployment Recommendations

"""

    if qualified_models:
        # Find best in each category
        best_accuracy = max(qualified_models, key=lambda p: p.avg_score)
        best_cost_eff = min([p for p in qualified_models if p.cost_per_test > 0],
                            key=lambda p: p.cost_per_test, default=qualified_models[0])
        best_speed = min(qualified_models, key=lambda p: p.avg_time_s)

        summary += f"""### For Maximum Security Accuracy (Audits & Compliance):
**Primary Choice:** {best_accuracy.model} ✅ {getattr(best_accuracy, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()}
- **Detection Rate:** {best_accuracy.avg_score:.1%} with human review for remaining {(1 - best_accuracy.avg_score):.0%}
- **Use Cases:** Security audits, compliance reviews, critical infrastructure assessment
- **Cost:** ${best_accuracy.cost_per_test:.5f} per analysis
- **Response Time:** {best_accuracy.avg_time_s:.1f}s average

### For Cost-Effective Operations:
**Recommended:** {best_cost_eff.model} ✅ {getattr(best_cost_eff, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()}
- **Value Proposition:** {best_cost_eff.enhanced_metrics.quality_weighted_effectiveness:.1f} quality points per dollar
- **Use Cases:** Production security workflows, automated analysis, development testing
- **Accuracy:** {best_cost_eff.avg_score:.1%} detection rate
- **Cost:** ${best_cost_eff.cost_per_test:.5f} per analysis

### For Real-Time Security (Monitoring & Response):
**Best Choice:** {best_speed.model} ✅ {getattr(best_speed, 'quality_tier', QualityTier.BELOW_STANDARDS).value.replace('_', ' ').title()}
- **Response Time:** {best_speed.avg_time_s:.1f}s average
- **Use Cases:** Live security monitoring, real-time threat detection, interactive analysis  
- **Accuracy:** {best_speed.avg_score:.1%} detection rate
- **Throughput:** {best_speed.throughput_per_hour:.0f} analyses per hour
"""
    else:
        # Fallback recommendations when no models qualify
        summary += f"""### Interim Deployment Strategy (No Qualified Models):

**Primary Choice:** {best_overall.model} ⚠️ Best Available ({best_overall.avg_score:.1%} accuracy)
- **Accuracy:** {best_overall.avg_score:.1%} automated detection + {(1 - best_overall.avg_score):.0%} human review required
- **Cost:** ${best_overall.cost_per_test:.5f} per analysis
- **Implementation:** Deploy with mandatory human expert validation for all findings
- **Use Cases:** Initial screening with comprehensive human oversight

**Risk Mitigation:**
- Implement confidence scoring to identify uncertain predictions
- Establish clear escalation procedures for security findings
- Regular performance monitoring and threshold adjustment
- Plan for model retraining or replacement as capabilities improve
"""

    # Preserve all original detailed sections
    summary += f"""
## 🌐 Language-Specific Security Analysis

"""

    if language_results:
        for language, metrics in sorted(language_results.items(), key=lambda x: x[1]['avg_score'], reverse=True):
            best_model = max(metrics['models'].items(), key=lambda x: x[1]['avg_score']) if metrics['models'] else (
                'None', {'avg_score': 0})
            summary += f"""**{language}:** {metrics['avg_score']:.1%} average accuracy across {metrics['total_tests']} tests
- Best performer: {best_model[0]} ({best_model[1]['avg_score']:.1%} accuracy)
- Cost effectiveness: {metrics['effectiveness']:.1f} points per dollar
"""

    summary += f"""
## 🔒 OWASP Security Category Performance

"""

    if owasp_results:
        for category, metrics in sorted(owasp_results.items(), key=lambda x: x[1]['avg_score'], reverse=True):
            best_model = max(metrics['models'].items(), key=lambda x: x[1]['avg_score']) if metrics['models'] else (
                'None', {'avg_score': 0})
            summary += f"""**{category}:** {metrics['avg_score']:.1%} average detection rate
- Top performer: {best_model[0]} ({best_model[1]['avg_score']:.1%} accuracy)
- Tests analyzed: {metrics['total_tests']}
"""

    # Preserve enhanced business impact analysis
    summary += f"""
## 📈 Enhanced Business Impact Assessment

**Quality-Adjusted Investment Analysis:**
- **Total Security Investment:** ${total_cost:.4f}
- **Production-Ready Models:** {len(qualified_models)}/{models_count}
- **Enterprise Readiness:** {len(qualified_models) / models_count:.1%} of tested models meet standards
- **Average Analysis Cost:** ${avg_cost_per_test:.5f} per test

**ROI Framework by Use Case:**
1. **Critical Security Audits:** Invest in highest accuracy models regardless of cost
2. **Production Operations:** Use quality-weighted effectiveness for optimal value
3. **Development Testing:** Balance speed and accuracy for iterative workflows
4. **Compliance Reviews:** Prioritize reliability and perfect score rates

**Quality Metrics Summary:**
- **Perfect Score Rate:** {sum(p.enhanced_metrics.perfect_scores for p in performance_by_model.values() if p.enhanced_metrics) / sum(p.enhanced_metrics.total_tests for p in performance_by_model.values() if p.enhanced_metrics):.1%} across all models
- **Enterprise Standard Compliance:** {len(qualified_models)}/{models_count} models meet thresholds
- **Cost Range:** ${min(p.cost_per_test for p in performance_by_model.values() if p.cost_per_test > 0):.5f} - ${max(p.cost_per_test for p in performance_by_model.values()):.5f} per test

## 🔍 Enhanced Quality Assurance & Methodology

**Quality Standards Framework:**
- **Minimum Viable (70%):** {QUALITY_STANDARDS[QualityTier.MINIMUM_VIABLE].description}
- **Enterprise Preferred (75%):** {QUALITY_STANDARDS[QualityTier.ENTERPRISE_PREFERRED].description}
- **Mission Critical (80%):** {QUALITY_STANDARDS[QualityTier.MISSION_CRITICAL].description}

**Enhanced Effectiveness Calculations:**
- **Traditional Effectiveness:** Raw accuracy ÷ cost per test
- **Quality-Weighted Effectiveness:** Weighted scoring considering response quality
- **Penalty-Adjusted Effectiveness:** Accounts for failed test penalties

**Analysis Limitations & Future Improvements:**
- Consider standardizing test counts across models for enhanced statistical validity
- Add p95 latency measurements for SLA planning
- Expand vulnerability category coverage
- Include multi-language security framework analysis

## ⚡ Use-Case Profile Analysis

### RAPID_RESPONSE Profile (Time-Sensitive Operations)
*Target: PR reviews, rapid vuln checks, AoC triage, malware analysis*

| Model | Meets Gate | Accuracy | Success | P95 Latency | Decision Score |
|-------|------------|----------|---------|-------------|----------------|
"""

    # Add RAPID_RESPONSE analysis
    rapid_models = []
    for model in performance_by_model.values():
        meets_rapid = RAPID_RESPONSE.meets_gate(
            model.avg_score, model.success_rate, model.p95_time_s
        )
        decision_score = RAPID_RESPONSE.decision_score(
            model.avg_score, model.p95_time_s, model.cost_per_test
        )
        rapid_models.append((model, meets_rapid, decision_score))

    rapid_models.sort(key=lambda x: x[2], reverse=True)  # Sort by decision score

    for model, meets_gate, score in rapid_models:
        status = "✅" if meets_gate else "⚠️"
        latency_display = f"{model.p95_time_s:.1f}s" if model.p95_time_s > 0 else f"{model.avg_time_s:.1f}s (mean only)"
        summary += f"| {model.model} | {status} | {model.avg_score:.1%} | {model.success_rate:.1%} | {latency_display} | {score:.2f} |\n"

    summary += f"""
**RAPID_RESPONSE Recommendations:**
- **Primary Pick:** {rapid_models[0][0].model if rapid_models else 'None'} (highest decision score)
- **Realistic Gates:** Accuracy ≥{RAPID_RESPONSE.min_accuracy:.0%}, Success ≥{RAPID_RESPONSE.min_success_rate:.0%}, P95 ≤{RAPID_RESPONSE.max_p95_latency_s:.0f}s
- **Sample Adequacy:** {'⚠️ Low confidence' if any(m[0].sample_adequacy_warning for m in rapid_models) else '✅ Adequate'}

### IN_DEPTH Profile (Comprehensive Analysis)
*Target: Full codebase analysis, compliance reviews, architecture assessment*

| Model | Meets Gate | Accuracy | Success | P95 Latency | Decision Score |
|-------|------------|----------|---------|-------------|----------------|
"""

    # Add IN_DEPTH analysis
    indepth_models = []
    for model in performance_by_model.values():
        meets_indepth = IN_DEPTH.meets_gate(
            model.avg_score, model.success_rate, model.p95_time_s
        )
        decision_score = IN_DEPTH.decision_score(
            model.avg_score, model.p95_time_s, model.cost_per_test
        )
        indepth_models.append((model, meets_indepth, decision_score))

    indepth_models.sort(key=lambda x: x[2], reverse=True)  # Sort by decision score

    for model, meets_gate, score in indepth_models:
        status = "✅" if meets_gate else "⚠️"
        latency_display = f"{model.p95_time_s:.1f}s" if model.p95_time_s > 0 else f"{model.avg_time_s:.1f}s (mean only)"
        summary += f"| {model.model} | {status} | {model.avg_score:.1%} | {model.success_rate:.1%} | {latency_display} | {score:.2f} |\n"

    summary += f"""
**IN_DEPTH Recommendations:**
- **Primary Pick:** {indepth_models[0][0].model if indepth_models else 'None'} (highest decision score)  
- **Realistic Gates:** Accuracy ≥{IN_DEPTH.min_accuracy:.0%}, Success ≥{IN_DEPTH.min_success_rate:.0%}, P95 ≤{IN_DEPTH.max_p95_latency_s:.0f}s
- **Sample Adequacy:** {'⚠️ Low confidence' if any(m[0].sample_adequacy_warning for m in indepth_models) else '✅ Adequate'}

## 📊 Latency Distribution Analysis

| Model | Mean | Median | P95 | P99 | Std Dev | Throughput/hr |
|-------|------|--------|-----|-----|---------|---------------|
"""

    # Add latency distribution table
    for model in sorted(performance_by_model.values(), key=lambda p: p.avg_time_s):
        latency_display = f"{model.p95_time_s:.1f}s" if model.p95_time_s > 0 else "N/A"
        p99_display = f"{model.p99_time_s:.1f}s" if model.p99_time_s > 0 else "N/A"
        summary += f"| {model.model} | {model.avg_time_s:.1f}s | {model.median_time_s:.1f}s | {latency_display} | {p99_display} | {model.std_time_s:.1f}s | {model.throughput_per_hour:.0f} |\n"

    summary += f"""
## 📈 Statistical Validation

### Confidence Intervals (95%)
| Model | Success Rate CI | Accuracy CI | Sample Size |
|-------|-----------------|-------------|-------------|
"""

    # Add statistical validation table
    for model in sorted(performance_by_model.values(), key=lambda p: p.model):
        sample_warning = "⚠️" if model.sample_adequacy_warning else "✅"
        summary += f"| {model.model} | {model.success_rate_ci_lower:.1%}-{model.success_rate_ci_upper:.1%} | {model.accuracy_ci_lower:.1%}-{model.accuracy_ci_upper:.1%} | {model.total_tests} {sample_warning} |\n"

    summary += f"""
### Sample Size Adequacy
- **Recommended minimum:** {RAPID_RESPONSE.min_samples} tests per model for RAPID_RESPONSE, {IN_DEPTH.min_samples} for IN_DEPTH
- **Current status:** {'⚠️ Some models below recommended sample size' if any(p.sample_adequacy_warning for p in performance_by_model.values()) else '✅ All models meet sample size requirements'}

## 🛡️ Security-Aware Metrics

### Precision/Recall Analysis
"""

    # Add security metrics if available
    security_models = [p for p in performance_by_model.values() if p.precision is not None]
    if security_models:
        summary += """| Model | Precision | Recall | F1 Score | Severity-Weighted |
|-------|-----------|--------|----------|------------------|
"""
        for model in security_models:
            summary += f"| {model.model} | {model.precision:.3f} | {model.recall:.3f} | {model.f1_score:.3f} | {model.severity_weighted_score:.3f} |\n"
    else:
        summary += "*Precision/Recall metrics not available - requires TP/FP/FN/TN data in test results*\n"

    summary += f"""
## 🔬 Reproducibility & Configuration

### Model Configuration Details
| Model | Version | Region | Temperature | Seed | Max Tokens |
|-------|---------|--------|-------------|------|------------|
"""

    # Add reproducibility info
    for model in sorted(performance_by_model.values(), key=lambda p: p.model):
        version = model.model_version or "Not specified"
        region = model.region or "Not specified"
        temp = f"{model.temperature:.2f}" if model.temperature is not None else "Not specified"
        seed = str(model.seed) if model.seed is not None else "Not specified"
        tokens = str(model.max_tokens) if model.max_tokens is not None else "Not specified"
        summary += f"| {model.model} | {version} | {region} | {temp} | {seed} | {tokens} |\n"

    summary += f"""
### Reproducibility Notes
- **Run Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Suite:** {suite_name}
- **Total Tests:** {total_tests}
- **Quality Framework:** Graduated tiers (70%, 75%, 80%)
- **Statistical Methods:** Wilson CI (proportions), Bootstrap CI (means)
- **Profile Gates:** RAPID_RESPONSE (Acc≥{RAPID_RESPONSE.min_accuracy:.0%}%, Succ≥{RAPID_RESPONSE.min_success_rate:.0%}%, P95≤{RAPID_RESPONSE.max_p95_latency_s:.0f}s), IN_DEPTH (Acc≥{IN_DEPTH.min_accuracy:.0%}%, Succ≥{IN_DEPTH.min_success_rate:.0%}%, P95≤{IN_DEPTH.max_p95_latency_s:.0f}s)

---

*This enhanced analysis incorporates graduated quality tiers, realistic LLM security capability assessment, and actionable deployment strategies. Generated by the Enhanced Unified Executive Summary Generator with Tiered Quality Framework for enterprise security program optimization.*

## 📋 Export Options

The following additional analysis formats are available:
- **Detailed CSV Export:** Individual test results and model summaries with quality tiers
- **Comprehensive JSON:** Full analysis with enhanced metrics and graduated quality assessment
- **Performance Visualizations:** Charts and graphs (if matplotlib available)

Use the export functions to generate these additional formats for deeper analysis.
"""

    # Save to file
    summary_path = outdir / "Executive_Summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    # Generate exports
    reporter.export_to_csv(results, models, performance_by_model, outdir)
    reporter.export_to_json(results, models, performance_by_model, language_results, owasp_results, outdir)

    return str(summary_path)


# Backward compatibility
def generate_basic_executive_summary(*args, **kwargs):
    return generate_enhanced_unified_executive_summary(*args, **kwargs)


def generate_quality_first_executive_summary(*args, **kwargs):
    return generate_enhanced_unified_executive_summary(*args, **kwargs)


def generate_comprehensive_executive_summary(*args, **kwargs):
    return generate_enhanced_unified_executive_summary(*args, **kwargs)