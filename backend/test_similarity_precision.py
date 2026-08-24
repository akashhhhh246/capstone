import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.infrastructure.database.session import SessionLocal
from app.domain.entities.models import Content
from app.ml.similarity.similarity_service import SimilarityService

db = SessionLocal()
sim_svc = SimilarityService()

contents = db.query(Content).all()
print(f"Total contents in DB: {len(contents)}")

# Test 1: Grid Disinformation vs everything
grid_text = "URGENT BREAKING: Confidential government whistleblowers have confirmed that national energy grid switching systems are undergoing a coordinated clandestine shutdown tonight at midnight to enforce simulated blackout mandates. Withdraw all bank funds immediately before ATMs freeze! #GridDown #EmergencyAlert"

matches = sim_svc.find_near_duplicates(
    grid_text,
    [{"id": c.id, "text": c.raw_text} for c in contents],
    threshold=0.65
)

print(f"\nMatches for Power Grid Disinformation (Threshold >= 0.65):")
for m in matches:
    print(f" - {m['id']}: Hybrid={m['hybrid_similarity']} (TF-IDF={m['tfidf_similarity']}, Dense={m['embedding_similarity']})")
    print(f"   Text: '{m['text'][:80]}...'")

# Test 2: Solar Orbiter Science article vs everything
solar_text = "The European Space Agency's Solar Orbiter spacecraft has captured the highest-resolution images of the Sun's surface to date, revealing fine magnetic structures across the corona. Researchers utilized extreme ultraviolet spectroscopy to measure coronal heating mechanisms across the solar transition region. The findings were published this week in Astronomy & Astrophysics."

matches_solar = sim_svc.find_near_duplicates(
    solar_text,
    [{"id": c.id, "text": c.raw_text} for c in contents],
    threshold=0.65
)

print(f"\nMatches for Solar Science (Threshold >= 0.65):")
for m in matches_solar:
    print(f" - {m['id']}: Hybrid={m['hybrid_similarity']} (TF-IDF={m['tfidf_similarity']}, Dense={m['embedding_similarity']})")
    print(f"   Text: '{m['text'][:80]}...'")

db.close()
