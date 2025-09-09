#!/usr/bin/env python3
"""
Enhanced Executive Summary Generator
Implements comprehensive quality-first reporting with strict thresholds and tiered recommendations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class QualityGate:
    """Quality gate thresholds for model evaluation"""
    accuracy_min: float = 0.80
    success_min: float = 0.98


@dataclass
class SpeedTargets:
    """Speed performance targets"""
    p95_triage_s: float = 10.0
    p95_ci_s: float = 20.0


@dataclass
class CostCaps:
    """Cost ceiling thresholds"""
    triage_max_usd: float = 0.01


@dataclass
class FairnessSettings:
    """Fairness and reliability requirements"""
    require_equal_counts: bool = True
    min_tests_per_slice: int = 30


@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics"""
    model_name: str
    total_tests: int
    successful_tests: int
    success_rate: float
    avg_score: float
    median_score: float
    score_std_dev: float
    avg_response_time: float
    p95_response_time: Optional[float]
    avg_cost_per_test: float
    total_cost: float
    by_slice: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class NearestFitAnalysis:
    """Analysis of nearest-fit model when no model meets thresholds"""
    model_name: str
    accuracy_shortfall: float
    success_shortfall: float
    speed_shortfall: float
    cost_excess: float
    total_shortfall: float
    tuning_recommendations: List[str]


