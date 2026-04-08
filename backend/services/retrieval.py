import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from backend.core.config import settings
from backend.core.logger import logger

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store():
    # Load or create FAISS index
    if os.path.exists(settings.faiss_index_path) and os.path.exists(os.path.join(settings.faiss_index_path, "index.faiss")):
        try:
            logger.info("Loading existing FAISS index.")
            return FAISS.load_local(settings.faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
    
    logger.info("Creating a new empty FAISS index.")
    # Create an empty vector store with a dummy document to initialize
    dummy_doc = Document(page_content="This is a trusted news reference system initializing.", metadata={"source": "init"})
    vector_store = FAISS.from_documents([dummy_doc], embeddings)
    vector_store.save_local(settings.faiss_index_path)
    return vector_store

vector_store = get_vector_store()

def retrieve_context(query: str, top_k: int = 3) -> list[str]:
    logger.info(f"Retrieving context for query: {query}")
    try:
        docs = vector_store.similarity_search(query, k=top_k)
        return [doc.page_content for doc in docs]
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return []

def add_documents_to_store(texts: list[str]):
    try:
        vector_store.add_texts(texts)
        vector_store.save_local(settings.faiss_index_path)
        logger.info(f"Added {len(texts)} documents to vector store.")
    except Exception as e:
        logger.error(f"Error adding to vector store: {e}")
