from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import CSVLoader, TextLoader

# 1. Ingest Data (Mixed Security Levels)
# DANGER: Loading sensitive data into the same index as public data
loader_public = TextLoader("data/public_policy.txt")
loader_private = CSVLoader("data/executive_comp.csv") 

docs = loader_public.load() + loader_private.load()

# 2. Build Index
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

def query_bot(question):
    # Vulnerable: Retrieves based on semantic similarity ONLY
    return retriever.get_relevant_documents(question)
