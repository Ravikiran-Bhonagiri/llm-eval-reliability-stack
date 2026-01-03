# Installation & Setup - RAGAS

## 🔍 Let's Get Scientific: Setting Up Your RAG Lab

You're about to transform RAG development from art to science. But first, we need the right tools.

**Goal**: Get RAGAS running and verify with your first evaluation (< 30 minutes).

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10+ (3.11 recommended)
- **RAM**: 4GB minimum (8GB recommended for large documents)
- **OS**: Linux, macOS, or Windows
- **Internet**: For LLM API calls (OpenAI, Anthropic, etc.)

### Required Knowledge
✅ Basic Python (functions, classes)  
✅ RAG concepts (retrieval + generation)  
✅ One of: LangChain OR LlamaIndex (basic familiarity)  
⚠️ **Not required**: Deep ML knowledge, neural networks

---

## 🚀 Installation Methods

### Method 1: pip (Recommended - Fastest)

```bash
# Install RAGAS
pip install ragas

# Verify installation
python -c "import ragas; print(f'RAGAS {ragas.__version__} installed!')"
```

**Expected output**:
```
RAGAS 0.1.x installed!
```

---

### Method 2: pip with Specific Extras

**For LangChain users**:
```bash
pip install ragas[langchain]
```

**For LlamaIndex users**:
```bash
pip install ragas[llama-index]
```

**For all features** (test generation + all frameworks):
```bash
pip install ragas[all]
```

---

### Method 3: From Source (Latest Features)

```bash
# Clone repository
git clone https://github.com/explodinggradients/ragas.git
cd ragas

# Install in development mode
pip install -e .

# Verify
python -c "import ragas; print('Development version installed!')"
```

**When to use**: You need bleeding-edge features not yet in PyPI.

---

### Method 4: conda (For conda users)

```bash
conda create -n ragas-env python=3.11
conda activate ragas-env
pip install ragas  # Note: RAGAS itself uses pip even in conda
```

---

## 🔑 API Configuration

RAGAS needs an LLM for metric calculations. Configure your provider:

### OpenAI (Recommended for Getting Started)

```bash
# Set API key (Linux/Mac)
export OPENAI_API_KEY="sk-..."

# Or Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

**Or use `.env` file** (better for teams):

`.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-...  # Optional
```

`.gitignore`:
```
.env
```

**Load in code**:
```python
from dotenv import load_dotenv
load_dotenv()  # Automatically loads .env

import ragas
# API key loaded automatically!
```

---

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Use in RAGAS**:
```python
from ragas.llms import LangchainLLMWrapper
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-opus-20240229")
ragas_llm = LangchainLLMWrapper(llm)
```

---

### Azure OpenAI

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-key",
    api_version="2024-02-01",
    deployment_name="gpt-4"
)
```

---

### Local Models (Ollama)

**Benefits**: Free, private, no API costs

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3:8b

# Start Ollama server
ollama serve
```

**Use with RAGAS**:
```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3:8b")
# Note: Smaller models may give lower quality scores
```

---

## ✅ Quickstart: Your First Evaluation (5 Minutes)

Let's verify everything works with a minimal RAG evaluation.

### Step 1: Create Test File

`test_ragas.py`:
```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Sample RAG outputs
data = {
    "question": ["What is the capital of France?"],
    "answer": ["Paris is the capital of France."],
    "contexts": [["Paris is the capital and largest city of France."]],
    "ground_truth": ["Paris"]  # Optional for some metrics
}

# Convert to dataset format
dataset = Dataset.from_dict(data)

# Evaluate!
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy]
)

print(result)
```

### Step 2: Run It

```bash
python test_ragas.py
```

### Step 3: Expected Output

```
Evaluating: 100%|████████| 1/1 [00:03<00:00,  3.21s/it]

{
    'faithfulness': 1.0,       # Perfect! Answer grounded in context
    'answer_relevancy': 0.95   # Highly relevant to question
}
```

**✅ Success!** RAGAS is working.

---

## 🔧 Framework Integration

### LangChain Integration

**Install**:
```bash
pip install langchain langchain-openai ragas
```

**Evaluate a LangChain RAG**:
```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from ragas.integrations.langchain import evaluate_chain

# Your LangChain RAG
llm = ChatOpenAI()
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(
    ["Paris is the capital of France..."],
    embeddings
)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

