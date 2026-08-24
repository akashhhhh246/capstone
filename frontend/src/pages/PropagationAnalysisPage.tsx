import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Chip,
  Tabs,
  Tab,
  Button,
  ButtonGroup,
  Divider,
} from '@mui/material';
import {
  Zap,
  Users,
  GitFork,
  Layers,
  ArrowRight,
  ShieldAlert,
  Bot,
  Radio,
  Clock,
  Compass,
  Network,
} from 'lucide-react';
import { api } from '../services/api';
import { CampaignItem, PropagationMetricsResponse } from '../types';
import { PropagationGraph } from '../components/PropagationGraph';
import { MetricCard } from '../components/MetricCard';

export const PropagationAnalysisPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>('');
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignItem | null>(null);
  const [metrics, setMetrics] = useState<PropagationMetricsResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<number>(0);
  const [filterPlatform, setFilterPlatform] = useState<string>('ALL');

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const list = await api.listCampaigns();
        setCampaigns(list);
        if (list.length > 0) {
          setSelectedCampaignId(list[0].id);
        }
      } catch (e) {
        console.error('Failed to load campaigns:', e);
      }
    };
    fetchCampaigns();
  }, []);

  useEffect(() => {
    if (!selectedCampaignId) return;
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const camp = await api.getCampaignDetail(selectedCampaignId);
        setSelectedCampaign(camp);
        if (camp.graph_metrics) {
          setMetrics(camp.graph_metrics);
        }
        setSelectedNode(null);
      } catch (e) {
        console.error('Failed to load propagation metrics:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, [selectedCampaignId]);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Information Propagation & Diffusion Analysis
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            Track how stories spread across platforms, measure velocity, and identify coordinated bot amplification.
          </Typography>
        </Box>

        <Box sx={{ minWidth: 260 }}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ color: '#9CA3AF' }}>Select Threat Campaign</InputLabel>
            <Select
              value={selectedCampaignId}
              label="Select Threat Campaign"
              onChange={(e) => setSelectedCampaignId(e.target.value)}
              sx={{
                backgroundColor: '#111827',
                color: '#FFF',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.1)' },
              }}
            >
              {campaigns.map((c) => (
                <MenuItem key={c.id} value={c.id}>
                  {c.name} ({c.severity})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Simple Executive Overview Box (Plain English) */}
      <Paper
        sx={{
          p: 2.5,
          mb: 3,
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: 2.5,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <Compass size={20} color="#60A5FA" />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
            What is happening in this campaign?
          </Typography>
          <Chip
            size="small"
            label={selectedCampaign?.severity || 'HIGH THREAT'}
            sx={{
              bgcolor: selectedCampaign?.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
              color: selectedCampaign?.severity === 'CRITICAL' ? '#F87171' : '#FBBF24',
              fontWeight: 800,
              fontSize: '0.7rem',
            }}
          />
        </Box>
        <Typography variant="body2" sx={{ color: '#D1D5DB', lineHeight: 1.6 }}>
          {selectedCampaign?.target_narrative
            ? `Narrative: "${selectedCampaign.target_narrative}". This story was published on ${metrics?.total_platforms || 4} platforms by automated bot accounts and rapidly reshared, multiplying in reach over a short time window.`
            : 'Select a campaign above to explore its step-by-step propagation pathway.'}
        </Typography>
      </Paper>

      {/* Simplified, Clear Metric Cards */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Spread Velocity"
            value={`${metrics?.propagation_velocity_per_hour || 0} posts/hr`}
            subtitle="How fast posts are published"
            icon={<Zap size={22} />}
            color="#3B82F6"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Estimated Audience"
            value={(metrics?.estimated_reach || 0).toLocaleString()}
            subtitle="Simulated people exposed"
            icon={<Users size={22} />}
            color="#10B981"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Multiplication Rate"
            value={`${metrics?.branching_factor || 1.0}x`}
            subtitle="Average reshares per post"
            icon={<GitFork size={22} />}
            color="#F59E0B"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Platforms Involved"
            value={metrics?.total_platforms || 1}
            subtitle="Distinct channels detected"
            icon={<Layers size={22} />}
            color="#06B6D4"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* View Switcher: Step-by-Step Flow vs Network Graph */}
      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.08)', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, val) => setActiveTab(val)}
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab
            label="1. Step-by-Step Propagation Flow (Easy to Read)"
            icon={<Compass size={18} />}
            iconPosition="start"
            sx={{ fontWeight: 700, textTransform: 'none', color: '#D1D5DB' }}
          />
          <Tab
            label="2. Interactive Network Graph Explorer"
            icon={<Network size={18} />}
            iconPosition="start"
            sx={{ fontWeight: 700, textTransform: 'none', color: '#D1D5DB' }}
          />
        </Tabs>
      </Box>

      {/* TAB 1: Step-by-Step Sequential Propagation Flow */}
      {activeTab === 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {selectedCampaign?.posts && selectedCampaign.posts.length > 0 ? (
            selectedCampaign.posts.map((post, idx) => (
              <Paper
                key={post.id}
                sx={{
                  p: 2.5,
                  backgroundColor: '#111827',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 2.5,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2.5,
                  transition: 'transform 0.15s ease',
                  '&:hover': {
                    borderColor: '#3B82F6',
                    transform: 'translateX(4px)',
                  },
                }}
              >
                {/* Step Number Badge */}
                <Box
                  sx={{
                    width: 44,
                    height: 44,
                    borderRadius: '12px',
                    backgroundColor: idx === 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                    border: `1.5px solid ${idx === 0 ? '#EF4444' : '#3B82F6'}`,
                    color: idx === 0 ? '#F87171' : '#60A5FA',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                    fontSize: '1.1rem',
                    flexShrink: 0,
                  }}
                >
                  {idx + 1}
                </Box>

                {/* Content Details */}
                <Box sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5, flexWrap: 'wrap' }}>
                    <Chip
                      size="small"
                      label={post.platform}
                      sx={{ bgcolor: '#1E293B', color: '#60A5FA', fontWeight: 700 }}
                    />
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                      {post.account}
                    </Typography>
                    <Chip
                      size="small"
                      label={post.post_type}
                      sx={{
                        fontSize: '0.65rem',
                        height: 18,
                        bgcolor: idx === 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(139, 92, 246, 0.15)',
                        color: idx === 0 ? '#F87171' : '#DDD6FE',
                        fontWeight: 700,
                      }}
                    />
                    {post.published_at && (
                      <Typography variant="caption" sx={{ color: '#6B7280', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Clock size={12} /> {new Date(post.published_at).toLocaleTimeString()}
                      </Typography>
                    )}
                  </Box>

                  <Typography variant="body2" sx={{ color: '#D1D5DB', mb: 1 }}>
                    "{post.content_snippet}"
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                      ❤️ <strong>{post.likes}</strong> likes
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                      🔁 <strong>{post.reshares}</strong> reshares
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            ))
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: '#6B7280' }}>
                No dissemination posts found for this campaign.
              </Typography>
            </Paper>
          )}
        </Box>
      )}

      {/* TAB 2: Filterable Network Topology Graph */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={selectedNode ? 8 : 12}>
            <Paper sx={{ p: 2.5 }}>
              {/* Platform Filter Buttons */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 600 }}>
                    Filter Platform:
                  </Typography>
                  <ButtonGroup size="small" variant="outlined">
                    {['ALL', 'SimuTwitter', 'SimuTelegram', 'SimuReddit', 'SimuNewsWire'].map((plat) => (
                      <Button
                        key={plat}
                        onClick={() => setFilterPlatform(plat)}
                        variant={filterPlatform === plat ? 'contained' : 'outlined'}
                        sx={{ fontSize: '0.75rem' }}
                      >
                        {plat}
                      </Button>
                    ))}
                  </ButtonGroup>
                </Box>
                <Typography variant="caption" sx={{ color: '#6B7280' }}>
                  Lanes: Campaign ──► Platforms ──► Accounts ──► Posts
                </Typography>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 560 }}>
                  <CircularProgress />
                </Box>
              ) : metrics && metrics.graph_nodes.length > 0 ? (
                <PropagationGraph
                  nodes={metrics.graph_nodes}
                  edges={metrics.graph_edges}
                  filterPlatform={filterPlatform}
                  onSelectNode={(node) => setSelectedNode(node)}
                />
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 560 }}>
                  <Typography variant="body2" sx={{ color: '#6B7280' }}>
                    No network propagation events recorded.
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Node Inspector Drawer */}
          {selectedNode && (
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#60A5FA', mb: 2 }}>
                  Selected Node Inspector
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Node Name / Handle:</Typography>
                  <Typography variant="h6" sx={{ color: '#F3F4F6', fontWeight: 700 }}>
                    {selectedNode.name || selectedNode.handle || selectedNode.label || selectedNode.id}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Type:</Typography>
                  <Chip size="small" label={selectedNode.type} sx={{ ml: 1, fontWeight: 700 }} />
                </Box>

                {selectedNode.bot_probability !== undefined && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Bot Probability:</Typography>
                    <Typography variant="h6" sx={{ color: selectedNode.bot_probability > 0.6 ? '#F87171' : '#34D399', fontFamily: 'monospace' }}>
                      {(selectedNode.bot_probability * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                )}

                {selectedNode.published_at && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Published At:</Typography>
                    <Typography variant="body2" sx={{ color: '#E5E7EB' }}>
                      {selectedNode.published_at}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* Coordinated Inauthentic Behavior (CIB) simplified explanation box */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1.5 }}>
          Why is this propagation pattern flagged as coordinated or high-risk?
        </Typography>

        <Grid container spacing={2}>
          {metrics?.coordinated_indicators && metrics.coordinated_indicators.length > 0 ? (
            metrics.coordinated_indicators.map((ind, i) => (
              <Grid item xs={12} md={6} key={i}>
                <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.25)', height: '100%' }}>
                  <Typography variant="body2" sx={{ color: '#FCA5A5', fontWeight: 600 }}>
                    ⚠️ {ind}
                  </Typography>
                </Box>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
                No suspicious coordination indicators identified for this network.
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  );
};
