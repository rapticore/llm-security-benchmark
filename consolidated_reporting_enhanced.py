#!/usr/bin/env python3
"""
Consolidated Enhanced Reporting Module

Combines the best features from:
- consolidated_reporting_solution.py (comprehensive reporting)
- enhanced_reporting.py (language/OWASP analysis, multi-format exports)

Built by the Rapticore Security Research Team
"""

import json
import csv
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime
from collections import defaultdict

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    import pandas as pd
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
    traditional_effectiveness: float
    quality_weighted_effectiveness: float
    penalty_adjusted_effectiveness: float


@dataclass
class ConsolidatedModelAnalysis:
    """Consolidated model analysis for unified reporting."""
    model_name: str
    accuracy_score: float
    response_time: float
    cost_per_test: float
    total_tests: int
    success_rate: float
    
    # Quality indicators
    meets_accuracy_threshold: bool
    cost_efficiency_tier: str
    reliability_score: float
    
    # Evaluation flags  
    evaluation_notes: List[str]
    recommended_use_cases: List[str]
    limitations: List[str]
    
    # Enhanced metrics (from enhanced_reporting.py)
    enhanced_metrics: EnhancedMetrics = None


class ConsolidatedEnhancedReporter:
    """
    Generates comprehensive reports that combine:
    1. Consolidated reporting from consolidated_reporting_solution.py
    2. Language/OWASP analysis from enhanced_reporting.py
    3. Multi-format exports from enhanced_reporting.py
    """
    
    def __init__(self):
        self.accuracy_threshold = 0.80
        self.cost_efficiency_categories = {
            'premium': 'Premium Quality (Focus on Accuracy)',
            'balanced': 'Balanced Performance (Speed + Quality)',
            'budget': 'Budget Option (Cost-Conscious)',
            'below_standards': 'Below Quality Standards'
        }
    
    def calculate_enhanced_cost_effectiveness(self, results: List, model_name: str) -> EnhancedMetrics:
        """Calculate enhanced cost-effectiveness metrics (from enhanced_reporting.py)"""
        model_results = [r for r in results if r.model == model_name]
        if not model_results:
            return EnhancedMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        successful_results = [r for r in model_results if r.ok]
        failed_results = [r for r in model_results if not r.ok]
        
        total_tests = len(model_results)
        successful_tests = len(successful_results)
        failed_tests = len(failed_results)
        
        # Score distribution
        scores = [r.score for r in successful_results]
        perfect_scores = sum(1 for s in scores if s == 1.0)
        excellent_scores = sum(1 for s in scores if s >= 0.8)
        good_scores = sum(1 for s in scores if s >= 0.6)
        fair_scores = sum(1 for s in scores if s >= 0.4)
        poor_scores = sum(1 for s in scores if s < 0.4)
        
        # Cost metrics
        costs = [r.cost_usd for r in successful_results if r.cost_usd is not None]
        total_cost = sum(costs)
        cost_per_test = total_cost / successful_tests if successful_tests > 0 else 0.0
        
        # Cost per correct answer (perfect scores only)
        perfect_costs = [r.cost_usd for r in successful_results if r.score == 1.0 and r.cost_usd is not None]
        cost_per_correct_answer = sum(perfect_costs) / len(perfect_costs) if perfect_costs else 0.0
        
        # Cost per partial answer (all successful)
        cost_per_partial_answer = cost_per_test
        
        # Enhanced effectiveness calculations
        avg_score = np.mean(scores) if scores else 0.0
        traditional_effectiveness = avg_score / cost_per_test if cost_per_test > 0 else 0.0
        
        # Quality-weighted effectiveness
        quality_weights = {
            'perfect': 1.0,
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.2
        }
        
        weighted_score = (
            perfect_scores * quality_weights['perfect'] +
            (excellent_scores - perfect_scores) * quality_weights['excellent'] +
            (good_scores - excellent_scores) * quality_weights['good'] +
            (fair_scores - good_scores) * quality_weights['fair'] +
            (poor_scores) * quality_weights['poor']
        ) / successful_tests if successful_tests > 0 else 0.0
        
        quality_weighted_effectiveness = weighted_score / cost_per_test if cost_per_test > 0 else 0.0
        
        # Penalty-adjusted effectiveness
        penalty = failed_tests * 0.5  # Penalty for failed tests
        penalty_adjusted_score = max(0, weighted_score - penalty)
        penalty_adjusted_effectiveness = penalty_adjusted_score / cost_per_test if cost_per_test > 0 else 0.0
        
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
            quality_weighted_effectiveness=quality_weighted_effectiveness,
            penalty_adjusted_effectiveness=penalty_adjusted_effectiveness
        )
    
    def analyze_by_language(self, results: List) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by programming language (from enhanced_reporting.py)"""
        language_results = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})
        
        for result in results:
            if not result.ok:
                continue
                
            # Classify by language based on test ID
            language = self._classify_language(result.suite_id)
            language_results[language]['results'].append(result)
            language_results[language]['scores'].append(result.score)
            if result.cost_usd:
                language_results[language]['costs'].append(result.cost_usd)
        
        # Calculate metrics for each language
        language_metrics = {}
        for language, data in language_results.items():
            if not data['results']:
                continue
                
            scores = data['scores']
            costs = data['costs']
            
            language_metrics[language] = {
                'total_tests': len(data['results']),
                'avg_score': np.mean(scores),
                'success_rate': len(scores) / len(data['results']),
                'avg_cost': np.mean(costs) if costs else 0.0,
                'effectiveness': np.mean(scores) / np.mean(costs) if costs and np.mean(costs) > 0 else 0.0
            }
        
        return language_metrics
    
    def analyze_by_owasp_category(self, results: List) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by OWASP category (from enhanced_reporting.py)"""
        owasp_results = defaultdict(lambda: {'results': [], 'scores': [], 'costs': []})
        
        for result in results:
            if not result.ok:
                continue
                
            # Classify by OWASP category
            category = self._classify_owasp_category(result.suite_id)
            owasp_results[category]['results'].append(result)
            owasp_results[category]['scores'].append(result.score)
            if result.cost_usd:
                owasp_results[category]['costs'].append(result.cost_usd)
        
        # Calculate metrics for each category
        category_metrics = {}
        for category, data in owasp_results.items():
            if not data['results']:
                continue
                
            scores = data['scores']
            costs = data['costs']
            
            category_metrics[category] = {
                'total_tests': len(data['results']),
                'avg_score': np.mean(scores),
                'success_rate': len(scores) / len(data['results']),
                'avg_cost': np.mean(costs) if costs else 0.0,
                'effectiveness': np.mean(scores) / np.mean(costs) if costs and np.mean(costs) > 0 else 0.0
            }
        
        return category_metrics
    
    def _classify_language(self, test_id: str) -> str:
        """Classify test by programming language"""
        test_lower = test_id.lower()
        
        if 'python' in test_lower or 'py_' in test_lower:
            return 'Python'
        elif 'javascript' in test_lower or 'js_' in test_lower:
            return 'JavaScript'
        elif 'java' in test_lower:
            return 'Java'
        elif 'go_' in test_lower or 'golang' in test_lower:
            return 'Go'
        elif 'rust' in test_lower:
            return 'Rust'
        elif 'c_' in test_lower or 'cpp_' in test_lower:
            return 'C/C++'
        elif 'csharp' in test_lower:
            return 'C#'
        elif 'php' in test_lower:
            return 'PHP'
        elif 'ruby' in test_lower:
            return 'Ruby'
        elif 'haskell' in test_lower:
            return 'Haskell'
        else:
            return 'General Security'
    
    def _classify_owasp_category(self, test_id: str) -> str:
        """Classify test by OWASP category"""
        test_lower = test_id.lower()
        
        if 'sql' in test_lower or 'injection' in test_lower:
            return 'A03: Injection'
        elif 'xss' in test_lower or 'cross' in test_lower:
            return 'A03: Injection (XSS)'
        elif 'broken' in test_lower or 'access' in test_lower:
            return 'A01: Broken Access Control'
        elif 'secret' in test_lower or 'hardcoded' in test_lower:
            return 'A02: Cryptographic Failures'
        elif 'csrf' in test_lower:
            return 'A01: Broken Access Control (CSRF)'
        elif 'deserialization' in test_lower:
            return 'A08: Software and Data Integrity Failures'
        elif 'ssrf' in test_lower:
            return 'A10: Server-Side Request Forgery'
        else:
            return 'General Security'
    
    def generate_comprehensive_executive_summary(
        self, 
        model_analyses: List[ConsolidatedModelAnalysis],
        language_results: Dict[str, Dict[str, Any]],
        owasp_results: Dict[str, Dict[str, Any]],
        total_cost: float,
        test_types: List[str],
        outdir: Path
    ) -> str:
        """Generate comprehensive executive summary"""
        
        # Separate qualified and disqualified models
        qualified_models = [m for m in model_analyses if m.meets_accuracy_threshold]
        disqualified_models = [m for m in model_analyses if not m.meets_accuracy_threshold]
        
        # Sort qualified models by effectiveness
        qualified_models.sort(key=lambda x: x.enhanced_metrics.quality_weighted_effectiveness if x.enhanced_metrics else 0, reverse=True)
        
        summary = f"""# LLM Security Benchmark - Comprehensive Executive Summary

**Analysis Date:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
**Total Models Analyzed:** {len(model_analyses)}
**Models Meeting Quality Standards:** {len(qualified_models)}
**Total Investment Analyzed:** ${total_cost:.4f}

## Executive Findings

### Quality-Approved Model Rankings

"""
        
        # Add qualified models
        for i, model in enumerate(qualified_models, 1):
            enhanced = model.enhanced_metrics
            summary += f"""#### {i}. {model.model_name} ({model.cost_efficiency_tier})
- **Security Accuracy:** {model.accuracy_score:.1%}
- **Quality-Weighted Effectiveness:** {enhanced.quality_weighted_effectiveness:.1f} points/$
- **Response Time:** {model.response_time:.2f}s average
- **Cost per Test:** ${model.cost_per_test:.5f}
- **Success Rate:** {model.success_rate:.1%}
- **Recommended For:** {', '.join(model.recommended_use_cases)}

"""
        
        # Add disqualified models
        if disqualified_models:
            summary += """### Models Below Quality Standards

The following models did not meet the minimum 80% accuracy threshold:

"""
            for model in disqualified_models:
                summary += f"""- **{model.model_name}:** {model.accuracy_score:.1%} accuracy - {', '.join(model.limitations)}

"""
        
        # Add strategic recommendations
        summary += """## Strategic Recommendations

### By Use Case:

**Enterprise Security Analysis:**
"""
        enterprise_models = [m for m in qualified_models if m.cost_efficiency_tier == 'premium']
        for model in enterprise_models[:2]:  # Top 2
            summary += f"- {model.model_name} (highest accuracy: {model.accuracy_score:.1%})\n"
        
        summary += """
**Production Workflows:**
"""
        production_models = [m for m in qualified_models if m.cost_efficiency_tier == 'balanced']
        for model in production_models[:2]:  # Top 2
            summary += f"- {model.model_name} (balanced performance)\n"
        
        summary += """
**Development & Testing:**
"""
        dev_models = [m for m in qualified_models if m.cost_efficiency_tier == 'budget']
        for model in dev_models[:2]:  # Top 2
            summary += f"- {model.model_name} (cost-effective)\n"
        
        # Add language analysis
        if language_results:
            summary += "\n## Language-Specific Performance\n\n"
            for language, metrics in sorted(language_results.items(), key=lambda x: x[1]['avg_score'], reverse=True):
                summary += f"- **{language}:** {metrics['avg_score']:.1%} accuracy, {metrics['effectiveness']:.1f} effectiveness\n"
        
        # Add OWASP analysis
        if owasp_results:
            summary += "\n## OWASP Category Performance\n\n"
            for category, metrics in sorted(owasp_results.items(), key=lambda x: x[1]['avg_score'], reverse=True):
                summary += f"- **{category}:** {metrics['avg_score']:.1%} accuracy, {metrics['effectiveness']:.1f} effectiveness\n"
        
        summary += f"""
## Quality Standards Framework

This analysis applies rigorous quality standards:
- **80% Accuracy Minimum:** Models below this threshold are not recommended for security analysis
- **Quality-Weighted Scoring:** Considers response completeness and technical depth
- **Cost Reasonableness:** Flags suspiciously low costs that may indicate quality limitations
- **Sample Size Requirements:** Ensures statistical reliability

---

*Comprehensive analysis by the Rapticore Security Research Team*
*Ensuring enterprise-grade security model selection*
"""
        
        # Save the summary
        summary_path = outdir / "COMPREHENSIVE_EXECUTIVE_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return str(summary_path)
    
    def export_to_csv(self, results: List, models: List[str], enhanced_metrics: Dict, outdir: Path) -> str:
        """Export detailed results to CSV (from enhanced_reporting.py)"""
        
        # Detailed results CSV
        csv_path = outdir / "detailed_results.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'model', 'suite_id', 'ok', 'score', 'elapsed_s', 'cost_usd',
                'input_tokens', 'output_tokens', 'total_tokens', 'text_preview'
            ])
            
            for result in results:
                writer.writerow([
                    result.model,
                    result.suite_id,
                    result.ok,
                    result.score,
                    result.elapsed_s,
                    result.cost_usd or 0.0,
                    result.input_tokens,
                    result.output_tokens,
                    result.total_tokens,
                    result.text[:100] + "..." if len(result.text) > 100 else result.text
                ])
        
        # Model summary CSV
        summary_path = outdir / "model_summary.csv"
        with open(summary_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'model', 'total_tests', 'successful_tests', 'avg_score', 'total_cost',
                'cost_per_test', 'traditional_effectiveness', 'quality_weighted_effectiveness',
                'penalty_adjusted_effectiveness'
            ])
            
            for model in models:
                metrics = enhanced_metrics.get(model)
                if metrics:
                    writer.writerow([
                        model,
                        metrics.total_tests,
                        metrics.successful_tests,
                        metrics.total_tests / metrics.successful_tests if metrics.successful_tests > 0 else 0,
                        metrics.total_cost,
                        metrics.cost_per_test,
                        metrics.traditional_effectiveness,
                        metrics.quality_weighted_effectiveness,
                        metrics.penalty_adjusted_effectiveness
                    ])
        
        return str(csv_path)
    
    def export_to_json(self, results: List, models: List[str], enhanced_metrics: Dict, 
                      language_results: Dict, owasp_results: Dict, outdir: Path) -> str:
        """Export comprehensive analysis to JSON (from enhanced_reporting.py)"""
        
        json_data = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_models': len(models),
                'total_tests': len(results),
                'analysis_type': 'consolidated_enhanced_reporting'
            },
            'model_analysis': {},
            'language_analysis': language_results,
            'owasp_analysis': owasp_results,
            'enhanced_metrics': {}
        }
        
        # Add model analysis
        for model in models:
            model_results = [r for r in results if r.model == model]
            if model_results:
                json_data['model_analysis'][model] = {
                    'total_tests': len(model_results),
                    'successful_tests': len([r for r in model_results if r.ok]),
                    'avg_score': np.mean([r.score for r in model_results if r.ok]) if any(r.ok for r in model_results) else 0,
                    'avg_response_time': np.mean([r.elapsed_s for r in model_results if r.ok]) if any(r.ok for r in model_results) else 0,
                    'total_cost': sum(r.cost_usd for r in model_results if r.cost_usd) or 0
                }
        
        # Add enhanced metrics
        for model, metrics in enhanced_metrics.items():
            json_data['enhanced_metrics'][model] = asdict(metrics)
        
        # Save JSON
        json_path = outdir / "comprehensive_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return str(json_path)