class EnhancedExecutiveSummaryGenerator:
    """
    Generates comprehensive, quality-first executive summaries with strict thresholds,
    tiered recommendations, and always-recommend rule.
    """
    
    def __init__(self, 
                 quality_gate: QualityGate = None,
                 speed_targets: SpeedTargets = None,
                 cost_caps: CostCaps = None,
                 fairness: FairnessSettings = None):
        self.quality_gate = quality_gate or QualityGate()
        self.speed_targets = speed_targets or SpeedTargets()
        self.cost_caps = cost_caps or CostCaps()
        self.fairness = fairness or FairnessSettings()
    
    def generate_executive_summary(self, 
                                 analysis_metadata: Dict[str, Any],
                                 model_comparison: Dict[str, Dict[str, Any]],
                                 aggregate_statistics: Dict[str, Any]) -> str:
        """
        Generate comprehensive executive summary following the enhanced requirements.
        
        Args:
            analysis_metadata: { total_tests, models_evaluated, timestamp }
            model_comparison: { <model_name>: { total_tests, successful_tests, success_rate, ... } }
            aggregate_statistics: { overall_success_rate, avg_score_across_models, ... }
        
        Returns:
            Markdown-formatted executive summary
        """
        
        # Convert model comparison to ModelMetrics objects
        models = []
        for model_name, metrics in model_comparison.items():
            models.append(ModelMetrics(
                model_name=model_name,
                total_tests=metrics.get('total_tests', 0),
                successful_tests=metrics.get('successful_tests', 0),
                success_rate=metrics.get('success_rate', 0.0),
                avg_score=metrics.get('avg_score', 0.0),
                median_score=metrics.get('median_score', 0.0),
                score_std_dev=metrics.get('score_std_dev', 0.0),
                avg_response_time=metrics.get('avg_response_time', 0.0),
                p95_response_time=metrics.get('p95_response_time'),
                avg_cost_per_test=metrics.get('avg_cost_per_test', 0.0),
                total_cost=metrics.get('total_cost', 0.0),
                by_slice=metrics.get('by_slice')
            ))
        
        # Apply quality gate to determine eligible models
        eligible_models = self._apply_quality_gate(models)
        
        # Generate executive overview
        overview = self._generate_executive_overview(models, eligible_models)
        
        # Generate summary table
        summary_table = self._generate_summary_table(models)
        
        # Generate leaders by dimension
        leaders = self._generate_leaders_by_dimension(models, eligible_models)
        
        # Generate tiered recommendations
        tiered_recs = self._generate_tiered_recommendations(models, eligible_models)
        
        # Generate per-slice analysis if available
        slice_analysis = self._generate_slice_analysis(models)
        
        # Generate caveats
        caveats = self._generate_caveats(models, analysis_metadata)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(models, eligible_models)
        
        # Generate next experiments
        next_experiments = self._generate_next_experiments(models, eligible_models)
        
        # Combine all sections
        summary = f"""# 🛡️ LLM Security Benchmark - Executive Summary

**Analysis Date:** {analysis_metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
**Total Tests:** {analysis_metadata.get('total_tests', 0):,}
**Models Evaluated:** {analysis_metadata.get('models_evaluated', len(models))}

{overview}

{summary_table}

{leaders}

{tiered_recs}

{slice_analysis}

{caveats}

{recommendations}

{next_experiments}

---
*Generated by Enhanced Executive Summary Generator v2.0*
*Quality-first methodology with strict thresholds and always-recommend rule*
"""
        
        return summary
    
    def _apply_quality_gate(self, models: List[ModelMetrics]) -> List[ModelMetrics]:
        """Apply quality gate to determine eligible models"""
        eligible = []
        for model in models:
            if (model.avg_score >= self.quality_gate.accuracy_min and 
                model.success_rate >= self.quality_gate.success_min):
                eligible.append(model)
        return eligible
    
    def _generate_executive_overview(self, models: List[ModelMetrics], 
                                   eligible_models: List[ModelMetrics]) -> str:
        """Generate executive overview with 4-6 key bullets"""
        
        # Highest Accuracy (eligible preferred)
        if eligible_models:
            best_accuracy = max(eligible_models, key=lambda x: x.avg_score)
            accuracy_bullet = f"- **Highest Accuracy:** {best_accuracy.model_name} with {best_accuracy.avg_score:.1%} accuracy and {best_accuracy.success_rate:.1%} success"
        else:
            best_accuracy = max(models, key=lambda x: x.avg_score)
            nearest_fit = self._analyze_nearest_fit(best_accuracy)
            accuracy_bullet = f"- **Highest Accuracy (Nearest-Fit):** {best_accuracy.model_name} with {best_accuracy.avg_score:.1%} accuracy (misses quality gate by {nearest_fit.accuracy_shortfall:.1%})"
        
        # Most Reliable (highest success rate, tie-break accuracy)
        most_reliable = max(models, key=lambda x: (x.success_rate, x.avg_score))
        reliability_bullet = f"- **Most Reliable:** {most_reliable.model_name} with {most_reliable.success_rate:.1%} success rate"
        
        # Fastest Eligible
        if eligible_models:
            fastest_eligible = min(eligible_models, key=lambda x: x.p95_response_time or x.avg_response_time)
            speed_label = "p95" if fastest_eligible.p95_response_time else "mean only"
            speed_value = fastest_eligible.p95_response_time or fastest_eligible.avg_response_time
            speed_bullet = f"- **Fastest Eligible:** {fastest_eligible.model_name} with {speed_value:.2f}s {speed_label}"
        else:
            fastest = min(models, key=lambda x: x.p95_response_time or x.avg_response_time)
            speed_label = "p95" if fastest.p95_response_time else "mean only"
            speed_value = fastest.p95_response_time or fastest.avg_response_time
            nearest_fit = self._analyze_nearest_fit(fastest)
            speed_bullet = f"- **Fastest (Nearest-Fit):** {fastest.model_name} with {speed_value:.2f}s {speed_label} (needs tuning to qualify)"
        
        # Best Value (quality-gated)
        if eligible_models:
            best_value = min(eligible_models, key=lambda x: (x.avg_cost_per_test, -x.avg_score, x.p95_response_time or x.avg_response_time))
            value_bullet = f"- **Best Value:** {best_value.model_name} at ${best_value.avg_cost_per_test:.5f}/test with {best_value.avg_score:.1%} accuracy"
        else:
            best_value = min(models, key=lambda x: x.avg_cost_per_test)
            nearest_fit = self._analyze_nearest_fit(best_value)
            value_bullet = f"- **Best Value (Nearest-Fit):** {best_value.model_name} at ${best_value.avg_cost_per_test:.5f}/test (needs quality improvements)"
        
        # Fairness note
        test_counts = [m.total_tests for m in models]
        if len(set(test_counts)) == 1:
            fairness_bullet = "- **Fairness:** ✅ Equal test counts and settings across all models"
        else:
            min_tests, max_tests = min(test_counts), max(test_counts)
            fairness_bullet = f"- **Fairness:** ⚠️ Mismatched test counts ({min_tests}-{max_tests} range) - comparison reliability concerns"
        
        return f"""## Executive Overview

{accuracy_bullet}
{reliability_bullet}
{speed_bullet}
{value_bullet}
{fairness_bullet}"""
    
    def _generate_summary_table(self, models: List[ModelMetrics]) -> str:
        """Generate clean summary table"""
        
        # Calculate median test count for flagging
        test_counts = [m.total_tests for m in models]
        median_tests = statistics.median(test_counts)
        
        table_rows = []
        for model in sorted(models, key=lambda x: x.avg_score, reverse=True):
            # Flag models with different test counts
            test_flag = "⚠️" if model.total_tests != median_tests else ""
            
            # Format latency (prefer p95, fallback to mean)
            if model.p95_response_time:
                latency = f"{model.p95_response_time:.2f}s"
            else:
                latency = f"{model.avg_response_time:.2f}s (mean only)"
            
            table_rows.append(f"| {model.model_name} {test_flag} | {model.total_tests} | {model.avg_score:.1%} | {model.success_rate:.1%} | {latency} | ${model.avg_cost_per_test:.5f} |")
        
        return f"""## Summary Table

| Model | Tests | Accuracy | Success | Latency (p95 or mean) | Cost/Test |
|-------|-------|----------|---------|----------------------|-----------|
{chr(10).join(table_rows)}"""
    
    def _generate_leaders_by_dimension(self, models: List[ModelMetrics], 
                                     eligible_models: List[ModelMetrics]) -> str:
        """Generate leaders by dimension (accuracy, speed, cost)"""
        
        # Accuracy Top 3
        accuracy_leaders = sorted(models, key=lambda x: x.avg_score, reverse=True)[:3]
        accuracy_section = "### Accuracy Top 3\n"
        for i, model in enumerate(accuracy_leaders, 1):
            accuracy_section += f"{i}. **{model.model_name}:** {model.avg_score:.1%}\n"
        
        # Speed Top 3 (p95 preferred, label if mean only)
        speed_leaders = sorted(models, key=lambda x: x.p95_response_time or x.avg_response_time)[:3]
        speed_section = "### Speed Top 3\n"
        for i, model in enumerate(speed_leaders, 1):
            if model.p95_response_time:
                speed_section += f"{i}. **{model.model_name}:** {model.p95_response_time:.2f}s (p95)\n"
            else:
                speed_section += f"{i}. **{model.model_name}:** {model.avg_response_time:.2f}s (mean only)\n"
        
        # Cost/Test Top 3 (eligible only)
        if eligible_models:
            cost_leaders = sorted(eligible_models, key=lambda x: x.avg_cost_per_test)[:3]
            cost_section = "### Cost/Test Top 3 (Eligible Only)\n"
            for i, model in enumerate(cost_leaders, 1):
                cost_section += f"{i}. **{model.model_name}:** ${model.avg_cost_per_test:.5f}\n"
        else:
            cost_section = "### Cost/Test Top 3\n*No eligible models - see Nearest-Fit in tiered recommendations*"
        
        return f"""## Leaders by Dimension

{accuracy_section}

{speed_section}

{cost_section}"""
    
    def _generate_tiered_recommendations(self, models: List[ModelMetrics], 
                                       eligible_models: List[ModelMetrics]) -> str:
        """Generate tiered recommendations with always-recommend rule"""
        
        # PR/Commit Triage
        triage_targets = f"accuracy ≥ {self.quality_gate.accuracy_min:.1%}, p95 ≤ {self.speed_targets.p95_triage_s:.1f}s, cost ≤ ${self.cost_caps.triage_max_usd:.3f}"
        triage_pick = self._find_tier_pick(eligible_models, models, 
                                         accuracy_min=self.quality_gate.accuracy_min,
                                         speed_max=self.speed_targets.p95_triage_s,
                                         cost_max=self.cost_caps.triage_max_usd)
        
        # CI Gate
        ci_accuracy_min = self.quality_gate.accuracy_min + 0.10
        ci_targets = f"accuracy ≥ {ci_accuracy_min:.1%}, p95 ≤ {self.speed_targets.p95_ci_s:.1f}s"
        ci_pick = self._find_tier_pick(eligible_models, models,
                                     accuracy_min=ci_accuracy_min,
                                     speed_max=self.speed_targets.p95_ci_s)
        
        # Audit/High-Signal
        audit_pick = self._find_audit_pick(eligible_models, models)
        
        return f"""## Tiered Recommendations

### PR/Commit Triage
**Targets:** {triage_targets}
**Primary Pick:** {triage_pick['primary']}
{triage_pick['tuning']}

### CI Gate  
**Targets:** {ci_targets}
**Primary Pick:** {ci_pick['primary']}
{ci_pick['tuning']}

### Audit/High-Signal
**Targets:** Highest accuracy/coverage; speed and cost secondary
**Primary Pick:** {audit_pick['primary']}
{audit_pick['tuning']}"""
    
    def _generate_slice_analysis(self, models: List[ModelMetrics]) -> str:
        """Generate per-language/per-test-type analysis if by_slice exists"""
        
        slice_sections = []
        
        for model in models:
            if not model.by_slice:
                continue
                
            for slice_name, slice_metrics in model.by_slice.items():
                if slice_metrics.get('total_tests', 0) < self.fairness.min_tests_per_slice:
                    continue
                    
                # Find top 3 by accuracy for this slice
                slice_models = []
                for m in models:
                    if m.by_slice and slice_name in m.by_slice:
                        slice_models.append((m.model_name, m.by_slice[slice_name]))
                
                if not slice_models:
                    continue
                    
                slice_models.sort(key=lambda x: x[1].get('avg_score', 0), reverse=True)
                
                slice_section = f"### {slice_name}\n"
                slice_section += "**Top 3 by Accuracy:**\n"
                for i, (model_name, metrics) in enumerate(slice_models[:3], 1):
                    n = metrics.get('total_tests', 0)
                    accuracy = metrics.get('avg_score', 0)
                    p95 = metrics.get('p95_response_time')
                    cost = metrics.get('avg_cost_per_test', 0)
                    
                    latency = f"{p95:.2f}s" if p95 else f"{metrics.get('avg_response_time', 0):.2f}s (mean)"
                    slice_section += f"{i}. **{model_name}:** {accuracy:.1%} accuracy, {latency}, ${cost:.5f}/test (n={n})\n"
                
                slice_sections.append(slice_section)
        
        if slice_sections:
            return f"""## Per-Slice Analysis

{chr(10).join(slice_sections)}"""
        else:
            return ""
    
    def _generate_caveats(self, models: List[ModelMetrics], 
                         analysis_metadata: Dict[str, Any]) -> str:
        """Generate caveats about data gaps and limitations"""
        
        caveats = []
        
        # Check for missing p95
        missing_p95 = [m.model_name for m in models if m.p95_response_time is None]
        if missing_p95:
            caveats.append(f"Missing p95 latency data for: {', '.join(missing_p95)} (using mean only)")
        
        # Check for uneven test counts
        test_counts = [m.total_tests for m in models]
        if len(set(test_counts)) > 1:
            caveats.append(f"Uneven test counts across models ({min(test_counts)}-{max(test_counts)} range)")
        
        # Check for missing confidence intervals
        caveats.append("Confidence intervals not provided - consider bootstrap analysis for statistical rigor")
        
        # Note cost consideration policy
        caveats.append("Cost analysis applied only after passing quality gates")
        
        return f"""## Caveats

{chr(10).join(f"- {caveat}" for caveat in caveats)}"""
    
    def _generate_recommendations(self, models: List[ModelMetrics], 
                                eligible_models: List[ModelMetrics]) -> str:
        """Generate comprehensive recommendations section"""
        
        return """## Recommendations

### Deployment Policy
- Use tiered recommendations for each pipeline stage per "Tiered Recommendations" above
- Enforce quality-first gates before any cost-based decisions
- Apply "Nearest-Fit" only as temporary stopgap with defined tuning tasks and re-test deadline

### Tuning to Qualify
- Cap max_output_tokens / require terse JSON responses
- Lower temperature for more deterministic outputs
- Constrain context window to essential content only
- Reuse caches where possible; set strict timeouts
- Add structured prompts/contracts for determinism
- Standardize system messages across models

### Measurement & Fairness
- Re-run on common subset with equal n per model
- Report micro vs macro averages
- Collect p95 and bootstrap confidence intervals
- Include non-response/timeouts/format-fails in reliability metrics

### Per-Slice Strategy
- Maintain language × test-type leaderboards
- Tighten thresholds for safety-critical slices (OWASP/SAST)
- Track "cost per correct CRITICAL finding" where labels exist

### Cost Guardrails
- Define budget ceilings per tier
- Monitor "cost per passing test"
- Alert on cost drift patterns

### Re-run Plan
- Schedule periodic refresh on identical seeds/prompts
- Compare performance deltas over time
- Promote/demote models by slice based on sustained performance"""
    
    def _generate_next_experiments(self, models: List[ModelMetrics], 
                                 eligible_models: List[ModelMetrics]) -> str:
        """Generate next experiments recommendations"""
        
        return """## Next Experiments

- **Common subset fairness rerun:** Equal test counts with p95 & confidence intervals
- **Cost per correct CRITICAL detection:** Ground truth analysis where available
- **Ensemble approach:** Fast triage → escalate uncertain/high-risk to quality-gated models
- **Prompt optimization:** Length/token controls to hit speed targets without harming accuracy
- **Slice-specific thresholds:** Language × test-type leaderboards in dashboards"""
    
    def _find_tier_pick(self, eligible_models: List[ModelMetrics], 
                       all_models: List[ModelMetrics],
                       accuracy_min: float = None,
                       speed_max: float = None,
                       cost_max: float = None) -> Dict[str, str]:
        """Find primary pick for a tier, with nearest-fit fallback"""
        
        # Filter eligible models by additional criteria
        tier_eligible = eligible_models.copy()
        
        if accuracy_min is not None:
            tier_eligible = [m for m in tier_eligible if m.avg_score >= accuracy_min]
        
        if speed_max is not None:
            tier_eligible = [m for m in tier_eligible if (m.p95_response_time or m.avg_response_time) <= speed_max]
        
        if cost_max is not None:
            tier_eligible = [m for m in tier_eligible if m.avg_cost_per_test <= cost_max]
        
        if tier_eligible:
            # Found eligible model
            primary = min(tier_eligible, key=lambda x: (x.avg_cost_per_test, -x.avg_score, x.p95_response_time or x.avg_response_time))
            return {
                'primary': f"{primary.model_name} (meets all criteria)",
                'tuning': ""
            }
        else:
            # Find nearest-fit
            nearest_fit = self._find_nearest_fit(all_models, accuracy_min, speed_max, cost_max)
            return {
                'primary': f"{nearest_fit.model_name} (Nearest-Fit)",
                'tuning': f"**Tuning to qualify:** {', '.join(nearest_fit.tuning_recommendations)}"
            }
    
    def _find_audit_pick(self, eligible_models: List[ModelMetrics], 
                        all_models: List[ModelMetrics]) -> Dict[str, str]:
        """Find audit/high-signal pick (highest accuracy, tie-break reliability)"""
        
        if eligible_models:
            primary = max(eligible_models, key=lambda x: (x.avg_score, x.success_rate, -(x.p95_response_time or x.avg_response_time)))
            return {
                'primary': f"{primary.model_name} (highest accuracy: {primary.avg_score:.1%})",
                'tuning': ""
            }
        else:
            primary = max(all_models, key=lambda x: (x.avg_score, x.success_rate))
            nearest_fit = self._analyze_nearest_fit(primary)
            return {
                'primary': f"{primary.model_name} (Nearest-Fit: {primary.avg_score:.1%} accuracy)",
                'tuning': f"**Tuning to qualify:** {', '.join(nearest_fit.tuning_recommendations)}"
            }
    
    def _find_nearest_fit(self, models: List[ModelMetrics], 
                         accuracy_min: float = None,
                         speed_max: float = None,
                         cost_max: float = None) -> NearestFitAnalysis:
        """Find nearest-fit model with minimal total shortfall"""
        
        best_fit = None
        best_shortfall = float('inf')
        
        for model in models:
            accuracy_shortfall = max(0, (accuracy_min or 0) - model.avg_score) if accuracy_min else 0
            success_shortfall = max(0, self.quality_gate.success_min - model.success_rate)
            speed_shortfall = max(0, (model.p95_response_time or model.avg_response_time) - (speed_max or float('inf')))
            cost_excess = max(0, model.avg_cost_per_test - (cost_max or float('inf')))
            
            total_shortfall = accuracy_shortfall + success_shortfall + speed_shortfall + cost_excess
            
            if total_shortfall < best_shortfall:
                best_shortfall = total_shortfall
                best_fit = model
                best_analysis = NearestFitAnalysis(
                    model_name=model.model_name,
                    accuracy_shortfall=accuracy_shortfall,
                    success_shortfall=success_shortfall,
                    speed_shortfall=speed_shortfall,
                    cost_excess=cost_excess,
                    total_shortfall=total_shortfall,
                    tuning_recommendations=self._generate_tuning_recommendations(
                        accuracy_shortfall, success_shortfall, speed_shortfall, cost_excess
                    )
                )
        
        return best_analysis
    
    def _analyze_nearest_fit(self, model: ModelMetrics) -> NearestFitAnalysis:
        """Analyze a specific model as nearest-fit"""
        
        accuracy_shortfall = max(0, self.quality_gate.accuracy_min - model.avg_score)
        success_shortfall = max(0, self.quality_gate.success_min - model.success_rate)
        speed_shortfall = max(0, (model.p95_response_time or model.avg_response_time) - self.speed_targets.p95_triage_s)
        cost_excess = max(0, model.avg_cost_per_test - self.cost_caps.triage_max_usd)
        
        return NearestFitAnalysis(
            model_name=model.model_name,
            accuracy_shortfall=accuracy_shortfall,
            success_shortfall=success_shortfall,
            speed_shortfall=speed_shortfall,
            cost_excess=cost_excess,
            total_shortfall=accuracy_shortfall + success_shortfall + speed_shortfall + cost_excess,
            tuning_recommendations=self._generate_tuning_recommendations(
                accuracy_shortfall, success_shortfall, speed_shortfall, cost_excess
            )
        )
    
    def _generate_tuning_recommendations(self, accuracy_shortfall: float,
                                       success_shortfall: float,
                                       speed_shortfall: float,
                                       cost_excess: float) -> List[str]:
        """Generate concrete tuning recommendations based on shortfalls"""
        
        recommendations = []
        
        if accuracy_shortfall > 0:
            recommendations.append(f"Improve accuracy by {accuracy_shortfall:.1%} (add structured prompts, lower temperature)")
        
        if success_shortfall > 0:
            recommendations.append(f"Improve success rate by {success_shortfall:.1%} (add retry logic, better error handling)")
        
        if speed_shortfall > 0:
            recommendations.append(f"Reduce latency by {speed_shortfall:.2f}s (cap tokens, terse JSON, smaller context)")
        
        if cost_excess > 0:
            recommendations.append(f"Reduce cost by ${cost_excess:.5f}/test (optimize prompts, reuse caches)")
        
        return recommendations


