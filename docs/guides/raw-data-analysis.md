# Raw Data Analysis Guide

## Overview

The Enhanced LLM Security Benchmark now captures comprehensive raw data for in-depth analysis and custom reporting. This guide explains how to access, analyze, and derive insights from the captured data.

**Built by the Rapticore Security Research Team**

## 📊 Data Capture Features

### Comprehensive Data Collection

Every benchmark run now captures:

1. **System Environment**: Hardware specs, OS, Python version, resource usage
2. **Test Case Details**: Full test metadata, prompts, expected outcomes  
3. **API Request/Response**: Complete HTTP transaction data with timing
4. **Token Usage**: Detailed token breakdowns and cost calculations
5. **Response Analysis**: Content analysis, security term extraction, quality metrics
6. **Execution Context**: System load, retry attempts, network latency
7. **Scoring Breakdown**: Multi-level scoring with detailed criteria analysis

### Multiple Export Formats

Each session generates:
- `complete_session_data_[session_id].json` - Complete data in JSON format
- `complete_session_data_[session_id].json.gz` - Compressed version 
- `session_objects_[session_id].pkl` - Python objects for programmatic analysis
- `raw_responses_[session_id].json` - Raw response text for NLP analysis
- `analysis_ready_[session_id].csv` - Spreadsheet-ready data
- `session_summary_[session_id].md` - Human-readable summary

## 🔍 Data Structure

### Core Data Models

```python
@dataclass
class EnhancedTestResult:
    result_id: str                    # Unique identifier
    session_id: str                   # Session identifier
    test_case: TestCaseDetails        # Complete test information
    model_name: str                   # Model tested
    api_request: APIRequestDetails    # Full API transaction
    token_usage: TokenUsageDetails    # Detailed cost breakdown
    response_analysis: ResponseAnalysis # Content analysis results
    execution_duration_ms: float      # Precise timing
    system_load_during_test: Dict     # System performance during test
    # ... and much more
```

### Available Metrics

**Response Quality Metrics:**
- `technical_depth_score`: How technical/detailed is the response
- `actionability_score`: How actionable are the recommendations  
- `completeness_score`: How complete is the analysis
- `security_terms_found`: List of security terms mentioned
- `vulnerability_types_mentioned`: Specific vulnerability types
- `confidence_indicators`: Language showing confidence
- `hedging_language`: Uncertain language patterns

**System Performance Metrics:**
- `network_latency_ms`: API call network latency
- `system_cpu_percent`: CPU usage during test
- `system_memory_percent`: Memory usage during test
- `retry_attempts`: Number of API retries needed

## 📈 Analysis Examples

### 1. Loading Data for Analysis

#### Python Analysis with Pickle
```python
import pickle
import pandas as pd
from pathlib import Path

# Load the complete session data
with open('session_objects_[session_id].pkl', 'rb') as f:
    data = pickle.load(f)
    
results = data['results']
metadata = data['metadata']
environment = data['environment']

# Convert to pandas DataFrame for analysis
df_data = []
for result in results:
    df_data.append({
        'model': result.model_name,
        'test_id': result.test_case.test_id,
        'programming_language': result.test_case.programming_language,
        'owasp_category': result.test_case.owasp_category,
        'score': result.normalized_score,
        'cost': result.token_usage.total_cost_usd,
        'response_length': result.response_analysis.response_length_chars,
        'technical_depth': result.response_analysis.technical_depth_score,
        'actionability': result.response_analysis.actionability_score,
        'security_terms_count': len(result.response_analysis.security_terms_found),
        'execution_time': result.execution_duration_ms,
        'network_latency': result.api_request.network_latency_ms,
        'system_load': result.system_load_during_test.get('cpu_percent', 0)
    })

df = pd.DataFrame(df_data)
```

#### CSV Analysis (Excel/R/Python)
```python
# Load the analysis-ready CSV
df = pd.read_csv('analysis_ready_[session_id].csv')

# Example: Compare model performance by programming language
performance_by_lang = df.groupby(['model_name', 'programming_language']).agg({
    'normalized_score': ['mean', 'std', 'count'],
    'cost_usd': 'sum',
    'technical_depth_score': 'mean',
    'actionability_score': 'mean'
}).round(3)

print(performance_by_lang)
```

#### JSON Analysis for Web Applications
```javascript
// Load raw responses for web-based analysis
fetch('raw_responses_[session_id].json')
  .then(response => response.json())
  .then(data => {
    const responses = data.responses;
    
    // Analyze response patterns
    const modelPerformance = responses.reduce((acc, r) => {
      if (!acc[r.model]) acc[r.model] = [];
      acc[r.model].push({
        score: r.score,
        responseLength: r.response.length,
        hasCode: r.response.includes('```')
      });
      return acc;
    }, {});
    
    console.log(modelPerformance);
  });
```

### 2. Advanced Analysis Examples

#### Response Quality vs Cost Analysis
```python
# Analyze relationship between response quality and cost
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('analysis_ready_[session_id].csv')

# Create quality composite score
df['quality_score'] = (
    df['technical_depth_score'] * 0.3 + 
    df['actionability_score'] * 0.3 + 
    df['normalized_score'] * 0.4
)

