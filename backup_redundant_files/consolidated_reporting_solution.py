#!/usr/bin/env python3
"""
Consolidated Reporting Solution

Creates a single, comprehensive executive summary that replaces all overlapping reports.
Uses professional language to describe model evaluation without gaming terminology.

Built by the Rapticore Security Research Team
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime


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


class ConsolidatedReportGenerator:
    """
    Generates a single, comprehensive executive summary that consolidates
    all analysis approaches into one authoritative report.
    """
    
    def __init__(self):
        self.accuracy_threshold = 0.80
        self.cost_efficiency_categories = {
            'premium': 'Premium Quality (Focus on Accuracy)',
            'balanced': 'Balanced Performance (Speed + Quality)',
            'economy': 'Cost-Optimized (Budget Conscious)',
            'specialized': 'Specialized Use Cases',
            'insufficient': 'Below Quality Standards'
        }
    
    def generate_consolidated_executive_summary(
        self,
        model_analyses: List[ConsolidatedModelAnalysis],
        total_cost: float,
        test_suite_info: Dict[str, Any],
        output_dir: Path
    ) -> str:
        """Generate single authoritative executive summary."""
        
        # Separate models by quality standards
        qualified_models = [m for m in model_analyses if m.meets_accuracy_threshold]
        below_threshold_models = [m for m in model_analyses if not m.meets_accuracy_threshold]
        
        # Sort qualified models by effectiveness
        qualified_models.sort(key=lambda m: self._calculate_balanced_effectiveness(m), reverse=True)
        
        # Generate report timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M UTC")
        
        # Build comprehensive summary
        summary = self._generate_header_section(model_analyses, total_cost, test_suite_info, timestamp)
        summary += self._generate_executive_findings(qualified_models, below_threshold_models)
        summary += self._generate_strategic_recommendations(qualified_models)
        summary += self._generate_model_evaluation_details(qualified_models, below_threshold_models)
        summary += self._generate_methodology_section()
        summary += self._generate_quality_standards_section()
        
        return summary
    
    def _generate_header_section(
        self, 
        models: List[ConsolidatedModelAnalysis], 
        total_cost: float, 
        test_info: Dict, 
        timestamp: str
    ) -> str:
        """Generate header section with key metrics."""
        
        return f"""# 🛡️ LLM Security Benchmark - Executive Summary

**Assessment Completed:** {timestamp}  
**Models Evaluated:** {len(models)}  
**Security Test Scenarios:** {test_info.get('test_count', 'N/A')}  
**Total Assessment Cost:** ${total_cost:.4f}

---

## 📊 Key Performance Indicators

"""
    
    def _generate_executive_findings(
        self, 
        qualified: List[ConsolidatedModelAnalysis], 
        below_threshold: List[ConsolidatedModelAnalysis]
    ) -> str:
        """Generate executive findings section."""
        
        section = "## 🎯 Executive Findings\n\n"
        
        if qualified:
            # Top performers
            most_accurate = max(qualified, key=lambda m: m.accuracy_score)
            fastest = min(qualified, key=lambda m: m.response_time)
            best_value = max(qualified, key=lambda m: self._calculate_balanced_effectiveness(m))
            
            section += f"""### 🏆 Top Performing Models (Meeting Quality Standards)

**Most Accurate Analysis:** {most_accurate.model_name} ({most_accurate.accuracy_score:.1%} accuracy)
**Fastest Response Time:** {fastest.model_name} ({fastest.response_time:.1f} seconds average)
**Best Overall Value:** {best_value.model_name} (balanced effectiveness score)

### Quality-Approved Model Rankings

| Rank | Model | Accuracy | Speed | Cost/Test | Effectiveness | Category |
|------|-------|----------|-------|-----------|---------------|----------|"""
            
            for i, model in enumerate(qualified[:10], 1):
                effectiveness = self._calculate_balanced_effectiveness(model)
                category = self._get_model_category(model)
                section += f"\n| {i} | **{model.model_name}** | {model.accuracy_score:.1%} | {model.response_time:.1f}s | ${model.cost_per_test:.5f} | {effectiveness:.0f} | {category} |"
        
        else:
            section += "### ⚠️ Quality Standards Assessment\n\nNo models in this evaluation met the 80% minimum accuracy threshold for enterprise security analysis.\n"
        
        # Below threshold models
        if below_threshold:
            section += f"\n\n### 📋 Models Below Quality Standards ({len(below_threshold)} models)\n\n"
            section += "The following models did not meet the minimum 80% accuracy threshold for reliable security analysis:\n\n"
            section += "| Model | Accuracy | Primary Limitation | Recommended Action |\n"
            section += "|-------|----------|-------------------|--------------------|\n"
            
            for model in below_threshold[:8]:  # Limit to top 8
                limitation = self._identify_primary_limitation(model)
                action = self._recommend_action(model)
                section += f"| **{model.model_name}** | {model.accuracy_score:.1%} | {limitation} | {action} |\n"
        
        return section + "\n"
    
    def _generate_strategic_recommendations(self, qualified: List[ConsolidatedModelAnalysis]) -> str:
        """Generate strategic recommendations by use case."""
        
        if not qualified:
            return """## 📋 Strategic Recommendations

