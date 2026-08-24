import os
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
from app.ml.embeddings.embedding_provider import EmbeddingProvider
from app.infrastructure.configuration import config

class SentenceTransformerProvider(EmbeddingProvider):
    """
    SentenceTransformers dense embedding provider using 'all-MiniLM-L6-v2' (384 dimensions).
    Provides dense semantic representation for cross-platform paraphrasing and near-duplicate detection.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    DIMENSION = 384

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None
        self._is_loaded = False
        self._load_error: Optional[str] = None

    def _ensure_loaded(self) -> None:
        """Lazy load SentenceTransformer model."""
        if self._is_loaded or self._load_error is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._is_loaded = True
        except Exception as e:
            self._load_error = str(e)
            self._is_loaded = False

    def get_embedding(self, text: str) -> np.ndarray:
        if not text:
            return np.zeros(self.DIMENSION, dtype=np.float32)
        
        self._ensure_loaded()
        if self._is_loaded and self._model is not None:
            try:
                emb = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return emb.astype(np.float32)
            except Exception:
                pass
                
        # Deterministic semantic hash pseudo-embedding fallback if offline
        return self._fallback_hash_embedding(text)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.DIMENSION), dtype=np.float32)
            
        self._ensure_loaded()
        if self._is_loaded and self._model is not None:
            try:
                embs = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embs.astype(np.float32)
            except Exception:
                pass
                
        return np.vstack([self._fallback_hash_embedding(t) for t in texts])

    def _fallback_hash_embedding(self, text: str) -> np.ndarray:
        """Deterministic, normalized pseudo-embedding based on token MD5 hashes."""
        vec = np.zeros(self.DIMENSION, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec
            
        for w in words:
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = h % self.DIMENSION
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vec[idx] += val
            
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def get_embedding_dimension(self) -> int:
        return self.DIMENSION

    def get_provider_metadata(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return {
            "provider": "SentenceTransformers",
            "model_name": self.model_name,
            "dimension": self.DIMENSION,
            "is_loaded": self._is_loaded,
            "status": "PRETRAINED" if self._is_loaded else "HEURISTIC_FALLBACK",
            "load_error": self._load_error
        }
