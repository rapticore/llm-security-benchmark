#!/usr/bin/env python3
"""
Quality-First Benchmark Audit & Fix

Implements methodologically correct, quality-first analysis with strict data integrity.
Addresses test count inconsistencies and ensures accuracy gates before cost optimization.

Built by the Rapticore Security Research Team
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd


@dataclass
class ModelMetrics:
    """Quality-first model metrics with strict accuracy gates."""
    model_name: str
    tests_run: int
    accuracy: float  # avg_score (0-1)
    reliability: float  # 1 - (empty_rate + timeout_rate + json_fail_rate)
    mean_latency: float  # seconds
    p95_latency: float  # seconds  
    cost_per_test: float  # USD
    good_count: int  # tests with score >= 0.70
    total_tokens: int
    input_tokens: int
    output_tokens: int

    # Quality gates
    passes_80_gate: bool = False  # accuracy >= 0.80 AND reliability >= 0.98
    passes_90_gate: bool = False  # accuracy >= 0.90 AND reliability >= 0.98

    # Rankings
    value80_rank: Optional[int] = None
    value90_rank: Optional[int] = None
    final_score: float = 0.0


class QualityFirstAuditor:
    """Implements quality-first audit with strict methodological requirements."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.accuracy_80_threshold = 0.80
        self.accuracy_90_threshold = 0.90
        self.reliability_threshold = 0.98
        self.good_score_threshold = 0.70
        self.target_latency = 10.0
        self.expected_test_count = 5

        # Diagnostic tracking
        self.duplicates_pruned = {}
        self.models_below_80 = []
        self.models_below_90 = []
        self.winners_before = {}
        self.winners_after = {}

    def audit_and_fix_benchmark(self, results_dir: Path) -> Dict[str, Any]:
        """Main audit function implementing all quality-first requirements."""

        print("🔍 === QUALITY-FIRST BENCHMARK AUDIT ===")
        print("Implementing methodologically correct, quality-first analysis")
        print()

        # A) Data Integrity & Test Count Consistency
        print("A) DATA INTEGRITY & TEST COUNT CONSISTENCY")
        print("-" * 50)

        raw_data = self._load_raw_data(results_dir)
        print(f"📊 Loaded {len(raw_data)} raw test results")

        # Assert suite has exactly 5 unique test cases
        unique_tests = set(r.get('suite_id', r.get('test_id', 'unknown')) for r in raw_data)
        print(f"🧪 Unique test cases found: {len(unique_tests)}")
        if len(unique_tests) != self.expected_test_count:
            print(f"⚠️  Expected {self.expected_test_count} tests, found {len(unique_tests)}")
            print(f"   Tests: {sorted(unique_tests)}")

        # Deduplicate and enforce one record per (model, test_case)
        deduped_data = self._deduplicate_results(raw_data)
        print(f"📋 After deduplication: {len(deduped_data)} results")

        # Validate test counts per model
        self._validate_test_counts(deduped_data)

        # B) Quality-First Metrics
        print("\nB) QUALITY-FIRST METRICS COMPUTATION")
        print("-" * 50)

        model_metrics = self._compute_quality_metrics(deduped_data)

        # Apply quality gates
        self._apply_quality_gates(model_metrics)

        # Compute rankings
        value80_table = self._compute_value80_ranking(model_metrics)
        value90_table = self._compute_value90_ranking(model_metrics)

        # C) Quality-First Final Scores
        print("\nC) CONTINUOUS FINAL SCORES (QUALITY-FIRST)")
        print("-" * 50)

        self._compute_final_scores(model_metrics, deduped_data)

        # D) Diagnostics
        print("\nD) AUDIT DIAGNOSTICS")
        print("-" * 50)

        self._print_diagnostics(model_metrics, value80_table, value90_table)

        # Generate corrected reports
        audit_results = {
            'model_metrics': model_metrics,
            'value80_table': value80_table,
            'value90_table': value90_table,
            'deduped_data': deduped_data,
            'unique_tests': list(unique_tests),
            'duplicates_pruned': self.duplicates_pruned,
            'audit_summary': self._generate_audit_summary(model_metrics, value80_table)
        }

        return audit_results

    def _load_raw_data(self, results_dir: Path) -> List[Dict]:
        """Load raw benchmark data from various sources."""
        raw_data = []

        # Try comprehensive analysis first
        comp_file = results_dir / "comprehensive_analysis.json"
        if comp_file.exists():
            with open(comp_file, 'r') as f:
                data = json.load(f)
                if 'detailed_results' in data:
                    raw_data.extend(data['detailed_results'])

        # Try performance analysis
        perf_file = results_dir / "performance_analysis.json"
        if perf_file.exists() and not raw_data:
            with open(perf_file, 'r') as f:
                data = json.load(f)
                # Convert performance analysis format to detailed results
                for model, stats in data.get('model_comparison', {}).items():
                    # Create synthetic records based on aggregated stats
                    for i in range(stats.get('total_tests', 0)):
                        raw_data.append({
                            'model_name': model,
                            'test_id': f"test_{i}",
                            'suite_id': f"test_{i}",
                            'success': True,
                            'score': stats['avg_score'],  # This is approximate
                            'response_time_s': stats['avg_response_time'],
                            'cost_usd': stats['avg_cost_per_test'],
                            'input_tokens': stats['avg_input_tokens_per_test'],
                            'output_tokens': stats['avg_output_tokens_per_test']
                        })

        # Try CSV if available
        csv_file = results_dir / "detailed_results.csv"
        if csv_file.exists() and not raw_data:
            df = pd.read_csv(csv_file)
            raw_data = df.to_dict('records')

        return raw_data

    def _deduplicate_results(self, raw_data: List[Dict]) -> List[Dict]:
        """Deduplicate results, keeping latest run per (model, test_case)."""

        # Group by (model, test_case)
        groups = {}
        for result in raw_data:
            model = result.get('model_name', result.get('model', 'unknown'))
            test_id = result.get('suite_id', result.get('test_id', 'unknown'))
            key = (model, test_id)

            if key not in groups:
                groups[key] = []
            groups[key].append(result)

        # Deduplicate each group
        deduped_data = []
        for (model, test_id), results in groups.items():
            if len(results) > 1:
                # Track duplicates
                if model not in self.duplicates_pruned:
                    self.duplicates_pruned[model] = 0
                self.duplicates_pruned[model] += len(results) - 1

                # Keep latest if timestamps exist, otherwise first
                if any('timestamp' in r for r in results):
                    selected = max(results, key=lambda x: x.get('timestamp', ''))
                else:
                    selected = results[0]  # Deterministic first

                deduped_data.append(selected)
            else:
                deduped_data.append(results[0])

        return deduped_data

    def _validate_test_counts(self, deduped_data: List[Dict]):
        """Validate that each model has exactly expected test count."""

        model_test_counts = {}
        for result in deduped_data:
            model = result.get('model_name', result.get('model', 'unknown'))
            if model not in model_test_counts:
                model_test_counts[model] = 0
            model_test_counts[model] += 1

        print("📊 Test counts per model (after deduplication):")
        all_correct = True
        for model, count in sorted(model_test_counts.items()):
            status = "✅" if count == self.expected_test_count else "❌"
            print(f"   {status} {model}: {count}/{self.expected_test_count}")
            if count != self.expected_test_count:
                all_correct = False

        if not all_correct:
            print(f"\n⚠️  WARNING: Not all models have {self.expected_test_count} tests!")
            print("   This will cause unfair comparisons. Consider re-running benchmark.")

    def _compute_quality_metrics(self, deduped_data: List[Dict]) -> Dict[str, ModelMetrics]:
        """Compute quality-first metrics for each model."""

        model_data = {}
        for result in deduped_data:
            model = result.get('model_name', result.get('model', 'unknown'))
            if model not in model_data:
                model_data[model] = []
            model_data[model].append(result)

        model_metrics = {}
        for model, results in model_data.items():
            metrics = self._compute_single_model_metrics(model, results)
            model_metrics[model] = metrics

        return model_metrics

    def _compute_single_model_metrics(self, model: str, results: List[Dict]) -> ModelMetrics:
        """Compute metrics for a single model."""

        # Basic counts
        tests_run = len(results)
        successful_tests = [r for r in results if r.get('success', True)]

        # Accuracy (avg_score)
        scores = [r.get('score', 0.0) for r in successful_tests]
        accuracy = np.mean(scores) if scores else 0.0

        # Reliability (1 - failure_rates)
        empty_rate = sum(1 for r in results if not r.get('text', '').strip()) / len(results)
        timeout_rate = sum(1 for r in results if 'timeout' in str(r.get('error', '')).lower()) / len(results)
        json_fail_rate = sum(1 for r in results if 'json' in str(r.get('error', '')).lower()) / len(results)
        reliability = max(0.0, min(1.0, 1.0 - empty_rate - timeout_rate - json_fail_rate))

        # Latency 
        latencies = [r.get('response_time_s', r.get('elapsed_s', 0.0)) for r in results]
        mean_latency = np.mean(latencies) if latencies else 0.0
        p95_latency = np.percentile(latencies, 95) if latencies else 0.0

        # Cost
        costs = [r.get('cost_usd', 0.0) for r in results]
        cost_per_test = np.mean(costs) if costs else 0.0

        # Good count (score >= 0.70)
        good_count = sum(1 for r in results if r.get('score', 0.0) >= self.good_score_threshold)

        # Tokens
        total_input = sum(r.get('input_tokens', 0) for r in results)
        total_output = sum(r.get('output_tokens', 0) for r in results)
        total_tokens = total_input + total_output

        return ModelMetrics(
            model_name=model,
            tests_run=tests_run,
            accuracy=accuracy,
            reliability=reliability,
            mean_latency=mean_latency,
            p95_latency=p95_latency,
            cost_per_test=cost_per_test,
            good_count=good_count,
            total_tokens=total_tokens,
            input_tokens=total_input,
            output_tokens=total_output
        )

    def _apply_quality_gates(self, model_metrics: Dict[str, ModelMetrics]):
        """Apply 80% and 90% accuracy gates with reliability requirements."""

        for model, metrics in model_metrics.items():
            # 80% gate
            metrics.passes_80_gate = (
                    metrics.accuracy >= self.accuracy_80_threshold and
                    metrics.reliability >= self.reliability_threshold
            )

            # 90% gate  
            metrics.passes_90_gate = (
                    metrics.accuracy >= self.accuracy_90_threshold and
                    metrics.reliability >= self.reliability_threshold
            )

            # Track models below thresholds
            if not metrics.passes_80_gate:
                self.models_below_80.append(model)
            if not metrics.passes_90_gate:
                self.models_below_90.append(model)

    def _compute_value80_ranking(self, model_metrics: Dict[str, ModelMetrics]) -> List[ModelMetrics]:
        """Compute Value80 ranking: accuracy >= 80%, reliability >= 98%, then cost-optimized."""

        eligible = [m for m in model_metrics.values() if m.passes_80_gate]

        # Sort by: cost (asc), accuracy (desc), p95_latency (asc)
        eligible.sort(key=lambda x: (x.cost_per_test, -x.accuracy, x.p95_latency))

        # Assign ranks
        for i, metrics in enumerate(eligible):
            metrics.value80_rank = i + 1

        return eligible

    def _compute_value90_ranking(self, model_metrics: Dict[str, ModelMetrics]) -> List[ModelMetrics]:
        """Compute Value90 ranking: accuracy >= 90%, reliability >= 98%, then cost-optimized."""

        eligible = [m for m in model_metrics.values() if m.passes_90_gate]

        # Sort by: cost (asc), accuracy (desc), p95_latency (asc)  
        eligible.sort(key=lambda x: (x.cost_per_test, -x.accuracy, x.p95_latency))

        # Assign ranks
        for i, metrics in enumerate(eligible):
            metrics.value90_rank = i + 1

        return eligible

    def _compute_final_scores(self, model_metrics: Dict[str, ModelMetrics], deduped_data: List[Dict]):
        """Compute continuous final scores with quality-first constraints."""

        costs = [m.cost_per_test for m in model_metrics.values() if m.cost_per_test > 0]
        median_cost = np.median(costs) if costs else 1.0

        for model, metrics in model_metrics.items():
            # Latency normalization
            l_norm = min(1.0, self.target_latency / max(metrics.mean_latency, 1.0))

            # Quality Index (accuracy^0.70 * reliability^0.20 * latency^0.10)
            qi_raw = (
                    (metrics.accuracy ** 0.70) *
                    (metrics.reliability ** 0.20) *
                    (l_norm ** 0.10)
            )

            # Cost penalty
            c_pen = 1 + 0.2 * np.log1p(metrics.cost_per_test / median_cost)

            # Final score
            metrics.final_score = qi_raw / c_pen

    def _print_diagnostics(self, model_metrics: Dict[str, ModelMetrics],
                           value80_table: List[ModelMetrics], value90_table: List[ModelMetrics]):
        """Print comprehensive audit diagnostics."""

        print("📋 DUPLICATES PRUNED:")
        if self.duplicates_pruned:
            for model, count in self.duplicates_pruned.items():
                print(f"   • {model}: {count} duplicate(s) removed")
        else:
            print("   ✅ No duplicates found")

        print(f"\n🚫 MODELS BELOW 80% ACCURACY GATE:")
        if self.models_below_80:
            for model in self.models_below_80:
                metrics = model_metrics[model]
                print(f"   • {model}: Accuracy={metrics.accuracy:.1%}, Reliability={metrics.reliability:.1%}")
        else:
            print("   ✅ All models pass 80% gate")

        print(f"\n🏆 VALUE80 TABLE (≥80% Accuracy, ≥98% Reliability):")
        if value80_table:
            print("   Rank | Model | Accuracy | Reliability | P95 Latency | Cost/Test")
            print("   -----|-------|----------|-------------|-------------|----------")
            for metrics in value80_table[:5]:  # Top 5
                print(
                    f"   {metrics.value80_rank:4d} | {metrics.model_name:8s} | {metrics.accuracy:8.1%} | {metrics.reliability:11.1%} | {metrics.p95_latency:11.2f}s | ${metrics.cost_per_test:.5f}")
        else:
            print("   ❌ NO MODELS QUALIFY for Value80 ranking")

        print(f"\n🏅 VALUE90 TABLE (≥90% Accuracy, ≥98% Reliability):")
        if value90_table:
            print("   Rank | Model | Accuracy | Reliability | P95 Latency | Cost/Test")
            print("   -----|-------|----------|-------------|-------------|----------")
            for metrics in value90_table[:3]:  # Top 3
                print(
                    f"   {metrics.value90_rank:4d} | {metrics.model_name:8s} | {metrics.accuracy:8.1%} | {metrics.reliability:11.1%} | {metrics.p95_latency:11.2f}s | ${metrics.cost_per_test:.5f}")
        else:
            print("   ❌ NO MODELS QUALIFY for Value90 ranking")

    def _generate_audit_summary(self, model_metrics: Dict[str, ModelMetrics],
                                value80_table: List[ModelMetrics]) -> Dict[str, Any]:
        """Generate audit summary for reporting."""

        # Find best performers  
        best_accuracy = max(model_metrics.values(), key=lambda x: x.accuracy)
        best_value80 = value80_table[0] if value80_table else None

        # Fast among eligible
        eligible_for_speed = [m for m in model_metrics.values() if m.passes_80_gate]
        fastest_eligible = min(eligible_for_speed, key=lambda x: x.p95_latency) if eligible_for_speed else None

        return {
            'total_models': len(model_metrics),
            'models_pass_80_gate': len([m for m in model_metrics.values() if m.passes_80_gate]),
            'models_pass_90_gate': len([m for m in model_metrics.values() if m.passes_90_gate]),
            'best_accuracy': {
                'model': best_accuracy.model_name,
                'accuracy': best_accuracy.accuracy,
                'reliability': best_accuracy.reliability
            } if best_accuracy else None,
            'best_value80': {
                'model': best_value80.model_name,
                'accuracy': best_value80.accuracy,
                'cost_per_test': best_value80.cost_per_test,
                'reliability': best_value80.reliability,
                'p95_latency': best_value80.p95_latency
            } if best_value80 else None,
            'fastest_eligible': {
                'model': fastest_eligible.model_name,
                'p95_latency': fastest_eligible.p95_latency,
                'accuracy': fastest_eligible.accuracy
            } if fastest_eligible else None,
            'duplicates_total': sum(self.duplicates_pruned.values()),
            'data_integrity_pass': all(m.tests_run == self.expected_test_count for m in model_metrics.values())
        }


