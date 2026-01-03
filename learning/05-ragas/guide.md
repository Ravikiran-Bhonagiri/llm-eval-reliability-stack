# Module 05: RAGAS - Scientific RAG Optimization

## 🕵️ Let's Investigate: Is Your Retriever Blind?

You built a RAG system. You set `chunk_size=1000`. Why? *"Because a tutorial said so."*
This is **Guesswork**, not Engineering.

What if `chunk_size=500` yields better answers? What if `overlap=50` cuts off critical sentences? In this module, we will stop guessing and start measuring. We will use **RAGAS** to scientifically tune our retrieval pipeline.

### 🎯 What We Will Achieve
- **Reference-Free Evaluation**: Grade your RAG system without needing human-labeled answers.
- **The RAG Triad**: Measure Faithfulness, Answer Relevance, and Context Relevance separately.
- **Hyperparameter Optimization**: Find the "Golden" chunk size for your specific data.

---

## 📚 Deep Dive: The "Triad" and Synthetic Evolution

RAGAS is unique because it doesn't need "Ground Truth" (ideal human answers) to tell you if your system is working. It uses the **RAG Triad** of metrics.

### Key References & Concepts
- **Faithfulness**: Is the answer derived *only* from the retrieved context? (Detects hallucinations).
- **Answer Relevance**: Did the bot actually answer the user's question, or did it dodge it?
- **Context Metrics**:
    - *Context Precision*: Did we find the right documents amidst the noise?
    - *Context Recall*: Did we verify that the answer is actually *in* the documents we found?
- **Evolutionary Generation**: RAGAS generates test data by "evolving" simple questions into complex ones (e.g., adding constraints, reasoning steps) to stress-test your retriever.

---

## 🛠️ Usage Material: The Legal Search Optimizer

Let's investigate a **Legal Research** scenario.
Lawyers need to find specific precedents. If we chunk a 100-page verdict incorrectly, we might split the "Guilty" verdict from the "Reasoning," making the retrieval useless.

### 1. The Experiment (Grid Search)
We want to find the best configuration. We define a hypothesis space.

```python
configs = [
    {"name": "Small_Chunks", "chunk_size": 256, "overlap": 20},
    {"name": "Medium_Chunks", "chunk_size": 512, "overlap": 50},
    {"name": "Large_Chunks", "chunk_size": 1024, "overlap": 100}
]
```

### 2. The Data (Synthetic Generation)
We don't ask a lawyer to write 100 questions. We ask RAGAS.

```python
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import reasoning, multi_context

# "Read this court case and generate 50 complex reasoning questions"
generator = TestsetGenerator.from_langchain(generator_llm, critic_llm)
testset = generator.generate_with_langchain_docs(docs, testset_size=50)
```
**Investigative Insight:** Look at the generated questions. RAGAS will create "Multi-hop" queries like *"Based on the dissenting opinion AND the majority ruling, what was the stance on API copyright?"* This forces the retriever to find *two* distinct chunks.

### 3. The Evaluation
We run our 3 configurations against this test set.

```python
from ragas import evaluate

results = evaluate(
    dataset=results_dataset,
    metrics=[context_precision, context_recall, faithfulness]
)
```

### 🔍 Analysis: The "Pareto Frontier"
When you plot the results, you often find a trade-off.
- **Small_Chunks**: High Precision (very specific), but Low Recall (missed the broader context).
- **Large_Chunks**: High Recall, but Low Faithfulness (the LLM got confused by too much text).
- **The Winner**: Maybe `chunk_size=512` is the "Goldilocks" zone for legal text.

---

## 🚀 What Was Achieved?
We transformed RAG development from an art to a science. Instead of arguing about parameters, we have **data**.

- **Before**: "I think larger chunks are better."
- **After**: "Experiments show `size=512` improves Context Recall by 14% without degrading Faithfulness."

---

## 🏁 Summary
RAGAS gives us the eyes to see *inside* our retrieval pipeline.

**Next Step:** We've tested Prompts (Promptfoo), Security (Giskard), Logic (DeepEval), and Retrieval (RAGAS). But what happens when we deploy this to production and it breaks at 2 AM? We need **Observability** with **Arize Phoenix**.