# Evaluate with RAGAS
questions = ["What's the capital of France?"]
results = evaluate_chain(qa_chain, questions)
```

---

### LlamaIndex Integration

**Install**:
```bash
pip install llama-index ragas
```

**Evaluate a LlamaIndex RAG**:
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from ragas.integrations.llama_index import evaluate

# Your LlamaIndex RAG
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Evaluate with RAGAS
questions = ["What's the capital of France?"]
results = evaluate(query_engine, questions)
```

---

## 🐛 Troubleshooting Common Issues

### Issue 1: ImportError for datasets

**Error**:
```
ModuleNotFoundError: No module named 'datasets'
```

**Fix**:
```bash
pip install datasets
```

---

### Issue 2: OpenAI Rate Limits

**Error**:
```
RateLimitError: Rate limit reached
```

**Fix**:
```python
from ragas import evaluate
from ragas.run_config import RunConfig

# Slow down requests
run_config = RunConfig(max_workers=1, timeout=60)

result = evaluate(
    dataset,
    metrics=[faithfulness],
    run_config=run_config
)
```

---

### Issue 3: CUDA Out of Memory (Local Models)

**Error**:
```
torch.cuda.OutOfMemoryError
```

**Fix**: Use smaller model or CPU
```python
from langchain_community.llms import Ollama

# Use smaller model
llm = Ollama(model="llama3:7b")  # Instead of 70b

# Or force CPU
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
```

---

### Issue 4: SSL Certificate Errors

**Error**:
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Fix** (Windows/Mac):
```bash
# Mac
/Applications/Python\ 3.11/Install\ Certificates.command

# Or disable SSL verification (NOT recommended for production)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

---

## 👥 Team Collaboration Setup

### 1. Create Shared Config

`ragas_config.py`:
```python
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import os

# Shared LLM configuration
def get_ragas_llm():
    return LangchainLLMWrapper(
        ChatOpenAI(
            model="gpt-3.5-turbo",  # Cheaper for team usage
            temperature=0  # Deterministic
        )
    )

# Shared metrics
from ragas.metrics import faithfulness, answer_relevancy, context_precision

DEFAULT_METRICS = [faithfulness, answer_relevancy, context_precision]
```

---

### 2. Shared Environment Setup

`setup_team.sh`:
```bash
#!/bin/bash

# Create virtual environment
python -m venv ragas-env
source ragas-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env template
cp .env.example .env

echo "✅ Setup complete! Edit .env with your API keys"
```

`requirements.txt`:
```
ragas==0.1.9
langchain==0.1.0
langchain-openai==0.0.5
python-dotenv==1.0.0
datasets==2.16.0
```

---

### 3. Docker Setup (Advanced)

`Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

CMD ["python", "evaluate.py"]
```

`docker-compose.yml`:
```yaml
version: '3.8'
services:
  ragas:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./results:/app/results
```

**Run**:
```bash
docker-compose up
```

---

## 📊 Verification Checklist

Before proceeding, verify:

- [ ] RAGAS installed (`import ragas` works)
- [ ] API key configured (OpenAI/Anthropic/Azure)
- [ ] Quickstart test passed (faithfulness + relevancy scores generated)
- [ ] Framework integration works (LangChain OR LlamaIndex)
- [ ] Team has shared config (if applicable)

---

## 💡 Performance Tips

### 1. Use GPT-3.5 for Development

```python
# Faster and cheaper for testing
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")  # 10x cheaper than GPT-4
```

**When to use GPT-4**: Production evaluations where accuracy matters.

---

### 2. Cache LLM Results

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
# Repeated evaluations will use cache
```

---

### 3. Parallel Execution

```python
from ragas import evaluate
from ragas.run_config import RunConfig

# Use multiple workers
config = RunConfig(max_workers=4)  # 4 parallel evaluations

result = evaluate(dataset, metrics=[...], run_config=config)
```

---

## 🚦 Next Steps

Now that RAGAS is installed and verified:

- **[Next: Faithfulness Metric](./03-faithfulness.md)** - Detect hallucinations
- **[Building Block 2: Answer Relevance](./04-answer-relevance.md)** - QA quality
- **[Quick Reference](../RAGAS_QUICKREF.md)** - Cheat sheet

---

## 📚 Additional Resources

- **Official Docs**: https://docs.ragas.io
- **GitHub**: https://github.com/explodinggradients/ragas
- **Discord**: Community support
- **Research Paper**: arxiv.org/abs/2309.15217

---

*From installation to first evaluation in 30 minutes. Now you're ready to measure, not guess!* ✨
