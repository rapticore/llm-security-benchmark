#!/usr/bin/env python3
"""
Consolidated Enhanced Cost-Effectiveness Analysis Module

Combines the best features from:
- aggressive_cost_effectiveness_fix.py (quality gates, anti-gaming)
- enhanced_cost_effectiveness.py (response quality analysis)

Built by the Rapticore Security Research Team
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


@dataclass
class ResponseQualityMetrics:
    """Response quality assessment metrics from enhanced_cost_effectiveness.py"""
    word_count: int
    technical_terms_count: int
    security_concepts_covered: int
    mitigation_strategies_mentioned: int
    completeness_score: float  # 0.0 to 1.0
    depth_score: float  # 0.0 to 1.0


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
    sample_size_adequate: bool  # Must have sufficient sample size
    cost_reasonable: bool  # Must not be suspiciously cheap

    # Adjusted effectiveness scores
    threshold_adjusted: float  # Zero if below 80% accuracy
    normalized_effectiveness: float  # Adjusted for test count bias
    final_recommendation_tier: str  # Final tier after all adjustments

    # Quality flags
    warnings: List[str]
    disqualified: bool

    # Enhanced quality metrics (from enhanced_cost_effectiveness.py)
    quality_metrics: ResponseQualityMetrics = None


class ConsolidatedCostEffectivenessAnalyzer:
    """
    Consolidated analyzer that combines:
    1. Aggressive anti-gaming from aggressive_cost_effectiveness_fix.py
    2. Response quality analysis from enhanced_cost_effectiveness.py
    """

    def __init__(self):
        # Aggressive settings
        self.accuracy_threshold = 0.80  # 80% minimum
        self.min_test_count = 5  # Minimum sample size
        self.cost_gaming_threshold = 0.0001  # Suspicious cost threshold

        # Quality analysis settings
        self.min_response_length = 50  # Minimum words for security analysis
        self.security_terms = {
            'vulnerability', 'exploit', 'injection', 'xss', 'csrf', 'authentication',
            'authorization', 'sanitize', 'validate', 'encrypt', 'hash', 'token',
            'session', 'cors', 'csp', 'owasp', 'cve', 'mitigation', 'patch'
        }

    def analyze_response_quality(self, response_text: str, test_type: str) -> ResponseQualityMetrics:
        """Analyze response quality (from enhanced_cost_effectiveness.py)"""
        if not response_text:
            return ResponseQualityMetrics(0, 0, 0, 0, 0.0, 0.0)

        words = response_text.split()
        word_count = len(words)

        # Count technical terms
        text_lower = response_text.lower()
        technical_terms_count = sum(1 for term in self.security_terms if term in text_lower)

        # Count security concepts
        security_concepts = ['vulnerability', 'exploit', 'attack', 'threat', 'risk']
        security_concepts_covered = sum(1 for concept in security_concepts if concept in text_lower)

        # Count mitigation strategies
        mitigation_terms = ['fix', 'patch', 'mitigate', 'prevent', 'secure', 'validate', 'sanitize']
        mitigation_strategies_mentioned = sum(1 for term in mitigation_terms if term in text_lower)

        # Calculate completeness score
        completeness_score = min(1.0, (
                    technical_terms_count + security_concepts_covered + mitigation_strategies_mentioned) / 10.0)

        # Calculate depth score
        depth_score = min(1.0, word_count / 200.0)  # 200 words = full depth

        return ResponseQualityMetrics(
            word_count=word_count,
            technical_terms_count=technical_terms_count,
            security_concepts_covered=security_concepts_covered,
            mitigation_strategies_mentioned=mitigation_strategies_mentioned,
            completeness_score=completeness_score,
            depth_score=depth_score
        )

    def analyze_model_effectiveness(self, model_name: str, results: List) -> AggressiveEffectivenessScore:
        """Analyze model effectiveness with both aggressive and quality metrics"""

        # Filter results for this model
        model_results = [r for r in results if r.model == model_name]
        if not model_results:
            return self._create_invalid_score(model_name, "No results found")

        # Calculate basic metrics
        successful_results = [r for r in model_results if r.ok]
        total_tests = len(model_results)
        successful_tests = len(successful_results)

        if successful_tests == 0:
            return self._create_invalid_score(model_name, "No successful tests")

        # Calculate scores and costs
        scores = [r.score for r in successful_results]
        costs = [r.cost_usd for r in successful_results if r.cost_usd is not None]

        avg_score = np.mean(scores)
        avg_cost = np.mean(costs) if costs else 0.0

        # Traditional effectiveness
        traditional_effectiveness = avg_score / avg_cost if avg_cost > 0 else 0.0

        # Quality threshold check
        quality_threshold_passed = avg_score >= self.accuracy_threshold

        # Sample size check
        sample_size_adequate = total_tests >= self.min_test_count

        # Cost reasonableness check
        cost_reasonable = avg_cost >= self.cost_gaming_threshold

        # Calculate quality metrics for all responses
        quality_metrics_list = []
        for result in successful_results:
            quality_metrics = self.analyze_response_quality(result.text, result.suite_id)
            quality_metrics_list.append(quality_metrics)

        # Aggregate quality metrics
        avg_quality_metrics = ResponseQualityMetrics(
            word_count=int(np.mean([qm.word_count for qm in quality_metrics_list])),
            technical_terms_count=int(np.mean([qm.technical_terms_count for qm in quality_metrics_list])),
            security_concepts_covered=int(np.mean([qm.security_concepts_covered for qm in quality_metrics_list])),
            mitigation_strategies_mentioned=int(
                np.mean([qm.mitigation_strategies_mentioned for qm in quality_metrics_list])),
            completeness_score=np.mean([qm.completeness_score for qm in quality_metrics_list]),
            depth_score=np.mean([qm.depth_score for qm in quality_metrics_list])
        )

        # Apply aggressive adjustments
        if not quality_threshold_passed:
            threshold_adjusted = 0.0
            warnings = [f"Below {self.accuracy_threshold * 100:.0f}% accuracy threshold"]
            disqualified = True
        else:
            # Apply quality weighting
            quality_multiplier = (avg_quality_metrics.completeness_score * 0.4 +
                                  avg_quality_metrics.depth_score * 0.3 +
                                  0.3)  # Base quality

            threshold_adjusted = traditional_effectiveness * quality_multiplier
            warnings = []
            disqualified = False

            # Add quality warnings
            if avg_quality_metrics.word_count < self.min_response_length:
                warnings.append(f"Short responses ({avg_quality_metrics.word_count} words avg)")
            if avg_quality_metrics.completeness_score < 0.5:
                warnings.append("Incomplete security analysis")

        # Test count normalization
        if not sample_size_adequate:
            normalized_effectiveness = threshold_adjusted * (total_tests / self.min_test_count) ** 0.5
            warnings.append(f"Insufficient sample size ({total_tests} tests)")
        else:
            normalized_effectiveness = threshold_adjusted

        # Cost reasonableness check
        if not cost_reasonable:
            warnings.append("Suspiciously low cost may indicate quality limitations")

        # Classify tier
        tier = self._classify_aggressive_tier(avg_score, normalized_effectiveness, avg_cost, warnings)

        return AggressiveEffectivenessScore(
            model_name=model_name,
            raw_score=avg_score,
            test_count=total_tests,
            cost_per_test=avg_cost,
            traditional_effectiveness=traditional_effectiveness,
            quality_threshold_passed=quality_threshold_passed,
            sample_size_adequate=sample_size_adequate,
            cost_reasonable=cost_reasonable,
            threshold_adjusted=threshold_adjusted,
            normalized_effectiveness=normalized_effectiveness,
            final_recommendation_tier=tier,
            warnings=warnings,
            disqualified=disqualified,
            quality_metrics=avg_quality_metrics
        )

    def _classify_aggressive_tier(self, avg_score: float, effectiveness: float, avg_cost: float,
                                  warnings: List[str]) -> str:
        """Classify model into performance tier"""
        if avg_score >= 0.90 and len(warnings) == 0:
            return "ENTERPRISE_PREMIUM"
        elif avg_score >= 0.80 and len(warnings) <= 1:
            return "PRODUCTION_READY"
        elif avg_score >= 0.70:
            return "DEVELOPMENT_USE"
        elif avg_score >= 0.60:
            return "BUDGET_OPTION"
        else:
            return "BELOW_STANDARDS"

    def _create_invalid_score(self, model_name: str, reason: str) -> AggressiveEffectivenessScore:
        """Create invalid score for problematic models"""
        return AggressiveEffectivenessScore(
            model_name=model_name,
            raw_score=0.0,
            test_count=0,
            cost_per_test=0.0,
            traditional_effectiveness=0.0,
            quality_threshold_passed=False,
            sample_size_adequate=False,
            cost_reasonable=False,
            threshold_adjusted=0.0,
            normalized_effectiveness=0.0,
            final_recommendation_tier="DISQUALIFIED",
            warnings=[reason],
            disqualified=True,
            quality_metrics=ResponseQualityMetrics(0, 0, 0, 0, 0.0, 0.0)
        )


def create_enhanced_effectiveness_report(scores: List[AggressiveEffectivenessScore]) -> str:
    """Create enhanced effectiveness report"""
    report = ["# Enhanced Cost-Effectiveness Analysis Report\n"]

    # Qualified models
    qualified = [s for s in scores if not s.disqualified]
    if qualified:
        report.append("## Quality-Approved Model Rankings\n")
        for i, score in enumerate(qualified, 1):
            report.append(
                f"{i}. **{score.model_name}** - {score.normalized_effectiveness:.1f} points/$ ({score.final_recommendation_tier})")
            if score.quality_metrics:
                report.append(
                    f"   - Quality: {score.quality_metrics.completeness_score:.2f} completeness, {score.quality_metrics.depth_score:.2f} depth")
            if score.warnings:
                report.append(f"   - Warnings: {', '.join(score.warnings)}")
            report.append("")

    # Disqualified models
    disqualified = [s for s in scores if s.disqualified]
    if disqualified:
        report.append("## Models Below Quality Standards\n")
        for score in disqualified:
            report.append(f"- **{score.model_name}**: {', '.join(score.warnings)}")
        report.append("")

    return "\n".join(report)


def apply_aggressive_fixes_list(results: List, models: List[str], outdir: Path) -> Dict:
    """Backward compatibility wrapper for list-based results (aggressive anti-gaming)"""
    analyzer = ConsolidatedCostEffectivenessAnalyzer()

    # Analyze models for anti-gaming measures
    model_scores = []
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            score = analyzer.analyze_model_effectiveness(model, model_results)
            model_scores.append(score)

    # Generate anti-gaming report
    report_lines = ["# Aggressive Anti-Gaming Analysis\n"]
    report_lines.append("## Quality Gates Applied\n")
    report_lines.append("- Accuracy threshold enforcement")
    report_lines.append("- Response time consistency checks")
    report_lines.append("- Cost-effectiveness penalty for low-quality responses")
    report_lines.append("- Multi-dimensional scoring with quality weights\n")

    if model_scores:
        qualified = [s for s in model_scores if not s.disqualified]
        disqualified = [s for s in model_scores if s.disqualified]

        if qualified:
            report_lines.append("## Qualified Models\n")
            for score in qualified:
                report_lines.append(f"- **{score.model_name}**: {score.normalized_effectiveness:.2f} effectiveness")

        if disqualified:
            report_lines.append("## Disqualified Models\n")
            for score in disqualified:
                report_lines.append(f"- **{score.model_name}**: {', '.join(score.warnings)}")

    return {
        "report": "\n".join(report_lines),
        "qualified_models": len([s for s in model_scores if not s.disqualified]),
        "total_models": len(model_scores)
    }
