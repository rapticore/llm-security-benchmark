#!/usr/bin/env python3
"""
Unified Executive Summary Generator

Consolidates all executive summary functions into a single, comprehensive function
that generates strategic LLM security analysis reports for business stakeholders.

Built by the Rapticore Security Research Team
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ModelPerformance:
    """Model performance metrics."""
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
    
    @classmethod
    def from_results(cls, model: str, results: List):
        """Create ModelPerformance from results list."""
        if not results:
            return cls(
                model=model, total_tests=0, passed_tests=0, avg_score=0.0,
                avg_time_s=0.0, total_cost_usd=0.0, cost_per_test=0.0,
                success_rate=0.0, perfect_rate=0.0, score_variance=0.0
            )
        
        scores = [getattr(r, 'score', 0.0) for r in results]
        times = [getattr(r, 'elapsed_s', 0.0) for r in results]
        costs = [getattr(r, 'cost_usd', 0.0) for r in results]
        
        passed = sum(1 for r in results if getattr(r, 'ok', False))
        perfect = sum(1 for s in scores if s >= 1.0)
        
        return cls(
            model=model,
            total_tests=len(results),
            passed_tests=passed,
            avg_score=sum(scores) / len(scores) if scores else 0.0,
            avg_time_s=sum(times) / len(times) if times else 0.0,
            total_cost_usd=sum(costs),
            cost_per_test=sum(costs) / len(costs) if costs else 0.0,
            success_rate=passed / len(results) if results else 0.0,
            perfect_rate=perfect / len(results) if results else 0.0,
            score_variance=0.0  # Calculate if needed
        )


def generate_unified_executive_summary(
    results: List,
    models: List[str],
    suite_name: str,
    outdir: Path,
    charts: Optional[Dict[str, str]] = None,
    enhanced_metrics: Optional[Dict] = None,
    language_results: Optional[Dict] = None,
    owasp_results: Optional[Dict] = None,
    total_cost: float = 0.0
) -> str:
    """
    Generate comprehensive executive summary combining all features:
    - Strategic LLM usage recommendations
    - Security architectural analysis
    - Cost-effectiveness optimization
    - Quality-first methodology
    - Business impact assessment
    """
    
    # Calculate performance metrics
    performance_by_model = {}
    for model in models:
        model_results = [r for r in results if getattr(r, 'model', '') == model]
        if model_results:
            performance_by_model[model] = ModelPerformance.from_results(model, model_results)
    
    if not performance_by_model:
        return "No valid results to analyze"
    
    # Find best performers
    best_accuracy = max(performance_by_model.values(), key=lambda p: p.avg_score)
    best_cost_eff = min(performance_by_model.values(), key=lambda p: p.cost_per_test if p.cost_per_test > 0 else float('inf'))
    best_speed = min(performance_by_model.values(), key=lambda p: p.avg_time_s)
    best_reliability = max(performance_by_model.values(), key=lambda p: p.success_rate)
    
    # Calculate total tests and costs
    total_tests = sum(p.total_tests for p in performance_by_model.values())
    models_count = len(performance_by_model)
    avg_cost_per_test = total_cost / total_tests if total_tests > 0 else 0.0
    
    # Generate comprehensive executive summary
    summary = f"""# 🛡️ LLM Security Benchmark Executive Summary

**Suite:** {suite_name} | **Models Tested:** {models_count} | **Total Security Tests:** {total_tests}
**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
**Total Investment:** ${total_cost:.4f} | **Average Cost per Test:** ${avg_cost_per_test:.5f}

## 🎯 Executive Overview

This comprehensive security assessment evaluated {models_count} leading AI models across {total_tests} security scenarios, analyzing their capability to identify vulnerabilities, provide appropriate recommendations, and demonstrate security knowledge alignment with industry standards.

### Key Security Findings

