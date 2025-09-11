# 🛡️ LLM Security Benchmark

A comprehensive, enterprise-grade security testing framework for evaluating Large Language Models (LLMs) across multiple providers. This benchmark tests how well LLMs identify and respond to various security vulnerabilities in code across different programming languages with statistical rigor and professional reporting.

**Built by the Rapticore Security Research Team**

## 🎯 Framework Mission

This framework is designed to advance the understanding of how Large Language Models can be effectively utilized to improve security outcomes. We provide this as an open testing platform for:

- **Security Researchers**: Evaluate LLM capabilities against diverse security scenarios
- **AI Developers**: Benchmark model performance on security-focused tasks with statistical rigor
- **Security Practitioners**: Understand LLM strengths and limitations for security analysis
- **Enterprise Teams**: Make data-driven decisions on LLM deployment for security use cases
- **Educators**: Teach security concepts using AI-assisted vulnerability detection

We encourage the community to contribute, expand test cases, and explore new use cases for LLMs in cybersecurity applications.

## ⚠️ IMPORTANT DISCLAIMERS

**Educational Purpose Only**: This benchmark is provided solely for educational, research, and testing purposes. 

**No Warranty or Liability**: While we have made every effort to conduct these tests fairly and accurately, we do not take any responsibility for inaccuracies, errors, or any consequences arising from the use of this framework. Results should be independently validated.

**Model Performance Variations**: LLM responses can vary due to model updates, API changes, network conditions, and other factors beyond our control. Results are provided as-is for comparative analysis only.

**Security Advisory**: This tool is for defensive security research only. Do not use for malicious purposes or against systems you do not own or have explicit permission to test.

## ⚡ Performance Optimized

**🚀 Ultra-Fast Benchmarking:**
- **Original Runtime:** ~2 hours → **Optimized Runtime:** ~20-60 seconds  
- **Speed Improvement:** 99%+ faster with concurrent execution
- **Quick validation:** 5 essential security tests in ~10-15 seconds
- **Full analysis:** Complete enhanced reporting maintained

## ⚠️ IMPORTANT COST NOTICE

**This benchmark uses paid API services and WILL incur costs to your accounts:**

- **OpenAI**: GPT-5, GPT-4o, and GPT-4o-mini require OpenAI API credits
- **Anthropic**: Claude Opus 4 and Claude Sonnet 4 require Anthropic API credits  
- **Google**: Gemini models require Google Cloud AI API credits
- **X.AI**: Grok models require X.AI API credits
- **DeepSeek**: DeepSeek models require DeepSeek API credits

**💰 Optimized Cost Structure:**
- **Fast suite (5 tests, 1 model)**: ~$0.01-0.05
- **Basic suite (11 tests, 2 models)**: ~$0.05-0.20  
- **Full benchmark**: $5-50+ depending on models selected

**Cost-saving optimizations:**
- ✅ Default fast models: `gpt-4o-mini`, `claude-sonnet-4`
- ✅ Reduced timeouts: 10s (vs 30s previously)
- ✅ Smaller token limits: 256/384 tokens
- ✅ Concurrent execution: 4x faster with same quality

## 🎯 Overview

This tool evaluates LLMs' ability to:
- ⚡ **Rapidly** identify security vulnerabilities in code snippets
- 🎯 Provide appropriate security recommendations
- 🔍 Recognize common attack patterns and weaknesses
- 📊 Demonstrate security knowledge across OWASP Top 10 and beyond
- 📈 Deliver statistically rigorous performance analysis
- 🏢 Support enterprise decision-making with professional reporting

### 🤖 Supported Models

**🏆 Premium Models (Highest Accuracy):**
- GPT-5 (`gpt-5`) - Advanced reasoning, highest cost
- Claude Opus 4 (`claude-opus-4`) - Top tier analysis  
- **Grok-4 (`grok-4`) - X.AI's flagship model, most intelligent globally**
- Gemini 2.5 Flash (`gemini-2.5-flash`) - Fast premium option

