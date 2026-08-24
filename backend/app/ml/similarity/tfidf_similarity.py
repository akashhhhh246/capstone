from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TFIDFSimilarity:
    """
    TF-IDF based lexical cosine similarity calculator.
    Best for detecting verbatim copies, retweets, and high-overlap text reposts.
    """

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2)):
        self.ngram_range = ngram_range

    def compute_similarity(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        """Compute cosine similarity between query and candidate texts."""
        if not candidate_texts or not query_text:
            return [0.0] * len(candidate_texts)

        all_texts = [query_text] + candidate_texts
        try:
            vectorizer = TfidfVectorizer(ngram_range=self.ngram_range, sublinear_tf=True)
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            query_vec = tfidf_matrix[0:1]
            cand_vecs = tfidf_matrix[1:]
            sim_scores = cosine_similarity(query_vec, cand_vecs)[0]
            return [round(float(s), 4) for s in sim_scores]
        except Exception:
            return [0.0] * len(candidate_texts)
