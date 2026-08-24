import pytest
import torch
import networkx as nx
from app.ml.graph.graph_features import GraphFeatureExtractor
from app.ml.graph.gnn_model import PropagationGNN

def test_graph_feature_extraction():
    G = nx.DiGraph()
    G.add_edge("acc-1", "post-1")
    G.add_edge("post-1", "post-2")
    G.add_edge("post-1", "post-3")
    G.add_edge("post-2", "post-4")

    metrics = GraphFeatureExtractor.extract_metrics(G, time_span_hours=4.0, total_accounts=2, total_platforms=2)
    assert metrics["total_nodes"] == 5
    assert metrics["total_edges"] == 4
    assert metrics["propagation_velocity_per_hour"] > 0
    assert metrics["branching_factor"] >= 1.0

def test_gnn_model_inference():
    gnn = PropagationGNN()
    x = torch.randn(5, 16)
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]], dtype=torch.long)
    
    result = gnn.evaluate_graph(x, edge_index)
    assert "gnn_risk_score" in result
    assert 0.0 <= result["gnn_risk_score"] <= 1.0
    assert result["total_nodes_evaluated"] == 5
    assert "operational_status" in result
