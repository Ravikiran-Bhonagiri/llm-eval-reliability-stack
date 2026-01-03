# Answer Relevance - Does It Actually Answer the Question?

## 🔍 The Investigation: The Evasive Assistant

**User asks**: "What's the CEO's salary?"

**RAG answers**: "The company has a comprehensive executive compensation program that includes base salary, equity grants, and performance bonuses. Our compensation committee ensures competitive market rates while aligning with shareholder interests."

**Question**: Did the system answer the question?

**Answer**: **NO**. It dodged with corporate speak.

**The Problem**: How do you detect non-answers automatically?

**The Solution**: RAGAS Answer Relevance Metric.

---

## 🧠 Theory: What is Answer Relevance?

### Definition

**Answer Relevance** measures how well the generated answer addresses the original question.

**Key Insight**: If the answer truly addresses the question, you should be able to reconstruct the original question from the answer.

**Formula**:
```
Answer Relevance = Semantic Similarity(
    Original Question,
    Average(Generated Questions from Answer)
)

Score Range: 0.0 (completely irrelevant) to 1.0 (perfectly relevant)
```

---

### Why It Matters

**Irrelevant answers destroy user experience**:
- User asks about pricing → Gets product history
- User asks "how" → Gets philosophical "why"
- User needs specifics → Gets generalities

**Answer Relevance ensures**:
- Questions get answered (not evaded)
- Answers stay on-topic
- Users don't leave frustrated

---

## 🔬 The Reverse Question Algorithm

RAGAS uses a clever approach: **reverse question generation**.

### The Process

```
Step 1: GENERATION
Answer → Generate Multiple Questions

Step 2: COMPARISON
Compare Generated Questions to Original Question

Step 3: SCORING
Average Similarity = Relevance Score
```

---

### Step-by-Step Example

**Original Question**: "What's the capital of France?"

**Answer**: "Paris is the capital of France, known for the Eiffel Tower."

**Step 1 - Generate Questions from Answer**:

The LLM reads the answer and generates questions it could answer:

1. "What is the capital of France?"
2. "Where is the Eiffel Tower located?"
3. "What city is known for the Eiffel Tower?"

**Step 2 - Compare to Original**:

```
Original: "What's the capital of France?"

Generated Q1: "What is the capital of France?" 
→ Similarity: 0.98 ✅ (nearly identical)

Generated Q2: "Where is the Eiffel Tower?"
→ Similarity: 0.40 ⚠️ (related but different)

Generated Q3: "What city has the Eiffel Tower?"
→ Similarity: 0.45 ⚠️ (related but different)
```

**Step 3 - Calculate Score**:

```python
average_similarity = (0.98 + 0.40 + 0.45) / 3 = 0.61

Answer Relevance = 0.61
```

**Interpretation**: Answer is 61% relevant. It answers the question but adds extra info about Eiffel Tower.

---

## 💻 Practical Implementation

### Basic Usage

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy

data = {
    "question": ["What's the CEO's salary?"],
    "answer": ["The company has a comprehensive compensation program..."],
    "contexts": [["CEO John Smith earned $2.5M in 2023"]]  # Retrieved context
}

dataset = Dataset.from_dict(data)

result = evaluate(dataset, metrics=[answer_relevancy])

print(result)
# Output: {'answer_relevancy': 0.23}  # LOW! Evasive answer
```

---

### Detailed Example with Debugging

```python
from ragas.metrics import answer_relevancy
from datasets import Dataset

# Question about specific feature
question = "Does this product support dark mode?"

# Three different answer qualities
answers = {
    "evasive": "Our product offers many customization options for user preferences.",
    "partial": "The product has theme settings. Dark mode is available in premium tier.",
    "perfect": "Yes, dark mode is supported. Enable it in Settings > Appearance."
}

contexts = [["Product supports dark mode in premium tier only"]] * 3

# Evaluate each
for name, answer in answers.items():
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts[0]]
    }
    
    result = evaluate(
        Dataset.from_dict(data),
        metrics=[answer_relevancy]
    )
    
    print(f"{name}: {result['answer_relevancy']:.2f}")

