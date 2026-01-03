from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def build_vector_store(pdf_path, chunk_size, chunk_overlap, collection_name):
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Dynamic Splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""] # Try to keep paragraphs together
    )
    docs = text_splitter.split_documents(documents)

    # Indexing
    db = Chroma.from_documents(
        docs, 
        OpenAIEmbeddings(), 
        collection_name=collection_name,
        persist_directory="./chroma_db"
    )
    return db.as_retriever()
