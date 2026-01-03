# Hyperparameter Optimization - From Guesswork to Science

## 🔍 The Investigation: The $10,000 Question

Your company's RAG system costs $0.02 per query (OpenAI API + compute).

With 500,000 queries/month, that's **$10,000/month**.

You're using:
- `chunk_size=1000`
- `chunk_overlap=200`  
- `top_k=5`

**Question**: What if `chunk_size=512` gives the same quality at half the cost? What if `top_k=3` actually performs better?

**Current approach**: "These numbers feel right" 🤷

**Data-driven approach**: "We tested 27 configurations and found the optimal one" 📊

**Savings potential**: $5,000/month = $60,000/year

**The Problem**: How do you find the best configuration scientifically?

**The Solution**: RAGAS-powered hyperparameter optimization.

---

## 🧠 Theory: What Are We Optimizing?

### The Hyperparameter Space

In RAG systems, you have many knobs to turn:

**Chunking Parameters**:
- `chunk_size`: How large each document chunk is (256, 512, 1024, 2048...)
- `chunk_overlap`: How much chunks overlap (0, 50, 100, 200...)

**Retrieval Parameters**:
- `top_k`: Number of chunks to retrieve (1, 3, 5, 10...)
- `similarity_threshold`: Minimum relevance score (0.5, 0.7, 0.9...)

**Embedding Parameters**:
- `embedding_model`: Which model to use (text-ada-002, text-embedding-3-small...)

**Total combinations**: With just 3 parameters × 4 values each = **64 possible configs**

**Manual testing**: 64 configs × 100 test questions × 2 minutes each = **213 hours** 😱

**Automated with RAGAS**: 64 configs × 100 questions × 2 seconds each = **3.5 hours** ✅

---

### The Optimization Objective

What are we trying to maximize?

**Option 1: Single Metric**
```python
# Maximize faithfulness
objective = lambda config: evaluate(config)['faithfulness']
```

**Option 2: Weighted Combination**
```python
# Balance multiple metrics
def objective(config):
    result = evaluate(config)
    return (
        0.4 * result['faithfulness'] +
        0.3 * result['answer_relevancy'] +
        0.2 * result['context_precision'] +
        0.1 * result['context_recall']
    )
```

**Option 3: Multi-Objective** (Most realistic)
```python
# Pareto optimization
objectives = {
    'quality': lambda c: evaluate(c)['faithfulness'],
    'cost': lambda c: -cost_per_query(c),  # Minimize (negate)
    'latency': lambda c: -avg_latency(c)   # Minimize
}
```

---

## 💻 Grid Search: The Systematic Approach

### Basic Grid Search

Test every combination exhaustively.

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import itertools
import pandas as pd

# Define parameter grid
param_grid = {
    'chunk_size': [256, 512, 1024],
    'chunk_overlap': [50, 100, 200],
    'top_k': [3, 5, 7]
}

# Generate all combinations
configs = [
    dict(zip(param_grid.keys(), values))
    for values in itertools.product(*param_grid.values())
]

print(f"Testing {len(configs)} configurations")
# Output: Testing 27 configurations

# Run evaluation for each
results = []
for config in configs:
    print(f"Testing: {config}")
    
    # Build RAG with this config
    rag = build_rag_system(**config)
    
    # Evaluate with RAGAS
    scores = evaluate(
        rag,
        testset,
        metrics=[faithfulness, answer_relevancy]
    )
    
    results.append({
        **config,
        'faithfulness': scores['faithfulness'],
        'answer_relevancy': scores['answer_relevancy'],
        'avg_score': (scores['faithfulness'] + scores['answer_relevancy']) / 2
    })

# Convert to DataFrame
df = pd.DataFrame(results)
df = df.sort_values('avg_score', ascending=False)

print("\nTop 5 configurations:")
print(df.head())
```

---

### Analyzing Grid Search Results

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Visualize impact of each parameter
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: chunk_size vs performance
df.groupby('chunk_size')['avg_score'].mean().plot(
    kind='bar', ax=axes[0], title='Chunk Size Impact'
)

# Plot 2: overlap vs performance
df.groupby('chunk_overlap')['avg_score'].mean().plot(
    kind='bar', ax=axes[1], title='Overlap Impact'
)

# Plot 3: top_k vs performance
df.groupby('top_k')['avg_score'].mean().plot(
    kind='bar', ax=axes[2], title='Top-K Impact'
)

plt.tight_layout()
plt.savefig('parameter_impact.png')
plt.show()
```

---

### Finding the Optimal Configuration