**⚖️ Balanced Models (Speed + Accuracy):**
- GPT-4o (`gpt-4o`) - OpenAI's optimized model
- Claude Sonnet 4 (`claude-sonnet-4`) - **Default choice**
- **Grok-3 (`grok-3`) - X.AI's standard model**
- Gemini 2.0 Flash (`gemini-2.0-flash`) - Google's balanced option

**⚡ Fast Models (Cost-Effective):**
- GPT-4o Mini (`gpt-4o-mini`) - **Default choice** 
- **Grok-3-Mini (`grok-3-mini`) - X.AI's fast variant**
- **Grok-Code-Fast-1 (`grok-code-fast-1`) - X.AI's code-optimized model**
- GPT-5 Mini (`gpt-5-mini`) - Budget OpenAI option
- Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`) - Ultrafast
- Gemini 2.0 Flash Lite (`gemini-2.0-flash-lite`) - Budget Google

**🏠 Local Models (Zero Cost - Advanced Setup Required):**
- **⚠️ Not included in 'all' by default** - use `--models local` or `--models all+local`
- **Requires significant setup**: Ollama installation, model pulling, custom tuning
- **Ollama Models**: Run completely free via local Ollama installation
  - `ollama/llama3.3` - Local Llama 3.3 model
  - `ollama/deepseek-r1` - Local DeepSeek reasoning model  
  - `ollama/qwen2.5` - Local Qwen 2.5 model
  - `ollama/gemma2` - Local Google Gemma 2 model
  - `ollama/mistral` - Local Mistral model

**🧠 Additional Provider Support:**
- **X.AI Grok Models**: Premium reasoning models with real-time search capability
- **DeepSeek Models**: Cost-effective models with excellent coding analysis
- **Meta Llama Models**: Open-source foundation models via API providers  
- **Ollama Integration**: Run any supported model locally without API costs

## 🎯 Enhanced Features (Enabled by Default)

Every benchmark run includes professional-grade analysis with statistical rigor:

### 📊 Rich Data Collection & Analysis
- **Comprehensive raw data capture** for future analysis and audit trails
- **Advanced cost-effectiveness calculations** with quality weighting and penalty adjustments
- **Token usage analysis** and pricing optimization recommendations
- **System performance monitoring** during concurrent execution
- **Statistical confidence intervals** (Wilson CI for proportions, Bootstrap CI for means)
- **Sample size adequacy validation** with warnings for low-confidence results

### 📈 Professional Reporting
- **Enhanced Executive Summary** with use-case profile analysis (RAPID_RESPONSE vs IN_DEPTH)
- **Technical Analysis Report** with engineering-grade metrics and statistical validation
- **Multi-format exports**: CSV, JSON, Markdown, Compressed archives
- **Interactive performance visualization** charts and graphs
- **Language-specific and OWASP category** effectiveness analysis
- **Latency distribution analysis** (P95, P99, throughput, standard deviation)

### 🎯 Advanced Metrics & Statistical Rigor
- **Quality-weighted cost effectiveness** (accuracy, reliability, consistency)
- **Penalty-adjusted scoring** for dangerous recommendations
- **Response quality assessment** (excellent/good/fair/poor/unusable)
- **Business impact quantification** and ROI calculations
- **Use-case profile gates** with decision scoring algorithms
- **Security-aware metrics** (precision/recall/F1 when TP/FP/FN data available)
- **Reproducibility tracking** (model version, region, temperature, seed, max_tokens)

### 🔍 Manual Validation Tools
- **Enhanced response analysis** for manual validation
- **Three display formats**: summary, detailed, full
- **Complete scoring breakdown** with criteria met/missed
- **Real-time quality assessment** during execution

### 🤖 Automatic Model Detection
- **Smart availability checking** - Only tests models with configured API keys
- **Ollama model verification** - Checks if local models are actually pulled
- **Helpful setup guidance** - Shows exactly how to configure missing models
- **No failed runs** - Automatically skips unavailable models with clear explanations

### 💾 Future-Proof Data Capture
- **Complete API request/response logging** for audit trails
- **System environment and performance data** for reproducibility
- **Reproducible results** with full configuration tracking
- **Ready for integration** with BI tools (Tableau, PowerBI)

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Internet connection for API calls
- API keys from supported providers (see step 3)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm-security-benchmark

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies (includes enhanced data analysis & visualization)
pip install -r requirements.txt

# This installs:
# - Core LLM APIs (OpenAI, Anthropic, Google, X.AI, DeepSeek)
# - Data analysis libraries (pandas, numpy, scipy)
# - Visualization tools (matplotlib, seaborn) 
# - System monitoring (psutil)
# - Concurrent execution capabilities
# - All enhanced reporting capabilities
```

