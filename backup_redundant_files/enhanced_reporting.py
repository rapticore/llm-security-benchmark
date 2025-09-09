#!/usr/bin/env python3
"""
Enhanced Reporting System for LLM Security Benchmark
Advanced reporting with improved cost-effectiveness calculations and multi-format exports.

Built by the Rapticore Security Research Team.
"""

import csv
import json
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    import pandas as pd
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


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
    traditional_effectiveness: float  # avg_score / cost_per_test
    weighted_effectiveness: float  # weighted by score quality
    penalty_adjusted_effectiveness: float  # penalties for wrong/missed answers
    
    # Quality-based metrics
    accuracy_weighted_cost: float
    partial_credit_value: float
    wrong_answer_penalty: float


def calculate_enhanced_cost_effectiveness(results: List, model_name: str) -> EnhancedMetrics:
    """Calculate enhanced cost-effectiveness metrics with partial correctness consideration."""
    
    model_results = [r for r in results if r.model == model_name]
    total_tests = len(model_results)
    
    if total_tests == 0:
        return EnhancedMetrics(
            total_tests=0, successful_tests=0, failed_tests=0,
            perfect_scores=0, excellent_scores=0, good_scores=0, 
            fair_scores=0, poor_scores=0,
            total_cost=0.0, cost_per_test=0.0, cost_per_correct_answer=0.0,
            cost_per_partial_answer=0.0, traditional_effectiveness=0.0,
            weighted_effectiveness=0.0, penalty_adjusted_effectiveness=0.0,
            accuracy_weighted_cost=0.0, partial_credit_value=0.0, wrong_answer_penalty=0.0
        )
    
    # Separate successful and failed tests
    successful = [r for r in model_results if r.ok]
    failed = [r for r in model_results if not r.ok]
    
    successful_tests = len(successful)
    failed_tests = len(failed)
    
    # Score distribution analysis
    perfect_scores = sum(1 for r in successful if r.score >= 1.0)
    excellent_scores = sum(1 for r in successful if 0.8 <= r.score < 1.0)  
    good_scores = sum(1 for r in successful if 0.6 <= r.score < 0.8)
    fair_scores = sum(1 for r in successful if 0.4 <= r.score < 0.6)
    poor_scores = sum(1 for r in successful if r.score < 0.4)
    
    # Cost calculations
    total_cost = sum(r.cost_usd for r in model_results if r.cost_usd is not None)
    cost_per_test = total_cost / total_tests if total_tests > 0 else 0.0
    
    # Cost per correct answer (only perfect scores)
    cost_per_correct_answer = total_cost / perfect_scores if perfect_scores > 0 else float('inf')
    
    # Cost per partial answer (all successful attempts)
    cost_per_partial_answer = total_cost / successful_tests if successful_tests > 0 else float('inf')
    
    # Calculate average score
    if successful_tests > 0:
        avg_score = statistics.mean([r.score for r in successful])
        success_rate = successful_tests / total_tests
        
        # Calculate score standard deviation for consistency assessment
        scores = [r.score for r in successful]
        score_std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
    else:
        avg_score = 0.0
        success_rate = 0.0
        score_std_dev = 0.0
    
    # Traditional effectiveness (simple baseline)
    traditional_effectiveness = avg_score / cost_per_test if cost_per_test > 0 and avg_score > 0 else 0.0
    
    # Weighted effectiveness (quality-based scoring)
    if successful_tests > 0:
        # Weight scores: perfect=1.0, excellent=0.9, good=0.7, fair=0.5, poor=0.2
        weighted_score = (perfect_scores * 1.0 + excellent_scores * 0.9 + 
                         good_scores * 0.7 + fair_scores * 0.5 + poor_scores * 0.2)
        weighted_avg = weighted_score / successful_tests
        weighted_effectiveness = weighted_avg / cost_per_test if cost_per_test > 0 else 0.0
    else:
        weighted_effectiveness = 0.0
    
    # Enhanced cost-effectiveness calculation that prioritizes accuracy and usability
    if cost_per_test > 0 and avg_score > 0:
        # Base effectiveness (traditional approach)
        base_effectiveness = avg_score / cost_per_test
        
        # Quality multiplier: severely penalize models with low average scores
        # Models below 0.4 average score are essentially unusable for security analysis
        if avg_score < 0.4:
            quality_multiplier = 0.1  # Almost worthless regardless of cost
        elif avg_score < 0.6:
            quality_multiplier = 0.4  # Poor quality, limited usefulness
        elif avg_score < 0.7:
            quality_multiplier = 0.7  # Fair quality
        elif avg_score < 0.8:
            quality_multiplier = 0.9  # Good quality
        else:
            quality_multiplier = 1.0  # Excellent quality
        
        # Reliability multiplier: penalize models with high failure rates
        reliability_multiplier = success_rate  # 0.0 to 1.0
        
        # Consistency multiplier: reward consistent performance
        consistency_multiplier = max(0.5, 1.0 - (score_std_dev * 2))  # 0.5 to 1.0
        
        # Final penalty-adjusted effectiveness: accuracy is paramount for security analysis
        penalty_adjusted_effectiveness = (base_effectiveness * quality_multiplier * 
                                        reliability_multiplier * consistency_multiplier)
    else:
        penalty_adjusted_effectiveness = 0.0
    
    # Legacy penalty calculation for backwards compatibility
    if total_tests > 0:
        # Calculate penalty: failed tests + partial penalties for low scores
        failure_penalty = failed_tests * 0.5  # Each failure costs 0.5 points
        poor_performance_penalty = poor_scores * 0.3  # Poor scores cost 0.3 points each
        
        total_positive_score = sum(r.score for r in successful)
        penalty_adjusted_score = total_positive_score - failure_penalty - poor_performance_penalty
        penalty_adjusted_score = max(penalty_adjusted_score, 0)  # Don't go negative
        
        # Legacy penalty effectiveness (kept for comparison)
        legacy_penalty_effectiveness = penalty_adjusted_score / total_cost if total_cost > 0 else 0.0
    else:
        legacy_penalty_effectiveness = 0.0
    
    # Additional quality metrics
    accuracy_weighted_cost = total_cost / (avg_score * successful_tests) if avg_score > 0 and successful_tests > 0 else float('inf')
    
    # Partial credit value (how much value comes from partial answers)
    partial_credit_value = (excellent_scores * 0.9 + good_scores * 0.7 + fair_scores * 0.5 + poor_scores * 0.2) / successful_tests if successful_tests > 0 else 0.0
    
    # Wrong answer penalty impact
    wrong_answer_penalty = (failed_tests + poor_scores) / total_tests if total_tests > 0 else 0.0
    
    return EnhancedMetrics(
        total_tests=total_tests,
        successful_tests=successful_tests,
        failed_tests=failed_tests,
        perfect_scores=perfect_scores,
        excellent_scores=excellent_scores,
        good_scores=good_scores,
        fair_scores=fair_scores,
        poor_scores=poor_scores,
        total_cost=total_cost,
        cost_per_test=cost_per_test,
        cost_per_correct_answer=cost_per_correct_answer,
        cost_per_partial_answer=cost_per_partial_answer,
        traditional_effectiveness=traditional_effectiveness,
        weighted_effectiveness=weighted_effectiveness,
        penalty_adjusted_effectiveness=penalty_adjusted_effectiveness,
        accuracy_weighted_cost=accuracy_weighted_cost,
        partial_credit_value=partial_credit_value,
        wrong_answer_penalty=wrong_answer_penalty
    )


