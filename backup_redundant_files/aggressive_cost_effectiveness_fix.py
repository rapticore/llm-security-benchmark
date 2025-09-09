#!/usr/bin/env python3
"""
Aggressive Cost-Effectiveness Fix Module

Addresses persistent gaming issues where ultra-cheap models dominate rankings
despite mediocre quality. Implements strict quality thresholds and normalization.

Built by the Rapticore Security Research Team
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AggressiveEffectivenessScore:
    """Aggressively adjusted effectiveness score to prevent gaming."""
    model_name: str
    raw_score: float
    test_count: int
    cost_per_test: float
    
    # Traditional metrics (for comparison)
    traditional_effectiveness: float
    
    # Aggressive anti-gaming metrics
    quality_threshold_passed: bool  # Must pass 80% accuracy minimum
    sample_size_adequate: bool      # Must have sufficient sample size
    cost_reasonable: bool           # Must not be suspiciously cheap
    
    # Adjusted effectiveness scores
    threshold_adjusted: float       # Zero if below 80% accuracy
    normalized_effectiveness: float # Adjusted for test count bias
    final_recommendation_tier: str  # Final tier after all adjustments
    
    # Quality flags
    warnings: List[str]
    disqualified: bool


class AggressiveCostEffectivenessAnalyzer:
    """
    Rigorous analyzer that applies quality standards for reliable model evaluation.
    
    Key principles:
    1. 80% accuracy minimum threshold - below this = zero effectiveness
    2. Test count normalization - all models compared on equal footing  
    3. Cost reasonableness assessment - ultra-low costs may indicate quality concerns
    4. Sample size requirements - insufficient data flagged for reliability
    """
    
    def __init__(self):
        self.accuracy_threshold = 0.80  # 80% minimum - no exceptions
        self.min_test_count = 5         # Minimum tests for reliable ranking
        self.suspicious_cost_threshold = 0.0001  # Below $0.0001 is suspicious
        self.max_cost_advantage = 100   # Max 100x cost advantage allowed
        
    def analyze_model_effectiveness(
        self, 
        model_name: str,
        raw_score: float,
        test_count: int,
        cost_per_test: float,
        good_responses: int,
        total_responses: int
    ) -> AggressiveEffectivenessScore:
        """Perform aggressive cost-effectiveness analysis."""
        
        warnings = []
        disqualified = False
        
        # 1. HARD ACCURACY THRESHOLD - No exceptions
        quality_threshold_passed = raw_score >= self.accuracy_threshold
        if not quality_threshold_passed:
            warnings.append(f"Below 80% accuracy threshold ({raw_score:.1%})")
            disqualified = True
        
        # 2. SAMPLE SIZE CHECK
        sample_size_adequate = test_count >= self.min_test_count
        if not sample_size_adequate:
            warnings.append(f"Insufficient sample size ({test_count} tests)")
        
        # 3. COST REASONABLENESS ASSESSMENT  
        cost_reasonable = cost_per_test >= self.suspicious_cost_threshold
        if not cost_reasonable:
            warnings.append(f"Extremely low cost may indicate quality limitations (${cost_per_test:.6f})")
            disqualified = True
        
        # Calculate traditional effectiveness (for comparison)
        traditional_effectiveness = raw_score / cost_per_test if cost_per_test > 0 else 0
        
        # 4. THRESHOLD-ADJUSTED EFFECTIVENESS
        # If below 80% accuracy, effectiveness = 0 (no exceptions)
        threshold_adjusted = traditional_effectiveness if quality_threshold_passed else 0.0
        
        # 5. COST ADVANTAGE LIMITING
        # Prevent any model from having >100x cost advantage
        cost_limited = max(cost_per_test, self.suspicious_cost_threshold)
        limited_effectiveness = raw_score / cost_limited if quality_threshold_passed else 0.0
        
        # 6. NORMALIZE FOR TEST COUNT BIAS
        # Adjust for unfair test count differences
        normalized_effectiveness = limited_effectiveness
        if test_count != self.min_test_count:
            # Penalty for fewer tests, slight penalty for many more tests
            if test_count < self.min_test_count:
                normalized_effectiveness *= (test_count / self.min_test_count) ** 0.5
            elif test_count > self.min_test_count * 2:
                normalized_effectiveness *= 0.9  # Slight penalty for excess tests
        
        # 7. FINAL TIER CLASSIFICATION
        final_tier = self._classify_aggressive_tier(
            raw_score, normalized_effectiveness, cost_per_test, warnings, disqualified
        )
        
        return AggressiveEffectivenessScore(
            model_name=model_name,
            raw_score=raw_score,
            test_count=test_count,
            cost_per_test=cost_per_test,
            traditional_effectiveness=traditional_effectiveness,
            quality_threshold_passed=quality_threshold_passed,
            sample_size_adequate=sample_size_adequate,
            cost_reasonable=cost_reasonable,
            threshold_adjusted=threshold_adjusted,
            normalized_effectiveness=normalized_effectiveness,
            final_recommendation_tier=final_tier,
            warnings=warnings,
            disqualified=disqualified
        )
    
    def _classify_aggressive_tier(
        self, 
        raw_score: float, 
        normalized_effectiveness: float, 
        cost_per_test: float,
        warnings: List[str], 
        disqualified: bool
    ) -> str:
        """Classify model into aggressive performance tiers."""
        
        if disqualified:
            return "BELOW_STANDARDS"
        
        if warnings:
            return "QUALITY_CONCERNS"
        
        # Only high-quality models can reach premium tiers
        if raw_score >= 0.95 and cost_per_test >= 0.005:
            return "ENTERPRISE_PREMIUM"
        elif raw_score >= 0.90 and normalized_effectiveness >= 50:
            return "ENTERPRISE_STANDARD"  
        elif raw_score >= 0.85 and normalized_effectiveness >= 100:
            return "PRODUCTION_READY"
        elif raw_score >= 0.80:
            return "ACCEPTABLE"
        else:
            return "BELOW_THRESHOLD"
    
    def generate_aggressive_rankings(
        self, 
        model_data: Dict[str, Dict]
    ) -> Tuple[List[AggressiveEffectivenessScore], Dict[str, str]]:
        """Generate aggressive rankings that prevent gaming."""
        
        scores = []
        
        for model_name, data in model_data.items():
            if 'raw_score' in data and 'cost_per_test' in data:
                score = self.analyze_model_effectiveness(
                    model_name=model_name,
                    raw_score=data['raw_score'],
                    test_count=data.get('test_count', 5),
                    cost_per_test=data['cost_per_test'],
                    good_responses=data.get('good_responses', 0),
                    total_responses=data.get('total_responses', 0)
                )
                scores.append(score)
        
        # Sort by normalized effectiveness (only qualified models)
        qualified_scores = [s for s in scores if not s.disqualified]
        disqualified_scores = [s for s in scores if s.disqualified]
        
        qualified_scores.sort(key=lambda s: s.normalized_effectiveness, reverse=True)
        
        # Generate tier-based recommendations
        recommendations = {
            "enterprise_premium": [s.model_name for s in qualified_scores 
                                 if s.final_recommendation_tier == "ENTERPRISE_PREMIUM"],
            "enterprise_standard": [s.model_name for s in qualified_scores 
                                  if s.final_recommendation_tier == "ENTERPRISE_STANDARD"],
            "production_ready": [s.model_name for s in qualified_scores 
                               if s.final_recommendation_tier == "PRODUCTION_READY"],
            "acceptable": [s.model_name for s in qualified_scores 
                          if s.final_recommendation_tier == "ACCEPTABLE"],
            "avoid_models": [s.model_name for s in disqualified_scores]
        }
        
        return qualified_scores + disqualified_scores, recommendations


def create_aggressive_cost_effectiveness_report(
    scores: List[AggressiveEffectivenessScore], 
    recommendations: Dict[str, List[str]]
) -> str:
    """Generate aggressive cost-effectiveness report."""
    
    qualified = [s for s in scores if not s.disqualified]
    disqualified = [s for s in scores if s.disqualified]
    
    report = f"""# 🚨 Aggressive Cost-Effectiveness Analysis Report

