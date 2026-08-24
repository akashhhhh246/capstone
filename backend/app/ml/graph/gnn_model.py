import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class PropagationModel(ABC):
    """
    Abstract interface for Graph Neural Network propagation risk models.
    """

    @abstractmethod
    def evaluate_graph(self, x: torch.Tensor, edge_index: torch.Tensor) -> Dict[str, Any]:
        """Evaluate graph node embeddings and return risk score + node risk classifications."""
        pass

    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """Return model metadata, operational status, and architecture details."""
        pass


class SAGEConvLayer(nn.Module):
    """
    Native PyTorch GraphSAGE Mean-Pooling Convolution Layer.
    Implements neighborhood aggregation without external binary dependencies.
    """

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.lin_self = nn.Linear(in_channels, out_channels, bias=False)
        self.lin_neigh = nn.Linear(in_channels, out_channels, bias=True)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        num_nodes = x.size(0)
        out = self.lin_self(x)
        
        if edge_index.size(1) == 0:
            return out

        src, dst = edge_index[0], edge_index[1]
        # Aggregate neighbor features into destination nodes
        neigh_aggr = torch.zeros_like(x)
        deg = torch.zeros(num_nodes, 1, device=x.device)
        
        ones = torch.ones((src.size(0), 1), device=x.device)
        deg.scatter_add_(0, dst.unsqueeze(1), ones)
        deg = torch.clamp(deg, min=1.0)
        
        neigh_aggr.scatter_add_(0, dst.unsqueeze(1).expand(-1, x.size(1)), x[src])
        neigh_aggr = neigh_aggr / deg
        
        return out + self.lin_neigh(neigh_aggr)


class PropagationGNN(nn.Module, PropagationModel):
    """
    Two-layer Graph Neural Network (GraphSAGE architecture) for
    Propagation Risk Assessment and Coordinated Inauthentic Behavior (CIB) detection.
    """

    MODEL_NAME = "PyG GraphSAGE Propagation Risk Evaluator"
    VERSION = "gnn-sage-v1.0"

    def __init__(self, in_features: int = 16, hidden_dim: int = 32, num_classes: int = 2, model_path: Optional[str] = None):
        super().__init__()
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.model_path = model_path or "./models/gnn_propagation_model.pt"

        # 2-layer GraphSAGE architecture
        self.conv1 = SAGEConvLayer(in_features, hidden_dim)
        self.conv2 = SAGEConvLayer(hidden_dim, hidden_dim)
        
        # Node classification head (0: Benign / Normal, 1: Coordinated / High Risk)
        self.node_classifier = nn.Linear(hidden_dim, num_classes)
        
        # Graph-level risk pooling head
        self.graph_risk_head = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

        self.is_trained = False
        self.operational_status = "DEMONSTRATION"  # TRAINED, PRETRAINED, DEMONSTRATION

        # Load weights if available
        if os.path.exists(self.model_path):
            self.load_model(self.model_path)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        Returns: (node_logits: [N, num_classes], graph_risk: [1])
        """
        h1 = F.relu(self.conv1(x, edge_index))
        h1 = F.dropout(h1, p=0.1, training=self.training)
        h2 = F.relu(self.conv2(h1, edge_index))
        
        # Node logits
        node_logits = self.node_classifier(h2)
        
        # Global mean pooling for graph-level risk score
        if h2.size(0) > 0:
            graph_rep = torch.mean(h2, dim=0, keepdim=True)
            graph_risk = self.graph_risk_head(graph_rep)
        else:
            graph_risk = torch.tensor([[0.0]])
            
        return node_logits, graph_risk.squeeze(-1)

    def evaluate_graph(self, x: torch.Tensor, edge_index: torch.Tensor) -> Dict[str, Any]:
        """
        Inference on an arbitrary propagation graph.
        """
        self.eval()
        with torch.no_grad():
            node_logits, graph_risk = self.forward(x, edge_index)
            node_probs = F.softmax(node_logits, dim=-1)
            high_risk_node_probs = node_probs[:, 1].tolist() if node_probs.size(0) > 0 else []
            risk_val = float(graph_risk.item()) if graph_risk.numel() > 0 else 0.0

        # Identified suspicious node indices
        suspicious_nodes = [i for i, p in enumerate(high_risk_node_probs) if p >= 0.6]

        return {
            "gnn_risk_score": round(risk_val, 4),
            "total_nodes_evaluated": x.size(0),
            "high_risk_nodes_count": len(suspicious_nodes),
            "suspicious_node_indices": suspicious_nodes,
            "node_risk_probabilities": [round(p, 4) for p in high_risk_node_probs],
            "model_version": self.VERSION,
            "operational_status": self.operational_status
        }

    def train_synthetic_benchmark(self, epochs: int = 50) -> Dict[str, Any]:
        """
        Train GNN on a reproducible synthetic graph benchmark dataset
        simulating coordinated propagation cascades vs organic viral cascades.
        """
        self.train()
        optimizer = torch.optim.Adam(self.parameters(), lr=0.01, weight_decay=1e-4)

        # Generate synthetic benchmark cascades
        torch.manual_seed(42)
        
        for epoch in range(epochs):
            # Synthetic batch: 20 nodes with 16 features
            # Features: [bot_score, in_deg, out_deg, velocity, sim_score, platform_id_onehot...]
            x_syn = torch.randn(20, self.in_features)
            
            # Synthetic edge index (star/cascade graph)
            src = torch.tensor([0, 0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            dst = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
            edge_idx = torch.stack([src, dst], dim=0)

            # Node labels (0 or 1)
            y_nodes = torch.tensor([1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=torch.long)
            y_graph = torch.tensor([0.85], dtype=torch.float32)

            optimizer.zero_grad()
            node_logits, graph_risk = self.forward(x_syn, edge_idx)
            
            loss_node = F.cross_entropy(node_logits, y_nodes)
            loss_graph = F.mse_loss(graph_risk, y_graph)
            loss = loss_node + loss_graph
            
            loss.backward()
            optimizer.step()

        self.is_trained = True
        self.operational_status = "TRAINED"
        self.save_model()
        return {"final_loss": round(float(loss.item()), 4), "status": self.operational_status}

    def save_model(self, path: Optional[str] = None) -> None:
        target = path or self.model_path
        os.makedirs(os.path.dirname(target), exist_ok=True)
        torch.save({
            "state_dict": self.state_dict(),
            "in_features": self.in_features,
            "hidden_dim": self.hidden_dim,
            "operational_status": self.operational_status,
            "version": self.VERSION
        }, target)

    def load_model(self, path: Optional[str] = None) -> bool:
        target = path or self.model_path
        if not os.path.exists(target):
            return False
        try:
            ckpt = torch.load(target, map_location="cpu")
            self.load_state_dict(ckpt["state_dict"])
            self.operational_status = ckpt.get("operational_status", "TRAINED")
            self.is_trained = True
            return True
        except Exception:
            return False

    def get_model_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.MODEL_NAME,
            "version": self.VERSION,
            "model_type": "PYG_GRAPHSAGE_GNN",
            "operational_status": self.operational_status,
            "in_features": self.in_features,
            "hidden_dim": self.hidden_dim,
            "num_classes": self.num_classes,
            "description": "Multi-layer GraphSAGE GNN for propagation pattern classification and campaign risk scoring.",
            "limitations": "Trained on synthetic propagation benchmarks; graph topology variance in novel environments can affect calibration."
        }
