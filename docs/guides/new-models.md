# 🤖 New Model Support Guide

## Overview

The LLM Security Benchmark now supports additional model providers:

- **🚀 X.AI Grok Models** - Advanced reasoning capabilities
- **🧠 DeepSeek Models** - Powerful code analysis models  
- **🦙 Meta Llama Models** - Open-source foundation models
- **🏠 Ollama Local Models** - Run models locally without API costs

## 🎯 Model Categories

### 🏆 Premium Models (Highest Accuracy)
- `grok-4` - X.AI's flagship model (most intelligent)
- `deepseek-reasoner` - DeepSeek V3.1 with advanced reasoning/thinking mode  
- `llama-3.3-70b` - Large parameter Llama model

### ⚖️ Balanced Models (Speed + Accuracy)
- `grok-3` - Standard Grok model
- `deepseek-chat` - DeepSeek V3.1 non-thinking mode (fast & accurate)
- `llama-3.3-70b` - Balanced Llama model

### ⚡ Fast Models (Cost-Effective)  
- `grok-3-mini` - Faster Grok variant
- `grok-code-fast-1` - Code-optimized fast model
- `llama-3.3-11b` - Smaller Llama model

### 🏠 Local Models (Zero Cost)
- `ollama/llama3.3` - Local Llama via Ollama
- `ollama/deepseek-r1` - Local DeepSeek reasoning
- `ollama/qwen2.5` - Qwen2.5 local model
- `ollama/gemma2` - Google Gemma local model
- `ollama/mistral` - Mistral local model

## 🔧 Setup Instructions

### X.AI Grok Setup

