import os
import sys
import json
import urllib.request

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.database.session import SessionLocal
from app.domain.entities.models import Content
from app.application.services.provenance_service import ProvenanceService

cid = "2f40cf41-f161-4d5a-867a-2248bcdc36ea"
db = SessionLocal()
c = db.query(Content).filter(Content.id == cid).first()
if c:
    print(f"Content found: ID={c.id}, text='{c.raw_text}'")
else:
    print(f"Content {cid} not found directly. Listing all contents:")
    for row in db.query(Content).all():
        print(f" - {row.id}: '{row.raw_text[:50]}'")

prov_svc = ProvenanceService()
if c:
    res = prov_svc.get_provenance_for_content(c.id, db)
    print(f"\nProvenance result for {cid}:")
    print(f"Total nodes: {len(res['nodes'])}, Total edges: {len(res['edges'])}")
    for n in res['nodes']:
        print(f"Node: id={n['id']}, label={n.get('label')}, rel={n.get('relationship')}, sim={n.get('similarity')}, text='{n.get('text', '')[:30]}'")

db.close()
