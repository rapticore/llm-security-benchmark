# 🔍 Response Analysis & Manual Validation Guide

## Overview

The `--show-responses` command provides detailed visibility into model responses for manual validation and analysis. This is essential for:

- **Manual validation** of automated scoring
- **Understanding model reasoning** and vulnerability detection logic  
- **Debugging scoring criteria** and test case effectiveness
- **Comparing model performance** across different security scenarios
- **Training and education** on security analysis patterns

## Usage Examples

### Quick Summary View
```bash
# Compact view for overview
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini --show-responses --response-format summary
```

**Output:**
```
📋 sql_injection_simple | 🤖 gpt-4o-mini | 📊 1.000 (100.0%) | ⏱️ 4.08s
   💬 The SQL query provided is vulnerable to SQL injection...
   ✅ 3 met | ❌ 0 missed | ⚠️ 0 violations
```

### Detailed Analysis (Default)
```bash
# Balanced view with key details
python3 run_llm_benchmark.py --suite basic --models claude-sonnet-4 --show-responses --response-format detailed
```

**Output:**
```
================================================================================
📋 TEST: command_injection  
🤖 MODEL: claude-sonnet-4
📊 SCORE: 0.750/1.0 (75.0%)
⏱️  TIME: 2.34s
💰 COST: $0.00023
================================================================================
🎯 TEST PROMPT:
   Analyze this code for security vulnerabilities:
   import subprocess
   def backup_file(filename):...

🔍 MODEL RESPONSE:
   This code has a critical command injection vulnerability...
   [...response truncated - full text saved to reports...]

📈 SCORING BREAKDOWN:
   ✅ CRITERIA MET (3):
      • command\s*injection
      • shell.*true|shell=True  
      • subprocess|shell
   ❌ CRITERIA MISSED (1):
      • sanitize|validate|escape
   ⚠️  MUST NOT VIOLATIONS (0):
================================================================================
```

### Complete Full Analysis  
```bash
# Maximum detail for thorough review
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini,claude-sonnet-4 --show-responses --response-format full
```

**Output:**
```
====================================================================================================
📋 TEST: hardcoded_secrets
🤖 MODEL: gpt-4o-mini  
📊 SCORE: 1.000/1.0 (100.0%)
⏱️  TIME: 3.89s
💰 COST: $0.00017
📥 INPUT TOKENS: 74
📤 OUTPUT TOKENS: 312
====================================================================================================
🎯 FULL TEST PROMPT:
   [Complete test prompt displayed]

🔍 FULL MODEL RESPONSE:
   [Complete untruncated response displayed]

📈 COMPLETE SCORING BREAKDOWN:
   📋 TOTAL CRITERIA: 4
   🔍 ALL EXPECTED CRITERIA:
      1. ✅ hardcoded.*secret|hardcoded.*credential|hardcoded.*password
      2. ✅ environment.*variable|config.*file
      3. ✅ secret.*management|credential.*management
      4. ❌ password.*plain.*text|password.*hardcoded
   🚫 MUST NOT PATTERNS (2):
      • ✅ OK: \bsafe\b
      • ✅ OK: \bno\s+issues\b
====================================================================================================
```

## Response Format Options

| Format | Use Case | Detail Level | Best For |
|--------|----------|--------------|----------|
| **summary** | Quick overview, many models | Compact | Rapid comparison across models |
| **detailed** | Standard analysis | Balanced | Regular manual validation |
| **full** | Deep investigation | Complete | Thorough review, debugging |

## Manual Validation Workflow

### 1. **Run with Summary for Overview**
```bash
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini,claude-sonnet-4 --show-responses --response-format summary
```
- Quickly identify scores and obvious issues
- Spot models with unexpected performance

### 2. **Detailed Analysis for Investigation**
```bash  
python3 run_llm_benchmark.py --suite basic --models claude-sonnet-4 --show-responses --response-format detailed
```
- Review specific test cases with unusual scores
- Understand model reasoning patterns
- Validate scoring accuracy

### 3. **Full Analysis for Deep Dive**
```bash
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini --show-responses --response-format full --timeout 15
```
- Complete audit of specific model responses
- Debug scoring criteria effectiveness
- Document model behavior for reports

## Key Benefits for Manual Validation

### **🎯 Test Prompt Context**
- See exactly what security scenario was presented
- Understand the vulnerability being tested
- Validate test case quality and clarity

### **🔍 Full Model Response**  
- Review complete security analysis from model
- Check for missed vulnerabilities or false positives
- Assess response quality and thoroughness

### **📈 Detailed Scoring Breakdown**
- See which criteria were met/missed
- Identify "must not" violations (dangerous advice)
- Validate automated scoring accuracy

### **💰 Performance Metrics**
- Track response time and cost per test
- Monitor token usage efficiency
- Optimize model selection based on speed/cost

## Common Validation Scenarios

### **High Score Validation** ✅
```bash
# Check if high scores are actually justified
python3 run_llm_benchmark.py --suite basic --models gpt-4o --show-responses --response-format detailed | grep -A 20 "SCORE: [0-9]\.[8-9]"
```

### **Low Score Investigation** ❌
```bash  
# Understand why scores are low
python3 run_llm_benchmark.py --suite comprehensive --models claude-sonnet-4 --show-responses --response-format full | grep -A 30 "SCORE: 0\.[0-3]"
```

### **Must Not Violations** ⚠️
```bash
# Find dangerous advice patterns
python3 run_llm_benchmark.py --suite all --models premium --show-responses --response-format detailed | grep -B 5 -A 10 "VIOLATIONS"
```

### **Model Comparison** 🤖
```bash
# Compare responses for same test
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini,claude-sonnet-4,gemini-2.5-flash --show-responses --response-format detailed
```

## Advanced Usage

### **Performance Monitoring**
```bash
# Track model speed and cost efficiency
python3 run_llm_benchmark.py --suite comprehensive --models fast --show-responses --response-format summary | grep "⏱️\|💰"
```

### **Criteria Effectiveness Analysis**
```bash
# Identify poorly designed test criteria
python3 run_llm_benchmark.py --suite all --models balanced --show-responses --response-format full | grep -B 2 -A 10 "CRITERIA MISSED"
```

### **Educational Review**
```bash  
# Study security analysis patterns
python3 run_llm_benchmark.py --suite owasp --models premium --show-responses --response-format detailed --timeout 20
```

## Tips for Effective Manual Validation

1. **Start with Summary** - Get overview before diving deep
2. **Focus on Edge Cases** - Pay attention to very high/low scores  
3. **Check Must Not Violations** - These indicate dangerous advice
4. **Compare Models** - Run same test with different models
5. **Validate Criteria** - Ensure scoring patterns match expectations
6. **Document Findings** - Keep notes on consistent patterns or issues

## Integration with Reports

All response data is automatically saved to:
- **`raw_responses.json`** - Complete model outputs  
- **`enhanced_analysis_report.md`** - Detailed analysis
- **`executive_summary.md`** - Business-focused summary

Use `--show-responses` for real-time validation, then reference the saved reports for detailed follow-up analysis.

**Built by the Rapticore Security Research Team**