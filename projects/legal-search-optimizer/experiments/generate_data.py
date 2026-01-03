from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. Load Data
loader = PyPDFLoader("data/landmark_cases.pdf")
documents = loader.load()

# 2. Configure Generator
generator_llm = ChatOpenAI(model="gpt-4")
critic_llm = ChatOpenAI(model="gpt-4")
embeddings = OpenAIEmbeddings()

generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

# 3. Generate Synthetic Data
# "Reasoning" evolution ensures questions aren't just keyword matches
testset = generator.generate_with_langchain_docs(
    documents,
    test_size=5,  # Keeping small for demo purposes (usually 20+)
    distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25}
)

# Save for reproducibility
testset.to_pandas().to_csv("tests/synthetic_ground_truth.csv")
print("Synthetic testset generated at tests/synthetic_ground_truth.csv")
