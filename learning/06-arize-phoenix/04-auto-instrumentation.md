# Auto-Instrumentation - The Magic Easy Button

## 🪄 Why Write Spans When You Can Generate Them?

In the previous section, we learned trace theory (Traces, Spans, Attributes). Writing that code manually (`tracer.start_span(...)`) is tedious and error-prone.

**Auto-instrumentation** automates this. It "monkey-patches" popular libraries (like OpenAI, LangChain) so that every time you call them, a span is implicitly created.

**The promise**: *Add 2 lines of code, get full observability.*

---

## 🛠️ The `openinference` Ecosystem

Arize Phoenix relies on a family of packages called `openinference-instrumentation-*`. You install specific packages for the libraries you use.

### Common Instrumentors

| Library | Package | What it Traces |
| :--- | :--- | :--- |
| **OpenAI** | `openinference-instrumentation-openai` | Chat completions, embeddings, token counts |
| **LangChain** | `openinference-instrumentation-langchain` | Chains, Retrievers, Tools, Agents |
| **LlamaIndex** | `openinference-instrumentation-llama-index` | Query Engines, Nodes, Retrievers |
| **Bedrock** | `openinference-instrumentation-bedrock` | AWS Bedrock calls |
| **Mistral** | `openinference-instrumentation-mistralai` | Mistral API usage |

---

## 💻 Scenario A: Tracing Raw OpenAI Calls

Even if you aren't using a framework, you can trace raw API calls.

### 1. Installation

```bash
pip install arize-phoenix openinference-instrumentation-openai openai
```

### 2. Implementation

```python
import os
import phoenix as px
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI

# 1. Configure Endpoint (Local Phoenix Server)
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006/v1/traces"
os.environ["PHOENIX_PROJECT_NAME"] = "openai-demo"

# 2. Launch Phoenix (Optional, if not running externally)
# px.launch_app() 

# 3. THE MAGIC LINE: Initialize Instrumentation
OpenAIInstrumentor().instrument()

# 4. Use OpenAI as normal!
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a joke about observability"}]
)

print(response.choices[0].message.content)
```

**What happened?**
The `instrument()` call intercepted the `client.chat.completions.create` method. It handled:
*   Creating a span named "OpenAI".
*   Capturing input payload (`messages`).
*   Capturing output payload (`choices`).
*   Calculating execution duration.
*   Sending it all to Phoenix.

---

## 💻 Scenario B: Tracing LangChain

LangChain is complex. Chains call Loggers which call Models. Auto-instrumentation untangles this web.

### 1. Installation

```bash
pip install openinference-instrumentation-langchain langchain langchain-openai
```

### 2. Implementation

```python
from openinference.instrumentation.langchain import LangChainInstrumentor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# 1. Instrument!
LangChainInstrumentor().instrument()

# 2. Build a Chain
model = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("Explain {topic} in 5 words.")
output_parser = StrOutputParser()

chain = prompt | model | output_parser

# 3. Run it
# The instrumentation captures the entire sequence
result = chain.invoke({"topic": "Quantum Physics"})
print(result)
```

**The Trace Visualization**:
Unlike the raw OpenAI trace (1 span), this creates a **Tree**:
```text
[CHAIN] RunnableSequence
├── [CHAIN] ChatPromptTemplate (Input: "Quantum Physics" -> Output: PromptObject)
├── [LLM] ChatOpenAI (Input: PromptObject -> Output: "Particles behave like waves.")
└── [CHAIN] StrOutputParser (Input: MsgObject -> Output: String)
```
You see the flow of data passing between components!

---

## 💻 Scenario C: Tracing LlamaIndex

LlamaIndex instrumentation is powerful because it understands **Retrieval**.

### 1. Installation

```bash
pip install openinference-instrumentation-llama-index llama-index
```

### 2. Implementation

```python
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 1. Instrument
LlamaIndexInstrumentor().instrument()

# 2. Build RAG
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 3. Query
response = query_engine.query("What does the data say?")
```

**The Trace Visualization**:
Phoenix detects the `RETRIEVER` span type.
*   It exposes a special **"Retrieved Documents"** tab in the UI.
*   You can see the text content and similarity score of every chunk fetched before it was sent to the LLM.

---

## 🧹 Managing Instrumentation (Start/Stop)

Sometimes you want to trace only specific parts of your code.

```python
instrumentor = OpenAIInstrumentor()

# Start
instrumentor.instrument()
run_critical_code()

# Stop (Un-patch)
instrumentor.uninstrument()
run_unimportant_code()
```

---

## ⚠️ Limitations & Gotchas

1.  **Concurrency**: Auto-instrumentation uses `contextvars`. If you launch threads manually without copying context, `child` spans might become `root` spans (orphaned).
2.  **Versioning**: If LangChain releases a breaking change (v0.1 -> v0.2), the instrumentor might break until `openinference` updates. *Always pin your versions.*
3.  **Overhead**: It creates a tiny bit of latency (microseconds), usually negligible compared to LLM latency.
4.  **Payload Size**: If you send massive documents (100k tokens), your trace payloads gets huge. You may need to configure ingestion limits on the server.

---

## 🚦 Summary

1.  **Don't write manual spans** for standard libraries. Use `OpenAIInstrumentor`, `LangChainInstrumentor`, etc.
2.  **Point to Phoenix** using `PHOENIX_COLLECTOR_ENDPOINT`.
3.  **Run your code** as normal. The magic happens in the background.

Next, we will look at **Framework Patterns** to understand exactly *what* these instrumentors are verifying in complex RAG workflows.

- **[Next: Framework Patterns](./05-framework-patterns.md)**

---

*The magic is installed. Now let's see what it reveals.*
