# Online Evaluation - LLMs Judging Live Traffic

## ⚖️ The Court That Never Sleeps

In previous modules (RAGAS/DeepEval), we ran evaluations *offline* on test sets.
**Online Evaluation** runs *continuously* on production traffic.

When a user chats with your bot, another "Judge LLM" (usually a smaller, faster one like GPT-3.5 or Claude Haiku) watches the conversation and scores it.

**Why?**
*   **Instant Alerts**: Know immediately if Hallucinations spike.
*   **No Human in the Loop**: You can't read 10,000 logs/day. An LLM can.
*   **Sampled Grading**: Grade 10% of traffic to track trends without breaking the bank.

---

## 🏗️ The Evaluator Architecture

1.  **Trace Arrives**: Phoenix receives a trace from your app.
2.  **Filter**: You select which spans to judge (e.g., only `OUTPUT` spans).
3.  **Evaluate**: The Phoenix server (or your script) runs an Evaluation Chain.
4.  **Annotate**: The result (e.g., "Toxic: True") is attached to the span as a tag.

---

## 💻 Implementation: Running an Evaluator

Phoenix provides built-in evaluators for common RAG metrics (Hallucination, QA Correctness, Toxicity).

### 1. Define the Judge Model

```python
from phoenix.evals import OpenAIModel
from phoenix.evals import HallucinationEvaluator, QAEvaluator
import pandas as pd
import phoenix as px

# Launch app using existing traces
client = px.Client()
trace_df = client.get_spans_dataframe() # filter for just 'OUTPUT' kind if needed

# Define Judge
model = OpenAIModel(model="gpt-4")

# Define Metric
hallucination_evaluator = HallucinationEvaluator(model)
```

### 2. Run the Evaluation (Batch Mode)

You can run this periodically (e.g., every hour via cron job).

```python
from phoenix.evals import run_evals

# Map DataFrame columns to Evaluator inputs
# The evaluator needs specific inputs: 'input', 'output', 'context'
# You might need to rename trace_df columns to match
trace_df['context'] = trace_df['retrieval.documents']  # Example mapping

results_df = run_evals(
    dataframe=trace_df,
    evaluators=[hallucination_evaluator],
    provide_explanation=True  # Important! Gets the "Reasoning"
)

# 3. Log results back to Phoenix UI
from phoenix.trace import SpanEvaluations

for index, row in results_df.iterrows():
    client.log_evaluations(
        SpanEvaluations(
            eval_name="Hallucination",
            span_id=index,  # trace_df index is usually span_id
            score=row['score'],
            label=row['label'], # "hallucinated" vs "factual"
            explanation=row['explanation']
        )
    )
```

---

## 🕵️ Viewing Evaluations in the UI

Once logged, go to the **Evaluations** tab in Phoenix.
1.  **Score Distribution**: See a histogram of scores. (e.g., 90% Factual, 10% Hallucinated).
2.  **Sort by Failure**: Sort by Score Ascending to see the worst interactions.
3.  **Explanations**: Click a trace to see *why* the Judge failed it.
    *   *Example*: "The answer claims X, but the retrieval context only mentions Y."

---

## 💡 Cost Management Strategies

Running GPT-4 on every user query doubles your cost. Don't do that.

### Strategy 1: Sampling
Only evaluate a random **5%** of traffic. This is statistically significant for spotting trends without high costs.

### Strategy 2: Targeted Evaluation
Only evaluate traces where:
*   User feedback was negative (Thumbs down).
*   Latency was > 10s.
*   Topic is "Legal/Compliance" (detected via embedding cluster).

### Strategy 3: Cheaper Judges
Use **GPT-3.5-Turbo** or **Claude 3 Haiku** for the judge. They are much cheaper and often "good enough" for spotting gross hallucinations or toxicity.

---

## 🚦 Summary

1.  **Online Eval** turns subjective logs into objective numbers.
2.  **Evaluators** (Hallucination, QA) run asynchronously; they don't slow down the user.
3.  **Log Results Back**: Always push the evaluation results back to Phoenix so they appear in the UI dashboards next to the original trace.

Next, what do we do with the "Bad" traces we found? We turn them into Gold.

- **[Next: Dataset Curation](./10-dataset-curation.md)**

---

*Judge not, lest ye be judged... by an LLM.* 👨‍⚖️
