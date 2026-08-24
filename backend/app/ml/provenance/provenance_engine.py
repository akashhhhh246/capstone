from typing import List, Dict, Any, Optional
from datetime import datetime
import networkx as nx
from app.ml.similarity.similarity_service import SimilarityService

class ProvenanceEngine:
    """
    Provenance Tracking & Lineage Reconstruction Engine.
    Builds clean, high-precision Directed Acyclic Graphs (DAG) mapping text content evolution
    from root origin to true exact reposts, paraphrased variants, and related narratives across platforms.
    """

    # Similarity Thresholds for Provenance Classification
    THRESHOLD_IDENTICAL = 0.95
    THRESHOLD_NEAR_DUPLICATE = 0.80
    THRESHOLD_PARAPHRASED_DERIVATIVE = 0.70
    THRESHOLD_RELATED = 0.60

    def __init__(self, similarity_service: Optional[SimilarityService] = None):
        self.similarity_service = similarity_service or SimilarityService()

    def classify_relationship(self, hybrid_similarity: float) -> str:
        """Categorize derivation relationship based on semantic similarity score."""
        if hybrid_similarity >= self.THRESHOLD_IDENTICAL:
            return "EXACT_COPY"
        elif hybrid_similarity >= self.THRESHOLD_NEAR_DUPLICATE:
            return "NEAR_DUPLICATE"
        elif hybrid_similarity >= self.THRESHOLD_PARAPHRASED_DERIVATIVE:
            return "PARAPHRASED_DERIVATIVE"
        elif hybrid_similarity >= self.THRESHOLD_RELATED:
            return "RELATED_NARRATIVE"
        else:
            return "UNRELATED"

    def reconstruct_provenance_dag(
        self,
        target_content: Dict[str, Any],
        historical_contents: List[Dict[str, Any]],
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconstruct pure content provenance graph for target content against historical database.
        Maps root seed -> true derivative texts with platform tags and verified semantic similarity.
        """
        G = nx.DiGraph()
        nodes_map: Dict[str, Dict[str, Any]] = {}
        edges_list: List[Dict[str, Any]] = []

        target_id = target_content["id"]
        target_text = target_content["text"]
        target_created = target_content.get("created_at")

        # Map content IDs to platform & account information from posts
        content_platforms: Dict[str, str] = {}
        content_accounts: Dict[str, str] = {}
        for p in posts:
            cid = p.get("content_id")
            if cid:
                if cid not in content_platforms:
                    content_platforms[cid] = p.get("platform_name", "SimuTwitter")
                if cid not in content_accounts:
                    content_accounts[cid] = p.get("account_handle", "@author")

        # 1. Add Target Node (Root Seed)
        nodes_map[target_id] = {
            "id": target_id,
            "label": f"Root Content ({target_id[:8]})",
            "type": "CONTENT",
            "text": target_text[:120] + "..." if len(target_text) > 120 else target_text,
            "full_text": target_text,
            "created_at": str(target_created) if target_created else "",
            "platform": content_platforms.get(target_id, "SimuTwitter"),
            "account": content_accounts.get(target_id, "@root_author"),
            "is_target": True,
            "similarity": 1.0,
            "relationship": "ORIGIN_ROOT",
            "classification": target_content.get("classification", "UNKNOWN")
        }
        G.add_node(target_id)

        # 2. Compare target against candidate historical contents
        candidate_items = [c for c in historical_contents if c["id"] != target_id]

        if candidate_items:
            matches = self.similarity_service.find_near_duplicates(
                target_text,
                candidate_items,
                threshold=self.THRESHOLD_RELATED
            )

            for match in matches:
                m_id = match["id"]
                m_text = match["text"]
                m_created = match.get("created_at")
                sim = float(match["hybrid_similarity"])
                rel_type = self.classify_relationship(sim)

                if rel_type == "UNRELATED":
                    continue

                nodes_map[m_id] = {
                    "id": m_id,
                    "label": f"{rel_type.replace('_', ' ')} ({m_id[:8]})",
                    "type": "CONTENT",
                    "text": m_text[:120] + "..." if len(m_text) > 120 else m_text,
                    "full_text": m_text,
                    "created_at": str(m_created) if m_created else "",
                    "platform": content_platforms.get(m_id, "SimuTelegram"),
                    "account": content_accounts.get(m_id, "@echo_node"),
                    "is_target": False,
                    "similarity": round(sim, 3),
                    "relationship": rel_type,
                    "classification": match.get("classification", "UNKNOWN")
                }

                # Chronological edge: older content -> newer derivative
                is_target_older = True
                if target_created and m_created:
                    try:
                        t_dt = datetime.fromisoformat(str(target_created).replace('Z', '+00:00'))
                        m_dt = datetime.fromisoformat(str(m_created).replace('Z', '+00:00'))
                        is_target_older = t_dt <= m_dt
                    except Exception:
                        pass

                source_id = target_id if is_target_older else m_id
                target_node_id = m_id if is_target_older else target_id

                edge_record = {
                    "id": f"edge_{source_id}_{target_node_id}",
                    "source": source_id,
                    "target": target_node_id,
                    "type": rel_type,
                    "relationship_type": rel_type,
                    "similarity": round(sim, 3),
                    "label": f"{rel_type.replace('_', ' ')} ({int(sim * 100)}%)"
                }
                edges_list.append(edge_record)
                G.add_edge(source_id, target_node_id, **edge_record)

        # 3. Identify Root Origin
        root_origin = {
            "id": target_id,
            "created_at": target_created,
            "text_preview": target_text[:100],
            "platform": content_platforms.get(target_id, "SimuTwitter"),
            "account": content_accounts.get(target_id, "@root_author")
        }

        return {
            "target_content_id": target_id,
            "root_origin": root_origin,
            "total_nodes": len(nodes_map),
            "total_edges": len(edges_list),
            "nodes": list(nodes_map.values()),
            "edges": edges_list,
            "is_acyclic": nx.is_directed_acyclic_graph(G) if len(G.nodes) > 0 else True
        }
