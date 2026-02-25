// Simple in-memory storage (replace with ChromaDB backend API later)
let knowledgeStore = [];

export async function storeInChroma({ text, metadata = {} }) {
  try {
    const id = `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    knowledgeStore.push({ id, text, metadata, timestamp: Date.now() });
    return id;
  } catch (error) {
    console.error('Storage error:', error);
    return null;
  }
}

export async function queryChroma(queryText, nResults = 3) {
  try {
    // Simple keyword matching (replace with vector search via backend)
    const keywords = queryText.toLowerCase().split(' ');
    const results = knowledgeStore
      .filter(doc => keywords.some(kw => doc.text.toLowerCase().includes(kw)))
      .slice(-nResults)
      .map(doc => doc.text);
    
    return results.join('\n\n');
  } catch (error) {
    console.error('Query error:', error);
    return '';
  }
}
