import giskard
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.naive_rag import query_bot

# Wrap the naive bot
def model_predict(df):
    results = []
    for q in df["question"]:
         docs = query_bot(q)
         results.append(" ".join([d.page_content for d in docs]))
    return results

giskard_model = giskard.Model(
    model=model_predict,
    model_type="text_generation",
    name="Vulnerable HR Bot",
    description="An HR bot that answers questions based on policy documents."
)

# Load testset
# Note: In real usage, we'd load the JSON we generated.
# For this script to be standalone runnable without generating 50 questions first:
from giskard.rag import generate_testset, KnowledgeBase
import pandas as pd
df_private = pd.read_csv("data/executive_comp.csv")
kb = KnowledgeBase.from_pandas(df_private, columns=["salary", "bonus"])
testset = generate_testset(kb, num_questions=5, question_type=["distracting"])


# Run the scan focusing on Information Disclosure
scan_results = giskard.scan(
    giskard_model, 
    dataset=testset, 
    only=["sensitive_information_disclosure"]
)

# Create output dir if not exists
os.makedirs("reports", exist_ok=True)
scan_results.to_html("reports/failed_audit.html")

print("Scan complete. Check reports/failed_audit.html")
