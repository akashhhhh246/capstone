import os
from typing import Dict, Any, List, Optional
import torch
from sqlalchemy.orm import Session
from app.domain.entities.models import Campaign, Post, Platform, SyntheticAccount, PropagationEvent, Content
from app.ml.graph.graph_builder import GraphBuilder
from app.ml.graph.graph_features import GraphFeatureExtractor
from app.ml.graph.gnn_model import PropagationGNN

class PropagationService:
    """
    Application Service for Propagation Graph Analysis & Graph ML Inference.
    Extracts structural NetworkX metrics and executes PyTorch Geometric GNN inference.
    """

    def __init__(self, gnn_model: Optional[PropagationGNN] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_gnn_path = os.path.join(base_dir, "models", "gnn_propagation_model.pt")
        self.gnn_model = gnn_model or PropagationGNN(model_path=default_gnn_path)

    def analyze_propagation_for_content(self, content_id: str, db: Session) -> Dict[str, Any]:
        """
        Analyze propagation graph metrics for a specific content item across campaigns.
        If no direct posts exist for new content, analyzes nearest or active propagation network.
        """
        posts = db.query(Post).filter(Post.content_id == content_id).all()
        campaign_ids = list(set([p.campaign_id for p in posts if p.campaign_id]))
        campaign_id = campaign_ids[0] if campaign_ids else None
        
        # If no direct campaign assigned yet, pull the most active campaign for graph context
        if not campaign_id:
            active_camp = db.query(Campaign).order_by(Campaign.risk_score.desc()).first()
            if active_camp:
                campaign_id = active_camp.id

        return self.analyze_campaign_propagation(campaign_id, db, fallback_content_id=content_id)

    def analyze_campaign_propagation(self, campaign_id: Optional[str], db: Session, fallback_content_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze full propagation network for a campaign.
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
            graph_nodes.append({
                "id": n_id,
                "label": n_attrs.get("name") or n_attrs.get("handle") or n_attrs.get("type", "Node"),
                "type": n_attrs.get("type", "POST"),
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
