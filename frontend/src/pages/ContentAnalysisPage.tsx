import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  Paper,
  TextField,
  Button,
  Chip,
  CircularProgress,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  Bot,
  UserCheck,
  Sparkles,
  GitBranch,
} from 'lucide-react';
import { api } from '../services/api';
import { DetectionResultResponse } from '../types';
import { GLTRViewer } from '../components/GLTRViewer';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

const SAMPLE_PRESETS = [
  {
    label: '⚡ Disinformation: Power Grid Panic (Seed)',
    text: 'URGENT ALERT: Confidential government whistleblowers have confirmed that national energy grid switching systems are undergoing a coordinated clandestine shutdown tonight at midnight to enforce simulated blackout mandates. Withdraw all bank funds immediately before ATMs freeze! #GridDown #EmergencyAlert',
    domain: 'disinformation',
  },
  {
    label: '🧬 Disinformation: AI Paraphrased Mutation',
    text: 'EMERGENCY LEAK: Insider sources reveal that electrical utility substations nationwide will be remotely disabled at 23:59 tonight under secret emergency decrees. Secure cash reserves and emergency rations before banking systems and telecommunications blackouts begin! Spread this message! #GridDown #BlackoutAlert',
    domain: 'disinformation',
  },
  {
    label: '💧 Disinformation: Water Contamination Alert',
    text: 'BREAKING INTEL: Leaked defense ministry documents prove that automated water filtration supplies in three major metropolitan districts have been secretly laced with unapproved biological neutralizing compounds. Do not drink municipal tap water under any circumstances! Share this alert immediately to protect your family! #WaterGateAlert #HealthCrisis',
    domain: 'disinformation',
  },
  {
    label: '🌌 Authentic Human: NASA JWST Deep Field Release',
    text: "NASA's James Webb Space Telescope has captured the deepest and sharpest infrared image of the distant universe to date. Known as Webb's First Deep Field, this image of galaxy cluster SMACS 0723 is overflowing with detail, revealing thousands of galaxies—including the faintest objects ever observed in the infrared—in a tiny sliver of sky approximately the size of a grain of sand held at arm's length by someone on the ground. The combined mass of the cluster acts as a gravitational lens, magnifying much more distant galaxies behind it.",
    domain: 'astrophysics',
  },
  {
    label: '🏛️ Authentic Human: EU AI Act Legislative Agreement',
    text: 'The European Parliament and Council have reached a landmark political agreement on the Artificial Intelligence Act, establishing comprehensive risk-based harmonized rules across the European Union. The legislation introduces strict prohibitions on unacceptable-risk AI systems such as cognitive behavioral manipulation and biometric categorization, while imposing rigorous transparency and systemic risk assessment obligations on general-purpose foundation models.',
    domain: 'technology_policy',
  },
  {
    label: '🔋 Authentic Human: MIT Solid-State Battery Journal',
    text: 'Materials scientists at MIT have engineered an inorganic solid-state lithium battery featuring a self-healing solid electrolyte interface that prevents dendrite penetration across thousands of rapid charge-discharge cycles. The solid-state architecture replaces volatile organic liquid electrolytes with a sulfide-based solid ceramic separator, achieving an energy density exceeding 500 watt-hours per kilogram while maintaining non-flammability.',
    domain: 'materials_science',
  },
  {
    label: '🤖 LLM Prose: GPT-4 Characteristic Boilerplate',
    text: 'It is important to remember that artificial intelligence systems are fundamentally computational models designed to process patterns in data. In conclusion, while AI models offer tremendous potential for productivity, they must be deployed with careful consideration of ethical standards, fairness, and safety protocols to ensure beneficial outcomes for society.',
    domain: 'technology',
  },
  {
    label: '🤖 LLM Prose: Sustainable Urban Architecture',
    text: 'As an AI language model, exploring the nuances of sustainable architecture reveals how modern urban planning integrates passive solar heating, green roofs, and recycled timber materials. Furthermore, these eco-friendly innovations significantly reduce the overall carbon footprint while optimizing energy efficiency across residential complexes.',
    domain: 'architecture',
  },
];

