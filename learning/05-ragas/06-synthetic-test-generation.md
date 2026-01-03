# Synthetic Test Generation - Automatic Test Creation

## 🔍 The Investigation: The Cold Start Problem

You just built a RAG system for your company's 500-page employee handbook.

**Question**: How do you create test questions?

**Option A**: Manual Creation
```
Day 1: Write 10 questions (2 hours)
Day 2: Write 10 more questions (2 hours)
Day 3: Running out of ideas...
Day 10: Total of 50 questions, completely exhausted
```

**Option B**: RAGAS Synthetic Generation
```
Minute 1: Run testset generator
Minute 15: Have 100 diverse, high-quality questions
```

**The Problem**: Manual test creation doesn't scale.

**The Solution**: RAGAS TestsetGenerator - automatically creates questions from your documents.

---

## 🧠 Theory: How Synthetic Generation Works

### The Magic: Documents → Questions

RAGAS reads your documents and generates three types of questions:

1. **Simple** - Direct factual questions
2. **Reasoning** - Multi-step logic required
3. **Multi-Context** - Needs info from multiple documents

**The Innovation**: Questions evolve from simple to complex using "evolution strategies."

---

### Evolution Strategies Explained

```
SIMPLE QUESTION
↓ Evolution: Add reasoning
REASONING QUESTION  
↓ Evolution: Add multi-hop
MULTI-CONTEXT QUESTION
↓ Evolution: Add conditions
CONDITIONAL QUESTION
```

**Example Evolution Chain**:

**Level 1 - Simple**: 
> "What is the vacation policy?"

**Level 2 - Reasoning**:
> "If I joined in March and want 10 days off in December, am I eligible?"

**Level 3 - Multi-Context**:
> "How does the vacation policy interact with the remote work policy for international employees?"

**Level 4 - Conditional**:
> "Given the sabbatical policy and vacation policy, what's the maximum time off an employee with 5 years tenure can take in one year?"

---

## 💻 Basic Implementation

### Step 1: Prepare Your Documents

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load your documents
loader = PyPDFLoader("employee_handbook.pdf")
documents = loader.load()

# Split into chunks (RAGAS works better with smaller chunks)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

print(f"Loaded {len(chunks)} chunks")
```

---

### Step 2: Generate Test Set

```python
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Configure generator
generator_llm = ChatOpenAI(model="gpt-3.5-turbo")
critic_llm = ChatOpenAI(model="gpt-4")  # For quality control
embeddings = OpenAIEmbeddings()

generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

# Generate testset
testset = generator.generate_with_langchain_docs(
    chunks,
    test_size=50,  # Generate 50 questions
    distributions={
        simple: 0.4,        # 40% simple questions (20 questions)
        reasoning: 0.4,     # 40% reasoning (20 questions)  
        multi_context: 0.2  # 20% multi-context (10 questions)
    }
)

print(f"Generated {len(testset)} test cases")
```

---

### Step 3: Inspect Generated Questions

```python
# Convert to pandas for easy viewing
test_df = testset.to_pandas()

print(test_df.head())

# Columns:
# - question: The generated question
# - contexts: Relevant document chunks
# - ground_truth: Expected answer (also generated)
# - evolution_type: What strategy was used
```

---

### Step 4: Save for Later Use

```python
# Save to file
testset.save("employee_handbook_tests.jsonl")

