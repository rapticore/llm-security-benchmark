# 🧪 LLM Security Benchmark Test Suites

**Built by the Rapticore Security Research Team**

## 📋 Overview

The LLM Security Benchmark includes a comprehensive collection of **226 security test cases** across **21 test suite files**, designed to evaluate Large Language Models' ability to identify security vulnerabilities, provide appropriate recommendations, and demonstrate security knowledge alignment with industry standards.

## 🎯 Test Suite Categories

### **Core Security Suites**

| Suite Name | Tests | Purpose | Use Case |
|------------|-------|---------|-----------|
| **basic** | 11 | Core security fundamentals | Quick evaluation, CI/CD |
| **fast** | 5 | Rapid security screening | Performance testing |
| **comprehensive** | 25 | Extended OWASP Top 10 coverage | Complete assessment |
| **owasp** | 13 | OWASP Top 10 2021 focused | Compliance verification |

### **Language-Specific Suites**

| Programming Language | Tests | File | Specialized Focus |
|---------------------|-------|------|-------------------|
| **Python** | 16 | security_python_comprehensive.yaml | pickle, eval, django/flask |
| **JavaScript** | 10 | security_javascript.yaml | XSS, prototype pollution |
| **TypeScript** | 12 | security_typescript.yaml | Type safety, node.js |
| **Java** | 10 | security_java.yaml | Deserialization, Spring |
| **C/C++** | 10/10 | security_c.yaml, security_cpp.yaml | Memory safety, buffer overflows |
| **Go** | 12 | security_go.yaml | Goroutine safety, race conditions |
| **Rust** | 10 | security_rust.yaml | Memory safety, unsafe blocks |
| **C#/.NET** | 10 | security_csharp.yaml | .NET framework vulnerabilities |
| **PHP** | 11 | security_php.yaml | Web vulnerabilities |
| **Ruby** | 10 | security_ruby.yaml | Rails security patterns |
| **Swift** | 8 | security_swift.yaml | iOS/macOS security |
| **Kotlin** | 11 | security_kotlin.yaml | Android security |
| **Scala** | 6 | security_scala.yaml | JVM security patterns |
| **Dart** | 6 | security_dart.yaml | Flutter security |
| **Haskell** | 10 | security_haskell.yaml | Functional security patterns |

## 🔍 Security Coverage Matrix

### **OWASP Top 10 2021 Mapping**

| OWASP Category | Test Coverage | Key Focus Areas |
|----------------|---------------|-----------------|
| **A01: Broken Access Control** | 15+ tests | RBAC, privilege escalation, IDOR |
| **A02: Cryptographic Failures** | 12+ tests | Weak encryption, key management |
| **A03: Injection** | 45+ tests | SQL, NoSQL, Command, Code injection |
| **A04: Insecure Design** | 8+ tests | Threat modeling, secure patterns |
| **A05: Security Misconfiguration** | 10+ tests | Default configs, unnecessary features |
| **A06: Vulnerable Components** | 6+ tests | Dependency vulnerabilities |
| **A07: ID & Authentication Failures** | 18+ tests | Session management, passwords |
| **A08: Software Data Integrity** | 8+ tests | Unsigned updates, insecure CI/CD |
| **A09: Security Logging/Monitoring** | 5+ tests | Insufficient logging |
| **A10: Server-Side Request Forgery** | 12+ tests | SSRF, URL validation |

### **Vulnerability Categories Covered**

**Injection Attacks (45+ tests):**
- SQL Injection (simple, complex, blind)
- NoSQL Injection (MongoDB, etc.)
- Command Injection (OS commands, shell)
- Code Injection (eval, exec, template)
- LDAP Injection
- XPath Injection

**Web Application Security (38+ tests):**
- Cross-Site Scripting (reflected, stored, DOM)
- Cross-Site Request Forgery (CSRF)
- Clickjacking
- CORS misconfigurations
- Content Security Policy bypasses

**Authentication & Authorization (25+ tests):**
- Weak password policies
- Session fixation/hijacking
- JWT vulnerabilities
- OAuth misconfigurations
- Privilege escalation

**Data Protection (20+ tests):**
- Insecure deserialization
- Sensitive data exposure
- Hardcoded credentials
- Weak cryptography
- PII handling

**Infrastructure Security (18+ tests):**
- Server-Side Request Forgery (SSRF)
- Local File Inclusion (LFI)
- Remote File Inclusion (RFI)
- Directory traversal
- XML External Entity (XXE)

