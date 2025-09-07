# LLM Security Benchmark

A comprehensive security testing framework for evaluating Large Language Models (LLMs) across multiple providers. This benchmark tests how well LLMs identify and respond to various security vulnerabilities in code across different programming languages.

**Built by the Rapticore Security Research Team**

## ⚠️ IMPORTANT COST NOTICE

**This benchmark uses paid API services and WILL incur costs to your accounts:**

- **OpenAI**: GPT-5, GPT-4o, and GPT-4o-mini require OpenAI API credits
- **Anthropic**: Claude Opus 4 and Claude Sonnet 4 require Anthropic API credits  
- **Google**: Gemini models require Google Cloud AI API credits

**Typical costs:**
- **Full benchmark (all models, all tests)**: $50-200+ depending on models selected
- **Premium models** (Claude Opus 4, GPT-5): $0.01-0.10 per test
- **Budget models** (Gemini Flash, GPT-4o-mini): $0.0001-0.001 per test  
- **162 tests × 10 models**: ~$10-100 total cost range

**Cost-saving tips:**
- Start with `--suite basic` (11 tests) to estimate costs
- Use budget models first: `--models "gpt-4o-mini,gemini-2.5-flash-lite"`
- Monitor costs in real-time through the benchmark output

**The benchmark will display total costs at the end of each run.**

## 🎯 Overview

This tool evaluates LLMs' ability to:
- Identify security vulnerabilities in code snippets
- Provide appropriate security recommendations
- Recognize common attack patterns and weaknesses
- Demonstrate security knowledge across OWASP Top 10 and beyond

### Supported Models

**Premium Models (Highest Accuracy):**
- GPT-5 (`gpt-5`)
- Claude Opus 4 (`claude-opus-4`)
- Gemini 2.5 Flash (`gemini-2.5-flash`)

**Balanced Models (Speed + Accuracy):**
- GPT-4o (`gpt-4o`)
- Claude Sonnet 4 (`claude-sonnet-4`)
- Gemini 2.0 Flash (`gemini-2.0-flash`)

**Fast Models (Cost-Effective):**
- GPT-5 Mini (`gpt-5-mini`)
- GPT-4o Mini (`gpt-4o-mini`)
- Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`)
- Gemini 2.0 Flash Lite (`gemini-2.0-flash-lite`)

### 🎯 Enhanced Features (Enabled by Default)

Every benchmark run now includes:

**📊 Rich Data Collection & Analysis:**
- Comprehensive raw data capture for future analysis
- Advanced cost-effectiveness calculations with partial correctness
- Token usage analysis and pricing optimization recommendations
- System performance monitoring during tests

**📈 Professional Reporting:**
- Executive summary reports for business stakeholders
- Multi-format exports: CSV, JSON, Markdown, Compressed archives
- Performance visualization charts and graphs
- Language-specific and OWASP category effectiveness analysis

**🎯 Advanced Metrics:**
- Quality-weighted cost effectiveness (not just pass/fail)
- Penalty-adjusted scoring for wrong answers
- Response quality assessment (excellent/good/fair/poor)
- Business impact quantification and ROI calculations

**💾 Future-Proof Data Capture:**
- Complete API request/response logging
- System environment and performance data
- Reproducible results with full audit trail
- Ready for integration with BI tools (Tableau, PowerBI)

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
# - Core LLM APIs (OpenAI, Anthropic, Google)
# - Data analysis libraries (pandas, numpy)
# - Visualization tools (matplotlib, seaborn) 
# - System monitoring (psutil)
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

#### Step 3.2: Configure Environment

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:
```env
# OpenAI API Key (for GPT models: gpt-5, gpt-5-mini, gpt-4o, gpt-4o-mini)
OPENAI_API_KEY=sk-your_openai_key_here

# Anthropic API Key (for Claude models: claude-opus-4, claude-sonnet-4)  
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Google AI API Key (for Gemini models: gemini-2.5-flash, gemini-2.0-flash, etc.)
GEMINI_API_KEY=AIyour_gemini_key_here
```

**Note:** You only need keys for the providers/models you want to test. The system will automatically detect available keys and skip unavailable providers.

### 4. Run Basic Benchmark

⚠️ **Start small to estimate costs before running full benchmarks**

```bash
# RECOMMENDED: Start with basic suite to estimate costs (~$0.01-1.00)
python enhanced_multi_llm_benchmark.py --suite basic