1. **Get API Key:**
   - Visit [X.AI Console](https://console.x.ai/)
   - Sign up or log in
   - Create a new API key

2. **Configure Environment:**
   ```bash
   # Add to .env file
   XAI_API_KEY=xai-your_api_key_here
   ```

3. **Test Connection:**
   ```bash
   python3 run_llm_benchmark.py --models grok-4 --suite fast
   ```

### DeepSeek Setup

1. **Get API Key:**
   - Visit [DeepSeek Platform](https://platform.deepseek.com/)
   - Create account and generate API key

2. **Configure Environment:**
   ```bash
   # Add to .env file
   DEEPSEEK_API_KEY=sk-your_deepseek_key_here
   ```

3. **Test Connection:**
   ```bash
   # Test non-thinking mode (faster, cheaper)
   python3 run_llm_benchmark.py --models deepseek-chat --suite fast --timeout 45
   
   # Test thinking mode (advanced reasoning)
   python3 run_llm_benchmark.py --models deepseek-reasoner --suite fast --timeout 45
   ```

4. **Model Details:**
   - **deepseek-chat**: DeepSeek V3.1 non-thinking mode - faster responses
   - **deepseek-reasoner**: DeepSeek V3.1 thinking mode - shows reasoning process

### Meta Llama Setup

1. **Choose Provider:**
   - **Anyscale**: https://console.anyscale.com/
   - **Fireworks AI**: https://fireworks.ai/
   - **Other OpenAI-compatible providers**

2. **Configure Environment:**
   ```bash
   # Add to .env file
   LLAMA_API_KEY=your_provider_api_key_here
   LLAMA_BASE_URL=https://api.your-provider.com/v1  # Configure based on your provider
   ```

3. **Test Connection:**
   ```bash
   python3 run_llm_benchmark.py --models llama-3.3-70b --suite fast
   ```

### Ollama Local Setup

1. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows: Download from https://ollama.com/download
   ```

2. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

3. **Pull Models:**
   ```bash
   # Popular security-focused models
   ollama pull llama3.3
   ollama pull deepseek-r1  
   ollama pull qwen2.5
   ollama pull gemma2
   ollama pull mistral
   ```

4. **Configure Environment (Optional):**
   ```bash
   # Add to .env file - only if using non-default URL
   OLLAMA_BASE_URL=http://localhost:11434  # Default value
   ```

5. **Test Connection:**
   ```bash
   python3 run_llm_benchmark.py --models ollama/llama3.3 --suite fast
   ```

## 🚀 Usage Examples

### Quick Model Category Tests
```bash
# Test all new model categories
python3 run_llm_benchmark.py --models premium --suite fast

# Test only local models (no API costs)
python3 run_llm_benchmark.py --models local --suite basic

# Test specific new models
python3 run_llm_benchmark.py --models grok-beta,deepseek-v3,llama-3.3-70b --suite fast
```

### Local Model Benchmarks
```bash
# Ultra-fast local testing (no API costs)
python3 run_llm_benchmark.py --models ollama/llama3.3,ollama/deepseek-r1 --suite fast

# Comprehensive local analysis
python3 run_llm_benchmark.py --models local --suite comprehensive --timeout 30

# Compare local vs API models
python3 run_llm_benchmark.py --models gpt-4o-mini,ollama/llama3.3 --suite basic
```

### Advanced Configurations
```bash
# High-timeout for local models
python3 run_llm_benchmark.py --models local --suite comprehensive --timeout 60

# Mixed API and local models
python3 run_llm_benchmark.py --models gpt-4o-mini,claude-sonnet-4,ollama/llama3.3,deepseek-v3 --suite fast

# Cost comparison (free vs paid)
python3 run_llm_benchmark.py --models ollama/llama3.3,gpt-4o-mini --suite basic --show-responses
```

## 💰 Cost Analysis

### API Model Costs (per 1M tokens)
| Model | Input Cost | Output Cost | Context | Notes |
|-------|------------|-------------|---------|-------|
| `grok-4` | $3.00 | $15.00 | 256K | Premium X.AI model |
| `grok-3` | $3.00 | $15.00 | 131K | Standard X.AI model |
| `grok-3-mini` | $0.30 | $0.50 | 131K | Fast X.AI model |
| `grok-code-fast-1` | $0.20 | $1.50 | 256K | Code-optimized |
| `deepseek-chat` | $0.14 | $0.28 | 32K | V3.1 non-thinking mode |
| `deepseek-reasoner` | $0.55 | $2.19 | 32K | V3.1 thinking mode (shows reasoning) |
| `llama-3.3-70b` | $0.90 | $0.90 | - | Via Together AI |

### Local Model Costs
| Model | Cost | Notes |
|-------|------|-------|
| All `ollama/*` models | $0.00 | Completely free after download |

## 🎯 Model Selection Guide

### For Security Analysis

**🏆 Highest Accuracy:**
1. `grok-4` - Most intelligent model worldwide
2. `deepseek-reasoner` - Advanced reasoning with thinking process
3. `claude-opus-4` - Proven security expertise

**💰 Best Value:**
1. `deepseek-chat` - Excellent security analysis at ultra-low cost ($0.14/$0.28)
2. `gpt-4o-mini` - Reliable and affordable
3. `ollama/deepseek-r1` - Free local alternative

**⚡ Fastest:**
1. `grok-code-fast-1` - Optimized for code analysis
2. `ollama/gemma2` - Very fast local model
3. `gpt-4o-mini` - Fast and reliable

### For Different Use Cases

**🔬 Research & Development:**
```bash
# Free experimentation
python3 run_llm_benchmark.py --models local --suite comprehensive
```

**🏢 Production Security Scanning:**
```bash  
# High accuracy with cost control
python3 run_llm_benchmark.py --models deepseek-v3,grok-4 --suite comprehensive
```

**🚀 CI/CD Integration:**
```bash
# Fast, reliable, low cost
python3 run_llm_benchmark.py --models deepseek-chat,gpt-4o-mini --suite fast
```

**🎓 Educational/Learning:**
```bash
# Free local models with detailed analysis
python3 run_llm_benchmark.py --models local --suite basic --show-responses --response-format full
```

## 🔧 Troubleshooting

### X.AI Grok Issues

**❌ "XAI client not initialized"**
```bash
# Check API key is set
echo $XAI_API_KEY
# Verify .env file
cat .env | grep XAI_API_KEY
```

### DeepSeek Issues

**❌ "DeepSeek client not initialized"**
```bash
# Verify API key format
echo $DEEPSEEK_API_KEY | grep "sk-"
# Test API access
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/v1/models
```

### Llama Issues

**❌ "Llama client not initialized"**
```bash
# Check provider configuration
echo $LLAMA_BASE_URL
echo $LLAMA_API_KEY

# Try different provider
export LLAMA_BASE_URL=https://api.fireworks.ai/inference/v1
```

### Ollama Issues

**❌ "Ollama not available"**
```bash
# Check Ollama is running
ollama list
curl http://localhost:11434/api/version

# Start Ollama if needed
ollama serve

# Check model availability
ollama list | grep llama3.3
```

**❌ "Model not available"**
```bash
# Pull missing model
ollama pull llama3.3
ollama pull deepseek-r1

# List available models
ollama list
```

## 📊 Performance Expectations

### Response Times
- **Grok/DeepSeek/Llama APIs:** 2-8 seconds
- **Local Ollama models:** 5-30 seconds (depends on hardware)

### Accuracy Levels
- **Grok Beta:** Excellent (comparable to GPT-5)
- **DeepSeek V3:** Excellent for code analysis
- **Llama 3.3 70B:** Very good overall
- **Local models:** Good (varies by model size)

### Hardware Requirements for Ollama
- **Minimum:** 8GB RAM, any CPU
- **Recommended:** 16GB+ RAM, GPU optional
- **Optimal:** 32GB+ RAM, NVIDIA GPU with CUDA

## 🎯 Best Practices

1. **Start with free local models** for testing and development
2. **Use DeepSeek for cost-effective API analysis** 
3. **Reserve Grok for critical security assessments**
4. **Run comprehensive suites with local models** to avoid API costs
5. **Mix local and API models** for cost-performance balance

---

**🛡️ Built by the Rapticore Security Research Team**

*Now supporting the full spectrum of AI models - from local to premium cloud services!*