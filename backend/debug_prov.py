import os
import sys

# Ensure backend root in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.database.session import SessionLocal
from app.domain.entities.models import Content, Post
from app.application.services.provenance_service import ProvenanceService

db = SessionLocal()
prov_svc = ProvenanceService()

# Find first content
content = db.query(Content).first()
print(f"Target Content: {content.id} -> '{content.raw_text[:60]}...'")

dag = prov_svc.get_provenance_for_content(content.id, db)
print(f"Total Nodes: {dag['total_nodes']}, Total Edges: {dag['total_edges']}")

for n in dag["nodes"]:
    print(f" - Node {n['id']}: type={n['type']}, label={n.get('label')}, text='{n.get('text', '')[:40]}', rel={n.get('relationship')}")

db.close()
