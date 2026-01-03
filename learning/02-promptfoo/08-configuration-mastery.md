# Building Block 6: Configuration Mastery - Advanced YAML Techniques

## 🔍 Let's Investigate: Beyond Basic Configs

You've mastered basic `promptfooconfig.yaml` files. But what if you need to:
- Test 50 prompts against 1000 scenarios?
- Share test configurations across teams?
- Dynamically generate test cases from databases?
- Apply conditional logic to tests?
- Manage secrets securely?

This is where **configuration mastery** transforms you from user to power user.

---

## 🧠 Theory: Configuration as Code

### Philosophy

Your `promptfooconfig.yaml` is not just a config file - it's **infrastructure as code** for LLM testing.

**Principles**:
1. **DRY (Don't Repeat Yourself)**: Reuse test definitions
2. **Modularity**: Split large configs into manageable files
3. **Version Control**: Track changes over time
4. **Environment Agnostic**: Works locally and in CI/CD

---

## 📁 File Organization Strategies

### Pattern 1: Flat Structure (Small Projects)

```
project/
├── promptfooconfig.yaml
├── prompts/
│   └── main.txt
└── tests/
    └── basic.csv
```

**Use when**: Simple projects, single team, < 50 tests.

---

### Pattern 2: Modular Structure (Recommended)

```
project/
├── promptfooconfig.yaml        # Main orchestrator
├── prompts/
│   ├── v1-formal.txt
│   ├── v2-friendly.txt
│   └── v3-balanced.txt
├── tests/
│   ├── smoke-tests.yaml        # Quick sanity checks
│   ├── regression-tests.yaml   # Full test suite
│   ├── security-tests.yaml     # Red team scenarios
│   └── data/
│       ├── personas.csv
│       └── edge-cases.csv
├── assertions/
│   ├── common-assertions.yaml  # Reusable assertion sets
│   └── validators/
│       ├── check_json.py
│       └── check_sql.py
└── providers/
    └── provider-configs.yaml   # Model configurations
```

**Use when**: Team projects, > 50 tests, CI/CD integration.

---

### Pattern 3: Multi-Environment Setup

```
project/
├── configs/
│   ├── dev.yaml               # Development settings
│   ├── staging.yaml           # Pre-production
│   └── prod.yaml              # Production (limited tests)
├── prompts/
├── tests/
└── .env.example               # Template for secrets
```

**Run with**:
```bash
promptfoo eval -c configs/dev.yaml
promptfoo eval -c configs/prod.yaml
```

---

## 🎯 Advanced YAML Features

### 1. YAML Anchors and Aliases (DRY Magic)

**Problem**: Repeating the same assertions 20 times.

**Solution**: Use YAML anchors (`&name`) and aliases (`*name`).

```yaml
# Define once
common-assertions: &common_checks
  - type: contains
    value: "processed"
  - type: latency
    threshold: 2000
  - type: cost
    threshold: 0.01

# Reuse everywhere
tests:
  - description: "Test 1"
    vars: {...}
    assert: *common_checks
  
  - description: "Test 2"
    vars: {...}
    assert: *common_checks
```

---

### 2. Default Test Configuration

**Avoid duplication** by setting defaults:

```yaml
# These apply to ALL tests unless overridden
defaultTest:
  options:
    provider: openai:gpt-4
    
  assert:
    - type: not-contains
      value: ["error", "failed", "undefined"]
    - type: latency
      threshold: 3000

# Individual tests inherit defaults
tests:
  - vars:
      query: "What's the weather?"
    # Automatically gets the defaultTest assertions
  
  - vars:
      query: "Book a flight"
    # Can override defaults
    options:
      provider: anthropic:claude-3-opus
```

---

### 3. Loading Tests from External Files

**Centralize test cases**:

```yaml
# promptfooconfig.yaml
tests:
  - file://tests/smoke-tests.yaml
  - file://tests/regression-tests.yaml
  - file://tests/security-tests.yaml
```

`tests/smoke-tests.yaml`:
```yaml
- description: "Quick check - model responds"
  vars:
    input: "Hello"
  assert:
    - type: is-json

- description: "Quick check - fast response"
  vars:
    input: "Test"
  assert:
    - type: latency
      threshold: 1000
```

---

### 4. CSV Integration for Large Test Sets

**For 1000+ test cases**, use CSV:

`tests/customer-scenarios.csv`:
```csv
customer_type,query,must_contain,must_not_contain
VIP,refund request,expedited,standard
Free,upgrade inquiry,benefits,guaranteed
Angry,complaint,understand,"unfortunately"
Technical,API question,documentation,upgrade
```

**Configuration**:
```yaml
tests:
  - vars:
      file: tests/customer-scenarios.csv
    assert:
      - type: contains
        value: "{{must_contain}}"
      - type: not-contains
        value: "{{must_not_contain}}"
```

**Result**: Automatically creates tests for each CSV row!

---

## 🔧 Variable Management

### Environment Variables

**Access secrets securely**:

```yaml
providers:
  - id: openai:gpt-4
    config:
      apiKey: ${OPENAI_API_KEY}  # From environment
      
tests:
  - vars:
      api_endpoint: ${API_ENDPOINT}
      user_id: ${TEST_USER_ID}
```

---

### Variable Composition

**Build complex variables from simple ones**:

```yaml
tests:
  - vars:
      first_name: "Alice"
      last_name: "Johnson"
      # Composed variable
      full_name: "{{first_name}} {{last_name}}"
      greeting: "Hello {{full_name}}, welcome!"
```

---

### Nunjucks Templates (Advanced)

**Use programming logic in variables**:

```yaml
tests:
  - vars:
      items: ["apple", "banana", "cherry"]
      # Use Nunjucks for loops
      itemList: |
        {% for item in items %}
        - {{ item }}
        {% endfor %}
```

**Conditional logic**:
```yaml
vars:
  user_type: "premium"
  greeting: >
    {% if user_type == "premium" %}
      Welcome back, valued customer!
    {% else %}
      Hello!
    {% endif %}
```

---

## 🎨 Provider Configurations

### Multi-Provider Testing

```yaml
providers:
  - id: gpt4
    label: "OpenAI GPT-4"
    config:
      provider: openai:gpt-4
      temperature: 0.7
      max_tokens: 500
  
  - id: claude
    label: "Anthropic Claude"
    config:
      provider: anthropic:claude-3-opus
      temperature: 0.7
      max_tokens: 500
  
  - id: budget_option
    label: "Cost Effective"
    config:
      provider: openai:gpt-3.5-turbo
      temperature: 0.5
```

**Automatic comparison** across all providers!

---

### Provider from External File

`providers/production-models.yaml`:
```yaml
- id: prod_model
  config:
    provider: openai:gpt-4-turbo
    temperature: 0.3  # Conservative for production
    max_tokens: 300
    presence_penalty: 0.1
```

**Load it**:
```yaml
providers:
  - file://providers/production-models.yaml
```

---

## 📊 Named Metrics and Derived Scores

### Define Custom Metrics

```yaml
# Create reusable metric definitions
metrics:
  - name: "compliance_score"
    assert:
      - type: not-contains
        weight: 0.4
        value: ["guarantee", "risk-free"]
      - type: llm-rubric
        weight: 0.6
        value: "Refuses to give financial advice"
  
  - name: "quality_score"
    assert:
      - type: answer-relevance
        weight: 0.5
      - type: factuality
        weight: 0.5

# Use metrics in tests
tests:
  - vars: {...}
    metric: compliance_score
```

---

### Derived Metrics (Mathematical Combinations)

```yaml
derivedMetrics:
  - name: "f1_score"
    value: "2 * (precision * recall) / (precision + recall)"
```

---

## 🧪 Transform Functions

### Output Transformation

**Clean LLM output before assertion**:

```yaml
tests:
  - vars:
      query: "Generate JSON"
    
    # Transform output before testing
    transform: |
      # Extract JSON from markdown code block
      output.split('```json')[1].split('```')[0].strip()
    
    assert:
      - type: is-json
```

**Python transformation**:
```yaml
transform: file://transforms/clean_output.py
```

`transforms/clean_output.py`:
```python
def transform(output, context):
    # Remove markdown formatting
    import re
    cleaned = re.sub(r'```.*?```', '', output, flags=re.DOTALL)
    return cleaned.strip()
```

---

### Input Transformation

**Modify variables before they reach the prompt**:

```yaml
tests:
  - vars:
      user_input: "HELLO WORLD"
    
    # Convert to lowercase before sending to prompt
    transformVars:
      user_input: "user_input.lower()"
```

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets

**.gitignore**:
```gitignore
.env
.env.*
**/api-keys.yaml
promptfoo-cache/
```

### 2. Use Environment Variables

**.env.example** (commit this):
```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=postgresql://...
```

**.env** (do NOT commit):
```bash
OPENAI_API_KEY=sk-actual-secret-key
ANTHROPIC_API_KEY=sk-ant-actual-key
DATABASE_URL=postgresql://prod-server...
```

### 3. Separate Configs by Environment

```yaml
# dev.yaml - uses cheap models
providers:
  - openai:gpt-3.5-turbo

# prod.yaml - uses best models
providers:
  - openai:gpt-4-turbo
```

---

## 💡 Real-World Pattern: The "Test Matrix Factory"

### The Challenge

You need to test:
- 10 prompt variations
- 5 user personas
- 20 scenarios
- 3 models

**Total**: 10 × 5 × 20 × 3 = **3000 test combinations**

**Solution**: Dynamic generation with CSV + anchors.

`personas.csv`:
```csv
persona_name,tone_instruction
VIP,extremely polite and attentive
Angry,calm and de-escalating
Technical,precise and jargon-appropriate
```

`scenarios.csv`:
```csv
category,scenario
refund,I want my money back
technical,The app crashed
inquiry,What are your hours?
```

**Config**:
```yaml
# Anchor for common assertions
common: &assertions
  - type: llm-rubric
    value: "Tone matches {{tone_instruction}}"
  - type: latency
    threshold: 3000

# Load prompts
prompts: file://prompts/*.txt

# Load models
providers: file://providers/all-models.yaml

# Generate matrix
tests:
  - vars:
      persona: file://personas.csv
      scenario: file://scenarios.csv
    assert: *assertions
```

**Result**: Automatic explosion into 3000 tests!

---

## ✅ What You've Achieved

You now master:

✅ **File organization** for scalable projects
✅ **YAML anchors** to eliminate repetition
✅ **Default configurations** for consistency
✅ **CSV integration** for massive test sets
✅ **Variable composition** and Nunjucks templating
✅ **Multi-provider** management
✅ **Transform functions** for data cleaning
✅ **Security practices** for secrets management

---

## 🚦 Next Steps

- **[Next: CI/CD Integration](./09-ci-cd-integration.md)** - Automate in pipelines
- **[Building Block 8: Real Examples](./10-real-world-examples.md)** - See it all together
- **[Summary](./11-summary-achievements.md)** - Reflect on your journey

---

*"Great configuration is invisible. It just works, scales, and adapts."*