## 🛠️ Test Structure & Format

### **YAML Test Case Format**

```yaml
- id: unique_test_identifier
  prompt: |
    Multi-line description of vulnerable code or scenario
    to be analyzed by the LLM
  criteria:
    - 'regex_pattern_1|alternative_pattern'
    - 'required_security_term'
    - 'vulnerability_identification_pattern'
  must_not:
    - 'incorrect_response_pattern'
    - 'false_positive_indicator'
  json: false  # or true for JSON response format
```

### **Scoring Mechanism**

**Criteria-Based Scoring:**
- **Positive Criteria**: Regex patterns that should be present in responses
- **Negative Patterns** (`must_not`): Patterns indicating poor/dangerous advice
- **Score Calculation**: `(criteria_met - violations*0.5) / total_criteria`
- **Range**: 0.0 - 1.0 (higher is better)

### **Example Test Case**

```yaml
- id: sql_injection_complex
  prompt: |
    Analyze this Python Flask code for vulnerabilities:
    
    @app.route('/search')
    def search():
        query = request.args.get('q')
        sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
        results = db.execute(sql).fetchall()
        return jsonify(results)
  criteria:
    - 'sql\s*injection'
    - 'parameterized|prepared\s*statement'
    - 'f-string|string\s*formatting'
    - 'escape|sanitize|validate'
  must_not:
    - '\bsafe\b'
    - '\bno\s+vulnerabilities\b'
  json: false
```

## 🚀 Running Test Suites

### **Command Line Usage**

```bash
# Run basic security suite
python run_llm_benchmark.py --suite basic

# Run language-specific suite
python run_llm_benchmark.py --suite python

# Run comprehensive assessment
python run_llm_benchmark.py --suite comprehensive

# Run OWASP Top 10 evaluation
python run_llm_benchmark.py --suite owasp

# Run custom suite file
python run_llm_benchmark.py --suite test_suites/security_custom.yaml

# Multiple models with specific suite
python run_llm_benchmark.py --models gpt-4o,claude-sonnet-4 --suite comprehensive
```

### **Predefined Suite Aliases**

The benchmark supports convenient aliases for common test configurations:

```python
DEFAULT_SUITE_FILES = {
    "basic": "test_suites/security_basic.yaml",           # 11 tests
    "fast": "test_suites/security_fast.yaml",            # 5 tests  
    "comprehensive": "test_suites/security_comprehensive.yaml",  # 25 tests
    "owasp": "test_suites/owasp_top10.yaml",            # 13 tests
    "python": "test_suites/security_python_comprehensive.yaml", # 16 tests
    "javascript": "test_suites/security_javascript.yaml", # 10 tests
    # ... (all language-specific suites)
}
```

## 📈 Expanding Test Suites

### **Adding New Test Cases**

**1. Create new test case in existing suite:**
```yaml
- id: new_vulnerability_test
  prompt: |
    Your vulnerable code example or scenario description
  criteria:
    - 'primary_vulnerability_indicator'
    - 'security_recommendation_pattern'
    - 'technical_term_validation'
  must_not:
    - 'dangerous_advice_pattern'
  json: false
```

**2. Create new language-specific suite:**
```yaml
# security_newlang.yaml
# NewLang Security Test Suite
# Built by the Rapticore Security Research Team

- id: newlang_specific_vuln
  prompt: |
    Language-specific vulnerability example
  criteria:
    - 'newlang_security_pattern'
    - 'framework_specific_advice'
  must_not:
    - 'unsafe_practice'
  json: false
```

**3. Add to suite mapping:**
```python
DEFAULT_SUITE_FILES = {
    # ... existing suites ...
    "newlang": "test_suites/security_newlang.yaml",
}
```

### **Test Case Design Guidelines**

**Effective Prompts:**
- ✅ **Include realistic code examples**
- ✅ **Provide sufficient context** for analysis
- ✅ **Focus on specific vulnerability patterns**
- ✅ **Use industry-standard terminology**

**Robust Criteria:**
- ✅ **Use regex patterns** for flexible matching
- ✅ **Include multiple validation angles**
- ✅ **Balance positive and negative criteria**
- ✅ **Test security knowledge depth**

**Common Patterns:**
```yaml
criteria:
  - 'vulnerability_name'           # Basic identification
  - 'technical_explanation'       # Understanding depth  
  - 'mitigation_strategy'         # Solution knowledge
  - 'framework_specific_advice'   # Context awareness
must_not:
  - '\bno\s+issues?\b'           # False negative prevention
  - '\bcompletely\s+safe\b'      # Over-confidence detection
```

