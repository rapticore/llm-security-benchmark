#!/usr/bin/env python3
"""
Improved Chart Generation Module

Fixes empty chart issues by improving data aggregation and visualization logic.
Built by the Rapticore Security Research Team
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


def improved_language_classification(test_id: str) -> str:
    """
    Enhanced language classification that's more permissive and useful for analysis.
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


def generate_improved_charts(results: List[Any], models: List[str], outdir: Path) -> Dict[str, str]:
    """
    Generate improved charts with better data aggregation and empty chart prevention.
    """
    charts_created = {}
    
    # Aggregate data by improved classifications
    model_data = defaultdict(lambda: defaultdict(list))
    test_type_data = defaultdict(lambda: defaultdict(list))
    language_data = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        if not hasattr(result, 'model') or not hasattr(result, 'score'):
            continue
            
        model = result.model
        score = result.score
        test_id = getattr(result, 'test_id', 'unknown')
        cost = getattr(result, 'cost_usd', 0.0)
        time = getattr(result, 'elapsed_s', 0.0)
        
        # Classify test
        language = improved_language_classification(test_id)
        
        # Aggregate by different dimensions
        model_data[model]['scores'].append(score)
        model_data[model]['costs'].append(cost)
        model_data[model]['times'].append(time)
        model_data[model]['tests'].append(test_id)
        
        test_type_data[test_id]['scores'].append(score)
        test_type_data[test_id]['models'].append(model)
        test_type_data[test_id]['costs'].append(cost)
        
        language_data[language]['scores'].append(score)
        language_data[language]['models'].append(model)
        language_data[language]['tests'].append(test_id)
    
    # Generate improved model comparison chart
    charts_created.update(_create_improved_model_comparison(model_data, outdir))
    
    # Generate test type analysis chart
    charts_created.update(_create_test_type_analysis(test_type_data, outdir))
    
    # Generate language effectiveness chart
    charts_created.update(_create_language_effectiveness(language_data, outdir))
    
    # Generate enhanced cost-effectiveness visualization
    charts_created.update(_create_enhanced_cost_effectiveness(model_data, outdir))
    
    return charts_created