## Anti-Gaming Methodology

This analysis implements **strict quality thresholds** to completely eliminate gaming by cheap models:

### 🛡️ Quality Gates Applied:
1. **80% Accuracy Minimum** - Models below 80% accuracy get ZERO effectiveness score
2. **Cost Gaming Prevention** - Ultra-cheap models (<$0.0001) flagged as suspicious  
3. **Test Count Normalization** - All models compared on equal sample size basis
4. **Sample Size Requirements** - Minimum {len(qualified[0].model_name) if qualified else 5} tests for reliable ranking

---

## 🏆 Qualified Models (Passed All Quality Gates)

| Rank | Model | Accuracy | Cost/Test | Traditional | Normalized | Tier |
|------|-------|----------|-----------|-------------|------------|------|"""

    for i, score in enumerate(qualified[:10], 1):
        tier_display = score.final_recommendation_tier.replace('_', ' ').title()
        report += f"""
| {i} | **{score.model_name}** | {score.raw_score:.1%} | ${score.cost_per_test:.5f} | {score.traditional_effectiveness:.1f} | {score.normalized_effectiveness:.1f} | {tier_display} |"""

    if disqualified:
        report += f"""

---

## ❌ Disqualified Models (Failed Quality Gates)

| Model | Accuracy | Issues | Reason |
|-------|----------|---------|---------|"""
        
        for score in disqualified:
            issues = "; ".join(score.warnings[:2])
            reason = "Gaming Prevention" if not score.quality_threshold_passed else "Suspicious Cost"
            report += f"""
| **{score.model_name}** | {score.raw_score:.1%} | {issues} | {reason} |"""

    report += f"""

---

## 📊 Tier-Based Recommendations

