# Advanced Metrics & Custom Evaluators

## 🔍 The Investigation: When Standard Metrics Aren't Enough

You've optimized your medical Q&A RAG system using RAGAS metrics:
- Faithfulness: 0.92 ✅
- Answer Relevancy: 0.88 ✅
- Context Recall: 0.85 ✅

**But your medical reviewers say**: "These answers are technically correct but don't follow clinical communication guidelines."

**Examples they cite**:
- Answers use jargon patients won't understand
- Missing required disclaimers ("consult your doctor")
- Not respecting symptom severity urgency protocols

**The Problem**: Standard metrics don't capture domain-specific requirements.

**The Solution**: Custom RAGAS evaluators for your domain.

---

## 🧠 Theory: Building Custom Metrics

### When to Create Custom Metrics

✅ **Industry-specific requirements** (medical, legal, financial)  
✅ **Compliance needs** (HIPAA, GDPR, regulatory)  
✅ **Brand voice** requirements  
✅ **Domain expertise** not captured by general metrics  
✅ **Business-specific** quality standards  

### Types of Custom Evaluators

**1. Rule-Based** (deterministic)
```python
def check_disclaimer(answer):
    required_phrases = ["consult your doctor", "seek medical attention"]
    return any(phrase in answer.lower() for phrase in required_phrases)
```

**2. Model-Based** (LLM-powered)
```python
def evaluate_tone(answer, expected_tone="empathetic"):
    prompt = f"Does this answer have an {expected_tone} tone? {answer}"
    # Use LLM to judge
```

**3. Hybrid** (combination)
```python
def medical_quality(answer, context):
    # Rule: Must have disclaimer
    has_disclaimer = check_disclaimer(answer)
    # Model: Check medical accuracy
    is_accurate = llm_verify_medical_facts(answer, context)
    return has_disclaimer and is_accurate
```

---

## 💻 Creating Custom Metrics

### Example 1: Medical Disclaimer Checker

```python
from ragas.metrics.base import MetricWithLLM
from ragas.metrics import metric

@metric
class MedicalDisclaimerMetric(MetricWithLLM):
    """Ensures medical answers include appropriate disclaimers"""
    
    name = "medical_disclaimer"
    
    def __init__(self):
        self.required_disclaimers = [
            "consult your doctor",
            "seek medical attention",
            "talk to your healthcare provider",
            "contact your physician"
        ]
    
    def _score(self, row):
        """Score a single answer"""
        answer = row['answer'].lower()
        
        # Check for any required disclaimer
        has_disclaimer = any(
            phrase in answer 
            for phrase in self.required_disclaimers
        )
        
        return 1.0 if has_disclaimer else 0.0
    
    def _ascore(self, row):
        """Async version (optional)"""
        return self._score(row)

# Use it
from ragas import evaluate

results = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        MedicalDisclaimerMetric()  # Your custom metric
    ]
)

print(results['medical_disclaimer'])
```

---

### Example 2: Readability Score

```python
import textstat

@metric  
class ReadabilityMetric(MetricWithLLM):
    """Ensures answers are readable at appropriate grade level"""
    
    name = "readability"
    
    def __init__(self, max_grade_level=8):
        """
        max_grade_level: Maximum Flesch-Kincaid grade level
        8 = middle school (appropriate for general public)
        """
        self.max_grade_level = max_grade_level
    
    def _score(self, row):
        answer = row['answer']
        
        # Calculate Flesch-Kincaid grade level
        grade = textstat.flesch_kincaid_grade(answer)
        
        # Score: 1.0 if under threshold, else penalize
        if grade <= self.max_grade_level:
            return 1.0
        else:
            # Linear penalty for complexity
            penalty = (grade - self.max_grade_level) / 10
            return max(0, 1.0 - penalty)

# Usage
readability_metric = ReadabilityMetric(max_grade_level=8)

results = evaluate(
    dataset,
    metrics=[readability_metric]
)

print(f"Average readability: {results['readability']}")
```

---

### Example 3: Financial Compliance Metric

```python
@metric
class FinancialComplianceMetric(MetricWithLLM):
    """Ensures financial answers don't give unauthorized advice"""
    
    name = "financial_compliance"
    
    def __init__(self):
        # Forbidden phrases (regulatory)
        self.forbidden = [
            "guaranteed return",
            "risk-free",
            "sure thing",
            "can't lose",
            "will definitely"
        ]
        
        # Required disclaimers
        self.required = [
            "not financial advice",
            "consult a financial advisor"
        ]
    
    def _score(self, row):
        answer = row['answer'].lower()
        
        # Check for forbidden claims
        has_forbidden = any(phrase in answer for phrase in self.forbidden)
        
        # Check for required disclaimers
        has_disclaimer = any(phrase in answer for phrase in self.required)
        
        if has_forbidden:
            return 0.0  # Critical failure
        elif not has_disclaimer:
            return 0.5  # Warning
        else:
            return 1.0  # Compliant

# Usage
compliance = FinancialComplianceMetric()

results = evaluate(
    financial_qa_dataset,
    metrics=[compliance]
)

# Fail deployment if compliance < 0.95
assert results['financial_compliance'] > 0.95, "Compliance failure!"
```