# Test budget models first (~$0.05-2.00)
python enhanced_multi_llm_benchmark.py --models "gpt-4o-mini,gemini-2.5-flash-lite" --suite basic

# Test single premium model (~$2.00-10.00)  
python enhanced_multi_llm_benchmark.py --models "claude-sonnet-4" --suite comprehensive

# EXPENSIVE: Full comprehensive benchmark (~$50-200+)
python enhanced_multi_llm_benchmark.py --models all --suite all
```

**Cost estimation by suite:**
- `basic` (11 tests): $0.01 - $1.00 per model
- `comprehensive` (~50 tests): $0.50 - $15.00 per model
- `all` (162 tests): $1.50 - $50.00+ per model

## 📊 Features

### Core Functionality
- **Multi-Provider Support**: Test across OpenAI, Anthropic, and Google models
- **Comprehensive Test Suites**: 14+ language-specific security test collections
- **Flexible Scoring**: Pattern-matching based evaluation with positive/negative criteria
- **Always-On Reporting**: Executive summaries and performance analysis generated automatically
- **Suite Combinations**: Test individual languages or combined suites (enterprise, web_dev, systems)

### Advanced Features  
- **Complete Coverage**: `--suite all` runs 100+ tests across all categories
- **Cost Tracking**: Monitor API usage costs across providers
- **Quality Assessment**: Evaluate response depth and accuracy
- **Comparative Analysis**: Side-by-side model performance comparison
- **JSON Export**: Structured data output for further analysis
- **Timeout Management**: Configurable request timeouts per provider

## 🗂️ Test Suites

### Available Test Suites

| Suite | File | Focus Area | Tests |
|-------|------|------------|-------|
| **Basic Security** | `security_basic.yaml` | Core vulnerabilities | 10 tests |
| **OWASP Top 10** | `owasp_top10.yaml` | OWASP 2021 standards | 13 tests |
| **Comprehensive** | `security_comprehensive.yaml` | Wide coverage | 25+ tests |
| **JavaScript/Node.js** | `security_javascript.yaml` | Frontend/backend JS | 10 tests |
| **Python** | `security_python.yaml` | Python-specific issues | 10 tests |
| **Go** | `security_go.yaml` | Go language security | 12 tests |
| **Rust** | `security_rust.yaml` | Memory safety, crypto | TBD |
| **Java** | `security_java.yaml` | Enterprise patterns | TBD |
| **C/C++** | `security_c_cpp.yaml` | Memory management | TBD |
| **Ruby** | `security_ruby.yaml` | Rails vulnerabilities | TBD |
| **PHP** | `security_php.yaml` | Web application issues | TBD |
| **Haskell** | `security_haskell.yaml` | Functional programming | TBD |

### Vulnerability Categories Covered

- **Injection Attacks**: SQL, NoSQL, Command, LDAP, XPath
- **Authentication**: Weak passwords, session management, MFA bypass
- **Authorization**: Access control, privilege escalation, IDOR
- **Cryptography**: Weak algorithms, poor key management, insecure storage
- **Input Validation**: XSS, path traversal, deserialization
- **Configuration**: Security misconfigurations, default credentials
- **Dependencies**: Vulnerable components, supply chain attacks
- **Monitoring**: Logging failures, incident response gaps
- **Language-Specific**: Memory safety, concurrency, type safety

## 💻 Usage Examples

### Basic Testing
```bash
# Test all models on all test suites (comprehensive benchmark)
python enhanced_multi_llm_benchmark.py --models all --suite all

# Test premium models on all available tests
python enhanced_multi_llm_benchmark.py --models premium --suite all

# Test balanced models on OWASP Top 10
python enhanced_multi_llm_benchmark.py --models balanced --suite owasp

# Test fast/budget models on basic security tests  
python enhanced_multi_llm_benchmark.py --models fast --suite basic

