import chromadb
from datetime import datetime

client = None
collection = None

def init_chroma():
    """Initialize ChromaDB client and collection"""
    global client, collection
    
    if client is None:
        client = chromadb.Client()
        collection = client.get_or_create_collection(name="business_knowledge")
    
    return collection

def store_in_chroma(text, metadata=None):
    """Store text in ChromaDB with metadata"""
    try:
        coll = init_chroma()
        doc_id = f"doc_{datetime.now().timestamp()}_{hash(text) % 10000}"
        
        if metadata is None:
            metadata = {}
        
        coll.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        
        return doc_id
    
    except Exception as e:
        print(f"ChromaDB store error: {e}")
        return None

def query_chroma(query_text, n_results=3):
    """Query ChromaDB for relevant context"""
    try:
        coll = init_chroma()
        results = coll.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if results['documents'] and results['documents'][0]:
            return '\n\n'.join(results['documents'][0])
        
        return ''
    
    except Exception as e:
        print(f"ChromaDB query error: {e}")
        return ''
