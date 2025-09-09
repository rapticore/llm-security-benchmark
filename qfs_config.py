#!/usr/bin/env python3
"""
Quality-First Score (QFS) Configuration Module
Built by the Rapticore Security Research Team

Centralized constants, scoring formulas, and validation rules for 
methodologically consistent quality-first analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

# =============================================================================
# CORE CONFIGURATION CONSTANTS
# =============================================================================

@dataclass
class QFSConfig:
    """Quality-First Score configuration constants."""
    
    # QFS Formula Weights (geometric mean - accuracy primary)
    ACCURACY_WEIGHT: float = 0.50      # Primary quality metric
    COMPLETENESS_WEIGHT: float = 0.30  # Tests achieving ≥80% detection
    COVERAGE_WEIGHT: float = 0.15      # Tests achieving ≥50% detection  
    RELIABILITY_WEIGHT: float = 0.05   # Success rate factor
    
    # Cost dampening (light penalty - cost is secondary)
    COST_PENALTY_FACTOR: float = 0.25  # Light cost dampening weight
    
    # Quality thresholds
    COMPLETENESS_THRESHOLD: float = 0.8  # "Good" detection threshold
    COVERAGE_THRESHOLD: float = 0.5      # "Basic" detection threshold
    
    # Statistical validation
    MIN_SAMPLE_SIZE: int = 30           # Minimum n for statistical confidence
    BOOTSTRAP_ITERATIONS: int = 1000    # Bootstrap CI iterations
    CONFIDENCE_LEVEL: float = 0.95      # 95% confidence intervals
    
    # Data validation bounds
    MIN_ACCURACY: float = 0.0
    MAX_ACCURACY: float = 1.0
    MIN_LATENCY: float = 0.0
    MIN_COST: float = 0.0
    
    # Timeout and failure thresholds
    TIMEOUT_THRESHOLD_S: float = 30.0   # Consider >30s as timeout proxy
    HIGH_FAILURE_RATE: float = 0.1      # Flag >10% failure rates
    
    # Random seed for reproducibility
    RANDOM_SEED: int = 42

# Global configuration instance
CONFIG = QFSConfig()

# =============================================================================
# QUALITY-FIRST SCORING FUNCTIONS
# =============================================================================

def validate_metrics(accuracy: float, completeness: float, coverage: float, 
                     reliability: float, cost: float, latency: float) -> bool:
    """Validate metric ranges according to schema."""
    return (
        CONFIG.MIN_ACCURACY <= accuracy <= CONFIG.MAX_ACCURACY and
        CONFIG.MIN_ACCURACY <= completeness <= CONFIG.MAX_ACCURACY and
        CONFIG.MIN_ACCURACY <= coverage <= CONFIG.MAX_ACCURACY and
        CONFIG.MIN_ACCURACY <= reliability <= CONFIG.MAX_ACCURACY and
        cost >= CONFIG.MIN_COST and
        latency >= CONFIG.MIN_LATENCY
    )

def calculate_reliability(success_rate: float, timeout_rate: float = 0.0, 
                         empty_rate: float = 0.0, json_fail_rate: float = 0.0) -> float:
    """Calculate reliability from failure rates."""
    reliability = 1.0 - empty_rate - timeout_rate - json_fail_rate
    return max(0.0, min(1.0, reliability))

def calculate_completeness(scores: List[float]) -> float:
    """Calculate completeness: % tests achieving ≥80% detection."""
    if not scores:
        return 0.0
    return sum(1 for s in scores if s >= CONFIG.COMPLETENESS_THRESHOLD) / len(scores)

def calculate_coverage(scores: List[float]) -> float:
    """Calculate coverage: % tests achieving ≥50% detection.""" 
    if not scores:
        return 0.0
    return sum(1 for s in scores if s >= CONFIG.COVERAGE_THRESHOLD) / len(scores)

def normalize_cost(cost_per_test: float, cost_p95: float) -> float:
    """Normalize cost using log transformation to prevent domination."""
    if cost_p95 <= 0 or cost_per_test <= 0:
        return 0.0
    
    # Use log1p to handle small values gracefully
    cost_normalized = np.log1p(cost_per_test) / np.log1p(cost_p95)
    return min(cost_normalized, 1.0)  # Clip to [0,1]

def calculate_qfs_raw(accuracy: float, completeness: float, coverage: float, 
                      reliability: float) -> float:
    """Calculate raw QFS using geometric mean with quality-first weights."""
    
    # Handle zero values gracefully (use small epsilon instead of 0)
    epsilon = 1e-6
    A = max(accuracy, epsilon)
    Cmpl = max(completeness, epsilon) 
    Cov = max(coverage, epsilon)
    Rel = max(reliability, epsilon)
    
    # Geometric mean with accuracy-heavy weighting
    qfs_raw = (
        (A ** CONFIG.ACCURACY_WEIGHT) * 
        (Cmpl ** CONFIG.COMPLETENESS_WEIGHT) * 
        (Cov ** CONFIG.COVERAGE_WEIGHT) * 
        (Rel ** CONFIG.RELIABILITY_WEIGHT)
    )
    
    return qfs_raw

def calculate_qfs(accuracy: float, completeness: float, coverage: float, 
                  reliability: float, cost_per_test: float, cost_p95: float) -> float:
    """Calculate final Quality-First Score with cost dampening."""
    
    # Validate inputs
    if not validate_metrics(accuracy, completeness, coverage, reliability, 
                           cost_per_test, 0.0):
        warnings.warn("Invalid metrics detected in QFS calculation")
        return 0.0
    
    # Calculate raw quality score
    qfs_raw = calculate_qfs_raw(accuracy, completeness, coverage, reliability)
    
    # Apply light cost dampening (cost is secondary)
    if cost_per_test > 0 and cost_p95 > 0:
        cost_normalized = normalize_cost(cost_per_test, cost_p95)
        qfs = qfs_raw / (1 + CONFIG.COST_PENALTY_FACTOR * cost_normalized)
    else:
        qfs = qfs_raw  # Free models get no penalty
    
    return qfs

# =============================================================================
# STATISTICAL FUNCTIONS  
# =============================================================================

def bootstrap_ci(data: List[float], statistic_func=np.mean, 
                confidence_level: float = CONFIG.CONFIDENCE_LEVEL, 
                n_bootstrap: int = CONFIG.BOOTSTRAP_ITERATIONS) -> Tuple[float, float, float]:
    """Calculate bootstrap confidence intervals for a statistic."""
    
    if len(data) < 2:
        stat_val = statistic_func(data) if data else 0.0
        return stat_val, stat_val, stat_val
    
    np.random.seed(CONFIG.RANDOM_SEED)
    
    # Bootstrap sampling
    bootstrap_stats = []
    n = len(data)
    
    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic_func(bootstrap_sample))
    
    # Calculate confidence interval
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    stat_val = statistic_func(data)
    ci_lower = np.percentile(bootstrap_stats, lower_percentile)
    ci_upper = np.percentile(bootstrap_stats, upper_percentile)
    
    return stat_val, ci_lower, ci_upper

def flag_low_sample_size(n: int) -> bool:
    """Flag slices with insufficient sample size."""
    return n < CONFIG.MIN_SAMPLE_SIZE

def calculate_p95_latency(latencies: List[float]) -> float:
    """Calculate 95th percentile latency."""
    if not latencies:
        return 0.0
    return np.percentile(latencies, 95)

# =============================================================================
# DATA VALIDATION SCHEMA
# =============================================================================

@dataclass
class ValidationResult:
    """Result of data validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    low_n_slices: List[str]
    high_failure_slices: List[str]