def _create_improved_model_comparison(model_data: Dict, outdir: Path) -> Dict[str, str]:
    """Create an improved model comparison chart."""
    if not model_data:
        return {}
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    models = list(model_data.keys())
    
    # 1. Accuracy Distribution
    scores_by_model = [model_data[m]['scores'] for m in models]
    bp1 = ax1.boxplot(scores_by_model, labels=[m.replace('-', '\n')[:15] for m in models], 
                      patch_artist=True)
    ax1.set_title('Score Distribution by Model', fontweight='bold', fontsize=14)
    ax1.set_ylabel('Security Score')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Color the boxes
    colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # 2. Average Performance
    avg_scores = [np.mean(model_data[m]['scores']) for m in models]
    bars2 = ax2.bar(range(len(models)), avg_scores, color=colors, alpha=0.8)
    ax2.set_title('Average Security Score by Model', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Average Score')
    ax2.set_xticks(range(len(models)))
    ax2.set_xticklabels([m.replace('-', '\n')[:15] for m in models], rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, score in zip(bars2, avg_scores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Response Time vs Accuracy
    for i, model in enumerate(models):
        if model_data[model]['times'] and model_data[model]['scores']:
            avg_time = np.mean(model_data[model]['times'])
            avg_score = np.mean(model_data[model]['scores'])
            ax3.scatter(avg_time, avg_score, s=100, alpha=0.8, color=colors[i], label=model)
    
    ax3.set_title('Response Time vs Accuracy', fontweight='bold', fontsize=14)
    ax3.set_xlabel('Average Response Time (seconds)')
    ax3.set_ylabel('Average Security Score')
    ax3.grid(True, alpha=0.3)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 4. Test Coverage
    test_counts = [len(set(model_data[m]['tests'])) for m in models]
    bars4 = ax4.bar(range(len(models)), test_counts, color=colors, alpha=0.8)
    ax4.set_title('Test Coverage by Model', fontweight='bold', fontsize=14)
    ax4.set_ylabel('Number of Different Tests')
    ax4.set_xticks(range(len(models)))
    ax4.set_xticklabels([m.replace('-', '\n')[:15] for m in models], rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, count in zip(bars4, test_counts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    chart_path = outdir / "improved_model_comparison.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {"improved_model_comparison": str(chart_path)}


def _create_test_type_analysis(test_type_data: Dict, outdir: Path) -> Dict[str, str]:
    """Create test type analysis chart."""
    if not test_type_data:
        return {}
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    test_types = list(test_type_data.keys())
    
    # 1. Average difficulty by test type
    avg_scores = []
    std_scores = []
    sample_sizes = []
    
    for test_type in test_types:
        scores = test_type_data[test_type]['scores']
        avg_scores.append(np.mean(scores))
        std_scores.append(np.std(scores))
        sample_sizes.append(len(scores))
    
    # Sort by difficulty (ascending scores)
    sorted_indices = np.argsort(avg_scores)
    test_types_sorted = [test_types[i] for i in sorted_indices]
    avg_scores_sorted = [avg_scores[i] for i in sorted_indices]
    std_scores_sorted = [std_scores[i] for i in sorted_indices]
    sample_sizes_sorted = [sample_sizes[i] for i in sorted_indices]
    
    colors = plt.cm.RdYlBu_r(np.linspace(0, 1, len(test_types_sorted)))
    bars1 = ax1.barh(range(len(test_types_sorted)), avg_scores_sorted, 
                     xerr=std_scores_sorted, color=colors, alpha=0.8)
    
    ax1.set_title('Average Difficulty by Test Type\n(Lower scores = harder tests)', 
                  fontweight='bold', fontsize=14)
    ax1.set_xlabel('Average Security Score')
    ax1.set_yticks(range(len(test_types_sorted)))
    ax1.set_yticklabels([t.replace('_', ' ').title() for t in test_types_sorted])
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add value and sample size labels
    for i, (bar, score, n) in enumerate(zip(bars1, avg_scores_sorted, sample_sizes_sorted)):
        width = bar.get_width()
        ax1.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{score:.2f}\n(n={n})', va='center', ha='left', fontsize=9)
    
    # 2. Test type distribution
    ax2.pie(sample_sizes_sorted, labels=[t.replace('_', ' ').title() for t in test_types_sorted],
            autopct='%1.1f%%', colors=colors)
    ax2.set_title('Test Distribution\n(by number of evaluations)', 
                  fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    chart_path = outdir / "test_type_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {"test_type_analysis": str(chart_path)}


def _create_language_effectiveness(language_data: Dict, outdir: Path) -> Dict[str, str]:
    """Create language effectiveness analysis."""
    if not language_data:
        return {}
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    languages = list(language_data.keys())
    
    # 1. Average performance by language category
    avg_scores = [np.mean(language_data[lang]['scores']) for lang in languages]
    sample_sizes = [len(language_data[lang]['scores']) for lang in languages]
    
    # Sort by performance
    sorted_indices = np.argsort(avg_scores)[::-1]
    languages_sorted = [languages[i] for i in sorted_indices]
    avg_scores_sorted = [avg_scores[i] for i in sorted_indices]
    sample_sizes_sorted = [sample_sizes[i] for i in sorted_indices]
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(languages_sorted)))
    bars1 = ax1.bar(range(len(languages_sorted)), avg_scores_sorted, color=colors, alpha=0.8)
    
    ax1.set_title('Average Performance by Security Domain', fontweight='bold', fontsize=14)
    ax1.set_ylabel('Average Security Score')
    ax1.set_xticks(range(len(languages_sorted)))
    ax1.set_xticklabels(languages_sorted, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add labels
    for bar, score, n in zip(bars1, avg_scores_sorted, sample_sizes_sorted):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.2f}\n(n={n})', ha='center', va='bottom', fontsize=9)
    
    # 2. Distribution of scores by language
    scores_by_lang = [language_data[lang]['scores'] for lang in languages_sorted]
    bp2 = ax2.boxplot(scores_by_lang, labels=[l[:10] for l in languages_sorted], patch_artist=True)
    ax2.set_title('Score Distribution by Domain', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Security Score')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # 3. Sample size distribution
    ax3.pie(sample_sizes_sorted, labels=languages_sorted, autopct='%1.1f%%', colors=colors)
    ax3.set_title('Test Distribution by Security Domain', fontweight='bold', fontsize=14)
    
    # 4. Performance vs coverage
    unique_tests = [len(set(language_data[lang]['tests'])) for lang in languages_sorted]
    ax4.scatter(unique_tests, avg_scores_sorted, s=np.array(sample_sizes_sorted)*3, 
               c=colors, alpha=0.7)
    
    # Add labels
    for i, lang in enumerate(languages_sorted):
        ax4.annotate(lang, (unique_tests[i], avg_scores_sorted[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax4.set_title('Domain Coverage vs Performance\n(bubble size = sample count)', 
                  fontweight='bold', fontsize=14)
    ax4.set_xlabel('Number of Different Test Types')
    ax4.set_ylabel('Average Security Score')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    chart_path = outdir / "language_effectiveness_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {"language_effectiveness_analysis": str(chart_path)}


def _create_enhanced_cost_effectiveness(model_data: Dict, outdir: Path) -> Dict[str, str]:
    """Create enhanced cost-effectiveness visualization addressing gaming issues."""
    if not model_data:
        return {}
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    models = list(model_data.keys())
    
    # Calculate enhanced metrics for each model
    model_metrics = {}
    for model in models:
        scores = model_data[model]['scores']
        costs = model_data[model]['costs']
        times = model_data[model]['times']
        
        if scores and costs:
            avg_score = np.mean(scores)
            avg_cost = np.mean(costs)
            avg_time = np.mean(times) if times else 0
            
            # Traditional cost-effectiveness
            traditional_ce = avg_score / avg_cost if avg_cost > 0 else 0
            
            # Quality-adjusted (penalize low scores exponentially)
            quality_adjusted_ce = (avg_score ** 1.5) / avg_cost if avg_cost > 0 else 0
            
            # Response completeness proxy (longer responses often better for security)
            # This is a simplification - in real implementation would analyze actual response content
            completeness_factor = min(1.0, len(str(scores)) / 10)  # Simplified proxy
            
            # Practical effectiveness (accounts for multiple rounds needed for poor responses)
            rounds_needed = 1.0 if avg_score > 0.7 else (2.0 if avg_score < 0.5 else 1.5)
            practical_ce = (avg_score * completeness_factor) / (avg_cost * rounds_needed) if avg_cost > 0 else 0
            
            model_metrics[model] = {
                'traditional': traditional_ce,
                'quality_adjusted': quality_adjusted_ce,
                'practical': practical_ce,
                'avg_score': avg_score,
                'avg_cost': avg_cost,
                'avg_time': avg_time
            }
    
    # 1. Traditional vs Quality-Adjusted Cost-Effectiveness
    traditional_ces = [model_metrics[m]['traditional'] for m in models]
    quality_ces = [model_metrics[m]['quality_adjusted'] for m in models]
    
    x = np.arange(len(models))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, traditional_ces, width, label='Traditional (Score/Cost)', alpha=0.8)
    bars2 = ax1.bar(x + width/2, quality_ces, width, label='Quality-Adjusted (Score¹·⁵/Cost)', alpha=0.8)
    
    ax1.set_title('Traditional vs Quality-Adjusted Cost-Effectiveness\n(Quality-adjusted prevents gaming by cheap models)', 
                  fontweight='bold', fontsize=12)
    ax1.set_ylabel('Cost-Effectiveness (Points per Dollar)')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.replace('-', '\n')[:15] for m in models], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Practical Effectiveness (Real-world usage)
    practical_ces = [model_metrics[m]['practical'] for m in models]
    colors = plt.cm.viridis(np.linspace(0, 1, len(models)))
    
    bars3 = ax2.bar(range(len(models)), practical_ces, color=colors, alpha=0.8)
    ax2.set_title('Practical Cost-Effectiveness\n(Accounts for multiple rounds needed for poor responses)', 
                  fontweight='bold', fontsize=12)
    ax2.set_ylabel('Practical Points per Dollar')
    ax2.set_xticks(range(len(models)))
    ax2.set_xticklabels([m.replace('-', '\n')[:15] for m in models], rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, ce in zip(bars3, practical_ces):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(practical_ces)*0.01,
                f'{ce:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 3. Cost vs Performance (bubble chart)
    avg_scores = [model_metrics[m]['avg_score'] for m in models]
    avg_costs = [model_metrics[m]['avg_cost'] for m in models]
    
    # Size bubbles by quality-adjusted effectiveness
    bubble_sizes = [max(50, model_metrics[m]['quality_adjusted'] / 10) for m in models]
    
    scatter = ax3.scatter(avg_costs, avg_scores, s=bubble_sizes, c=colors, alpha=0.7)
    ax3.set_title('Cost vs Performance\n(Bubble size = Quality-Adjusted Cost-Effectiveness)', 
                  fontweight='bold', fontsize=12)
    ax3.set_xlabel('Average Cost per Test ($)')
    ax3.set_ylabel('Average Security Score')
    ax3.grid(True, alpha=0.3)
    
    # Add model labels
    for i, model in enumerate(models):
        ax3.annotate(model.replace('-', '\n')[:10], (avg_costs[i], avg_scores[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 4. Quality tier classification
    tier_data = {'Enterprise Grade': [], 'Value Champion': [], 'Budget Option': [], 'Problematic': []}
    
    for model in models:
        metrics = model_metrics[model]
        score = metrics['avg_score']
        cost = metrics['avg_cost']
        quality_ce = metrics['quality_adjusted']
        
        if score >= 0.8 and cost >= 0.01:
            tier_data['Enterprise Grade'].append(model)
        elif quality_ce >= 500 and score >= 0.6:
            tier_data['Value Champion'].append(model)
        elif score >= 0.5:
            tier_data['Budget Option'].append(model)
        else:
            tier_data['Problematic'].append(model)
    
    # Create tier visualization
    tier_names = list(tier_data.keys())
    tier_counts = [len(tier_data[tier]) for tier in tier_names]
    tier_colors = ['gold', 'lightgreen', 'lightblue', 'lightcoral']
    
    bars4 = ax4.bar(tier_names, tier_counts, color=tier_colors, alpha=0.8)
    ax4.set_title('Model Classification by Performance Tier', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Number of Models')
    ax4.tick_params(axis='x', rotation=45)
    
    # Add count labels
    for bar, count in zip(bars4, tier_counts):
        if count > 0:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    chart_path = outdir / "enhanced_cost_effectiveness_analysis.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {"enhanced_cost_effectiveness_analysis": str(chart_path)}


# Integration function for existing codebase
def integrate_improved_charts(results, models, outdir):
    """Integration function to be called from main benchmark."""
    try:
        improved_charts = generate_improved_charts(results, models, outdir)
        print(f"✅ Generated {len(improved_charts)} improved charts")
        return improved_charts
    except Exception as e:
        print(f"⚠️ Improved chart generation failed: {e}")
        return {}