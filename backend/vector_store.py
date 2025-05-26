import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = None
        self.similarity_threshold = 0.7
    
    def load_index(self, index_path: str, chunks: List[str]):
        """Load FAISS index and chunks."""
        self.index = faiss.read_index(index_path)
        self.chunks = chunks
    
    def search(self, query: str, k: int = 3) -> Tuple[List[str], List[float]]:
        """Search for similar chunks using the query."""
        if not self.index or not self.chunks:
            raise ValueError("Index and chunks must be loaded before searching")
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in FAISS index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            k
        )
        
        # Convert distances to similarity scores (FAISS uses L2 distance)
        max_distance = np.max(distances)
        similarities = 1 - (distances / max_distance)
        
        # Filter results based on similarity threshold
        relevant_results = []
        relevant_scores = []
        
        for idx, score in zip(indices[0], similarities[0]):
            if score >= self.similarity_threshold:
                relevant_results.append(self.chunks[idx])
                relevant_scores.append(float(score))
        
        return relevant_results, relevant_scores
    
    def is_query_relevant(self, query: str) -> bool:
        """Check if the query is relevant to the stories."""
        results, scores = self.search(query, k=1)
        return len(results) > 0 and scores[0] >= self.similarity_threshold 