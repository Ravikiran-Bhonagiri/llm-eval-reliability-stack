# Embedding Analysis - Visualizing the Invisible

## 🌌 Seeing in 1536 Dimensions

Every time a user sends a query, it gets turned into a vector (e.g., an array of 1,536 floats for OpenAI `text-embedding-3-small`). This vector represents the "meaning" of the query.

You can't read a vector. But Arize Phoenix can **project** it.

Using dimensionality reduction techniques (UMAP), Phoenix squashes these high-dimensional vectors down to 2D or 3D points on a scatter plot. Points that are close together have similar meanings.

This unlocks **Cluster Analysis**: Finding patterns in your data that you didn't know existed.

---

## 🗺️ The Embedding View

When you upload traces *specifically containing embedding data*, Phoenix generates a 3D point cloud.

### 1. Ingestion Requirements

To see this view, you must capture the *embedding vector itself* in your trace, or generate it post-hoc. Auto-instrumentation for OpenAI handles this automatically if you use the Embeddings API.

For RAG queries (where you only have text), Phoenix can infer embeddings if you compute them on your dataset dataframe and upload it as a "Corpus."

---

## 🕵️ Use Case 1: Finding "The Cluster of Confusion"

Imagine you see a dense cluster of points. You hover over them:
*   "How do I reset my API key?"
*   "API token lost"
*   "Generate new secret key"

**Observation**: You notice 80% of these points are colored **Red** (indicating Negative User Feedback or Failed Evaluation).

**Insight**: Users are asking about API keys, and your bot is consistently failing. You didn't know this was a major topic until you saw the cluster.

**Action**: Add a new section to your documentation about API keys. The solution is clear because the problem is isolated.

---

## 🕵️ Use Case 2: Detecting Data Drift

**Scenario**: You trained/tested your RAG system on "Product A" documentation.
**Production**: Users start asking about "Product B" (which launched yesterday).

**Visual Signature**:
*   Blue points (Training Data) are on the Left side.
*   Green points (Production Traffic) represent a huge new blob on the Right side.
*   **Euclidean Distance**: The center of mass of your production traffic has utilized a distinct semantic space.

**Diagnosis**: **Drift**. Your test set no longer represents reality.
**Action**: You need to export the "Product B" cluster, label it, and add it to your test suite (using Promptfoo/DeepEval) to ensure coverage.

---

## 🎨 Coloring by Metric

The most powerful feature is **Color Coding**.

You can color the points in the 3D cloud by any attribute or metric:
1.  **Color by `token_count`**: Find the "long query" cluster.
2.  **Color by `latency_ms`**: Find the "slow query" cluster. (Maybe complex legal questions take longer?)
3.  **Color by `eval.relevance`**: Find the "hallucination" cluster.

**Example**: You color by `latency`. You see a distinct island of points that are bright red (10s+ latency). You hover. They are all queries in **Japanese**.
*   *Discovery*: Use of non-English characters is breaking your tokenizer or triggering a slow translation model.

---

## 💻 Code: Generating Visualization Data

Typically, you work with pandas DataFrames for this advanced analysis.

```python
import pandas as pd
import phoenix as px
from phoenix.session.evaluation import get_qa_with_reference

# 1. Export your traces to a DataFrame
trace_df = px.Client().get_spans_dataframe()

# 2. Add embeddings (if not present)
# (pseudo-code using a helper)
trace_df["embedding"] = trace_df["input.value"].apply(lambda x: get_openai_embedding(x))

# 3. Launch Phoenix with the specialized 'corpus' mode for visualization
# This explicitly enables the Embedding Analysis tab
px.launch_app(primary=trace_df, schema=px.Schema(
    timestamp_column_name="start_time",
    prompt_column_names=px.EmbeddingColumnNames(
        vector_column_name="embedding",
        raw_data_column_name="input.value"
    )
))
```

---

## 🚦 Summary

1.  **Vectors define Meaning**: UMAP visualization allows you to see semantic relationships in your production traffic.
2.  **Clusters tell Stories**: Dense groups of points reveal user intents (topics) or failure modes.
3.  **Color reveals Correlation**: Coloring clusters by Latency or Evaluation Score highlights systemic issues.

Next, we move to the "Feedback Loop." How do we automatically grade these traces so we know which dots to color red?

- **[Next: Online Evaluation](./09-online-evaluation.md)**

---

*See the shape of your data.* 🔺