### 3. API Key Configuration

#### Step 3.1: Get API Keys

You'll need API keys from the providers you want to test:

**OpenAI API Key (for GPT models):**
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Anthropic API Key (for Claude models):**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create account
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

**Google AI API Key (for Gemini models):**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AI`)

**X.AI API Key (for Grok models):**
1. Visit [X.AI Console](https://console.x.ai/)
2. Sign in or create account
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key

**DeepSeek API Key (for DeepSeek models):**
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign in or create account
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key

#### Step 3.2: Configure Environment

Create `.env` file and add your API keys:
```env
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=sk-your_openai_key_here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-api03-your_anthropic_key_here

# Google AI API Key (for Gemini models)  
GEMINI_API_KEY=AIzaSy-your_google_key_here

# X.AI API Key (for Grok models)
XAI_API_KEY=xai-your_xai_key_here

# DeepSeek API Key (for DeepSeek models)
DEEPSEEK_API_KEY=sk-your_deepseek_key_here
```

### 4. Run Your First Benchmark

#### ⚡ Ultra-Fast Test (10-15 seconds)
```bash
# Minimal viable benchmark - perfect for CI/CD
python3 enhanced_multi_llm_benchmark.py --suite fast --models gpt-4o-mini
```

#### 🚀 Quick Quality Check (20-30 seconds)
```bash
# Two models, essential security tests
python3 enhanced_multi_llm_benchmark.py --suite fast --models gpt-4o-mini,claude-sonnet-4
```

#### ⚖️ Balanced Analysis (45-60 seconds)
```bash
# More comprehensive with basic test suite
python3 enhanced_multi_llm_benchmark.py --suite basic --models gpt-4o-mini,claude-sonnet-4
```

## 📊 Test Suites

### 🎯 Built-in Test Suites

| Suite | Tests | Runtime | Best For |
|-------|-------|---------|----------|
| **fast** | 5 | 10-20s | CI/CD, rapid validation |
| **basic** | 11 | 20-40s | Regular assessments |
| **comprehensive** | 25 | 60-90s | Thorough evaluation |
| **owasp** | 13 | 30-50s | OWASP Top 10 focus |
| **all** | 150+ | 5-15min | Complete analysis |

### 🌐 Language-Specific Suites

- **python**: Python security vulnerabilities (10 tests)
- **javascript**: JavaScript/Node.js security (10 tests)  
- **java**: Java enterprise security (10 tests)
- **go**: Go systems programming security (12 tests)
- **rust**: Rust memory safety and security (10 tests)
- **c/cpp**: C/C++ memory management (10 tests each)
- **csharp**: C# .NET security (10 tests)
- **php**: PHP web security (11 tests)
- **ruby**: Ruby on Rails security (10 tests)
- **haskell**: Functional programming security (10 tests)
- **dart**: Dart/Flutter security (10 tests)
- **kotlin**: Kotlin/Android security (10 tests)
- **scala**: Scala enterprise security (10 tests)
- **swift**: Swift/iOS security (10 tests)
- **typescript**: TypeScript security (10 tests)

### 🎯 Predefined Combinations

- **web_languages**: JavaScript, PHP, Python, Ruby
- **systems_languages**: C, C++, Rust, Go
- **enterprise**: Java, C#, Python
- **memory_safe**: Java, C#, Haskell
- **memory_unsafe**: C, C++

## 🚀 Usage Examples

### ⚡ Performance Optimized Examples

#### Ultra-Fast Development Testing
```bash
# Perfect for development workflow
python3 enhanced_multi_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini \
    --timeout 8 \
    --max-workers 4

