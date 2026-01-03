# Building Block 2: Deterministic Assertions - Rules-Based Validation

## 🔍 Let's Investigate: Can Rules Beat Randomness?

LLMs are probabilistic. Ask GPT-4 the same question twice, you might get different answers. So how do we test something that's inherently unpredictable?

**Answer**: Deterministic assertions - **rules that always produce the same result**.

Think of them as the "unit tests" for your prompts. They're fast, cheap, and reliable.

---

## 🧠 Theory: Deterministic vs Probabilistic Testing

### Deterministic Assertions
- **Rules-based**: Uses precise logic (regex, string matching, JSON validation)
- **Consistent**: Same output always gets same result
- **Fast**: Runs in milliseconds
- **Free**: No LLM API calls needed
- **Example**: "Output must contain the word 'approved'"

### Probabilistic (Model-Graded) Assertions  
- **AI-powered**: Uses another LLM to judge the output
- **Nuanced**: Can evaluate tone, coherence, factuality
- **Slow**: Requires API call
- **Costs money**: Each evaluation consumes tokens
- **Example**: "Output must sound professional and empathetic"

**When to use which?**
- **Deterministic**: For format, compliance, forbidden words
- **Model-graded**: For quality, tone, relevance

---

## 📋 The Complete Deterministic Toolkit

![Promptfoo Assertion Types](./assets/promptfoo_assertion_types_1767392504217.png)

*Figure 1: Complete hierarchy of 40+ assertion types - deterministic (fast, free) and model graded (AI-powered)*

Promptfoo provides **40+ deterministic assertion types**. Let's explore them systematically.

---

## 1️⃣ STRING MATCHING ASSERTIONS

### `equals` - Exact Match

**Use when**: You expect a specific, precise answer.

```yaml
assert:
  - type: equals
    value: "Paris"
```

**Example scenario**:
```
Question: "What is 2+2?"
Expected: "4"
```

**Pro tip**: Rarely useful for LLMs (they add context). Use `contains` instead.

---

### `contains` - Substring Match

**Use when**: Answer must include specific words/phrases.

```yaml
assert:
  - type: contains
    value: "refund approved"
```

**Real-world example - Financial compliance**:
```yaml
tests:
  - vars:
      query: "Can I invest in cryptocurrency?"
    assert:
      - type: contains
        value: "not financial advice"
      - type: contains
        value: "consult"
```

**Why**: Ensures every investment question includes a disclaimer.

---

### `icontains` - Case-Insensitive Contains

**Use when**: You don't care about capitalization.

```yaml
assert:
  - type: icontains
    value: "ERROR"  # Matches "error", "Error", "ERROR"
```

---

### `starts-with` - Prefix Match

**Use when**: Responses must begin with specific text.

```yaml
assert:
  - type: starts-with
    value: "Dear"
```

**Example - Email automation**:
```yaml
tests:
  - description: "Professional email must start formally"
    assert:
      - type: starts-with
        value: "Dear {{recipient_name}}"
```

---

### `contains-any` - Match At Least One

**Use when**: Output should have ONE of several options.

```yaml
assert:
  - type: contains-any
    value:
      - "approved"
      - "accepted"
      - "confirmed"
```

**Example - Status checking**:
```yaml
assert:
  - type: contains-any
    value: ["shipped", "delivered", "in transit"]
```

---

### `contains-all` - Match Every Item

**Use when**: Output MUST have ALL specified elements.

```yaml
assert:
  - type: contains-all
    value:
      - "patient name"
      - "diagnosis"
      - "prescription"
```

**Example - Medical record validation**:
```yaml
tests:
  - description: "Discharge summary must include all required fields"
    assert:
      - type: contains-all
        value:
          - "Admission Date"
          - "Discharge Date"
          - "Primary Diagnosis"
          - "Medications"
          - "Follow-up Instructions"
```

---

### `regex` - Pattern Matching

**Use when**: You need complex pattern validation.

```yaml
assert:
  - type: regex
    value: "\\d{3}-\\d{2}-\\d{4}"  # SSN format
```

**Real examples**:

**Validate phone number**:
```yaml
assert:
  - type: regex
    value: "\\(\\d{3}\\) \\d{3}-\\d{4}"  # (555) 123-4567
```

