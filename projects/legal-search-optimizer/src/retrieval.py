from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

def rag_chain(retriever, query):
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    return qa_chain.invoke({"query": query})