🏆 **Highest Security Accuracy:** {best_accuracy.model} achieved {best_accuracy.avg_score:.1%} detection rate
💰 **Best Cost-Effectiveness:** {best_cost_eff.model} at ${best_cost_eff.cost_per_test:.5f} per analysis
⚡ **Fastest Response Time:** {best_speed.model} averages {best_speed.avg_time_s:.2f}s per analysis
🎯 **Most Reliable:** {best_reliability.model} shows {best_reliability.success_rate:.1%} success rate

## 📊 Strategic Model Analysis

### Premium Security Models (Highest Accuracy):
**{best_accuracy.model}**
- **Security Detection Rate:** {best_accuracy.avg_score:.3f}/1.0 ({best_accuracy.avg_score:.1%})
- **Reliability:** {best_accuracy.success_rate:.1%} success rate
- **Response Time:** {best_accuracy.avg_time_s:.2f}s average
- **Cost Efficiency:** ${best_accuracy.cost_per_test:.5f} per analysis
- **Perfect Assessments:** {int(best_accuracy.perfect_rate * best_accuracy.total_tests)}/{best_accuracy.total_tests}

### Most Cost-Effective: {best_cost_eff.model}
- **Value Score:** {(best_cost_eff.avg_score / best_cost_eff.cost_per_test if best_cost_eff.cost_per_test > 0 else 0):.1f} security points per dollar
  - *Formula: average_score ÷ cost_per_test*
  - *Higher values indicate better cost-effectiveness for security analysis*
- **Detection Accuracy:** {best_cost_eff.avg_score:.3f}/1.0
- **Operational Cost:** ${best_cost_eff.cost_per_test:.5f} per test
- **Success Rate:** {best_cost_eff.success_rate:.1%}

### Fastest Response: {best_speed.model}
- **Average Response Time:** {best_speed.avg_time_s:.2f}s
- **Security Accuracy:** {best_speed.avg_score:.3f}/1.0
- **Speed Score:** {1 / best_speed.avg_time_s:.3f}

### Most Reliable: {best_reliability.model}
- **Success Rate:** {best_reliability.success_rate:.1%}
- **Average Detection:** {best_reliability.avg_score:.3f}/1.0
- **Response Consistency:** {best_reliability.perfect_rate:.1%} perfect scores

## 🎯 LLM Security Deployment Guide

### High-Stakes Security Analysis:
**Recommended: {best_accuracy.model}**
- {best_accuracy.avg_score:.1%} vulnerability detection rate
- Best for: Penetration testing, security audits, compliance reviews
- Cost: ${best_accuracy.cost_per_test:.5f} per analysis (premium but reliable)

### Cost-Effective Security Screening:
**Recommended: {best_cost_eff.model}**
- Balance of accuracy and cost efficiency
- Best for: Code review automation, CI/CD pipeline integration
- Cost: ${best_cost_eff.cost_per_test:.5f} per analysis

### Real-Time Security Monitoring:
**Recommended: {best_speed.model}**
- {best_speed.avg_time_s:.2f}s average response time
- Best for: Live security monitoring, rapid threat detection
- Speed advantage: {1/best_speed.avg_time_s:.1f} analyses per second

## 🏗️ Security Architecture Integration

### Deployment Scenarios by Model:

