# Building Block 5: Business Failure Testing

## Beyond Security: Validating Correctness

Security = "Can it be hacked?"
Business Failures = "Does it work correctly?"

---

## 🎯 What Are Business Failures?

- **Hallucinations**: Inventing false information
- **Factual errors**: Wrong answers from correct docs
- **Policy violations**: Breaking business rules
- **Tone issues**: Inappropriate formality/informality

---

## 🔬 Testing Business Logic

### Example: Financial Advisor Bot

```python
from giskard.rag import generate_testset

# Generate tests from compliance docs
testset = generate_testset(
    knowledge_base,
    num_questions=100,
    agent_description="Must never give specific investment advice"
)

# Evaluate
results = evaluate(model, testset)
```

### Custom Business Rules

```python
def check_no_financial_advice(question, answer):
    """Custom detector for regulatory compliance"""
    forbidden = ["buy", "sell", "invest in", "guaranteed"]
    return not any(word in answer.lower() for word in forbidden)
```

---

## 📊 Key Metrics

- **Faithfulness**: Answer grounded in retrieved context?
- **Correctness**: Factually accurate?
- **Completeness**: Addresses all parts of question?
- **Appropriateness**: Follows business guidelines?

---

## ✅ Best Practices

1. **Define clear business rules** before testing
2. **Generate domain-specific tests** using RAGET
3. **Combine with security testing** for comprehensive validation
4. **Iterate based on failures**

---

*Business correctness is as critical as security.*
