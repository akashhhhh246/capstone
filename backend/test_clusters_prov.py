import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.database.session import SessionLocal
from app.domain.entities.models import Content
from app.application.services.provenance_service import ProvenanceService

db = SessionLocal()
prov_svc = ProvenanceService()

test_clusters = [
    ("jwst-001", "NASA JWST Cosmic Discovery Cluster"),
    ("ai-reg-001", "EU AI Governance & Regulation Cluster"),
    ("grid-001", "Power Grid Disinformation Campaign Cluster"),
    ("battery-001", "MIT Solid-State Battery Energy Cluster"),
    ("semi-001", "ASML High-NA EUV Semiconductor Cluster"),
    ("water-001", "Water Contamination Disinformation Cluster"),
    ("stand-001", "Standalone Machine Learning Research Paper"),
]

for cid, name in test_clusters:
    print(f"\n==================================================")
    print(f"Cluster: {name} (ID: {cid})")
    dag = prov_svc.get_provenance_for_content(cid, db)
    print(f"Total Nodes in DAG: {dag['total_nodes']}, Total Edges: {dag['total_edges']}")
    for n in dag["nodes"]:
        print(f"  * [{n.get('relationship', 'N/A')}] (Sim: {int((n.get('similarity') or 0)*100)}%) Node: {n['id']} ({n.get('platform', 'N/A')}) -> '{n.get('text', '')[:65]}...'")

db.close()
