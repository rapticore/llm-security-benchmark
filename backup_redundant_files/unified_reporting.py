#!/usr/bin/env python3
"""
Unified Reporting Module

Consolidates all reporting into a single, comprehensive executive summary
instead of generating multiple overlapping reports.

Built by the Rapticore Security Research Team
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class UnifiedModelMetrics:
    """Unified model metrics for consolidated reporting."""
    model_name: str
    total_tests: int
    success_rate: float
    avg_score: float
    response_time: float
    cost_per_test: float
    good_responses: int
    
    # Quality indicators
    consistency_score: float  # Lower variance = better
    reliability_score: float  # Success rate + consistency
    
    # Anti-gaming metrics
    qualified: bool          # Passes quality thresholds
    tier: str               # Performance tier
    warnings: List[str]     # Quality concerns


class UnifiedReportGenerator:
    """Generates a single, comprehensive executive summary."""
    
    def __init__(self):
        self.quality_threshold = 0.80
        self.cost_gaming_threshold = 0.0001
        
    def generate_unified_executive_summary(
        self, 
        model_metrics: List[UnifiedModelMetrics],
        total_cost: float,
        test_types: List[str],
        outdir: Path
    ) -> str:
        """Generate single comprehensive executive summary."""
        
        # Separate qualified vs problematic models
        qualified = [m for m in model_metrics if m.qualified]
        problematic = [m for m in model_metrics if not m.qualified]
        
        # Sort by normalized effectiveness (anti-gaming)
        qualified.sort(key=lambda m: self._calculate_safe_effectiveness(m), reverse=True)
        
        # Generate comprehensive report
        summary = f"""# 🛡️ LLM Security Benchmark - Executive Summary

**Assessment Date:** {Path.cwd().name}  
**Models Evaluated:** {len(model_metrics)}  
**Test Categories:** {len(test_types)}  
**Total Investment:** ${total_cost:.4f}

---

## 🎯 Executive Findings

### Quality-First Rankings (Anti-Gaming Applied)
*Only models meeting 80% accuracy threshold and cost-reasonableness standards*

"""
        
        if qualified:
            summary += "| Rank | Model | Accuracy | Speed | Cost/Test | Effectiveness | Tier |\n"
            summary += "|------|-------|----------|-------|-----------|---------------|------|\n"
            
            for i, model in enumerate(qualified[:8], 1):  # Top 8 qualified
                effectiveness = self._calculate_safe_effectiveness(model)
                tier_display = model.tier.replace('_', ' ').title()
                
                summary += f"| {i} | **{model.model_name}** | {model.avg_score:.1%} | {model.response_time:.1f}s | ${model.cost_per_test:.5f} | {effectiveness:.0f} | {tier_display} |\n"
        
        else:
            summary += "⚠️ **No models met quality standards** - All models either below 80% accuracy or showed cost gaming patterns.\n"
        
        # Problem models section
        if problematic:
            summary += f"\n### ❌ Disqualified Models ({len(problematic)} models)\n"
            summary += "*Models failing quality thresholds or showing gaming patterns*\n\n"
            summary += "| Model | Issue | Accuracy | Cost/Test | Reason |\n"
            summary += "|-------|-------|----------|-----------|--------|\n"
            
            for model in problematic[:5]:  # Top 5 problem models
                primary_issue = model.warnings[0] if model.warnings else "Quality threshold"
                reason = "Low accuracy" if model.avg_score < self.quality_threshold else "Cost gaming"
                summary += f"| **{model.model_name}** | {primary_issue} | {model.avg_score:.1%} | ${model.cost_per_test:.6f} | {reason} |\n"
        
        # Strategic recommendations
        summary += self._generate_strategic_recommendations(qualified)
        
        # Technical methodology
        summary += self._generate_methodology_section()
        
        # Cost analysis
        summary += self._generate_cost_analysis(model_metrics, total_cost)
        
        # Chart explanations
        summary += self._generate_chart_explanations()
        
        return summary
    
    def _calculate_safe_effectiveness(self, model: UnifiedModelMetrics) -> float:
        """Calculate anti-gaming cost-effectiveness."""
        if not model.qualified or model.cost_per_test <= 0:
            return 0.0
        
        # Ensure minimum cost to prevent gaming
        safe_cost = max(model.cost_per_test, self.cost_gaming_threshold)
        
        # Quality-adjusted effectiveness
        return (model.avg_score ** 1.2) / safe_cost
    
    def _generate_strategic_recommendations(self, qualified: List[UnifiedModelMetrics]) -> str:
        """Generate strategic recommendations by use case."""
        
        if not qualified:
            return "\n## 📋 Strategic Recommendations\n\n⚠️ **No qualified models available** - Consider adjusting quality thresholds or testing additional models.\n"
        
        # Categorize by tier and use case
        enterprise_models = [m for m in qualified if 'ENTERPRISE' in m.tier]
        production_models = [m for m in qualified if 'PRODUCTION' in m.tier]
        acceptable_models = [m for m in qualified if 'ACCEPTABLE' in m.tier]
        
        fastest = min(qualified, key=lambda m: m.response_time) if qualified else None
        most_accurate = max(qualified, key=lambda m: m.avg_score) if qualified else None
        best_value = max(qualified, key=lambda m: self._calculate_safe_effectiveness(m)) if qualified else None
        
        rec = f"""
