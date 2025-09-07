#!/usr/bin/env python3
"""
Enhanced Raw Data Capture System for LLM Security Benchmark
Comprehensive data preservation for future analysis and reporting.

Built by the Rapticore Security Research Team.
"""

import json
import pickle
import gzip
import hashlib
import platform
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. System monitoring will use basic fallbacks.")
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
import uuid


@dataclass
class SystemEnvironment:
    """Capture system environment information."""
    
    timestamp: str
    session_id: str
    hostname: str
    platform: str
    platform_version: str
    python_version: str
    cpu_count: int
    memory_total_gb: float
    memory_available_gb: float
    disk_free_gb: float
    network_connected: bool
    timezone: str
    user_agent: str = field(default_factory=lambda: f"LLM-Security-Benchmark/1.0")
    
    @classmethod
    def capture(cls, session_id: str) -> 'SystemEnvironment':
        """Capture current system environment."""
        import sys
        
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_count = psutil.cpu_count()
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            disk_free_gb = disk.free / (1024**3)
        else:
            # Fallback values when psutil is not available
            cpu_count = 4  # Reasonable default
            memory_total_gb = 8.0  # Reasonable default
            memory_available_gb = 4.0  # Reasonable default
            disk_free_gb = 100.0  # Reasonable default
        
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            hostname=platform.node(),
            platform=platform.system(),
            platform_version=platform.version(),
            python_version=sys.version,
            cpu_count=cpu_count,
            memory_total_gb=memory_total_gb,
            memory_available_gb=memory_available_gb,
            disk_free_gb=disk_free_gb,
            network_connected=True,  # Simplified - could add actual network check
            timezone=str(datetime.now().astimezone().tzinfo)
        )


@dataclass
class APIRequestDetails:
    """Detailed API request information."""
    
    request_id: str
    model_name: str
    provider: str
    endpoint: str
    method: str
    headers: Dict[str, Any]
    request_body: Dict[str, Any]
    request_size_bytes: int
    request_hash: str
    timestamp_sent: str
    
    # Response details
    response_status: int
    response_headers: Dict[str, Any]
    response_body: Dict[str, Any]
    response_size_bytes: int
    response_hash: str
    timestamp_received: str
    network_latency_ms: float
    
    # Error details (if any)
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Rate limiting info
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[str] = None
    retry_count: int = 0
    
    @classmethod
    def create_request_id(cls) -> str:
        return f"req_{uuid.uuid4().hex[:8]}_{int(time.time())}"


@dataclass
class TokenUsageDetails:
    """Detailed token usage information."""
    
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    total_cost_usd: float
    
    # Token breakdown (if available)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    
    # Pricing details
    pricing_model: str = "standard"
    pricing_date: str = field(default_factory=lambda: datetime.now().isoformat())
    currency: str = "USD"


@dataclass
class ResponseAnalysis:
    """Detailed analysis of model response."""
    
    raw_response: str
    cleaned_response: str
    response_length_chars: int
    response_length_words: int
    response_length_sentences: int
    response_language_detected: str
    
    # Scoring breakdown
    criteria_patterns: List[str]
    criteria_matches: List[Dict[str, Any]]
    criteria_missed: List[str]
    must_not_patterns: List[str]
    must_not_violations: List[Dict[str, Any]]
    
    # Content analysis
    contains_code: bool
    code_languages_detected: List[str]
    security_terms_found: List[str]
    vulnerability_types_mentioned: List[str]
    
    # Quality metrics
    readability_score: Optional[float] = None
    technical_depth_score: float = 0.0
    actionability_score: float = 0.0
    completeness_score: float = 0.0
    
    # Response characteristics
    response_structure: Dict[str, Any] = field(default_factory=dict)
    confidence_indicators: List[str] = field(default_factory=list)
    hedging_language: List[str] = field(default_factory=list)


@dataclass
class TestCaseDetails:
    """Enhanced test case information."""
    
    test_id: str
    test_suite: str
    test_category: str
    test_subcategory: Optional[str]
    programming_language: Optional[str]
    vulnerability_type: str
    owasp_category: Optional[str]
    cwe_numbers: List[str]
    severity_level: str
    
    # Test content
    prompt_template: str
    prompt_variables: Dict[str, Any]
    final_prompt: str
    prompt_hash: str
    
    # Expected outcomes
    expected_patterns: List[str]
    forbidden_patterns: List[str]
    difficulty_level: str
    points_possible: float
    
    # Metadata
    created_date: str
    last_modified: str
    test_version: str
    tags: List[str] = field(default_factory=list)


