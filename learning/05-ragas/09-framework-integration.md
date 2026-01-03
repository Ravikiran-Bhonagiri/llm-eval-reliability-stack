# Framework Integration - LangChain & LlamaIndex

## 🔍 The Investigation: Evaluating Your Existing RAG

You already built a RAG system using LangChain or LlamaIndex.

**Question**: How do you evaluate it with RAGAS without rewriting everything?

**Answer**: RAGAS has native integrations!

---

## 🧠 Integration Philosophy

RAGAS is **framework-agnostic** but provides helpers for popular frameworks:

- **LangChain**: Direct chain evaluation
- **LlamaIndex**: Query engine evaluation
- **Custom/Other**: Adapt with wrapper functions

**Goal**: Eval uate your existing RAG with minimal code changes.

---

## 💻 LangChain Integration

### Basic LangChain RAG Evaluation

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from ragas.integrations.langchain import evaluate

# 1. Build your LangChain RAG (as usual)
loader = TextLoader("company_docs.txt")
documents = loader.load()

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)

llm = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
)

# 2. Create test questions
questions = [
    "What's the vacation policy?",
    "How do I submit expenses?",
    "What are the remote work guidelines?"
]

# 3. Evaluate with RAGAS!
from ragas.metrics import faithfulness, answer_relevancy

results = evaluate(
    qa_chain,
    questions=questions,
    metrics=[faithfulness, answer_relevancy]
)

print(results)
```

**Output**:
```python
{
    'faithfulness': 0.87,
    'answer_relevancy': 0.82,
    'question_count': 3
}
```

---

### Advanced: Custom Chain Evaluation

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Custom chain with specific prompt
template = """
You are a helpful HR assistant. Answer based on this context:

Context: {context}

Question: {question}

Answer:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

custom_chain = LLMChain(llm=llm, prompt=prompt)

# Evaluate with retriever
from ragas.integrations.langchain import evaluate_chain

results = evaluate_chain(
    chain=custom_chain,
    retriever=vectorstore.as_retriever(),
    questions=questions,
    metrics=[faithfulness, answer_relevancy, context_precision]
)
```

---

### Evaluating with Ground Truth

```python
from datasets import Dataset

# Prepare dataset with expected answers
data = {
    "question": [
        "What's the vacation policy?",
        "How do I reset my password?"
    ],
    "ground_truth": [
        "20 vacation days per year",
        "Click 'Forgot Password' on the login page"
    ]
}

test_dataset = Dataset.from_dict(data)

# Evaluate
from ragas import evaluate
from ragas.metrics import answer_correctness

results = evaluate(
    qa_chain,
    test_dataset,
    metrics=[answer_correctness, faithfulness]
)
```

---

## 🦙 LlamaIndex Integration

### Basic LlamaIndex Evaluation

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from ragas.integrations.llama_index import evaluate

# 1. Build your LlamaIndex RAG
documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 2. Test questions
questions = [
    "What is the company mission?",
    "How many employees work here?",
    "What products do we sell?"
]

# 3. Evaluate with RAGAS
from ragas.metrics import faithfulness, answer_relevancy

results = evaluate(
    query_engine,
    questions=questions,
    metrics=[faithfulness, answer_relevancy]
)

print(results)
```

---

### Custom LlamaIndex Query Engine

```python
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import get_response_synthesizer

# Custom retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,  # Get more docs
)

# Custom response synthesizer
response_synthesizer = get_response_synthesizer(
    response_mode="tree_summarize",  # Different synthesis method
)

# Custom query engine
custom_query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

# Evaluate custom engine
results = evaluate(
    custom_query_engine,
    questions=questions,
    metrics=[faithfulness, answer_relevancy, context_precision]
)
```

---

## 🔧 Framework-Agnostic Evaluation

If you're not using LangChain or LlamaIndex, wrap your RAG:

```python
from ragas import evaluate
from datasets import Dataset

# Your custom RAG function
def my_custom_rag(question):
    # Your retrieval logic
    contexts = retrieve_documents(question)
    
    # Your generation logic
    answer = generate_answer(question, contexts)
    
    return {
        'answer': answer,
        'contexts': contexts
    }

# Prepare dataset
questions = ["Q1", "Q2", "Q3"]
data = {
    'question': [],
    'answer': [],
    'contexts': []
}

for q in questions:
    result = my_custom_rag(q)
    data['question'].append(q)
    data['answer'].append(result['answer'])
    data['contexts'].append(result['contexts'])

dataset = Dataset.from_dict(data)

# Evaluate
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy]
)
```

---

## 📊 Comparative Evaluation

Compare different frameworks or configurations:

```python
# Test 3 different implementations
setups = {
    "LangChain_GPT4": langchain_qa_gpt4,
    "LangChain_Claude": langchain_qa_claude,
    "LlamaIndex_GPT4": llamaindex_query_engine
}

comparison = {}
for name, system in setups.items():
    results = evaluate(
        system,
        questions=test_questions,
        metrics=[faithfulness, answer_relevancy]
    )
    comparison[name] = results

# Display comparison
import pandas as pd
df = pd.DataFrame(comparison).T
print(df)
```

**Output**:
```
                    faithfulness  answer_relevancy
LangChain_GPT4            0.92          0.88
LangChain_Claude          0.89          0.91
LlamaIndex_GPT4           0.94          0.85
```

---

## ✅ What You've Achieved

✅ **LangChain integration** - Evaluate chains directly  
✅ **LlamaIndex integration** - Evaluate query engines  
✅ **Framework-agnostic** approach  
✅ **Comparative evaluation** across implementations  

---

## 🚦 Next Steps

- **[Next: Real-World Example](./10-real-world-example.md)** - Complete Legal Search project
- **[Back: Advanced Metrics](./08-advanced-metrics.md)** - Custom evaluators
- **[Summary](./11-summary.md)** - Module recap

---

*Evaluate any RAG, regardless of how it's built.* ✨