# Expected: ~10-15 seconds, ~$0.01-0.02
```

#### Test All X.AI Grok Models (Comprehensive)
```bash
# Test all X.AI models with OWASP security suite
python3 enhanced_multi_llm_benchmark.py \
    --models grok-4,grok-3,grok-3-mini,grok-code-fast-1 \
    --suite owasp \
    --show-responses \
    --response-format detailed \
    --timeout 45 \
    --max-workers 2

# Expected: ~3-6 minutes, ~$0.50-2.00
# Note: Grok-4 is slower (~20s/request) due to advanced reasoning
```

#### Compare New Model Providers
```bash
# Compare X.AI, DeepSeek, and traditional models
python3 enhanced_multi_llm_benchmark.py \
    --models grok-3-mini,deepseek-chat,gpt-4o-mini,claude-sonnet-4 \
    --suite basic \
    --show-responses \
    --response-format summary \
    --timeout 30

# Expected: ~60-90 seconds, ~$0.20-0.50
```

#### Local Models (Advanced Users)
```bash
# Test local models (requires Ollama setup and model pulling)
python3 enhanced_multi_llm_benchmark.py \
    --models local \
    --suite basic \
    --timeout 60 \
    --max-workers 1

# Include both API and local models
python3 enhanced_multi_llm_benchmark.py \
    --models all+local \
    --suite fast \
    --timeout 45

# Note: Local models require significant setup and tuning
```

#### CI/CD Pipeline Integration  
```bash
# Optimized for continuous integration
python3 enhanced_multi_llm_benchmark.py \
    --suite basic \
    --models gpt-4o-mini,claude-sonnet-4 \
    --timeout 10 \
    --concurrent \
    --max-workers 8

# Expected: ~25-40 seconds, ~$0.05-0.15
```

#### Quality Assurance Benchmark
```bash
# Comprehensive but time-efficient
python3 enhanced_multi_llm_benchmark.py \
    --suite comprehensive \
    --models balanced \
    --timeout 12 \
    --max-workers 6

# Expected: ~90-120 seconds, ~$2-8
```

### 🔍 Manual Validation Examples

#### Quick Response Overview
```bash
# Compact summary for rapid validation
python3 enhanced_multi_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini,claude-sonnet-4 \
    --show-responses \
    --response-format summary
```

#### Detailed Analysis
```bash
# Standard manual validation workflow
python3 enhanced_multi_llm_benchmark.py \
    --suite basic \
    --models claude-sonnet-4 \
    --show-responses \
    --response-format detailed
```

#### Deep Investigation
```bash
# Complete response analysis for debugging
python3 enhanced_multi_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini \
    --show-responses \
    --response-format full \
    --timeout 15
```

### 🎯 Advanced Usage

#### Language-Specific Security Testing
```bash
# Test Python security knowledge
python3 enhanced_multi_llm_benchmark.py --suite python --models premium

# Compare web security across models
python3 enhanced_multi_llm_benchmark.py --suite web_languages --models gpt-4o,claude-sonnet-4

# Systems programming security
python3 enhanced_multi_llm_benchmark.py --suite systems_languages --models fast
```

#### Cost Optimization
```bash
# Minimum cost benchmark
python3 enhanced_multi_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini \
    --timeout 5 \
    --max-workers 8

# Balance cost and quality
python3 enhanced_multi_llm_benchmark.py \
    --suite basic \
    --models fast \
    --timeout 8
```

#### Maximum Performance 
```bash
# Fastest possible execution
python3 enhanced_multi_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini \
    --timeout 5 \
    --max-workers 8 \
    --concurrent