def validate_dataset(results_df) -> ValidationResult:
    """Validate dataset against schema and quality thresholds."""
    errors = []
    warnings = []
    low_n_slices = []
    high_failure_slices = []
    
    required_columns = [
        'model', 'test_id', 'success', 'score', 'response_time_s', 
        'cost_usd', 'input_tokens', 'output_tokens'
    ]
    
    # Check required columns
    missing_cols = [col for col in required_columns if col not in results_df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    
    if not errors:  # Only continue if basic structure is valid
        
        # Check data types and ranges
        if 'score' in results_df.columns:
            invalid_scores = results_df[
                (results_df['score'] < 0) | (results_df['score'] > 1)
            ]
            if len(invalid_scores) > 0:
                errors.append(f"Found {len(invalid_scores)} invalid scores outside [0,1]")
        
        if 'response_time_s' in results_df.columns:
            invalid_times = results_df[results_df['response_time_s'] < 0]
            if len(invalid_times) > 0:
                errors.append(f"Found {len(invalid_times)} negative response times")
                
        if 'cost_usd' in results_df.columns:
            invalid_costs = results_df[results_df['cost_usd'] < 0]
            if len(invalid_costs) > 0:
                errors.append(f"Found {len(invalid_costs)} negative costs")
        
        # Check sample sizes per slice
        if 'model' in results_df.columns:
            slice_counts = results_df.groupby(['model']).size()
            low_n = slice_counts[slice_counts < CONFIG.MIN_SAMPLE_SIZE]
            low_n_slices.extend([f"{idx} (n={count})" for idx, count in low_n.items()])
        
        # Check failure rates
        if 'success' in results_df.columns and 'model' in results_df.columns:
            failure_rates = results_df.groupby('model')['success'].apply(
                lambda x: 1 - x.mean()
            )
            high_failure = failure_rates[failure_rates > CONFIG.HIGH_FAILURE_RATE]
            high_failure_slices.extend([
                f"{model} ({rate:.1%} failure)" 
                for model, rate in high_failure.items()
            ])
    
    if low_n_slices:
        warnings.append(f"Low sample size slices detected: {len(low_n_slices)}")
    
    if high_failure_slices:
        warnings.append(f"High failure rate slices detected: {len(high_failure_slices)}")
    
    is_valid = len(errors) == 0
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors, 
        warnings=warnings,
        low_n_slices=low_n_slices,
        high_failure_slices=high_failure_slices
    )

# =============================================================================
# COST STANDARDIZATION  
# =============================================================================

def cost_per_million_tokens(input_tokens: int, output_tokens: int, 
                           input_cost_per_1k: float, output_cost_per_1k: float) -> float:
    """Calculate standardized cost per 1M tokens."""
    total_cost_per_1k = (
        (input_tokens / 1000) * input_cost_per_1k + 
        (output_tokens / 1000) * output_cost_per_1k
    )
    total_tokens = input_tokens + output_tokens
    
    if total_tokens == 0:
        return 0.0
    
    # Convert to cost per 1M tokens  
    cost_per_1m = (total_cost_per_1k / (total_tokens / 1000)) * 1000
    return cost_per_1m

def cost_per_passing_test(total_cost: float, passing_tests: int) -> float:
    """Calculate cost per passing test."""
    if passing_tests == 0:
        return float('inf')
    return total_cost / passing_tests

def cost_per_correct_finding(total_cost: float, correct_findings: int) -> float:
    """Calculate cost per correct security finding."""
    if correct_findings == 0:
        return float('inf')
    return total_cost / correct_findings