#!/usr/bin/env python3
"""
Enhanced Cost-Effectiveness Analysis Module

Addresses critical flaws in cost-effectiveness calculations that allow
cheap-but-poor models to artificially dominate rankings.

Built by the Rapticore Security Research Team
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import re
from collections import defaultdict


@dataclass
class ResponseQualityMetrics:
    """Response quality assessment metrics."""
    word_count: int
    technical_terms_count: int
    security_concepts_covered: int
    mitigation_strategies_mentioned: int
    completeness_score: float  # 0.0 to 1.0
    depth_score: float  # 0.0 to 1.0


@dataclass  
class EnhancedEffectivenessScore:
    """Enhanced cost-effectiveness with quality adjustments."""
    model_name: str
    raw_effectiveness: float  # Traditional score/cost
    quality_adjusted: float   # With response quality factored in
    practical_effectiveness: float  # Real-world usability
    tier: str  # accuracy_leader, value_champion, practical_choice, enterprise_grade
    quality_metrics: ResponseQualityMetrics
    warnings: List[str]  # Quality concerns


class EnhancedCostEffectivenessAnalyzer:
    """
    Advanced cost-effectiveness analyzer that prevents gaming by cheap models
    with poor response quality.
    """
    
    def __init__(self):
        self.min_score_threshold = 0.6  # Exclude models below 60% accuracy
        self.min_response_length = 50   # Minimum words for security analysis
        self.security_terms = {
            'injection', 'xss', 'csrf', 'authentication', 'authorization', 
            'sanitize', 'validate', 'parameter', 'prepared', 'escape',
            'vulnerability', 'attack', 'exploit', 'mitigation', 'secure',
            'owasp', 'sql', 'command', 'script', 'malicious', 'input'
        }
        self.mitigation_terms = {
            'parameter', 'prepared', 'sanitize', 'validate', 'escape',
            'whitelist', 'blacklist', 'encoding', 'filter', 'patch',
            'update', 'fix', 'remediat', 'prevent', 'protect'
        }
    
    def analyze_response_quality(self, response_text: str, test_type: str) -> ResponseQualityMetrics:
        """Analyze the quality and completeness of a security response."""
        if not response_text:
            return ResponseQualityMetrics(0, 0, 0, 0, 0.0, 0.0)
        
        words = response_text.lower().split()
        word_count = len(words)
        
        # Count security-related technical terms
        technical_terms = sum(1 for word in words if any(term in word for term in self.security_terms))
        
        # Count security concepts covered (unique terms)
        security_concepts = len(set(word for word in words if any(term in word for term in self.security_terms)))
        
        # Count mitigation strategies mentioned
        mitigation_mentions = sum(1 for word in words if any(term in word for term in self.mitigation_terms))
        
        # Calculate completeness score based on expected elements for security analysis
        completeness_factors = []
        
        # Check for vulnerability identification
        if any(term in response_text.lower() for term in ['vulnerability', 'vuln', 'flaw', 'issue', 'risk']):
            completeness_factors.append(0.25)
            
        # Check for impact/consequence discussion  
        if any(term in response_text.lower() for term in ['impact', 'consequence', 'damage', 'exploit', 'attack']):
            completeness_factors.append(0.25)
            
        # Check for mitigation/fix discussion
        if mitigation_mentions > 0:
            completeness_factors.append(0.25)
            
        # Check for technical depth (code examples, specific techniques)
        if any(term in response_text.lower() for term in ['example', 'code', 'query', 'statement', 'function']):
            completeness_factors.append(0.25)
        
        completeness_score = sum(completeness_factors)
        
        # Calculate technical depth score
        depth_factors = []
        
        # Reward detailed responses
        if word_count >= 100:
            depth_factors.append(0.3)
        elif word_count >= 50:
            depth_factors.append(0.15)
            
        # Reward technical terminology usage
        if technical_terms >= 5:
            depth_factors.append(0.3)
        elif technical_terms >= 3:
            depth_factors.append(0.15)
            
        # Reward diverse security concept coverage
        if security_concepts >= 4:
            depth_factors.append(0.4)
        elif security_concepts >= 2:
            depth_factors.append(0.2)
        
        depth_score = min(1.0, sum(depth_factors))
        
        return ResponseQualityMetrics(
            word_count=word_count,
            technical_terms_count=technical_terms,
            security_concepts_covered=security_concepts,
            mitigation_strategies_mentioned=mitigation_mentions,
            completeness_score=completeness_score,
            depth_score=depth_score
        )
    
    def calculate_enhanced_effectiveness(
        self, 
        model_name: str,
        scores: List[float],
        costs: List[float], 
        response_times: List[float],
        responses: List[str],
        test_types: List[str]
    ) -> EnhancedEffectivenessScore:
        """Calculate enhanced cost-effectiveness with quality adjustments."""
        
        if not scores or not costs:
            return self._create_invalid_score(model_name, "No data available")
        
        avg_score = np.mean(scores)
        avg_cost = np.mean(costs)
        avg_time = np.mean(response_times) if response_times else 0
        
        warnings = []
        
        # Quality gate: minimum accuracy threshold
        if avg_score < self.min_score_threshold:
            warnings.append(f"Below minimum accuracy threshold ({self.min_score_threshold:.1%})")
        
        # Analyze response quality
        quality_scores = []
        for i, response in enumerate(responses):
            test_type = test_types[i] if i < len(test_types) else "unknown"
            quality = self.analyze_response_quality(response, test_type)
            quality_scores.append(quality)
        
        # Aggregate quality metrics
        avg_word_count = np.mean([q.word_count for q in quality_scores])
        avg_completeness = np.mean([q.completeness_score for q in quality_scores])  
        avg_depth = np.mean([q.depth_score for q in quality_scores])
        
        # Quality gates
        if avg_word_count < self.min_response_length:
            warnings.append(f"Insufficient response detail (avg {avg_word_count:.0f} words)")
            
        if avg_completeness < 0.5:
            warnings.append(f"Incomplete security analysis (completeness: {avg_completeness:.1%})")
        
        # Calculate traditional effectiveness (for comparison)
        raw_effectiveness = avg_score / avg_cost if avg_cost > 0 else 0
        
        # Calculate quality-adjusted effectiveness
        quality_multiplier = (
            (avg_completeness * 0.4) +  # 40% weight on completeness
            (avg_depth * 0.3) +         # 30% weight on technical depth  
            (min(avg_word_count / 200, 1.0) * 0.2) +  # 20% weight on response length
            (0.1)  # 10% baseline
        )
        
        # Penalize low scores exponentially to prevent gaming
        score_penalty = max(0, avg_score - self.min_score_threshold) ** 1.5
        
        # Time penalty for extremely slow responses
        time_penalty = 1.0
        if avg_time > 30:
            time_penalty = 0.7  # 30% penalty for >30s responses
        elif avg_time > 60:
            time_penalty = 0.5  # 50% penalty for >60s responses
            
        quality_adjusted = (score_penalty * quality_multiplier * time_penalty) / avg_cost if avg_cost > 0 else 0
        
        # Calculate practical effectiveness (real-world usability)
        # Accounts for the fact that poor responses require additional rounds
        rounds_needed = 1.0
        if avg_completeness < 0.7:
            rounds_needed = 1.5  # Need additional prompting
        if avg_score < 0.5:
            rounds_needed = 2.0  # Need significant rework
            
        practical_cost = avg_cost * rounds_needed
        practical_effectiveness = (avg_score * quality_multiplier) / practical_cost if practical_cost > 0 else 0
        
        # Determine tier classification
        tier = self._classify_tier(avg_score, quality_adjusted, avg_cost, warnings)
        
        # Create aggregate quality metrics
        agg_quality = ResponseQualityMetrics(
            word_count=int(avg_word_count),
            technical_terms_count=int(np.mean([q.technical_terms_count for q in quality_scores])),
            security_concepts_covered=int(np.mean([q.security_concepts_covered for q in quality_scores])),
            mitigation_strategies_mentioned=int(np.mean([q.mitigation_strategies_mentioned for q in quality_scores])),
            completeness_score=avg_completeness,
            depth_score=avg_depth
        )
        
        return EnhancedEffectivenessScore(
            model_name=model_name,
            raw_effectiveness=raw_effectiveness,
            quality_adjusted=quality_adjusted,
            practical_effectiveness=practical_effectiveness,
            tier=tier,
            quality_metrics=agg_quality,
            warnings=warnings
        )
    
    def _classify_tier(self, avg_score: float, quality_adjusted: float, avg_cost: float, warnings: List[str]) -> str:
        """Classify model into performance tiers."""
        
        if warnings:
            return "problematic"  # Has quality issues
            
        if avg_score >= 0.9 and avg_cost >= 0.01:
            return "enterprise_grade"  # High accuracy, premium cost
        elif quality_adjusted >= 1000 and avg_score >= 0.7:
            return "value_champion"  # Good balance of cost and quality
        elif avg_score >= 0.8:
            return "accuracy_leader"  # High accuracy focus
        elif quality_adjusted >= 500:
            return "practical_choice"  # Decent balance for everyday use
        else:
            return "budget_option"  # Lowest tier
    
    def _create_invalid_score(self, model_name: str, reason: str) -> EnhancedEffectivenessScore:
        """Create a score object for invalid/missing data."""
        return EnhancedEffectivenessScore(
            model_name=model_name,
            raw_effectiveness=0.0,
            quality_adjusted=0.0,
            practical_effectiveness=0.0,
            tier="invalid",
            quality_metrics=ResponseQualityMetrics(0, 0, 0, 0, 0.0, 0.0),
            warnings=[reason]
        )
    
    def generate_tier_recommendations(self, scores: List[EnhancedEffectivenessScore]) -> Dict[str, List[str]]:
        """Generate recommendations by tier."""
        
        tiers = defaultdict(list)
        for score in scores:
            if score.tier != "invalid" and not score.warnings:
                tiers[score.tier].append(score.model_name)
        
        # Sort within each tier by quality-adjusted effectiveness
        for tier in tiers:
            tiers[tier] = sorted(tiers[tier], 
                               key=lambda name: next(s.quality_adjusted for s in scores if s.model_name == name),
                               reverse=True)
        
        recommendations = {
            "high_stakes_security": tiers.get("enterprise_grade", [])[:3],
            "balanced_cicd": tiers.get("practical_choice", [])[:3] + tiers.get("value_champion", [])[:3],
            "cost_conscious": tiers.get("value_champion", [])[:3],
            "accuracy_focused": tiers.get("accuracy_leader", [])[:3],
            "avoid_models": [s.model_name for s in scores if s.warnings]
        }
        
        return recommendations


def create_enhanced_effectiveness_report(scores: List[EnhancedEffectivenessScore]) -> str:
    """Generate a detailed report on enhanced cost-effectiveness analysis."""
    
    report = """# 🛡️ Enhanced Cost-Effectiveness Analysis Report