```

## 📊 Output & Reports

Every benchmark run generates comprehensive reports with statistical rigor:

### 📁 File Structure
```
benchmark_results/enhanced_YYYYMMDD_HHMMSS/
├── 📋 enhanced_executive_summary.md      # Enhanced business stakeholder report
├── 🔧 technical_analysis_report.md       # Engineering-grade technical analysis
├── 📊 performance_analysis.json          # Machine-readable metrics
├── 📄 detailed_results.csv               # Tabular analysis data
├── 📄 comprehensive_analysis.json        # Complete structured data
├── 📄 model_summary.csv                  # Model performance summary
├── 🎯 Visualization Charts (5+ files):
│   ├── performance_comparison.png        # Model comparison
│   ├── cost_effectiveness.png           # Quality vs cost analysis
│   ├── token_usage.png                  # Resource utilization
│   ├── performance_breakdown.png        # Detailed metrics
│   └── owasp_effectiveness.png          # OWASP category analysis
└── 💾 Raw Data Exports:
    ├── complete_session_data.json       # Full audit trail
    ├── session_data.json.gz            # Compressed archive
    ├── analysis_ready.csv              # Ready for BI tools
    └── session_summary.md              # Human-readable summary
```

### 📈 Enhanced Executive Summary Features

The enhanced executive summary now includes:

#### ⚡ Use-Case Profile Analysis
- **RAPID_RESPONSE Profile**: Time-sensitive operations (PR reviews, rapid vuln checks, AoC triage)
- **IN_DEPTH Profile**: Comprehensive analysis (full codebase, compliance reviews, architecture assessment)
- **Profile-specific gates**: Accuracy, success rate, and P95 latency thresholds
- **Decision scoring**: Weighted algorithms for optimal model selection per use case

#### 📊 Latency Distribution Analysis
- **Complete latency metrics**: Mean, median, P95, P99, standard deviation
- **Throughput analysis**: Theoretical requests per hour
- **Performance profiling**: Detailed response time distribution

#### 📈 Statistical Validation
- **Confidence intervals**: Wilson CI for success rates, Bootstrap CI for accuracy
- **Sample size adequacy**: Warnings for low-confidence results
- **Statistical rigor**: 95% confidence intervals with proper methodology

#### 🛡️ Security-Aware Metrics
- **Precision/Recall/F1**: When TP/FP/FN/TN data is available
- **Severity-weighted scoring**: For security-critical assessments
- **Security-specific analysis**: Tailored for vulnerability detection

#### 🔬 Reproducibility & Configuration
- **Model configuration tracking**: Version, region, temperature, seed, max_tokens
- **Run reproducibility**: Complete configuration capture for audit trails
- **Methodology documentation**: Statistical methods and profile definitions

### 📈 Sample Enhanced Executive Summary Output

```markdown
# 🛡️ Enhanced Security Benchmark Executive Summary

**Suite:** fast | **Models Tested:** 2 | **Total Security Tests:** 5
**Analysis Date:** September 10, 2025 | **Runtime:** 23.4 seconds

## 🎯 Key Security Findings

🏆 **Highest Security Accuracy:** claude-sonnet-4 achieved 85.2% detection rate
💰 **Best Value (Quality-Aware):** gpt-4o-mini delivers 847.3 quality points per dollar  
⚡ **Fastest Response Time:** gpt-4o-mini averages 3.2s per analysis
🎯 **Most Consistent Performance:** claude-sonnet-4 shows 0.12 variance

## ⚡ Use-Case Profile Analysis

### RAPID_RESPONSE Profile (Time-Sensitive Operations)
| Model | Meets Gate | Accuracy | Success | P95 Latency | Decision Score |
|-------|------------|----------|---------|-------------|----------------|
| claude-sonnet-4 | ✅ | 85.2% | 100.0% | 12.3s | 2.45 |
| gpt-4o-mini | ⚠️ | 78.4% | 95.0% | 18.7s | 1.89 |

**RAPID_RESPONSE Recommendations:**
- **Primary Pick:** claude-sonnet-4 (meets all gates)
- **Gate Requirements:** Accuracy ≥75%, Success ≥95%, P95 ≤15s

## 📊 Latency Distribution Analysis

| Model | Mean | Median | P95 | P99 | Std Dev | Throughput/hr |
|-------|------|--------|-----|-----|---------|---------------|
| gpt-4o-mini | 3.2s | 2.8s | 5.1s | 6.2s | 1.1s | 1,125 |
| claude-sonnet-4 | 4.1s | 3.9s | 12.3s | 15.2s | 2.3s | 878 |

## 📈 Statistical Validation

