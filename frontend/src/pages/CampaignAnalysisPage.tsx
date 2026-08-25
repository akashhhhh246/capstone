import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Chip,
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
  Download,
} from 'lucide-react';
import { api } from '../services/api';
import { CampaignItem } from '../types';
import { RiskScoreBadge } from '../components/RiskScoreBadge';
import { DisclaimerAlert } from '../components/DisclaimerAlert';
import { exportCampaignToPdf } from '../utils/pdfExport';

export const CampaignAnalysisPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);

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

  const handleDownloadPdf = () => {
    if (!selectedCampaign) return;
    try {
      setExportingPdf(true);
      exportCampaignToPdf(selectedCampaign);
    } catch (e) {
      console.error('Failed to export PDF:', e);
    } finally {
      setTimeout(() => setExportingPdf(false), 500);
    }
  };

  const [discovering, setDiscovering] = useState(false);

  const handleScanEmergentThreats = async () => {
    try {
      setDiscovering(true);
      const res = await api.discoverCampaigns();
      const updatedList = await api.listCampaigns();
      setCampaigns(updatedList);
      if (updatedList.length > 0 && (!selectedCampaign || !updatedList.some(c => c.id === selectedCampaign.id))) {
        loadCampaignDetail(updatedList[0].id);
      }
    } catch (e) {
      console.error('Failed to run dynamic threat discovery scan:', e);
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Threat Campaign Intelligence & Explainable Risk Scoring
          </Typography>
          <Typography variant="body2" sx={{ color: '#94A3B8' }}>
            Multi-factor threat attribution, dynamic live stream clustering, and neat PDF dossier export.
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            startIcon={discovering ? <CircularProgress size={16} color="inherit" /> : <Activity size={16} color="#38BDF8" />}
            onClick={handleScanEmergentThreats}
            disabled={discovering}
            sx={{ borderColor: 'rgba(56, 189, 248, 0.4)', color: '#BAE6FD' }}
          >
            {discovering ? 'Clustering Live Feed...' : 'Scan Live Feed for Threats'}
          </Button>

          {selectedCampaign && (
            <Button
              variant="contained"
              startIcon={exportingPdf ? <CircularProgress size={16} color="inherit" /> : <Download size={16} />}
              onClick={handleDownloadPdf}
              disabled={exportingPdf}
              sx={{ background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)', fontWeight: 800 }}
            >
              Export Threat Dossier (PDF)
            </Button>
          )}
        </Box>
      </Box>

      {/* Safety Alert */}
      <DisclaimerAlert type="privacy" />

      <Grid container spacing={3}>
        {/* Campaign Master List */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2.5, minHeight: 600, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                Tracked Operations ({campaigns.length})
              </Typography>
              <Chip
                size="small"
                label="LIVE ML CLUSTERING ACTIVE"
                sx={{ bgcolor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', fontWeight: 800, fontSize: '0.62rem' }}
              />
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {campaigns.map((c) => {
                const isSelected = selectedCampaign?.id === c.id;
                const isLiveDiscovered = c.id.startsWith('camp-live');

                return (
                  <Box
                    key={c.id}
                    onClick={() => loadCampaignDetail(c.id)}
                    sx={{
                      p: 2,
                      borderRadius: 2.5,
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.15)' : '#070B14',
                      border: isSelected ? '1.5px solid #3B82F6' : '1px solid rgba(255, 255, 255, 0.06)',
                      transition: 'all 0.15s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.8 }}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#F3F4F6' }}>
                          {c.name}
                        </Typography>
                        {isLiveDiscovered && (
                          <Chip
                            size="small"
                            label="LIVE STREAM DISCOVERED"
                            sx={{ height: 16, fontSize: '0.58rem', fontWeight: 800, bgcolor: 'rgba(6, 182, 212, 0.2)', color: '#22D3EE', mt: 0.3 }}
                          />
                        )}
                      </Box>
                      <RiskScoreBadge score={c.risk_score} severity={c.severity} />
                    </Box>
                    <Typography variant="caption" sx={{ color: '#94A3B8', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', mb: 1 }}>
                      {c.objective}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip
                        size="small"
                        label={c.status}
                        sx={{
                          height: 18,
                          fontSize: '0.65rem',
                          fontWeight: 800,
                          bgcolor: c.status === 'ACTIVE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                          color: c.status === 'ACTIVE' ? '#F87171' : '#34D399',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#64748B' }}>
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
            <Paper sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 600, backgroundColor: '#0E1726' }}>
              <CircularProgress />
            </Paper>
          ) : selectedCampaign ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Header Card */}
              <Paper sx={{ p: 3, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)', borderLeft: `6px solid ${selectedCampaign.severity === 'CRITICAL' ? '#EF4444' : (selectedCampaign.severity === 'HIGH' ? '#F59E0B' : '#3B82F6')}` }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
                      {selectedCampaign.name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', mt: 0.5 }}>
                      Objective: <strong>{selectedCampaign.objective}</strong>
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <RiskScoreBadge score={selectedCampaign.risk_score} severity={selectedCampaign.severity} />
                    <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mt: 0.5 }}>
                      GNN Anomaly: {(selectedCampaign.gnn_risk_score * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                </Box>

                <Paper sx={{ p: 2, backgroundColor: '#070B14', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 2 }}>
                  <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 800, textTransform: 'uppercase' }}>
                    Core Target Narrative:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E2E8F0', fontStyle: 'italic', mt: 0.5 }}>
                    "{selectedCampaign.target_narrative}"
                  </Typography>
                </Paper>
              </Paper>

              {/* Explainable Risk Reasoning Breakdown */}
              <Paper sx={{ p: 3, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB', mb: 1.5 }}>
                  Explainable Risk Attribution & Evidence
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
                  Multi-factor composite scoring ({selectedCampaign.risk_score.toFixed(2)}) based on bot density, velocity, and reach:
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {selectedCampaign.explainability_reasons.map((reason, idx) => {
                    // Parse optional [TAG] prefix
                    let tag = 'GENERAL EVIDENCE';
                    let text = reason;
                    let tagColor = { bg: 'rgba(59, 130, 246, 0.15)', text: '#93C5FD', border: 'rgba(59, 130, 246, 0.4)' };

                    if (reason.startsWith('[')) {
                      const endBracket = reason.indexOf(']');
                      if (endBracket !== -1) {
                        tag = reason.substring(1, endBracket);
                        text = reason.substring(endBracket + 1).trim();

                        if (tag.includes('NARRATIVE')) {
                          tagColor = { bg: 'rgba(239, 68, 68, 0.15)', text: '#F87171', border: 'rgba(239, 68, 68, 0.4)' };
                        } else if (tag.includes('NETWORK') || tag.includes('COORDINATED')) {
                          tagColor = { bg: 'rgba(245, 158, 11, 0.15)', text: '#FBBF24', border: 'rgba(245, 158, 11, 0.4)' };
                        } else if (tag.includes('EVASION') || tag.includes('TACTIC')) {
                          tagColor = { bg: 'rgba(168, 85, 247, 0.15)', text: '#C084FC', border: 'rgba(168, 85, 247, 0.4)' };
                        } else if (tag.includes('AI') || tag.includes('SYNTHESIS')) {
                          tagColor = { bg: 'rgba(6, 182, 212, 0.15)', text: '#22D3EE', border: 'rgba(6, 182, 212, 0.4)' };
                        }
                      }
                    }

                    return (
                      <Box
                        key={idx}
                        sx={{
                          p: 1.8,
                          borderRadius: 2,
                          backgroundColor: '#070B14',
                          border: '1px solid rgba(255, 255, 255, 0.06)',
                          display: 'flex',
                          flexDirection: { xs: 'column', sm: 'row' },
                          alignItems: { xs: 'flex-start', sm: 'center' },
                          gap: 1.5,
                        }}
                      >
                        <Chip
                          size="small"
                          label={tag}
                          sx={{
                            bgcolor: tagColor.bg,
                            color: tagColor.text,
                            border: `1px solid ${tagColor.border}`,
                            fontWeight: 800,
                            fontSize: '0.65rem',
                            letterSpacing: '0.04em',
                            minWidth: 140,
                            justifyContent: 'center',
                          }}
                        />
                        <Typography variant="body2" sx={{ color: '#F3F4F6', fontWeight: 500, flex: 1 }}>
                          {text}
                        </Typography>
                      </Box>
                    );
                  })}
                </Box>
              </Paper>

              {/* Linked Multi-Platform Posts Table */}
              <Paper sx={{ p: 3, backgroundColor: '#0E1726', border: '1px solid rgba(255,255,255,0.08)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#F9FAFB', mb: 2 }}>
                  Dissemination Posts & Cross-Platform Lineage
                </Typography>

                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Platform</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Author Account</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Type</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Content Snippet</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Engagement</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedCampaign.posts?.map((p) => (
                        <TableRow key={p.id} hover>
                          <TableCell sx={{ color: '#60A5FA', fontWeight: 700 }}>{p.platform}</TableCell>
                          <TableCell sx={{ color: '#F3F4F6' }}>{p.account}</TableCell>
                          <TableCell>
                            <Chip size="small" label={p.post_type} sx={{ fontSize: '0.68rem', height: 20, fontWeight: 700 }} />
                          </TableCell>
                          <TableCell sx={{ color: '#94A3B8', maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {p.content_snippet}
                          </TableCell>
                          <TableCell sx={{ color: '#64748B', fontSize: '0.78rem', fontWeight: 600 }}>
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
            <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: '#0E1726' }}>
              <Typography variant="body1" sx={{ color: '#64748B' }}>
                Select a campaign from the list to view detailed telemetry.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
