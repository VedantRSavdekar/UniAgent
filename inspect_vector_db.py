from App.services.rag_service import RAGService

rag_service = RAGService()

# Pull everything directly from the vector store - no LLM calls, no tokens used
all_data = rag_service.vector_store.get()

print(f"Total chunks stored: {len(all_data['documents'])}\n")

for i, doc in enumerate(all_data['documents']):
    print(f"--- Chunk {i+1} ({len(doc)} characters) ---")
    print(doc[:300])  # first 300 chars of each chunk
    print()