from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Detection DTOs
class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Raw text snippet or social media post content to evaluate.")
    domain: Optional[str] = Field("general", description="Domain context (e.g. science, civic, news, social).")
    register_content: Optional[bool] = Field(False, description="Whether to automatically register content in the provenance database.")

class GLTRBucketDistribution(BaseModel):
    green: float
    yellow: float
    red: float
    purple: float

class GLTRTokenInfo(BaseModel):
    token: str
    rank: int
    bucket: str
    prob: float
    log_prob: float

class GLTRResult(BaseModel):
    tokens: List[GLTRTokenInfo]
    bucket_distribution: GLTRBucketDistribution
    estimated_perplexity: float
    mean_cross_entropy: float
    ai_likelihood_indicator: float
    analysis_mode: str
    methodology: str
    disclaimer: str

class WatermarkResult(BaseModel):
    status: str
    confidence: float
    scheme: str
    details: Dict[str, Any]

class ClassifierResult(BaseModel):
    predicted_class: str
    p_human: float
    p_ai: float
    confidence: float
    model_version: str
    is_trained: bool

class DetectionResultResponse(BaseModel):
    content_id: Optional[str] = None
    classification: str
    confidence: float
    ai_probability: float
    classifier_result: ClassifierResult
    gltr_result: GLTRResult
    watermark_result: WatermarkResult
    statistical_features: Dict[str, Any]
    indicators: List[str]
    model_version: str
    timestamp: str
    disclaimer: str

# Content DTOs
class ContentCreateRequest(BaseModel):
    text: str
    domain: Optional[str] = "general"
    source_label: Optional[str] = "analyst_submission"

class ContentResponse(BaseModel):
    id: str
    text_hash: str
    raw_text: str
    clean_text: str
    domain: str
    word_count: int
    char_count: int
    created_at: str
    latest_detection: Optional[Dict[str, Any]] = None

# Provenance DTOs
class ProvenanceGraphNode(BaseModel):
    id: str
    label: str
    type: str  # CONTENT, POST, SYNTHETIC_ACCOUNT, PLATFORM
    text: Optional[str] = None
    platform: Optional[str] = None
    account: Optional[str] = None
    similarity: Optional[float] = None
    relationship: Optional[str] = None
    created_at: Optional[str] = None
    is_target: Optional[bool] = False

class ProvenanceGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: Optional[str] = None
    similarity: Optional[float] = None

class ProvenanceResponse(BaseModel):
    target_content_id: str
    root_origin: Optional[Dict[str, Any]] = None
    total_nodes: int
    total_edges: int
    nodes: List[ProvenanceGraphNode]
    edges: List[ProvenanceGraphEdge]
    is_acyclic: bool

# Propagation & Graph DTOs
class PropagationMetricsResponse(BaseModel):
    content_id: Optional[str] = None
    campaign_id: Optional[str] = None
    total_nodes: int
    total_edges: int
    propagation_velocity_per_hour: float
    estimated_reach: int
    reshare_depth: int
    branching_factor: float
    avg_degree: float
    max_degree: int
    clustering_coefficient: float
    top_hub_centrality: float
    total_platforms: int
    total_accounts: int
    coordinated_indicators: List[str]
    gnn_analysis: Optional[Dict[str, Any]] = None
    graph_nodes: List[Dict[str, Any]] = []
    graph_edges: List[Dict[str, Any]] = []

# Campaign DTOs
class CampaignResponse(BaseModel):
    id: str
    name: str
    objective: str
    target_narrative: str
    status: str
    risk_score: float
    gnn_risk_score: float
    severity: str
    explainability_reasons: List[str]
    total_events: int
    total_reach: int
    total_platforms: int
    velocity_events_per_hour: float
    branching_factor: float
    created_at: str

class CampaignDetailResponse(CampaignResponse):
    posts: List[Dict[str, Any]] = []
    platforms: List[Dict[str, Any]] = []
    accounts: List[Dict[str, Any]] = []
    graph_metrics: Dict[str, Any] = {}

# Simulation DTOs
class SimulationStartRequest(BaseModel):
    campaign_id: str
    event_rate_per_sec: Optional[float] = 1.5
    duration_seconds: Optional[int] = 120

class SimulationResponse(BaseModel):
    id: str
    campaign_id: str
    status: str
    event_rate_per_sec: float
    total_events_emitted: Optional[int] = 0
    duration_seconds: int
    started_at: Optional[str] = None
    paused_at: Optional[str] = None
    stopped_at: Optional[str] = None

class SimulationEventPayload(BaseModel):
    event_id: str
    simulation_id: str
    campaign_id: str
    event_type: str
    source_post_id: Optional[str] = None
    target_post_id: Optional[str] = None
    account_id: str
    account_handle: str
    platform_id: str
    platform_name: str
    content_id: str
    content_snippet: str
    timestamp: str
    velocity: float
    total_reach: int
    risk_score: float

# Models Governance DTO
class ModelDetail(BaseModel):
    name: str
    version: str
    model_type: str
    operational_status: str
    metrics: Dict[str, Any]
    limitations: str
    dataset_info: str

# Dashboard Stats DTO
class DashboardStatsResponse(BaseModel):
    total_analyzed_content: int
    human_content_count: int
    ai_content_count: int
    suspicious_content_count: int
    active_campaigns_count: int
    high_risk_campaigns_count: int
    active_simulations_count: int
    platforms_count: int
    recent_alerts: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    platform_breakdown: List[Dict[str, Any]]
    recent_analyses: List[Dict[str, Any]]