# Output:
# evasive: 0.31   # ❌ Doesn't answer
# partial: 0.68   # ⚠️ Answers but verbose
# perfect: 0.95   # ✅ Direct answer
```

---

## 🔍 Debugging: Why Is My Score Low?

###  Scenario 1: The Rambler

**Question**: "What's the refund policy?"

**Answer**: "Our company was founded in 2010 with a mission to provide excellent customer service. We believe in transparency and fairness. Our refund policy, which was updated last year after customer feedback, allows returns within 30 days."

**Generated Questions** (what LLM infers):
1. "When was the company founded?"
2. "What's the company's mission?"
3. "What's the refund timeframe?"

**Similarity Scores**:
- Q1 vs Original: 0.15 (irrelevant)
- Q2 vs Original: 0.12 (irrelevant)
- Q3 vs Original: 0.75 (relevant!)

**Average**: (0.15 + 0.12 + 0.75) / 3 = **0.34** ❌

**Problem**: Too much fluff, not enough signal.

**Fix**: Instruct LLM to be concise.

---

### Scenario 2: The Dodger

**Question**: "What's the pricing for the enterprise plan?"

**Answer**: "Pricing varies based on customer needs. Please contact our sales team for a customized quote tailored to your organization's requirements."

**Generated Questions**:
1. "How does pricing vary?"
2. "How to contact sales?"
3. "What factors affect pricing?"

**Similarity to Original**:
- Q1: 0.40 (vaguely related)
- Q2: 0.20 (different topic)
- Q3: 0.35 (related to pricing concept)

**Average**: **0.32** ❌

**Problem**: Non-answer disguised as an answer.

**Fix**: Either provide actual pricing or explicitly state "not publicly listed."

---

### Scenario 3: The Over-Deliverer

**Question**: "Is this product vegan?"

**Answer**: "Yes, this product is 100% vegan. It contains no animal products, byproducts, or derivatives. The manufacturing facility is also certified vegan by the Vegan Society. Additionally, we use sustainable packaging and donate 1% of revenue to ocean conservation. Our supply chain is fully transparent and traceable."

**Generated Questions**:
1. "Is this product vegan?"
2. "Is the facility vegan-certified?"
3. "What packaging does the product use?"
4. "Does the company support conservation?"
5. "Is the supply chain transparent?"

**Similarity Scores**:
- Q1: 0.99 ✅
- Q2: 0.45
- Q3: 0.25
- Q4: 0.15
- Q5: 0.20

**Average**: (0.99 + 0.45 + 0.25 + 0.15 + 0.20) / 5 = **0.41**⚠️

**Surprising**: Great info, but lower score because of extra details.

**Tradeoff**: High relevance vs complete information.

---

## 📊 Real-World Examples

### Example 1: Technical Support

**Q**: "How do I reset my password?"

**A1** (Poor - 0.35): "Account security is important. We use industry-standard encryption and two-factor authentication to protect user data."
- **Issue**: Talks ABOUT security, doesn't answer HOW

**A2** (Good - 0.72): "To reset: 1) Click 'Forgot Password' 2) Check email 3) Follow link. Also, we recommend enabling 2FA for security."
- **Issue**: Answers but adds extra

**A3** (Excellent - 0.96): "Click 'Forgot Password' on login page. Enter your email. Follow the reset link sent to you."
- **Perfect**: Direct, complete answer

---

### Example 2: Medical RAG

**Q**: "What are side effects of aspirin?"

**A1** (Dangerous - 0.25): "Aspirin is a widely used medication discovered in 1899. It's derived from willow bark and has revolutionized pain management."
- **Issue**: History lesson, not medical info

**A2** (Good - 0.85): "Common side effects include stomach upset, heartburn, and easy bruising. Rare but serious effects include bleeding and allergic reactions."
- **Perfect**: Answers directly with important info

---

### Example 3: Financial Q&A

**Q**: "What was Q2 revenue?"

**A1** (Evasive - 0.30): "The company had a strong quarter with revenue growth driven by our core business segments."
- **Issue**: Nice words, no numbers

**A2** (Perfect - 0.98): "Q2 revenue was $45.2 million."
- **Perfect**: Exactly what was asked

---

## 🎯 Advanced Techniques

### 1. Controlling Strictness

You can adjust how strict the relevance check is:

```python
from ragas.metrics import answer_relevancy

# More lenient (allows some tangential info)
# This is done by adjusting number of generated questions

# Fewer questions = more lenient
# More questions = stricter (answer must stay focused)

# Default is 3 questions, you can customize the metric config
```

---

### 2. Combining with Other Metrics

Answer relevance alone isn't enough. Combine with faithfulness:

```python
from ragas.metrics import answer_relevancy, faithfulness

# Good: Relevant AND faithful
# - Answers the question
# - Using only retrieved context

result = evaluate(
    dataset,
    metrics=[answer_relevancy, faithfulness]
)

def quality_check(result):
    rel = result['answer_relevancy']
    faith = result['faithfulness']
    
    if rel > 0.8 and faith > 0.9:
        return "✅ Excellent answer"
    elif rel < 0.5:
        return "❌ Doesn't answer question"
    elif faith < 0.7:
        return "❌ Contains hallucinations"
    else:
        return "⚠️ Needs improvement"
```

---

### 3. Domain-Specific Relevance

For specialized domains, you might want semantic understanding:

```python
# Medical domain
question = "What treats hypertension?"
answer1 = "ACE inhibitors lower high blood pressure"  # Relevant!
answer2 = "Hypertension is high blood pressure"       # Not treatment

# Without domain knowledge, both might score similarly
# With medical context, answer1 should score much higher
```

**Solution**: Use domain-specific embeddings or few-shot examples.

---

## 🔧 Troubleshooting

### Issue 1: Scores Too Low for Good Answers

**Symptom**: Your answer is great but scores 0.50

**Cause**: Question phrasing mismatches

**Example**:
- Question: "Show me the CEO" pay"
- Answer: "The chief executive earned $2M"
- Issue: "pay" vs "earned", "CEO" vs "chief executive"

**Fix**: Use better embeddings

```python
from langchain_openai import OpenAIEmbeddings

