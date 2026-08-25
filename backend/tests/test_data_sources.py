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
        # Should gracefully return fallback real-world articles for continuous operational uptime
        assert len(items) > 0
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

def test_dynamic_campaign_discovery_from_live_content(test_db):
    from app.domain.entities.models import Platform, SyntheticAccount, Campaign
    from app.application.services.campaign_discovery_service import CampaignDiscoveryService

    # Setup basic test platforms and accounts
    plat = Platform(id="plat-test-01", name="TestTwitter", platform_type="microblogging", risk_weight=1.0)
    acc = SyntheticAccount(id="acc-test-01", platform_id="plat-test-01", pseudonym_handle="@bot_test", bot_probability=0.9)
    test_db.add_all([plat, acc])
    test_db.commit()

    # Seed 2 live contents with high semantic similarity
    now = datetime.now(timezone.utc)
    c1 = Content(
        id="c-live-01",
        text_hash="hash01",
        raw_text="URGENT ALERT: Confidential whistleblowers confirm coordinated power grid shutdown tonight at midnight.",
        clean_text="URGENT ALERT: Confidential whistleblowers confirm coordinated power grid shutdown tonight at midnight.",
        title="Power Grid Emergency Alert",
        domain="disinformation",
        created_at=now
    )
    c2 = Content(
        id="c-live-02",
        text_hash="hash02",
        raw_text="EMERGENCY BULLETIN: Whistleblowers report coordinated electric grid blackout tonight. Withdraw funds immediately!",
        clean_text="EMERGENCY BULLETIN: Whistleblowers report coordinated electric grid blackout tonight. Withdraw funds immediately!",
        title="Electric Grid Blackout Warning",
        domain="disinformation",
        created_at=now + datetime.resolution
    )
    test_db.add_all([c1, c2])
    test_db.commit()

    # Run discovery engine
    discovery = CampaignDiscoveryService()
    discovered = discovery.discover_and_update_campaigns(test_db, similarity_threshold=0.55)

    assert len(discovered) >= 1
    first_camp = discovered[0]
    assert "camp-live-" in first_camp["id"]
    assert len(first_camp["explainability_reasons"]) >= 3
    assert any("[NARRATIVE HARM]" in r for r in first_camp["explainability_reasons"])

    # Verify DB persistence
    saved_camp = test_db.query(Campaign).filter(Campaign.id == first_camp["id"]).first()
    assert saved_camp is not None
    assert saved_camp.risk_score > 0.0

def json_bytes(obj):
    import json
    return json.dumps(obj).encode("utf-8")