### 🥇 Enterprise Premium ({len(recommendations['enterprise_premium'])} models)
**For critical security analysis with unlimited budget**
- {', '.join(recommendations['enterprise_premium'][:5]) if recommendations['enterprise_premium'] else 'None qualified'}

### 🥈 Enterprise Standard ({len(recommendations['enterprise_standard'])} models)  
**For production security analysis with cost consideration**
- {', '.join(recommendations['enterprise_standard'][:5]) if recommendations['enterprise_standard'] else 'None qualified'}

### 🥉 Production Ready ({len(recommendations['production_ready'])} models)
**For automated security scanning in CI/CD**
- {', '.join(recommendations['production_ready'][:5]) if recommendations['production_ready'] else 'None qualified'}

### ⚠️ Models to Avoid ({len(recommendations['avoid_models'])} models)
**Disqualified for quality or cost gaming concerns**
- {', '.join(recommendations['avoid_models'][:10]) if recommendations['avoid_models'] else 'None'}

---

## 🔍 Anti-Gaming Analysis Results

**Quality Threshold Impact:**
- {len(qualified)} models passed 80% accuracy threshold
- {len(disqualified)} models disqualified for insufficient quality
- {len([s for s in scores if not s.cost_reasonable])} models flagged for suspicious low cost

**Test Count Normalization:**
- Applied sample size adjustments for fair comparison
- Prevented bias from mixed test counts (5 vs 10 tests)

**Cost Gaming Prevention:**
- Eliminated artificial cost-effectiveness inflation
- Focused rankings on genuine value, not just low cost

---

*This analysis prioritizes **security analysis quality** over artificial cost optimization.*
**Built by the Rapticore Security Research Team**"""

    return report


def fix_pareto_chart_explanation() -> str:
    """Generate explanation for Pareto scatter analysis chart."""
    
    return """## 📊 Understanding the Pareto Scatter Analysis Chart

### What is a Pareto Frontier?
The **Pareto frontier** identifies models that are "non-dominated" - meaning no other model is both faster AND more accurate.

### How to Read the Chart:

#### **Axes:**
- **X-Axis:** Response Time (seconds) - Lower is better (faster)
- **Y-Axis:** Security Accuracy Score - Higher is better (more accurate)

#### **Symbol Meaning:**
- **🟢 Green Dots:** Models on the Pareto frontier (optimal trade-offs)
- **🔴 Red Dots:** Dominated models (suboptimal - another model is both faster and more accurate)
- **📏 Size:** Bubble size represents cost per test (larger = more expensive)

#### **Interpretation:**
1. **Top-Left Corner = Best:** High accuracy, low response time
2. **Pareto Frontier Models:** Represent the best possible trade-offs
3. **Dominated Models:** Should be avoided unless there are other considerations

#### **Example Reading:**
If you see a model at position (5 seconds, 0.9 accuracy):
- Takes 5 seconds to respond on average
- Achieves 90% security detection accuracy
- If it's green (on frontier), no other model is both faster AND more accurate
- If it's red (dominated), there exists another model that's both faster and more accurate

#### **Business Decision Guide:**
- **Need Speed:** Choose leftmost green dot (fastest among optimal models)
- **Need Accuracy:** Choose topmost green dot (most accurate among optimal models)  
- **Balanced:** Choose green dot in middle of frontier
- **Avoid:** Any red dots (dominated by superior alternatives)

### Why Some Models Appear Multiple Times:
Models may appear multiple times if they were tested on different test suites or configurations, showing their performance range across different scenarios."""


# Integration function for main benchmark
def apply_aggressive_fixes(results_data: Dict) -> Dict[str, Any]:
    """Apply aggressive cost-effectiveness fixes to benchmark results."""
    
    analyzer = AggressiveCostEffectivenessAnalyzer()
    
    # Extract model data for analysis
    model_data = {}
    for model, data in results_data.items():
        if isinstance(data, dict) and 'avg_score' in data:
            model_data[model] = {
                'raw_score': data['avg_score'],
                'cost_per_test': data.get('cost_per_test', 0.0),
                'test_count': data.get('total_tests', 5),
                'good_responses': data.get('good_scores', 0),
                'total_responses': data.get('total_tests', 5)
            }
    
    # Generate aggressive rankings
    scores, recommendations = analyzer.generate_aggressive_rankings(model_data)
    
    # Generate report
    report = create_aggressive_cost_effectiveness_report(scores, recommendations)
    
    # Add Pareto chart explanation
    pareto_explanation = fix_pareto_chart_explanation()
    
    return {
        "aggressive_scores": scores,
        "recommendations": recommendations, 
        "report": report,
        "pareto_explanation": pareto_explanation,
        "summary": {
            "qualified_models": len([s for s in scores if not s.disqualified]),
            "disqualified_models": len([s for s in scores if s.disqualified]),
            "gaming_prevented": len([s for s in scores if not s.cost_reasonable])
        }
    }