# Test specific models on Python security tests
python enhanced_multi_llm_benchmark.py --models "gpt-4o,claude-sonnet-4" --suite python --timeout 60
```

### 📊 Enhanced Analysis & Reporting (Enabled By Default)

The benchmark now includes comprehensive data collection and visualization as core features:
```bash
# Complete benchmark with JSON export
python enhanced_multi_llm_benchmark.py --models all --suite all --output comprehensive_results.json

# Compare premium models across all language-specific tests
python enhanced_multi_llm_benchmark.py --models premium --suite all_languages --output premium_analysis.json

# Enterprise security assessment
python enhanced_multi_llm_benchmark.py --models balanced --suite enterprise --output enterprise_results.json

# Web development security comparison
python enhanced_multi_llm_benchmark.py --models all --suite web_dev --output web_security_results.json
```

### 📈 Example Enhanced Output

Every run now generates comprehensive analysis automatically:

```
🔍 Enhanced Multi-LLM Security Benchmark
Built by the Rapticore Security Research Team
================================================================================
Models: gpt-4o, claude-sonnet-4, gemini-2.0-flash
Suite: comprehensive (47 test cases)
Output: ./benchmark_results/enhanced_20240101_123456

🎯 Feature Status:
   ✓ Executive reporting: Always enabled
   ✓ Performance analysis: Always enabled
   ✓ Visualization charts: Enabled
   📊 Enhanced data capture: ENABLED
   📈 Enhanced reporting: ENABLED

... [benchmark execution] ...

📊 Generated Reports & Analysis:
   📋 Executive summary: ./benchmark_results/executive_summary.md
   📈 Performance analysis: ./benchmark_results/performance_analysis.json
   🎯 Visualization charts: 6 files
      - performance_comparison.png
      - cost_effectiveness.png
      - language_effectiveness.png
      - owasp_effectiveness.png
   💾 Raw data exports: Multiple formats for advanced analysis
   📊 Enhanced CSV/JSON reports with cost-effectiveness analysis
   📈 Language and OWASP category breakdowns

🎉 Comprehensive benchmark complete!
📁 All results saved to: ./benchmark_results/enhanced_20240101_123456
💡 For advanced analysis, see the raw data exports and CSV files
```

### Suite Categories
```bash
# Test all available suites (most comprehensive)
python enhanced_multi_llm_benchmark.py --models premium --suite all

# Language-specific testing
python enhanced_multi_llm_benchmark.py --models all --suite python      # Python security tests
python enhanced_multi_llm_benchmark.py --models all --suite javascript  # JavaScript/Node.js tests  
python enhanced_multi_llm_benchmark.py --models all --suite go          # Go language tests
python enhanced_multi_llm_benchmark.py --models all --suite rust        # Rust security tests

