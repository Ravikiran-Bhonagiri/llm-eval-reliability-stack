# Module 06: Arize Phoenix - X-Ray Vision for Agents

## 🕵️ Let's Investigate: Why Did My Agent Get Stuck?

Testing in a notebook is one thing. Running in production is another.
Imagine you deploy a "Supply Chain Agent." It's supposed to negotiate prices. But suddenly, your API bill spikes to $500 in one hour. The agent is stuck in an infinite loop, politely saying *"I agree"* to itself 5,000 times.

How do you debug this? `print()` statements won't save you here.
In this module, we explore **Arize Phoenix**, an observability platform that gives us "X-Ray Vision" into the execution of our agents.

### 🎯 What We Will Achieve
- **Distributed Tracing**: Visualize the entire flow of a complex Agentic workflow.
- **Span Replay**: Take a failed production trace and "replay" it locally to fix it.
- **Embedding Visualization**: See exactly what your RAG system "thinks" your documents look like.

---

## 📚 Deep Dive: Tracing and OpenInference

Phoenix is built on **OpenInference**, an industry standard for capturing LLM execution data. It captures **Traces** (the whole request) and **Spans** (individual steps, like a retrieval or an LLM call).

### Key References & Concepts
- **Waterfall Visualization**: Phoenix shows a timeline. You can see:
    - *Retrieve*: Took 400ms.
    - *LLM Generation*: Took 2.5s.
    - *Tool Call*: Failed after 1s.
- **Span Replay**: The "Killer Feature." You can click on a failed step in the UI, tweak the prompt, and run *just that step* again to see if it fixes the bug.
- **Embedding Drift**: By visualizing embeddings in 3D space, you can spot if user queries are drifting away from your knowledge base (i.e., users asking about things you have no docs for).

---

## 🛠️ Usage Material: The "Glass-Box" Negotiator

Let's debug a **Multi-Agent System**. We have a "Buyer" and a "Seller" agent negotiating a price.

### 1. The Setup (Auto-Instrumentation)
Adding Phoenix is suspiciously easy. It often takes just two lines of code to instrument LangChain or LlamaIndex.

```python
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor

# 1. Launch the UI
px.launch_app()

# 2. Hook into LangChain
LangChainInstrumentor().instrument()

# 3. Run your Agent
agent.invoke({"input": "Negotiate a price for 500 widgets"})
```

### 2. The Investigation (The Infinite Loop)
You run the agent. It never finishes. You check `localhost:6006`.
**The Trace:**
- You see a stack of 50 green bars.
- Click one: *Seller says "I can do $45."*
- Click next: *Buyer says "Deal."*
- Click next: *Seller says "Great."*
- Click next: *Buyer says "Awesome."*

**The Diagnosis:** The agents agreed, but neither called the `sign_contract` tool. They are too polite to hang up!

### 3. The Fix (Span Replay)
In Phoenix, grab the last "Seller" span. Click **"Open in Playground"**.
Change the system prompt:
*"If the buyer agrees, you MUST call the `sign_contract` tool immediately. Do not chatter."*

Run it in the playground.
**Result:** The model outputs a Tool Call: `sign_contract(price=45)`.

**Optimization:** Copy this improved prompt back to your codebase.

---

## 🚀 Advanced: Embedding Analysis
Phoenix aids RAG too.
Go to the **"Embeddings"** tab.
- **Blue Dots**: Your documents.
- **Red Dots**: User queries.
- **Investigation**: If you see a cluster of Red Dots far away from any Blue Dots, it means users are asking about a topic you have zero documentation for. You need to ingest new PDFs!

---

## 🏁 Summary of Achievement
We turned a "Black Box" into a "Glass Box."
- We saw exactly where the latency was.
- We debugged an infinite loop without reading 500 lines of logs.
- We visualized the gaps in our knowledge base.

**Conclusion:** This completes the stack. You now have the tools to **Test** (Promptfoo), **Secure** (Giskard), **Validate** (DeepEval), **Optimize** (RAGAS), and **Observe** (Phoenix).

You are no longer just an "AI Developer." You are an **AI Reliability Engineer.**
