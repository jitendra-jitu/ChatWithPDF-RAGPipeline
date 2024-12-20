from langchain_community.vectorstores import FAISS  # Updated import
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_vector_store(text_chunks):
    # Initialize embeddings with the required model argument
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Specify the model
    # Create vector store from text chunks
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    # Save the vector store locally
    vector_store.save_local("faiss_index")