## Methodology Improvements

This analysis addresses critical flaws in traditional cost-effectiveness metrics:

1. **Quality Adjustment**: Prevents cheap models with poor responses from gaming rankings
2. **Response Completeness**: Analyzes actual security analysis quality, not just scores  
3. **Practical Cost**: Accounts for multiple rounds needed for incomplete responses
4. **Performance Tiers**: Multi-dimensional classification beyond simple cost/performance

---

## Enhanced Model Rankings

"""
    
    # Sort by quality-adjusted effectiveness
    sorted_scores = sorted(scores, key=lambda s: s.quality_adjusted, reverse=True)
    
    report += "| Model | Traditional | Quality-Adjusted | Practical | Tier | Warnings |\n"
    report += "|-------|-------------|------------------|-----------|------|----------|\n"
    
    for score in sorted_scores[:15]:  # Top 15 models
        warnings_str = "; ".join(score.warnings[:2]) if score.warnings else "None"
        if len(warnings_str) > 50:
            warnings_str = warnings_str[:47] + "..."
            
        report += f"| {score.model_name} | {score.raw_effectiveness:.1f} | {score.quality_adjusted:.1f} | {score.practical_effectiveness:.1f} | {score.tier.replace('_', ' ').title()} | {warnings_str} |\n"
    
    return report


# Integration hook for existing codebase
def integrate_enhanced_effectiveness(results, models) -> Dict[str, Any]:
    """Integration function for existing benchmark code."""
    
    analyzer = EnhancedCostEffectivenessAnalyzer()
    enhanced_scores = []
    
    # Group results by model
    model_data = defaultdict(lambda: {"scores": [], "costs": [], "times": [], "responses": [], "test_types": []})
    
    for result in results:
        if hasattr(result, 'model') and hasattr(result, 'score'):
            model_data[result.model]["scores"].append(result.score)
            model_data[result.model]["costs"].append(getattr(result, 'cost_usd', 0.0))
            model_data[result.model]["times"].append(getattr(result, 'elapsed_s', 0.0))
            model_data[result.model]["responses"].append(getattr(result, 'text', ''))
            model_data[result.model]["test_types"].append(getattr(result, 'test_id', 'unknown'))
    
    # Calculate enhanced scores for each model
    for model in models:
        if model in model_data:
            data = model_data[model]
            if data["scores"]:  # Only process if we have data
                enhanced_score = analyzer.calculate_enhanced_effectiveness(
                    model_name=model,
                    scores=data["scores"],
                    costs=data["costs"], 
                    response_times=data["times"],
                    responses=data["responses"],
                    test_types=data["test_types"]
                )
                enhanced_scores.append(enhanced_score)
    
    # Generate recommendations
    recommendations = analyzer.generate_tier_recommendations(enhanced_scores)
    
    return {
        "enhanced_scores": enhanced_scores,
        "recommendations": recommendations,
        "report": create_enhanced_effectiveness_report(enhanced_scores),
        "methodology_notes": [
            "Quality-adjusted scoring prevents gaming by cheap models with poor responses",
            "Practical effectiveness accounts for multiple rounds needed for incomplete analysis", 
            "Response quality metrics evaluate technical depth and completeness",
            "Performance tiers provide multi-dimensional model classification"
        ]
    }