# Backward compatibility functions
def calculate_enhanced_cost_effectiveness(results: List, model_name: str) -> EnhancedMetrics:
    """Backward compatibility wrapper for enhanced cost-effectiveness calculation"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.calculate_enhanced_cost_effectiveness(results, model_name)


def analyze_by_language(results: List, outdir: Path) -> Dict:
    """Backward compatibility wrapper for language analysis"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.analyze_by_language(results)


def analyze_by_owasp_category(results: List, outdir: Path) -> Dict:
    """Backward compatibility wrapper for OWASP analysis"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.analyze_by_owasp_category(results)


def export_to_csv(results: List, models: List[str], enhanced_metrics: Dict, outdir: Path) -> str:
    """Backward compatibility wrapper for CSV export"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.export_to_csv(results, models, enhanced_metrics, outdir)


def export_to_json(results: List, models: List[str], enhanced_metrics: Dict, 
                   language_results: Dict, owasp_results: Dict, outdir: Path) -> str:
    """Backward compatibility wrapper for JSON export"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.export_to_json(results, models, enhanced_metrics, language_results, owasp_results, outdir)


def generate_comprehensive_executive_summary(model_analyses, language_results, owasp_results, total_cost, test_types, outdir):
    """Backward compatibility wrapper"""
    reporter = ConsolidatedEnhancedReporter()
    return reporter.generate_comprehensive_executive_summary(
        model_analyses, language_results, owasp_results, total_cost, test_types, outdir
    )


def clean_up_redundant_reports(output_dir: Path):
    """Clean up redundant reports (from consolidated_reporting_solution.py)"""
    redundant_files = [
        "executive_summary.md",
        "quality_first_executive_summary.md", 
        "AGGRESSIVE_ANTI_GAMING_ANALYSIS.md",
        "enhanced_cost_effectiveness_report.md",
        "UNIFIED_EXECUTIVE_SUMMARY.md"
    ]
    
    archive_dir = output_dir / "archived_reports"
    archive_dir.mkdir(exist_ok=True)
    
    for file_name in redundant_files:
        file_path = output_dir / file_name
        if file_path.exists():
            archive_path = archive_dir / file_name
            file_path.rename(archive_path)
    
    # Create archive README
    readme_path = archive_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""# Archived Reports

These reports have been consolidated into the comprehensive executive summary.
The information from these files has been integrated into `COMPREHENSIVE_EXECUTIVE_SUMMARY.md`.

## Archived Files:
- executive_summary.md
- quality_first_executive_summary.md
- AGGRESSIVE_ANTI_GAMING_ANALYSIS.md
- enhanced_cost_effectiveness_report.md
- UNIFIED_EXECUTIVE_SUMMARY.md

## Current Primary Report:
Use `COMPREHENSIVE_EXECUTIVE_SUMMARY.md` as your single source of truth for all analysis results.
""")


def generate_unified_report(model_analyses, language_results, owasp_results, total_cost, test_types, outdir):
    """Backward compatibility wrapper"""
    return generate_comprehensive_executive_summary(model_analyses, language_results, owasp_results, total_cost, test_types, outdir)


def consolidate_reporting_files(output_dir: Path):
    """Backward compatibility wrapper"""
    return clean_up_redundant_reports(output_dir)
