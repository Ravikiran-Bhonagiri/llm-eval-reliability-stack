# Building Block 1: Model Wrapping System

## 🔍 Let's Investigate: How Giskard Sees Your RAG

You built a RAG system with LangChain, LlamaIndex, or custom code. How does Giskard test it?

**Answer**: Through **model wrapping** - a simple adapter pattern that makes your complex system testable.

---

## 🧠 Theory: The Wrapper Pattern

### The Challenge

Every RAG system is different:
- **LangChain**: Uses chains and retrievers
- **LlamaIndex**: Uses indices and query engines
- **Custom**: Could be anything

Giskard needs a **standard interface** to test them all.

### The Solution: DataFrame In, List Out

```python
def your_rag_function(df: pd.DataFrame) -> list[str]:
    """
    Input: DataFrame with a 'question' column
    Output: List of string responses
    """
    pass
```

**That's it!** Regardless of your internal complexity, Giskard only needs this simple interface.

---

## 🎯 Basic Wrapping

### Example 1: Simple Function

```python
import pandas as pd
from giskard import Model

def answer_question(df: pd.DataFrame) -> list[str]:
    """Minimal RAG function"""
    responses = []
    for question in df["question"].values:
        # Your RAG logic here
        answer = my_rag_pipeline(question)
        responses.append(answer)
    return responses

# Wrap it
giskard_model = Model(
    model=answer_question,
    model_type="text_generation",
    name="My RAG Bot",
    description="Answers questions about company policies",
    feature_names=["question"]
)
```

### Example 2: LangChain Integration

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
import pandas as pd
from giskard import Model

# Your existing LangChain setup
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("my_index", embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever()
)

# Giskard wrapper
def langchain_rag(df: pd.DataFrame) -> list[str]:
    responses = []
    for question in df["question"].values:
        result = qa_chain.run(question)
        responses.append(result)
    return responses

giskard_model = Model(
    model=langchain_rag,
    model_type="text_generation",
    name="LangChain RAG",
    description="Company knowledge base using LangChain",
    feature_names=["question"]
)
```

### Example 3: LlamaIndex Integration

```python
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
import pandas as pd
from giskard import Model

# Your LlamaIndex setup
documents = SimpleDirectoryReader('data').load_data()
index = GPTVectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# Giskard wrapper
def llamaindex_rag(df: pd.DataFrame) -> list[str]:
    responses = []
    for question in df["question"].values:
        response = query_engine.query(question)
        responses.append(str(response))
    return responses

giskard_model = Model(
    model=llamaindex_rag,
    model_type="text_generation",
    name="LlamaIndex RAG",
    description="Technical documentation retrieval",
    feature_names=["question"]
)
```

---

## 🔧 Advanced Wrapping Patterns

### Pattern 1: Multi-Feature Input

If your RAG considers user context:

```python
def contextual_rag(df: pd.DataFrame) -> list[str]:
    """RAG that uses user_role for permission filtering"""
    responses = []
    for _, row in df.iterrows():
        question = row["question"]
        user_role = row.get("user_role", "guest")
        
        # Filter retrieval based on role
        if user_role == "admin":
            docs = retrieve_all_docs(question)
        else:
            docs = retrieve_public_docs(question)
        
        answer = generate_answer(question, docs)
        responses.append(answer)
    return responses

giskard_model = Model(
    model=contextual_rag,
    model_type="text_generation",
    name="Role-Aware RAG",
    description="Filters results based on user permissions",
    feature_names=["question", "user_role"]  # Multiple features!
)
```

### Pattern 2: Conversation History

For chatbots with memory:

```python
def conversational_rag(df: pd.DataFrame) -> list[str]:
    """RAG with conversation context"""
    responses = []
    for _, row in df.iterrows():
        question = row["question"]
        history = row.get("conversation_history", [])
        
        # Incorporate history into retrieval
        contextualized_query = rewrite_with_history(question, history)
        docs = retrieve(contextualized_query)
        answer = generate_answer(question, docs, history)
        
        responses.append(answer)
    return responses

giskard_model = Model(
    model=conversational_rag,
    model_type="text_generation",
    name="Conversational RAG",
    feature_names=["question", "conversation_history"]
)
```

### Pattern 3: Error Handling

Production-ready wrapper with robust error handling:

```python
import logging
from typing import List

logger = logging.getLogger(__name__)

def robust_rag(df: pd.DataFrame) -> List[str]:
    """Production RAG with error handling"""
    responses = []
    
    for idx, row in df.iterrows():
        try:
            question = row["question"]
            
            # Validate input
            if not question or len(question.strip()) == 0:
                responses.append("Error: Empty question")
                continue
            
            # Call RAG pipeline with timeout
            answer = rag_pipeline(question, timeout=10)
            
            # Validate output
            if not answer:
                logger.warning(f"Empty response for: {question}")
                answer = "I don't have enough information to answer that."
            
            responses.append(answer)
            
        except TimeoutError:
            logger.error(f"Timeout on question {idx}")
            responses.append("Error: Request timed out")
            
        except Exception as e:
            logger.error(f"Error on question {idx}: {e}")
            responses.append(f"Error: {type(e).__name__}")
    
    return responses

