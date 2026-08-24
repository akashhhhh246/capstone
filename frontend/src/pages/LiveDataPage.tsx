import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Button,
  Chip,
  CircularProgress,
  Divider,
  TextField,
  InputAdornment,
  LinearProgress,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Radio,
  RefreshCw,
  Globe,
  Rss,
  Share2,
  ExternalLink,
  ShieldCheck,
  Bot,
  UserCheck,
  Zap,
  GitBranch,
  Search,
  CheckCircle2,
  AlertTriangle,
  Play,
} from 'lucide-react';
import { api } from '../services/api';
import { wsService } from '../services/websocket';
import { DataSourceStatus, LiveContentItem } from '../types';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const LiveDataPage: React.FC = () => {
  const navigate = useNavigate();
  const [sources, setSources] = useState<DataSourceStatus[]>([]);
  const [liveItems, setLiveItems] = useState<LiveContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingGdelt, setSyncingGdelt] = useState(false);
  const [syncingRss, setSyncingRss] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('ALL');
  const [bannerAlert, setBannerAlert] = useState<string | null>(null);

  const fetchStatuses = async () => {
    try {
      const data = await api.getDataSourcesStatus();
      setSources(data.sources);
    } catch (e) {
      console.error('Failed to load source statuses:', e);
    }
  };

  const fetchContent = async () => {
    try {
      setLoading(true);
      const data = await api.listLiveContent(50, 'REAL_WORLD');
      setLiveItems(data.items);
    } catch (e) {
      console.error('Failed to load live content feed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatuses();
    fetchContent();

    // Subscribe to real-time incoming articles via WebSockets
    const unsub = wsService.subscribe((event: any) => {
      if (event.event_type === 'REAL_WORLD_CONTENT_INGESTED' && event.payload) {
        setLiveItems((prev) => [event.payload, ...prev]);
        setBannerAlert(`New Real-World Article Ingested: "${event.payload.title?.substring(0, 50)}..."`);
        fetchStatuses();
      }
    });

    return () => unsub();
  }, []);

  const handleSyncGdelt = async () => {
    try {
      setSyncingGdelt(true);
      const res = await api.syncGDELT(25);
      setBannerAlert(`GDELT Sync Completed: ${res.ingested} new articles ingested, ${res.skipped_duplicates} duplicates skipped.`);
      await fetchStatuses();
      await fetchContent();
    } catch (e: any) {
      console.error('GDELT sync error:', e);
      setBannerAlert(`GDELT Sync Notice: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSyncingGdelt(false);
    }
  };

  const handleSyncRss = async () => {
    try {
      setSyncingRss(true);
      const res = await api.syncRSS(20);
      setBannerAlert(`RSS Sync Completed: ${res.ingested} new articles ingested.`);
      await fetchStatuses();
      await fetchContent();
    } catch (e: any) {
      console.error('RSS sync error:', e);
    } finally {
      setSyncingRss(false);
    }
  };

  const handleSeedSimulation = async (item: LiveContentItem) => {
    try {
      const res = await api.seedSyntheticSimulation(item.id, `Simulated Cascade: ${item.title.substring(0, 30)}`);
      setBannerAlert(`Synthetic simulation seeded for campaign "${res.campaign_name}". Navigating to Simulation Deck...`);
      setTimeout(() => {
        navigate('/simulation');
      }, 1000);
    } catch (e: any) {
      console.error('Failed to seed simulation:', e);
    }
  };

  // Filter items by search query and topic
  const filteredItems = liveItems.filter((item) => {
    const matchesSearch =
      searchQuery === '' ||
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.raw_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.source_name && item.source_name.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesTopic =
      selectedTopic === 'ALL' ||
      item.topics.some((t) => t.toLowerCase() === selectedTopic.toLowerCase());

    return matchesSearch && matchesTopic;
  });

  const gdeltStatus = sources.find((s) => s.source_type === 'gdelt');
  const rssStatus = sources.find((s) => s.source_type === 'rss');
  const blueskyStatus = sources.find((s) => s.source_type === 'bluesky');

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Live Public Data Ingestion & Telemetry
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            Real-time public news streams from GDELT Project DOC 2.0 API and Open RSS feeds passing through the ML detection pipeline.
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
          <Chip
            icon={<Radio size={14} color="#10B981" />}
            label="TELEMETRY STREAM: ACTIVE"
            sx={{ bgcolor: 'rgba(16, 185, 129, 0.15)', color: '#34D399', fontWeight: 800, border: '1px solid #10B981' }}
          />
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshCw size={14} />}
            onClick={() => {
              fetchStatuses();
              fetchContent();
            }}
            sx={{ borderColor: 'rgba(255,255,255,0.1)', color: '#9CA3AF' }}
          >
            Refresh Feed
          </Button>
        </Box>
      </Box>

      {/* Mandatory Real vs Synthetic Safeguards Banner */}
      <DisclaimerAlert type="privacy" />

      {/* Live Action Banner Alert if new items ingested */}
      {bannerAlert && (
        <Alert
          severity="info"
          onClose={() => setBannerAlert(null)}
          sx={{ mb: 3, backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#93C5FD', border: '1px solid rgba(59, 130, 246, 0.3)' }}
        >
          {bannerAlert}
        </Alert>
      )}

      {/* Top Monitoring Panel: Data Source Status Cards */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        {/* Card 1: GDELT Project (Primary Source) */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2.5,
              height: '100%',
              backgroundColor: '#0F172A',
              border: '1.5px solid #3B82F6',
              borderRadius: 2.5,
              boxShadow: '0 0 20px rgba(59, 130, 246, 0.15)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Globe size={20} color="#60A5FA" />
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                  GDELT Project
                </Typography>
              </Box>
              <Chip
                size="small"
                label={gdeltStatus?.status || 'CONNECTED'}
                sx={{
                  bgcolor: gdeltStatus?.status === 'ERROR' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                  color: gdeltStatus?.status === 'ERROR' ? '#F87171' : '#34D399',
                  fontWeight: 800,
                  fontSize: '0.68rem',
                }}
              />
            </Box>

            <Typography variant="caption" sx={{ color: '#9CA3AF', display: 'block', mb: 1.5 }}>
              Free, publicly accessible global news intelligence API. No API key required.
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Total Ingested:</Typography>
              <Typography variant="caption" sx={{ color: '#F3F4F6', fontWeight: 700 }}>
                {gdeltStatus?.total_ingested || 0} articles
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Duplicates Filtered:</Typography>
              <Typography variant="caption" sx={{ color: '#34D399', fontWeight: 700 }}>
                {gdeltStatus?.duplicates_skipped || 0} skipped
              </Typography>
            </Box>

            <Button
              fullWidth
              size="small"
              variant="contained"
              disabled={syncingGdelt}
              startIcon={syncingGdelt ? <CircularProgress size={14} color="inherit" /> : <Zap size={14} />}
              onClick={handleSyncGdelt}
              sx={{ background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)' }}
            >
              {syncingGdelt ? 'Polling GDELT API...' : '⚡ Sync GDELT News Now'}
            </Button>
          </Paper>
        </Grid>

        {/* Card 2: Public RSS Feeds (Optional Source) */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2.5,
              height: '100%',
              backgroundColor: '#0F172A',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 2.5,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Rss size={20} color="#F59E0B" />
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                  Public RSS Feeds
                </Typography>
              </Box>
              <Chip
                size="small"
                label={rssStatus?.status || 'ENABLED'}
                sx={{ bgcolor: 'rgba(245, 158, 11, 0.2)', color: '#FBBF24', fontWeight: 800, fontSize: '0.68rem' }}
              />
            </Box>

            <Typography variant="caption" sx={{ color: '#9CA3AF', display: 'block', mb: 1.5 }}>
              Public news feeds configured via environment variables (BBC, NYT, Reuters).
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Total Ingested:</Typography>
              <Typography variant="caption" sx={{ color: '#F3F4F6', fontWeight: 700 }}>
                {rssStatus?.total_ingested || 0} articles
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Status:</Typography>
              <Typography variant="caption" sx={{ color: '#93C5FD', fontWeight: 700 }}>
                Configurable in .env
              </Typography>
            </Box>

            <Button
              fullWidth
              size="small"
              variant="outlined"
              disabled={syncingRss}
              startIcon={syncingRss ? <CircularProgress size={14} color="inherit" /> : <RefreshCw size={14} />}
              onClick={handleSyncRss}
              sx={{ borderColor: 'rgba(255,255,255,0.15)', color: '#D1D5DB' }}
            >
              {syncingRss ? 'Parsing RSS...' : 'Sync RSS Feeds'}
            </Button>
          </Paper>
        </Grid>

        {/* Card 3: Bluesky Public Stream (Optional Interface) */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2.5,
              height: '100%',
              backgroundColor: '#0F172A',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 2.5,
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Share2 size={20} color="#8B5CF6" />
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                  Bluesky Public Stream
                </Typography>
              </Box>
              <Chip
                size="small"
                label="OPTIONAL / STANDBY"
                sx={{ bgcolor: 'rgba(139, 92, 246, 0.2)', color: '#DDD6FE', fontWeight: 800, fontSize: '0.68rem' }}
              />
            </Box>

            <Typography variant="caption" sx={{ color: '#9CA3AF', display: 'block', mb: 1.5 }}>
              Modular ATProto public firehose interface. Ready for public stream activation.
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Endpoint:</Typography>
              <Typography variant="caption" sx={{ color: '#9CA3AF', fontFamily: 'monospace' }}>
                public.api.bsky.app
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Status:</Typography>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                Optional Module
              </Typography>
            </Box>

            <Button
              fullWidth
              size="small"
              variant="outlined"
              disabled
              sx={{ borderColor: 'rgba(255,255,255,0.08)', color: '#6B7280' }}
            >
              Public Stream Standby
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Filter and Search Toolbar */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 700, mr: 1 }}>
            Topics Filter:
          </Typography>
          {['ALL', 'Disinformation', 'AI', 'Generative ai', 'Cyberattack', 'Security', 'Election', 'Technology'].map((topic) => (
            <Chip
              key={topic}
              label={topic}
              clickable
              size="small"
              onClick={() => setSelectedTopic(topic)}
              sx={{
                bgcolor: selectedTopic === topic ? 'rgba(59, 130, 246, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: selectedTopic === topic ? '#93C5FD' : '#D1D5DB',
                fontWeight: selectedTopic === topic ? 800 : 500,
                border: selectedTopic === topic ? '1px solid #3B82F6' : '1px solid rgba(255,255,255,0.08)',
              }}
            />
          ))}
        </Box>

        <Box sx={{ minWidth: 260 }}>
          <TextField
            size="small"
            placeholder="Search headline, text, domain..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search size={16} color="#9CA3AF" />
                </InputAdornment>
              ),
            }}
            sx={{
              backgroundColor: '#090D16',
              '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.1)' },
            }}
          />
        </Box>
      </Paper>

      {/* Live Ingestion Feed */}
      <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Globe size={18} color="#60A5FA" />
        Live Ingested Real-World Feed ({filteredItems.length} Articles)
      </Typography>

      {loading ? (
        <Paper sx={{ p: 6, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress />
        </Paper>
      ) : filteredItems.length > 0 ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {filteredItems.map((item) => {
            const isAI = item.classification === 'AI_GENERATED';
            return (
              <Paper
                key={item.id}
                sx={{
                  p: 2.5,
                  backgroundColor: '#0F172A',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 2.5,
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    borderColor: 'rgba(59, 130, 246, 0.4)',
                    boxShadow: '0 0 16px rgba(59, 130, 246, 0.15)',
                  },
                }}
              >
                {/* Header Row */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
                    <Chip
                      size="small"
                      label="REAL-WORLD"
                      sx={{ bgcolor: 'rgba(16, 185, 129, 0.2)', color: '#34D399', fontWeight: 800, fontSize: '0.65rem' }}
                    />
                    <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 700 }}>
                      {item.source_name || 'GDELT'}
                    </Typography>
                    {item.country && item.country !== 'Unknown' && (
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                        • {item.country}
                      </Typography>
                    )}
                    <Typography variant="caption" sx={{ color: '#6B7280' }}>
                      • Ingested: {new Date(item.ingested_at).toLocaleTimeString()}
                    </Typography>
                  </Box>

                  {/* AI Detection Classification Badge */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      size="small"
                      icon={isAI ? <Bot size={14} color="#F87171" /> : <UserCheck size={14} color="#34D399" />}
                      label={`${item.classification.replace('_', ' ')} (${(item.confidence * 100).toFixed(0)}%)`}
                      sx={{
                        bgcolor: isAI ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                        color: isAI ? '#F87171' : '#34D399',
                        fontWeight: 800,
                        fontSize: '0.7rem',
                      }}
                    />
                    <Chip
                      size="small"
                      label={`Risk: ${(item.risk_score * 100).toFixed(0)}%`}
                      sx={{
                        bgcolor: item.risk_score > 0.6 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                        color: item.risk_score > 0.6 ? '#F87171' : '#FBBF24',
                        fontWeight: 800,
                        fontSize: '0.7rem',
                      }}
                    />
                  </Box>
                </Box>

                {/* Title / Headline */}
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1, fontSize: '1.05rem' }}>
                  {item.title}
                </Typography>

                {/* Snippet */}
                <Typography variant="body2" sx={{ color: '#D1D5DB', mb: 1.5, lineHeight: 1.5 }}>
                  "{item.raw_text}"
                </Typography>

                {/* Topics & Indicators */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  <Box sx={{ display: 'flex', gap: 0.8, flexWrap: 'wrap' }}>
                    {item.topics.map((t, idx) => (
                      <Chip key={idx} size="small" label={t} sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(255,255,255,0.06)' }} />
                    ))}
                    {item.indicators.map((ind, idx) => (
                      <Chip key={`ind-${idx}`} size="small" label={ind} sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(59, 130, 246, 0.15)', color: '#93C5FD' }} />
                    ))}
                  </Box>

                  {item.url && (
                    <Button
                      size="small"
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      endIcon={<ExternalLink size={12} />}
                      sx={{ color: '#60A5FA', fontSize: '0.75rem', textTransform: 'none' }}
                    >
                      View Original Article
                    </Button>
                  )}
                </Box>

                <Divider sx={{ my: 1.5, borderColor: 'rgba(255, 255, 255, 0.06)' }} />

                {/* 3 Action Buttons */}
                <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<ShieldCheck size={14} />}
                    onClick={() => navigate(`/analysis`)}
                    sx={{ color: '#93C5FD', borderColor: 'rgba(59, 130, 246, 0.3)', fontSize: '0.75rem' }}
                  >
                    Inspect in Content Analysis
                  </Button>

                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<GitBranch size={14} />}
                    onClick={() => navigate(`/provenance?contentId=${item.id}`)}
                    sx={{ color: '#C4B5FD', borderColor: 'rgba(139, 92, 246, 0.3)', fontSize: '0.75rem' }}
                  >
                    Track in Provenance DAG
                  </Button>

                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<Play size={14} />}
                    onClick={() => handleSeedSimulation(item)}
                    sx={{ color: '#34D399', borderColor: 'rgba(16, 185, 129, 0.3)', fontSize: '0.75rem' }}
                  >
                    ⚡ Seed Synthetic Simulation [SIMULATED]
                  </Button>
                </Box>
              </Paper>
            );
          })}
        </Box>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: '#6B7280' }}>
            No real-world articles match your current filter. Click "Sync GDELT News Now" above to poll recent global intelligence feeds.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};
