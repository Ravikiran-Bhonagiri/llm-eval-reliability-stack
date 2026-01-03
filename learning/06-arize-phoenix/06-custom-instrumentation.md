# Custom Instrumentation - Adding Your Own Sensors

## 🛠️ Going Off-Road

Auto-instrumentation is great for libraries Phoenix knows (OpenAI, LangChain). But what about *your* code?
- The text preprocessing function?
- The custom re-ranking algorithm?
- The final response formatter?

If you don't trace these, they become "dark matter" in your latency waterfall—time gaps you can't explain.

**Goal**: Use the `@trace` decorator to visualize your own functions.

---

## 🏗️ The `@trace` Decorator

The easiest way to add a span is creating a decorator. Phoenix doesn't ship a simplified one (it relies on standard OTEL), so typically developers define a helper.

If you are using `openinference-instrumentation`, it often hooks into generic methods, but let's look at the **OpenTelemetry Standard Way** which works universally.

### 1. Minimal Setup

First, standard OTEL imports:

```python
from opentelemetry import trace

# Get a tracer
tracer = trace.get_tracer(__name__)
```

### 2. Manual Context Manager

Wrap any block of code in a `start_as_current_span` block.

```python
def my_complex_logic(user_input):
    # This part is hidden unless we trace it
    with tracer.start_as_current_span("preprocess_input") as span:
        cleaned = user_input.strip().lower()
        span.set_attribute("input.original_length", len(user_input))
        span.set_attribute("input.cleaned", cleaned)
        return cleaned
```

### 3. The Reusable Decorator

Instead of `with` blocks everywhere, let's make a `@trace` decorator.

```python
import functools
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def trace_span(name=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name) as span:
                # Optional: Auto-log inputs (be careful with PII)
                span.set_attribute("function.args", str(args))
                
                try:
                    result = func(*args, **kwargs)
                    # Optional: Auto-log output
                    span.set_attribute("function.result", str(result))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    raise e
        return wrapper
    return decorator
```

---

## 💻 Example: Tracing a Custom RAG Pipeline

Let's say you built RAG from scratch (no LangChain).

```python
# app.py

@trace_span("process_request")
def handle_user_query(query):
    # 1. Search
    docs = retrieve_documents(query)
    
    # 2. Rerank (Custom logic!)
    ranked_docs = custom_reranker(docs)
    
    # 3. Generate
    answer = call_llm(ranked_docs, query)
    return answer

@trace_span("vector_search")
def retrieve_documents(query):
    # Simulate DB call
    return ["Doc A", "Doc B", "Doc C"]

@trace_span("rerank_logic")
def custom_reranker(docs):
    # Your proprietary magic
    return sorted(docs, reverse=True)  # Simple logic for demo

# Run it
handle_user_query("Hello world")
```

**The Visualization**:
```text
[SPAN] process_request
 ├── [SPAN] vector_search
 ├── [SPAN] rerank_logic  <-- Use this to debug your custom algo latency!
 └── [SPAN] OpenAI (Auto-instrumented if enabled)
```

---

## 🏷️ Adding Rich Attributes (Tagging)

Spans are boring without data. Attributes make them searchable in Phoenix.

### Useful Attributes to Add

1.  **Session Metadata**:
    ```python
    span.set_attribute("session.id", "sess_123")
    span.set_attribute("user.plan", "premium")
    ```
    *Why*: Allows you to filter traces by "Premium Users" later.

2.  **RAG Specifics**:
    If you aren't using LlamaIndex but want the "Retrieval" visualization, you must adhere to OpenInference semantic conventions manually.

    ```python
    from openinference.semconv.trace import SpanAttributes

    with tracer.start_as_current_span("my_retriever") as span:
        # Tell Phoenix this is a RETRIEVER span
        span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, "RETRIEVER")
        
        # Add 'retrieval.documents' attribute (JSON string) to show chunks in UI
        # See OpenInference docs for exact JSON schema
    ```

3.  **Experiment Tracking**:
    ```python
    span.set_attribute("experiment.prompt_version", "v2.1-aggressive")
    ```
    *Why*: Compare "v2.1" vs "v2.0" performance in the Evaluation tab.

---

## ⚠️ Handling Async Code

If your app uses `async def`, your decorator must handle awaitables.

```python
def trace_async(name=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name) as span:
                result = await func(*args, **kwargs)
                return result
        return wrapper
    return decorator

@trace_async("async_search")
async def search_db():
    await asyncio.sleep(1)
```

---

## 🚦 Summary

1.  **Use `@trace`** (custom decorator) to wrap significant business logic blocks (preprocessing, reranking, post-processing).
2.  **Inherit Context**: These manual spans automatically become children of whatever span was active (e.g., the root request span).
3.  **Tag Aggressively**: Add `user_id`, `version`, and `mode` attributes. These become your filters in the Phoenix UI.

Next, we move to the ANALYSIS phase. We have traces; now let's analyze the **Retrieval** specific data.

- **[Next: RAG Analysis](./07-rag-analysis.md)**

---

*Now you can see the dark matter.*