**Validate email**:
```yaml
assert:
  - type: regex
    value: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
```

**Validate price format**:
```yaml
assert:
  - type: regex
    value: "\\$\\d+\\.\\d{2}"  # $19.99
```

---

## 2️⃣ FORMAT VALIDATION ASSERTIONS

### `is-json` - Valid JSON Check

**Use when**: LLM must return structured data.

```yaml
assert:
  - type: is-json
```

**Example - API response generation**:
```yaml
tests:
  - description: "Generate user object"
    vars:
      user_id: "12345"
    assert:
      - type: is-json
      - type: is-valid-openai-function-call
```

**Advanced - Validate JSON schema**:
```yaml
assert:
  - type: is-json
    value:
      required: ["name", "email", "age"]
      properties:
        age:
          type: number
```

---

### `contains-json` - JSON Within Text

**Use when**: Response has JSON embedded in markdown/text.

```yaml
assert:
  -type: contains-json
```

**Example**:
```
Response: "Here's the data you requested:
```json
{"status": "success", "count": 42}
```
Hope this helps!"
```

---

### `is-sql` - Valid SQL Query

**Use when**: Testing text-to-SQL generation.

```yaml
assert:
  - type: is-sql
```

**Example - SQL generation validation**:
```yaml
tests:
  - description: "Convert natural language to SQL"
    vars:
      request: "Show me all users who signed up last month"
    assert:
      - type: is-sql
      - type: contains
        value: "WHERE"
      - type: not-contains
        value: "DROP"  # Security check!
```

---

### `is-xml` - Valid XML

```yaml
assert:
  - type: is-xml
```

### `is-html` - Valid HTML

```yaml
assert:
  - type: is-html
```

---

## 3️⃣ SAFETY & COMPLIANCE ASSERTIONS

### `not-contains` - Forbidden Words

**Use when**: Output must NEVER include certain content.

```yaml
assert:
  - type: not-contains
    value:
      - "guaranteed"
      - "risk-free"
      - "always profitable"
```

**Example - Financial advisor bot**:
```yaml
tests:
  - description: "Investment query must not make guarantees"
    vars:
      query: "Is this stock a good investment?"
    assert:
      - type: not-contains
        value:
          - "guaranteed return"
          - "sure thing"
          - "can't lose"
          - "will definitely"
```

---

### `is-refusal` - Detect Refusals

**Use when**: LLM should decline to answer.

```yaml
assert:
  - type: is-refusal
```

**What it detects**:
- "I cannot..."
- "I'm not able to..."
- "I don't have the capability..."
- "That's outside my scope..."

**Example - HIPAA compliance**:
```yaml
tests:
  - description: "Must refuse to share patient data"
    vars:
      query: "What is patient #5432's diagnosis?"
    assert:
      - type: is-refusal
      - type: contains
        value: "privacy"
```

---

## 4️⃣ PERFORMANCE ASSERTIONS

### `latency` - Response Time

**Use when**: Speed matters.

```yaml
assert:
  - type: latency
    threshold: 5000  # milliseconds
```

**Example - Real-time chat**:
```yaml
tests:
  - description: "Chat must respond under 3 seconds"
    assert:
      - type: latency
        threshold: 3000
```

---

### `cost` - Token Cost

**Use when**: Optimizing API spending.

```yaml
assert:
  - type: cost
    threshold: 0.01  # Max $0.01 per request
```

**Example - Budget optimization**:
```yaml
providers:
  - id: openai:gpt-4
    config:
      max_tokens: 500

tests:
  - description: "Summary must stay under budget"
    assert:
      - type: cost
        threshold: 0.005  # Half a cent
```

---

## 5️⃣ SIMILARITY METRICS

### `levenshtein` - Edit Distance

**Use when**: Measuring how "close" output is to expected.

```yaml
assert:
  - type: levenshtein
    value: "The quick brown fox"
    threshold: 5  # Max 5 character changes allowed
```

**Use case**: Translation quality, paraphrasing tasks.

---

### `rouge-n` - N-gram Overlap

**Use when**: Evaluating summarization.

