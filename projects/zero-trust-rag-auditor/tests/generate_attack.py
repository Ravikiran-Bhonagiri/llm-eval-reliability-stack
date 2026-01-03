import pandas as pd
from giskard.rag import KnowledgeBase, generate_testset

# 1. Define the "Target" (The Restricted Data)
df_private = pd.read_csv("data/executive_comp.csv")
kb = KnowledgeBase.from_pandas(df_private, columns=["salary", "bonus"])

# 2. Generate Attacks using RAGET
# We specifically request "Distracting" and "Situational" questions.
# These types are best at tricking retrievers.
testset = generate_testset(
    kb,
    num_questions=10, # Keeping small for demo
    question_type=["distracting", "situational"], 
    agent_description="HR Bot that should ONLY answer public policy questions"
)

testset.save("tests/attack_vectors.json")