# Load later
from ragas.testset import Testset
loaded_testset = Testset.load("employee_handbook_tests.jsonl")
```

---

## 🎯 Evolution Strategies Deep Dive

### 1. Simple Evolution

Generates straightforward factual questions.

**Input Document**:
> "Employees receive 20 vacation days per year. This increases to 25 days after 5 years of service."

**Generated Questions**:
- "How many vacation days do employees receive?"
- "When do employees get 25 vacation days?"
- "What is the vacation day policy?"

**Characteristics**:
- ✅ Easy to answer
- ✅ Single fact needed
- ✅ Tests basic recall

**Use Case**: Smoke tests, sanity checks

---

### 2. Reasoning Evolution

Requires multi-step logic.

**Input Document** (same as above)

**Generated Questions**:
- "If an employee has worked for 4 years and takes 15 days vacation, how many days will they have remaining?"
- "An employee joined on January 1, 2019. In 2024, how many vacation days are they entitled to?"
- "What's the difference in vacation days between a new employee and one with 6 years tenure?"

**Characteristics**:
- ✅ Multi-step reasoning
- ✅ Math or logic required
- ✅ Tests understanding, not just recall

**Use Case**: Testing actual comprehension

---

### 3. Multi-Context Evolution

Needs information from multiple documents.

**Input Documents**:

**Doc 1**: "Employees receive 20 vacation days per year."

**Doc 2**: "Remote workers can work from any location up to 30 days per year."

**Generated Questions**:
- "Can an employee use vacation days while working remotely?"
- "How many total days can an employee be away from the main office combining vacation and remote work?"
- "What's the policy overlap between vacation time and remote work allowance?"

**Characteristics**:
- ✅ Tests retrieval (must find multiple docs)
- ✅ Tests synthesis (combine info)
- ✅ Realistic complex queries

**Use Case**: Production-level evaluation

---

### 4. Conditional Evolution

Adds "if-then" complexity.

**Generated Questions**:
- "If an employee is remote and wants to take vacation, do both policies apply?"
- "Given that an employee has 5 years tenure and works remotely, what's their maximum time away from office?"
- "Under what conditions would an employee have more than 40 days of flexibility?"

**Characteristics**:
- ✅ Most complex
- ✅ Tests edge cases
- ✅ Discovers policy gaps

**Use Case**: Stress testing, finding system limits

---

## 📊 Controlling Question Quality

### Quality Parameters

```python
generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

testset = generator.generate_with_langchain_docs(
    chunks,
    test_size=100,
    distributions={
        simple: 0.3,
        reasoning: 0.5,
        multi_context: 0.2
    },
    # Quality controls
    raise_exceptions=False,  # Don't fail on bad questions
    run_config={
        "max_retries": 3,     # Retry failed generations
        "timeout": 180        # Timeout per question
    }
)
```

---

### Filtering Low-Quality Questions

```python
# Review generated questions
test_df = testset.to_pandas()

# Remove too-short questions
test_df = test_df[test_df['question'].str.len() > 20]

# Remove questions without context
test_df = test_df[test_df['contexts'].str.len() > 0]

# Remove vague questions
vague_words = ['this', 'that', 'thing', 'stuff']
mask = ~test_df['question'].str.lower().str.contains('|'.join(vague_words))
test_df = test_df[mask]

print(f"Filtered from {len(testset)} to {len(test_df)} questions")
```

---

### Manual Review Process

```python
# Sample questions for review
sample = test_df.sample(10)

for idx, row in sample.iterrows():
    print(f"\nQuestion: {row['question']}")
    print(f"Type: {row['evolution_type']}")
    print(f"Contexts: {len(row['contexts'])} documents")
    print(f"Ground truth: {row['ground_truth']}")
    print("-" * 80)
    
    # Manual quality rating
    rating = input("Quality (1-5): ")
    # Store ratings for later filtering
```

---

## 🎨 Advanced Generation Techniques

### 1. Domain-Specific Instructions

Guide generation toward your domain:

```python
# For medical domain
generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

# Add domain context
testset = generator.generate_with_langchain_docs(
    medical_docs,
    test_size=50,
    # Domain-specific prompt engineering
    critic_persona="medical accuracy reviewer",
    language="en"
)
```

---

### 2. Seeding with Example Questions

Provide examples to guide style:

```python
# Example questions you've written
seed_questions = [
    {
        "question": "What are the contraindications for aspirin?",
        "answer": "Aspirin is contraindicated in patients with active bleeding, severe liver disease, or allergy to NSAIDs."
    },
    # More examples...
]

# RAGAS will generate similar-style questions
# (Feature may vary by version - check docs)
```

---

### 3. Targeted Generation by Topic

Generate questions for specific sections:

```python
from langchain.document_loaders import PyPDFLoader

# Load only specific sections
loader = PyPDFLoader("handbook.pdf")
all_docs = loader.load()