---

## 🎯 LLM-Powered Custom Metrics

For more nuanced evaluation, use an LLM as the judge.

### Example: Empathy Score

```python
from ragas.metrics.base import MetricWithLLM
from langchain_openai import ChatOpenAI

@metric
class EmpathyMetric(MetricWithLLM):
    """Evaluates emotional tone of answers"""
    
    name = "empathy"
    
    def __init__(self, llm=None):
        if llm is None:
            llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.llm = llm
    
    def _score(self, row):
        question = row['question']
        answer = row['answer']
        
        evaluation_prompt = f"""
        Evaluate the empathy level of this answer on a scale of 0.0 to 1.0.

        Question: {question}
        Answer: {answer}

        Consider:
        - Does it acknowledge the user's concern?
        - Is the tone warm and understanding?
        - Does it show care for the user's situation?

        Respond with ONLY a number between 0.0 and 1.0.
        """
        
        response = self.llm.invoke(evaluation_prompt)
        
        try:
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except:
            return 0.5  # Default on parse error

# Usage
empathy_metric = EmpathyMetric()

results = evaluate(
    customer_support_dataset,
    metrics=[empathy_metric]
)
```

---

## 🔧 Combining Multiple Custom Metrics

### Domain-Specific Evaluation Suite

```python
# Medical RAG Complete Evaluation
medical_metrics = [
    # Standard RAGAS
    faithfulness,
    answer_relevancy,
    
    # Custom compliance
    MedicalDisclaimerMetric(),
    
    # Custom readability
    ReadabilityMetric(max_grade_level=8),
    
    # Custom tone
    EmpathyMetric()
]

# Evaluate
results = evaluate(
    medical_qa_dataset,
    metrics=medical_metrics
)

# Weighted quality score
def calculate_medical_quality_score(results):
    return {
        0.3 * results['faithfulness'] +        # Factual accuracy
        0.2 * results['answer_relevancy'] +    # Answers question
        0.3 * results['medical_disclaimer'] +  # Compliance
        0.1 * results['readability'] +         # Accessibility
        0.1 * results['empathy']               # Patient care
    }

quality_score = calculate_medical_quality_score(results)
print(f"Overall Medical Quality: {quality_score:.2f}")
```

---

## 📊 Real-World Custom Metrics

### 1. Legal Citation Accuracy

```python
import re

@metric
class LegalCitationMetric(MetricWithLLM):
    """Verifies legal citations are properly formatted"""
    
    name = "legal_citation"
    
    def _score(self, row):
        answer = row['answer']
        
        # Pattern: Case Name, Volume Reporter Page (Court Year)
        # e.g., "Brown v. Board of Education, 347 U.S. 483 (1954)"
        citation_pattern = r'\d+\s+[A-Z\.]+\s+\d+\s+\(\d{4}\)'
        
        citations = re.findall(citation_pattern, answer)
        
        if not citations:
            # Check if answer claims to cite cases
            if 'court' in answer.lower() or 'case' in answer.lower():
                return 0.0  # Claims cases but no proper citations
            return 1.0  # No citations needed
        
        # Verify citations are in context
        for cite in citations:
            # Check if referenced in the contexts
            found_in_context = any(
                cite in context 
                for context in row['contexts']
            )
            if not found_in_context:
                return 0.0  # Fake citation!
        
        return 1.0  # All citations verified
```

---

### 2. Brand Voice Consistency

```python
@metric
class BrandVoiceMetric(MetricWithLLM):
    """Ensures answers match company brand voice"""
    
    name = "brand_voice"
    
    def __init__(self, brand_guidelines, llm=None):
        """
        brand_guidelines: Dict with tone, forbidden words, etc.
        """
        self.guidelines = brand_guidelines
        if llm is None:
            llm = ChatOpenAI(model="gpt-4")
        self.llm = llm
    
    def _score(self, row):
        answer = row['answer']
        
        # Check forbidden words
        forbidden = self.guidelines.get('forbidden_words', [])
        if any(word.lower() in answer.lower() for word in forbidden):
            return 0.0
        
        # Check required elements
        required = self.guidelines.get('required_elements', [])
        has_all_required = all(
            elem.lower() in answer.lower() 
            for elem in required
        )
        
        if not has_all_required:
            return 0.5
        
        # LLM check for tone
        tone = self.guidelines.get('tone', 'professional')
        prompt = f"""
        Does this answer match a {tone} brand voice?
        
        Answer: {answer}
        
        Rate 0.0-1.0:
        """
        
        response = self.llm.invoke(prompt)
        
        try:
            tone_score = float(response.content.strip())
            return tone_score
        except:
            return 0.7  # Default

# Usage
brand_guidelines = {
    'tone': 'friendly and helpful',
    'forbidden_words': ['unfortunately', 'impossible', 'never'],
    'required_elements': []  # e.g., ['Let us help']
}

brand_metric = BrandVoiceMetric(brand_guidelines)
```