### Confidence Intervals (95%)
| Model | Success Rate CI | Accuracy CI | Sample Size |
|-------|-----------------|-------------|-------------|
| claude-sonnet-4 | 95.0%-100.0% | 80.1%-90.3% | 5 ✅ |
| gpt-4o-mini | 90.0%-100.0% | 72.1%-84.7% | 5 ✅ |
```

### 🔍 Manual Validation Output Examples

#### Summary Format:
```
📋 command_injection | 🤖 gpt-4o-mini | 📊 0.750 (75.0%) | ⏱️ 3.2s
   💬 This code has a shell injection vulnerability due to shell=True...
   ✅ 3 met | ❌ 1 missed | ⚠️ 0 violations

📋 hardcoded_secrets | 🤖 claude-sonnet-4 | 📊 1.000 (100.0%) | ⏱️ 2.1s  
   💬 Critical security issue: hardcoded database password found...
   ✅ 4 met | ❌ 0 missed | ⚠️ 0 violations
```

#### Detailed Format:
```
================================================================================
📋 TEST: sql_injection_simple
🤖 MODEL: claude-sonnet-4
📊 SCORE: 1.000/1.0 (100.0%)
⏱️  TIME: 2.34s
💰 COST: $0.00023
================================================================================
🎯 TEST PROMPT:
   Analyze this code for security issues: SELECT * FROM users WHERE id = 123'

🔍 MODEL RESPONSE:
   This SQL query contains a classic SQL injection vulnerability...
   [...response truncated - full text saved to reports...]

📈 SCORING BREAKDOWN:
   ✅ CRITERIA MET (3):
      • sql\s*injection
      • parameter|prepared
      • sanitize|validation
   ❌ CRITERIA MISSED (0):
   ⚠️  MUST NOT VIOLATIONS (0):
================================================================================
```

## ⚙️ Command Line Options

### 🎯 Core Options
```bash
python3 enhanced_multi_llm_benchmark.py [OPTIONS]

# Model Selection
--models MODEL_LIST          # gpt-4o-mini,claude-sonnet-4 (default)
                             # Options: all (API only), all+local, premium, balanced, fast, local, or specific models

# Test Suite Selection  
--suite SUITE_NAME          # fast (default), basic, comprehensive, owasp, all
                             # Or language: python, javascript, java, etc.

# Performance Optimization
--concurrent                 # Enable concurrent execution (default: True)
--max-workers N             # Concurrent worker threads (default: 4)
--timeout SECONDS           # Per-request timeout (default: 10)

# Response Analysis
--show-responses            # Enable manual validation display  
--response-format FORMAT    # summary, detailed, full (default: detailed)

# Output Control
--outdir DIRECTORY          # Custom output directory
--json                      # Force JSON output mode
--pricing CUSTOM_PRICING    # Override cost calculations
```

### 🚀 Performance Examples
```bash
# Ultra-fast (10s)
--suite fast --models gpt-4o-mini --timeout 5 --max-workers 8

# Balanced (30s)  
--suite basic --models gpt-4o-mini,claude-sonnet-4 --timeout 10

# Comprehensive (90s)
--suite comprehensive --models balanced --timeout 12 --max-workers 6
```

### 🔍 Validation Examples
```bash
# Quick validation overview
--show-responses --response-format summary

# Standard analysis
--show-responses --response-format detailed