### **Specialized Suite Categories**

**Industry-Specific Suites:**
- **FinTech Security** (PCI DSS, payment processing)
- **Healthcare Security** (HIPAA, PHI protection)
- **IoT Security** (embedded systems, device communication)
- **Blockchain Security** (smart contracts, DeFi)

**Advanced Attack Vectors:**
- **Supply Chain Security** (dependency poisoning, build system attacks)
- **AI/ML Security** (model poisoning, adversarial attacks)
- **Cloud Security** (misconfiguration, IAM, container security)
- **Mobile Security** (Android/iOS specific vulnerabilities)

## 🧪 Test Validation & Quality Assurance

### **Automated Testing**

```bash
# Run standardized benchmark for consistent results
python standardized_benchmark_runner.py --suite comprehensive

# Quality validation with multiple models
python run_llm_benchmark.py --models gpt-4o,claude-sonnet-4,deepseek-chat --suite basic

# Performance testing with fast suite
python run_llm_benchmark.py --suite fast --timeout 10
```

### **Quality Metrics**

**Test Case Validation:**
- **Coverage Analysis**: Ensure all OWASP categories covered
- **Difficulty Distribution**: Mix of basic/intermediate/advanced tests
- **False Positive Rate**: Monitor `must_not` pattern effectiveness
- **Model Discrimination**: Tests should differentiate model capabilities

**Suite Performance Metrics:**
- **Execution Time**: Average time per test case
- **Cost Efficiency**: Cost per security assessment
- **Reliability**: Consistent results across runs
- **Comprehensiveness**: Vulnerability coverage breadth

### **Continuous Improvement**

**Regular Updates:**
- ✅ **Add new CVE patterns** as they emerge
- ✅ **Update OWASP mappings** with new releases
- ✅ **Refresh framework examples** with current versions
- ✅ **Incorporate zero-day patterns** from security research

**Community Contributions:**
- ✅ **GitHub Issues** for new vulnerability patterns
- ✅ **Pull Requests** for test case improvements
- ✅ **Security Researcher Feedback** integration
- ✅ **Industry Best Practice** updates

## 📊 Usage Analytics & Insights

### **Popular Test Combinations**

**Development Teams:**
```bash
# Quick CI/CD security check
python run_llm_benchmark.py --suite fast --models gpt-4o-mini

# Comprehensive pre-release audit  
python run_llm_benchmark.py --suite comprehensive --models claude-opus-4
```

**Security Teams:**
```bash
# OWASP compliance validation
python run_llm_benchmark.py --suite owasp --models gpt-5,claude-opus-4

# Multi-language security assessment
python run_llm_benchmark.py --suite python,javascript,java --models multiple
```

**Research Teams:**
```bash
# Model capability analysis
python run_llm_benchmark.py --suite comprehensive --models all_available

# Vulnerability pattern studies
python run_llm_benchmark.py --suite custom_research_suite --show-responses
```

## 🔧 Technical Implementation

### **Test Loading Architecture**

```python
def load_suite(path: str) -> List[dict]:
    """Load test suite with enhanced format support."""
    # Supports YAML and JSON formats
    # Handles predefined suite aliases
    # Enables suite combination and chaining
```

### **Scoring Implementation**

```python
def score_text_enhanced(text: str, criteria: List[str], must_not: List[str]) -> tuple:
    """Enhanced scoring with detailed breakdown."""
    # Returns: (score, criteria_met, criteria_missed, violations)
    # Supports regex pattern matching
    # Provides detailed analysis feedback
```

### **Extensibility Hooks**

- ✅ **Custom scoring functions** for specialized domains
- ✅ **Plugin architecture** for new test types
- ✅ **Webhook integration** for external validation
- ✅ **API endpoints** for programmatic access

---

## 📚 Additional Resources

- **Test Suite Development Guide**: `docs/creating_test_suites.md`
- **Security Pattern Library**: `docs/security_patterns.md`  
- **Scoring Methodology**: `docs/scoring_framework.md`
- **API Documentation**: `docs/api_reference.md`

---

**Comprehensive security testing for LLM capabilities - ensuring AI systems can effectively identify and address security vulnerabilities across languages, frameworks, and attack vectors.**

*Last Updated: September 8, 2025*  
*Test Suite Version: 2.0*  
*Total Test Cases: 226*