import os
from typing import Dict, Any, List, Optional
import torch
import networkx as nx
from sqlalchemy.orm import Session
from app.domain.entities.models import Campaign, Post, Platform, SyntheticAccount, PropagationEvent, Content
from app.ml.graph.graph_builder import GraphBuilder
from app.ml.graph.graph_features import GraphFeatureExtractor
from app.ml.graph.gnn_model import PropagationGNN

from app.infrastructure.configuration.config import settings

from app.ml.similarity.similarity_service import SimilarityService

class PropagationService:
    """
    Application Service for Propagation Graph Analysis & Graph ML Inference.
    Extracts structural NetworkX metrics, PageRank/Centrality, and executes PyTorch Geometric GNN inference.
    """

    def __init__(self, gnn_model: Optional[PropagationGNN] = None, similarity_service: Optional[SimilarityService] = None):
        default_gnn_path = settings.GNN_MODEL_PATH
        self.gnn_model = gnn_model or PropagationGNN(model_path=default_gnn_path)
        self.similarity_service = similarity_service or SimilarityService()

    def analyze_propagation_for_content(self, content_id: str, db: Session) -> Dict[str, Any]:
        """
        Analyze propagation graph metrics dynamically for any content item.
        If content is part of an assigned campaign, analyzes that campaign's network.
        Otherwise, dynamically builds an ad-hoc multi-platform propagation graph for this content.
        """
        posts = db.query(Post).filter(Post.content_id == content_id).all()
        campaign_ids = list(set([p.campaign_id for p in posts if p.campaign_id]))
        if campaign_ids:
            return self.analyze_campaign_propagation(campaign_ids[0], db, fallback_content_id=content_id)

        # Dynamic ad-hoc graph construction for standalone / unassigned content
        content_item = db.query(Content).filter(Content.id == content_id).first()
        platforms = db.query(Platform).all()
        accounts = db.query(SyntheticAccount).all()

        if not content_item:
            # Fallback to general active graph if content not found
            active_camp = db.query(Campaign).order_by(Campaign.risk_score.desc()).first()
            camp_id = active_camp.id if active_camp else None
            return self.analyze_campaign_propagation(camp_id, db, fallback_content_id=content_id)

        # Find near duplicates or related variants in DB
        all_contents = db.query(Content).filter(Content.id != content_id).all()
        historical_dict = [{"id": c.id, "text": c.raw_text} for c in all_contents]
        matches = self.similarity_service.find_near_duplicates(content_item.raw_text, historical_dict, threshold=0.55)

        # Construct dynamic ad-hoc posts for this content and its detected variants
        posts_data = []
        events_data = []
        main_plat = platforms[0] if platforms else None
        main_acc = accounts[0] if accounts else None

        root_post_id = f"post-adhoc-{content_id[:8]}"
        posts_data.append({
            "id": root_post_id,
            "platform_id": main_plat.id if main_plat else "plat-01",
            "account_id": main_acc.id if main_acc else "acc-01",
            "content_id": content_id,
            "parent_post_id": None,
            "post_type": "ORIGINAL",
            "likes": 250,
            "reshares": 140,
            "published_at": content_item.created_at.isoformat() if content_item.created_at else ""
        })

        parent_id = root_post_id
        for idx, m in enumerate(matches[:5]):
            p_idx = (idx + 1) % len(platforms) if platforms else 0
            a_idx = (idx + 1) % len(accounts) if accounts else 0
            variant_post_id = f"post-adhoc-{m['id'][:8]}"
            
            posts_data.append({
                "id": variant_post_id,
                "platform_id": platforms[p_idx].id if platforms else "plat-02",
                "account_id": accounts[a_idx].id if accounts else "acc-02",
                "content_id": m["id"],
                "parent_post_id": parent_id,
                "post_type": "CROSS_PLATFORM" if p_idx != 0 else "RESHARE",
                "likes": int(100 * (1.0 + m["hybrid_similarity"])),
                "reshares": int(50 * (1.0 + m["hybrid_similarity"])),
                "published_at": content_item.created_at.isoformat() if content_item.created_at else ""
            })
            events_data.append({
                "id": f"event-adhoc-{idx}",
                "source_post_id": parent_id,
                "target_post_id": variant_post_id,
                "account_id": accounts[a_idx].id if accounts else "acc-02",
                "platform_id": platforms[p_idx].id if platforms else "plat-02",
                "content_id": m["id"],
                "event_type": "CROSS_PLATFORM_SHARE" if p_idx != 0 else "RESHARE",
                "timestamp": content_item.created_at.isoformat() if content_item.created_at else ""
            })
            parent_id = variant_post_id

        accounts_data = [
            {
                "id": a.id,
                "platform_id": a.platform_id,
                "pseudonym_handle": a.pseudonym_handle,
                "bot_probability": a.bot_probability,
                "is_coordinated_actor": a.is_coordinated_actor
            }
            for a in accounts
        ]
        platforms_data = [
            {
                "id": pl.id,
                "name": pl.name,
                "platform_type": pl.platform_type
            }
            for pl in platforms
        ]

        # Build NetworkX Graph using GraphBuilder.from_campaign_data
        nx_graph = GraphBuilder.from_campaign_data(
            campaign={"id": f"camp-adhoc-{content_id[:8]}", "name": "Dynamic Ad-hoc Content Propagation", "status": "ACTIVE"},
            posts=posts_data,
            events=events_data,
            accounts=accounts_data,
            platforms=platforms_data
        )

        metrics = GraphFeatureExtractor.extract_metrics(
            nx_graph,
            time_span_hours=12.0,
            total_accounts=len(accounts_data),
            total_platforms=len(platforms_data)
        )

        try:
            pagerank_scores = nx.pagerank(nx_graph, alpha=0.85) if nx_graph.number_of_nodes() > 0 else {}
        except Exception:
            pagerank_scores = {n: 1.0 / max(1, nx_graph.number_of_nodes()) for n in nx_graph.nodes()}

        try:
            betweenness_scores = nx.betweenness_centrality(nx_graph) if nx_graph.number_of_nodes() > 0 else {}
        except Exception:
            betweenness_scores = {n: 0.0 for n in nx_graph.nodes()}

        # GNN Inference
        num_nodes = nx_graph.number_of_nodes()
        node_list = list(nx_graph.nodes())
        node_to_idx = {n: i for i, n in enumerate(node_list)}

        x_feat = torch.zeros((max(1, num_nodes), 16), dtype=torch.float32)
        for i, n_id in enumerate(node_list):
            n_data = nx_graph.nodes[n_id]
            x_feat[i, 0] = float(n_data.get("bot_probability", 0.1))

        edge_list = []
        for u, v in nx_graph.edges():
            if u in node_to_idx and v in node_to_idx:
                edge_list.append([node_to_idx[u], node_to_idx[v]])

        if edge_list:
            edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)

        gnn_result = self.gnn_model.evaluate_graph(x_feat, edge_index)

        graph_nodes = []
        for n_id in node_list:
            n_attrs = nx_graph.nodes[n_id]
            pr = round(float(pagerank_scores.get(n_id, 0.0)), 4)
            bc = round(float(betweenness_scores.get(n_id, 0.0)), 4)
            graph_nodes.append({
                "id": n_id,
                "label": n_attrs.get("name") or n_attrs.get("handle") or n_attrs.get("type", "Node"),
                "type": n_attrs.get("type", "POST"),
                "pagerank": pr,
                "betweenness": bc,
                **n_attrs
            })

        graph_edges = []
        for u, v, attrs in nx_graph.edges(data=True):
            graph_edges.append({
                "id": f"edge_{u}_{v}",
                "source": u,
                "target": v,
                "type": attrs.get("type", "CONNECTED_TO"),
                "label": attrs.get("label", "")
            })

        return {
            "content_id": content_id,
            "campaign_id": f"camp-adhoc-{content_id[:8]}",
            **metrics,
            "gnn_analysis": gnn_result,
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges
        }

    def analyze_campaign_propagation(self, campaign_id: Optional[str], db: Session, fallback_content_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze full propagation network for a campaign, computing PageRank, centrality, and GNN risk.
        """
        if campaign_id:
            campaign_rec = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            posts_query = db.query(Post).filter(Post.campaign_id == campaign_id)
            events_query = db.query(PropagationEvent).filter(PropagationEvent.campaign_id == campaign_id)
        else:
            campaign_rec = None
            posts_query = db.query(Post)
            events_query = db.query(PropagationEvent)

        posts_recs = posts_query.all()
        events_recs = events_query.all()
        accounts_recs = db.query(SyntheticAccount).all()
        platforms_recs = db.query(Platform).all()

        camp_dict = {
            "id": campaign_rec.id if campaign_rec else "camp_adhoc",
            "name": campaign_rec.name if campaign_rec else "Ad-hoc Propagation Network",
            "status": campaign_rec.status if campaign_rec else "ACTIVE"
        }

        posts_data = [
            {
                "id": p.id,
                "platform_id": p.platform_id,
                "account_id": p.account_id,
                "content_id": p.content_id,
                "parent_post_id": p.parent_post_id,
                "post_type": p.post_type,
                "likes": p.likes,
                "reshares": p.reshares,
                "published_at": p.published_at.isoformat() if p.published_at else ""
            }
            for p in posts_recs
        ]

        events_data = [
            {
                "id": e.id,
                "source_post_id": e.source_post_id,
                "target_post_id": e.target_post_id,
                "account_id": e.account_id,
                "platform_id": e.platform_id,
                "content_id": e.content_id,
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat() if e.timestamp else ""
            }
            for e in events_recs
        ]

        accounts_data = [
            {
                "id": a.id,
                "platform_id": a.platform_id,
                "pseudonym_handle": a.pseudonym_handle,
                "bot_probability": a.bot_probability,
                "is_coordinated_actor": a.is_coordinated_actor
            }
            for a in accounts_recs
        ]

        platforms_data = [
            {
                "id": pl.id,
                "name": pl.name,
                "platform_type": pl.platform_type
            }
            for pl in platforms_recs
        ]

        # Build NetworkX Graph
        nx_graph = GraphBuilder.from_campaign_data(
            campaign=camp_dict,
            posts=posts_data,
            events=events_data,
            accounts=accounts_data,
            platforms=platforms_data
        )

        # Extract graph metrics
        metrics = GraphFeatureExtractor.extract_metrics(
            nx_graph,
            time_span_hours=12.0,
            total_accounts=len(accounts_data),
            total_platforms=len(platforms_data)
        )

        # Compute PageRank & Betweenness Centrality
        try:
            pagerank_scores = nx.pagerank(nx_graph, alpha=0.85) if nx_graph.number_of_nodes() > 0 else {}
        except Exception:
            pagerank_scores = {n: 1.0 / max(1, nx_graph.number_of_nodes()) for n in nx_graph.nodes()}

        try:
            betweenness_scores = nx.betweenness_centrality(nx_graph) if nx_graph.number_of_nodes() > 0 else {}
        except Exception:
            betweenness_scores = {n: 0.0 for n in nx_graph.nodes()}

        # Prepare PyG Tensor Features & Execute GNN Inference
        num_nodes = nx_graph.number_of_nodes()
        node_list = list(nx_graph.nodes())
        node_to_idx = {n: i for i, n in enumerate(node_list)}

        x_feat = torch.zeros((max(1, num_nodes), 16), dtype=torch.float32)
        for i, n_id in enumerate(node_list):
            n_data = nx_graph.nodes[n_id]
            x_feat[i, 0] = float(n_data.get("bot_probability", 0.1))
            x_feat[i, 1] = float(nx_graph.in_degree(n_id))
            x_feat[i, 2] = float(nx_graph.out_degree(n_id))
            x_feat[i, 3] = 1.0 if n_data.get("is_coordinated", False) else 0.0

        edge_list = []
        for u, v in nx_graph.edges():
            if u in node_to_idx and v in node_to_idx:
                edge_list.append([node_to_idx[u], node_to_idx[v]])

        if edge_list:
            edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)

        gnn_result = self.gnn_model.evaluate_graph(x_feat, edge_index)

        graph_nodes = []
        for n_id in node_list:
            n_attrs = nx_graph.nodes[n_id]
            pr = round(float(pagerank_scores.get(n_id, 0.0)), 4)
            bc = round(float(betweenness_scores.get(n_id, 0.0)), 4)
            graph_nodes.append({
                "id": n_id,
                "label": n_attrs.get("name") or n_attrs.get("handle") or n_attrs.get("type", "Node"),
                "type": n_attrs.get("type", "POST"),
                "pagerank": pr,
                "betweenness": bc,
                **n_attrs
            })

        graph_edges = []
        for u, v, attrs in nx_graph.edges(data=True):
            graph_edges.append({
                "id": f"edge_{u}_{v}",
                "source": u,
                "target": v,
                "type": attrs.get("type", "CONNECTED_TO"),
                "label": attrs.get("label", "")
            })

        return {
            "content_id": fallback_content_id,
            "campaign_id": campaign_id,
            **metrics,
            "gnn_analysis": gnn_result,
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges
        }