# Plot cost vs quality by model
plt.figure(figsize=(12, 8))
sns.scatterplot(data=df, x='cost_usd', y='quality_score', 
                hue='model_name', size='response_length_chars', 
                alpha=0.7)
plt.title('Response Quality vs Cost by Model')
plt.xlabel('Cost (USD)')
plt.ylabel('Quality Score')
plt.show()

# Find best value models
value_score = df.groupby('model_name').apply(
    lambda x: x['quality_score'].mean() / x['cost_usd'].sum() 
    if x['cost_usd'].sum() > 0 else 0
).sort_values(ascending=False)

print("Best value models (quality per dollar):")
print(value_score)
```

#### Security Term Usage Analysis
```python
# Analyze security terminology usage patterns
import json

with open('complete_session_data_[session_id].json', 'r') as f:
    data = json.load(f)

# Extract security terms by model
security_terms_by_model = {}
for result in data['results']:
    model = result['model_name']
    terms = result['response_analysis']['security_terms_found']
    
    if model not in security_terms_by_model:
        security_terms_by_model[model] = []
    security_terms_by_model[model].extend(terms)

# Analyze term frequency
from collections import Counter
for model, terms in security_terms_by_model.items():
    term_freq = Counter(terms)
    print(f"\n{model} - Top Security Terms:")
    for term, count in term_freq.most_common(10):
        print(f"  {term}: {count}")
```

#### Performance Regression Analysis
```python
# Analyze if model performance degrades over time in session
df['test_sequence'] = df.groupby('model_name').cumcount() + 1

# Check for performance trends
from scipy import stats

model_trends = {}
for model in df['model_name'].unique():
    model_data = df[df['model_name'] == model]
    if len(model_data) > 3:  # Need minimum data points
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            model_data['test_sequence'], model_data['normalized_score']
        )
        model_trends[model] = {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend': 'declining' if slope < -0.01 else 'stable' if abs(slope) < 0.01 else 'improving'
        }

print("Performance trends during session:")
for model, trend in model_trends.items():
    print(f"{model}: {trend['trend']} (R²={trend['r_squared']:.3f})")
```

### 3. Custom Reporting Examples

#### Generate Custom Executive Report
```python
def generate_custom_report(session_id):
    """Generate a custom executive report from raw data."""
    
    # Load data
    with open(f'session_objects_{session_id}.pkl', 'rb') as f:
        data = pickle.load(f)
    
    results = data['results']
    
    # Calculate custom metrics
    total_cost = sum(r.token_usage.total_cost_usd for r in results)
    avg_technical_depth = sum(r.response_analysis.technical_depth_score for r in results) / len(results)
    security_coverage = len(set(term for r in results for term in r.response_analysis.security_terms_found))
    
    # Create custom report
    report = f"""
# Custom Analysis Report - Session {session_id}

## Key Findings
- **Total Investment**: ${total_cost:.4f}
- **Average Technical Depth**: {avg_technical_depth:.2f}/1.0
- **Security Concepts Covered**: {security_coverage} unique terms
- **Response Quality Distribution**: 
    - High Quality (>0.8): {sum(1 for r in results if r.normalized_score > 0.8)} tests
    - Medium Quality (0.5-0.8): {sum(1 for r in results if 0.5 <= r.normalized_score <= 0.8)} tests
    - Low Quality (<0.5): {sum(1 for r in results if r.normalized_score < 0.5)} tests

## Actionable Insights
[Your custom analysis here]
    """
    
    with open(f'custom_report_{session_id}.md', 'w') as f:
        f.write(report)

# Usage
generate_custom_report('your_session_id')
```

#### Export Data for R Analysis
```python
# Prepare data for R statistical analysis
import pandas as pd

def prepare_r_export(session_id):
    """Prepare data optimized for R analysis."""
    
    df = pd.read_csv(f'analysis_ready_{session_id}.csv')
    
    # Create additional derived variables for R
    df['cost_per_char'] = df['cost_usd'] / df['response_length_chars']
    df['efficiency_score'] = df['normalized_score'] / df['cost_usd']
    df['response_speed_score'] = 1000 / df['execution_duration_ms']  # Responses per second
    
    # Export for R
    df.to_csv(f'r_analysis_ready_{session_id}.csv', index=False)
    
    # Create R analysis script
    r_script = f"""
# R Analysis Script for Session {session_id}
library(ggplot2)
library(dplyr)

# Load data
data <- read.csv('r_analysis_ready_{session_id}.csv')

# Model comparison
model_summary <- data %>%
  group_by(model_name) %>%
  summarise(
    avg_score = mean(normalized_score),
    avg_cost = mean(cost_usd),
    efficiency = mean(efficiency_score),
    response_speed = mean(response_speed_score)
  )

print(model_summary)

# Statistical tests
model_performance <- aov(normalized_score ~ model_name, data = data)
summary(model_performance)
TukeyHSD(model_performance)
    """
    
    with open(f'analyze_session_{session_id}.R', 'w') as f:
        f.write(r_script)

