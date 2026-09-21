from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.models import Content, Post, Platform, SyntheticAccount
from app.ml.provenance.provenance_engine import ProvenanceEngine
from app.ml.similarity.similarity_service import SimilarityService

class ProvenanceService:
    """
    Application Service for Content Provenance Reconstruction.
    Queries the persistence layer and utilizes ProvenanceEngine to reconstruct
    lineage DAGs for any requested content ID or text snippet.
    """

    def __init__(
        self,
        provenance_engine: Optional[ProvenanceEngine] = None,
        similarity_service: Optional[SimilarityService] = None
    ):
        self.similarity_service = similarity_service or SimilarityService()
        self.provenance_engine = provenance_engine or ProvenanceEngine(self.similarity_service)

    def get_provenance_for_content(self, content_id: str, db: Session) -> Dict[str, Any]:
        """
        Reconstruct provenance graph for a registered content ID.
        """
        target_content_rec = db.query(Content).filter(Content.id == content_id).first()
        if not target_content_rec:
            return {
                "target_content_id": content_id,
                "error": "Content not found in database.",
                "total_nodes": 0,
                "total_edges": 0,
                "nodes": [],
                "edges": [],
                "is_acyclic": True
            }

        target_dict = {
            "id": target_content_rec.id,
            "text": target_content_rec.raw_text,
            "source_name": target_content_rec.source_name,
            "source_type": target_content_rec.source_type,
            "author": target_content_rec.author,
            "created_at": target_content_rec.created_at.isoformat() if target_content_rec.created_at else None,
            "classification": target_content_rec.detection_results[0].classification if target_content_rec.detection_results else "UNKNOWN"
        }

        # Query candidate historical contents
        historical_recs = db.query(Content).all()
        historical_contents = [
            {
                "id": c.id,
                "text": c.raw_text,
                "source_name": c.source_name,
                "source_type": c.source_type,
                "author": c.author,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "classification": c.detection_results[0].classification if c.detection_results else "UNKNOWN"
            }
            for c in historical_recs
        ]

        # First find relevant matching content IDs (near duplicates, paraphrases, related)
        matches = self.similarity_service.find_near_duplicates(
            target_dict["text"],
            [c for c in historical_contents if c["id"] != target_dict["id"]],
            threshold=ProvenanceEngine.THRESHOLD_RELATED
        )
        relevant_content_ids = {target_dict["id"]} | {m["id"] for m in matches}

        # ONLY query posts that reference relevant contents
        posts_recs = db.query(Post).filter(Post.content_id.in_(relevant_content_ids)).all()
        posts_data = []
        for p in posts_recs:
            posts_data.append({
                "id": p.id,
                "content_id": p.content_id,
                "parent_post_id": p.parent_post_id,
                "platform_id": p.platform_id,
                "platform_name": p.platform.name if p.platform else "Unknown Platform",
                "account_id": p.account_id,
                "account_handle": p.account.pseudonym_handle if p.account else "@synth_user",
                "bot_probability": p.account.bot_probability if p.account else 0.0,
                "post_type": p.post_type,
                "likes": p.likes,
                "reshares": p.reshares,
                "published_at": p.published_at.isoformat() if p.published_at else None
            })

        dag_result = self.provenance_engine.reconstruct_provenance_dag(
            target_content=target_dict,
            historical_contents=historical_contents,
            posts=posts_data
        )

        return dag_result
