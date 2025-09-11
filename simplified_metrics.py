#!/usr/bin/env python3
"""
Simplified Metrics Calculation Module
Built by the Rapticore Security Research Team

Implements the simplified policy metrics with attempt semantics,
smoothed rates, and breadth coverage.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from simplified_config import get_config


def encode_row_simple(record: Dict[str, Any], suite_name: str) -> Dict[str, Any]:
    """
    Simple mode: everything in data is treated as attempted; failures → 0. 
    N/A only for corruption.
    
    Args:
        record: Raw benchmark result record
        suite_name: Name of the test suite
        
    Returns:
        Dictionary with encoded metrics
    """
    config = get_config()
    
    # Extract data from record structure
    api = record.get("api_request", {})
    status = api.get("response_status", None)
    text = ((api.get("response_body", {})).get("text", "") or "")
    score = record.get("normalized_score")
    elapsed_s = (record.get("execution_duration_ms", 0) or 0) / 1000.0
    timeout_s = config.get_timeout(suite_name)
    
    # Detect corruption: no api object and no score field at all
    corrupt = (
        api == {} and 
        score is None and 
        record.get("token_usage") is None
    )
    
    if corrupt:
        # In simple mode this is exceptional: still mark N/A but emit a flag
        return {
            "attempted": 0,
            "score": np.nan,
            "ok": np.nan,
            "elapsed_s": np.nan,
            "timeout": np.nan,
            "corrupt": True
        }
    
    # Attempted path - treat all records as attempted
    ok = int(status == 200 and bool(str(text).strip()))
    timeout = int(elapsed_s >= timeout_s)
    
    # Failures → 0
    if score is None:
        score = 0.0
    if not ok:
        score = 0.0
    
    return {
        "attempted": 1,
        "score": float(score),
        "ok": ok,
        "elapsed_s": float(elapsed_s),
        "timeout": timeout,
        "corrupt": False
    }


def smoothed_rate(k: int, n: int, prior: int = 1, prior_total: int = 2) -> float:
    """
    Calculate smoothed rate with prior to handle small samples.
    
    Args:
        k: Number of successes
        n: Total number of attempts
        prior: Prior successes
        prior_total: Prior total attempts
        
    Returns:
        Smoothed rate
    """
    if n == 0:
        return 0.0
    
    return (k + prior) / (n + prior_total)


def reliability_fixed(ok_array: np.ndarray, elapsed_array: np.ndarray, timeout_s: float) -> float:
    """
    Calculate reliability as success_rate × (1 - timeout_rate).
    
    Args:
        ok_array: Array of success indicators (0/1)
        elapsed_array: Array of elapsed times
        timeout_s: Timeout threshold in seconds
        
    Returns:
        Reliability score [0, 1]
    """
    if len(ok_array) == 0:
        return 0.0
    
    success_rate = np.mean(ok_array)
    timeout_rate = np.mean(elapsed_array >= timeout_s)
    
    reliability = success_rate * (1 - timeout_rate)
    return max(0.0, min(1.0, reliability))


def breadth_coverage(df_slice: pd.DataFrame, category_col: str = "owasp_category") -> float:
    """
    Calculate breadth coverage: % of categories where mean score ≥ min_mean.
    
    Args:
        df_slice: DataFrame slice for a model
        category_col: Column name for categories
        
    Returns:
        Breadth coverage score [0, 1]
    """
    config = get_config()
    
    if category_col not in df_slice.columns:
        return np.nan
    
    min_mean = config.breadth_min_mean
    
    # Group by category and calculate mean scores
    category_means = df_slice.groupby(category_col)["score"].mean()
    
    if len(category_means) == 0:
        return np.nan
    
    # Count categories that meet the threshold
    covered = (category_means >= min_mean).sum()
    total = len(category_means)
    
    return covered / total


def qfs_hybrid(accuracy: float, completeness: float, coverage: float, 
               reliability: float, weights: Dict[str, float], epsilon: float = 0.05) -> float:
    """
    Calculate QFS using hybrid product/sum with given weights.
    
    Args:
        accuracy: Accuracy score [0, 1]
        completeness: Completeness score [0, 1] 
        coverage: Coverage score [0, 1]
        reliability: Reliability score [0, 1]
        weights: Weight dictionary
        epsilon: Small value to avoid log(0)
        
    Returns:
        QFS score [0, 1]
    """
    # Handle zero values gracefully
    A = max(accuracy, epsilon)
    Cmpl = max(completeness, epsilon)
    Cov = max(coverage, epsilon)
    Rel = max(reliability, epsilon)
    
    # Geometric mean with given weights
    qfs = (
        (A ** weights.get("accuracy", 0.6)) *
        (Cmpl ** weights.get("completeness", 0.35)) *
        (Cov ** weights.get("coverage", 0.0)) *  # Coverage weight from config
        (Rel ** weights.get("reliability", 0.05))
    )
    
    return qfs


def aggregate_slice_simple(df_slice: pd.DataFrame, suite_name: str) -> Dict[str, Any]:
    """
    Aggregate a slice of data using simplified policy.
    
    Args:
        df_slice: DataFrame slice for a model
        suite_name: Name of the test suite
        
    Returns:
        Dictionary with aggregated metrics
    """
    config = get_config()
    
    # Filter out any rare corrupt rows from metrics
    valid = (df_slice["attempted"] == 1)
    n = int(valid.sum())
    
    if n == 0:
        return {
            "n": 0,
            "accuracy": np.nan,
            "completeness": np.nan,
            "reliability": np.nan,
            "qfs": np.nan,
            "breadth_cov": np.nan
        }
    
    scores = df_slice.loc[valid, "score"].astype(float).to_numpy()
    accuracy = float(np.mean(scores))
    
    # Completeness with smoothing
    threshold = config.completeness_threshold
    k_complete = int(np.sum(scores >= threshold))
    completeness = smoothed_rate(
        k_complete, n,
        prior=config.completeness_prior,
        prior_total=config.completeness_prior_total
    )
    
    # Reliability
    ok = df_slice.loc[valid, "ok"].astype(int).to_numpy()
    elapsed = df_slice.loc[valid, "elapsed_s"].astype(float).to_numpy()
    reliability = reliability_fixed(ok, elapsed, config.get_timeout(suite_name))
    
    # QFS without attempt-coverage
    qfs = qfs_hybrid(
        accuracy, completeness, 1.0, reliability,  # coverage = 1.0 (neutral)
        config.qfs_weights, epsilon=0.05
    )
    
    # Breadth coverage (optional)
    breadth_cov = breadth_coverage(df_slice) if config.enable_breadth_coverage else np.nan
    
    return {
        "n": n,
        "accuracy": accuracy,
        "completeness": completeness,
        "reliability": reliability,
        "qfs": qfs,
        "breadth_cov": breadth_cov
    }


def calculate_percentages(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert metrics to percentages for display.
    
    Args:
        metrics: Dictionary with raw metrics
        
    Returns:
        Dictionary with percentage versions
    """
    result = metrics.copy()
    
    for key in ["accuracy", "completeness", "reliability", "qfs", "breadth_cov"]:
        if key in result and not np.isnan(result[key]):
            result[f"{key}_pct"] = result[key] * 100.0
        else:
            result[f"{key}_pct"] = np.nan
    
    return result
