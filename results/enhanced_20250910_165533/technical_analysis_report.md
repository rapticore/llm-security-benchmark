# LLM Security Benchmark — Technical Analysis Report

**Generated:** 2025-09-11 01:22:00 UTC  
**Suite:** all  
**Models Analyzed:** 18  
**Total Tests:** 3798  
**Total Investment:** $37.6313

## Objective
Security-focused evaluation for both **RAPID_RESPONSE** (time-sensitive) and **IN_DEPTH** (deep) use-cases.

- Performance: latency distribution, reliability
- Statistical rigor: Wilson CIs (proportions), Bootstrap CIs (means), sample-size adequacy
- Cost efficiency: token utilization, cost per correct
- Gates: per-use-case thresholds and Go/No-Go

## TL;DR Recommendations

**For Rapid Response:** gemini-2.5-flash-lite
**For In-Depth Analysis (highest accuracy):** claude-opus-4, claude-sonnet-4

## Model Performance Summary

| Model | n | Success (95% CI) | Avg Acc (95% CI) | P95 Lat (s) | Cost/Test | Avg Tokens |
|------|--:|-------------------|------------------|------------:|----------:|----------:|
| claude-opus-4 | 211 | 100.0% [0.98, 1.00] | 72.7% [0.70, 0.75] | 28.76 | $0.10488 | 1,662 |
| claude-sonnet-4 | 211 | 100.0% [0.98, 1.00] | 71.4% [0.69, 0.73] | 28.10 | $0.02113 | 1,672 |
| gemini-2.5-flash-lite | 211 | 100.0% [0.98, 1.00] | 71.3% [0.69, 0.74] | 6.85 | $0.00032 | 2,375 |
| gpt-4o | 211 | 100.0% [0.98, 1.00] | 66.4% [0.63, 0.69] | 18.13 | $0.00705 | 903 |
| gpt-4o-mini | 211 | 100.0% [0.98, 1.00] | 66.2% [0.63, 0.69] | 24.46 | $0.00052 | 1,071 |
| grok-3 | 422 | 100.0% [0.99, 1.00] | 65.7% [0.64, 0.68] | 42.16 | $0.01209 | 1,016 |
| gpt-5-mini | 211 | 100.0% [0.98, 1.00] | 52.0% [0.49, 0.55] | 11.56 | $0.00217 | 739 |
| deepseek-chat | 422 | 100.0% [0.99, 1.00] | 47.0% [0.45, 0.50] | 15.65 | $0.00007 | 401 |
| grok-code-fast-1 | 211 | 100.0% [0.98, 1.00] | 42.7% [0.39, 0.46] | 8.56 | $0.00062 | 807 |
| grok-4 | 211 | 100.0% [0.98, 1.00] | 42.2% [0.38, 0.46] | 31.81 | $0.00793 | 1,278 |
| gpt-5 | 211 | 97.2% [0.94, 0.99] | 39.5% [0.36, 0.43] | 22.76 | $0.00789 | 744 |
| deepseek-reasoner | 211 | 100.0% [0.98, 1.00] | 29.5% [0.26, 0.34] | 35.30 | $0.00137 | 833 |
| grok-3-mini | 211 | 100.0% [0.98, 1.00] | 17.5% [0.15, 0.21] | 19.41 | $0.00014 | 381 |
| gemini-2.5-flash | 211 | 9.5% [0.06, 0.14] | 5.5% [0.03, 0.08] | 14.56 | $0.00001 | 52 |
| gemini-2.0-flash-lite | 211 | 0.5% [0.00, 0.03] | 0.3% [0.00, 0.01] | 14.13 | $0.00000 | 10 |
| gemini-2.0-flash | 211 | 0.0% [0.00, 0.02] | 0.0% [0.00, 0.00] | 0.00 | $0.00000 | 0 |

### Latency Distribution

