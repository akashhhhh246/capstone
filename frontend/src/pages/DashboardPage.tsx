import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Shield,
  FileSearch,
  Bot,
  UserCheck,
  AlertTriangle,
  Flame,
  Activity,
  Layers,
  ArrowRight,
  RefreshCw,
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

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Threat Intelligence & Information Integrity Dashboard
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            Multi-Platform LLM Disinformation Tracking & Content Provenance Operations
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshCw size={16} />}
            onClick={fetchStats}
            sx={{ borderColor: 'rgba(255, 255, 255, 0.15)', color: '#D1D5DB' }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<FileSearch size={16} />}
            onClick={() => navigate('/analysis')}
          >
            Analyze Text
          </Button>
        </Box>
      </Box>

      {/* Safety Notice */}
      <DisclaimerAlert type="privacy" />

      {/* Metric Cards KPI Grid */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Analyzed Content"
            value={stats?.total_analyzed_content || 0}
            subtitle="Benchmark & Live Submissions"
            icon={<FileSearch size={22} />}
            color="#3B82F6"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="AI-Generated Content"
            value={stats?.ai_content_count || 0}
            subtitle={`${stats ? Math.round((stats.ai_content_count / Math.max(1, stats.total_analyzed_content)) * 100) : 0}% of Corpus`}
            icon={<Bot size={22} />}
            color="#EF4444"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Campaigns"
            value={stats?.active_campaigns_count || 0}
            subtitle={`${stats?.high_risk_campaigns_count || 0} High-Risk Threat Operations`}
            icon={<Flame size={22} />}
            color="#F59E0B"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Platforms Tracked"
            value={stats?.platforms_count || 4}
            subtitle="Simulated Multi-Platform Mesh"
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
          <Paper sx={{ p: 3, height: 340 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
              Corpus Classification (AI vs Human)
            </Typography>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={aiHumanData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                >
                  {aiHumanData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', color: '#FFF' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Campaign Risk Distribution */}
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: 340 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
              Campaign Threat Severity Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={riskData}>
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', color: '#FFF' }}
                />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]}>
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
          <Paper sx={{ p: 3, minHeight: 340 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
                Active Threat Alerts
              </Typography>
              <Button size="small" endIcon={<ArrowRight size={14} />} onClick={() => navigate('/campaigns')}>
                View All Campaigns
              </Button>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {stats?.recent_alerts.map((alert) => (
                <Box
                  key={alert.id}
                  sx={{
                    p: 1.8,
                    borderRadius: 2,
                    backgroundColor: '#0F172A',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderLeft: `4px solid ${alert.severity === 'CRITICAL' ? '#EF4444' : '#F59E0B'}`,
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                      {alert.campaign_name}
                    </Typography>
                    <Chip
                      size="small"
                      label={`${alert.severity} (${alert.risk_score})`}
                      sx={{
                        bgcolor: alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                        color: alert.severity === 'CRITICAL' ? '#F87171' : '#FBBF24',
                        fontWeight: 700,
                        fontSize: '0.7rem',
                      }}
                    />
                  </Box>
                  <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                    {alert.message}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Analyzed Content */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 340 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
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
                    <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Snippet</TableCell>
                    <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Verdict</TableCell>
                    <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>AI Prob</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stats?.recent_analyses.map((item) => (
                    <TableRow key={item.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/provenance?contentId=${item.id}`)}>
                      <TableCell sx={{ color: '#E5E7EB', maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {item.text_snippet}
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={item.classification}
                          sx={{
                            bgcolor: item.classification === 'AI_GENERATED' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                            color: item.classification === 'AI_GENERATED' ? '#F87171' : '#34D399',
                            fontWeight: 700,
                            fontSize: '0.68rem',
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: '#9CA3AF', fontFamily: 'monospace' }}>
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