---

### 3. Code Quality Metric (for tech docs)

```python
@metric
class CodeQualityMetric(MetricWithLLM):
    """Evaluates code examples in answers"""
    
    name = "code_quality"
    
    def _score(self, row):
        answer = row['answer']
        
        # Extract code blocks
        import re
        code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', answer, re.DOTALL)
        
        if not code_blocks:
            # No code to evaluate
            return 1.0
        
        score = 0
        for code in code_blocks:
            # Basic checks
            checks = {
                'has_comments': '#' in code,
                'has_docstring': '"""' in code or "'''" in code,
                'proper_naming': not re.search(r'\bx\b|\by\b|\bvar\b', code),
                'no_syntax_error': self._check_syntax(code)
            }
            
            block_score = sum(checks.values()) / len(checks)
            score += block_score
        
        return score / len(code_blocks)
    
    def _check_syntax(self, code):
        try:
            compile(code, '<string>', 'exec')
            return True
        except:
            return False
```

---

## 🧪 Testing Custom Metrics

### Unit Testing Your Metrics

```python
import pytest

def test_medical_disclaimer_metric():
    metric = MedicalDisclaimerMetric()
    
    # Test case: Has disclaimer
    row_with = {
        'answer': "Take tylenol for headaches. Consult your doctor if pain persists."
    }
    assert metric._score(row_with) == 1.0
    
    # Test case: No disclaimer
    row_without = {
        'answer': "Take tylenol for headaches."
    }
    assert metric._score(row_without) == 0.0
    
    print("✅ Medical disclaimer metric tests passed")

def test_readability_metric():
    metric = ReadabilityMetric(max_grade_level=8)
    
    # Simple text (grade 6)
    row_simple = {
        'answer': "The cat sat on the mat. It was a sunny day."
    }
    score_simple = metric._score(row_simple)
    assert score_simple > 0.8  # Should score high
    
    # Complex text (grade 14)
    row_complex = {
        'answer': "The feline specimen demonstrated sedentary comportment upon the textile substrate, concurrent with meteorological conditions characterized by heliocentric radiation."
    }
    score_complex = metric._score(row_complex)
    assert score_complex < 0.6  # Should score low
    
    print("✅ Readability metric tests passed")

# Run tests
test_medical_disclaimer_metric()
test_readability_metric()
```

---

## 📈 Production Integration

### Automated Quality Gates

```python
def quality_gate_check(dataset, metrics, thresholds):
    """
    Enforce quality standards before deployment
    
    Args:
        dataset: Test questions
        metrics: List of RAGAS metrics (standard + custom)
        thresholds: Dict of metric_name -> minimum_score
    
    Returns:
        bool: Whether system passes quality gate
    """
    results = evaluate(dataset, metrics=metrics)
    
    failures = []
    for metric_name, min_score in thresholds.items():
        actual_score = results.get(metric_name, 0)
        
        if actual_score < min_score:
            failures.append(
                f"{metric_name}: {actual_score:.2f} < {min_score:.2f}"
            )
    
    if failures:
        print("❌ Quality Gate FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ Quality Gate PASSED")
    return True

# Usage in CI/CD
medical_thresholds = {
    'faithfulness': 0.90,
    'answer_relevancy': 0.85,
    'medical_disclaimer': 0.95,  # Custom metric
    'readability': 0.80,          # Custom metric
    'empathy': 0.75               # Custom metric
}

passed = quality_gate_check(
    test_dataset,
    medical_metrics,
    medical_thresholds
)

if not passed:
    raise ValueError("Cannot deploy - quality standards not met")
```

---

## ✅ What You've Achieved

You now understand:

✅ **When to create** custom metrics  
✅ **Rule-based metrics** (deterministic)  
✅ **LLM-powered metrics** (semantic evaluation)  
✅ **Domain-specific evaluators** (medical, legal, financial)  
✅ **Testing custom metrics** (unit tests)  
✅ **Production integration** (quality gates)  
✅ **Combining metrics** for comprehensive evaluation  

**Impact**: You can now evaluate RAG systems against ANY criteria, not just standard metrics!

---

## 🚦 Next Steps

You've mastered all the metrics. Time to integrate RAGAS with your existing frameworks.

- **[Next: Framework Integration](./09-framework-integration.md)** - LangChain & LlamaIndex
- **[Back: Hyperparameter Optimization](./07-hyperparameter-optimization.md)** - Review optimization
- **[Real Example](./10-real-world-example.md)** - See custom metrics in action

---

*From generic evaluation to domain-specific quality standards. From "good enough" to "compliant and excellent."* ✨