| Model | Mean | Median | P95 | P99 | Std Dev | Theoretical Throughput/Worker (req/h) |
|------|-----:|------:|---:|---:|------:|-------------------------------------:|
| gpt-5 | 15.17s | 15.63s | 22.76s | 25.45s | 4.83s | 237 |
| claude-opus-4 | 20.69s | 20.43s | 28.76s | 29.95s | 5.44s | 174 |
| gemini-2.5-flash | 11.69s | 11.87s | 14.56s | 15.29s | 2.31s | 308 |
| grok-4 | 20.26s | 18.59s | 31.81s | 38.19s | 6.79s | 178 |
| grok-3 | 22.64s | 18.94s | 42.16s | 85.70s | 17.62s | 159 |
| deepseek-reasoner | 25.72s | 30.92s | 35.30s | 37.53s | 9.15s | 140 |
| deepseek-chat | 8.62s | 7.78s | 15.65s | 19.50s | 3.77s | 418 |
| gpt-4o | 10.88s | 10.12s | 18.13s | 27.52s | 4.48s | 331 |
| claude-sonnet-4 | 20.78s | 21.15s | 28.10s | 29.28s | 5.29s | 173 |
| gemini-2.0-flash | 0.00s | 0.00s | 0.00s | 0.00s | 0.00s | 0 |
| gpt-5-mini | 8.86s | 8.45s | 11.56s | 22.42s | 3.80s | 406 |
| gpt-4o-mini | 14.47s | 13.51s | 24.46s | 35.78s | 5.34s | 249 |
| gemini-2.5-flash-lite | 5.61s | 5.72s | 6.85s | 7.31s | 0.97s | 641 |
| gemini-2.0-flash-lite | 14.13s | 14.13s | 14.13s | 14.13s | 0.00s | 255 |
| grok-3-mini | 12.63s | 11.75s | 19.41s | 26.27s | 2.88s | 285 |
| grok-code-fast-1 | 6.10s | 5.86s | 8.56s | 11.26s | 1.36s | 590 |

## Detailed Time-Sensitive Analysis

### Simple Complexity

| Model | n | Success | Acc | P95 (s) | Cost/Test |
|------|--:|--------:|----:|--------:|----------:|
| gemini-2.5-flash-lite | 1 | 100.0% | 100.0% | 6.85 | $0.00035 |
| gpt-5-mini | 1 | 100.0% | 100.0% | 8.46 | $0.00200 |
| claude-sonnet-4 | 1 | 100.0% | 100.0% | 14.80 | $0.01156 |
| gpt-4o-mini | 1 | 100.0% | 100.0% | 15.64 | $0.00051 |
| claude-opus-4 | 1 | 100.0% | 100.0% | 16.98 | $0.07105 |
| gpt-4o | 1 | 100.0% | 100.0% | 17.79 | $0.00792 |
| grok-code-fast-1 | 1 | 100.0% | 80.0% | 5.85 | $0.00069 |
| deepseek-reasoner | 1 | 100.0% | 80.0% | 15.36 | $0.00067 |
| grok-3 | 2 | 100.0% | 80.0% | 17.49 | $0.01200 |
| deepseek-chat | 2 | 100.0% | 60.0% | 5.36 | $0.00003 |
| grok-3-mini | 1 | 100.0% | 40.0% | 11.03 | $0.00011 |
| gpt-5 | 1 | 100.0% | 40.0% | 14.41 | $0.00829 |
| grok-4 | 1 | 100.0% | 40.0% | 19.12 | $0.00891 |
| gemini-2.5-flash | 1 | 0.0% | 0.0% | 0.00 | $0.00000 |
| gemini-2.0-flash | 1 | 0.0% | 0.0% | 0.00 | $0.00000 |
| gemini-2.0-flash-lite | 1 | 0.0% | 0.0% | 0.00 | $0.00000 |

### Moderate Complexity

| Model | n | Success | Acc | P95 (s) | Cost/Test |
|------|--:|--------:|----:|--------:|----------:|

### High Complexity

| Model | n | Success | Acc | P95 (s) | Cost/Test |
|------|--:|--------:|----:|--------:|----------:|

## Gates & Readiness (per-use-case)

**RAPID_RESPONSE Gate:** Acc ≥ 70%, Success ≥ 95%, P95 ≤ 20s, Cost/Test ≤ $0.0020  
**IN_DEPTH Gate:** Acc ≥ 75%, Success ≥ 97%, P95 ≤ 45s

