import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

class RAGService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name="resume_collection",
            persist_directory="./resume_vector_db"
        )

    def clear_existing_for_source(self, file_path: str) -> None:
        """Deletes any previously embedded chunks that came from this file path,
        regardless of whether it was stored as a relative or absolute path."""
        try:
            abs_path = os.path.abspath(file_path)
            # Try both the exact path given AND its absolute form, since
            # PyPDFLoader may have stored 'source' metadata in either format
            self.vector_store.delete(where={"source": file_path})
            self.vector_store.delete(where={"source": abs_path})
        except Exception as e:
            print(f"Warning: could not clear existing embeddings for {file_path}: {e}")

    def process_and_create_embeddings(self, file_path: str = "./Assets/Vedant_Savdekar_CV.pdf") -> None:
        self.clear_existing_for_source(file_path)

        loader = PyPDFLoader(file_path)
        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(pages)

        self.vector_store.add_documents(chunks)

    def get_retriever(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        return retriever

    def get_all_chunk_count(self) -> int:
        """Debug helper: returns total number of chunks currently stored."""
        return len(self.vector_store.get()["documents"])


if __name__ == "__main__":
    rag_service = RAGService()
    rag_service.process_and_create_embeddings()
    print("--------------VECTOR DB IS READY---------------")
    print(f"Total chunks now stored: {rag_service.get_all_chunk_count()}")