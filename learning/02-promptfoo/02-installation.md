# Installation & Setup

## 📦 Prerequisites

Before we begin, ensure you have:

### System Requirements
- **Node.js** 18+ or **Python** 3.9+
- **Terminal/Command Line** access
- **Text Editor** (VS Code recommended)
- **API Keys** for at least one LLM provider

### Recommended: Node.js Installation

Promptfoo is primarily distributed as an npm package. If you don't have Node.js:

**macOS/Linux:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

**Windows:**
Download from [nodejs.org](https://nodejs.org/)

---

## 🎯 Installation Methods

### Method 1: NPX (Quickest - No Installation)

The fastest way to try Promptfoo without installing:

```bash
npx promptfoo@latest init
```

This runs the latest version directly. Perfect for experimentation!

###Method 2: Global Install (Recommended)

Install once, use everywhere:

```bash
npm install -g promptfoo
```

Verify installation:
```bash
promptfoo --version
```

### Method 3: Project-Specific Install

For team projects where you want version consistency:

```bash
# In your project directory
npm init -y
npm install --save-dev promptfoo
```

Run via npm scripts:
```bash
npx promptfoo eval
```

### Method 4: Python (Alternative)

If you're in a Python-only environment:

```bash
pip install promptfoo
```

**Note**: The Python package is a wrapper around the Node.js version.

---

## 🔑 API Configuration

Promptfoo needs to talk to LLM providers. Let's configure API keys.

### OpenAI Setup

1. **Get API Key**: https://platform.openai.com/api-keys

2. **Set Environment Variable**:

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-..."
# Make it permanent
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
# Make it permanent
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY','sk-...','User')
```

### Anthropic Setup

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Google Gemini Setup

```bash
export GOOGLE_API_KEY="AI..."
```

### Local Models (Ollama)

No API key needed! Just install Ollama:

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull a model
ollama pull llama2
```

---

## 🚦 Quickstart: Your First Evaluation

Let's verify everything works with a 60-second test.

### Step 1: Initialize a Project

```bash
mkdir my-llm-tests
cd my-llm-tests
promptfoo init
```

This creates:
```
my-llm-tests/
├── promptfooconfig.yaml   # Main configuration
└── prompts/
    └── prompt1.txt         # Your first prompt
```

### Step 2: Examine the Config

Open `promptfooconfig.yaml`:

```yaml
prompts:
  - prompts/prompt1.txt  # The prompt file to test
  
providers:
  - openai:gpt-3.5-turbo  # The model to use

tests:
  - vars:
      question: "What's the capital of France?"
    assert:
      - type: contains
        value: "Paris"
```

**Let's understand this**:
- We're testing ONE prompt
- Using ONE model (GPT-3.5)
- With ONE test case
- Expecting the output to contain "Paris"

### Step 3: Create the Prompt

Edit `prompts/prompt1.txt`:

```
You are a helpful geography assistant.

Question: {{question}}

Provide a concise answer.
```

**Note the `{{question}}`**: This is a variable that will be replaced with test values.

### Step 4: Run the Evaluation

```bash
promptfoo eval
```

**Expected output**:
```
┌────────────────────┬─────────┐
│ Test               │ Pass/Fail│
├────────────────────┼─────────┤
│ Capital of France  │ ✅      │
└────────────────────┴─────────┘

Summary: 1/1 tests passed (100%)
```

### Step 5: View Results in UI

```bash
promptfoo view
```

This opens a web interface at `http://localhost:15500` where you can:
- See the full prompt and output
- Inspect why tests passed/failed
- Compare multiple runs

---

## 🎨 Configuration File Structure

Let's explore the YAML config in detail.

### Basic Structure

```yaml
# Which prompts to test
prompts:
  - path/to/prompt.txt
  - path/to/another.txt

# Which models to test against
providers:
  - openai:gpt-4
  - anthropic:claude-3-opus

# Test cases
tests:
  - description: "Test 1 name"
    vars:
      variable_name: "value"
    assert:
      - type: contains
        value: "expected substring"
```

### Advanced: Multiple Variables

```yaml
tests:
  - vars:
      user_type: "premium"
      request: "refund"
      amount: "$500"
    assert:
      - type: contains
        value: "approved"
  
  - vars:
      user_type: "free"
      request: "refund"
      amount: "$500"
    assert:
      - type: contains
        value: "contact support"
```

**Your prompt** (`prompts/support.txt`):
```
Customer Type: {{user_type}}
Request: {{request}} for {{amount}}

Respond according to policy.
```

---

## 🔧 Environment Setup Best Practices

### 1. Use .env Files

Create `.env`:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

**Load it** (add to `.bashrc` or use `dotenv`):
```bash
export $(cat .env | grep -v ^# | xargs)
```

### 2. Gitignore Secrets

Create `.gitignore`:
```gitignore
.env
.env.*
promptfoo-cache/
node_modules/
*.log
```

### 3. Version Control Your Config

**DO commit**:
- `promptfooconfig.yaml`
- `prompts/*.txt`
- Test cases

**DON'T commit**:
- API keys
- Cache files
- Results (unless shareable)

---

## 🧪 Verify Your Setup

Run this diagnostic to ensure everything works:

```bash
# Test OpenAI
promptfoo eval -p "Say hello" -o openai:gpt-3.5-turbo

# Test multiple providers
promptfoo eval -p "Say hello" -o openai:gpt-3.5-turbo -o anthropic:claude-3-haiku

# Test local model (if Ollama installed)
prompt foo eval -p "Say hello" -o ollama:llama2
```

**All successful?** You're ready to build real tests!

---

## 🎯 Next Steps

Now that Promptfoo is installed and configured:

- **[Building Block 1: Matrix Testing](./03-matrix-testing.md)** - Run prompts against multiple scenarios
- **[Building Block 2: Deterministic Assertions](./04-assertions-deterministic.md)** - Validate outputs with rules
- **[Building Block 3: Model-Graded Assertions](./05-assertions-model-graded.md)** - Use AI to judge AI

---

## 🆘 Troubleshooting

### Issue: `command not found: promptfoo`

**Solution**:
```bash
# Make sure global install directory is in PATH
npm config get prefix
# Add to PATH
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Issue: `API key not found`

**Solution**:
```bash
# Verify environment variable
echo $OPENAI_API_KEY
# If empty, set it again and restart terminal
```

### Issue: `Rate limit exceeded`

**Solution**:
```yaml
# In promptfooconfig.yaml, add delay between requests
providers:
  - id: openai:gpt-3.5-turbo
    config:
      delay: 1000  # 1 second between calls
```

### Issue: `Evaluation hanging`

**Solution**:
```bash
# Use cache to avoid re-running expensive calls
promptfoo eval --cache
```

---

*"A well-configured environment is half the journey. Let's start testing!"*
