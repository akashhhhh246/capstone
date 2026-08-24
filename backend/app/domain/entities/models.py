import enum
from datetime import datetime, timezone
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DataOriginEnum(str, enum.Enum):
    REAL_WORLD = "REAL_WORLD"
    SYNTHETIC = "SYNTHETIC"
    SIMULATED = "SIMULATED"

class ClassificationEnum(str, enum.Enum):
    HUMAN = "HUMAN"
    AI_GENERATED = "AI_GENERATED"

class WatermarkStatusEnum(str, enum.Enum):
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    UNAVAILABLE = "UNAVAILABLE"

class PostTypeEnum(str, enum.Enum):
    ORIGINAL = "ORIGINAL"
    REPOST = "REPOST"
    REPLY = "REPLY"
    QUOTE = "QUOTE"
    CROSS_PLATFORM = "CROSS_PLATFORM"

class EventTypeEnum(str, enum.Enum):
    POST = "POST"
    RESHARE = "RESHARE"
    REPLY = "REPLY"
    QUOTE = "QUOTE"
    CROSS_PLATFORM_SHARE = "CROSS_PLATFORM_SHARE"
    CONTENT_VARIANT = "CONTENT_VARIANT"

class CampaignStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CONTAINED = "CONTAINED"
    ARCHIVED = "ARCHIVED"

class SimulationStatusEnum(str, enum.Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"

class ModelStatusEnum(str, enum.Enum):
    TRAINED = "TRAINED"
    PRETRAINED = "PRETRAINED"
    DEMONSTRATION = "DEMONSTRATION"
    HEURISTIC_FALLBACK = "HEURISTIC_FALLBACK"


class Content(Base):
    __tablename__ = "contents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    text_hash = Column(String(64), index=True, nullable=False)
    title = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=False)
    url = Column(String(500), nullable=True, index=True)
    source_name = Column(String(100), nullable=True)  # e.g., 'GDELT', 'Reuters RSS', 'Benchmark'
    source_type = Column(String(50), nullable=True)   # 'gdelt', 'rss', 'bluesky', 'user_input', 'sample_dataset'
    author = Column(String(100), nullable=True)
    published_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=get_utc_now)
    source_label = Column(String(50), nullable=True)
    domain = Column(String(50), default="general")
    language = Column(String(10), default="en")
    country = Column(String(50), nullable=True)
    topics = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    data_origin = Column(String(30), default="REAL_WORLD")  # REAL_WORLD, SYNTHETIC, SIMULATED
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    detection_results = relationship("DetectionResult", back_populates="content", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="content", cascade="all, delete-orphan")


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content_id = Column(String(36), ForeignKey("contents.id"), nullable=False, index=True)
    classification = Column(String(20), nullable=False)  # HUMAN, AI_GENERATED
    confidence = Column(Float, nullable=False)
    ai_probability = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    gltr_stats = Column(JSON, default=dict)  # token distribution buckets, entropy, perplexity
    watermark_status = Column(String(30), default="NOT_SUPPORTED")
    watermark_details = Column(JSON, default=dict)
    statistical_features = Column(JSON, default=dict)  # burstiness, avg_word_len, entropy
    indicators = Column(JSON, default=list)  # list of textual explanation tags
    is_heuristic_fallback = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    content = relationship("Content", back_populates="detection_results")


class DataSourceAudit(Base):
    __tablename__ = "data_source_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_name = Column(String(50), unique=True, nullable=False)  # GDELT, RSS, Bluesky
    is_enabled = Column(Boolean, default=True)
    status = Column(String(20), default="CONNECTED")  # CONNECTED, POLLING, ERROR, DISABLED
    last_sync_at = Column(DateTime, nullable=True)
    total_ingested = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    last_error = Column(Text, default="")
    config_json = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)  # e.g. 'SimuTwitter', 'SimuTelegram'
    platform_type = Column(String(50), default="microblogging")  # microblogging, messaging, forum, news
    risk_weight = Column(Float, default=1.0)
    description = Column(String(255), default="")
    icon_name = Column(String(50), default="share")
    created_at = Column(DateTime, default=get_utc_now)

    accounts = relationship("SyntheticAccount", back_populates="platform")
    posts = relationship("Post", back_populates="platform")


class SyntheticAccount(Base):
    __tablename__ = "synthetic_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    platform_id = Column(String(36), ForeignKey("platforms.id"), nullable=False)
    pseudonym_handle = Column(String(100), nullable=False, index=True)
    account_age_days = Column(Integer, default=30)
    bot_probability = Column(Float, default=0.0)
    follower_count = Column(Integer, default=100)
    following_count = Column(Integer, default=100)
    is_coordinated_actor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    platform = relationship("Platform", back_populates="accounts")
    posts = relationship("Post", back_populates="account")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    objective = Column(String(255), default="")
    target_narrative = Column(Text, default="")
    status = Column(String(20), default="ACTIVE")  # ACTIVE, CONTAINED, ARCHIVED
    risk_score = Column(Float, default=0.0)
    gnn_risk_score = Column(Float, default=0.0)
    explainability_reasons = Column(JSON, default=list)  # list of explanatory strings
    total_events = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_platforms = Column(Integer, default=1)
    velocity_events_per_hour = Column(Float, default=0.0)
    branching_factor = Column(Float, default=1.0)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    posts = relationship("Post", back_populates="campaign")
    simulations = relationship("SimulationRun", back_populates="campaign")


class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    platform_id = Column(String(36), ForeignKey("platforms.id"), nullable=False)
    account_id = Column(String(36), ForeignKey("synthetic_accounts.id"), nullable=False)
    content_id = Column(String(36), ForeignKey("contents.id"), nullable=False)
    parent_post_id = Column(String(36), ForeignKey("posts.id"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    post_type = Column(String(30), default="ORIGINAL")  # ORIGINAL, REPOST, REPLY, QUOTE, CROSS_PLATFORM
    likes = Column(Integer, default=0)
    reshares = Column(Integer, default=0)
    published_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)

    platform = relationship("Platform", back_populates="posts")
    account = relationship("SyntheticAccount", back_populates="posts")
    content = relationship("Content", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")
    parent_post = relationship("Post", remote_side=[id], backref="child_posts")


class PropagationEvent(Base):
    __tablename__ = "propagation_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    simulation_id = Column(String(36), ForeignKey("simulation_runs.id"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=True)
    event_type = Column(String(30), nullable=False)  # POST, RESHARE, REPLY, QUOTE, CROSS_PLATFORM_SHARE, CONTENT_VARIANT
    source_post_id = Column(String(36), nullable=True)
    target_post_id = Column(String(36), nullable=True)
    account_id = Column(String(36), nullable=False)
    platform_id = Column(String(36), nullable=False)
    content_id = Column(String(36), nullable=False)
    timestamp = Column(DateTime, default=get_utc_now)
    metadata_json = Column(JSON, default=dict)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    status = Column(String(20), default="STOPPED")  # RUNNING, PAUSED, STOPPED, COMPLETED
    event_rate_per_sec = Column(Float, default=1.0)
    total_events_emitted = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=120)
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    campaign = relationship("Campaign", back_populates="simulations")


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # CLASSIFIER, GLTR, WATERMARK, EMBEDDING, GNN, RISK
    operational_status = Column(String(30), default="TRAINED")  # TRAINED, PRETRAINED, DEMONSTRATION, HEURISTIC_FALLBACK
    metrics = Column(JSON, default=dict)
    limitations = Column(Text, default="")
    dataset_info = Column(Text, default="")
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