@dataclass
class EnhancedTestResult:
    """Comprehensive test result with all raw data."""
    
    # Identifiers
    result_id: str
    session_id: str
    test_case: TestCaseDetails
    model_name: str
    
    # Execution details
    execution_start: str
    execution_end: str
    execution_duration_ms: float
    retry_attempts: int
    
    # API details
    api_request: APIRequestDetails
    token_usage: TokenUsageDetails
    
    # Response analysis
    response_analysis: ResponseAnalysis
    
    # Scoring
    raw_score: float
    weighted_score: float
    normalized_score: float
    score_breakdown: Dict[str, float]
    
    # Status
    success: bool
    
    # Context (non-default fields must come before default fields)
    test_sequence_number: int
    total_tests_in_session: int
    
    # Optional fields with defaults
    error_details: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    system_load_during_test: Dict[str, float] = field(default_factory=dict)


class EnhancedDataCapture:
    """Enhanced data capture system."""
    
    def __init__(self, output_dir: Path, session_id: Optional[str] = None):
        self.output_dir = output_dir
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:12]}"
        self.start_time = datetime.now(timezone.utc)
        self.test_sequence = 0
        
        # Create session directory
        self.session_dir = output_dir / f"raw_data_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Capture system environment
        self.system_env = SystemEnvironment.capture(self.session_id)
        
        # Initialize data stores
        self.results: List[EnhancedTestResult] = []
        self.session_metadata = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "system_environment": asdict(self.system_env),
            "benchmark_version": "1.0.0",
            "data_format_version": "1.0"
        }
    
    def capture_test_result(self, 
                          test_case_info: Dict,
                          model_name: str,
                          request_details: Dict,
                          response_data: Dict,
                          analysis_results: Dict) -> EnhancedTestResult:
        """Capture comprehensive test result data."""
        
        self.test_sequence += 1
        result_id = f"result_{self.session_id}_{self.test_sequence:04d}"
        
        # Create enhanced test case details
        test_case = TestCaseDetails(
            test_id=test_case_info.get('id', 'unknown'),
            test_suite=test_case_info.get('suite', 'unknown'),
            test_category=test_case_info.get('category', 'security'),
            test_subcategory=test_case_info.get('subcategory'),
            programming_language=self._extract_language(test_case_info.get('id', '')),
            vulnerability_type=test_case_info.get('vulnerability_type', 'unknown'),
            owasp_category=self._map_to_owasp(test_case_info.get('id', '')),
            cwe_numbers=test_case_info.get('cwe_numbers', []),
            severity_level=test_case_info.get('severity', 'medium'),
            prompt_template=test_case_info.get('prompt', ''),
            prompt_variables=test_case_info.get('variables', {}),
            final_prompt=request_details.get('final_prompt', ''),
            prompt_hash=hashlib.sha256(request_details.get('final_prompt', '').encode()).hexdigest()[:16],
            expected_patterns=test_case_info.get('criteria', []),
            forbidden_patterns=test_case_info.get('must_not', []),
            difficulty_level=test_case_info.get('difficulty', 'medium'),
            points_possible=test_case_info.get('points', 1.0),
            created_date=test_case_info.get('created', datetime.now().isoformat()),
            last_modified=test_case_info.get('modified', datetime.now().isoformat()),
            test_version=test_case_info.get('version', '1.0'),
            tags=test_case_info.get('tags', [])
        )
        
        # Create API request details
        api_request = APIRequestDetails(
            request_id=APIRequestDetails.create_request_id(),
            model_name=model_name,
            provider=self._get_provider(model_name),
            endpoint=request_details.get('endpoint', 'unknown'),
            method=request_details.get('method', 'POST'),
            headers=request_details.get('headers', {}),
            request_body=request_details.get('body', {}),
            request_size_bytes=len(json.dumps(request_details.get('body', {})).encode()),
            request_hash=hashlib.sha256(json.dumps(request_details.get('body', {}), sort_keys=True).encode()).hexdigest()[:16],
            timestamp_sent=request_details.get('sent_at', datetime.now().isoformat()),
            response_status=response_data.get('status_code', 200),
            response_headers=response_data.get('headers', {}),
            response_body=response_data.get('body', {}),
            response_size_bytes=len(json.dumps(response_data.get('body', {})).encode()),
            response_hash=hashlib.sha256(json.dumps(response_data.get('body', {}), sort_keys=True).encode()).hexdigest()[:16],
            timestamp_received=response_data.get('received_at', datetime.now().isoformat()),
            network_latency_ms=response_data.get('latency_ms', 0.0),
            error_type=response_data.get('error_type'),
            error_message=response_data.get('error_message'),
            error_traceback=response_data.get('error_traceback'),
            rate_limit_remaining=response_data.get('rate_limit_remaining'),
            rate_limit_reset=response_data.get('rate_limit_reset'),
            retry_count=request_details.get('retry_count', 0)
        )
        
        # Create token usage details
        token_usage = TokenUsageDetails(
            input_tokens=response_data.get('input_tokens', 0),
            output_tokens=response_data.get('output_tokens', 0),
            total_tokens=response_data.get('total_tokens', 0),
            input_cost_per_1k=response_data.get('input_cost_per_1k', 0.0),
            output_cost_per_1k=response_data.get('output_cost_per_1k', 0.0),
            total_cost_usd=response_data.get('cost_usd', 0.0),
            prompt_tokens=response_data.get('prompt_tokens'),
            completion_tokens=response_data.get('completion_tokens'),
            reasoning_tokens=response_data.get('reasoning_tokens'),
            cached_tokens=response_data.get('cached_tokens')
        )
        
        # Create response analysis
        raw_response = response_data.get('text', '')
        response_analysis = ResponseAnalysis(
            raw_response=raw_response,
            cleaned_response=self._clean_response(raw_response),
            response_length_chars=len(raw_response),
            response_length_words=len(raw_response.split()),
            response_length_sentences=raw_response.count('.') + raw_response.count('!') + raw_response.count('?'),
            response_language_detected=self._detect_language(raw_response),
            criteria_patterns=test_case_info.get('criteria', []),
            criteria_matches=analysis_results.get('criteria_matches', []),
            criteria_missed=analysis_results.get('criteria_missed', []),
            must_not_patterns=test_case_info.get('must_not', []),
            must_not_violations=analysis_results.get('must_not_violations', []),
            contains_code=self._contains_code(raw_response),
            code_languages_detected=self._detect_code_languages(raw_response),
            security_terms_found=self._extract_security_terms(raw_response),
            vulnerability_types_mentioned=self._extract_vulnerability_types(raw_response),
            technical_depth_score=self._calculate_technical_depth(raw_response),
            actionability_score=self._calculate_actionability(raw_response),
            completeness_score=analysis_results.get('score', 0.0),
            response_structure=self._analyze_structure(raw_response),
            confidence_indicators=self._extract_confidence_indicators(raw_response),
            hedging_language=self._extract_hedging_language(raw_response)
        )
        
        # Create enhanced result
        result = EnhancedTestResult(
            result_id=result_id,
            session_id=self.session_id,
            test_case=test_case,
            model_name=model_name,
            execution_start=request_details.get('start_time', datetime.now().isoformat()),
            execution_end=response_data.get('end_time', datetime.now().isoformat()),
            execution_duration_ms=response_data.get('elapsed_ms', 0.0),
            retry_attempts=request_details.get('retry_count', 0),
            api_request=api_request,
            token_usage=token_usage,
            response_analysis=response_analysis,
            raw_score=analysis_results.get('raw_score', 0.0),
            weighted_score=analysis_results.get('weighted_score', 0.0),
            normalized_score=analysis_results.get('score', 0.0),
            score_breakdown=analysis_results.get('score_breakdown', {}),
            success=analysis_results.get('success', False),
            error_details=response_data.get('error_details'),
            warnings=analysis_results.get('warnings', []),
            test_sequence_number=self.test_sequence,
            total_tests_in_session=analysis_results.get('total_tests', 0),
            system_load_during_test=self._capture_system_load()
        )
        
        self.results.append(result)
        return result
    
    def _extract_language(self, test_id: str) -> Optional[str]:
        """Extract programming language from test ID."""
        language_mapping = {
            'python_': 'Python',
            'js_': 'JavaScript',
            'java_': 'Java',
            'go_': 'Go',
            'rust_': 'Rust',
            'c_': 'C',
            'cpp_': 'C++',
            'csharp_': 'C#',
            'php_': 'PHP',
            'ruby_': 'Ruby',
            'haskell_': 'Haskell'
        }
        
        for prefix, lang in language_mapping.items():
            if test_id.startswith(prefix):
                return lang
        return None
    
    def _map_to_owasp(self, test_id: str) -> Optional[str]:
        """Map test to OWASP category."""
        owasp_mapping = {
            'sql_injection': 'A03 - Injection',
            'command_injection': 'A03 - Injection',
            'broken_access_control': 'A01 - Broken Access Control',
            'weak_crypto': 'A02 - Cryptographic Failures',
            'insecure_deserialization': 'A08 - Software and Data Integrity Failures',
            'ssrf': 'A10 - Server-Side Request Forgery',
            'xss': 'A03 - Injection',
            'authentication': 'A07 - Identification and Authentication Failures'
        }
        
        for pattern, category in owasp_mapping.items():
            if pattern in test_id.lower():
                return category
        return None
    
    def _get_provider(self, model_name: str) -> str:
        """Get provider from model name."""
        if model_name.startswith('gpt-'):
            return 'OpenAI'
        elif model_name.startswith('claude-'):
            return 'Anthropic'
        elif model_name.startswith('gemini-'):
            return 'Google'
        return 'Unknown'
    
    def _clean_response(self, text: str) -> str:
        """Clean response text."""
        # Basic cleaning - could be enhanced
        return text.strip()
    
    def _detect_language(self, text: str) -> str:
        """Detect response language."""
        # Simplified - would use proper language detection in production
        return 'English'
    
    def _contains_code(self, text: str) -> bool:
        """Check if response contains code."""
        code_indicators = ['```', '`', 'def ', 'function ', 'class ', '{', '}', 'import ', 'from ']
        return any(indicator in text for indicator in code_indicators)
    
    def _detect_code_languages(self, text: str) -> List[str]:
        """Detect programming languages in code blocks."""
        languages = []
        if '```python' in text or 'def ' in text:
            languages.append('Python')
        if '```javascript' in text or 'function ' in text:
            languages.append('JavaScript')
        if '```java' in text or 'public class' in text:
            languages.append('Java')
        return languages
    
    def _extract_security_terms(self, text: str) -> List[str]:
        """Extract security-related terms."""
        security_terms = [
            'vulnerability', 'exploit', 'attack', 'injection', 'XSS', 'CSRF', 'SQL injection',
            'authentication', 'authorization', 'encryption', 'hash', 'sanitize', 'validate'
        ]
        found_terms = []
        text_lower = text.lower()
        for term in security_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        return found_terms
    
    def _extract_vulnerability_types(self, text: str) -> List[str]:
        """Extract mentioned vulnerability types."""
        vuln_types = [
            'SQL Injection', 'XSS', 'CSRF', 'Command Injection', 'Path Traversal',
            'Insecure Deserialization', 'Weak Cryptography', 'Broken Access Control'
        ]
        found_vulns = []
        text_lower = text.lower()
        for vuln in vuln_types:
            if vuln.lower() in text_lower:
                found_vulns.append(vuln)
        return found_vulns
    
    def _calculate_technical_depth(self, text: str) -> float:
        """Calculate technical depth score."""
        technical_indicators = [
            'parameter', 'function', 'method', 'class', 'variable', 'algorithm',
            'protocol', 'header', 'payload', 'encoding', 'parsing', 'validation'
        ]
        score = sum(1 for indicator in technical_indicators if indicator.lower() in text.lower())
        return min(score / 5.0, 1.0)  # Normalize to 0-1
    
    def _calculate_actionability(self, text: str) -> float:
        """Calculate actionability score."""
        actionable_indicators = [
            'should', 'must', 'recommend', 'suggest', 'fix', 'prevent', 'use',
            'avoid', 'implement', 'configure', 'update', 'patch'
        ]
        score = sum(1 for indicator in actionable_indicators if indicator.lower() in text.lower())
        return min(score / 6.0, 1.0)  # Normalize to 0-1
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze response structure."""
        return {
            'has_introduction': text.strip().startswith(('This', 'The', 'A ')),
            'has_conclusion': any(word in text.lower() for word in ['conclusion', 'summary', 'finally']),
            'has_bullet_points': '•' in text or '*' in text or text.count('\n- ') > 0,
            'has_code_blocks': '```' in text,
            'paragraph_count': text.count('\n\n') + 1,
            'has_headings': '#' in text or any(line.isupper() for line in text.split('\n') if line.strip())
        }
    
    def _extract_confidence_indicators(self, text: str) -> List[str]:
        """Extract confidence indicators."""
        confidence_words = ['definitely', 'certainly', 'clearly', 'obviously', 'sure', 'confident']
        found = []
        text_lower = text.lower()
        for word in confidence_words:
            if word in text_lower:
                found.append(word)
        return found
    
    def _extract_hedging_language(self, text: str) -> List[str]:
        """Extract hedging language."""
        hedging_words = ['might', 'could', 'possibly', 'perhaps', 'maybe', 'seems', 'appears', 'likely']
        found = []
        text_lower = text.lower()
        for word in hedging_words:
            if word in text_lower:
                found.append(word)
        return found
    
    def _capture_system_load(self) -> Dict[str, float]:
        """Capture current system load."""
        if not PSUTIL_AVAILABLE:
            return {
                'cpu_percent': 50.0,  # Default values when psutil unavailable
                'memory_percent': 60.0,
                'disk_io_read_mb': 0.0,
                'disk_io_write_mb': 0.0,
                'network_sent_mb': 0.0,
                'network_recv_mb': 0.0
            }
        
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_io_read_mb': psutil.disk_io_counters().read_bytes / (1024*1024),
                'disk_io_write_mb': psutil.disk_io_counters().write_bytes / (1024*1024),
                'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024*1024),
                'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024*1024)
            }
        except:
            return {
                'cpu_percent': 0.0,  # Fallback if psutil calls fail
                'memory_percent': 0.0,
                'disk_io_read_mb': 0.0,
                'disk_io_write_mb': 0.0,
                'network_sent_mb': 0.0,
                'network_recv_mb': 0.0
            }
    
    def export_raw_data(self) -> Dict[str, str]:
        """Export all captured data in multiple formats."""
        
        session_end_time = datetime.now(timezone.utc)
        self.session_metadata.update({
            "end_time": session_end_time.isoformat(),
            "duration_seconds": (session_end_time - self.start_time).total_seconds(),
            "total_tests": len(self.results),
            "successful_tests": sum(1 for r in self.results if r.success),
            "failed_tests": sum(1 for r in self.results if not r.success),
            "unique_models": len(set(r.model_name for r in self.results)),
            "total_cost": sum(r.token_usage.total_cost_usd for r in self.results)
        })
        
        exported_files = {}
        
        # 1. Complete session data as JSON
        complete_data = {
            "session_metadata": self.session_metadata,
            "system_environment": asdict(self.system_env),
            "results": [asdict(result) for result in self.results]
        }
        
        json_path = self.session_dir / f"complete_session_data_{self.session_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, default=str)
        exported_files['complete_json'] = str(json_path)
        
        # 2. Compressed complete data
        gzip_path = self.session_dir / f"complete_session_data_{self.session_id}.json.gz"
        with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, default=str)
        exported_files['compressed_json'] = str(gzip_path)
        
        # 3. Python pickle for future analysis
        pickle_path = self.session_dir / f"session_objects_{self.session_id}.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump({
                'metadata': self.session_metadata,
                'environment': self.system_env,
                'results': self.results,
                'capture_instance': self
            }, f)
        exported_files['pickle_data'] = str(pickle_path)
        
        # 4. Raw responses only (for text analysis)
        raw_responses = {
            "session_id": self.session_id,
            "responses": [
                {
                    "result_id": r.result_id,
                    "model": r.model_name,
                    "test_id": r.test_case.test_id,
                    "prompt": r.test_case.final_prompt,
                    "response": r.response_analysis.raw_response,
                    "score": r.normalized_score,
                    "timestamp": r.execution_start
                }
                for r in self.results
            ]
        }
        
        responses_path = self.session_dir / f"raw_responses_{self.session_id}.json"
        with open(responses_path, 'w', encoding='utf-8') as f:
            json.dump(raw_responses, f, indent=2, default=str)
        exported_files['raw_responses'] = str(responses_path)
        
        # 5. Analysis-ready CSV
        import csv
        csv_path = self.session_dir / f"analysis_ready_{self.session_id}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'session_id', 'result_id', 'timestamp', 'model_name', 'provider',
                'test_id', 'test_category', 'programming_language', 'vulnerability_type', 'owasp_category',
                'prompt_hash', 'response_hash', 'execution_duration_ms', 'retry_attempts',
                'input_tokens', 'output_tokens', 'total_tokens', 'cost_usd',
                'response_length_chars', 'response_length_words', 'contains_code',
                'security_terms_count', 'vulnerability_types_count', 'technical_depth_score',
                'actionability_score', 'raw_score', 'weighted_score', 'normalized_score',
                'success', 'criteria_matches', 'criteria_missed', 'must_not_violations',
                'confidence_indicators_count', 'hedging_language_count', 'network_latency_ms',
                'system_cpu_percent', 'system_memory_percent'
            ])
            
            # Data rows
            for r in self.results:
                writer.writerow([
                    r.session_id, r.result_id, r.execution_start, r.model_name, self._get_provider(r.model_name),
                    r.test_case.test_id, r.test_case.test_category, r.test_case.programming_language,
                    r.test_case.vulnerability_type, r.test_case.owasp_category,
                    r.test_case.prompt_hash, r.api_request.response_hash, r.execution_duration_ms, r.retry_attempts,
                    r.token_usage.input_tokens, r.token_usage.output_tokens, r.token_usage.total_tokens, r.token_usage.total_cost_usd,
                    r.response_analysis.response_length_chars, r.response_analysis.response_length_words, r.response_analysis.contains_code,
                    len(r.response_analysis.security_terms_found), len(r.response_analysis.vulnerability_types_mentioned),
                    r.response_analysis.technical_depth_score, r.response_analysis.actionability_score,
                    r.raw_score, r.weighted_score, r.normalized_score, r.success,
                    len(r.response_analysis.criteria_matches), len(r.response_analysis.criteria_missed),
                    len(r.response_analysis.must_not_violations), len(r.response_analysis.confidence_indicators),
                    len(r.response_analysis.hedging_language), r.api_request.network_latency_ms,
                    r.system_load_during_test.get('cpu_percent', 0), r.system_load_during_test.get('memory_percent', 0)
                ])
        
        exported_files['analysis_csv'] = str(csv_path)
        
        # 6. Summary report
        summary_path = self.session_dir / f"session_summary_{self.session_id}.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Raw Data Capture Session Summary

**Session ID:** {self.session_id}
**Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Duration:** {self.session_metadata.get('duration_seconds', 0):.1f} seconds

## Data Captured

- **Total Tests:** {len(self.results):,}
- **Unique Models:** {len(set(r.model_name for r in self.results))}
- **Success Rate:** {(sum(1 for r in self.results if r.success) / len(self.results) * 100):.1f}%
- **Total Cost:** ${sum(r.token_usage.total_cost_usd for r in self.results):.4f}
- **Total Tokens:** {sum(r.token_usage.total_tokens for r in self.results):,}

## Files Generated

{chr(10).join(f"- **{name}**: `{Path(path).name}`" for name, path in exported_files.items())}

## System Environment

- **Platform:** {self.system_env.platform} {self.system_env.platform_version}
- **Python:** {self.system_env.python_version.split()[0]}
- **Memory:** {self.system_env.memory_total_gb:.1f}GB total
- **CPU Cores:** {self.system_env.cpu_count}

## Next Steps

Use the captured data for:
1. Advanced statistical analysis with `analysis_ready_{self.session_id}.csv`
2. Response quality analysis with `raw_responses_{self.session_id}.json`
3. Detailed investigation with `complete_session_data_{self.session_id}.json`
4. Python analysis with `session_objects_{self.session_id}.pkl`

**Built by the Rapticore Security Research Team**
""")
        
        exported_files['summary_report'] = str(summary_path)
        
        return exported_files