# Deep investigation  
--show-responses --response-format full --timeout 15
```

## 🎯 Performance & Optimization

### ⚡ Speed Optimizations Applied

| Optimization | Before | After | Impact |
|--------------|--------|-------|--------|
| **Default timeout** | 30s | 10s | 67% faster |
| **Token limits** | 512/768 | 256/384 | Faster responses |
| **Default models** | 4 premium | 2 fast | 50% fewer calls |
| **Execution mode** | Sequential | Concurrent | 4x parallelism |
| **Test suite** | 11 tests | 5 tests (fast) | 55% fewer tests |

### 📊 Runtime Estimates

| Configuration | Models | Tests | Workers | Timeout | Est. Time |
|---------------|---------|--------|---------|---------|-----------|
| **Ultra-fast** | 1 | 5 | 8 | 5s | 8-12s |
| **Fast** | 2 | 5 | 4 | 10s | 15-25s |
| **Balanced** | 2 | 11 | 4 | 10s | 25-40s |
| **Comprehensive** | 4 | 11 | 4 | 10s | 45-70s |
| **Full suite** | 6 | 25 | 4 | 15s | 3-5 min |

### 💰 Cost Optimization

**Optimized defaults save 90%+ on costs:**
- **Before:** $50-200+ for full benchmarks
- **After:** $0.01-5 for most use cases
- **Fast models:** gpt-4o-mini, claude-sonnet-4
- **Reduced timeouts:** Less waiting, lower costs
- **Concurrent execution:** Same results, dramatically faster

## 🛠️ Advanced Configuration

### 🎯 Custom Test Suites

Create `custom_tests.yaml`:
```yaml
# Custom security test suite
- id: my_security_test
  prompt: |
    Analyze this authentication code:
    
    def login(username, password):
        if username == "admin" and password == "password":
            return True
        return False
  criteria:
    - 'hardcoded.*credential|hardcoded.*password'
    - 'authentication.*weakness'
    - 'password.*security'
  must_not:
    - '\bsafe\b'
    - '\bno\s+issues\b'
  json: false
```

Run with custom suite:
```bash
python3 enhanced_multi_llm_benchmark.py --suite custom_tests.yaml --models fast
```

### 🔧 Environment Variables

```env
# Performance tuning
DEFAULT_TIMEOUT=10
MAX_WORKERS=4
ENABLE_CONCURRENT=true

# Cost controls
USE_FAST_MODELS=true
ENABLE_RETRY=false

# Output preferences
RESPONSE_FORMAT=detailed
ENABLE_CHARTS=true
```

## 🧪 Testing & Validation

### ✅ Functionality Tests
```bash
# Test API connectivity
python3 enhanced_multi_llm_benchmark.py --suite fast --models gpt-4o-mini --timeout 30

# Validate scoring system
python3 enhanced_multi_llm_benchmark.py --suite basic --models gpt-4o-mini --show-responses --response-format detailed

# Performance test
time python3 enhanced_multi_llm_benchmark.py --suite fast --models gpt-4o-mini --max-workers 8
```

### 🔍 Manual Validation Workflow

1. **Quick Overview:** `--show-responses --response-format summary`
2. **Standard Analysis:** `--show-responses --response-format detailed`  
3. **Deep Investigation:** `--show-responses --response-format full`
4. **Multi-model Comparison:** Multiple models with detailed format

## 📋 Requirements

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum, 2GB recommended for large suites
- **Storage**: 100MB for installation, 1GB+ for comprehensive result archives
- **Network**: Stable internet connection for API calls
- **Performance**: Multi-core CPU recommended for concurrent execution

### Python Dependencies

**Core LLM API clients:**
```
openai>=1.0.0                    # GPT models
anthropic>=0.8.0                 # Claude models  
google-generativeai>=0.3.0       # Gemini models
python-dotenv>=1.0.0             # Environment configuration
pyyaml>=6.0.0                    # Test suite parsing
```

**Enhanced analysis & visualization (core features):**
```
pandas>=1.3.0                    # Data analysis
numpy>=1.21.0                    # Numerical computing
scipy>=1.16.0                    # Statistical functions for QFS audit
matplotlib>=3.5.0                # Chart generation
seaborn>=0.11.0                  # Statistical visualization
psutil>=5.8.0                    # System monitoring
```

**Performance & data handling:**
```
requests>=2.31.0                 # HTTP client
pathlib>=1.0.0                   # Path handling
dataclasses>=0.6.0               # Data structures
typing-extensions>=4.0.0         # Type hints
```

## 🤝 Contributing

### Adding New Models

1. **Add model configuration** in `enhanced_multi_llm_benchmark.py`:
```python
# Add to appropriate model category
javaFAST_MODELS.append("new-fast-model")
```

2. **Implement model runner**:
```python
def run_new_model(client, suite_id, model, sys_msg, prompt, timeout, json_mode, pricing):
    # Implementation for new model API
    pass