def analyze_by_language(results: List) -> Dict[str, Dict[str, Any]]:
    """Analyze effectiveness by programming language."""
    
    language_mapping = {
        'python_': 'Python',
        'js_': 'JavaScript', 
        'java_': 'Java',
        'go_': 'Go',
        'rust_': 'Rust',
        'c_': 'C',
        'cpp_': 'C++',
        'csharp_': 'C#',
        'php_': 'PHP',
        'ruby_': 'Ruby',
        'haskell_': 'Haskell'
    }
    
    language_results = {}
    
    for lang_prefix, lang_name in language_mapping.items():
        lang_tests = [r for r in results if r.suite_id.startswith(lang_prefix)]
        if lang_tests:
            # Group by model
            by_model = {}
            for model in set(r.model for r in lang_tests):
                model_tests = [r for r in lang_tests if r.model == model]
                successful = [r for r in model_tests if r.ok]
                
                if model_tests:
                    avg_score = statistics.mean([r.score for r in successful]) if successful else 0.0
                    success_rate = len(successful) / len(model_tests)
                    total_cost = sum(r.cost_usd for r in model_tests if r.cost_usd is not None)
                    cost_per_test = total_cost / len(model_tests) if model_tests else 0.0
                    effectiveness = avg_score / cost_per_test if cost_per_test > 0 else 0.0
                    
                    by_model[model] = {
                        'avg_score': avg_score,
                        'success_rate': success_rate,
                        'total_tests': len(model_tests),
                        'successful_tests': len(successful),
                        'total_cost': total_cost,
                        'cost_per_test': cost_per_test,
                        'effectiveness': effectiveness
                    }
            
            language_results[lang_name] = by_model
    
    return language_results