# Use better embeddings for similarity
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
```

---

### Issue 2: Short Answers Penalized

**Symptom**: "Yes" answers get low scores

**Question**: "Is shipping free?"
**Answer**: "Yes"

**Generated questions**: Hard to generate meaningful questions
**Score**: Low (0.40) despite being correct

**Fix**: Encourage slightly expanded answers

```
System prompt: "Answer questions directly but include one supporting detail."

Improved answer: "Yes, shipping is free for orders over $50."
Score: 0.85 ✅
```

---

### Issue 3: Questions with Multiple Parts

**Question**: "What's the price and is there a discount?"

**Answer**: "The price is $99."

**Problem**: Only answers first part

**Solution**: Detect multi-part questions and require comprehensive answers

```python
def is_multipart(question):
    return any(word in question.lower() for word in ['and', 'or', 'also', ','])

if is_multipart(question):
    # Require minimum length
    if len(answer.split()) < 10:
        relevance_score *= 0.5  # Penalize short answers to complex questions
```

---

## 📈 Production Best Practices

### 1. Set Answer Quality Gates

```python
RELEVANCE_THRESHOLDS = {
    "critical_questions": 0.90,  # Must be highly relevant
    "standard_questions": 0.70,  # Generally good
    "exploratory": 0.50         # Broad answers OK
}

def classify_question(question):
    # Simple classification
    critical_words = ["price", "cost", "refund", "cancel", "delete"]
    if any(word in question.lower() for word in critical_words):
        return "critical_questions"
    return "standard_questions"

def meets_quality(question, relevance_score):
    q_type = classify_question(question)
    threshold = RELEVANCE_THRESHOLDS[q_type]
    
    if relevance_score < threshold:
        return False, f"Relevance {relevance_score} < {threshold} for {q_type}"
    
    return True, "Passed"
```

---

### 2. A/B Test System Prompts

```python
# Test if instructing "be concise" improves relevance

prompt_a = "Answer the question: {question}"
prompt_b = "Answer concisely: {question}"

scores_a = evaluate_with_prompt(dataset, prompt_a)
scores_b = evaluate_with_prompt(dataset, prompt_b)

improvement = scores_b['answer_relevancy'] - scores_a['answer_relevancy']

if improvement > 0.10:  # 10% boost
    print(f"✅ Concise prompt improves relevance by {improvement:.1%}")
```

---

### 3. Monitor Relevance Trends

```python
# Track relevance over time
from datetime import datetime
import pandas as pd

relevance_log = []

def log_relevance(question_type, score):
    relevance_log.append({
        "timestamp": datetime.now(),
        "question_type": question_type,
        "relevance": score
    })

# Weekly report
df = pd.DataFrame(relevance_log)
weekly_avg = df.groupby([
    df['timestamp'].dt.week,
    'question_type'
])['relevance'].mean()

# Alert if any category drops
if any(weekly_avg < 0.70):
    alert_team("Answer relevance degradation!")
```

---

## 🧪 Hands-On Exercise

**Challenge**: Improve a low-relevance answer.

**Setup**:
```python
question = "What's the cancellation policy?"

answer_v1 = """
Our company values customer satisfaction and transparency. 
We've been in business for 15 years serving millions of customers. 
We believe in flexibility and fair treatment of all users.
"""

# Your task: Rewrite to improve relevance score
# Target: > 0.85
```

**Solution**:
```python
answer_v2 = """
You can cancel anytime before shipping. 
Full refund if cancelled within 24 hours of order.
After shipping, returns accepted within 30 days.
"""

# Evaluate both
result = evaluate(
    Dataset.from_dict({
        "question": [question, question],
        "answer": [answer_v1, answer_v2],
        "contexts": [[policy], [policy]]
    }),
    metrics=[answer_relevancy]
)

print(f"V1: {result['answer_relevancy'][0]}")  # ~0.25
print(f"V2: {result['answer_relevancy'][1]}")  # ~0.92
```

---

## ✅ What You've Achieved

You now understand:

✅ **Answer relevance definition** and purpose  
✅ **Reverse question algorithm** (generate → compare → score)  
✅ **Common failure modes** (rambling, dodging, over-delivering)  
✅ **Real-world examples** across domains  
✅ **Debugging techniques** for low scores  
✅ **Production practices** (thresholds, A/B testing, monitoring)  

**So far in RAG Triad**:
- ✅ **Faithfulness**: No hallucinations
- ✅ **Answer Relevance**: Actually answers the question
- ⏳ **Context Quality**: Did we retrieve the right docs? (Next!)

---

## 🚦 Next Steps

- **[Next: Context Metrics](./05-context-metrics.md)** - Retrieval quality (Precision, Recall)
- **[Back: Faithfulness](./03-faithfulness.md)** - Review hallucination detection
- **[Introduction](./01-introduction.md)** - RAG Triad overview

---

*From evasive answers to direct, relevant responses. From confusion to clarity.* ✨
