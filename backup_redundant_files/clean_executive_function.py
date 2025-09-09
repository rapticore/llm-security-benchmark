import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


from .enhanced_multi_llm_benchmark import ModelPerformance
from .enhanced_multi_llm_benchmark import EnhancedRunResult
from .enhanced_multi_llm_benchmark import analyze_vulnerability_categories
from .enhanced_multi_llm_benchmark import  calculate_business_metrics



def generate_executive_summary(
    results: List[EnhancedRunResult], 
    models: List[str], 
    suite_name: str,
    outdir: Path,
    charts: Optional[Dict[str, str]] = None
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
    
    # Build chart section
    chart_section = ""
    if charts:
        if "performance_comparison" in charts:
            chart_section += f"- **Performance Comparison Chart:** `{Path(charts['performance_comparison']).name}` - Scatter plot showing security score vs response time with cost indicators\n"
        if "cost_effectiveness" in charts:
            chart_section += f"- **Cost Effectiveness Chart:** `{Path(charts['cost_effectiveness']).name}` - Bar chart comparing security points per dollar across models\n"
        if "token_usage" in charts:
            chart_section += f"- **Token Usage Analysis:** `{Path(charts['token_usage']).name}` - Input and output token consumption by model\n"
        if "performance_radar" in charts:
            chart_section += f"- **Performance Radar Chart:** `{Path(charts['performance_radar']).name}` - Multi-dimensional performance comparison\n"
    else:
        chart_section = "*Charts not available - install matplotlib and seaborn for visual analysis*"
    
    # Build complete executive summary
    summary = f"""# 🛡️ LLM Security Benchmark Executive Summary

**Suite:** {suite_name} | **Models Tested:** {len(models)} | **Total Security Tests:** {total_tests}
**Analysis Date:** {datetime.now().strftime("%B %d, %Y")}

## 🎯 Executive Overview

This comprehensive security assessment evaluated {len(models)} leading AI models across {total_tests} security scenarios, analyzing their capability to identify vulnerabilities, provide appropriate recommendations, and demonstrate security knowledge alignment with industry standards.

### Key Security Findings

🏆 **Highest Security Accuracy:** {best_accuracy.model_name} achieved {best_accuracy.avg_score:.1%} detection rate
💰 **Best Cost-Effectiveness:** {best_value.model_name} delivers {best_value.cost_effectiveness:.0f} security points per dollar
⚡ **Fastest Response Time:** {fastest.model_name} averages {fastest.avg_response_time:.2f}s per analysis
🎯 **Most Consistent Performance:** {most_reliable.model_name} shows {most_reliable.score_std_dev:.3f} variance in scoring

## 📊 Strategic Model Analysis

### Premium Security Models (Highest Accuracy):
{best_accuracy.model_name}
- **Security Detection Rate:** {best_accuracy.avg_score:.3f}/1.0 ({best_accuracy.avg_score:.1%})
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

## 📊 Performance Visualizations

The following charts provide visual insights into model performance and comparisons:

{chart_section}

---

*This analysis is based on {len(results)} security test executions across {len(models)} leading LLM models. Built by the Rapticore Security Research Team for comprehensive security program optimization.*

*For detailed technical metrics and raw performance data, see `performance_analysis.json`*"""
    
    # Write executive summary
    with open(outdir / "executive_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)