# 🚀 Speed Optimization Guide

## Quick Summary
**Original Runtime:** ~2 hours  
**Optimized Runtime:** ~20-60 seconds  
**Speed Improvement:** ~99% faster

## Performance Optimizations Applied

### 1. **Reduced Default Timeout**
- **Before:** 30 seconds per API call
- **After:** 10 seconds per API call
- **Impact:** 67% reduction in wait time for slow responses

### 2. **Faster Default Models**
- **Before:** `gpt-5`, `claude-opus-4`, `gemini-2.5-flash`, `claude-sonnet-4` (4 premium models)
- **After:** `gpt-4o-mini`, `claude-sonnet-4` (2 fast models)
- **Impact:** 50% fewer API calls, much faster responses

### 3. **Reduced Token Limits**
- **Before:** 512/768 tokens (first/retry attempts)
- **After:** 256/384 tokens (first/retry attempts)  
- **Impact:** Faster API responses, lower costs

### 4. **Concurrent Execution**
- **Before:** Sequential (one model at a time, one test at a time)
- **After:** Parallel execution with ThreadPoolExecutor (4 workers by default)
- **Impact:** Multiple API calls running simultaneously

### 5. **Fast Test Suite**
- **Before:** 11 test cases (basic suite)
- **After:** 5 essential test cases (fast suite)
- **Impact:** 55% fewer tests, focusing on critical security issues

## Usage Examples

### Ultra-Fast (10-15 seconds)
```bash
# Fast suite, single model, aggressive timeout
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini --timeout 8 --max-workers 4
```

### Balanced Speed (20-30 seconds)
```bash
# Fast suite, 2 models, default settings
python3 run_llm_benchmark.py --suite fast --models gpt-4o-mini,claude-sonnet-4
```

### Quick Quality Check (45-60 seconds)
```bash
# Basic suite with optimizations
python3 run_llm_benchmark.py --suite basic --models gpt-4o-mini,claude-sonnet-4 --timeout 8
```

### Maximum Speed Settings
```bash
# Minimal viable benchmark
python3 run_llm_benchmark.py \
    --suite fast \
    --models gpt-4o-mini \
    --timeout 5 \
    --max-workers 8 \
    --concurrent
```

## Configuration Options

### Test Suites by Size
- **fast:** 5 tests (~10-15 seconds)
- **basic:** 11 tests (~20-30 seconds)  
- **comprehensive:** 25 tests (~60-90 seconds)
- **all:** 150+ tests (~10-15 minutes with optimizations)

### Model Speed Categories
- **Fastest:** `gpt-4o-mini`, `gemini-2.0-flash-lite`
- **Fast:** `claude-sonnet-4`, `gpt-4o`
- **Slower:** `gpt-5`, `claude-opus-4`

### Concurrent Workers
- **--max-workers 1:** Sequential execution
- **--max-workers 4:** Default concurrent (recommended)
- **--max-workers 8:** Maximum concurrency (for fast models only)

## Runtime Estimates

| Configuration | Models | Tests | Workers | Timeout | Est. Time |
|---------------|---------|--------|---------|---------|-----------|
| Ultra-fast | 1 | 5 | 4 | 5s | 10-15s |
| Fast | 2 | 5 | 4 | 10s | 15-25s |
| Balanced | 2 | 11 | 4 | 10s | 25-40s |
| Comprehensive | 4 | 11 | 4 | 10s | 45-70s |
| Full suite | 6 | 25 | 4 | 15s | 3-5 min |

## Quality vs Speed Trade-offs

### What you keep with optimizations:
✅ **All enhanced reporting features** (executive summaries, graphs, analysis)  
✅ **Full security vulnerability detection**  
✅ **Cost-effectiveness calculations**  
✅ **Data export capabilities**  
✅ **Visualization charts**  

### What changes:
⚠️ **Reduced response depth** (shorter token limits)  
⚠️ **Faster timeouts** (may miss slow but thorough responses)  
⚠️ **Fewer models tested** (unless specified)  
⚠️ **Smaller test suite** (unless using comprehensive/all)  

## Reverting to Original Settings

To use original slower but more comprehensive settings:
```bash
python3 run_llm_benchmark.py \
    --suite comprehensive \
    --models premium \
    --timeout 30 \
    --max-workers 1 \
    --concurrent false
```

**Built by the Rapticore Security Research Team**