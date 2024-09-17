import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')

llm = Ollama(model="llama3-chatqa:latest")

# Function to load and process documents
def load_documents(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    return texts

# Function to create or load FAISS index
def get_faiss_index(texts, index_name="faiss_index"):
    if os.path.exists(f"{index_name}.faiss"):
        vector_store = FAISS.load_local(index_name, embedding_model)
    else:
        vector_store = FAISS.from_documents(texts, embedding_model)
        vector_store.save_local(index_name)
    return vector_store

# Main RAG pipeline
class RAGQASystem:
    def __init__(self):
        self.vector_store = None
        self.qa_chain = None

    def load_documents(self, file_path: str):
        texts = load_documents(file_path)
        self.vector_store = get_faiss_index(texts)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )

    def answer_question(self, query: str):
        if not self.qa_chain:
            raise ValueError("Documents not loaded. Please load documents first.")

        result = self.qa_chain.invoke({
            "system": "Strictly follow these instructions: Provide only the exact answer in a short and clear way as stated in the context text in short. If the answer is not present, return 'Answer not found'. Do not generate or include any additional text or information beyond the answer provided in the context.",
            "system": "You will be heavily penalized if you do not follow the above instructions.",
            "query": query
        }, temperature=0.0)
        
        return result['result'], result['source_documents']