# Specialized test combinations
python enhanced_multi_llm_benchmark.py --models all --suite systems     # C/C++/Rust/Go
python enhanced_multi_llm_benchmark.py --models all --suite web_dev     # Web development stack
python enhanced_multi_llm_benchmark.py --models all --suite enterprise  # Enterprise languages
```

## 💰 Cost Monitoring

The benchmark provides comprehensive cost tracking:

### Real-Time Cost Display
```
💰 TOTAL COST THIS RUN: $12.4567
📊 Total Tests Executed: 162
📈 Average Cost per Test: $0.076879
⚠️  NOTE: This benchmark uses paid API services
```

### Cost Breakdown by Model  
```
Model                Tests    Success   Avg Score  Time(s)  Total Cost   
--------------------------------------------------------------------------------------------------------------
claude-opus-4        162/162 100.0%     0.641     10.22 $  6.5861      
gpt-5               162/162  100.0%     0.577      8.49 $  1.2192
gpt-4o-mini         162/162  100.0%     0.592      8.40 $  0.0525
```

### Quality-Aware Cost-Effectiveness Analysis  

Our cost-effectiveness calculation prioritizes **accuracy and usability** over raw speed/cost:

```
💰 Best Value (Quality-Aware): claude-sonnet-4 (245.3 quality-weighted points per dollar)
🏆 Best Accuracy: claude-opus-4 (64.1% average score, $6.59 total cost)  
⚡ Fastest: gemini-2.5-flash (0.78s average, $0.0002 total cost)
```

**How Quality-Aware Cost-Effectiveness Works:**
- **Quality Multiplier**: Models scoring <40% are heavily penalized (nearly worthless for security)
- **Reliability Multiplier**: Failed API calls waste money and provide no value  
- **Consistency Multiplier**: Unpredictable results reduce practical utility
- **Result**: Cheap but inaccurate models are correctly identified as poor value

This prevents the common mistake of choosing models that are cheap but produce unusable security analysis.

## 📈 Output and Reporting

### Console Output
- Real-time progress indicators
- Individual test results with scoring
- Summary statistics (pass rate, average score)
- Cost analysis and recommendations
- Executive insights (always generated)

### JSON Export
```json
{
  "model": "claude-opus-4",
  "suite": "owasp_top10",
  "summary": {
    "total_tests": 13,
    "passed": 11,
    "failed": 2,
    "pass_rate": 84.6,
    "average_score": 0.846,
    "total_cost": 0.0234
  },
  "detailed_results": [...],
  "performance_metrics": {...},
  "executive_summary": {...}
}
```

### Executive Summary Features
- **Strategic Recommendations**: Model selection guidance
- **Enhanced Cost-Effectiveness Analysis**: Multiple calculation methods considering partial correctness
- **Security Coverage Assessment**: Vulnerability detection rates by language and OWASP category
- **Business Impact Metrics**: Risk reduction quantification
- **Quality Distribution Analysis**: Perfect, excellent, good, fair, and poor score breakdown

#### Enhanced Cost-Effectiveness Calculations
The benchmark now provides **three cost-effectiveness metrics**:

```
1. Traditional Effectiveness = average_score ÷ cost_per_test
2. Quality-Weighted Effectiveness = weighted_average_score ÷ cost_per_test  
3. Penalty-Adjusted Effectiveness = (positive_scores - penalties) ÷ total_cost
```

**Quality Weighting:**
- Perfect (1.0): Weight = 1.0
- Excellent (0.8-0.99): Weight = 0.9
- Good (0.6-0.79): Weight = 0.7  
- Fair (0.4-0.59): Weight = 0.5
- Poor (0.0-0.39): Weight = 0.2

**Penalties Applied:**
- Failed tests: -0.5 points each
- Poor performance: -0.3 points each

This provides a more accurate assessment of cost-effectiveness that considers:
- **Partial correctness** vs treating all scores equally
- **Quality levels** of responses  
- **Penalties for wrong/missed answers**
- **Cost per perfect answer** vs cost per attempt

## ⚙️ Configuration

### Environment Variables
```env
# Required API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...

