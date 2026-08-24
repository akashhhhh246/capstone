import pytest
from app.ml.similarity.similarity_service import SimilarityService
from app.ml.provenance.provenance_engine import ProvenanceEngine

def test_similarity_service():
    service = SimilarityService()
    query = "URGENT BREAKING: Power grid shutdown tonight at midnight!"
    candidates = [
        "URGENT BREAKING: Power grid shutdown tonight at midnight!",
        "ALERT: Whistleblowers confirm electrical grid shutdown at midnight!",
        "The local bakery serves fresh croissants every morning at 7 AM."
    ]

    tfidf_sims = service.compute_tfidf_similarity(query, candidates)
    emb_sims = service.compute_embedding_similarity(query, candidates)
    hybrid_sims = service.compute_hybrid_similarity(query, candidates)

    assert len(tfidf_sims) == 3
    assert len(emb_sims) == 3
    assert len(hybrid_sims) == 3

    # Exact match should have highest similarity
    assert tfidf_sims[0] >= tfidf_sims[1]
    assert tfidf_sims[0] > tfidf_sims[2]
    assert hybrid_sims[0]["hybrid_similarity"] > hybrid_sims[2]["hybrid_similarity"]

def test_provenance_dag_construction():
    engine = ProvenanceEngine()
    target = {
        "id": "c-target",
        "text": "ALERT: Power grid shutdown ordered tonight at midnight!",
        "created_at": "2026-08-24T12:00:00Z",
        "classification": "AI_GENERATED"
    }
    history = [
        {
            "id": "c-hist-1",
            "text": "URGENT BREAKING: Power grid shutdown ordered tonight at midnight!",
            "created_at": "2026-08-24T11:00:00Z",
            "classification": "AI_GENERATED"
        }
    ]
    posts = [
        {
            "id": "p-1",
            "content_id": "c-hist-1",
            "platform_name": "SimuTwitter",
            "account_handle": "@bot_01",
            "post_type": "ORIGINAL"
        }
    ]

    dag = engine.reconstruct_provenance_dag(target, history, posts)
    assert "nodes" in dag
    assert "edges" in dag
    assert dag["is_acyclic"] is True
    assert len(dag["nodes"]) >= 2
