import numpy as np
from typing import List, Dict, Any, Optional
import json
import pickle
from datetime import datetime
import hashlib

class VectorStore:
    """Vector store for semantic search and memory management"""
    
    def __init__(self, dimension: int = 384, persistence_path: str = "data/vector_store.pkl"):
        self.dimension = dimension
        self.persistence_path = persistence_path
        self.vectors = np.array([])
        self.metadata = []
        self.embeddings_model = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        try:
            self.load()
            print(f"Loaded vector store with {len(self.metadata)} entries")
        except FileNotFoundError:
            self.vectors = np.zeros((0, self.dimension))
            self.metadata = []
            print("Initialized new vector store")
    
    async def add_memory(self, text: str, metadata: Dict[str, Any], embedding: Optional[np.ndarray] = None):
        """Add memory to vector store"""
        if embedding is None:
            embedding = await self._generate_embedding(text)
        
        # Ensure embedding has correct dimension
        if len(embedding) != self.dimension:
            embedding = self._adjust_embedding_dimension(embedding)
        
        # Add to vectors and metadata
        if len(self.vectors) == 0:
            self.vectors = embedding.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, embedding])
        
        full_metadata = {
            'id': self._generate_id(text, metadata),
            'text': text,
            'embedding': embedding.tolist(),
            'timestamp': datetime.now().isoformat(),
            'access_count': 0,
            **metadata
        }
        
        self.metadata.append(full_metadata)
        self.save()
    
    async def search_similar(self, query: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar memories using semantic similarity"""
        if len(self.vectors) == 0:
            return []
        
        query_embedding = await self._generate_embedding(query)
        query_embedding = self._adjust_embedding_dimension(query_embedding)
        
        # Calculate similarities
        similarities = self._cosine_similarity(query_embedding, self.vectors)
        
        # Get top-k results above threshold
        indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        
        for idx in indices:
            if similarities[idx] >= threshold:
                metadata = self.metadata[idx].copy()
                metadata['similarity'] = float(similarities[idx])
                metadata['access_count'] += 1
                results.append(metadata)
        
        return results
    
    async def search_by_metadata(self, filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search memories by metadata filters"""
        results = []
        
        for memory in self.metadata:
            match = True
            for key, value in filters.items():
                if key not in memory or memory[key] != value:
                    match = False
                    break
            
            if match:
                results.append(memory)
                if len(results) >= top_k:
                    break
        
        return results
    
    async def get_context(self, query: str, max_memories: int = 10, recency_weight: float = 0.3) -> str:
        """Get contextual information for a query"""
        similar_memories = await self.search_similar(query, top_k=max_memories * 2)
        
        if not similar_memories:
            return ""
        
        # Apply recency weighting
        for memory in similar_memories:
            recency = self._calculate_recency_score(memory['timestamp'])
            memory['weighted_score'] = memory['similarity'] * (1 - recency_weight) + recency * recency_weight
        
        # Sort by weighted score and take top memories
        similar_memories.sort(key=lambda x: x['weighted_score'], reverse=True)
        top_memories = similar_memories[:max_memories]
        
        # Build context string
        context_parts = []
        for memory in top_memories:
            context_parts.append(f"- {memory['text']} (relevance: {memory['weighted_score']:.2f})")
        
        return "\n".join(context_parts)
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.metadata:
            return {
                'total_memories': 0,
                'average_access_count': 0,
                'memory_age_distribution': {}
            }
        
        access_counts = [m['access_count'] for m in self.metadata]
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in self.metadata]
        now = datetime.now()
        
        age_distribution = {
            'less_than_day': len([ts for ts in timestamps if (now - ts).days < 1]),
            'less_than_week': len([ts for ts in timestamps if (now - ts).days < 7]),
            'less_than_month': len([ts for ts in timestamps if (now - ts).days < 30]),
            'older': len([ts for ts in timestamps if (now - ts).days >= 30])
        }
        
        return {
            'total_memories': len(self.metadata),
            'average_access_count': sum(access_counts) / len(access_counts),
            'memory_age_distribution': age_distribution,
            'vector_dimension': self.dimension,
            'storage_size_mb': self._calculate_storage_size()
        }
    
    def cleanup_old_memories(self, max_age_days: int = 90, min_access_count: int = 1):
        """Remove old and rarely accessed memories"""
        now = datetime.now()
        indices_to_remove = []
        
        for i, memory in enumerate(self.metadata):
            memory_age = (now - datetime.fromisoformat(memory['timestamp'])).days
            if memory_age > max_age_days and memory['access_count'] < min_access_count:
                indices_to_remove.append(i)
        
        # Remove in reverse order to maintain indices
        for i in sorted(indices_to_remove, reverse=True):
            del self.metadata[i]
            self.vectors = np.delete(self.vectors, i, axis=0)
        
        if indices_to_remove:
            print(f"Removed {len(indices_to_remove)} old memories")
            self.save()
    
    def save(self):
        """Save vector store to disk"""
        import os
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        
        data = {
            'vectors': self.vectors,
            'metadata': self.metadata,
            'dimension': self.dimension
        }
        
        with open(self.persistence_path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self):
        """Load vector store from disk"""
        with open(self.persistence_path, 'rb') as f:
            data = pickle.load(f)
        
        self.vectors = data['vectors']
        self.metadata = data['metadata']
        self.dimension = data['dimension']
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text - would integrate with embedding models"""
        # Simplified embedding generation
        # In production, this would use SentenceTransformers, OpenAI embeddings, etc.
        text_hash = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(text_hash[:8], 16))
        return np.random.randn(self.dimension)
    
    def _adjust_embedding_dimension(self, embedding: np.ndarray) -> np.ndarray:
        """Adjust embedding to correct dimension"""
        if len(embedding) > self.dimension:
            return embedding[:self.dimension]
        elif len(embedding) < self.dimension:
            return np.pad(embedding, (0, self.dimension - len(embedding)))
        return embedding
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between vectors"""
        if vec2.ndim == 1:
            vec2 = vec2.reshape(1, -1)
        
        dot_product = np.dot(vec2, vec1)
        norms = np.linalg.norm(vec2, axis=1) * np.linalg.norm(vec1)
        
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        
        return dot_product / norms
    
    def _generate_id(self, text: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for memory"""
        content = text + json.dumps(metadata, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _calculate_recency_score(self, timestamp: str) -> float:
        """Calculate recency score (0 to 1, 1 being most recent)"""
        memory_time = datetime.fromisoformat(timestamp)
        now = datetime.now()
        age_hours = (now - memory_time).total_seconds() / 3600
        
        # Exponential decay: score = e^(-age_hours / 168) [1 week half-life]
        return np.exp(-age_hours / 168)
    
    def _calculate_storage_size(self) -> float:
        """Calculate approximate storage size in MB"""
        vector_size = self.vectors.nbytes if self.vectors.size > 0 else 0
        metadata_size = sum(len(json.dumps(m).encode('utf-8')) for m in self.metadata)
        total_bytes = vector_size + metadata_size
        return total_bytes / (1024 * 1024)  # Convert to MB