```python
# Get best config
best_config = df.iloc[0].to_dict()

print(f"🏆 Optimal Configuration:")
print(f"  chunk_size: {best_config['chunk_size']}")
print(f"  chunk_overlap: {best_config['chunk_overlap']}")
print(f"  top_k: {best_config['top_k']}")
print(f"  Average Score: {best_config['avg_score']:.3f}")

# Get worst for comparison
worst_config = df.iloc[-1].to_dict()

improvement = (
    (best_config['avg_score'] - worst_config['avg_score']) 
    / worst_config['avg_score'] * 100
)

print(f"\n📈 Improvement over worst config: {improvement:.1f}%")
```

---

## 🎯 Real-World Example: Legal Search Optimization

### The Scenario

Law firm with 100 court case PDFs. Lawyers need precise case law retrieval.

**Requirements**:
- High faithfulness (can't misquote court opinions)
- High context recall (can't miss relevant precedents)
- Reasonable latency (<3 seconds)

### The Experiment

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from ragas.testset.generator import TestsetGenerator

# Step 1: Load legal documents
loader = DirectoryLoader("court_cases/", glob="**/*.pdf")
docs = loader.load()

# Step 2: Generate test questions
generator = TestsetGenerator.from_langchain(...)
legal_testset = generator.generate_with_langchain_docs(
    docs,
    test_size=50
)

# Step 3: Define search space
param_grid = {
    'chunk_size': [512, 1024, 2048],
    'chunk_overlap': [50, 100, 200],
    'top_k': [3, 5, 10],
    'embedding_model': ['text-embedding-ada-002', 'text-embedding-3-small']
}

# Combinations: 3 × 3 × 3 × 2 = 54 configs

# Step 4: Grid search
def build_legal_rag(chunk_size, chunk_overlap, top_k, embedding_model):
    """Build RAG with given parameters"""
    
    # Split documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    
    # Create vector store
    embeddings = OpenAIEmbeddings(model=embedding_model)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": top_k}
    )
    
    return retriever

# Step 5: Evaluate each config
from tqdm import tqdm

results = []
for config in tqdm(configs):
    rag = build_legal_rag(**config)
    
    scores = evaluate(
        rag,
        legal_testset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
    )
    
    results.append({
        **config,
        **scores,
        'avg_score': sum(scores.values()) / len(scores)
    })

df = pd.DataFrame(results)
```

---

### The Results

```python
# Best configuration
best = df.loc[df['avg_score'].idxmax()]

print("🏆 OPTIMAL CONFIGURATION:")
print(f"  chunk_size: {best['chunk_size']}")
print(f"  chunk_overlap: {best['chunk_overlap']}")  
print(f"  top_k: {best['top_k']}")
print(f"  embedding: {best['embedding_model']}")
print(f"\nSCORES:")
print(f"  Faithfulness: {best['faithfulness']:.3f}")
print(f"  Answer Relevancy: {best['answer_relevancy']:.3f}")
print(f"  Context Precision: {best['context_precision']:.3f}")
print(f"  Context Recall: {best['context_recall']:.3f}")
```

**Sample Output**:
```
🏆 OPTIMAL CONFIGURATION:
  chunk_size: 1024
  chunk_overlap: 100
  top_k: 5
  embedding: text-embedding-3-small

SCORES:
  Faithfulness: 0.923
  Answer Relevancy: 0.887
  Context Precision: 0.845
  Context Recall: 0.891
```

---

### Insights from Results

```python
# Analyze which parameters matter most
import numpy as np

# Correlation analysis
correlations = df[['chunk_size', 'chunk_overlap', 'top_k']].corrwith(
    df['avg_score']
)

print("Parameter Impact (Correlation with Score):")
print(correlations.sort_values(ascending=False))
```

**Sample Output**:
```
top_k            0.45  # Most important!
chunk_overlap    0.32
chunk_size      -0.15  # Larger not always better
```

**Insights**:
- `top_k` matters most (retrieve more chunks = better recall)
- Overlap helps (prevents splitting important sentences)
- Larger chunks don't always improve quality (context overload)

---

## 📊 Multi-Objective Optimization

Often you care about multiple objectives that conflict:

```
High Quality ⬆️  vs  Low Cost ⬇️
High Recall ⬆️   vs  Low Latency ⬇️
```

### Pareto Frontier Analysis

```python
import matplotlib.pyplot as plt

# Plot quality vs cost
plt.figure(figsize=(10, 6))
plt.scatter(
    df['avg_score'],
    df['estimated_cost'],
    s=100,
    alpha=0.6,
    c=df['chunk_size'],
    cmap='viridis'
)

plt.xlabel('Quality (Average Score)')
plt.ylabel('Cost per 1000 Queries ($)')
plt.title('Quality-Cost Tradeoff')
plt.colorbar(label='Chunk Size')

# Identify Pareto optimal points
from scipy.spatial import ConvexHull

# Points that are not dominated by any other point
pareto_points = []
for i, row in df.iterrows():
    dominated = False
    for j, other in df.iterrows():
        if i != j:
            # Other point is better in all objectives
            if (other['avg_score'] >= row['avg_score'] and 
                other['estimated_cost'] <= row['estimated_cost']):
                if (other['avg_score'] > row['avg_score'] or 
                    other['estimated_cost'] < row['estimated_cost']):
                    dominated = True
                    break
    
    if not dominated:
        pareto_points.append(i)

# Highlight Pareto optimal configs
pareto_df = df.loc[pareto_points]
plt.scatter(
    pareto_df['avg_score'],
    pareto_df['estimated_cost'],
    s=200,
    marker='*',
    c='red',
    label='Pareto Optimal'
)

plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("\n⭐ Pareto Optimal Configurations:")
print(pareto_df[['chunk_size', 'top_k', 'avg_score', 'estimated_cost']])
```

**Interpretation**:
```
Config A: Score=0.92, Cost=$0.015  ← High quality, high cost
Config B: Score=0.87, Cost=$0.008  ← Medium quality, low cost  
Config C: Score=0.85, Cost=$0.012  ← Dominated (worse than B)

Choose A or B depending on budget vs quality priority
```

---

## 🚀 Bayesian Optimization (Advanced)

Grid search tests every combination. Bayesian optimization is smarter - it learns which areas of the parameter space are promising.

**Advantage**: Finds good config with fewer evaluations.

```python
from skopt import gp_minimize
from skopt.space import Integer, Categorical
from skopt.utils import use_named_args

# Define search space
space = [
    Integer(256, 2048, name='chunk_size'),
    Integer(0, 300, name='chunk_overlap'),
    Integer(1, 10, name='top_k')
]

# Define objective function
@use_named_args(space)
def objective(chunk_size, chunk_overlap, top_k):
    """What we're trying to maximize"""
    
    # Build RAG
    rag = build_rag_system(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k
    )
    
    # Evaluate
    scores = evaluate(rag, testset, metrics=[faithfulness, answer_relevancy])
    
    # Return negative (we're minimizing)
    avg_score = (scores['faithfulness'] + scores['answer_relevancy']) / 2
    return -avg_score  # Negative because we minimize

# Run Bayesian optimization
result = gp_minimize(
    objective,
    space,
    n_calls=30,  # Only 30 evaluations instead of 64!
    random_state=42,
    verbose=True
)

print(f"Best parameters: {result.x}")
print(f"Best score: {-result.fun}")  # Negate back
```

**Comparison**:
```
Grid Search:   64 evaluations → score 0.89
Bayesian Opt:  30 evaluations → score 0.88

Result: 54% fewer evaluations, nearly same quality!
```

---

## 🔧 Production Deployment

### Step 1: Validate on Hold-Out Set

```python
# Don't just optimize on your test set!

# Split testset
train_testset = testset[:40]  # 80%
holdout_testset = testset[40:]  # 20%

# Optimize on train
best_config = optimize_on_testset(train_testset)

# Validate on holdout
final_scores = evaluate(
    build_rag(**best_config),
    holdout_testset,
    metrics=[faithfulness, answer_relevancy]
)

print(f"Hold-out validation: {final_scores}")

# Ensure no overfitting
if final_scores['faithfulness'] < 0.8:
    print("⚠️ Performance dropped on hold-out set!")
```

---

### Step 2: A/B Test in Production

```python
# Don't just deploy! Test with real users first.

import random

def get_rag_for_user(user_id):
    """50/50 split between configs"""
    
    if hash(user_id) % 2 == 0:
        # Control: Current config
        return build_rag(chunk_size=1000, top_k=5)
    else:
        # Treatment: Optimized config
        return build_rag(chunk_size=512, top_k=3)

# Monitor both groups
def log_query(user_id, query, answer, feedback):
    """Track user feedback"""
    variant = "optimized" if hash(user_id) % 2 == 1 else "control"
    
    log_to_db({
        "user_id": user_id,
        "variant": variant,
        "query": query,
        "answer": answer,
        "feedback": feedback,  # User thumbs up/down
        "timestamp": datetime.now()
    })

# After 1000 queries each
analytics = analyze_ab_test()
print(f"Control satisfaction: {analytics['control']['thumbs_up_rate']}")
print(f"Optimized satisfaction: {analytics['optimized']['thumbs_up_rate']}")

# Deploy winner
if analytics['optimized']['thumbs_up_rate'] > analytics['control']['thumbs_up_rate']:
    deploy_to_production(optimized_config)
```

---

### Step 3: Continuous Optimization

```python
import schedule

def weekly_optimization():
    """Re-optimize as documents change"""
    
    # Generate fresh testset
    latest_docs = load_latest_documents()
    testset = generate_testset(latest_docs, test_size=50)
    
    # Run optimization
    best_config = grid_search(testset)
    
    # Compare to current production config
    current_scores = evaluate(production_rag, testset)
    new_scores = evaluate(build_rag(**best_config), testset)
    
    improvement = new_scores['avg_score'] - current_scores['avg_score']
    
    if improvement > 0.05:  # 5% improvement
        print(f"📈 Found better config (+{improvement:.1%})")
        trigger_ab_test(best_config)
    else:
        print("Current config still optimal")

# Run every Monday
schedule.every().monday.at("02:00").do(weekly_optimization)
```

---

## 📈 Cost-Performance Analysis

### Calculating True Costs

```python
def calculate_config_cost(config, queries_per_month=100000):
    """Estimate monthly cost"""
    
    # Embedding costs
    avg_chunk_count = 1000000 / config['chunk_size']  # Assuming 1M tokens total
    embedding_cost = (avg_chunk_count / 1000) * 0.0001  # $0.0001 per 1K tokens
    
    # LLM generation costs (based on context size)
    context_tokens = config['top_k'] * config['chunk_size']
    cost_per_query = (context_tokens / 1000) * 0.002  # GPT-3.5 pricing
    monthly_llm_cost = cost_per_query * queries_per_month
    
    total_monthly_cost = embedding_cost + monthly_llm_cost
    
    return {
        'embedding_cost': embedding_cost,
        'monthly_llm_cost': monthly_llm_cost,
        'total_monthly_cost': total_monthly_cost,
        'cost_per_query': total_monthly_cost / queries_per_month
    }

# Compare configs
configs_to_compare = [
    {'name': 'Current', 'chunk_size': 1000, 'top_k': 5},
    {'name': 'Optimized', 'chunk_size': 512, 'top_k': 3},
]

for config in configs_to_compare:
    costs = calculate_config_cost(config)
    scores = evaluate(build_rag(**config), testset)
    
    print(f"\n{config['name']} Configuration:")
    print(f"  Monthly Cost: ${costs['total_monthly_cost']:.2f}")
    print(f"  Quality Score: {scores['avg_score']:.3f}")
    print(f"  Cost per Point of Quality: ${costs['total_monthly_cost'] / scores['avg_score']:.2f}")
```

---

## 🧪 Hands-On Exercise

**Challenge**: Optimize a RAG system for your use case

**Scenario**: Customer support knowledge base

**Task**:
1. Generate 30 test questions
2. Define parameter grid (chunk_size, overlap, top_k)
3. Run grid search
4. Identify optimal configuration
5. Calculate cost savings vs baseline

**Starter Code**:
```python
# Your code here
param_grid = {
    'chunk_size': [256, 512, 1024],
    'chunk_overlap': [0, 50, 100],
    'top_k': [3, 5, 7]
}

# Hint: 27 configurations to test
# Expected time: ~30 minutes for 30 questions × 27 configs
```

---

## ✅ What You've Achieved

You now understand:

✅ **Grid search** for systematic optimization  
✅ **Multi-objective optimization** (quality vs cost vs latency)  
✅ **Pareto frontier** analysis  
✅ **Bayesian optimization** for efficiency  
✅ **Production deployment** (validation, A/B testing)  
✅ **Continuous optimization** workflows  
✅ **Cost-performance** analysis  
✅ **Real legal search** case study  

**Impact**: You can now scientifically find the optimal RAG configuration instead of guessing!

---

## 🚦 Next Steps

You've optimized hyperparameters. Want to create custom evaluation metrics for your domain?

- **[Next: Advanced Metrics](./08-advanced-metrics.md)** - Custom evaluators
- **[Back: Test Generation](./06-synthetic-test-generation.md)** - Review test creation
- **[Real Example](./10-real-world-example.md)** - Complete optimization workflow

---

*From "these values feel right" to "we tested 54 configurations and chose the optimal one." From guesswork to science.* ✨
