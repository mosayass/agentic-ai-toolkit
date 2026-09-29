import chromadb

def load_and_chunk_knowledge_base(file_path: str):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="rag_data")
    
    # Only index if collection is empty!
    if collection.count() == 0:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = text.split("\n\n")
        clean_chunks = [c.strip() for c in chunks if c.strip()]
        collection.add(
            documents=clean_chunks,
            ids=[f"doc_{i}" for i in range(len(clean_chunks))]
        )
        print("Indexed chunks to disk.")
    return collection


def query_knowledge_base(query: str) -> str:
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="rag_data")
    results = collection.query(query_texts=[query], n_results=1)
    if results["documents"] and results["documents"][0]:
        return results["documents"][0][0]
    return f"No relevant documentation found for: '{query}'"


    