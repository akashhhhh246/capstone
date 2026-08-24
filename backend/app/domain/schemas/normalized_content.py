from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

@dataclass
class NormalizedContent:
    """
    Normalized internal model for external and public data sources.
    Strictly distinguishes data origin (REAL_WORLD vs SYNTHETIC vs SIMULATED).
    """
    id: str
    title: str
    content: str
    url: str
    source_name: str
    source_type: str  # 'gdelt', 'rss', 'bluesky', 'user_input'
    published_at: datetime
    ingested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    author: Optional[str] = None
    language: str = "en"
    country: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    content_hash: str = ""
    original_source: Optional[str] = None
    data_origin: str = "REAL_WORLD"  # REAL_WORLD, SYNTHETIC, SIMULATED
    metadata: Dict[str, Any] = field(default_factory=dict)