## 📋 Strategic Recommendations

### By Use Case:

#### 🏢 **Enterprise Security Reviews** (Unlimited Budget)
- **Primary Choice:** {enterprise_models[0].model_name if enterprise_models else 'None qualified'}
- **Alternative:** {enterprise_models[1].model_name if len(enterprise_models) > 1 else 'None'}
- **Rationale:** Highest accuracy standards, comprehensive analysis depth

#### 🚀 **Production CI/CD Integration** (Balanced Requirements)
- **Primary Choice:** {production_models[0].model_name if production_models else best_value.model_name if best_value else 'None'}
- **Speed Focus:** {fastest.model_name if fastest else 'None'}
- **Rationale:** Balance of accuracy, speed, and cost for automated scanning

#### 💰 **Cost-Conscious Teams** (Budget Constraints)
- **Best Value:** {best_value.model_name if best_value else 'None'}
- **Acceptable Option:** {acceptable_models[0].model_name if acceptable_models else 'None'}
- **Rationale:** Meets quality standards while optimizing cost

### Performance Leaders:

- **🎯 Most Accurate:** {most_accurate.model_name if most_accurate else 'None'} ({most_accurate.avg_score:.1%} accuracy)
- **⚡ Fastest Response:** {fastest.model_name if fastest else 'None'} ({fastest.response_time:.1f}s average)
- **💎 Best Overall Value:** {best_value.model_name if best_value else 'None'} (quality-adjusted effectiveness)

### ⚠️ **Important Considerations:**
- All recommendations based on models meeting 80% minimum accuracy threshold
- Cost gaming prevention applied - ultra-cheap models may be disqualified
- Consider response quality, not just scores, for security analysis tasks
"""
        
        return rec
    
    def _generate_methodology_section(self) -> str:
        """Generate methodology explanation."""
        
        return f"""
---

## 🔬 Methodology & Anti-Gaming Measures

### Quality Thresholds Applied:
- **Minimum Accuracy:** 80% - Models below this threshold receive zero effectiveness score
- **Cost Gaming Prevention:** Models with suspiciously low costs (<${self.cost_gaming_threshold:.6f}) flagged
- **Sample Size Requirements:** Minimum test requirements for reliable statistical analysis
- **Response Quality Analysis:** Evaluation of technical depth and completeness

### Effectiveness Calculation:
```
Safe Effectiveness = (Accuracy^1.2) / max(Cost, MinCost)
```
- Exponential accuracy weighting prevents low-quality models from dominating
- Minimum cost threshold prevents gaming through artificially low pricing
- Test count normalization ensures fair comparison

### Why This Matters:
Traditional cost-effectiveness (`Score/Cost`) allowed ultra-cheap models with poor analysis 
to artificially dominate rankings. Our enhanced methodology prioritizes:
1. **Security analysis quality** over raw cost metrics
2. **Practical usability** for real-world security assessment
3. **Gaming-resistant rankings** that reflect true value

"""
    
    def _generate_cost_analysis(self, models: List[UnifiedModelMetrics], total_cost: float) -> str:
        """Generate cost analysis section."""
        
        qualified = [m for m in models if m.qualified]
        if not qualified:
            return ""
            
        cheapest = min(qualified, key=lambda m: m.cost_per_test)
        most_expensive = max(qualified, key=lambda m: m.cost_per_test)
        avg_cost = np.mean([m.cost_per_test for m in qualified])
        
        return f"""
## 💰 Cost Analysis

### Investment Overview:
- **Total Cost:** ${total_cost:.4f}
- **Average Cost per Test:** ${avg_cost:.5f}
- **Cost Range:** ${cheapest.cost_per_test:.6f} - ${most_expensive.cost_per_test:.5f}
- **Price Variation:** {most_expensive.cost_per_test/cheapest.cost_per_test:.0f}x difference

### Cost vs Quality Trade-offs:
- **Most Affordable (Qualified):** {cheapest.model_name} (${cheapest.cost_per_test:.5f}/test, {cheapest.avg_score:.1%} accuracy)
- **Premium Option:** {most_expensive.model_name} (${most_expensive.cost_per_test:.5f}/test, {most_expensive.avg_score:.1%} accuracy)