| Model | Rapid Response | Margin | In-Depth | Margin |
|------|:--------------:|:------:|:--------:|:------:|
| gpt-5 | acc❌ p95❌ cost❌ | acc -30.5%, p95 -2.8s, cost -0.00589 | ❌ | acc -35.5% |
| claude-opus-4 | acc✅ p95❌ cost❌ | acc +2.7%, p95 -8.8s, cost -0.10288 | ❌ | acc -2.3% |
| gemini-2.5-flash | acc❌ p95✅ cost✅ | acc -64.5%, p95 +5.4s, cost +0.00199 | ❌ | acc -69.5% |
| grok-4 | acc❌ p95❌ cost❌ | acc -27.8%, p95 -11.8s, cost -0.00593 | ❌ | acc -32.8% |
| grok-3 | acc❌ p95❌ cost❌ | acc -4.3%, p95 -22.2s, cost -0.01009 | ❌ | acc -9.3% |
| deepseek-reasoner | acc❌ p95❌ cost✅ | acc -40.5%, p95 -15.3s, cost +0.00063 | ❌ | acc -45.5% |
| deepseek-chat | acc❌ p95✅ cost✅ | acc -23.0%, p95 +4.4s, cost +0.00193 | ❌ | acc -28.0% |
| gpt-4o | acc❌ p95✅ cost❌ | acc -3.6%, p95 +1.9s, cost -0.00505 | ❌ | acc -8.6% |
| claude-sonnet-4 | acc✅ p95❌ cost❌ | acc +1.4%, p95 -8.1s, cost -0.01913 | ❌ | acc -3.6% |
| gemini-2.0-flash | acc❌ p95✅ cost✅ | acc -70.0%, p95 +20.0s, cost +0.00200 | ❌ | acc -75.0% |
| gpt-5-mini | acc❌ p95✅ cost❌ | acc -18.0%, p95 +8.4s, cost -0.00017 | ❌ | acc -23.0% |
| gpt-4o-mini | acc❌ p95❌ cost✅ | acc -3.8%, p95 -4.5s, cost +0.00148 | ❌ | acc -8.8% |
| gemini-2.5-flash-lite | ✅ | acc +1.3%, p95 +13.1s, cost +0.00168 | ❌ | acc -3.7% |
| gemini-2.0-flash-lite | acc❌ p95✅ cost✅ | acc -69.7%, p95 +5.9s, cost +0.00200 | ❌ | acc -74.7% |
| grok-3-mini | acc❌ p95✅ cost✅ | acc -52.5%, p95 +0.6s, cost +0.00186 | ❌ | acc -57.5% |
| grok-code-fast-1 | acc❌ p95✅ cost✅ | acc -27.3%, p95 +11.4s, cost +0.00138 | ❌ | acc -32.3% |

## Cost & Token Utilization

| Model | Total Cost | Cost/Test | Cost/Correct (Acc≥0.8) | Token Efficiency (Acc/AvgTokens) |
|------|-----------:|----------:|-----------------------:|----------------------------------:|
| deepseek-chat | $0.0311 | $0.00007 | $0.00049 | 0.001173 |
| gemini-2.5-flash | $0.0028 | $0.00001 | $0.00056 | 0.001058 |
| gemini-2.5-flash-lite | $0.0684 | $0.00032 | $0.00074 | 0.000300 |
| gpt-4o-mini | $0.1104 | $0.00052 | $0.00131 | 0.000618 |
| grok-code-fast-1 | $0.1301 | $0.00062 | $0.00465 | 0.000530 |
| grok-3-mini | $0.0291 | $0.00014 | $0.00582 | 0.000460 |
| gpt-5-mini | $0.4571 | $0.00217 | $0.01063 | 0.000703 |
| gpt-4o | $1.4866 | $0.00705 | $0.01709 | 0.000735 |
| deepseek-reasoner | $0.2891 | $0.00137 | $0.02628 | 0.000354 |
| grok-3 | $5.1005 | $0.01209 | $0.03188 | 0.000646 |
| grok-4 | $1.6722 | $0.00793 | $0.04401 | 0.000330 |
| claude-sonnet-4 | $4.4582 | $0.02113 | $0.04794 | 0.000427 |
| gpt-5 | $1.6656 | $0.00789 | $0.06169 | 0.000530 |
| claude-opus-4 | $22.1299 | $0.10488 | $0.22130 | 0.000438 |
| gemini-2.0-flash | $0.0000 | $0.00000 | $inf | 0.000000 |
| gemini-2.0-flash-lite | $0.0003 | $0.00000 | $inf | 0.000284 |

## Methodology Notes
- **Success** = non-error response (schema-valid)  
- **Accuracy** = normalized score [0..1] consistently calculated across all results
- **Latency** = end-to-end elapsed_s per request  
- **CIs**: Wilson (proportions), Bootstrap (means, deterministic seed)
- **Throughput** reported as theoretical per worker (no concurrency factor)

**Sample Size Adequacy**
- Rapid Response recommended n ≥ 30 per model
- In-Depth recommended n ≥ 50 per model

## Deployment Recommendations
- **Rapid path**: Choose models meeting RAPID_RESPONSE gates; implement response caching; pre-tokenize common patterns
- **In-depth**: Choose highest accuracy models for batch processing; implement RAG on repo indexes; schedule weekly drift monitoring
- **Cost optimization**: Consider a low-cost, high-throughput model for high-volume, lower-criticality screening
- **Ops**: Pin model versions; implement circuit breakers; monitor P95 latency closely

---
Generated by the Rapticore Technical Analysis Engine.