def create_enhanced_executive_summary(results: List, models: List[str], 
                                    outdir: Path, 
                                    quality_gate: QualityGate = None,
                                    speed_targets: SpeedTargets = None,
                                    cost_caps: CostCaps = None,
                                    fairness: FairnessSettings = None) -> str:
    """
    Create enhanced executive summary from benchmark results.
    
    Args:
        results: List of EnhancedRunResult objects
        models: List of model names tested
        outdir: Output directory for saving summary
        quality_gate: Quality thresholds (optional)
        speed_targets: Speed targets (optional) 
        cost_caps: Cost ceilings (optional)
        fairness: Fairness settings (optional)
    
    Returns:
        Path to generated summary file
    """
    
    # Convert results to analysis format
    analysis_metadata = {
        'total_tests': len(results),
        'models_evaluated': len(models),
        'timestamp': datetime.now().isoformat()
    }
    
    model_comparison = {}
    for model in models:
        model_results = [r for r in results if r.model == model]
        if model_results:
            scores = [r.score for r in model_results if r.ok]
            response_times = [r.elapsed_s for r in model_results if r.ok]
            costs = [r.cost_usd for r in model_results if r.cost_usd]
            
            model_comparison[model] = {
                'total_tests': len(model_results),
                'successful_tests': len([r for r in model_results if r.ok]),
                'success_rate': len([r for r in model_results if r.ok]) / len(model_results) if model_results else 0,
                'avg_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'score_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'p95_response_time': None,  # Would need to calculate from raw data
                'avg_cost_per_test': statistics.mean(costs) if costs else 0,
                'total_cost': sum(costs) if costs else 0
            }
    
    aggregate_statistics = {
        'overall_success_rate': statistics.mean([m['success_rate'] for m in model_comparison.values()]),
        'avg_score_across_models': statistics.mean([m['avg_score'] for m in model_comparison.values()])
    }
    
    # Generate summary
    generator = EnhancedExecutiveSummaryGenerator(quality_gate, speed_targets, cost_caps, fairness)
    summary = generator.generate_executive_summary(analysis_metadata, model_comparison, aggregate_statistics)
    
    # Save summary
    summary_path = outdir / "ENHANCED_EXECUTIVE_SUMMARY.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return str(summary_path)


if __name__ == "__main__":
    # Example usage
    print("Enhanced Executive Summary Generator")
    print("This module provides comprehensive, quality-first executive reporting")
    print("with strict thresholds, tiered recommendations, and always-recommend rule.")