# Optional Configuration
DEFAULT_TIMEOUT=30
LOG_LEVEL=INFO
```

### Command Line Options
```
--models SELECTION     Model selection: 'all', 'premium', 'balanced', 'fast', or comma-separated names
--suite SELECTION      Suite selection: 'all', 'basic', 'comprehensive', 'owasp', language names, or file path
--timeout SECONDS      Request timeout (default: 30)
--output FILE          JSON output file path (optional)
--show-responses       Show full response text in console
--json                 Enforce JSON-only outputs in prompts
--verbose             Enable verbose logging
```

### Selection Options

**Model Categories:**
- **`all`**: Test all 9 supported models across all tiers
- **`premium`**: Test highest accuracy models (GPT-5, Claude Opus 4, Gemini 2.5 Flash)
- **`balanced`**: Test speed+accuracy models (GPT-4o, Claude Sonnet 4, Gemini 2.0 Flash)
- **`fast`**: Test cost-effective models (GPT-5-mini, GPT-4o-mini, Gemini Flash Lite variants)
- **Custom**: Comma-separated list of specific model names

**Test Suite Categories:**
- **`all`**: Run all available test suites (most comprehensive, 100+ tests)
- **`basic`**: Core security vulnerability tests
- **`comprehensive`**: Extended security test coverage
- **`owasp`**: OWASP Top 10 2021 focused tests
- **`all_languages`**: All language-specific security tests
- **`enterprise`**: Enterprise-focused tests (Java, C#, Python)
- **`web_dev`**: Web development security (JS, Python, PHP, Java)
- **`systems`**: Systems programming security (C, C++, Rust, Go)
- **Language-specific**: `python`, `javascript`, `go`, `rust`, `java`, `c`, `cpp`, `csharp`, `php`, `ruby`, `haskell`

**Model Categories:**
- **`all`**: Test all 9 supported models across all tiers
- **`premium`**: Test highest accuracy models (GPT-5, Claude Opus 4, Gemini 2.5 Flash)
- **`balanced`**: Test speed+accuracy models (GPT-4o, Claude Sonnet 4, Gemini 2.0 Flash)
- **`fast`**: Test cost-effective models (GPT-5-mini, GPT-4o-mini, Gemini Flash Lite variants)

## 🏗️ Architecture

### Core Components
- **`enhanced_multi_llm_benchmark.py`**: Main benchmark engine
- **`run_benchmark.py`**: Legacy single-model runner
- **`test_suites/`**: YAML-based test definitions
- **`.env`**: API key configuration

### Test Structure
Each test includes:
- **ID**: Unique identifier
- **Prompt**: Code snippet or security scenario
- **Criteria**: Positive regex patterns (what should be mentioned)
- **Must_not**: Negative patterns (what should be avoided)
- **JSON**: Whether to expect structured output

### Scoring Algorithm
1. **Pattern Matching**: Regex evaluation against response
2. **Positive Criteria**: Points for security awareness
3. **Negative Criteria**: Deductions for unsafe recommendations
4. **Quality Assessment**: Response depth and accuracy evaluation

## 🧪 Testing and Validation

### Running Tests
```bash
# Basic functionality test
python enhanced_multi_llm_benchmark.py --models fast --suite basic

# Comprehensive validation  
python enhanced_multi_llm_benchmark.py --models premium --suite comprehensive --output validation_results.json
```

### Creating Custom Test Suites
```yaml
# example_test.yaml
- id: custom_sql_injection
  prompt: |
    Review this database query:
    
    def get_user(user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return db.execute(query)
  criteria:
    - 'sql.*injection|sqli'
    - 'parameterized.*query|prepared.*statement'
    - 'sanitize|validate'
  must_not:
    - '\bsafe\b'
  json: false
```

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Internet connection for API calls
- 100MB+ available disk space
- API keys from desired LLM providers

### Python Dependencies
All dependencies are listed in `requirements.txt`:
```txt
# Core LLM API clients
openai>=1.0.0
anthropic>=0.8.0
google-generativeai>=0.3.0

# Configuration and data handling
python-dotenv>=1.0.0
pyyaml>=6.0.0

# Additional utilities
requests>=2.31.0
pathlib>=1.0.0
dataclasses>=0.6.0
typing-extensions>=4.0.0
```

Install with: `pip install -r requirements.txt`

## 🤝 Contributing

### Adding New Test Suites
1. Create YAML file in `test_suites/` directory
2. Follow existing format with id, prompt, criteria, must_not, json fields
3. Test with multiple models to validate scoring
4. Update this README with new suite information

### Adding New Models
1. Add model configuration to pricing dictionary
2. Implement model-specific API call handling
3. Update supported models list in README
4. Test with existing test suites

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings for new functions
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues and Support

For bug reports, feature requests, or questions:
1. Check existing issues in the repository
2. Create detailed issue reports with reproduction steps
3. Include model version, test suite, and error messages

## 🔧 Troubleshooting

### Common Issues

**API Key Errors**
```
Error: Invalid API key
Solution: Check .env file and verify key format
```

**Timeout Issues**
```
Error: Request timeout
Solution: Increase timeout with --timeout 60
```

**YAML Parsing Errors**
```
Error: could not find expected ':'
Solution: Validate YAML syntax in test suite files
```

**Missing Dependencies**
```
Error: No module named 'openai'
Solution: pip install -r requirements.txt

Error: No module named 'yaml'  
Solution: pip install pyyaml
```

### Performance Tips
- Use faster models (mini/flash versions) for quick testing
- Enable performance analysis for detailed optimization
- Batch similar tests together for efficiency
- Monitor API rate limits and costs

---

**Built with ❤️ by the Rapticore Security Research Team for security research and LLM evaluation**