# Filter to specific topic
hr_policy_docs = [
    doc for doc in all_docs 
    if "human resources" in doc.page_content.lower()
]

# Generate questions only about HR
hr_testset = generator.generate_with_langchain_docs(
    hr_policy_docs,
    test_size=30
)
```

---

## 🔧 Production Workflows

### Workflow 1: Continuous Test Generation

```python
import schedule
import time

def generate_weekly_tests():
    """Generate new tests weekly as docs change"""
    
    # Load latest documents
    docs = load_latest_documents()
    
    # Generate tests
    testset = generator.generate_with_langchain_docs(
        docs,
        test_size=50
    )
    
    # Save with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d")
    testset.save(f"tests_{timestamp}.jsonl")
    
    # Run evaluation
    results = evaluate(your_rag, testset)
    
    # Alert if performance drops
    if results['faithfulness'] < 0.8:
        send_alert("RAG performance degraded!")

# Schedule weekly
schedule.every().monday.at("02:00").do(generate_weekly_tests)
```

---

### Workflow 2: Version-Specific Test Suites

```python
# Generate tests for each document version
versions = ["v1.0", "v2.0", "v3.0"]

for version in versions:
    docs = load_documents(version)
    
    testset = generator.generate_with_langchain_docs(
        docs,
        test_size=100
    )
    
    testset.save(f"tests_{version}.jsonl")
    
    # Compare performance across versions
    results = evaluate(your_rag_v2, testset)
    print(f"Version {version}: {results['faithfulness']}")
```

---

### Workflow 3: Regression Test Suite

```python
# Generate once, use forever
initial_testset = generator.generate_with_langchain_docs(
    docs,
    test_size=200,  # Larger suite
    distributions={
        simple: 0.2,
        reasoning: 0.5,         # Heavy on reasoning
        multi_context: 0.3
    }
)

# Save as "golden" test suite
initial_testset.save("regression_tests.jsonl")

# Use in CI/CD
def test_rag():
    testset = Testset.load("regression_tests.jsonl")
    results = evaluate(current_rag, testset)
    
    # Fail if below baseline
    assert results['faithfulness'] > 0.85, "Faithfulness regression!"
    assert results['answer_relevancy'] > 0.80, "Relevance regression!"
```

---

## 📈 Quality Assessment

### Measuring Testset Quality

```python
def assess_testset_quality(testset):
    """Evaluate the generated testset itself"""
    
    df = testset.to_pandas()
    
    metrics = {
        "total_questions": len(df),
        "avg_question_length": df['question'].str.len().mean(),
        "unique_questions": df['question'].nunique(),
        "evolution_distribution": df['evolution_type'].value_counts().to_dict(),
        "avg_contexts_per_question": df['contexts'].apply(len).mean()
    }
    
    # Quality checks
    issues = []
    
    if metrics['avg_question_length'] < 30:
        issues.append("⚠️ Questions too short")
    
    if metrics['unique_questions'] < len(df) * 0.95:
        issues.append("⚠️ Too many duplicate questions")
    
    if metrics['avg_contexts_per_question'] < 1:
        issues.append("⚠️ Questions lack context")
    
    return metrics, issues

# Assess
metrics, issues = assess_testset_quality(testset)
print(f"Quality Metrics: {metrics}")
if issues:
    print("Issues found:")
    for issue in issues:
        print(f"  {issue}")
```

---

## 🎯 Real-World Example: Legal Document Test Generation

### Scenario

Law firm has 100 court case PDFs. Need to test legal research RAG.

```python
from langchain.document_loaders import DirectoryLoader
from ragas.testset.generator import TestsetGenerator

# Load all case files
loader = DirectoryLoader(
    "court_cases/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # Larger for legal text
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)

print(f"Loaded {len(chunks)} chunks from {len(docs)} cases")

# Generate legal-focused questions
testset = generator.generate_with_langchain_docs(
    chunks,
    test_size=100,
    distributions={
        simple: 0.2,          # Basic facts
        reasoning: 0.5,       # Legal reasoning
        multi_context: 0.3    # Cross-case comparison
    }
)