"""

    # Add comprehensive model performance table
    summary += "\n## 📋 Detailed Model Performance Analysis\n\n"
    summary += "| Model | Tests | Success Rate | Avg Score | Response Time | Cost/Test | Perfect Scores | Token Usage |\n"
    summary += "|-------|-------|--------------|-----------|---------------|-----------|----------------|-------------|\n"
    
    for model, perf in sorted(performance_by_model.items(), key=lambda x: x[1].avg_score, reverse=True):
        # Get token usage info from results if available
        model_results = [r for r in results if getattr(r, 'model', '') == model]
        total_input_tokens = sum(getattr(r, 'input_tokens', 0) for r in model_results)
        total_output_tokens = sum(getattr(r, 'output_tokens', 0) for r in model_results)
        
        summary += f"| {model} | {perf.total_tests}/{perf.total_tests} | {perf.success_rate:.1%} | {perf.avg_score:.3f} | {perf.avg_time_s:.2f}s | ${perf.cost_per_test:.6f} | {int(perf.perfect_rate * perf.total_tests)} | {total_input_tokens}/{total_output_tokens} |\n"

    # Add detailed test-by-test performance table
    summary += "\n## 🧪 Individual Test Performance\n\n"
    summary += "| Test Case | Model | Score | Time | Cost | Key Findings |\n"
    summary += "|-----------|-------|-------|------|------|-------------|\n"
    
    # Add individual test results sorted by score
    for result in sorted(results, key=lambda r: getattr(r, 'score', 0), reverse=True):
        test_id = getattr(result, 'path', getattr(result, 'suite_id', 'unknown'))
        model = getattr(result, 'model', 'unknown')
        score = getattr(result, 'score', 0.0)
        time_taken = getattr(result, 'elapsed_s', 0.0)
        cost = getattr(result, 'cost_usd', 0.0)
        
        # Extract key finding from response text
        text = getattr(result, 'text', '')
        key_finding = text[:80] + "..." if len(text) > 80 else text
        key_finding = key_finding.replace('\n', ' ').replace('|', '\\|')  # Escape for markdown table
        
        summary += f"| {test_id} | {model} | {score:.3f} | {time_taken:.2f}s | ${cost:.6f} | {key_finding} |\n"

    # Add security category performance analysis
    summary += "\n## 🔍 Security Category Performance\n\n"
    
    # Categorize test results by security type
    security_categories = {
        'SQL Injection': ['sql_injection_simple', 'sql_injection_complex'],
        'Cross-Site Scripting (XSS)': ['reflected_xss', 'stored_xss', 'dom_xss'],
        'Command Injection': ['command_injection', 'os_command_injection'],
        'Access Control': ['broken_access_control', 'privilege_escalation'],
        'Authentication': ['weak_authentication', 'session_management'],
        'Input Validation': ['csrf_vulnerability', 'parameter_pollution'],
        'Data Security': ['hardcoded_secrets', 'sensitive_data_exposure'],
        'Deserialization': ['insecure_deserialization_basic', 'insecure_deserialization_advanced'],
        'Network Security': ['ssrf_basic', 'ssrf_advanced'],
        'OWASP Knowledge': ['owasp_top3', 'owasp_top10', 'security_principles']
    }
    
    summary += "| Security Category | Tests | Avg Score | Success Rate | Key Issues Found |\n"
    summary += "|-------------------|-------|-----------|--------------|------------------|\n"
    
    for category, test_patterns in security_categories.items():
        category_results = []
        for result in results:
            test_id = getattr(result, 'path', getattr(result, 'suite_id', ''))
            if any(pattern in test_id for pattern in test_patterns):
                category_results.append(result)
        
        if category_results:
            avg_score = sum(getattr(r, 'score', 0) for r in category_results) / len(category_results)
            success_rate = sum(1 for r in category_results if getattr(r, 'ok', False)) / len(category_results)
            
            # Extract common issues
            issues = []
            for result in category_results:
                text = getattr(result, 'text', '').lower()
                if 'injection' in text:
                    issues.append('Injection vulnerabilities')
                elif 'xss' in text or 'cross-site' in text:
                    issues.append('XSS vulnerabilities')  
                elif 'hardcoded' in text:
                    issues.append('Hardcoded credentials')
                elif 'access control' in text:
                    issues.append('Broken access control')
                elif 'authentication' in text:
                    issues.append('Weak authentication')
            
            key_issues = ', '.join(list(set(issues))[:3]) if issues else 'Various security issues'
            
            summary += f"| {category} | {len(category_results)} | {avg_score:.3f} | {success_rate:.1%} | {key_issues} |\n"

    # Add language-specific recommendations if available
    if language_results:
        summary += "\n## 📊 Language-Specific Security Recommendations\n\n"
        for lang, data in language_results.items():
            if isinstance(data, dict) and 'models' in data:
                best_model = max(data['models'].items(), key=lambda x: x[1].get('avg_score', 0))
                summary += f"**{lang.title()} Security:** Use {best_model[0]} ({best_model[1].get('avg_score', 0):.1%} accuracy)\n"

    # Add OWASP category analysis if available
    if owasp_results:
        summary += "\n## 🔒 OWASP Top 10 Security Analysis\n\n"
        for category, data in owasp_results.items():
            if isinstance(data, dict) and 'models' in data:
                best_model = max(data['models'].items(), key=lambda x: x[1].get('avg_score', 0))
                summary += f"**{category}:** {best_model[0]} leads with {best_model[1].get('avg_score', 0):.1%} detection rate\n"

    # Add charts section if available
    if charts:
        summary += "\n## 📊 Performance Visualizations\n\n"
        summary += "The following charts provide visual insights into model performance and comparisons:\n\n"
        for chart_name, chart_path in charts.items():
            chart_file = Path(chart_path).name
            summary += f"- **{chart_name.replace('_', ' ').title()}:** `{chart_file}` - "
            
            # Add descriptions based on chart type
            if 'performance' in chart_name:
                summary += "Scatter plot showing security score vs response time with cost indicators\n"
            elif 'cost' in chart_name:
                summary += "Bar chart comparing security points per dollar across models\n"
            elif 'token' in chart_name:
                summary += "Input and output token consumption by model\n"
            else:
                summary += "Model comparison and analysis visualization\n"

    # Add methodology and recommendations
    summary += f"""

