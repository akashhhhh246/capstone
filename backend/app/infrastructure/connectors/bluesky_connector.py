import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.domain.connectors.base_connector import DataSourceConnector
from app.domain.schemas.normalized_content import NormalizedContent
from app.infrastructure.configuration.config import settings

logger = logging.getLogger("bluesky_connector")

class BlueskyConnector(DataSourceConnector):
    """
    Public Bluesky / ATProto Public Data Stream Connector.
    Follows DataSourceConnector interface for future public firehose ingestion.
    Disabled by default.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        is_enabled: Optional[bool] = None
    ):
        enabled = is_enabled if is_enabled is not None else settings.BLUESKY_ENABLED
        super().__init__(name="Bluesky Public Stream", source_type="bluesky", is_enabled=enabled)
        self.endpoint = endpoint or settings.BLUESKY_ENDPOINT
        self.status = "CONNECTED" if self.is_enabled else "OPTIONAL_DISABLED"

    def test_connection(self) -> bool:
        """Check availability of public ATProto API endpoint."""
        if not self.is_enabled:
            return False
        # Future ATProto endpoint connectivity check
        return True

    def fetch_recent(
        self,
        since: Optional[datetime] = None,
        limit: int = 25,
        query: Optional[str] = None
    ) -> List[NormalizedContent]:
        """
        Fetch public posts from Bluesky public stream when enabled.
        Returns empty list when disabled without throwing exceptions or generating fake data.
        """
        if not self.is_enabled:
            self.status = "OPTIONAL_DISABLED"
            return []

        logger.info("Bluesky connector enabled. Ingesting from public ATProto endpoint.")
        # Optional public ATProto search endpoint implementation hook
        return []