def analyze_by_owasp_category(results: List) -> Dict[str, Dict[str, Any]]:
    """Analyze effectiveness by OWASP vulnerability category."""
    
    owasp_mapping = {
        'sql_injection': 'A03 - Injection',
        'nosql_injection': 'A03 - Injection', 
        'ldap_injection': 'A03 - Injection',
        'command_injection': 'A03 - Injection',
        'code_injection': 'A03 - Injection',
        'broken_access_control': 'A01 - Broken Access Control',
        'insecure_direct_object_reference': 'A01 - Broken Access Control',
        'jwt_algorithm_confusion': 'A01 - Broken Access Control',
        'mass_assignment': 'A01 - Broken Access Control',
        'weak_crypto': 'A02 - Cryptographic Failures',
        'hardcoded_secrets': 'A02 - Cryptographic Failures',
        'weak_tls': 'A02 - Cryptographic Failures',
        'weak_random': 'A02 - Cryptographic Failures',
        'insecure_deserialization': 'A08 - Software and Data Integrity Failures',
        'xml_external_entity': 'A05 - Security Misconfiguration',
        'xxe_attack': 'A05 - Security Misconfiguration',
        'ssrf': 'A10 - Server-Side Request Forgery',
        'xss': 'A03 - Injection',
        'dom_xss': 'A03 - Injection',
        'reflected_xss': 'A03 - Injection',
        'csrf': 'A01 - Broken Access Control',
        'session_fixation': 'A07 - Identification and Authentication Failures',
        'weak_authentication': 'A07 - Identification and Authentication Failures',
        'authentication_failures': 'A07 - Identification and Authentication Failures',
        'path_traversal': 'A01 - Broken Access Control',
        'file_inclusion': 'A01 - Broken Access Control',
        'information_disclosure': 'A09 - Security Logging and Monitoring Failures',
        'logging_monitoring': 'A09 - Security Logging and Monitoring Failures',
        'vulnerable_components': 'A06 - Vulnerable and Outdated Components',
        'security_misconfiguration': 'A05 - Security Misconfiguration',
        'insecure_design': 'A04 - Insecure Design'
    }
    
    owasp_results = {}
    
    for test in results:
        # Try to map test_id to OWASP category
        category = None
        for pattern, owasp_cat in owasp_mapping.items():
            if pattern in test.suite_id.lower():
                category = owasp_cat
                break
        
        if category:
            if category not in owasp_results:
                owasp_results[category] = []
            owasp_results[category].append(test)
    
    # Calculate metrics for each category
    category_metrics = {}
    for category, tests in owasp_results.items():
        by_model = {}
        for model in set(r.model for r in tests):
            model_tests = [r for r in tests if r.model == model]
            successful = [r for r in model_tests if r.ok]
            
            if model_tests:
                avg_score = statistics.mean([r.score for r in successful]) if successful else 0.0
                success_rate = len(successful) / len(model_tests)
                total_cost = sum(r.cost_usd for r in model_tests if r.cost_usd is not None)
                cost_per_test = total_cost / len(model_tests) if model_tests else 0.0
                effectiveness = avg_score / cost_per_test if cost_per_test > 0 else 0.0
                
                by_model[model] = {
                    'avg_score': avg_score,
                    'success_rate': success_rate,
                    'total_tests': len(model_tests),
                    'successful_tests': len(successful),
                    'total_cost': total_cost,
                    'cost_per_test': cost_per_test,
                    'effectiveness': effectiveness
                }
        
        category_metrics[category] = by_model
    
    return category_metrics


