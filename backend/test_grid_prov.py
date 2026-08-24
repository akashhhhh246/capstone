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

# Find grid narrative content
grid_contents = db.query(Content).filter(Content.domain == "disinformation").all()
for c in grid_contents:
    print(f"\n==========================================")
    print(f"Checking Provenance for: {c.id} -> '{c.raw_text[:70]}...'")
    dag = prov_svc.get_provenance_for_content(c.id, db)
    print(f"Total Nodes: {dag['total_nodes']}, Total Edges: {dag['total_edges']}")
    for n in dag["nodes"]:
        print(f"  * {n['id']} ({n['type']}): rel={n.get('relationship')}, sim={n.get('similarity')}, label='{n.get('label')}', text='{n.get('text', '')[:40]}'")

db.close()
