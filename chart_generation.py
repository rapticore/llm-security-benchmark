#!/usr/bin/env python3
"""
Consolidated Improved Chart Generation Module

Combines the best features from:
- improved_chart_generation.py (comprehensive chart generation)
- visualization_output_fix.py (visualization fixes and reporting)

Built by the Rapticore Security Research Team
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: matplotlib/seaborn not available. Chart generation will be disabled.")


def improved_language_classification(test_id: str) -> str:
    """
    Enhanced language classification that's more permissive and useful for analysis.
    (From improved_chart_generation.py)
    """
    test_lower = test_id.lower()
    
    # More aggressive pattern matching
    language_patterns = {
        'Python': ['python', 'py_', 'django', 'flask', 'pickle', 'eval', 'exec'],
        'JavaScript': ['javascript', 'js', 'typescript', 'node', 'prototype', 'npm', 'react', 'vue'],
        'Java/JVM': ['java', 'kotlin', 'scala', 'jvm', 'spring', 'deserialization', 'jackson'],
        'C/C++': ['c_', 'cpp_', 'buffer', 'memory', 'unsafe', 'stack', 'heap'],
        'Go': ['go_', 'golang', 'goroutine', 'race'],
        'PHP': ['php', 'wordpress', 'drupal', 'laravel'],
        'C#/.NET': ['csharp', 'dotnet', 'aspnet', 'entity'],
        'Ruby': ['ruby', 'rails', 'gem'],
        'Rust': ['rust', 'cargo', 'unsafe'],
        'Swift': ['swift', 'ios', 'cocoa'],
        'General Security': ['security', 'owasp', 'injection', 'xss', 'csrf', 'sql', 'command']
    }
    
    for language, patterns in language_patterns.items():
        if any(pattern in test_lower for pattern in patterns):
            return language
    
    # If no specific language detected, classify by security type
    if any(term in test_lower for term in ['sql', 'injection', 'xss', 'csrf']):
        return 'Web Security'
    elif any(term in test_lower for term in ['buffer', 'memory', 'overflow']):
        return 'Systems Security'
    elif any(term in test_lower for term in ['secret', 'key', 'token', 'credential']):
        return 'Secrets/Auth'
    else:
        return 'General Security'


def report_visualization_success(charts_dict: dict, chart_type: str = "performance"):
    """Report successful visualization generation with detailed output (from visualization_output_fix.py)"""
    if not charts_dict:
        print(f"⚠️  No {chart_type} charts generated")
        return
        
    print(f"✅ Successfully generated {len(charts_dict)} {chart_type} charts:")
    for chart_name, chart_path in charts_dict.items():
        file_path = Path(chart_path)
        if file_path.exists():
            file_size = file_path.stat().st_size
            size_kb = file_size // 1024
            print(f"   ✓ {file_path.name} ({size_kb} KB)")
        else:
            print(f"   ❌ {file_path.name} (file missing)")


def generate_model_comparison_chart(results: List, models: List[str], outdir: Path) -> str:
    """Generate comprehensive model comparison chart (from improved_chart_generation.py)"""
    
    if not VISUALIZATION_AVAILABLE:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available")
        return None
    
    # Prepare data
    model_data = defaultdict(lambda: {'scores': [], 'times': [], 'costs': []})
    
    for result in results:
        if result.ok:
            model_data[result.model]['scores'].append(result.score)
            model_data[result.model]['times'].append(result.elapsed_s)
            if result.cost_usd:
                model_data[result.model]['costs'].append(result.cost_usd)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comprehensive Model Performance Analysis', fontsize=16, fontweight='bold')
    
    # 1. Score Distribution
    model_names = list(model_data.keys())
    score_means = [np.mean(model_data[model]['scores']) for model in model_names]
    score_stds = [np.std(model_data[model]['scores']) for model in model_names]
    
    bars1 = ax1.bar(model_names, score_means, yerr=score_stds, capsize=5, alpha=0.7)
    ax1.set_title('Security Score Distribution', fontweight='bold')
    ax1.set_ylabel('Average Score')
    ax1.set_ylim(0, 1.1)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, mean, std in zip(bars1, score_means, score_stds):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + std + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. Response Time vs Accuracy
    times = [np.mean(model_data[model]['times']) for model in model_names]
    colors = plt.cm.viridis(np.linspace(0, 1, len(model_names)))
    
    scatter = ax2.scatter(times, score_means, c=colors, s=100, alpha=0.7)
    ax2.set_xlabel('Average Response Time (seconds)')
    ax2.set_ylabel('Average Security Score')
    ax2.set_title('Response Time vs Security Accuracy', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add model labels
    for i, model in enumerate(model_names):
        ax2.annotate(model, (times[i], score_means[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 3. Cost Analysis
    costs = [np.mean(model_data[model]['costs']) if model_data[model]['costs'] else 0 for model in model_names]
    bars3 = ax3.bar(model_names, costs, alpha=0.7, color='orange')
    ax3.set_title('Cost per Test Analysis', fontweight='bold')
    ax3.set_ylabel('Cost per Test ($)')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add cost labels
    for bar, cost in zip(bars3, costs):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(costs)*0.01,
                f'${cost:.5f}', ha='center', va='bottom', fontsize=8)
    
    # 4. Cost-Effectiveness
    effectiveness = [score/cost if cost > 0 else 0 for score, cost in zip(score_means, costs)]
    bars4 = ax4.bar(model_names, effectiveness, alpha=0.7, color='green')
    ax4.set_title('Cost-Effectiveness (Score per Dollar)', fontweight='bold')
    ax4.set_ylabel('Effectiveness Score')
    ax4.tick_params(axis='x', rotation=45)
    
    # Add effectiveness labels
    for bar, eff in zip(bars4, effectiveness):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + max(effectiveness)*0.01,
                f'{eff:.1f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = outdir / "improved_model_comparison.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def generate_test_type_analysis_chart(results: List, outdir: Path) -> str:
    """Generate test type difficulty analysis chart (from improved_chart_generation.py)"""
    
    if not VISUALIZATION_AVAILABLE:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available")
        return None
    
    # Group results by test type
    test_data = defaultdict(lambda: {'scores': [], 'times': [], 'count': 0})
    
    for result in results:
        if result.ok:
            test_data[result.suite_id]['scores'].append(result.score)
            test_data[result.suite_id]['times'].append(result.elapsed_s)
            test_data[result.suite_id]['count'] += 1
    
    # Calculate metrics
    test_names = list(test_data.keys())
    avg_scores = [np.mean(test_data[test]['scores']) for test in test_names]
    avg_times = [np.mean(test_data[test]['times']) for test in test_names]
    test_counts = [test_data[test]['count'] for test in test_names]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Test Type Difficulty Analysis', fontsize=16, fontweight='bold')
    
    # 1. Score distribution by test type
    bars1 = ax1.bar(range(len(test_names)), avg_scores, alpha=0.7, color='skyblue')
    ax1.set_title('Average Score by Test Type', fontweight='bold')
    ax1.set_ylabel('Average Score')
    ax1.set_xlabel('Test Type')
    ax1.set_xticks(range(len(test_names)))
    ax1.set_xticklabels(test_names, rotation=45, ha='right')
    ax1.set_ylim(0, 1.1)
    
    # Add score labels
    for i, (bar, score) in enumerate(zip(bars1, avg_scores)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. Response time by test type
    bars2 = ax2.bar(range(len(test_names)), avg_times, alpha=0.7, color='lightcoral')
    ax2.set_title('Average Response Time by Test Type', fontweight='bold')
    ax2.set_ylabel('Response Time (seconds)')
    ax2.set_xlabel('Test Type')
    ax2.set_xticks(range(len(test_names)))
    ax2.set_xticklabels(test_names, rotation=45, ha='right')
    
    # Add time labels
    for i, (bar, time) in enumerate(zip(bars2, avg_times)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(avg_times)*0.01,
                f'{time:.2f}s', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = outdir / "test_type_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def generate_language_effectiveness_chart(results: List, outdir: Path) -> str:
    """Generate language effectiveness analysis chart (from improved_chart_generation.py)"""
    
    if not VISUALIZATION_AVAILABLE:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available")
        return None
    
    # Group results by language
    language_data = defaultdict(lambda: {'scores': [], 'times': [], 'costs': [], 'count': 0})
    
    for result in results:
        if result.ok:
            language = improved_language_classification(result.suite_id)
            language_data[language]['scores'].append(result.score)
            language_data[language]['times'].append(result.elapsed_s)
            if result.cost_usd:
                language_data[language]['costs'].append(result.cost_usd)
            language_data[language]['count'] += 1
    
    # Calculate metrics
    languages = list(language_data.keys())
    avg_scores = [np.mean(language_data[lang]['scores']) for lang in languages]
    avg_times = [np.mean(language_data[lang]['times']) for lang in languages]
    avg_costs = [np.mean(language_data[lang]['costs']) if language_data[lang]['costs'] else 0 for lang in languages]
    test_counts = [language_data[lang]['count'] for lang in languages]
    
    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Language-Specific Security Analysis Performance', fontsize=16, fontweight='bold')
    
    # 1. Score by language
    bars1 = ax1.bar(languages, avg_scores, alpha=0.7, color='lightblue')
    ax1.set_title('Average Security Score by Language', fontweight='bold')
    ax1.set_ylabel('Average Score')
    ax1.set_ylim(0, 1.1)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Response time by language
    bars2 = ax2.bar(languages, avg_times, alpha=0.7, color='lightgreen')
    ax2.set_title('Average Response Time by Language', fontweight='bold')
    ax2.set_ylabel('Response Time (seconds)')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Cost by language
    bars3 = ax3.bar(languages, avg_costs, alpha=0.7, color='lightcoral')
    ax3.set_title('Average Cost by Language', fontweight='bold')
    ax3.set_ylabel('Cost per Test ($)')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Test count by language
    bars4 = ax4.bar(languages, test_counts, alpha=0.7, color='gold')
    ax4.set_title('Test Coverage by Language', fontweight='bold')
    ax4.set_ylabel('Number of Tests')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = outdir / "language_effectiveness_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def generate_enhanced_cost_effectiveness_chart(results: List, models: List[str], outdir: Path) -> str:
    """Generate enhanced cost-effectiveness analysis chart"""
    
    if not VISUALIZATION_AVAILABLE:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available")
        return None
    
    # Prepare data
    model_data = defaultdict(lambda: {'scores': [], 'costs': [], 'times': []})
    
    for result in results:
        if result.ok:
            model_data[result.model]['scores'].append(result.score)
            if result.cost_usd:
                model_data[result.model]['costs'].append(result.cost_usd)
            model_data[result.model]['times'].append(result.elapsed_s)
    
    # Calculate metrics
    model_names = list(model_data.keys())
    avg_scores = [np.mean(model_data[model]['scores']) for model in model_names]
    avg_costs = [np.mean(model_data[model]['costs']) if model_data[model]['costs'] else 0 for model in model_names]
    avg_times = [np.mean(model_data[model]['times']) for model in model_names]
    
    # Calculate effectiveness metrics
    traditional_effectiveness = [score/cost if cost > 0 else 0 for score, cost in zip(avg_scores, avg_costs)]
    
    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Enhanced Cost-Effectiveness Analysis', fontsize=16, fontweight='bold')
    
    # 1. Traditional effectiveness
    bars1 = ax1.bar(model_names, traditional_effectiveness, alpha=0.7, color='steelblue')
    ax1.set_title('Traditional Cost-Effectiveness (Score/Cost)', fontweight='bold')
    ax1.set_ylabel('Effectiveness Score')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Score vs Cost scatter
    scatter = ax2.scatter(avg_costs, avg_scores, s=100, alpha=0.7, c=avg_times, cmap='viridis')
    ax2.set_xlabel('Average Cost per Test ($)')
    ax2.set_ylabel('Average Security Score')
    ax2.set_title('Security Score vs Cost (colored by response time)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Response Time (seconds)')
    
    # Add model labels
    for i, model in enumerate(model_names):
        ax2.annotate(model, (avg_costs[i], avg_scores[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 3. Response time vs effectiveness
    scatter2 = ax3.scatter(avg_times, traditional_effectiveness, s=100, alpha=0.7, c=avg_scores, cmap='plasma')
    ax3.set_xlabel('Average Response Time (seconds)')
    ax3.set_ylabel('Cost-Effectiveness Score')
    ax3.set_title('Response Time vs Cost-Effectiveness (colored by accuracy)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar2 = plt.colorbar(scatter2, ax=ax3)
    cbar2.set_label('Security Score')
    
    # 4. Pareto frontier
    # Sort by effectiveness
    sorted_indices = sorted(range(len(traditional_effectiveness)), 
                          key=lambda i: traditional_effectiveness[i], reverse=True)
    
    pareto_models = [model_names[i] for i in sorted_indices]
    pareto_effectiveness = [traditional_effectiveness[i] for i in sorted_indices]
    pareto_scores = [avg_scores[i] for i in sorted_indices]
    
    ax4.plot(range(len(pareto_models)), pareto_effectiveness, 'o-', alpha=0.7, color='red')
    ax4.set_title('Model Rankings by Cost-Effectiveness', fontweight='bold')
    ax4.set_xlabel('Model Rank')
    ax4.set_ylabel('Cost-Effectiveness Score')
    ax4.set_xticks(range(len(pareto_models)))
    ax4.set_xticklabels(pareto_models, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = outdir / "enhanced_cost_effectiveness_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def integrate_improved_charts(results: List, models: List[str], outdir: Path) -> Dict[str, str]:
    """Integrate all improved charts with enhanced reporting (consolidated version)"""
    
    print("📊 === CONSOLIDATED VISUALIZATION GENERATION ===")
    
    charts = {}
    
    try:
        # 1. Model comparison chart
        print("🎯 Generating comprehensive model comparison chart...")
        chart_path = generate_model_comparison_chart(results, models, outdir)
        if chart_path:
            charts['improved_model_comparison'] = chart_path
            print(f"   ✓ Model comparison: {Path(chart_path).name}")
        else:
            print("   ⚠️ Model comparison chart skipped (visualization not available)")
        
    except Exception as e:
        print(f"   ❌ Model comparison chart failed: {e}")
    
    try:
        # 2. Test type analysis chart
        print("📋 Generating test type difficulty analysis...")
        chart_path = generate_test_type_analysis_chart(results, outdir)
        if chart_path:
            charts['test_type_analysis'] = chart_path
            print(f"   ✓ Test type analysis: {Path(chart_path).name}")
        else:
            print("   ⚠️ Test type analysis chart skipped (visualization not available)")
        
    except Exception as e:
        print(f"   ❌ Test type analysis chart failed: {e}")
    
    try:
        # 3. Language effectiveness chart
        print("🌐 Generating language effectiveness analysis...")
        chart_path = generate_language_effectiveness_chart(results, outdir)
        if chart_path:
            charts['language_effectiveness'] = chart_path
            print(f"   ✓ Language analysis: {Path(chart_path).name}")
        else:
            print("   ⚠️ Language effectiveness chart skipped (visualization not available)")
        
    except Exception as e:
        print(f"   ❌ Language effectiveness chart failed: {e}")
    
    try:
        # 4. Enhanced cost-effectiveness chart
        print("💰 Generating enhanced cost-effectiveness analysis...")
        chart_path = generate_enhanced_cost_effectiveness_chart(results, models, outdir)
        if chart_path:
            charts['enhanced_cost_effectiveness'] = chart_path
            print(f"   ✓ Cost-effectiveness: {Path(chart_path).name}")
        else:
            print("   ⚠️ Cost-effectiveness chart skipped (visualization not available)")
        
    except Exception as e:
        print(f"   ❌ Cost-effectiveness chart failed: {e}")
    
    # Report success
    report_visualization_success(charts, "consolidated improved")
    
    return charts


def generate_language_effectiveness_chart_from_dict(language_results: Dict, outdir: Path) -> str:
    """Generate effectiveness by language chart (adapted for consolidated reporting format)."""
    
    if not VISUALIZATION_AVAILABLE or not language_results:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available or no data")
        return None
    
    # Prepare data - language_results is Dict[language, metrics]
    languages = list(language_results.keys())
    effectiveness_scores = []
    
    for lang in languages:
        lang_data = language_results[lang]
        if isinstance(lang_data, dict) and 'effectiveness' in lang_data:
            effectiveness_scores.append(lang_data['effectiveness'])
        else:
            effectiveness_scores.append(0)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(languages, effectiveness_scores, color='skyblue', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, effectiveness_scores):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(effectiveness_scores)*0.01,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Cost-Effectiveness by Programming Language\n(Security Points per Dollar)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Programming Language', fontsize=12)
    ax.set_ylabel('Effectiveness (Points/$)', fontsize=12)
    ax.set_xticklabels(languages, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    chart_path = outdir / "language_effectiveness.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


def generate_owasp_effectiveness_chart(owasp_results: Dict, outdir: Path) -> str:
    """Generate effectiveness by OWASP category chart (adapted for consolidated reporting format)."""
    
    if not VISUALIZATION_AVAILABLE or not owasp_results:
        print("   ⚠️ Chart generation skipped - matplotlib/seaborn not available or no data")
        return None
    
    # Prepare data - owasp_results is Dict[category, metrics]
    categories = list(owasp_results.keys())
    effectiveness_scores = []
    
    for category in categories:
        cat_data = owasp_results[category]
        if isinstance(cat_data, dict) and 'effectiveness' in cat_data:
            effectiveness_scores.append(cat_data['effectiveness'])
        else:
            effectiveness_scores.append(0)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(15, 8))
    
    bars = ax.bar(categories, effectiveness_scores, color='lightcoral', alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, effectiveness_scores):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(effectiveness_scores)*0.01,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_title('Cost-Effectiveness by OWASP Top 10 Category\n(Security Points per Dollar)', fontsize=14, fontweight='bold')
    ax.set_xlabel('OWASP Category', fontsize=12)
    ax.set_ylabel('Effectiveness (Points/$)', fontsize=12)
    ax.set_xticklabels([cat.replace(' - ', '\n') for cat in categories], rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    chart_path = outdir / "owasp_effectiveness.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(chart_path)


# Backward compatibility functions
def integrate_improved_charts_legacy(results: List, models: List[str], outdir: Path) -> Dict[str, str]:
    """Backward compatibility wrapper"""
    return integrate_improved_charts(results, models, outdir)