### ⚠️ Assessment Results

No models in this evaluation met enterprise security analysis standards. Consider:
- Testing additional premium models (Claude Opus, GPT-5)
- Adjusting evaluation criteria for specific use cases
- Supplementing with manual security review processes

"""
        
        # Categorize models by use case
        enterprise_models = [m for m in qualified if m.accuracy_score >= 0.90 and m.cost_per_test >= 0.005]
        production_models = [m for m in qualified if 0.85 <= m.accuracy_score < 0.90 or (m.accuracy_score >= 0.90 and m.response_time <= 10)]
        automation_models = [m for m in qualified if m.response_time <= 8 and m.accuracy_score >= 0.80]
        budget_models = [m for m in qualified if m.cost_per_test <= 0.001 and m.accuracy_score >= 0.80]
        
        section = """## 📋 Strategic Recommendations

### By Organizational Use Case:

"""
        
        # Enterprise Security Reviews
        if enterprise_models:
            primary = enterprise_models[0]
            section += f"""#### 🏢 **Enterprise Security Reviews** (Comprehensive Analysis)
- **Primary Recommendation:** {primary.model_name}
  - Accuracy: {primary.accuracy_score:.1%} | Speed: {primary.response_time:.1f}s | Cost: ${primary.cost_per_test:.5f}
  - **Best for:** Detailed vulnerability assessments, compliance reviews, critical system analysis
"""
            if len(enterprise_models) > 1:
                alt = enterprise_models[1]
                section += f"- **Alternative Option:** {alt.model_name} (Accuracy: {alt.accuracy_score:.1%})\n"
        else:
            section += "#### 🏢 **Enterprise Security Reviews**\n- No models met enterprise-grade standards in this evaluation\n"
        
        # Production CI/CD
        if production_models:
            primary = production_models[0]
            section += f"""
#### 🚀 **Production CI/CD Integration** (Automated Scanning)
- **Primary Recommendation:** {primary.model_name}
  - Accuracy: {primary.accuracy_score:.1%} | Speed: {primary.response_time:.1f}s | Cost: ${primary.cost_per_test:.5f}
  - **Best for:** Automated security scanning, continuous integration, deployment gates
"""
        
        # Development Automation
        if automation_models:
            primary = min(automation_models, key=lambda m: m.response_time)
            section += f"""
#### ⚡ **Development Automation** (Fast Feedback)
- **Primary Recommendation:** {primary.model_name}
  - Accuracy: {primary.accuracy_score:.1%} | Speed: {primary.response_time:.1f}s | Cost: ${primary.cost_per_test:.5f}
  - **Best for:** IDE integration, rapid code review, developer feedback loops
"""
        
        # Budget-Conscious Teams
        if budget_models:
            primary = max(budget_models, key=lambda m: m.accuracy_score)
            section += f"""
#### 💰 **Cost-Conscious Teams** (Budget Optimization)
- **Primary Recommendation:** {primary.model_name}
  - Accuracy: {primary.accuracy_score:.1%} | Speed: {primary.response_time:.1f}s | Cost: ${primary.cost_per_test:.5f}
  - **Best for:** Startups, educational use, large-scale batch processing
"""
        
        return section + "\n"
    
    def _generate_model_evaluation_details(
        self, 
        qualified: List[ConsolidatedModelAnalysis], 
        below_threshold: List[ConsolidatedModelAnalysis]
    ) -> str:
        """Generate detailed model evaluation section."""
        
        section = """---

## 🔍 Detailed Model Evaluation

### Model Performance Categories

"""
        
        if qualified:
            section += "#### ✅ **Quality-Approved Models**\n\n"
            
            for model in qualified[:8]:
                category = self._get_model_category(model)
                use_cases = " | ".join(model.recommended_use_cases[:3])
                limitations = " | ".join(model.limitations[:2]) if model.limitations else "None identified"
                
                section += f"""**{model.model_name}** ({category})
- **Performance:** {model.accuracy_score:.1%} accuracy, {model.response_time:.1f}s average response
- **Cost Analysis:** ${model.cost_per_test:.5f} per test ({model.total_tests} tests evaluated)
- **Recommended For:** {use_cases}
- **Considerations:** {limitations}

