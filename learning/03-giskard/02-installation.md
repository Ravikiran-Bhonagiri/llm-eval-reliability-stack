# Installation & Setup

## 📦 Prerequisites

Before we begin, ensure you have:

### System Requirements
- **Python** 3.9 or higher
- **pip** (Python package manager)
- **Virtual environment** (recommended)
- **API Keys** for LLM providers (OpenAI, Anthropic, etc.)

### Recommended: Virtual Environment

```bash
# Create virtual environment
python -m venv giskard-env

# Activate it
# macOS/Linux:
source giskard-env/bin/activate
# Windows:
giskard-env\Scripts\activate
```

---

## 🎯 Installation Methods

### Method 1: Standard Installation (Recommended)

Install Giskard with LLM support:

```bash
pip install "giskard[llm]"
```

**What this includes**:
- Core Giskard framework
- LLM vulnerability scanning
- RAGET (test generation)
- All necessary dependencies

### Method 2: Development Installation

For contributors or advanced users:

```bash
pip install "giskard[dev,llm]"
```

**Additional features**:
- Testing utilities
- Development tools
- Code quality checkers

### Method 3: Minimal Installation

If you only need basic features:

```bash
pip install giskard
```

**Note**: LLM features require the `[llm]` extra.

---

## 🔑 API Configuration

Giskard uses **LiteLLM** under the hood, supporting 100+ LLM providers.

### OpenAI Setup (Default)

```python
import os
import giskard

# Set API key
os.environ["OPENAI_API_KEY"] = "sk-..."

# Optional: Configure models (defaults shown)
giskard.llm.set_llm_model("openai/gpt-4o")
giskard.llm.set_embedding_model("openai/text-embedding-3-small")
```

### Anthropic Setup

```python
import os
import giskard

os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

giskard.llm.set_llm_model("anthropic/claude-3-5-sonnet")
giskard.llm.set_embedding_model("openai/text-embedding-3-small")  # Still use OpenAI for embeddings
```

### Azure OpenAI Setup

```python
import os
import giskard

os.environ["AZURE_API_KEY"] = "..."
os.environ["AZURE_API_BASE"] = "https://your-resource.openai.azure.com/"
os.environ["AZURE_API_VERSION"] = "2023-05-15"

giskard.llm.set_llm_model("azure/gpt-4")
```

### Local Models (Ollama)

```bash
# First, install and run Ollama
ollama serve

# Pull a model
ollama pull llama2
```

```python
import giskard

# No API key needed!
giskard.llm.set_llm_model("ollama/llama2")
```

---

## 🚦 Quickstart: Your First Scan

Let's verify everything works with a 60-second test.

### Step 1: Create a Simple RAG Function

```python
import pandas as pd
from giskard import Model

def simple_rag(df: pd.DataFrame) -> list[str]:
    """
    A minimal RAG function for testing.
    In production, this would call your actual RAG pipeline.
    """
    responses = []
    for question in df["question"].values:
        # Simulated RAG response
        if "ceo" in question.lower():
            response = "I cannot disclose executive information."
        else:
            response = f"Here's an answer to: {question}"
        responses.append(response)
    return responses
```

### Step 2: Wrap It as a Giskard Model

```python
giskard_model = Model(
    model=simple_rag,
    model_type="text_generation",
    name="Simple RAG Bot",
    description="A basic RAG system for testing",
    feature_names=["question"]
)
```

### Step 3: Run Security Scan

```python
import giskard

# Run the scan
scan_results = giskard.scan(giskard_model)

# Display results
display(scan_results)
```

**Expected output**:
```
Scanning model for vulnerabilities...
✓ Tested 50 attack vectors
✓ Found 3 potential issues
✓ Generated report
```

### Step 4: View the Report

```python
# Generate HTML report
scan_results.to_html("security_report.html")

# Or view in notebook
scan_results
```

---

## 🔧 Configuration Options

### Setting Custom Models

```python
import giskard

# For vulnerability scanning
giskard.llm.set_llm_model("anthropic/claude-3-opus")

# For embeddings (used in RAGET)
giskard.llm.set_embedding_model("voyage/voyage-2")

# For test generation
giskard.llm.set_default_client("openai/gpt-4-turbo")
```

### Advanced: Custom LLM Provider

If you have a custom API:

