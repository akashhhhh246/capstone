import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ml.similarity.similarity_service import SimilarityService
from data.generate_rich_dataset import DATASET

sim_svc = SimilarityService()

print("Pairwise similarity scores within clusters:")

# Test Cluster JWST
t1 = DATASET[0]["text"] # jwst-001 (Root)
for item in DATASET[1:4]:
    t2 = item["text"]
    scores = sim_svc.compute_hybrid_similarity(t1, [t2])[0]
    print(f"JWST-001 vs {item['id']} ({item['cluster_role']}): Hybrid={scores['hybrid_similarity']:.3f}, TF-IDF={scores['tfidf_similarity']:.3f}, Dense={scores['embedding_similarity']:.3f}")

# Test Cluster AI Governance
t_ai = DATASET[4]["text"] # ai-reg-001 (Root)
for item in DATASET[5:8]:
    t2 = item["text"]
    scores = sim_svc.compute_hybrid_similarity(t_ai, [t2])[0]
    print(f"AI-REG-001 vs {item['id']} ({item['cluster_role']}): Hybrid={scores['hybrid_similarity']:.3f}, TF-IDF={scores['tfidf_similarity']:.3f}, Dense={scores['embedding_similarity']:.3f}")

# Test Cluster Grid Disinfo
t_grid = DATASET[8]["text"] # grid-001 (Root)
for item in DATASET[9:13]:
    t2 = item["text"]
    scores = sim_svc.compute_hybrid_similarity(t_grid, [t2])[0]
    print(f"GRID-001 vs {item['id']} ({item['cluster_role']}): Hybrid={scores['hybrid_similarity']:.3f}, TF-IDF={scores['tfidf_similarity']:.3f}, Dense={scores['embedding_similarity']:.3f}")