"""
        
        if below_threshold:
            section += "\n#### 📋 **Below Quality Standards**\n\n"
            
            for model in below_threshold[:5]:
                limitation = self._identify_primary_limitation(model)
                notes = " | ".join(model.evaluation_notes[:2]) if model.evaluation_notes else "Requires improvement"
                
                section += f"""**{model.model_name}** (Accuracy: {model.accuracy_score:.1%})
- **Primary Concern:** {limitation}
- **Evaluation Notes:** {notes}
- **Cost per Test:** ${model.cost_per_test:.5f}

"""
        
        return section
    
    def _generate_methodology_section(self) -> str:
        """Generate methodology explanation."""
        
        return """---

## 🔬 Evaluation Methodology

### Quality Standards Framework

Our evaluation applies rigorous quality standards to ensure recommendations are suitable for enterprise security use:

#### **Accuracy Threshold Analysis**
- **Minimum Standard:** 80% accuracy for security vulnerability detection
- **Rationale:** Security analysis requires high precision - false negatives in vulnerability detection can have severe consequences
- **Assessment:** Models below this threshold may miss critical security issues

#### **Balanced Effectiveness Scoring**
```
Effectiveness = (Accuracy^1.2 × Reliability) / (Cost × Response_Time_Factor)
```
- **Accuracy Weight:** Exponential weighting prioritizes security effectiveness
- **Reliability Factor:** Success rate and consistency measurements  
- **Cost Consideration:** Balanced against quality - not the primary factor
- **Speed Factor:** Response time impact on practical usability

#### **Multi-Dimensional Evaluation**
1. **Security Detection Accuracy:** Ability to identify vulnerabilities correctly
2. **Response Quality:** Depth and actionability of security analysis  
3. **Operational Reliability:** Consistency and success rate
4. **Cost Efficiency:** Value delivered per investment dollar
5. **Performance Speed:** Practical usability for different workflows

"""
    
    def _generate_quality_standards_section(self) -> str:
        """Generate quality standards explanation."""
        
        return """### Quality Assurance Framework

#### **Why Quality Thresholds Matter**
Security analysis is a critical business function where accuracy directly impacts:
- **Risk Assessment Accuracy:** Missed vulnerabilities can lead to breaches
- **Resource Allocation:** False positives waste developer time
- **Compliance Requirements:** Regulatory standards demand reliable detection
- **Business Continuity:** Security failures can disrupt operations

#### **Model Evaluation Criteria**
- **Enterprise Grade:** ≥90% accuracy, comprehensive analysis depth
- **Production Ready:** ≥85% accuracy, suitable for automated workflows
- **Development Use:** ≥80% accuracy, appropriate for developer feedback
- **Below Standards:** <80% accuracy, not recommended for security decisions

#### **Cost Efficiency Philosophy**
While cost is important, our methodology prioritizes **security effectiveness first**:
- Quality security analysis prevents breaches that cost far more than model usage
- Marginal cost savings don't justify increased security risk
- Premium models may provide better ROI through superior detection capabilities

---

*This unified report consolidates multiple analysis methodologies to provide comprehensive, actionable guidance for LLM security model selection.*

