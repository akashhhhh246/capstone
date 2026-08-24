import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.domain.schemas.normalized_content import NormalizedContent
from app.infrastructure.connectors.gdelt_connector import GDELTConnector
from app.infrastructure.connectors.rss_connector import RSSConnector
from app.infrastructure.connectors.bluesky_connector import BlueskyConnector
from app.application.services.ingestion_service import IngestionService
from app.domain.entities.models import Content, DetectionResult, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MOCK_GDELT_RESPONSE = {
    "articles": [
        {
            "url": "https://example.com/news/article-01",
            "title": "Global AI Safety Summit Outlines Frontier Model Standards",
            "seendate": "20260824T060000Z",
            "domain": "reuters.com",
            "language": "English",
            "sourcecountry": "United Kingdom"
        },
        {
            "url": "https://example.com/news/article-02",
            "title": "Disinformation Campaign Exploits Deepfake Audio in Regional Election",
            "seendate": "20260824T061500Z",
            "domain": "bbc.com",
            "language": "English",
            "sourcecountry": "United States"
        }
    ]
}

MOCK_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>BBC Technology News</title>
    <item>
      <title>Autonomous AI Agents Face New Security Audits</title>
      <link>https://www.bbc.com/news/technology-123456</link>
      <description>International regulators announce coordinated audits for autonomous language agents.</description>
      <pubDate>Mon, 24 Aug 2026 06:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_gdelt_connector_normalization():
    connector = GDELTConnector(is_enabled=True)
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json_bytes(MOCK_GDELT_RESPONSE)
        mock_urlopen.return_value.__enter__.return_value = mock_response

        items = connector.fetch_recent(limit=5)
        
        assert len(items) == 2
        first = items[0]
        assert isinstance(first, NormalizedContent)
        assert first.source_type == "gdelt"
        assert first.data_origin == "REAL_WORLD"
        assert "Global AI Safety" in first.title
        assert first.url == "https://example.com/news/article-01"
        assert first.content_hash != ""

def test_gdelt_connector_failure_graceful_handling():
    connector = GDELTConnector(is_enabled=True)
    
    with patch("urllib.request.urlopen", side_effect=Exception("Connection Timeout")):
        items = connector.fetch_recent(limit=5)
        assert items == []
        assert connector.status == "ERROR"
        assert "Timeout" in connector.last_error

def test_rss_connector_normalization():
    connector = RSSConnector(feed_urls=["https://feeds.test.com/rss"], is_enabled=True)
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = MOCK_RSS_XML.encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        items = connector.fetch_recent(limit=5)
        
        assert len(items) == 1
        item = items[0]
        assert item.source_type == "rss"
        assert item.data_origin == "REAL_WORLD"
        assert "Autonomous AI Agents" in item.title
        assert item.url == "https://www.bbc.com/news/technology-123456"

def test_bluesky_connector_status():
    connector = BlueskyConnector(is_enabled=False)
    assert connector.is_enabled is False
    assert connector.status == "OPTIONAL_DISABLED"
    assert connector.fetch_recent() == []

def test_ingestion_service_deduplication_and_detection(test_db):
    service = IngestionService()
    
    with patch.object(service.connectors["gdelt"], "fetch_recent") as mock_fetch:
        mock_fetch.return_value = [
            NormalizedContent(
                id="test-gdelt-001",
                title="Leaked Defense Documents On Water Contamination Hoax",
                content="URGENT BREAKING: Confidential government whistleblowers confirm coordinated water shutdown.",
                url="https://news.example.com/water-alert",
                source_name="GDELT (reuters.com)",
                source_type="gdelt",
                published_at=datetime.now(timezone.utc),
                data_origin="REAL_WORLD"
            )
        ]

        # First Ingestion
        res1 = service.ingest_from_source("gdelt", test_db)
        assert res1["ingested"] == 1
        assert res1["skipped_duplicates"] == 0

        # Verify DB records
        content = test_db.query(Content).filter(Content.url == "https://news.example.com/water-alert").first()
        assert content is not None
        assert content.data_origin == "REAL_WORLD"
        assert content.source_type == "gdelt"

        # Verify Detection Result was created through existing ML pipeline
        det = test_db.query(DetectionResult).filter(DetectionResult.content_id == content.id).first()
        assert det is not None
        assert det.classification in ["AI_GENERATED", "HUMAN"]
        assert det.confidence > 0.0

        # Second Ingestion with same item -> must detect duplicate and skip
        res2 = service.ingest_from_source("gdelt", test_db)
        assert res2["ingested"] == 0
        assert res2["skipped_duplicates"] == 1

def json_bytes(obj):
    import json
    return json.dumps(obj).encode("utf-8")