def generate_language_effectiveness_chart(language_results: Dict, outdir: Path) -> str:
    """Generate effectiveness by language chart."""
    
    if not VISUALIZATION_AVAILABLE or not language_results:
        return ""
    
    # Prepare data
    languages = list(language_results.keys())
    models = set()
    for lang_data in language_results.values():
        models.update(lang_data.keys())
    models = sorted(list(models))
    
    # Create matrix of effectiveness scores
    effectiveness_matrix = []
    for model in models:
        model_scores = []
        for lang in languages:
            if model in language_results[lang]:
                model_scores.append(language_results[lang][model]['effectiveness'])
            else:
                model_scores.append(0)
        effectiveness_matrix.append(model_scores)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    
    im = ax.imshow(effectiveness_matrix, cmap='RdYlGn', aspect='auto')
    
    # Set ticks and labels
    ax.set_xticks(range(len(languages)))
    ax.set_yticks(range(len(models)))
    ax.set_xticklabels(languages, rotation=45, ha='right')
    ax.set_yticklabels(models)
    
    # Add text annotations
    for i in range(len(models)):
        for j in range(len(languages)):
            value = effectiveness_matrix[i][j]
            if value > 0:
                text = ax.text(j, i, f'{value:.0f}', ha='center', va='center', 
                             color='white' if value < 1000 else 'black', fontweight='bold')
    
    ax.set_title('Cost-Effectiveness by Programming Language\n(Security Points per Dollar)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Programming Language', fontsize=12)
    ax.set_ylabel('Model', fontsize=12)
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Effectiveness (Points/$)', rotation=270, labelpad=15)
    
    plt.tight_layout()
    chart_path = outdir / "language_effectiveness.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def generate_owasp_effectiveness_chart(owasp_results: Dict, outdir: Path) -> str:
    """Generate effectiveness by OWASP category chart."""
    
    if not VISUALIZATION_AVAILABLE or not owasp_results:
        return ""
    
    # Prepare data for grouped bar chart
    categories = list(owasp_results.keys())
    models = set()
    for category_data in owasp_results.values():
        models.update(category_data.keys())
    models = sorted(list(models))
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    x = np.arange(len(categories))
    width = 0.8 / len(models)
    
    colors = sns.color_palette("Set3", len(models))
    
    for i, model in enumerate(models):
        effectiveness_scores = []
        for category in categories:
            if model in owasp_results[category]:
                effectiveness_scores.append(owasp_results[category][model]['effectiveness'])
            else:
                effectiveness_scores.append(0)
        
        bars = ax.bar(x + (i - len(models)/2 + 0.5) * width, effectiveness_scores, 
                     width, label=model, color=colors[i], alpha=0.8)
        
        # Add value labels on bars
        for bar, value in zip(bars, effectiveness_scores):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(effectiveness_scores)*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontsize=8, rotation=0)
    
    ax.set_title('Cost-Effectiveness by OWASP Top 10 Category\n(Security Points per Dollar)', fontsize=14, fontweight='bold')
    ax.set_xlabel('OWASP Category', fontsize=12)
    ax.set_ylabel('Effectiveness (Points/$)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([cat.replace(' - ', '\n') for cat in categories], rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    chart_path = outdir / "owasp_effectiveness.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def export_to_csv(results: List, models: List[str], enhanced_metrics: Dict, outdir: Path) -> str:
    """Export detailed results to CSV format."""
    
    csv_path = outdir / "detailed_results.csv"
    
    # Prepare detailed results
    detailed_data = []
    for result in results:
        row = {
            'model_name': result.model,
            'test_id': result.suite_id,
            'success': result.ok,
            'score': result.score,
            'response_time_s': result.elapsed_s,
            'cost_usd': result.cost_usd or 0.0,
            'input_tokens': result.input_tokens,
            'output_tokens': result.output_tokens,
            'criteria_met': len(result.criteria_met) if hasattr(result, 'criteria_met') else 0,
            'criteria_missed': len(result.criteria_missed) if hasattr(result, 'criteria_missed') else 0,
            'violations': len(result.must_not_violations) if hasattr(result, 'must_not_violations') else 0
        }
        detailed_data.append(row)
    
    # Write detailed results
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if detailed_data:
            writer = csv.DictWriter(f, fieldnames=detailed_data[0].keys())
            writer.writeheader()
            writer.writerows(detailed_data)
        else:
            # Write empty CSV with headers for failed runs
            headers = ['model_name', 'test_id', 'success', 'score', 'response_time_s', 
                      'cost_usd', 'input_tokens', 'output_tokens', 'criteria_met', 
                      'criteria_missed', 'violations']
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            # No rows to write for completely failed runs
    
    # Also create a summary CSV
    summary_path = outdir / "model_summary.csv"
    summary_data = []
    
    for model in models:
        if model in enhanced_metrics:
            metrics = enhanced_metrics[model]
            row = {
                'model_name': model,
                'total_tests': metrics.total_tests,
                'successful_tests': metrics.successful_tests,
                'success_rate': metrics.successful_tests / metrics.total_tests if metrics.total_tests > 0 else 0,
                'perfect_scores': metrics.perfect_scores,
                'excellent_scores': metrics.excellent_scores,
                'good_scores': metrics.good_scores,
                'fair_scores': metrics.fair_scores,
                'poor_scores': metrics.poor_scores,
                'total_cost': metrics.total_cost,
                'cost_per_test': metrics.cost_per_test,
                'cost_per_correct_answer': metrics.cost_per_correct_answer if metrics.cost_per_correct_answer != float('inf') else 'N/A',
                'traditional_effectiveness': metrics.traditional_effectiveness,
                'weighted_effectiveness': metrics.weighted_effectiveness,
                'penalty_adjusted_effectiveness': metrics.penalty_adjusted_effectiveness,
                'partial_credit_value': metrics.partial_credit_value,
                'wrong_answer_penalty': metrics.wrong_answer_penalty
            }
            summary_data.append(row)
    
    with open(summary_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
        writer.writeheader()
        writer.writerows(summary_data)
    
    return str(csv_path)


def export_to_json(results: List, models: List[str], enhanced_metrics: Dict, 
                  language_results: Dict, owasp_results: Dict, outdir: Path) -> str:
    """Export comprehensive analysis to JSON format."""
    
    json_data = {
        'metadata': {
            'timestamp': str(datetime.now()),
            'total_tests': len(results),
            'models_tested': len(models),
            'unique_test_cases': len(set(r.suite_id for r in results))
        },
        'detailed_results': [
            {
                'model_name': r.model,
                'test_id': r.suite_id,
                'success': r.ok,
                'score': r.score,
                'response_time_s': r.elapsed_s,
                'cost_usd': r.cost_usd or 0.0,
                'input_tokens': r.input_tokens,
                'output_tokens': r.output_tokens,
                'criteria_met': getattr(r, 'criteria_met', []),
                'criteria_missed': getattr(r, 'criteria_missed', []),
                'violations': getattr(r, 'must_not_violations', [])
            }
            for r in results
        ],
        'enhanced_metrics': {
            model: asdict(metrics) for model, metrics in enhanced_metrics.items()
        },
        'language_analysis': language_results,
        'owasp_analysis': owasp_results,
        'summary': {
            'best_overall_accuracy': max(enhanced_metrics.items(), 
                                       key=lambda x: x[1].traditional_effectiveness)[0] if enhanced_metrics else None,
            'best_weighted_effectiveness': max(enhanced_metrics.items(), 
                                             key=lambda x: x[1].weighted_effectiveness)[0] if enhanced_metrics else None,
            'best_penalty_adjusted': max(enhanced_metrics.items(), 
                                       key=lambda x: x[1].penalty_adjusted_effectiveness)[0] if enhanced_metrics else None,
            'total_cost_all_models': sum(r.cost_usd for r in results if r.cost_usd),
            'average_score_all_models': statistics.mean([r.score for r in results if r.ok]) if any(r.ok for r in results) else 0
        }
    }
    
    json_path = outdir / "comprehensive_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    return str(json_path)


def generate_enhanced_markdown_report(results: List, models: List[str], enhanced_metrics: Dict,
                                    language_results: Dict, owasp_results: Dict, outdir: Path) -> str:
    """Generate comprehensive markdown report."""
    
    from datetime import datetime
    
    # Calculate total costs
    total_cost_all_models = sum(r.cost_usd for r in results if r.cost_usd)
    total_tests_run = len(results)
    avg_cost_per_test = total_cost_all_models / total_tests_run if total_tests_run > 0 else 0
    
    # Find best performers
    best_traditional = max(enhanced_metrics.items(), key=lambda x: x[1].traditional_effectiveness) if enhanced_metrics else (None, None)
    best_weighted = max(enhanced_metrics.items(), key=lambda x: x[1].weighted_effectiveness) if enhanced_metrics else (None, None)
    best_penalty_adjusted = max(enhanced_metrics.items(), key=lambda x: x[1].penalty_adjusted_effectiveness) if enhanced_metrics else (None, None)
    most_accurate = max(enhanced_metrics.items(), key=lambda x: x[1].perfect_scores) if enhanced_metrics else (None, None)
    
    markdown_content = f"""# Enhanced LLM Security Benchmark Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Built by:** Rapticore Security Research Team

## 💰 Cost Summary

**⚠️ IMPORTANT:** This benchmark uses paid API services and will incur costs.

- **Total Cost This Run:** ${total_cost_all_models:.4f}
- **Average Cost per Test:** ${avg_cost_per_test:.6f}
- **Total Tests Executed:** {total_tests_run:,}
- **Models Tested:** {len(models)}

*Costs vary significantly by model - premium models like Claude Opus 4 cost ~20x more than budget models*

## Executive Summary

This comprehensive analysis evaluates {len(models)} Large Language Models across {len(set(r.suite_id for r in results))} security test cases, providing enhanced cost-effectiveness metrics that consider partial correctness, quality weighting, and performance penalties.

### Key Findings

"""
    
    if best_traditional[0]:
        markdown_content += f"""
🏆 **Best Traditional Effectiveness:** {best_traditional[0]} ({best_traditional[1].traditional_effectiveness:.1f} points/$)
⭐ **Best Quality-Weighted Effectiveness:** {best_weighted[0]} ({best_weighted[1].weighted_effectiveness:.1f} points/$)  
🎯 **Best Penalty-Adjusted Effectiveness:** {best_penalty_adjusted[0]} ({best_penalty_adjusted[1].penalty_adjusted_effectiveness:.1f} points/$)
🔒 **Most Accurate (Perfect Scores):** {most_accurate[0]} ({most_accurate[1].perfect_scores} perfect assessments)

"""
    
    markdown_content += """
### Cost-Effectiveness Methodology

Our enhanced cost-effectiveness calculation considers three key metrics:

1. **Traditional Effectiveness:** `average_score ÷ cost_per_test`
2. **Quality-Weighted Effectiveness:** Weights scores by quality (perfect=1.0, excellent=0.9, good=0.7, fair=0.5, poor=0.2)  
3. **Penalty-Adjusted Effectiveness:** Applies penalties for failed tests (-0.5) and poor performance (-0.3)

## Detailed Model Performance

| Model | Total Tests | Success Rate | Perfect Scores | Cost/Test | Traditional | Weighted | Penalty-Adjusted |
|-------|-------------|--------------|----------------|-----------|------------|----------|------------------|
"""
    
    for model in models:
        if model in enhanced_metrics:
            m = enhanced_metrics[model]
            success_rate = (m.successful_tests / m.total_tests * 100) if m.total_tests > 0 else 0
            markdown_content += f"| {model} | {m.total_tests} | {success_rate:.1f}% | {m.perfect_scores} | ${m.cost_per_test:.5f} | {m.traditional_effectiveness:.1f} | {m.weighted_effectiveness:.1f} | {m.penalty_adjusted_effectiveness:.1f} |\n"
    
    markdown_content += """
## Score Quality Distribution

Understanding how models perform across different quality levels:

"""
    
    for model in models[:5]:  # Top 5 models for space
        if model in enhanced_metrics:
            m = enhanced_metrics[model]
            markdown_content += f"""
### {model}
- **Perfect (1.0):** {m.perfect_scores} tests
- **Excellent (0.8-0.99):** {m.excellent_scores} tests  
- **Good (0.6-0.79):** {m.good_scores} tests
- **Fair (0.4-0.59):** {m.fair_scores} tests
- **Poor (0.0-0.39):** {m.poor_scores} tests
- **Failed:** {m.failed_tests} tests

"""
    
    # Language analysis
    if language_results:
        markdown_content += """
## Programming Language Effectiveness

Performance breakdown by programming language:

"""
        for lang, models_data in list(language_results.items())[:5]:  # Top 5 languages
            markdown_content += f"""
### {lang}
"""
            for model, data in sorted(models_data.items(), key=lambda x: x[1]['effectiveness'], reverse=True)[:3]:
                markdown_content += f"- **{model}:** {data['effectiveness']:.1f} points/$, {data['avg_score']:.2f} avg score, {data['success_rate']:.1%} success\n"
    
    # OWASP analysis  
    if owasp_results:
        markdown_content += """
## OWASP Top 10 Category Analysis

Effectiveness against different vulnerability categories:

"""
        for category, models_data in list(owasp_results.items())[:5]:  # Top 5 categories
            markdown_content += f"""
### {category}
"""
            for model, data in sorted(models_data.items(), key=lambda x: x[1]['effectiveness'], reverse=True)[:3]:
                markdown_content += f"- **{model}:** {data['effectiveness']:.1f} points/$, {data['avg_score']:.2f} avg score\n"
    
    # Calculate cost statistics safely
    cost_values = [r.cost_usd for r in results if r.cost_usd]
    total_cost = sum(cost_values) if cost_values else 0.0
    avg_cost = statistics.mean(cost_values) if cost_values else 0.0
    
    # Find most cost-effective model for perfect answers
    best_cost_effective = 'N/A'
    if enhanced_metrics:
        valid_models = [(name, data) for name, data in enhanced_metrics.items() 
                       if data.cost_per_correct_answer != float('inf')]
        if valid_models:
            best_cost_effective = min(valid_models, key=lambda x: x[1].cost_per_correct_answer)[0]
    
    perfect_scores_total = sum(m.perfect_scores for m in enhanced_metrics.values()) if enhanced_metrics else 0

    markdown_content += f"""
## Cost Analysis Summary

- **Total Testing Cost:** ${total_cost:.2f}
- **Average Cost per Test:** ${avg_cost:.5f}
- **Most Cost-Effective per Perfect Answer:** {best_cost_effective}
- **Tests with Perfect Scores:** {perfect_scores_total} / {len(results)}

## Recommendations

Based on this analysis:

1. **For Maximum Accuracy:** Use {most_accurate[0] if most_accurate[0] else 'N/A'} for critical security assessments
2. **For Best Value:** Use {best_penalty_adjusted[0] if best_penalty_adjusted[0] else 'N/A'} for cost-effective security screening
3. **For Quality Balance:** Use {best_weighted[0] if best_weighted[0] else 'N/A'} for balanced accuracy and cost

*Report generated by Rapticore Security Research Team's Enhanced LLM Security Benchmark*
"""
    
    md_path = outdir / "enhanced_analysis_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(md_path)