from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import CSVLoader, TextLoader

# 1. Load Data
loader_public = TextLoader("data/public_policy.txt")
loader_private = CSVLoader("data/executive_comp.csv")

docs_public = loader_public.load()
docs_private = loader_private.load()

# 1. Tagging during Ingestion
for doc in docs_public:
    doc.metadata["access_level"] = "all"

for doc in docs_private:
    doc.metadata["access_level"] = "admin_only" # RESTRICTED TAG

# Re-build Index with Metadata
vectorstore = FAISS.from_documents(docs_public + docs_private, OpenAIEmbeddings())

# 2. The Permission-Aware Retriever
class SecureRetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def get_docs(self, query, user_role):
        # SECURITY LOGIC: Enforce filter based on role
        if user_role == "employee":
            filter_dict = {"access_level": "all"}
        elif user_role == "admin":
            filter_dict = {} # No filter
            
        return self.vectorstore.similarity_search(
            query, 
            filter=filter_dict # The Shield
        )
