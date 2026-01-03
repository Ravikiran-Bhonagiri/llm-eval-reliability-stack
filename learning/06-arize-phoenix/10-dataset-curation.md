# Dataset Curation - Alchemy for Data

## ♻️ The Cycle of Improvement

You found 50 traces where your bot hallucinated (using Online Eval from File 09).
Now what?
1.  Fix the code.
2.  **Ensure it never happens again.**

To do step 2, you need to add those 50 failures to your Test Suite. Phoenix makes this easy by allowing you to "Curate" spans into a Dataset.

---

## 💾 Golden Datasets in Phoenix

Phoenix isn't just a trace viewer; it's a Dataset Manager.

### The Problem with CSVs
Teams usually email around `test_set_v3_final_final.csv`. It's messy.
Phoenix stores datasets centrally (SQLite/Postgres) with:
*   **Versioning**: v1, v2, v3...
*   **Metadata**: Created at, Source trace ID.
*   **Schema**: Input, Output, Expected Output.

### Creating a Dataset from Traces

**In the UI**:
1.  Filter for `eval.hallucination == "hallucinated"`.
2.  Select 10 difficult examples.
3.  Click **"Add to Dataset"**.
4.  Choose "Weakness_Hallucinations" dataset.

**In Python**:
```python
import phoenix as px

client = px.Client()

# Get problematic spans
bad_df = client.get_spans_dataframe(
    filter_condition="eval.hallucination_score == 1.0"
)

# Create/Append to Dataset
dataset = client.upload_dataset(
    dataframe=bad_df,
    dataset_name="production_failures_v1",
    input_keys=["input.value"],
    output_keys=["output.value"], # This is the "bad" output, useful for "negative" testing
    metadata_keys=["span_id"]
)
```

---

## 🛠️ The Human-in-the-Loop (Annotation)

Before you use these for testing, a human often needs to write the **Correct Answer**.

In the Phoenix UI:
1.  Open the Dataset.
2.  Review the "Input" (User Query).
3.  Edit the "Output" (Bot Answer) -> Change it to the **Ideal Answer**.
4.  Save.

Now you have a labeled Golden Example.

---

## 📦 Exporting for CI/CD

Now exporting this back to your reliability stack (Promptfoo/DeepEval/RAGAS).

```python
# Load dataset
dataset = client.get_dataset(name="production_failures_v1")
df = dataset.as_dataframe()

# Convert to RAGAS format
ragas_data = {
    "question": df["input.value"].tolist(),
    "ground_truth": df["output.value"].tolist() # Assuming you fixed them
}

# Run Eval
from ragas import evaluate
# ... run standard evaluation ...
```

**The Flywheel Effect**:
1.  Deploy.
2.  Find failures (Phoenix).
3.  Add to Dataset.
4.  Regression Test (RAGAS).
5.  Fix Code.
6.  Deploy (Confidence +1).

---

## 🚦 Summary

1.  **Don't waste failures**: Every failure is a future test case waiting to be born.
2.  **Centralize**: Store datasets in Phoenix, not loose files.
3.  **Annotate**: Use the UI to fix "Bad" outputs into "Golden" outputs.

Next, we look at the logistics of running this in a real environment.

- **[Next: Production Deployment](./11-production-deployment.md)**

---

*Turn lead (errors) into gold (tests).* ⚗️
