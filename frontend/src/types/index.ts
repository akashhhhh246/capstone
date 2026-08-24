export interface GLTRBucketDistribution {
  green: number;
  yellow: number;
  red: number;
  purple: number;
}

export interface GLTRTokenInfo {
  token: string;
  rank: number;
  bucket: 'green' | 'yellow' | 'red' | 'purple' | 'whitespace';
  prob: number;
  log_prob: number;
}

export interface GLTRResult {
  tokens: GLTRTokenInfo[];
  bucket_distribution: GLTRBucketDistribution;
  estimated_perplexity: number;
  mean_cross_entropy: number;
  ai_likelihood_indicator: number;
  analysis_mode: string;
  methodology: string;
  disclaimer: string;
}

export interface WatermarkResult {
  status: 'DETECTED' | 'NOT_DETECTED' | 'NOT_SUPPORTED' | 'UNAVAILABLE';
  confidence: number;
  scheme: string;
  details: Record<string, any>;
}

export interface ClassifierResult {
  predicted_class: 'HUMAN' | 'AI_GENERATED';
  p_human: number;
  p_ai: number;
  confidence: number;
  model_version: string;
  is_trained: boolean;
}

export interface DetectionResultResponse {
  content_id?: string;
  classification: 'HUMAN' | 'AI_GENERATED';
  confidence: number;
  ai_probability: number;
  classifier_result: ClassifierResult;
  gltr_result: GLTRResult;
  watermark_result: WatermarkResult;
  statistical_features: Record<string, any>;
  indicators: string[];
  model_version: string;
  timestamp: string;
  disclaimer: string;
}

export interface ContentItem {
  id: string;
  text_hash: string;
  title?: string;
  raw_text: string;
  clean_text: string;
  url?: string;
  source_name?: string;
  source_type?: string;
  author?: string;
  published_at?: string;
  ingested_at?: string;
  domain: string;
  language?: string;
  country?: string;
  topics?: string[];
  entities?: string[];
  data_origin?: string;
  word_count: number;
  char_count: number;
  created_at: string;
  latest_detection?: {
    classification: string;
    confidence: number;
    ai_probability: number;
  };
}

export interface DataSourceStatus {
  source_name: string;
  source_type: string;
  is_enabled: boolean;
  status: 'CONNECTED' | 'POLLING' | 'ERROR' | 'DISABLED' | 'OPTIONAL_DISABLED';
  last_sync_at: string | null;
  total_ingested: number;
  duplicates_skipped: number;
  last_error: string;
}

export interface LiveContentItem {
  id: string;
  title: string;
  raw_text: string;
  clean_text: string;
  url?: string;
  source_name?: string;
  source_type?: string;
  author?: string;
  published_at?: string;
  ingested_at: string;
  language?: string;
  country?: string;
  topics: string[];
  entities: string[];
  data_origin: 'REAL_WORLD' | 'SYNTHETIC' | 'SIMULATED';
  classification: 'HUMAN' | 'AI_GENERATED' | 'UNANALYZED';
  confidence: number;
  ai_probability: number;
  indicators: string[];
  risk_score: number;
  word_count: number;
}

export interface ProvenanceNode {
  id: string;
  label: string;
  type: 'CONTENT' | 'POST' | 'SYNTHETIC_ACCOUNT' | 'PLATFORM';
  text?: string;
  full_text?: string;
  platform?: string;
  account?: string;
  similarity?: number;
  relationship?: string;
  created_at?: string;
  is_target?: boolean;
  classification?: string;
  bot_probability?: number;
  post_type?: string;
  likes?: number;
  reshares?: number;
}

export interface ProvenanceEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  similarity?: number;
  relationship_type?: string;
}

export interface ProvenanceGraphResponse {
  target_content_id: string;
  root_origin?: {
    id: string;
    created_at?: string;
    text_preview?: string;
  };
  total_nodes: number;
  total_edges: number;
  nodes: ProvenanceNode[];
  edges: ProvenanceEdge[];
  is_acyclic: boolean;
}

export interface PropagationMetricsResponse {
  content_id?: string;
  campaign_id?: string;
  total_nodes: number;
  total_edges: number;
  propagation_velocity_per_hour: number;
  estimated_reach: number;
  reshare_depth: number;
  branching_factor: number;
  avg_degree: number;
  max_degree: number;
  clustering_coefficient: number;
  top_hub_centrality: number;
  total_platforms: number;
  total_accounts: number;
  coordinated_indicators: string[];
  gnn_analysis?: {
    gnn_risk_score: number;
    total_nodes_evaluated: number;
    high_risk_nodes_count: number;
    suspicious_node_indices: number[];
    operational_status: string;
    model_version: string;
  };
  graph_nodes: any[];
  graph_edges: any[];
}

export interface CampaignItem {
  id: string;
  name: string;
  objective: string;
  target_narrative: string;
  status: 'ACTIVE' | 'CONTAINED' | 'ARCHIVED';
  risk_score: number;
  gnn_risk_score: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  explainability_reasons: string[];
  total_events: number;
  total_reach: number;
  total_platforms: number;
  velocity_events_per_hour: number;
  branching_factor: number;
  created_at: string;
  posts?: any[];
  platforms?: any[];
  accounts?: any[];
  graph_metrics?: any;
}

export interface SimulationEventPayload {
  event_id: string;
  simulation_id: string;
  campaign_id: string;
  event_type: 'POST' | 'RESHARE' | 'REPLY' | 'QUOTE' | 'CROSS_PLATFORM_SHARE' | 'CONTENT_VARIANT';
  source_post_id?: string;
  target_post_id?: string;
  account_id: string;
  account_handle: string;
  bot_probability: number;
  platform_id: string;
  platform_name: string;
  content_id: string;
  content_snippet: string;
  timestamp: string;
  velocity: number;
  total_reach: number;
  risk_score: number;
}

export interface ModelMetadataItem {
  id: string;
  name: string;
  version: string;
  model_type: string;
  operational_status: 'TRAINED' | 'PRETRAINED' | 'DEMONSTRATION' | 'HEURISTIC_FALLBACK';
  methodology: string;
  metrics: Record<string, any>;
  dataset_info: string;
  limitations: string;
}

export interface DashboardStats {
  total_analyzed_content: number;
  human_content_count: number;
  ai_content_count: number;
  suspicious_content_count: number;
  active_campaigns_count: number;
  high_risk_campaigns_count: number;
  active_simulations_count: number;
  platforms_count: number;
  recent_alerts: {
    id: string;
    campaign_id: string;
    campaign_name: string;
    severity: string;
    risk_score: number;
    message: string;
    timestamp: string;
  }[];
  risk_distribution: Record<string, number>;
  platform_breakdown: {
    name: string;
    type: string;
    posts_count: number;
    accounts_count: number;
  }[];
  recent_analyses: {
    id: string;
    text_snippet: string;
    domain: string;
    classification: string;
    ai_probability: number;
    confidence: number;
    created_at: string;
  }[];
}
