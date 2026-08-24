import os
import sys
import json

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from app.ml.detection.tfidf_classifier import TFIDFContentClassifier
from app.ml.graph.gnn_model import PropagationGNN

def train_all():
    print("==================================================")
    print("AI-Driven Malign InfoOps Defense — Model Training")
    print("==================================================")
    
    models_dir = os.path.join(backend_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    dataset_path = os.path.join(backend_dir, "data", "sample_dataset.json")
    tfidf_path = os.path.join(models_dir, "tfidf_classifier.joblib")
    gnn_path = os.path.join(models_dir, "gnn_propagation_model.pt")

    # 1. Train TF-IDF Classifier
    print(f"\n[1/2] Training TF-IDF + Logistic Regression Classifier from {dataset_path}...")
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    classifier = TFIDFContentClassifier(model_path=tfidf_path)
    metrics = classifier.train(texts, labels)
    classifier.save(tfidf_path)

    print(f"  -> Model saved to: {tfidf_path}")
    print(f"  -> Accuracy: {metrics['accuracy'] * 100:.1f}%")
    print(f"  -> Precision: {metrics['precision'] * 100:.1f}%")
    print(f"  -> Recall: {metrics['recall'] * 100:.1f}%")
    print(f"  -> F1 Score: {metrics['f1_score'] * 100:.1f}%")
    print(f"  -> Trained on {metrics['training_samples']} samples.")

    # 2. Train PyTorch Geometric GraphSAGE GNN
    print(f"\n[2/2] Training PyG GraphSAGE GNN Propagation Model...")
    gnn = PropagationGNN(model_path=gnn_path)
    gnn_res = gnn.train_synthetic_benchmark(epochs=50)
    print(f"  -> Model saved to: {gnn_path}")
    print(f"  -> Training Loss: {gnn_res['final_loss']}")
    print(f"  -> Operational Status: {gnn_res['status']}")

    print("\n==================================================")
    print("All Models Successfully Trained and Persisted!")
    print("==================================================")

if __name__ == "__main__":
    train_all()
