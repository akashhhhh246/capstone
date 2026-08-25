import React, { useState } from 'react';
import { Box, Typography, Tooltip, Paper, Chip, LinearProgress } from '@mui/material';
import { Info, Sparkles, BarChart2 } from 'lucide-react';
import { GLTRResult, GLTRTokenInfo } from '../types';

interface GLTRViewerProps {
  gltrResult: GLTRResult;
}

export const GLTRViewer: React.FC<GLTRViewerProps> = ({ gltrResult }) => {
  const { tokens, bucket_distribution, estimated_perplexity, ai_likelihood_indicator, disclaimer } = gltrResult;
  const [selectedToken, setSelectedToken] = useState<GLTRTokenInfo | null>(null);

  const getBucketColor = (bucket: string) => {
    switch (bucket) {
      case 'green':
        return { bg: 'rgba(16, 185, 129, 0.25)', border: '#10B981', text: '#34D399', name: 'Top 10 (Predictable)' };
      case 'yellow':
        return { bg: 'rgba(245, 158, 11, 0.25)', border: '#F59E0B', text: '#FBBF24', name: 'Top 100 (Common)' };
      case 'red':
        return { bg: 'rgba(239, 68, 68, 0.25)', border: '#EF4444', text: '#F87171', name: 'Top 1000 (Uncommon)' };
      case 'purple':
        return { bg: 'rgba(168, 85, 247, 0.25)', border: '#A855F7', text: '#C084FC', name: '> 1000 (Tail / Human)' };
      default:
        return { bg: 'transparent', border: 'transparent', text: '#E5E7EB', name: 'Whitespace' };
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Bucket Distribution Legend Bar */}
      <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <Chip
          label={`Top 10 (Green): ${(bucket_distribution.green * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(16, 185, 129, 0.15)',
            color: '#34D399',
            border: '1px solid #10B981',
            fontWeight: 700,
          }}
        />
        <Chip
          label={`Top 100 (Yellow): ${(bucket_distribution.yellow * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(245, 158, 11, 0.15)',
            color: '#FBBF24',
            border: '1px solid #F59E0B',
            fontWeight: 700,
          }}
        />
        <Chip
          label={`Top 1000 (Red): ${(bucket_distribution.red * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(239, 68, 68, 0.15)',
            color: '#F87171',
            border: '1px solid #EF4444',
            fontWeight: 700,
          }}
        />
        <Chip
          label={`Tail >1000 (Purple): ${(bucket_distribution.purple * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(168, 85, 247, 0.15)',
            color: '#C084FC',
            border: '1px solid #A855F7',
            fontWeight: 700,
          }}
        />
      </Box>

      {/* Visual Proportion Bar */}
      <Box sx={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden', mb: 2 }}>
        <Box sx={{ width: `${bucket_distribution.green * 100}%`, bgcolor: '#10B981', transition: 'width 0.5s' }} />
        <Box sx={{ width: `${bucket_distribution.yellow * 100}%`, bgcolor: '#F59E0B', transition: 'width 0.5s' }} />
        <Box sx={{ width: `${bucket_distribution.red * 100}%`, bgcolor: '#EF4444', transition: 'width 0.5s' }} />
        <Box sx={{ width: `${bucket_distribution.purple * 100}%`, bgcolor: '#A855F7', transition: 'width 0.5s' }} />
      </Box>

      {/* Token Visualization Flow */}
      <Paper
        sx={{
          p: 2.5,
          maxHeight: 280,
          overflowY: 'auto',
          backgroundColor: '#0A0F1D',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2.5,
          lineHeight: 2.3,
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '0.92rem',
        }}
      >
        {tokens.map((t, idx) => {
          if (t.bucket === 'whitespace') {
            return <span key={idx}>{t.token}</span>;
          }
          const style = getBucketColor(t.bucket);
          const isSelected = selectedToken === t;
          return (
            <Tooltip
              key={idx}
              title={`Token: "${t.token}" | Rank: ${t.rank} | Prob: ${(t.prob * 100).toFixed(2)}% | Log-Prob: ${t.log_prob.toFixed(2)} | Click to pin`}
              arrow
            >
              <Box
                component="span"
                onClick={() => setSelectedToken(t)}
                sx={{
                  display: 'inline-block',
                  px: 0.8,
                  py: 0.2,
                  mx: 0.2,
                  borderRadius: '5px',
                  backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.4)' : style.bg,
                  border: isSelected ? '2px solid #60A5FA' : `1px solid ${style.border}`,
                  color: isSelected ? '#FFFFFF' : style.text,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    transform: 'scale(1.08)',
                    boxShadow: `0 0 10px ${style.border}`,
                  },
                }}
              >
                {t.token}
              </Box>
            </Tooltip>
          );
        })}
      </Paper>

      {/* Selected Token Inspector Card */}
      {selectedToken && (
        <Paper sx={{ p: 2, mt: 2, backgroundColor: '#0F172A', border: '1px solid #3B82F6', borderRadius: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2" sx={{ color: '#93C5FD', fontWeight: 800 }}>
              Pinned Token Forensic Details: "{selectedToken.token}"
            </Typography>
            <Chip
              size="small"
              label={getBucketColor(selectedToken.bucket).name}
              sx={{
                bgcolor: getBucketColor(selectedToken.bucket).bg,
                color: getBucketColor(selectedToken.bucket).text,
                fontWeight: 700,
              }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              Token Rank: <strong style={{ color: '#F3F4F6' }}>{selectedToken.rank}</strong> / 50,000
            </Typography>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              Next-Token Probability: <strong style={{ color: '#34D399' }}>{(selectedToken.prob * 100).toFixed(3)}%</strong>
            </Typography>
            <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
              Log Probability: <strong style={{ color: '#93C5FD' }}>{selectedToken.log_prob.toFixed(3)}</strong>
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Metrics Footer */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5, flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="caption" sx={{ color: '#94A3B8' }}>
          Estimated Perplexity: <strong style={{ color: '#F9FAFB' }}>{estimated_perplexity.toFixed(1)}</strong> | AI Likelihood: <strong style={{ color: ai_likelihood_indicator > 0.6 ? '#F87171' : '#34D399' }}>{(ai_likelihood_indicator * 100).toFixed(0)}%</strong>
        </Typography>
        <Typography variant="caption" sx={{ color: '#64748B', fontStyle: 'italic' }}>
          {disclaimer}
        </Typography>
      </Box>
    </Box>
  );
};