## 🎯 Strategic Recommendations

### For Maximum Security Accuracy:
Use **{best_accuracy.model}** for critical security assessments where accuracy is paramount. This model provides the highest vulnerability detection rate at {best_accuracy.avg_score:.1%}, making it ideal for:
- Security audits and compliance reviews
- Penetration testing analysis
- Critical infrastructure assessment

### For Cost-Effective Operations:
Use **{best_cost_eff.model}** for high-volume security screening where cost efficiency matters. At ${best_cost_eff.cost_per_test:.5f} per analysis, it provides:
- Automated code review integration
- CI/CD pipeline security gates
- Large-scale vulnerability scanning

### For Real-Time Security:
Use **{best_speed.model}** for time-sensitive security monitoring. With {best_speed.avg_time_s:.2f}s response time, it enables:
- Live security monitoring
- Real-time threat detection
- Interactive security analysis

## 📈 Business Impact Assessment

**Total Security Investment:** ${total_cost:.4f}
**Tests Executed:** {total_tests}
**Models Evaluated:** {models_count}
**Average Analysis Cost:** ${avg_cost_per_test:.5f}

**ROI Optimization:**
- Premium models ({best_accuracy.model}): High accuracy, higher cost - use for critical assessments
- Balanced models: Good accuracy-to-cost ratio - use for regular operations  
- Fast models ({best_speed.model}): Real-time capabilities - use for monitoring

## 🔍 Quality-First Methodology

This analysis prioritizes security detection accuracy over cost optimization, ensuring that model recommendations are based on actual security capability rather than just economic factors. Cost is considered as a secondary factor to enable informed business decisions while maintaining security effectiveness.

---

*This analysis is based on {total_tests} security test executions across {models_count} leading LLM models. Built by the Rapticore Security Research Team for comprehensive security program optimization.*

*For detailed technical metrics and raw performance data, see `performance_analysis.json`*
"""

    # Save to file
    summary_path = outdir / "unified_executive_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    
    return str(summary_path)


def replace_multiple_executive_summaries(
    results: List,
    models: List[str], 
    suite_name: str,
    outdir: Path,
    **kwargs
) -> str:
    """
    Single function to replace all executive summary functions:
    - generate_executive_summary()
    - generate_basic_executive_summary() 
    - generate_quality_first_executive_summary()
    - generate_comprehensive_executive_summary()
    """
    return generate_unified_executive_summary(
        results=results,
        models=models,
        suite_name=suite_name,
        outdir=outdir,
        **kwargs
    )