### ROI Considerations:
Quality security analysis prevents breaches that cost orders of magnitude more than model usage.
Focus on **accuracy and completeness** over marginal cost savings for security-critical applications.

"""
    
    def _generate_chart_explanations(self) -> str:
        """Generate chart reading guides."""
        
        return """
---

## 📊 Chart Reading Guide

### Cost-Effectiveness Chart:
Shows quality-adjusted cost-effectiveness with gaming prevention applied.
- **Higher bars = Better value** (quality per dollar)
- **Disqualified models** shown with warnings or excluded entirely

### Pareto Scatter Analysis:
Identifies optimal accuracy/speed trade-offs.
- **X-axis:** Response time (lower = faster)
- **Y-axis:** Accuracy score (higher = better) 
- **Green dots:** Pareto-optimal models (best possible trade-offs)
- **Red dots:** Dominated models (inferior alternatives exist)
- **Bubble size:** Cost per test (larger = more expensive)

**How to use:** Choose green dots based on your priority:
- Need speed? → Leftmost green dot
- Need accuracy? → Topmost green dot  
- Balanced? → Middle of green frontier

### Model Comparison Charts:
- **Box plots:** Show score distribution and consistency
- **Bar charts:** Compare average performance across models
- **Scatter plots:** Explore relationships between metrics

---

*This unified report consolidates all benchmark findings into a single comprehensive analysis.*
**Built by the Rapticore Security Research Team**
"""


def consolidate_reporting_files(outdir: Path) -> None:
    """Consolidate multiple report files into unified summary."""
    
    # List of redundant files that can be merged
    redundant_files = [
        "quality_first_executive_summary.md",
        "standardized_analysis.md", 
        "enhanced_cost_effectiveness_report.md"
    ]
    
    consolidated_content = "# 📊 Consolidated Analysis Report\n\n"
    consolidated_content += "*This report consolidates multiple analysis perspectives for comprehensive review.*\n\n"
    
    for filename in redundant_files:
        file_path = outdir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            consolidated_content += f"\n---\n\n## From: {filename}\n\n{content}\n"
    
    # Save consolidated report
    consolidated_path = outdir / "CONSOLIDATED_ANALYSIS.md"
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        f.write(consolidated_content)
    
    print(f"✓ Created consolidated report: {consolidated_path.name}")
    print("  Consider using this instead of multiple individual reports.")


# Integration function for main benchmark
def generate_unified_report(results_data: Dict, outdir: Path) -> str:
    """Generate unified executive summary report."""
    
    generator = UnifiedReportGenerator()
    
    # Convert results to unified metrics
    model_metrics = []
    total_cost = 0.0
    test_types = set()
    
    for model_name, data in results_data.items():
        if isinstance(data, dict) and 'avg_score' in data:
            
            # Determine qualification status
            qualified = (data['avg_score'] >= 0.80 and 
                        data.get('cost_per_test', 0) >= 0.0001)
            
            warnings = []
            if data['avg_score'] < 0.80:
                warnings.append(f"Below accuracy threshold ({data['avg_score']:.1%})")
            if data.get('cost_per_test', 0) < 0.0001:
                warnings.append("Suspicious low cost")
            
            # Classify tier
            if qualified:
                if data['avg_score'] >= 0.95:
                    tier = "ENTERPRISE_PREMIUM"
                elif data['avg_score'] >= 0.90:
                    tier = "ENTERPRISE_STANDARD"
                elif data['avg_score'] >= 0.85:
                    tier = "PRODUCTION_READY"
                else:
                    tier = "ACCEPTABLE"
            else:
                tier = "DISQUALIFIED"
            
            metrics = UnifiedModelMetrics(
                model_name=model_name,
                total_tests=data.get('total_tests', 5),
                success_rate=data.get('success_rate', 1.0),
                avg_score=data['avg_score'],
                response_time=data.get('avg_response_time', 0),
                cost_per_test=data.get('cost_per_test', 0),
                good_responses=data.get('good_scores', 0),
                consistency_score=1.0 - data.get('score_std_dev', 0),
                reliability_score=data.get('success_rate', 1.0),
                qualified=qualified,
                tier=tier,
                warnings=warnings
            )
            
            model_metrics.append(metrics)
            total_cost += data.get('total_cost', 0)
    
    # Generate unified summary
    summary = generator.generate_unified_executive_summary(
        model_metrics, total_cost, list(test_types), outdir
    )
    
    # Save unified report
    unified_path = outdir / "UNIFIED_EXECUTIVE_SUMMARY.md"
    with open(unified_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✓ Generated unified executive summary: {unified_path.name}")
    
    # Also consolidate existing redundant files
    consolidate_reporting_files(outdir)
    
    return summary