**Assessment Framework Built by the Rapticore Security Research Team**
"""
    
    def _calculate_balanced_effectiveness(self, model: ConsolidatedModelAnalysis) -> float:
        """Calculate balanced effectiveness score."""
        if model.cost_per_test <= 0:
            return 0.0
        
        # Balanced effectiveness emphasizing accuracy
        accuracy_weight = model.accuracy_score ** 1.2
        reliability_factor = model.reliability_score
        time_factor = 1.0 / (1.0 + model.response_time / 20.0)  # Diminishing returns after 20s
        
        return (accuracy_weight * reliability_factor * time_factor) / model.cost_per_test
    
    def _get_model_category(self, model: ConsolidatedModelAnalysis) -> str:
        """Get model category for display."""
        if model.accuracy_score >= 0.95:
            return "Premium Quality"
        elif model.accuracy_score >= 0.90:
            return "Enterprise Grade"
        elif model.accuracy_score >= 0.85:
            return "Production Ready"
        elif model.accuracy_score >= 0.80:
            return "Development Use"
        else:
            return "Below Standards"
    
    def _identify_primary_limitation(self, model: ConsolidatedModelAnalysis) -> str:
        """Identify primary limitation for below-threshold models."""
        if model.accuracy_score < 0.60:
            return "Low detection accuracy"
        elif model.accuracy_score < 0.70:
            return "Moderate detection gaps"
        elif model.accuracy_score < 0.80:
            return "Inconsistent vulnerability identification"
        else:
            return "Quality threshold not met"
    
    def _recommend_action(self, model: ConsolidatedModelAnalysis) -> str:
        """Recommend action for below-threshold models."""
        if model.accuracy_score < 0.50:
            return "Not suitable for security use"
        elif model.accuracy_score < 0.70:
            return "Consider for non-critical tasks only"
        else:
            return "May be acceptable with manual review"


def clean_up_redundant_reports(output_dir: Path) -> None:
    """Clean up redundant report files and create consolidated summary."""
    
    redundant_files = [
        "executive_summary.md",
        "quality_first_executive_summary.md", 
        "AGGRESSIVE_ANTI_GAMING_ANALYSIS.md",
        "enhanced_cost_effectiveness_report.md",
        "UNIFIED_EXECUTIVE_SUMMARY.md"
    ]
    
    print("🧹 Consolidating redundant reports...")
    
    # Archive redundant files instead of deleting
    archive_dir = output_dir / "archived_reports"
    archive_dir.mkdir(exist_ok=True)
    
    archived_count = 0
    for filename in redundant_files:
        file_path = output_dir / filename
        if file_path.exists():
            archive_path = archive_dir / filename
            file_path.rename(archive_path)
            archived_count += 1
    
    if archived_count > 0:
        print(f"✓ Archived {archived_count} redundant reports to archived_reports/")
        print("✓ Created single COMPREHENSIVE_EXECUTIVE_SUMMARY.md")
        
        # Create archive index
        with open(archive_dir / "README.md", "w") as f:
            f.write("# Archived Reports\n\n")
            f.write("These reports have been consolidated into COMPREHENSIVE_EXECUTIVE_SUMMARY.md\n\n")
            f.write("Archived files:\n")
            for filename in redundant_files:
                if (archive_dir / filename).exists():
                    f.write(f"- {filename}\n")


# Integration function for main benchmark
def generate_comprehensive_executive_summary(
    results_data: Dict[str, Any], 
    output_dir: Path,
    test_suite_info: Dict[str, Any]
) -> str:
    """Generate comprehensive executive summary replacing all other reports."""
    
    generator = ConsolidatedReportGenerator()
    
    # Convert results to consolidated analysis format
    model_analyses = []
    total_cost = 0.0
    
    for model_name, data in results_data.items():
        if isinstance(data, dict) and 'avg_score' in data:
            
            # Determine quality status
            meets_threshold = data['avg_score'] >= 0.80
            
            # Categorize model
            if data['avg_score'] >= 0.95 and data.get('cost_per_test', 0) >= 0.005:
                tier = "Premium Quality"
            elif data['avg_score'] >= 0.90:
                tier = "Enterprise Grade"
            elif data['avg_score'] >= 0.85:
                tier = "Production Ready"
            elif data['avg_score'] >= 0.80:
                tier = "Development Use"
            else:
                tier = "Below Standards"
            
            # Generate evaluation notes
            notes = []
            if data['avg_score'] < 0.80:
                notes.append(f"Accuracy below enterprise threshold ({data['avg_score']:.1%})")
            if data.get('cost_per_test', 0) < 0.0001:
                notes.append("Extremely low-cost model - verify quality expectations")
            if data.get('avg_response_time', 0) > 20:
                notes.append("Slower response time may impact workflow integration")
            
            # Determine recommended use cases
            use_cases = []
            if meets_threshold:
                if data['avg_score'] >= 0.90:
                    use_cases.extend(["Enterprise security reviews", "Compliance audits", "Critical system analysis"])
                elif data['avg_score'] >= 0.85:
                    use_cases.extend(["Production CI/CD", "Automated scanning", "Code review"])
                else:
                    use_cases.extend(["Development feedback", "Educational use", "Non-critical analysis"])
            else:
                use_cases.append("Not recommended for security analysis")
            
            analysis = ConsolidatedModelAnalysis(
                model_name=model_name,
                accuracy_score=data['avg_score'],
                response_time=data.get('avg_response_time', 0),
                cost_per_test=data.get('cost_per_test', 0),
                total_tests=data.get('total_tests', 5),
                success_rate=data.get('success_rate', 1.0),
                meets_accuracy_threshold=meets_threshold,
                cost_efficiency_tier=tier,
                reliability_score=data.get('success_rate', 1.0),
                evaluation_notes=notes,
                recommended_use_cases=use_cases,
                limitations=[]
            )
            
            model_analyses.append(analysis)
            total_cost += data.get('total_cost', 0)
    
    # Generate comprehensive summary
    summary = generator.generate_consolidated_executive_summary(
        model_analyses, total_cost, test_suite_info, output_dir
    )
    
    # Save comprehensive summary
    comprehensive_path = output_dir / "COMPREHENSIVE_EXECUTIVE_SUMMARY.md"
    with open(comprehensive_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # Clean up redundant reports
    clean_up_redundant_reports(output_dir)
    
    print(f"✓ Generated comprehensive executive summary: {comprehensive_path.name}")
    print("💡 This single report replaces all previous executive summaries")
    
    return summary