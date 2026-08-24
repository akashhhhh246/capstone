from typing import List
import numpy as np
from app.ml.embeddings.embedding_provider import EmbeddingProvider

class EmbeddingSimilarity:
    """
    Dense semantic embedding cosine similarity calculator.
    Best for detecting paraphrased narratives, multi-lingual variants, and conceptual mutations.
    """

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def compute_similarity(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        """Compute semantic cosine similarity between query and candidate texts."""
        if not candidate_texts or not query_text:
            return [0.0] * len(candidate_texts)

        query_emb = self.provider.get_embedding(query_text)
        cand_embs = self.provider.get_embeddings(candidate_texts)

        # Cosine similarity for unit-normalized vectors: dot product
        # Ensure 2D normalization
        q_norm = np.linalg.norm(query_emb)
        if q_norm > 0:
            query_emb = query_emb / q_norm

        c_norms = np.linalg.norm(cand_embs, axis=1, keepdims=True)
        c_norms[c_norms == 0] = 1.0
        cand_embs = cand_embs / c_norms

        sim_scores = np.dot(cand_embs, query_emb)
        return [round(float(s), 4) for s in sim_scores]
