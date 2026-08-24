import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from '@mui/material';
import {
  ShieldAlert,
  Flame,
  Layers,
  Activity,
  CheckCircle,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { api } from '../services/api';
import { CampaignItem } from '../types';
import { RiskScoreBadge } from '../components/RiskScoreBadge';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const CampaignAnalysisPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        setLoading(true);
        const list = await api.listCampaigns();
        setCampaigns(list);
        if (list.length > 0) {
          loadCampaignDetail(list[0].id);
        }
      } catch (e) {
        console.error('Failed to load campaigns:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchCampaigns();
  }, []);

  const loadCampaignDetail = async (id: string) => {
    try {
      setDetailLoading(true);
      const detail = await api.getCampaignDetail(id);
      setSelectedCampaign(detail);
    } catch (e) {
      console.error('Failed to load campaign detail:', e);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
          Threat Campaign Intelligence & Explainable Risk Scoring
        </Typography>
        <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
          Comprehensive Multi-Factor Risk Assessment with Itemized Explanations and Disinformation Narrative Tracking
        </Typography>
      </Box>

      {/* Safety Alert */}
      <DisclaimerAlert type="privacy" />

      <Grid container spacing={3}>
        {/* Campaign Master List */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, minHeight: 600 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
              Tracked Malign Campaigns ({campaigns.length})
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {campaigns.map((c) => {
                const isSelected = selectedCampaign?.id === c.id;
                return (
                  <Box
                    key={c.id}
                    onClick={() => loadCampaignDetail(c.id)}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.15)' : '#0F172A',
                      border: isSelected ? '1.5px solid #3B82F6' : '1px solid rgba(255, 255, 255, 0.06)',
                      transition: 'all 0.15s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                        {c.name}
                      </Typography>
                      <RiskScoreBadge score={c.risk_score} severity={c.severity} />
                    </Box>
                    <Typography variant="caption" sx={{ color: '#9CA3AF', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', mb: 1 }}>
                      {c.objective}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip
                        size="small"
                        label={c.status}
                        sx={{
                          height: 18,
                          fontSize: '0.65rem',
                          fontWeight: 700,
                          bgcolor: c.status === 'ACTIVE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                          color: c.status === 'ACTIVE' ? '#F87171' : '#34D399',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#6B7280' }}>
                        {c.total_platforms} Platforms • {c.total_events} Events
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Paper>
        </Grid>

        {/* Selected Campaign In-Depth Inspector */}
        <Grid item xs={12} md={8}>
          {detailLoading ? (
            <Paper sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 600 }}>
              <CircularProgress />
            </Paper>
          ) : selectedCampaign ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Header Card */}
              <Paper sx={{ p: 3, borderLeft: `6px solid ${selectedCampaign.severity === 'CRITICAL' ? '#EF4444' : (selectedCampaign.severity === 'HIGH' ? '#F59E0B' : '#3B82F6')}` }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                      {selectedCampaign.name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#9CA3AF', mt: 0.5 }}>
                      Objective: <strong>{selectedCampaign.objective}</strong>
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <RiskScoreBadge score={selectedCampaign.risk_score} severity={selectedCampaign.severity} />
                    <Typography variant="caption" sx={{ color: '#6B7280', display: 'block', mt: 0.5 }}>
                      GNN Anomaly: {(selectedCampaign.gnn_risk_score * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                </Box>

                <Paper sx={{ p: 2, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 2 }}>
                  <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 700, textTransform: 'uppercase' }}>
                    Core Target Narrative:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E5E7EB', fontStyle: 'italic', mt: 0.5 }}>
                    "{selectedCampaign.target_narrative}"
                  </Typography>
                </Paper>
              </Paper>

              {/* Explainable Risk Reasoning Breakdown */}
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1.5 }}>
                  Explainable Risk Attribution & Reasons
                </Typography>
                <Typography variant="body2" sx={{ color: '#9CA3AF', mb: 2 }}>
                  Explicit factors contributing to the computed threat score ({selectedCampaign.risk_score.toFixed(2)}):
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {selectedCampaign.explainability_reasons.map((reason, idx) => (
                    <Box
                      key={idx}
                      sx={{
                        p: 1.5,
                        borderRadius: 1.5,
                        backgroundColor: '#0F172A',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                      }}
                    >
                      <AlertCircle size={18} color="#F59E0B" />
                      <Typography variant="body2" sx={{ color: '#F3F4F6' }}>
                        {reason}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Paper>

              {/* Linked Multi-Platform Posts Table */}
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
                  Dissemination Posts & Platform Lineage
                </Typography>

                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Platform</TableCell>
                        <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Author Account</TableCell>
                        <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Type</TableCell>
                        <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Content Snippet</TableCell>
                        <TableCell sx={{ color: '#9CA3AF', fontWeight: 600 }}>Engagement</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedCampaign.posts?.map((p) => (
                        <TableRow key={p.id} hover>
                          <TableCell sx={{ color: '#60A5FA', fontWeight: 600 }}>{p.platform}</TableCell>
                          <TableCell sx={{ color: '#F3F4F6' }}>{p.account}</TableCell>
                          <TableCell>
                            <Chip size="small" label={p.post_type} sx={{ fontSize: '0.68rem', height: 20 }} />
                          </TableCell>
                          <TableCell sx={{ color: '#9CA3AF', maxWidth: 220 }}>{p.content_snippet}</TableCell>
                          <TableCell sx={{ color: '#6B7280', fontSize: '0.78rem' }}>
                            ❤️ {p.likes} | 🔁 {p.reshares}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Box>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" sx={{ color: '#6B7280' }}>
                Select a campaign from the list to view detailed telemetry.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
