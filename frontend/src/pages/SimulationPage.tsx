import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Play,
  Pause,
  Square,
  Radio,
  Zap,
  Users,
  Activity,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import { wsService } from '../services/websocket';
import { CampaignItem, SimulationEventPayload } from '../types';
import { LiveEventStream } from '../components/LiveEventStream';
import { MetricCard } from '../components/MetricCard';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const SimulationPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>('');
  const [eventRate, setEventRate] = useState<number>(1.5);
  const [duration, setDuration] = useState<number>(120);

  const [activeSimId, setActiveSimId] = useState<string | null>(null);
  const [simStatus, setSimStatus] = useState<'STOPPED' | 'RUNNING' | 'PAUSED'>('STOPPED');
  const [liveEvents, setLiveEvents] = useState<SimulationEventPayload[]>([]);
  const [currentVelocity, setCurrentVelocity] = useState<number>(0);
  const [currentReach, setCurrentReach] = useState<number>(0);
  const [currentRisk, setCurrentRisk] = useState<number>(0.75);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchCampaignsAndActiveSim = async () => {
      try {
        const [list, active] = await Promise.all([
          api.listCampaigns(),
          api.getActiveSimulation().catch(() => null),
        ]);
        setCampaigns(list);

        if (active && (active.status === 'RUNNING' || active.status === 'PAUSED')) {
          setActiveSimId(active.id);
          setSimStatus(active.status);
          setSelectedCampaignId(active.campaign_id);
          wsService.connect(active.id);
        } else if (list.length > 0) {
          setSelectedCampaignId(list[0].id);
        }
      } catch (e) {
        console.error('Failed to initialize simulation page:', e);
      }
    };
    fetchCampaignsAndActiveSim();

    // Subscribe to WebSocket live events
    const unsubEvents = wsService.subscribe((event) => {
      setLiveEvents((prev) => [event, ...prev.slice(0, 99)]);
      setCurrentVelocity(event.velocity);
      setCurrentReach(event.total_reach);
      setCurrentRisk(event.risk_score);

      // Auto-detect running simulation if events are arriving
      setSimStatus((prev) => (prev === 'PAUSED' ? 'PAUSED' : 'RUNNING'));
      if (event.simulation_id) {
        setActiveSimId((prev) => prev || event.simulation_id);
      }
    });

    // Subscribe to simulation lifecycle control signals
    const unsubControl = wsService.onControl((type) => {
      if (type === 'SIMULATION_STOPPED' || type === 'SIMULATION_COMPLETED') {
        setSimStatus('STOPPED');
        setActiveSimId(null);
        setCurrentVelocity(0);
      } else if (type === 'SIMULATION_PAUSED') {
        setSimStatus('PAUSED');
      }
    });

    return () => {
      unsubEvents();
      unsubControl();
    };
  }, []);

  const handleStart = async () => {
    if (!selectedCampaignId) return;
    setActionLoading(true);
    try {
      const res = await api.startSimulation(selectedCampaignId, eventRate, duration);
      setActiveSimId(res.id);
      setSimStatus('RUNNING');
      wsService.connect(res.id);
    } catch (e) {
      console.error('Failed to start simulation:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePause = async () => {
    setActionLoading(true);
    try {
      if (activeSimId) {
        await api.pauseSimulation(activeSimId);
      }
      setSimStatus('PAUSED');
    } catch (e) {
      console.error('Failed to pause simulation:', e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    setActionLoading(true);
    try {
      if (activeSimId) {
        await api.stopSimulation(activeSimId);
      }
      // Guarantee all active simulation loops are stopped on server
      await api.stopAllSimulations();
    } catch (e) {
      console.error('Failed to stop simulation:', e);
      try {
        await api.stopAllSimulations();
      } catch {}
    } finally {
      setSimStatus('STOPPED');
      setActiveSimId(null);
      setCurrentVelocity(0);
      setActionLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Real-Time Propagation Simulator & WebSocket Telemetry
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            Live Asynchronous Multi-Platform Social Media Cascades (POST, RESHARE, REPLY, QUOTE, CROSS-PLATFORM)
          </Typography>
        </Box>

        <Chip
          icon={<Radio size={14} color={simStatus === 'RUNNING' ? '#10B981' : '#9CA3AF'} />}
          label={`SIMULATOR: ${simStatus}`}
          sx={{
            bgcolor: simStatus === 'RUNNING' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(156, 163, 175, 0.15)',
            color: simStatus === 'RUNNING' ? '#34D399' : '#9CA3AF',
            fontWeight: 800,
            border: `1px solid ${simStatus === 'RUNNING' ? '#10B981' : '#4B5563'}`,
          }}
        />
      </Box>

      {/* Safety Notice */}
      <DisclaimerAlert type="privacy" />

      {/* Control Console */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
          Simulation Parameters & Mission Deck
        </Typography>

        <Grid container spacing={3} alignItems="center">
          {/* Target Campaign Selector */}
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#9CA3AF' }}>Scenario Campaign</InputLabel>
              <Select
                value={selectedCampaignId}
                label="Scenario Campaign"
                disabled={simStatus === 'RUNNING'}
                onChange={(e) => setSelectedCampaignId(e.target.value)}
                sx={{
                  backgroundColor: '#090D16',
                  color: '#FFF',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.1)' },
                }}
              >
                {campaigns.map((c) => (
                  <MenuItem key={c.id} value={c.id}>
                    {c.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Event Rate Slider */}
          <Grid item xs={12} md={4}>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              Event Generation Rate: <strong>{eventRate} events/sec</strong>
            </Typography>
            <Slider
              value={eventRate}
              min={0.5}
              max={5.0}
              step={0.5}
              disabled={simStatus === 'RUNNING'}
              onChange={(_, val) => setEventRate(val as number)}
              sx={{ color: '#3B82F6' }}
            />
          </Grid>

          {/* Execution Controls */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', gap: 1.5, justifyContent: { md: 'flex-end', xs: 'flex-start' } }}>
              {simStatus !== 'RUNNING' ? (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<Play size={16} />}
                  onClick={handleStart}
                  sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                >
                  Start Simulation
                </Button>
              ) : (
                <Button
                  variant="outlined"
                  color="warning"
                  startIcon={<Pause size={16} />}
                  onClick={handlePause}
                >
                  Pause
                </Button>
              )}

              <Button
                variant="outlined"
                color="error"
                startIcon={<Square size={16} />}
                disabled={actionLoading}
                onClick={handleStop}
                sx={{
                  borderColor: '#EF4444',
                  color: '#EF4444',
                  fontWeight: 700,
                  '&:hover': { bgcolor: 'rgba(239, 68, 68, 0.15)', borderColor: '#DC2626' },
                }}
              >
                {actionLoading ? 'Halting...' : 'Stop Simulation'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Real-Time Telemetry KPI Row */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Live Velocity"
            value={`${currentVelocity} ev/hr`}
            subtitle="Real-Time Emission Cadence"
            icon={<Zap size={22} />}
            color="#3B82F6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Estimated Audience"
            value={currentReach.toLocaleString()}
            subtitle="Dynamic Exposure Gauge"
            icon={<Users size={22} />}
            color="#10B981"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Events Streamed"
            value={liveEvents.length}
            subtitle="WebSocket Event Counter"
            icon={<Activity size={22} />}
            color="#8B5CF6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Real-Time Threat Score"
            value={`${(currentRisk * 100).toFixed(0)}%`}
            subtitle="Live Composite Risk"
            icon={<Layers size={22} />}
            color={currentRisk > 0.7 ? '#EF4444' : '#F59E0B'}
          />
        </Grid>
      </Grid>

      {/* Live Event Stream Console */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
              Live Telemetry Event Log
            </Typography>
            <Chip
              size="small"
              label={`${liveEvents.length} Captured`}
              sx={{ bgcolor: 'rgba(59, 130, 246, 0.15)', color: '#60A5FA', fontWeight: 700 }}
            />
          </Box>
          <Button
            size="small"
            onClick={() => {
              setLiveEvents([]);
              if (simStatus === 'STOPPED') {
                setCurrentVelocity(0);
              }
            }}
            sx={{ color: '#9CA3AF' }}
          >
            Clear Log
          </Button>
        </Box>

        <LiveEventStream events={liveEvents} />
      </Paper>
    </Box>
  );
};