export const ContentAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState(SAMPLE_PRESETS[0].text);
  const [domain, setDomain] = useState(SAMPLE_PRESETS[0].domain);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResultResponse | null>(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    try {
      setLoading(true);
      const data = await api.analyzeContent(inputText, domain, true);
      setResult(data);
    } catch (e) {
      console.error('Analysis failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
          Multi-Model Content Analysis & Estimation Workbench
        </Typography>
        <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
          AI Text Detection: TF-IDF Logistic Regression, GLTR Statistical Token Likelihood, and Watermark Audit
        </Typography>
      </Box>

      {/* Mandatory Human Oversight Advisory */}
      <DisclaimerAlert type="detection" />

      {/* Input Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1.5 }}>
          Investigative Text Ingestion
        </Typography>

        {/* Preset Sample Selector */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Typography variant="caption" sx={{ color: '#9CA3AF', display: 'flex', alignItems: 'center', mr: 1 }}>
            Benchmark Presets:
          </Typography>
          {SAMPLE_PRESETS.map((preset, idx) => (
            <Chip
              key={idx}
              label={preset.label}
              clickable
              size="small"
              onClick={() => {
                setInputText(preset.text);
                setDomain(preset.domain);
              }}
              sx={{
                bgcolor: inputText === preset.text ? 'rgba(59, 130, 246, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: inputText === preset.text ? '#93C5FD' : '#D1D5DB',
                border: inputText === preset.text ? '1px solid #3B82F6' : '1px solid rgba(255, 255, 255, 0.1)',
                '&:hover': { bgcolor: 'rgba(59, 130, 246, 0.2)' },
              }}
            />
          ))}
        </Box>

        <TextField
          fullWidth
          multiline
          rows={5}
          variant="outlined"
          placeholder="Paste real-world article, speech, report, or social media text snippet to evaluate..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          sx={{
            backgroundColor: '#090D16',
            borderRadius: 2,
            mb: 2,
            '& .MuiOutlinedInput-root': {
              color: '#F3F4F6',
              fontFamily: '"Inter", sans-serif',
              fontSize: '0.92rem',
            },
          }}
        />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" sx={{ color: '#6B7280' }}>
            Text Length: {inputText.length} characters | Word Count: {inputText.trim().split(/\s+/).filter(Boolean).length}
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <Sparkles size={18} />}
            onClick={handleAnalyze}
            disabled={loading || !inputText.trim()}
          >
            {loading ? 'Evaluating Multi-Model Pipeline...' : 'Run Detection Pipeline'}
          </Button>
        </Box>
      </Paper>

      {/* Analysis Results Display */}
      {result && (
        <Grid container spacing={3}>
          {/* Left Column: Classification Badge & Score breakdown */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
                Linguistic Classifier Verdict
              </Typography>

              <Box
                sx={{
                  p: 2.5,
                  borderRadius: 2,
                  textAlign: 'center',
                  backgroundColor: result.classification === 'AI_GENERATED' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                  border: `1.5px solid ${result.classification === 'AI_GENERATED' ? '#EF4444' : '#10B981'}`,
                  mb: 3,
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  {result.classification === 'AI_GENERATED' ? (
                    <Bot size={36} color="#F87171" />
                  ) : (
                    <UserCheck size={36} color="#34D399" />
                  )}
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 800, color: result.classification === 'AI_GENERATED' ? '#F87171' : '#34D399' }}>
                  {result.classification.replace('_', ' ')}
                </Typography>
                <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                  Model Confidence: {(result.confidence * 100).toFixed(1)}%
                </Typography>
              </Box>

              {/* Calibrated AI Probability Meter */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
                  <Typography variant="body2" sx={{ color: '#9CA3AF', fontWeight: 600 }}>
                    AI-Generation Probability
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#F3F4F6', fontWeight: 800, fontFamily: 'monospace' }}>
                    {(result.ai_probability * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={result.ai_probability * 100}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    backgroundColor: '#1E293B',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: result.ai_probability > 0.6 ? '#EF4444' : (result.ai_probability > 0.4 ? '#F59E0B' : '#10B981'),
                    },
                  }}
                />
              </Box>

              {/* Watermark Status */}
              <Box sx={{ mb: 3, p: 2, borderRadius: 2, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 700, textTransform: 'uppercase' }}>
                  Watermark Verification
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: result.watermark_result.status === 'DETECTED' ? '#34D399' : '#9CA3AF' }}>
                    {result.watermark_result.status}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#6B7280' }}>
                    {result.watermark_result.scheme}
                  </Typography>
                </Box>
              </Box>

              {/* Diagnostic Indicators */}
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1 }}>
                Synthesized Indicators
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.8, mb: 3 }}>
                {result.indicators.map((ind, idx) => (
                  <Typography key={idx} variant="caption" sx={{ color: '#D1D5DB', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    • {ind}
                  </Typography>
                ))}
              </Box>

              {/* Track in Part 2 Provenance button */}
              {result.content_id && (
                <Button
                  fullWidth
                  variant="outlined"
                  color="primary"
                  startIcon={<GitBranch size={16} />}
                  onClick={() => navigate(`/provenance?contentId=${result.content_id}`)}
                >
                  Track Lineage in Provenance DAG
                </Button>
              )}
            </Paper>
          </Grid>

          {/* Right Column: GLTR Token Distribution & Stylometric Features */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 1 }}>
                GLTR-Style Statistical Token Rank Breakdown
              </Typography>
              <Typography variant="body2" sx={{ color: '#9CA3AF', mb: 2 }}>
                Tokens colored by statistical likelihood: Green (Top 10), Yellow (Top 100), Red (Top 1000), Purple (Tail).
              </Typography>

              <GLTRViewer gltrResult={result.gltr_result} />

              <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

              {/* Stylometric Feature Grid */}
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#F9FAFB', mb: 2 }}>
                Stylometric & Entropy Features
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Burstiness Variance</Typography>
                    <Typography variant="h6" sx={{ color: '#F3F4F6', fontFamily: 'monospace' }}>
                      {result.statistical_features.burstiness}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Shannon Entropy</Typography>
                    <Typography variant="h6" sx={{ color: '#F3F4F6', fontFamily: 'monospace' }}>
                      {result.statistical_features.shannon_entropy}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Lexical TTR Ratio</Typography>
                    <Typography variant="h6" sx={{ color: '#F3F4F6', fontFamily: 'monospace' }}>
                      {result.statistical_features.lexical_diversity_ttr}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ p: 1.5, borderRadius: 1.5, backgroundColor: '#090D16', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Avg Word Length</Typography>
                    <Typography variant="h6" sx={{ color: '#F3F4F6', fontFamily: 'monospace' }}>
                      {result.statistical_features.avg_word_length}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};
