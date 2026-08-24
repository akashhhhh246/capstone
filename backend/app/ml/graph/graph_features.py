import math
import collections
from typing import Dict, Any, List
import networkx as nx

class GraphFeatureExtractor:
    """
    Computes structural graph metrics, propagation kinematics,
    and Coordinated Inauthentic Behavior (CIB) indicators from NetworkX graphs.
    """

    @classmethod
    def extract_metrics(
        cls,
        graph: nx.DiGraph,
        time_span_hours: float = 24.0,
        total_accounts: int = 0,
        total_platforms: int = 1
    ) -> Dict[str, Any]:
        """Compute complete propagation metrics dictionary."""
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()

        if num_nodes == 0:
            return cls._empty_metrics()

        # Reshare depth (longest shortest path or DAG longest path)
        try:
            if nx.is_directed_acyclic_graph(graph):
                depth = nx.dag_longest_path_length(graph)
            else:
                depth = nx.diameter(graph.to_undirected()) if nx.is_connected(graph.to_undirected()) else 1
        except Exception:
            depth = 1

        # Branching factor (mean out-degree of non-leaf nodes)
        out_degrees = [d for n, d in graph.out_degree() if d > 0]
        branching_factor = round(sum(out_degrees) / max(1, len(out_degrees)), 2) if out_degrees else 1.0

        # Degree centrality and betweenness
        degree_dict = dict(graph.degree())
        max_degree = max(degree_dict.values()) if degree_dict else 0
        avg_degree = round(sum(degree_dict.values()) / max(1, num_nodes), 2)

        try:
            betweenness = nx.betweenness_centrality(graph)
            top_hub_score = round(max(betweenness.values()), 4) if betweenness else 0.0
        except Exception:
            top_hub_score = 0.0

        # Clustering coefficient (on undirected view)
        try:
            undirected_g = graph.to_undirected()
            clustering_coeff = round(nx.average_clustering(undirected_g), 4)
        except Exception:
            clustering_coeff = 0.0

        # Propagation velocity: (total edge events) / max(0.5, time_span_hours)
        velocity = round(num_edges / max(0.5, time_span_hours), 2)

        # Estimated Reach: simulated reach based on accounts and branching amplification
        reach = int(max(num_nodes * 15, num_edges * 45))

        # Coordinated Inauthentic Behavior (CIB) Indicators
        cib_indicators = []
        if branching_factor > 3.0:
            cib_indicators.append("High branching factor indicates automated burst resharing.")
        if top_hub_score > 0.4:
            cib_indicators.append("Centralized hub node orchestrating multi-channel distribution.")
        if velocity > 10.0:
            cib_indicators.append("Elevated propagation velocity surpassing typical organic dissemination.")
        if total_platforms >= 3:
            cib_indicators.append("Synchronized cross-platform deployment across 3+ distinct platforms.")

        return {
            "total_nodes": num_nodes,
            "total_edges": num_edges,
            "propagation_velocity_per_hour": velocity,
            "estimated_reach": reach,
            "reshare_depth": depth,
            "branching_factor": branching_factor,
            "avg_degree": avg_degree,
            "max_degree": max_degree,
            "clustering_coefficient": clustering_coeff,
            "top_hub_centrality": top_hub_score,
            "total_platforms": max(1, total_platforms),
            "total_accounts": max(1, total_accounts),
            "coordinated_indicators": cib_indicators
        }

    @classmethod
    def _empty_metrics(cls) -> Dict[str, Any]:
        return {
            "total_nodes": 0,
            "total_edges": 0,
            "propagation_velocity_per_hour": 0.0,
            "estimated_reach": 0,
            "reshare_depth": 0,
            "branching_factor": 1.0,
            "avg_degree": 0.0,
            "max_degree": 0,
            "clustering_coefficient": 0.0,
            "top_hub_centrality": 0.0,
            "total_platforms": 1,
            "total_accounts": 0,
            "coordinated_indicators": []
        }