```

3. **Add pricing information**:
```python
DEFAULT_PRICING["new-model"] = {"in": 0.001, "out": 0.002}
```

### Adding New Test Suites

Create YAML file in `test_suites/`:
```yaml
# test_suites/security_new_language.yaml
- id: new_vuln_test
  prompt: "Test prompt here"
  criteria:
    - 'pattern1'
    - 'pattern2'
  must_not:
    - 'bad_pattern'
  json: false
```

Add to suite definitions:
```python
DEFAULT_SUITE_FILES["new_language"] = "test_suites/security_new_language.yaml"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Issues and Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: See additional guides in the `docs/` directory:
  - [Installation Guide](docs/installation.md)
  - [New Models Guide](docs/guides/new-models.md)
  - [Response Analysis Guide](docs/guides/response-analysis.md)
  - [Speed Optimization Guide](docs/guides/speed-optimization.md)
  - [Raw Data Analysis Guide](docs/guides/raw-data-analysis.md)
  - [Technical Analysis Background](docs/guides/technical_analysis_background.md)

## 🔧 Troubleshooting

### Common Issues

**❌ "No API keys found"**
```bash
# Check .env file exists and has correct keys
ls -la .env
cat .env
```

**❌ "Timeout errors"**
```bash  
# Increase timeout for slow responses
python3 enhanced_multi_llm_benchmark.py --timeout 20

# Or use faster models
python3 enhanced_multi_llm_benchmark.py --models fast
```

**❌ "High API costs"**
```bash
# Use optimized settings
python3 enhanced_multi_llm_benchmark.py --suite fast --models gpt-4o-mini --timeout 8
```

**❌ "Slow execution"**
```bash
# Enable maximum concurrency  
python3 enhanced_multi_llm_benchmark.py --max-workers 8 --concurrent
```

### Performance Tips

1. **Use fast suite** for development and CI/CD
2. **Enable concurrent execution** with `--concurrent`
3. **Optimize timeouts** based on your needs
4. **Choose appropriate models** for speed vs accuracy balance
5. **Monitor costs** with the built-in cost reporting

## 🤝 Contributing & Community

We welcome contributions to expand this framework and explore new applications of LLMs in cybersecurity:

### 🎯 Areas for Contribution

**Test Case Development:**
- Add new vulnerability test cases
- Expand language-specific security scenarios
- Create industry-specific security test suites
- Develop advanced OWASP coverage

**Model Integration:**
- Add support for new LLM providers
- Implement specialized security-focused models
- Create local model optimization guides
- Develop cost-optimization strategies

**Research Applications:**
- Security education and training scenarios
- AI-assisted penetration testing workflows
- Vulnerability disclosure automation
- Security code review acceleration

### 📖 Research & Educational Use

This framework serves multiple educational and research purposes:

- **Academic Research**: Benchmark LLM capabilities in security domains
- **Security Training**: Teach vulnerability identification using AI assistance  
- **Model Evaluation**: Compare security analysis capabilities across providers
- **Framework Development**: Build specialized security-focused AI tools

### 🔗 How to Contribute

1. **Fork the Repository**: Create your own copy for development
2. **Add Test Cases**: Contribute new security scenarios in YAML format
3. **Submit Pull Requests**: Share improvements with the community
4. **Report Issues**: Help us identify bugs and improvement opportunities
5. **Share Results**: Contribute to the knowledge base with your findings

### 🎓 Using LLMs to Improve Security Outcomes

This framework demonstrates practical applications of AI in cybersecurity:

- **Accelerated Vulnerability Discovery**: Rapid identification of security issues
- **Educational Enhancement**: Interactive learning for security concepts
- **Code Review Automation**: AI-assisted security code analysis
- **Threat Modeling**: LLM-powered security architecture review
- **Incident Response**: AI-assisted forensic analysis and documentation

---

**🛡️ Built by the Rapticore Security Research Team**

*Advancing AI-powered security research through comprehensive LLM testing frameworks with statistical rigor and enterprise-grade reporting*

**📧 Contact & Support**: For research collaborations, enterprise applications, or technical support, please reach out through our research channel - contact@rapticore.com.

**🔗 Documentation**: See our comprehensive guides in the `docs/` directory for detailed information on all aspects of the framework.