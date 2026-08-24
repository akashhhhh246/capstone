from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.schemas.normalized_content import NormalizedContent

class DataSourceConnector(ABC):
    """
    Abstract Base Class for all external data source connectors.
    Provides uniform interfaces for fetching recent records, health checks, and status telemetry.
    """

    def __init__(self, name: str, source_type: str, is_enabled: bool = True):
        self.name = name
        self.source_type = source_type
        self.is_enabled = is_enabled
        self.last_sync_at: Optional[datetime] = None
        self.total_ingested: int = 0
        self.duplicates_skipped: int = 0
        self.last_error: str = ""
        self.status: str = "CONNECTED" if is_enabled else "DISABLED"

    @abstractmethod
    def fetch_recent(
        self,
        since: Optional[datetime] = None,
        limit: int = 50,
        query: Optional[str] = None
    ) -> List[NormalizedContent]:
        """
        Fetch recent content from the external public data source and normalize records.
        Must handle errors gracefully and return empty list on network/API failure without crashing.
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Verify API connectivity or endpoint availability."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Return connector runtime status telemetry."""
        return {
            "source_name": self.name,
            "source_type": self.source_type,
            "is_enabled": self.is_enabled,
            "status": self.status,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "total_ingested": self.total_ingested,
            "duplicates_skipped": self.duplicates_skipped,
            "last_error": self.last_error,
        }