prepare_r_export('your_session_id')
```

## 📋 Analysis Checklist

### Essential Analyses to Perform

1. **Model Performance Comparison**
   - [ ] Overall accuracy by model
   - [ ] Cost-effectiveness analysis
   - [ ] Response quality metrics
   - [ ] Speed vs accuracy trade-offs

2. **Security Coverage Analysis**
   - [ ] OWASP category coverage by model
   - [ ] Programming language effectiveness
   - [ ] Vulnerability detection rates
   - [ ] Security terminology usage

3. **Quality Assessment**
   - [ ] Technical depth analysis
   - [ ] Actionability scoring
   - [ ] Response completeness
   - [ ] Confidence vs hedging language

4. **Cost Analysis**
   - [ ] Total cost breakdown
   - [ ] Cost per quality point
   - [ ] Token efficiency analysis
   - [ ] ROI calculations

5. **System Performance**
   - [ ] Network latency impact
   - [ ] System load correlation
   - [ ] Retry patterns
   - [ ] Performance degradation over time

## 🛠 Advanced Use Cases

### 1. Custom Scoring Models

```python
def create_custom_scoring_model(results):
    """Create a custom scoring model based on your specific needs."""
    
    weights = {
        'accuracy': 0.4,      # How correct is the response
        'completeness': 0.2,  # How comprehensive
        'actionability': 0.2, # How useful for fixing
        'efficiency': 0.2     # Cost-effectiveness
    }
    
    for result in results:
        custom_score = (
            result.normalized_score * weights['accuracy'] +
            result.response_analysis.completeness_score * weights['completeness'] +
            result.response_analysis.actionability_score * weights['actionability'] +
            (1.0 / result.token_usage.total_cost_usd if result.token_usage.total_cost_usd > 0 else 0) * weights['efficiency']
        )
        
        # Add custom score to result
        result.custom_score = custom_score
    
    return results
```

### 2. Longitudinal Analysis

```python
def compare_sessions(session_ids):
    """Compare multiple benchmark sessions over time."""
    
    session_data = []
    for session_id in session_ids:
        with open(f'session_objects_{session_id}.pkl', 'rb') as f:
            data = pickle.load(f)
            session_data.append(data)
    
    # Compare model performance evolution
    for model in ['gpt-4o', 'claude-sonnet-4', 'gemini-2.0-flash']:
        model_evolution = []
        for session in session_data:
            model_results = [r for r in session['results'] if r.model_name == model]
            if model_results:
                avg_score = sum(r.normalized_score for r in model_results) / len(model_results)
                avg_cost = sum(r.token_usage.total_cost_usd for r in model_results) / len(model_results)
                model_evolution.append({
                    'session_date': session['metadata']['start_time'],
                    'avg_score': avg_score,
                    'avg_cost': avg_cost
                })
        
        print(f"\n{model} Evolution:")
        for point in model_evolution:
            print(f"  {point['session_date'][:10]}: Score={point['avg_score']:.3f}, Cost=${point['avg_cost']:.5f}")
```

### 3. Export for Business Intelligence Tools

```python
def export_for_tableau(session_id):
    """Export data optimized for Tableau or PowerBI."""
    
    df = pd.read_csv(f'analysis_ready_{session_id}.csv')
    
    # Create business-friendly columns
    df['Model_Category'] = df['model_name'].apply(lambda x: 
        'Premium' if x in ['claude-opus-4', 'gpt-5'] else
        'Balanced' if x in ['claude-sonnet-4', 'gpt-4o'] else 'Budget'
    )
    
    df['Test_Category'] = df['programming_language'].fillna('General')
    df['Security_Focus'] = df['owasp_category'].fillna('Other')
    df['Cost_Tier'] = pd.cut(df['cost_usd'], bins=[0, 0.001, 0.01, 1.0], 
                             labels=['Low', 'Medium', 'High'])
    
    # Export for BI tools
    df.to_csv(f'tableau_export_{session_id}.csv', index=False)
    
    # Create data dictionary
    dictionary = """
# Data Dictionary for Tableau Export

- Model_Category: Premium/Balanced/Budget classification
- Test_Category: Programming language or General
- Security_Focus: OWASP category mapping
- Cost_Tier: Low/Medium/High cost classification
- normalized_score: Final test score (0.0-1.0)
- technical_depth_score: How technical the response is (0.0-1.0)
- actionability_score: How actionable the advice is (0.0-1.0)
    """
    
    with open(f'data_dictionary_{session_id}.md', 'w') as f:
        f.write(dictionary)
```

## 📊 Next Steps

With comprehensive raw data capture, you can:

1. **Build Custom Dashboards**: Use the CSV/JSON exports with visualization tools
2. **Perform Statistical Analysis**: Use R or Python for advanced statistics
3. **Create ML Models**: Train models to predict response quality or costs
4. **Monitor Performance**: Track model performance changes over time
5. **Optimize Testing**: Use cost and performance data to optimize test selection

The raw data provides the foundation for unlimited custom analysis and reporting tailored to your specific security evaluation needs.

**Built by the Rapticore Security Research Team**