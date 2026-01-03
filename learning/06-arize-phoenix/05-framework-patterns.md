# Framework Patterns - Decoding the Diagrams

## 🗺️ Reading the Maps of LangChain & LlamaIndex

When you instrument a complex framework, Phoenix generates rich, nested trace trees. To debug effectively, you need to recognize the "visual signature" of common RAG patterns.

This guide teaches you how to read these patterns like an X-Ray chart.

---

## 🦜 LangChain Patterns

LangChain relies heavily on the "Chain" concept (sequences of Runnables). This appears in Phoenix as a deep hierarchy of generic `CHAIN` spans wrapping specific `LLM` or `TOOL` spans.

### Pattern 1: The `RunnableSequence` (Pipe `|`)

**Code**: `chain = prompt | model | parser`

**Phoenix Visual Signature**:
```text
[CHAIN] RunnableSequence (Root)
 ├── [CHAIN] ChatPromptTemplate
 │    └── Input: {"topic": "AI"}
 │    └── Output: [HumanMessage(content="Explain AI")]
 ├── [LLM] ChatOpenAI
 │    └── Input: [HumanMessage(content="Explain AI")]
 │    └── Output: AIMessage(content="AI is...")
 │         └── Attributes: token_usage, model_name
 └── [CHAIN] StrOutputParser
      └── Input: AIMessage(...)
      └── Output: "AI is..."
```

**Debugging Tip**:
*   If the output is wrong, check the **Output** of the `ChatPromptTemplate` span. Did the variable substitution `{topic}` happen correctly?
*   If formatting is wrong, check the **Input** of `StrOutputParser`. Did the LLM output JSON when the parser expected text?

### Pattern 2: The `RetrievalQA` Chain

**Code**: `RetrievalQA.from_chain_type(...)`

**Phoenix Visual Signature**:
```text
[CHAIN] RetrievalQA
 ├── [RETRIEVER] VectorStoreRetriever  <-- CRITICAL SPAN
 │    ├── Input: "What is RAG?"
 │    └── Output: [Document(page_content="..."), Document(...)]
 │         └── Attributes: retrieval.documents (Click to view chunks!)
 └── [CHAIN] StuffDocumentsChain
      └── [LLM] ChatOpenAI
           └── Input: "System: Use this context... User: ..."
```

**Debugging Tip**:
*   Always expand the `RETRIEVER` span first.
*   **Zero Results?**: Check the Input query string. Was it modified/rephrased unexpectedly?
*   **Bad Results?**: Check the retrieved document scores in the attributes tab.

### Pattern 3: The Agent (`AgentExecutor`)

**Code**: `AgentExecutor(agent=..., tools=...)`

**Phoenix Visual Signature**:
```text
[CHAIN] AgentExecutor
 ├── [LLM] ChatOpenAI
 │    └── Output: "I need to calculate 2 + 2. Action: Calculator"
 ├── [TOOL] Calculator
 │    └── Input: "2 + 2"
 │    └── Output: "4"
 ├── [LLM] ChatOpenAI
 │    └── Input: "Observation: 4"
 │    └── Output: "The answer is 4."
```

**Debugging Tip**:
*   Look for the **Loop**. Agents loop. You will see LLM -> Tool -> LLM -> Tool sequences.
*   **Infinite Loop?**: Check if the Tool Output spans contain error messages that confuse the LLM, causing it to retry the same failed action.

---

## 🦙 LlamaIndex Patterns

LlamaIndex traces usually have more specific names (e.g., `QueryEngine`, `Synthesizer`) rather than generic `Chain`.

### Pattern 1: The Basic `QueryEngine`

**Code**: `index.as_query_engine().query(...)`

**Phoenix Visual Signature**:
```text
[CHAIN] BaseQueryEngine.query
 ├── [CHAIN] RetrieverQueryEngine.query
 │    ├── [RETRIEVER] VectorIndexRetriever.retrieve
 │    │    └── Output: [NodeWithScore(...), NodeWithScore(...)]
 │    └── [CHAIN] ResponseSynthesizer.synthesize
 │         ├── [LLM] OpenAI.chat
 │         │    └── Input: "Context: ... Query: ..."
 │         │    └── Output: "Response..."
```

**Visual Difference**: LlamaIndex explicitly separates "Retriever" and "Synthesizer" logic in the trace tree, making it slightly easier to navigate RAG logic than standard LangChain.

### Pattern 2: Sub-Question Query Engine (Complex RAG)

**Code**: Breaks 1 hard question into 3 simpler ones.

**Phoenix Visual Signature**:
```text
[CHAIN] SubQuestionQueryEngine
 ├── [LLM] OpenAI (Plan Generation)
 │    └── Output: "1. What is X? 2. What is Y?"
 ├── [CHAIN] QueryEngine (for Question 1)
 │    └── [RETRIEVER] ...
 │    └── [LLM] ...
 ├── [CHAIN] QueryEngine (for Question 2)
 │    └── [RETRIEVER] ...
 │    └── [LLM] ...
 └── [CHAIN] ResponseSynthesizer (Combine answers)
      └── [LLM] OpenAI
```

**Debugging Tip**:
*   Look at parallel branches. Use the **Latency Waterfall** view in Phoenix to see if questions 1 and 2 ran in parallel (bars overlap) or sequentially (staircase pattern). This is a prime optimization target.

---

## 🏗️ Custom Pattern: The "Sanity Check"

Sometimes you wrap a framework call with your own logic.

```python
@trace  # Custom
def safe_query(user_query):
    if is_toxic(user_query): return "Blocked"
    return agent.invoke(user_query)
```

**Phoenix Visual Signature**:
```text
[CHAIN] safe_query (Your Function)
 ├── [CHAIN] AgentExecutor
      └── ...
```

**Why this is huge**: The ROOT span is now *your* function. You can tag it with metadata like `user_id` or `session_id`, and all the child spans (LangChain/LlamaIndex internals) usually inherit that context if using proper instrumentors.

---

## 🚦 Summary

1.  **LangChain** looks like a deep tree of `CHAIN` -> `RUNNABLE` -> `LLM`.
2.  **LlamaIndex** looks structured with `RETRIEVER`, `SYNTHESIZER`, and `NODE_PARSING`.
3.  **Agents** look like alternating `LLM` and `TOOL` spans.
4.  **Retrievers** are the most critical spans to inspect for RAG quality issues.

In the next section, we will learn how to create those **Custom Spans** manually, for times when auto-instrumentation isn't enough.

- **[Next: Custom Instrumentation](./06-custom-instrumentation.md)**

---

*Now you can read the Matrix.* 🕶️