giskard_model = Model(
    model=robust_rag,
    model_type="text_generation",
    name="Production RAG",
    description="Enterprise RAG with comprehensive error handling"
)
```

---

## 💡 Real-World Example: HR Policy Bot

### The Scenario

You have an HR bot that answers employee questions. It must:
- Filter documents by employee tier (Full-time, Contractor, Intern)
- Never reveal salary information
- Escalate HR violations to human review

### The Implementation

```python
import pandas as pd
from giskard import Model
from typing import Dict, List

class HRPolicyRAG:
    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.escalation_keywords = [
            "harassment", "discrimination", "hostile", 
            "unsafe", "illegal"
        ]
    
    def retrieve_with_permissions(self, question: str, tier: str) -> List[Dict]:
        """Retrieve docs filtered by employee tier"""
        # Search with metadata filtering
        docs = self.vectorstore.similarity_search(
            question,
            k=5,
            filter={"access_level": tier}  # Critical security filter!
        )
        return docs
    
    def check_escalation(self, question: str) -> bool:
        """Detect if question should go to human"""
        return any(kw in question.lower() for kw in self.escalation_keywords)
    
    def generate_answer(self, question: str, docs: List, tier: str) -> str:
        """Generate answer with safety checks"""
        # Check for escalation
        if self.check_escalation(question):
            return "This matter requires speaking with HR directly. Please contact hr@company.com"
        
        # Build prompt with retrieved context
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = f"""You are an HR assistant.
        
Employee Tier: {tier}
Context: {context}

Rules:
- Never reveal salary information
- Never discuss specific employees
- If unsure, suggest contacting HR

Question: {question}
Answer:"""
        
        return self.llm(prompt)

# Initialize
hr_rag = HRPolicyRAG(vectorstore=my_vectorstore, llm=my_llm)

# Giskard wrapper
def hr_bot(df: pd.DataFrame) -> list[str]:
    """Giskard-compatible HR RAG function"""
    responses = []
    for _, row in df.iterrows():
        question = row["question"]
        tier = row.get("employee_tier", "intern")  # Default to most restricted
        
        # Retrieve with permissions
        docs = hr_rag.retrieve_with_permissions(question, tier)
        
        # Generate safe answer
        answer = hr_rag.generate_answer(question, docs, tier)
        
        responses.append(answer)
    
    return responses

# Wrap for Giskard
giskard_model = Model(
    model=hr_bot,
    model_type="text_generation",
    name="HR Policy Assistant",
    description="""
    Answers employee questions about company policies.
    Security requirements:
    - Filters documents by employee tier
    - Never reveals salary/compensation data
    - Escalates sensitive issues to humans
    """,
    feature_names=["question", "employee_tier"]
)
```

### Testing This Model

```python
import giskard

# Run security scan
scan_results = giskard.scan(giskard_model)

# Giskard will automatically test:
# - Can interns access full-time employee docs?
# - Can clever prompts extract salary info?
# - Does escalation work for harassment questions?
```

---

## ✅ Best Practices

### 1. Keep Wrapper Simple

```python
# ❌ Don't do complex logic in wrapper
def bad_wrapper(df):
    # Tons of preprocessing
    # Complex business logic
    # Hard to debug
    pass

# ✅ Do: Keep wrapper thin, logic in classes
def good_wrapper(df):
    return my_rag_class.process(df)
```

### 2. Always Return List[str]

```python
# ❌ Wrong types
def bad(df):
    return "single string"  # Should be list!

def bad2(df):
    return [{"answer": "text"}]  # Should be strings!

# ✅ Correct
def good(df):
    return ["answer1", "answer2", ...]
```

### 3. Handle Edge Cases

```python
def robust_wrapper(df):
    if df.empty:
        return []
    
    if "question" not in df.columns:
        raise ValueError("Missing 'question' column")
    
    return [process(q) for q in df["question"]]
```

---

## 🧪 Testing Your Wrapper

Before scanning, verify your wrapper works:

```python
import pandas as pd

# Create test data
test_df = pd.DataFrame({
    "question": [
        "What is the vacation policy?",
        "How do I request time off?"
    ]
})

# Call your wrapper
try:
    results = your_wrapped_function(test_df)
    assert isinstance(results, list)
    assert len(results) == len(test_df)
    assert all(isinstance(r, str) for r in results)
    print("✅ Wrapper is valid!")
except Exception as e:
    print(f"❌ Wrapper error: {e}")
```

---

## 🎯 What You've Achieved

You now understand:

✅ **Why wrapping is needed** (standard interface)
✅ **How to wrap any RAG** (DataFrame → List pattern)
✅ **LangChain integration** (wrapping chains)
✅ **LlamaIndex integration** (wrapping indices)
✅ **Multi-feature models** (context-aware RAG)
✅ **Error handling** (production-ready patterns)
✅ **Real implementation** (HR Policy Bot example)

---

## 🚦 Next Steps

- **[Next: LLM Scan](./04-llm-scan.md)** - Automated vulnerability detection
- **[Building Block 3: RAGET](./05-raget.md)** - Generate tests from docs
- **[Real Example](./10-real-world-example.md)** - Complete project

---

*"A good wrapper makes the complex simple. Now let's find vulnerabilities!"*