```python
import os
import requests
from typing import Optional
import litellm
import giskard

class MyCustomLLM(litellm.CustomLLM):
    def completion(self, messages: str, api_key: Optional[str] = None, **kwargs):
        api_key = api_key or os.environ.get("MY_API_KEY")
        
        response = requests.post(
            "https://my-llm-api.com/chat",
            json={"messages": messages},
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        return litellm.ModelResponse(**response.json())

# Register custom provider
os.environ["MY_API_KEY"] = "..."
my_llm = MyCustomLLM()

litellm.custom_provider_map = [
    {"provider": "my-llm", "custom_handler": my_llm}
]

# Use it
giskard.llm.set_llm_model("my-llm/my-model", api_key=os.environ["MY_API_KEY"])
```

---

## 🎨 Environment Setup Best Practices

### 1. Use Environment Files

Create `.env`:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_API_KEY=...
AZURE_API_BASE=...
```

**Load with python-dotenv**:
```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
import giskard
# API keys auto-detected!
```

### 2. Separate Test/Prod Configs

```python
import os

ENV = os.getenv("ENVIRONMENT", "dev")

if ENV == "prod":
    giskard.llm.set_llm_model("openai/gpt-4-turbo")  # Best model
else:
    giskard.llm.set_llm_model("openai/gpt-3.5-turbo")  # Cheaper for testing
```

### 3. Cost Management

```python
# Use cheaper models for scanning
giskard.llm.set_llm_model("openai/gpt-3.5-turbo")

# But best model for critical detections
# (configure per-scan if needed)
```

---

## 🧪 Verify Your Setup

Run this diagnostic to ensure everything works:

```python
import pandas as pd
from giskard import Model
import giskard

# Test function
def test_model(df: pd.DataFrame) -> list[str]:
    return ["Test response"] * len(df)

# Wrap it
model = Model(
    model=test_model,
    model_type="text_generation",
    name="Diagnostic Test",
    feature_names=["question"]
)

# Try scanning
try:
    results = giskard.scan(model)
    print("✅ Giskard is working correctly!")
    print(f"✅ Scan completed with {len(results.issues) if hasattr(results, 'issues') else 0} findings")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Check your API keys and model configuration")
```

---

## 📋 Dependencies Reference

### Core Dependencies (Auto-installed)
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `litellm` - Multi-provider LLM interface
- `pydantic` - Data validation
- `requests` - HTTP client

### Optional but Recommended
```bash
pip install jupyter  # For notebooks
pip install python-dotenv  # For .env files
pip install rich  # For beautiful terminal output
```

---

## 🆘 Troubleshooting

### Issue: `ImportError: No module named 'giskard'`

**Solution**:
```bash
# Ensure you're in the right environment
which python  # Should point to your venv

# Reinstall
pip install --upgrade "giskard[llm]"
```

### Issue: `API key not found`

**Solution**:
```python
import os

# Verify key is set
print(os.environ.get("OPENAI_API_KEY"))

# If None, set it explicitly
os.environ["OPENAI_API_KEY"] = "sk-..."
```

### Issue: `Model not found: openai/gpt-4o`

**Solution**:
```python
# Check available models
import litellm
print(litellm.model_list)

# Or use a different model
giskard.llm.set_llm_model("openai/gpt-4-turbo")
```

### Issue: `Rate limit exceeded`

**Solution**:
```python
# Configure scan to use fewer requests
scan_results = giskard.scan(
    model,
    max_issues=10,  # Limit number of tests
    only=["prompt_injection"]  # Test specific vulnerabilities
)
```

---

## 🎯 Next Steps

Now that Giskard is installed and configured:

- **[Building Block 1: Model Wrapping](./03-model-wrapping.md)** - Integrate your RAG system
- **[Building Block 2: LLM Scan](./04-llm-scan.md)** - Automated vulnerability detection
- **[Building Block 3: RAGET](./05-raget.md)** - Generate tests from documents

---

## 📚 Additional Resources

- **Official Documentation**: https://docs.giskard.ai/
- **GitHub Repository**: https://github.com/Giskard-AI/giskard
- **Community Discord**: https://discord.gg/giskard
- **Example Notebooks**: https://github.com/Giskard-AI/giskard/tree/main/examples

---

*"A well-configured environment is the foundation of effective testing. Let's start scanning!"*