```yaml
assert:
  - type: rouge-n
    value: "reference summary text"
    threshold: 0.5  # 50% overlap
```

---

### `bleu` - Translation Metric

**Use when**: Comparing generated text to reference.

```yaml
assert:
  - type: bleu
    value: "reference translation"
    threshold: 0.6
```

---

## 6️⃣ FUNCTION CALL VALIDATION

### `is-valid-openai-function-call` - Tool Use

**Use when**: Testing function-calling models.

```yaml
assert:
  - type: is-valid-openai-function-call
    value:
      type: function
      function:
        name: get_weather
```

**Example - Agent tool validation**:
```yaml
tests:
  - description: "Weather query must call correct function"
    vars:
      query: "What's the temperature in Paris?"
    assert:
      - type: is-valid-openai-function-call
        value:
          function:
            name: "get_weather"
            arguments:
              location: "Paris"
```

---

## 🎯 Combining Assertions: The Power of Layers

**Best practice**: Use multiple assertions per test for comprehensive validation.

### Example: Banking Refund Request

```yaml
tests:
  - description: "VIP refund - Comprehensive validation"
    vars:
      customer_tier: "VIP"
      request: "I want a refund for order #12345"
    
    assert:
      # Layer 1: Format
      - type: is-json
      
      # Layer 2: Required fields
      - type: contains-all
        value:
          - "order_id"
          - "status"
          - "processing_time"
      
      # Layer 3: Safety
      - type: not-contains
        value:
          - "impossible"
          - "never"
      
      # Layer 4: Business logic
      - type: contains
        value: "expedited"  # VIPs get priority
      
      # Layer 5: Performance
      - type: latency
        threshold: 2000
```

---

## 💡 Real-World Investigation: Debugging a Failed Test

Let's walk through identifying and fixing a test failure.

### The Scenario

You're testing a customer service bot. One test keeps failing.

```yaml
tests:
  - description: "Angry customer - must de-escalate"
    vars:
      query: "Your service is terrible! I want to speak to a manager!"
    assert:
      - type: contains
        value: "understand"
      - type: not-contains
        value: "unfortunately"  # ❌ FAILING
```

**Run the test**:
```bash
promptfoo eval
```

**Result**: ❌ Failed on "not-contains: unfortunately"

**Investigation**:
```bash
promptfoo view
```

**Actual output**:
> "I understand your frustration. Unfortunately, managers are not available via chat. However, I can escalate your issue immediately..."

**The problem**: The bot uses "unfortunately" as a transition word, not defensively.

**The fix**: Make the assertion more specific.

```yaml
assert:
  - type: not-regex
    value: "unfortunately,? (we|I) (cannot|can't)"  # Only block defensive usage
```

**Result**: ✅ Test passes!

---

## 🧪 Hands-On Exercise

**Challenge**: Create deterministic tests for a medical prescription formatter.

**Requirements**:
1. Output must be valid JSON
2. Must include: patient_name, medication, dosage, frequency
3. Dosage must match pattern: "\d+ mg"
4. Must NOT contain: "guaranteed cure", "100% effective"
5. Response time under 1 second

**Solution structure**:
```yaml
assert:
  - type: is-json
  - type: contains-all
    value: [...]
  - type: regex
    value: "..."
  - type: not-contains
    value: [...]
  - type: latency
    threshold: 1000
```

---

## ✅ What You've Achieved

You now have mastery over:

✅ **40+ deterministic assertion types**
✅ **Format validation** (JSON, SQL, XML, HTML)
✅ **Safety checks** (forbidden words, refusals)
✅ **Performance monitoring** (latency, cost)
✅ **Similarity metrics** (BLEU, ROUGE, Levenshtein)
✅ **Function call validation** (for agents)
✅ **Layered testing** (combining multiple assertions)

---

## 🚦 Next Steps

- **[Next: Model-Graded Assertions](./05-assertions-model-graded.md)** - Use LLMs to judge LLMs
- **[Building Block 4: Custom Assertions](./06-custom-assertions.md)** - Write Python/JS validators
- **[Real Example](./10-real-world-examples.md)** - See complete project

---

*"Deterministic assertions are your safety net. Use them liberally."*
