from fastapi import APIRouter
from typing import List, Dict, Any
from app.ml.detection.tfidf_classifier import TFIDFContentClassifier
from app.ml.detection.gltr_analyzer import GLTRStatisticalAnalyzer
from app.ml.detection.watermark_detector import KirchenbauerWatermarkDetector
from app.ml.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.ml.graph.gnn_model import PropagationGNN

router = APIRouter(prefix="/models", tags=["Model Governance & Transparency"])

@router.get("", response_model=List[Dict[str, Any]])
def list_models_metadata():
    """
    Retrieve transparency audit cards for all ML models, algorithms, and heuristic providers.
    Explicitly reports operational status (TRAINED, PRETRAINED, DEMONSTRATION, HEURISTIC_FALLBACK)
    along with limitations, methodology, and ethical oversight considerations.
    """
    tfidf = TFIDFContentClassifier()
    gltr = GLTRStatisticalAnalyzer()
    wm = KirchenbauerWatermarkDetector()
    embed = SentenceTransformerProvider()
    gnn = PropagationGNN()

    models_data = [
        {
            "id": "model_tfidf_clf",
            "name": "TF-IDF + Logistic Regression Binary Classifier",
            "version": tfidf.VERSION,
            "model_type": "STATISTICAL_NLP_CLASSIFIER",
            "operational_status": "TRAINED" if tfidf.is_trained else "HEURISTIC_FALLBACK",
            "methodology": "Word and sub-word n-gram (1-2) TF-IDF vectorization with calibrated L2-regularized logistic regression.",
            "metrics": tfidf.metrics,
            "dataset_info": "Curated benchmark containing real human journalism/science and synthetic LLM generation samples (sample_dataset.json).",
            "limitations": "Susceptible to stylistic perturbations, high lexical diversity variations, and short text fragments (<25 words)."
        },
        {
            "id": "model_gltr_stats",
            "name": "GLTR Statistical Token Distribution Analyzer",
            "version": gltr.VERSION,
            "model_type": "TOKEN_STATISTICAL_ANALYZER",
            "operational_status": "DEMONSTRATION",
            "methodology": "Categorizes token frequencies into likelihood tiers (Top 10 Green, Top 100 Yellow, Top 1000 Red, Tail Purple) and estimates perplexity.",
            "metrics": {"buckets_supported": 4, "top_k_ranks": [10, 100, 1000]},
            "dataset_info": "Reference corpus frequency distributions from English vocabulary baselines.",
            "limitations": "Approximates language model probabilities. Highly technical or domain-specific jargon may register as low probability (purple) false positives."
        },
        {
            "id": "model_watermark_verifier",
            "name": "Kirchenbauer Green-List Watermark Detector",
            "version": "wm-kirchenbauer-v1.0",
            "model_type": "WATERMARK_STATISTICAL_TEST",
            "operational_status": "TRAINED",
            "methodology": "One-tailed hypothesis test (z-score) evaluating whether token transitions disproportionately follow pseudo-random keyed green partitions.",
            "metrics": {"z_threshold": 4.0, "null_gamma": 0.5},
            "dataset_info": "Cryptographic PRNG seed agreement verification.",
            "limitations": "Requires known key agreement; vulnerable to token deletion, aggressive paraphrasing, or non-watermarked generative models."
        },
        {
            "id": "model_sentence_embeddings",
            "name": "SentenceTransformers Dense Semantic Embedding",
            "version": "all-MiniLM-L6-v2",
            "model_type": "TRANSFORMER_DENSE_EMBEDDING",
            "operational_status": embed.get_provider_metadata()["status"],
            "methodology": "384-dimensional dense semantic vector projection optimized for cosine similarity and cross-platform narrative tracking.",
            "metrics": {"embedding_dimension": 384, "metric": "cosine_similarity"},
            "dataset_info": "Pretrained on 1B+ sentence pairs for sentence semantic textual similarity.",
            "limitations": "Embedding cosine similarity alone does not establish malicious intent; must be contextualized with graph velocity."
        },
        {
            "id": "model_pyg_gnn",
            "name": "PyTorch Geometric GraphSAGE Propagation GNN",
            "version": gnn.VERSION,
            "model_type": "GRAPH_NEURAL_NETWORK",
            "operational_status": gnn.operational_status,
            "methodology": "2-layer GraphSAGE mean-pooling message-passing neural network for node classification and cascade risk scoring.",
            "metrics": {"in_features": 16, "hidden_dim": 32, "pooling": "global_mean"},
            "dataset_info": "Reproducible synthetic multi-platform cascade benchmarks simulating coordinated bot bursts vs organic diffusion.",
            "limitations": "Graph topology differences between simulated and real-world network structures may impact transferability."
        }
    ]

    return models_data
