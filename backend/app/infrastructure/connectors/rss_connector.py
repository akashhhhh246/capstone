import logging
import hashlib
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from email.utils import parsedate_to_datetime
from app.domain.connectors.base_connector import DataSourceConnector
from app.domain.schemas.normalized_content import NormalizedContent
from app.infrastructure.configuration.config import settings

logger = logging.getLogger("rss_connector")

class RSSConnector(DataSourceConnector):
    """
    Public RSS / Atom Feed Connector.
    Retrieves public news items from user-configured RSS feed URLs without hardcoding news sources.
    """

    def __init__(
        self,
        feed_urls: Optional[List[str]] = None,
        is_enabled: Optional[bool] = None
    ):
        enabled = is_enabled if is_enabled is not None else settings.RSS_ENABLED
        super().__init__(name="Public RSS Feeds", source_type="rss", is_enabled=enabled)
        
        if feed_urls:
            self.feed_urls = feed_urls
        else:
            raw_feeds = settings.RSS_FEEDS
            self.feed_urls = [f.strip() for f in raw_feeds.split(",") if f.strip()]

    def test_connection(self) -> bool:
        """Test accessibility of the first configured RSS feed."""
        if not self.feed_urls:
            return False
        try:
            req = urllib.request.Request(
                self.feed_urls[0],
                headers={"User-Agent": "AIShieldResearchBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                return res.status == 200
        except Exception:
            return False

    def fetch_recent(
        self,
        since: Optional[datetime] = None,
        limit: int = 25,
        query: Optional[str] = None
    ) -> List[NormalizedContent]:
        """
        Fetch and parse public RSS XML feeds into NormalizedContent.
        """
        if not self.is_enabled or not self.feed_urls:
            self.status = "DISABLED" if not self.is_enabled else "NO_FEEDS"
            return []

        all_items: List[NormalizedContent] = []
        now = datetime.now(timezone.utc)

        for feed_url in self.feed_urls:
            try:
                req = urllib.request.Request(
                    feed_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AIShieldResearchBot/1.0"}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status != 200:
                        continue
                    xml_data = response.read()

                root = ET.fromstring(xml_data)
                
                # Check for standard RSS channel items
                channel = root.find("channel")
                items = channel.findall("item") if channel is not None else root.findall(".//item")
                
                # Also support Atom format (<entry>)
                if not items:
                    items = root.findall("{http://www.w3.org/2005/Atom}entry")

                feed_title = channel.findtext("title", "RSS Feed") if channel is not None else "RSS Feed"

                for item in items[:limit]:
                    # Extract title, link, description/content
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    if not link:
                        link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                        if link_elem is not None:
                            link = link_elem.get("href", "")

                    desc = item.findtext("description", "").strip()
                    if not desc:
                        desc = item.findtext("{http://www.w3.org/2005/Atom}summary", "")

                    if not title:
                        continue

                    # Extract publication date
                    pub_date_str = item.findtext("pubDate", "")
                    if not pub_date_str:
                        pub_date_str = item.findtext("{http://www.w3.org/2005/Atom}updated", "")

                    pub_dt = now
                    if pub_date_str:
                        try:
                            pub_dt = parsedate_to_datetime(pub_date_str)
                            if pub_dt.tzinfo is None:
                                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                        except Exception:
                            pub_dt = now

                    # Synthesize text body for analysis
                    content_body = f"{title}. {desc}" if desc else title
                    content_hash = hashlib.sha256(content_body.encode("utf-8")).hexdigest()
                    doc_id = f"rss-{hashlib.md5(link.encode('utf-8') if link else title.encode('utf-8')).hexdigest()[:12]}"

                    normalized = NormalizedContent(
                        id=doc_id,
                        title=title,
                        content=content_body,
                        url=link,
                        source_name=feed_title,
                        source_type="rss",
                        published_at=pub_dt,
                        ingested_at=now,
                        author=feed_title,
                        language="en",
                        country="International",
                        topics=["Technology", "News"],
                        entities=[feed_title],
                        content_hash=content_hash,
                        original_source=feed_url,
                        data_origin="REAL_WORLD",
                        metadata={"feed_url": feed_url}
                    )
                    all_items.append(normalized)

            except Exception as e:
                logger.warning(f"Failed to fetch RSS feed {feed_url}: {e}")
                self.last_error = str(e)

        self.last_sync_at = now
        self.status = "CONNECTED" if all_items else "IDLE"
        return all_items
