import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  FileSearch,
  Bot,
  Flame,
  Layers,
  ArrowRight,
  RefreshCw,
  Radio,
  Share2,
  GitBranch,
  Play,
  Zap,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { DashboardStats } from '../types';
import { MetricCard } from '../components/MetricCard';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load dashboard telemetry:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const aiHumanData = stats
    ? [
        { name: 'AI Generated', value: stats.ai_content_count, color: '#EF4444' },
        { name: 'Human Authored', value: stats.human_content_count, color: '#10B981' },
      ]
    : [];

  const riskData = stats?.risk_distribution
    ? [
        { name: 'Critical', count: stats.risk_distribution.CRITICAL || 0, color: '#EF4444' },
        { name: 'High', count: stats.risk_distribution.HIGH || 0, color: '#F59E0B' },
        { name: 'Medium', count: stats.risk_distribution.MEDIUM || 0, color: '#3B82F6' },
        { name: 'Low', count: stats.risk_distribution.LOW || 0, color: '#10B981' },
      ]
    : [];

  const totalContent = stats?.total_analyzed_content || 0;
  const humanRatio = totalContent > 0 && stats ? Math.round((stats.human_content_count / totalContent) * 100) : 0;
  const aiRatio = totalContent > 0 && stats ? Math.round((stats.ai_content_count / totalContent) * 100) : 0;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5 }}>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
              Information Integrity & Threat Defense Operations
            </Typography>
            <Chip
              icon={<Radio size={12} color="#10B981" />}
              label="MONITORING ACTIVE"
              size="small"
              sx={{ bgcolor: 'rgba(16, 185, 129, 0.15)', color: '#34D399', fontWeight: 800, border: '1px solid #10B981' }}
            />
          </Box>
          <Typography variant="body2" sx={{ color: '#94A3B8' }}>
            Unified workbench for AI content detection, provenance DAG reconstruction, and cross-platform propagation defense.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshCw size={14} />}
            onClick={fetchStats}
            sx={{ borderColor: 'rgba(255, 255, 255, 0.15)', color: '#D1D5DB' }}
          >
            Refresh Telemetry
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<Radio size={14} />}
            onClick={() => navigate('/live-data')}
            sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
          >
            Live Ingestion Feed
          </Button>
        </Box>
      </Box>

      {/* Safety Notice */}
      <DisclaimerAlert type="privacy" />

      {/* Quick Action Launchpad */}
      <Paper sx={{ p: 2.5, mb: 3, backgroundColor: '#0C1322', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 3 }}>
        <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 800, letterSpacing: '0.08em', display: 'block', mb: 1.5 }}>
          QUICK-ACTION INVESTIGATION LAUNCHPAD
        </Typography>
        <Grid container spacing={1.5}>
          <Grid item xs={12} sm={6} md={2.4}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              startIcon={<Radio size={16} color="#34D399" />}
              onClick={() => navigate('/live-data')}
              sx={{ borderColor: 'rgba(16, 185, 129, 0.3)', color: '#D1FAE5', py: 1 }}
            >
              Live Public Feed
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              startIcon={<FileSearch size={16} color="#60A5FA" />}
              onClick={() => navigate('/analysis')}
              sx={{ borderColor: 'rgba(59, 130, 246, 0.3)', color: '#DBEAFE', py: 1 }}
            >
              Content Analyzer
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              startIcon={<GitBranch size={16} color="#A78BFA" />}
              onClick={() => navigate('/provenance')}
              sx={{ borderColor: 'rgba(139, 92, 246, 0.3)', color: '#EDE9FE', py: 1 }}
            >
              Provenance DAG
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              startIcon={<Share2 size={16} color="#FBBF24" />}
              onClick={() => navigate('/propagation')}
              sx={{ borderColor: 'rgba(245, 158, 11, 0.3)', color: '#FEF3C7', py: 1 }}
            >
              Propagation Graph
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={2.4}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              startIcon={<Play size={16} color="#F87171" />}
              onClick={() => navigate('/simulation')}
              sx={{ borderColor: 'rgba(239, 68, 68, 0.3)', color: '#FEE2E2', py: 1 }}
            >
              Live Simulator
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Metric Cards KPI Grid */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Analyzed Corpus"
            value={stats?.total_analyzed_content || 0}
            subtitle="Rich Lineage Benchmark & Live News"
            icon={<FileSearch size={22} />}
            color="#3B82F6"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="AI-Generated Content"
            value={stats?.ai_content_count || 0}
            subtitle={`${aiRatio}% Synthetic Density`}
            icon={<Bot size={22} />}
            color="#EF4444"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Tracked Campaigns"
            value={stats?.active_campaigns_count || 0}
            subtitle={`${stats?.high_risk_campaigns_count || 0} Critical Disinformation Vectors`}
            icon={<Flame size={22} />}
            color="#F59E0B"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Monitored Platforms"
            value={stats?.platforms_count || 4}
            subtitle="X/Twitter, Telegram, Reddit, NewsWires"
            icon={<Layers size={22} />}
            color="#06B6D4"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Analytical Charts Row */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        {/* AI vs Human Distribution */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: 350, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)', position: 'relative' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                Corpus Classification
              </Typography>
              <Chip
                size="small"
                label={`${humanRatio}% Human / ${aiRatio}% AI`}
                sx={{ bgcolor: 'rgba(59, 130, 246, 0.15)', color: '#93C5FD', fontWeight: 800, fontSize: '0.72rem' }}
              />
            </Box>

            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={aiHumanData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={92}
                  paddingAngle={5}
                >
                  {aiHumanData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#0E1726" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#070B14',
                    border: '1px solid rgba(59, 130, 246, 0.4)',
                    borderRadius: 8,
                    padding: '8px 12px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  }}
                  itemStyle={{ color: '#F9FAFB', fontWeight: 700 }}
                  labelStyle={{ color: '#60A5FA', fontWeight: 800 }}
                />
                <Legend wrapperStyle={{ color: '#E2E8F0', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Campaign Risk Distribution */}
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: 350, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                Campaign Threat Severity Breakdown
              </Typography>
              <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 600 }}>
                {stats?.active_campaigns_count || 0} Total Active Campaigns
              </Typography>
            </Box>

            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={riskData} margin={{ top: 20, right: 20, left: 0, bottom: 5 }}>
                <XAxis dataKey="name" stroke="#94A3B8" tick={{ fill: '#CBD5E1', fontSize: 12, fontWeight: 600 }} />
                <YAxis stroke="#94A3B8" allowDecimals={false} tick={{ fill: '#CBD5E1', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#070B14',
                    border: '1px solid rgba(59, 130, 246, 0.4)',
                    borderRadius: 8,
                    padding: '8px 12px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  }}
                  itemStyle={{ color: '#F9FAFB', fontWeight: 700 }}
                  labelStyle={{ color: '#60A5FA', fontWeight: 800 }}
                />
                <Bar
                  dataKey="count"
                  radius={[8, 8, 0, 0]}
                  label={{ position: 'top', fill: '#F9FAFB', fontSize: 13, fontWeight: 800 }}
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`bar-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Row: Recent Alerts & Recent Analyses */}
      <Grid container spacing={2.5}>
        {/* High-Risk Threat Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 340, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                Active Threat Alerts
              </Typography>
              <Button size="small" endIcon={<ArrowRight size={14} />} onClick={() => navigate('/campaigns')}>
                View Dossiers
              </Button>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {stats?.recent_alerts.map((alert) => (
                <Box
                  key={alert.id}
                  sx={{
                    p: 2,
                    borderRadius: 2.5,
                    backgroundColor: '#070B14',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderLeft: `4px solid ${alert.severity === 'CRITICAL' ? '#EF4444' : (alert.severity === 'HIGH' ? '#F59E0B' : '#3B82F6')}`,
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 800, color: '#F3F4F6' }}>
                      {alert.campaign_name}
                    </Typography>
                    <Chip
                      size="small"
                      label={`${alert.severity} (${(alert.risk_score * 100).toFixed(0)}%)`}
                      sx={{
                        bgcolor: alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : (alert.severity === 'HIGH' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(59, 130, 246, 0.2)'),
                        color: alert.severity === 'CRITICAL' ? '#F87171' : (alert.severity === 'HIGH' ? '#FBBF24' : '#93C5FD'),
                        fontWeight: 800,
                        fontSize: '0.7rem',
                      }}
                    />
                  </Box>
                  <Typography variant="caption" sx={{ color: '#94A3B8' }}>
                    {alert.message}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Analyzed Content */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 340, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                Recent Content Ingestions
              </Typography>
              <Button size="small" endIcon={<ArrowRight size={14} />} onClick={() => navigate('/analysis')}>
                New Analysis
              </Button>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Snippet</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Verdict</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>AI Prob</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stats?.recent_analyses.map((item) => (
                    <TableRow
                      key={item.id}
                      hover
                      sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'rgba(255,255,255,0.04)' } }}
                      onClick={() => navigate(`/provenance?contentId=${item.id}`)}
                    >
                      <TableCell sx={{ color: '#E2E8F0', maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {item.text_snippet}
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={item.classification.replace('_', ' ')}
                          sx={{
                            bgcolor: item.classification === 'AI_GENERATED' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                            color: item.classification === 'AI_GENERATED' ? '#F87171' : '#34D399',
                            fontWeight: 800,
                            fontSize: '0.68rem',
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#94A3B8', fontFamily: 'monospace', fontWeight: 700 }}>
                        {(item.ai_probability * 100).toFixed(0)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
