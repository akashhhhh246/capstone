import axios from 'axios';
import {
  DetectionResultResponse,
  ContentItem,
  ProvenanceGraphResponse,
  PropagationMetricsResponse,
  CampaignItem,
  ModelMetadataItem,
  DashboardStats,
  DataSourceStatus,
  LiveContentItem,
} from '../types';

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 25000,
});

export const api = {
  // Detection
  analyzeContent: async (text: string, domain = 'general', registerContent = false): Promise<DetectionResultResponse> => {
    const res = await apiClient.post<DetectionResultResponse>('/detection/analyze', {
      text,
      domain,
      register_content: registerContent,
    });
    return res.data;
  },

  // Content
  registerContent: async (text: string, domain = 'general', sourceLabel = 'analyst_submission'): Promise<ContentItem> => {
    const res = await apiClient.post<ContentItem>('/content', {
      text,
      domain,
      source_label: sourceLabel,
    });
    return res.data;
  },

  getContentById: async (id: string): Promise<ContentItem> => {
    const res = await apiClient.get<ContentItem>(`/content/${id}`);
    return res.data;
  },

  listContents: async (limit = 25): Promise<ContentItem[]> => {
    const res = await apiClient.get<ContentItem[]>(`/content?limit=${limit}`);
    return res.data;
  },

  // Public Data Ingestion & Live Sources
  getDataSourcesStatus: async (): Promise<{ status: string; sources: DataSourceStatus[] }> => {
    const res = await apiClient.get<{ status: string; sources: DataSourceStatus[] }>('/data-sources/status');
    return res.data;
  },

  syncGDELT: async (limit = 25, query?: string): Promise<any> => {
    const res = await apiClient.post('/data-sources/gdelt/sync', { limit, query });
    return res.data;
  },

  syncRSS: async (limit = 25, query?: string): Promise<any> => {
    const res = await apiClient.post('/data-sources/rss/sync', { limit, query });
    return res.data;
  },

  listLiveContent: async (limit = 50, dataOrigin = 'REAL_WORLD', sourceType?: string): Promise<{ total: number; items: LiveContentItem[] }> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (dataOrigin) params.append('data_origin', dataOrigin);
    if (sourceType) params.append('source_type', sourceType);
    const res = await apiClient.get<{ total: number; items: LiveContentItem[] }>(`/live-content?${params.toString()}`);
    return res.data;
  },

  getLiveContentItem: async (id: string): Promise<any> => {
    const res = await apiClient.get(`/live-content/${id}`);
    return res.data;
  },

  seedSyntheticSimulation: async (contentId: string, campaignName?: string): Promise<any> => {
    const res = await apiClient.post(`/live-content/${contentId}/simulate-cascade`, {
      campaign_name: campaignName,
    });
    return res.data;
  },

  // Provenance
  getProvenanceGraph: async (contentId: string): Promise<ProvenanceGraphResponse> => {
    const res = await apiClient.get<ProvenanceGraphResponse>(`/provenance/${contentId}`);
    return res.data;
  },

  // Propagation
  getPropagationMetrics: async (contentId: string): Promise<PropagationMetricsResponse> => {
    const res = await apiClient.get<PropagationMetricsResponse>(`/propagation/${contentId}`);
    return res.data;
  },

  // Campaigns
  listCampaigns: async (): Promise<CampaignItem[]> => {
    const res = await apiClient.get<CampaignItem[]>('/campaigns');
    return res.data;
  },

  getCampaignDetail: async (id: string): Promise<CampaignItem> => {
    const res = await apiClient.get<CampaignItem>(`/campaigns/${id}`);
    return res.data;
  },

  getCampaignReport: async (id: string): Promise<any> => {
    const res = await apiClient.get(`/campaigns/${id}/report`);
    return res.data;
  },

  discoverCampaigns: async (): Promise<any> => {
    const res = await apiClient.post('/campaigns/discover');
    return res.data;
  },

  // Simulation
  startSimulation: async (campaignId: string, eventRate = 1.5, durationSeconds = 120): Promise<any> => {
    const res = await apiClient.post('/simulation/start', {
      campaign_id: campaignId,
      event_rate_per_sec: eventRate,
      duration_seconds: durationSeconds,
    });
    return res.data;
  },

  pauseSimulation: async (simulationId: string): Promise<any> => {
    const res = await apiClient.post(`/simulation/${simulationId}/pause`);
    return res.data;
  },

  stopSimulation: async (simulationId: string): Promise<any> => {
    const res = await apiClient.post(`/simulation/${simulationId}/stop`);
    return res.data;
  },

  getActiveSimulation: async (): Promise<any> => {
    const res = await apiClient.get('/simulation/active');
    return res.data;
  },

  stopAllSimulations: async (): Promise<any> => {
    const res = await apiClient.post('/simulation/stop');
    return res.data;
  },

  getSimulationStatus: async (simulationId: string): Promise<any> => {
    const res = await apiClient.get(`/simulation/${simulationId}`);
    return res.data;
  },

  // Models Governance
  listModels: async (): Promise<ModelMetadataItem[]> => {
    const res = await apiClient.get<ModelMetadataItem[]>('/models');
    return res.data;
  },

  // Dashboard Stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get<DashboardStats>('/dashboard/stats');
    return res.data;
  },
};