def run_quality_first_audit(results_dir: str = None) -> Dict[str, Any]:
    """Run complete quality-first audit on latest benchmark results."""

    if not results_dir:
        # Find latest results
        results_base = Path("benchmark_results")
        if not results_base.exists():
            raise ValueError("No benchmark_results directory found")

        result_dirs = [d for d in results_base.iterdir() if d.is_dir() and d.name.startswith("enhanced_")]
        if not result_dirs:
            raise ValueError("No enhanced benchmark results found")

        results_dir = max(result_dirs, key=lambda x: x.stat().st_mtime)
    else:
        results_dir = Path(results_dir)

    print(f"🔍 Auditing benchmark results: {results_dir.name}")
    print()

    auditor = QualityFirstAuditor()
    return auditor.audit_and_fix_benchmark(results_dir)


if __name__ == "__main__":
    # Run audit on latest results
    try:
        audit_results = run_quality_first_audit()
        print("\n" + "=" * 80)
        print("✅ QUALITY-FIRST AUDIT COMPLETE")
        print("=" * 80)

        summary = audit_results['audit_summary']
        print(f"📊 Total models analyzed: {summary['total_models']}")
        print(f"✅ Models passing 80% gate: {summary['models_pass_80_gate']}")
        print(f"🏅 Models passing 90% gate: {summary['models_pass_90_gate']}")

        if summary['best_value80']:
            bv = summary['best_value80']
            print(f"💰 Best Value (≥80%): {bv['model']} @ ${bv['cost_per_test']:.5f}/test")
            print(
                f"   (Accuracy={bv['accuracy']:.1%}, Reliability={bv['reliability']:.1%}, P95={bv['p95_latency']:.1f}s)")
        else:
            print("❌ NO MODEL qualifies as 'Best Value' (none pass 80% accuracy gate)")

        if summary['duplicates_total'] > 0:
            print(f"🔧 Data integrity: {summary['duplicates_total']} duplicates pruned")
        else:
            print("✅ Data integrity: No duplicates found")

    except Exception as e:
        print(f"❌ Audit failed: {e}")
        import traceback

        traceback.print_exc()
