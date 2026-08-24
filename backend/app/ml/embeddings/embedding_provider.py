from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

class EmbeddingProvider(ABC):
    """
    Abstract interface for dense semantic embedding providers.
    Supports modular substitution between SentenceTransformers, OpenAI embeddings,
    Cohere, or ONNX-optimized embedding runtimes.
    """

    @abstractmethod
    def get_embedding(self, text: str) -> np.ndarray:
        """Return 1D numpy vector embedding for a single string."""
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Return 2D numpy array of embeddings (N, embedding_dim)."""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Return dimensionality of the embedding space."""
        pass

    @abstractmethod
    def get_provider_metadata(self) -> Dict[str, Any]:
        """Return provider name, model identifier, and runtime status."""
        pass