# Review sample
df = testset.to_pandas()
print("\nSample Generated Questions:")
print(df[['question', 'evolution_type']].head(10))
```

**Sample Output**:
```
Question: What was the verdict in Smith v. Jones (2023)?
Type: simple

Question: Based on the precedent set in Case A and the facts in Case B, what would likely be the ruling?
Type: reasoning

Question: How do the dissenting opinions in Cases X, Y, and Z differ on the interpretation of Section 230?
Type: multi_context
```

---

## 🐛 Troubleshooting

### Issue 1: Generic or Vague Questions

**Symptom**: Questions like "What is this about?"

**Cause**: Documents lack structure or clear topics

**Fix**: Improve document chunking

```python
# Add metadata to guide generation
from langchain.schema import Document

docs_with_metadata = []
for chunk in chunks:
    docs_with_metadata.append(
        Document(
            page_content=chunk.page_content,
            metadata={
                "source": chunk.metadata.get("source"),
                "topic": extract_topic(chunk),  # Custom function
                "section": chunk.metadata.get("section")
            }
        )
    )

# Generate with better context
testset = generator.generate_with_langchain_docs(
    docs_with_metadata,
    test_size=50
)
```

---

### Issue 2: Too Many Simple Questions

**Symptom**: 80% of questions are simple despite setting 40%

**Cause**: Documents don't support complex reasoning

**Fix**: Adjust distributions and increase chunk size

```python
# Larger chunks for more context
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Increased from 1000
    chunk_overlap=300
)

# Force more complex questions
testset = generator.generate_with_langchain_docs(
    chunks,
    test_size=50,
    distributions={
        simple: 0.1,           # Minimize simple
        reasoning: 0.6,        # Emphasize reasoning
        multi_context: 0.3
    }
)
```

---

### Issue 3: Generation Fails or Hangs

**Symptom**: Timeout errors or no questions generated

**Cause**: LLM struggles with documents

**Fix**: Use better LLM and add error handling

```python
from langchain_openai import ChatOpenAI

# Use GPT-4 for generation (better than 3.5)
generator_llm = ChatOpenAI(model="gpt-4", temperature=0.7)
critic_llm = ChatOpenAI(model="gpt-4", temperature=0.3)

generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

# Add timeout and retries
testset = generator.generate_with_langchain_docs(
    chunks,
    test_size=50,
    raise_exceptions=False,  # Continue on failures
    run_config={
        "max_retries": 3,
        "timeout": 300  # 5 minutes per batch
    }
)
```

---

## 🧪 Hands-On Exercise

**Challenge**: Generate a test suite for a product documentation site

**Setup**:
1. Download sample product docs (use any open-source project README)
2. Generate 30 test questions
3. Review for quality
4. Use to evaluate a RAG system

**Code Skeleton**:
```python
from langchain.document_loaders import WebBaseLoader
from ragas.testset.generator import TestsetGenerator

# Load docs
loader = WebBaseLoader("https://example.com/docs")
docs = loader.load()

# YOUR CODE HERE:
# 1. Split documents
# 2. Configure generator
# 3. Generate 30 questions
# 4. Filter for quality
# 5. Save results
```

---

## ✅ What You've Achieved

You now understand:

✅ **Synthetic test generation** fundamentals  
✅ **Evolution strategies** (simple → reasoning → multi-context)  
✅ **Quality control** for generated questions  
✅ **Production workflows** (continuous generation, versioning)  
✅ **Domain-specific generation** techniques  
✅ **Troubleshooting** common issues  
✅ **Quality assessment** of testsets  

**Impact**: You can now generate 100+ diverse test questions in minutes instead of days!

---

## 🚦 Next Steps

Now you have test questions. How do you use them to optimize your RAG?

- **[Next: Hyperparameter Optimization](./07-hyperparameter-optimization.md)** - Find optimal chunk_size
- **[Back: Context Metrics](./05-context-metrics.md)** - Review retrieval quality
- **[Real Example](./10-real-world-example.md)** - See full workflow

---

*From manual test writing to automatic generation. From dozens of questions to hundreds.* ✨
