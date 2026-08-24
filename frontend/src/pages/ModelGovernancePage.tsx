import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Cpu,
  ShieldCheck,
  AlertTriangle,
  Info,
  ChevronDown,
  Lock,
  EyeOff,
  UserCheck,
} from 'lucide-react';
import { api } from '../services/api';
import { ModelMetadataItem } from '../types';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const ModelGovernancePage: React.FC = () => {
  const [models, setModels] = useState<ModelMetadataItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setLoading(true);
        const data = await api.listModels();
        setModels(data);
      } catch (e) {
        console.error('Failed to load model metadata:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'TRAINED':
        return { bg: 'rgba(16, 185, 129, 0.2)', border: '#10B981', text: '#34D399' };
      case 'PRETRAINED':
        return { bg: 'rgba(59, 130, 246, 0.2)', border: '#3B82F6', text: '#60A5FA' };
      case 'DEMONSTRATION':
        return { bg: 'rgba(245, 158, 11, 0.2)', border: '#F59E0B', text: '#FBBF24' };
      default:
        return { bg: 'rgba(156, 163, 175, 0.2)', border: '#9CA3AF', text: '#D1D5DB' };
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
          ML Model Governance, Transparency & Ethics
        </Typography>
        <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
          Model Cards, Technical Methodologies, Uncertainty Bounds, and Privacy Safeguards
        </Typography>
      </Box>

      {/* Primary Privacy & Civil Liberties Charter Banner */}
      <DisclaimerAlert type="privacy" />

      {/* Model Cards Grid */}
      <Typography variant="h6" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
        Active Machine Learning Subsystems ({models.length})
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {models.map((m) => {
          const statusStyle = getStatusColor(m.operational_status);

          return (
            <Grid item xs={12} md={6} key={m.id}>
              <Paper
                sx={{
                  p: 3,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#F3F4F6', fontSize: '1.05rem' }}>
                      {m.name}
                    </Typography>
                    <Chip
                      size="small"
                      label={m.operational_status}
                      sx={{
                        bgcolor: statusStyle.bg,
                        border: `1px solid ${statusStyle.border}`,
                        color: statusStyle.text,
                        fontWeight: 700,
                        fontSize: '0.68rem',
                      }}
                    />
                  </Box>

                  <Typography variant="caption" sx={{ color: '#60A5FA', fontFamily: 'monospace', display: 'block', mb: 2 }}>
                    Version: {m.version} | Type: {m.model_type}
                  </Typography>

                  <Typography variant="body2" sx={{ color: '#D1D5DB', mb: 2 }}>
                    <strong>Methodology:</strong> {m.methodology}
                  </Typography>

                  <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.05)', mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 700 }}>
                      Training / Reference Dataset:
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#E5E7EB', display: 'block', mt: 0.3 }}>
                      {m.dataset_info}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.15)' }}>
                  <Typography variant="caption" sx={{ color: '#F87171', fontWeight: 700 }}>
                    Known Limitations & Uncertainty:
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#FCA5A5', display: 'block', mt: 0.3 }}>
                    {m.limitations}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          );
        })}
      </Grid>

      {/* Ethical Governance & Civil Liberties Charter Accordion */}
      <Typography variant="h6" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
        Ethical Framework & Legal Safeguards
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        <Accordion sx={{ backgroundColor: '#111827', border: '1px solid rgba(255,255,255,0.08)' }}>
          <AccordionSummary expandIcon={<ChevronDown color="#9CA3AF" />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <EyeOff size={18} color="#06B6D4" />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                1. Non-Surveillance & Pseudonymization Guarantees
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ color: '#D1D5DB' }}>
              This research platform strictly utilizes synthetic social media graphs and pseudonymized node IDs. No real personal accounts, private communications, or biometric identifiers are harvested or tracked. The system is designed for defensive research on information network topologies rather than individual surveillance.
            </Typography>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ backgroundColor: '#111827', border: '1px solid rgba(255,255,255,0.08)' }}>
          <AccordionSummary expandIcon={<ChevronDown color="#9CA3AF" />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <UserCheck size={18} color="#10B981" />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                2. Mandatory Human-in-the-Loop Oversight
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ color: '#D1D5DB' }}>
              All algorithmic outputs (AI probability scores, GLTR perplexities, GNN anomaly scores) represent statistical estimates and decision-support aids. They must never serve as sole automated grounds for censorship, account termination, or legal sanctions without thorough human analyst verification.
            </Typography>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ backgroundColor: '#111827', border: '1px solid rgba(255,255,255,0.08)' }}>
          <AccordionSummary expandIcon={<ChevronDown color="#9CA3AF" />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <AlertTriangle size={18} color="#F59E0B" />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                3. Bias Mitigation & False Positive Awareness
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ color: '#D1D5DB' }}>
              Statistical detectors are susceptible to false positives when evaluating non-native English writing, formal academic prose, or technical legal documents. The multi-model pipeline combines stylometry, token entropy, and structural graph diffusion metrics to cross-verify signals before attributing coordinated intent.
            </Typography>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ backgroundColor: '#111827', border: '1px solid rgba(255,255,255,0.08)' }}>
          <AccordionSummary expandIcon={<ChevronDown color="#9CA3AF" />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Lock size={18} color="#8B5CF6" />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                4. Adversarial Robustness & Evasion Limits
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ color: '#D1D5DB' }}>
              Adversaries can evade single-point text classifiers through homoglyph substitution, adversarial paraphrasing, or zero-shot prompt rewriting. The system counters this through dense semantic embedding clusters (SentenceTransformers) and multi-platform graph propagation analysis (NetworkX + GNN), detecting the coordinated spread of information even when textual wording mutates.
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
};
