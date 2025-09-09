# 🛡️ LLM Security Benchmark - Installation Guide

**Built by the Rapticore Security Research Team**

## Quick Start

### 1. Install Dependencies

**Option A: Minimal Installation (Recommended)**
```bash
pip install -r requirements-minimal.txt
```

**Option B: Full Installation (All Features)**  
```bash
pip install -r requirements.txt
```

**Option C: System Package Installation**
```bash
pip install --break-system-packages -r requirements-minimal.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project directory:
```bash
# Required API keys (get from respective providers)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  
GEMINI_API_KEY=your_google_ai_key_here

# Optional API keys
XAI_API_KEY=your_x_ai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 3. Verify Installation

```bash
python3 enhanced_multi_llm_benchmark.py --models gpt-4o-mini --suite basic
```

You should see:
```
✅ QFS audit modules loaded - using methodologically consistent analysis
✓ OpenAI client initialized
[... benchmark runs successfully]
🔍 Quality-First Score methodology applied - prioritizing accuracy over cost
```

## Dependencies Explained

### ⚠️ **Required for QFS Audit Compliance:**

| Package | Purpose | Version |
|---------|---------|---------|
| **scipy** | Bootstrap confidence intervals, statistical tests | ≥1.16.0 |
| **pandas** | Data validation, schema enforcement | ≥1.3.0 |
| **numpy** | Geometric mean, cost normalization | ≥1.21.0 |
| **matplotlib** | Quality-first visualizations | ≥3.5.0 |
| **seaborn** | Pareto frontier analysis | ≥0.11.0 |

### 🔧 **Core API Clients:**

| Package | Purpose | Version |
|---------|---------|---------|
| **openai** | GPT-4o, GPT-5 models | ≥1.0.0 |
| **anthropic** | Claude Sonnet, Opus models | ≥0.8.0 |
| **google-generativeai** | Gemini Pro, Flash models | ≥0.3.0 |
| **python-dotenv** | API key management | ≥1.0.0 |

## Troubleshooting

### Common Issues:

**1. Missing scipy:**
```bash
pip install --break-system-packages scipy>=1.16.0
```

**2. Import errors:**
```bash
python3 -c "from qfs_config import CONFIG; print('✅ QFS modules working')"
```

**3. API key issues:**
- Ensure `.env` file is in the same directory as the script
- Check API key format and validity
- Verify account has sufficient credits

**4. Permission errors:**
- Use `--break-system-packages` flag
- Consider using virtual environment
- Check file permissions

### System Requirements:

- **Python:** 3.8+ (3.9+ recommended)
- **OS:** macOS, Linux, Windows
- **Memory:** 4GB RAM minimum, 8GB recommended  
- **Disk:** 1GB free space for test suites and results

## Features Verification

### Test QFS Audit System:
```bash  
python3 -c "
from qfs_config import CONFIG, calculate_qfs
from qfs_analysis import bootstrap_ci
print('✅ QFS audit system operational')
print(f'   Quality thresholds: {CONFIG.COMPLETENESS_THRESHOLD}/{CONFIG.COVERAGE_THRESHOLD}')
print(f'   Bootstrap iterations: {CONFIG.BOOTSTRAP_ITERATIONS}')
print(f'   Sample size minimum: {CONFIG.MIN_SAMPLE_SIZE}')
"
```

### Test Language Coverage:
```bash
python3 -c "
import os
suites = [f for f in os.listdir('test_suites') if f.startswith('security_') and f.endswith('.yaml')]
print(f'✅ Available test suites: {len(suites)}')
for suite in sorted(suites)[:5]:
    print(f'   - {suite}')
if len(suites) > 5:
    print(f'   - ... and {len(suites)-5} more')
"
```

## Advanced Installation

### Virtual Environment (Recommended):
```bash
python3 -m venv llm-security-env
source llm-security-env/bin/activate  # Linux/macOS
# llm-security-env\Scripts\activate   # Windows
pip install -r requirements-minimal.txt
```

### Development Installation:
```bash
git clone <repository>
cd llm-security-benchmark  
pip install -e .  # Editable installation
pip install -r requirements.txt  # Full dependencies
```

### Docker Installation (Optional):
```bash
# Build container with all dependencies
docker build -t llm-security-benchmark .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY llm-security-benchmark
```

## Quality Assurance

The installation includes:
- ✅ **Methodological Consistency:** QFS audit-compliant analysis
- ✅ **Statistical Rigor:** Bootstrap confidence intervals  
- ✅ **Data Validation:** Schema enforcement and quality checks
- ✅ **21 Language Test Suites:** 236+ comprehensive security tests
- ✅ **Quality-First Ranking:** Accuracy prioritized over cost

## Support

For installation issues:
1. Check this guide first
2. Verify Python version: `python3 --version`
3. Test minimal installation: `pip install openai anthropic scipy pandas numpy`
4. Report issues with error messages and system details

---

**🎯 Goal:** A statistically rigorous, methodologically consistent, and decision-ready LLM security analysis system.