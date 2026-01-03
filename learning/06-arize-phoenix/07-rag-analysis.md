# RAG Analysis - Debugging Retrieval Quality

## 🕵️ The "Wrong Answer" Investigation

Your user asks: *"Does the insurance cover dental implants?"*
The bot answers: *"No, routine cleaning is not covered."*

**The problem**: The answer is unrelated.
**The diagnosis**: Did the LLM fail to simplify the text? Or did the Retriever find the wrong document?

In Phoenix, you don't guess. You look at the **Retrieved Documents** view.

---

## 📄 The RAG Trace View

When you click on a trace in Phoenix, look for the span labeled `RETRIEVER`.

### The Retrieval Panel

This creates a split-screen view:
*   **Left**: The Query (`input.value`)
*   **Right**: The Documents (`output.value`)

**What you see for each document:**
1.  **Content**: The actual text chunk.
2.  **Score**: The similarity score (e.g., `0.82`) assigned by the Vector DB.
3.  **Metadata**: Source filename, page number, etc.

### Scenario A: "Right Document, Wrong Answer"
*   **Observation**: The Retrieval Panel shows "Plan B covers implants at 50%." (Score: 0.89).
*   **Observation**: The LLM Output says "Not covered."
*   **Conclusion**: **Hallucination / Reasoning Failure**. The context was there, but the LLM ignored it.
*   **Fix**: Improve System Prompt instructions ("Prioritize context over training data").

### Scenario B: "Wrong Document, Wrong Answer"
*   **Observation**: The Retrieval Panel shows documents about "Deep Cleaning" and "Orthodontics." (Scores: 0.65, 0.62). The "Implants" document is missing.
*   **Conclusion**: **Retrieval Failure**.
*   **Fix**: Improve embeddings, change chunk size, or add Hybrid Search (Keyword + Vector).

---

## 🧮 Analyzing Scores & Reranking

RAG is rarely just "Search -> Answer". It's often "Search -> Rerank -> Filter -> Answer".

### Visualizing Reranking impact

If you use a localized reranker (like Colbert or Cohere Rerank), you will see **TWO** spans:
1.  `RETRIEVER` (Initial Fetch): 50 docs. Scores are raw vector cosine similarity.
2.  `RERANKER` (Refinement): 5 docs. Scores are semantic relevance probabilities.

**Debugging Patterns**:
*   **Pattern**: Initial fetch gets the right doc (Rank 15), but Reranker drops it (doesn't appear in top 5).
    *   *Issue*: Reranker model disagrees with Embedding model.
*   **Pattern**: Initial fetch misses the doc entirely.
    *   *Issue*: Embedding model (Bi-encoder) failed to map query close to doc.

### The "Score Cliff"

Sort your retrieved docs by score.
*   **Healthy**: `[0.91, 0.89, 0.88, 0.85]` (Gradual decline).
*   **Unhealthy**: `[0.92, 0.55, 0.54, 0.50]` (Sharp drop).
*   **Insight**: Only the first document is relevant. The rest are noise filling the `top_k`.
*   **Action**: Implement a **Similarity Cutoff** threshold (e.g., `score > 0.7`) to filter noise before it hits the LLM context window.

---

## 🔍 Search & Filtering

When you have 10,000 traces, you can't click them individually. You filter.

Phoenix uses a query language on attributes.

### Common Filters for RAG

1.  **Find Missing Context**:
    *   Filter: `retriever.documents is_empty` (or count = 0).
    *   *Meaning*: Queries where the vector DB returned nothing. These are instant failures.

2.  **Find Low Relevance**:
    *   Filter: `retriever.document_scores < 0.5`
    *   *Meaning*: The database struggled to find a good match. High risk of hallucination.

3.  **Find Expensive Queries**:
    *   Filter: `retriever.document_count > 10`
    *   *Meaning*: You are stuffing the context window. Is latency high here?

---

## 🧪 Embedding Analysis (Preview)

While looking at *text* is useful, sometimes you need to look at *clusters*.

*   "Why do we fail on dental queries?"
*   "Show me all queries semantically similar to this failure."

Phoenix integrates **UMAP visualizations** directly into the trace view. You can see your current query as a dot in a cloud of all past queries.

*If your query lands in a 'red' cluster (known failure zone), you know the issue is systemic, not isolated.* (More on this in File 08).

---

## 🚦 Summary

1.  **Don't trust the LLM**: Always verify the `RETRIEVER` span first.
2.  **Context is Truth**: If the answer contradicts the context span, it's a hallucination. If the context span is irrelevant, it's a retrieval failure.
3.  **Watch the Scores**: Use score distributions to tune your `top_k` and `score_threshold` parameters.

Next, we will look deeper into those "Clusters" using **Embedding Analysis**.

- **[Next: Embedding Analysis](./08-embedding-analysis.md)**

---

*The truth is in the context.*
