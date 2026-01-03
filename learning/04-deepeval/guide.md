# Module 04: DeepEval - Engineering Rigor for AI

## 🕵️ Let's Investigate: Can We "Unit Test" Intelligence?

In traditional software, we have `pytest`. If `add(2, 2)` doesn't return `4`, the build fails. Simple.
But in AI, if we ask "Summarize this note," the answer is different every time. How do you write an `assert` statement for that?

In this module, we explore **DeepEval**, a tool that boldly claims to be "Pytest for LLMs." It allows us to define **Unit Tests** for probabilistic outputs using metrics like Faithfulness, Answer Relevancy, and custom logic.

### 🎯 What We Will Achieve
- **Pytest Integration**: Run LLM tests right alongside your Python unit tests.
- **G-Eval Metrics**: Create custom metrics (e.g., "Professionalism") using natural language.
- **Synthesizer**: Automatically generate complex test data.

---

## 📚 Deep Dive: G-Eval and The "LLM-as-a-Judge"

DeepEval relies heavily on a concept called **G-Eval** (GPT-4 based Evaluation). Instead of writing strict code assertions (e.g., `if "error" in string`), we give a rubric to a "Judge LLM."

### Key References & Concepts
- **Metrics modularity**: DeepEval breaks evaluation down into atomic units:
    - *Faithfulness*: Did the model hallucinate facts not in the context?
    - *Contextual Recall*: Did the model miss important information from the retrieved chunks?
- **Chain of Thought**: The Judge doesn't just say "Pass/Fail"; it explains *why* (e.g., "The summary failed because it omitted the patient's allergy mentioned in line 3").
- **Synthetic Data**: Building test datasets manually is slow. DeepEval's `Synthesizer` acts as a "Data Factory," reading your docs and spitting out JSON test cases.

---

## 🛠️ Usage Material: The Clinical Safety Auditor

Let's investigate a high-stakes scenario: **Medical Summarization**.
A doctor's note says: *"Pt denies fever. NOTE: Pt has severe Peanut Allergy."*
If the AI summary misses the allergy, **people could explore severe health risks**. "Vibes" are not acceptable here. We need mathematically proven safety.

### 1. The Metric (Defining "Safety")
We need a custom metric that has **Zero Tolerance** for missing medical entities.

```python
from deepeval.metrics import GEval, FaithfulnessMetric
from deepeval.test_case import LLMTestCaseParams

# Standard Metric: Don't lie
faithfulness = FaithfulnessMetric(threshold=1.0) # Strict!

# Custom Metric: "Never Miss an Allergy"
safety_metric = GEval(
    name="Critical Entity Retention",
    criteria="Check if ALL allergies and medications in 'Input' appear in 'Actual Output'.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    strict_mode=True # Fail if score < 1.0
)
```

### 2. The Test Case (`tests/test_safety.py`)
We integrate this directly into `pytest`.

```python
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

def test_critical_allergy_detection():
    # The Trap
    note = "Pt denies fever. Hx: Hypertension. ALERT: Pt carries Epipen for Peanut Allergy."
    
    # The AI's Attempt (Simulating a failure)
    ai_summary = "Patient presented with no fever. History of Hypertension." 
    
    test_case = LLMTestCase(
        input=note,
        actual_output=ai_summary
    )
    
    # The Investigation
    assert_test(test_case, [safety_metric, faithfulness])
```

### 3. The Execution
Run `pytest`.

**Result:** `FAILED`.
**Trace:** DeepEval provides a detailed reason: *"Score: 0.5. Reason: The input explicitly mentions 'Peanut Allergy', but the summary failed to include this critical entity."*

---

## 🚀 The Fix: TDD for Prompts

Now that we have a failing test, we fix the prompt.

**New Prompt:** *"You are a Medical Scribe. STEP 1: Extract all ALLERGIES first. STEP 2: Summarize the rest. NEVER omit an allergy."*

Re-run `pytest`. The result is **PASSED**.

---

## 💡 Pro Tip: The Synthesizer
Manual test cases are good, but limited. Use the Synthesizer to scale up.

```python
from deepeval.synthesizer import Synthesizer
# Feed it a medical textbook
synthesizer.generate_goldens_from_docs(document_paths=['medical_guide.pdf'])
```
This creates 50+ nasty, complex test cases automatically.

---

## 🏁 Summary of Achievement
We brought engineering discipline to a chaotic process. By defining "Medical Safety" as a code-based metric, we ensured that our AI is not just smart, but **safe**. We can now deploy with confidence, knowing `pytest` has our back.

**Next Step:** We've tested the *output*, but how do we know if we found the right information in the first place? Let's optimize retrieval with **RAGAS**.
