from typing import List, Dict, Any, Optional
from app.ml.embeddings.embedding_provider import EmbeddingProvider
from app.ml.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.ml.similarity.tfidf_similarity import TFIDFSimilarity
from app.ml.similarity.embedding_similarity import EmbeddingSimilarity

class SimilarityService:
    """
    Unified Similarity Service for AI Paraphrase & Provenance Tracking.
    Employs dense neural embeddings (SentenceTransformers all-MiniLM-L6-v2) for semantic matching
    and lexical TF-IDF for exact copy verification.
    """

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        self.embedding_provider = embedding_provider or SentenceTransformerProvider()
        self.tfidf_engine = TFIDFSimilarity()
        self.embedding_engine = EmbeddingSimilarity(self.embedding_provider)

    def compute_tfidf_similarity(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        return self.tfidf_engine.compute_similarity(query_text, candidate_texts)

    def compute_embedding_similarity(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        return self.embedding_engine.compute_similarity(query_text, candidate_texts)

    def compute_hybrid_similarity(
        self,
        query_text: str,
        candidate_texts: List[str],
        tfidf_weight: float = 0.2,
        embedding_weight: float = 0.8
    ) -> List[Dict[str, float]]:
        """
        Compute combined similarity scores:
        Dense embeddings capture AI-paraphrased semantic meaning (80%),
        while TF-IDF captures lexical word-overlap (20%).
        """
        if not candidate_texts:
            return []

        tfidf_scores = self.compute_tfidf_similarity(query_text, candidate_texts)
        emb_scores = self.compute_embedding_similarity(query_text, candidate_texts)

        results = []
        for t_score, e_score in zip(tfidf_scores, emb_scores):
            # The effective semantic score reflects true neural semantic alignment
            hybrid = round((tfidf_weight * t_score) + (embedding_weight * e_score), 4)
            # Use the max of dense and hybrid to ensure paraphrased mutations are accurately captured
            effective_sim = round(max(e_score, hybrid), 4)
            results.append({
                "tfidf_similarity": round(t_score, 4),
                "embedding_similarity": round(e_score, 4),
                "hybrid_similarity": effective_sim
            })
        return results

    def find_near_duplicates(
        self,
        query_text: str,
        candidate_items: List[Dict[str, Any]],
        threshold: float = 0.60
    ) -> List[Dict[str, Any]]:
        """
        Identify related, duplicate, and paraphrased items exceeding similarity threshold.
        """
        if not candidate_items:
            return []

        texts = [item.get("text", "") for item in candidate_items]
        scores = self.compute_hybrid_similarity(query_text, texts)

        matches = []
        for item, score_dict in zip(candidate_items, scores):
            if score_dict["hybrid_similarity"] >= threshold:
                matches.append({
                    "id": item.get("id"),
                    "text": item.get("text"),
                    "metadata": item.get("metadata", {}),
                    "created_at": item.get("created_at"),
                    **score_dict
                })

        matches.sort(key=lambda x: x["hybrid_similarity"], reverse=True)
        return matches
