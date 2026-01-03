import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ragas import evaluate
from ragas.metrics import context_precision, context_recall, faithfulness
from src.ingestion import build_vector_store
from src.retrieval import rag_chain
from datasets import Dataset

# Load the Golden Dataset
# Ensure generation has run first
if not os.path.exists("tests/synthetic_ground_truth.csv"):
    print("Please run experiments/generate_data.py first.")
    sys.exit(1)

test_df = pd.read_csv("tests/synthetic_ground_truth.csv")
questions = test_df['question'].tolist()
ground_truths = test_df['ground_truth'].tolist()

# Define Strategies
configs = [
    {"name": "Small_Chunks", "size": 256, "overlap": 20},
    {"name": "Medium_Chunks", "size": 512, "overlap": 50},
    # Larger chunks might require larger context windows or different models
]

results_log = []

for config in configs:
    print(f"Testing {config['name']}...")
    
    # 1. Build Index
    retriever = build_vector_store(
        "data/landmark_cases.pdf", 
        config['size'], 
        config['overlap'], 
        config['name']
    )
    
    # 2. Run Inference
    answers = []
    contexts = []
    for q in questions:
        response = rag_chain(retriever, q) # Your RAG generation logic
        answers.append(response['result'])
        contexts.append([doc.page_content for doc in response['source_documents']])
        
    # 3. Evaluate with RAGAS
    data_dict = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": [[gt] for gt in ground_truths] # RAGAS expects list of lists for GT
    }
    
    dataset = Dataset.from_dict(data_dict)
    
    scores = evaluate(
        dataset=dataset,
        metrics=[context_precision, context_recall, faithfulness]
    )
    
    results_log.append({
        "config": config['name'],
        "precision": scores["context_precision"],
        "recall": scores["context_recall"],
        "faithfulness": scores["faithfulness"]
    })

# Output Results
pd.DataFrame(results_log).to_csv("experiments/final_results.csv")
print("Optimization complete. Results saved to experiments/final_results.csv")
