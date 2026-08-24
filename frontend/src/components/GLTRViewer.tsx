import React from 'react';
import { Box, Typography, Tooltip, Paper, Chip } from '@mui/material';
import { GLTRResult } from '../types';

interface GLTRViewerProps {
  gltrResult: GLTRResult;
}

export const GLTRViewer: React.FC<GLTRViewerProps> = ({ gltrResult }) => {
  const { tokens, bucket_distribution, estimated_perplexity, ai_likelihood_indicator, disclaimer } = gltrResult;

  const getBucketColor = (bucket: string) => {
    switch (bucket) {
      case 'green':
        return { bg: 'rgba(16, 185, 129, 0.25)', border: '#10B981', text: '#34D399' };
      case 'yellow':
        return { bg: 'rgba(245, 158, 11, 0.25)', border: '#F59E0B', text: '#FBBF24' };
      case 'red':
        return { bg: 'rgba(239, 68, 68, 0.25)', border: '#EF4444', text: '#F87171' };
      case 'purple':
        return { bg: 'rgba(168, 85, 247, 0.25)', border: '#A855F7', text: '#C084FC' };
      default:
        return { bg: 'transparent', border: 'transparent', text: '#E5E7EB' };
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Bucket Distribution Legend Bar */}
      <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
        <Chip
          label={`Top 10 (Green): ${(bucket_distribution.green * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(16, 185, 129, 0.15)',
            color: '#34D399',
            border: '1px solid #10B981',
            fontWeight: 600,
          }}
        />
        <Chip
          label={`Top 100 (Yellow): ${(bucket_distribution.yellow * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(245, 158, 11, 0.15)',
            color: '#FBBF24',
            border: '1px solid #F59E0B',
            fontWeight: 600,
          }}
        />
        <Chip
          label={`Top 1000 (Red): ${(bucket_distribution.red * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(239, 68, 68, 0.15)',
            color: '#F87171',
            border: '1px solid #EF4444',
            fontWeight: 600,
          }}
        />
        <Chip
          label={`Tail >1000 (Purple): ${(bucket_distribution.purple * 100).toFixed(1)}%`}
          sx={{
            bgcolor: 'rgba(168, 85, 247, 0.15)',
            color: '#C084FC',
            border: '1px solid #A855F7',
            fontWeight: 600,
          }}
        />
      </Box>

      {/* Token Visualization Flow */}
      <Paper
        sx={{
          p: 2.5,
          maxHeight: 280,
          overflowY: 'auto',
          backgroundColor: '#0F172A',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          lineHeight: 2.2,
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: '0.92rem',
        }}
      >
        {tokens.map((t, idx) => {
          if (t.bucket === 'whitespace') {
            return <span key={idx}>{t.token}</span>;
          }
          const style = getBucketColor(t.bucket);
          return (
            <Tooltip
              key={idx}
              title={`Token: "${t.token}" | Estimated Rank: ${t.rank} | Prob: ${t.prob.toFixed(4)} | Tier: ${t.bucket.toUpperCase()}`}
              arrow
            >
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  px: 0.8,
                  py: 0.2,
                  mx: 0.2,
                  borderRadius: '4px',
                  backgroundColor: style.bg,
                  border: `1px solid ${style.border}`,
                  color: style.text,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    transform: 'scale(1.08)',
                    boxShadow: `0 0 8px ${style.border}`,
                  },
                }}
              >
                {t.token}
              </Box>
            </Tooltip>
          );
        })}
      </Paper>

      {/* Metrics Footer */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1.5 }}>
        <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
          Estimated Perplexity: <strong>{estimated_perplexity.toFixed(1)}</strong> | AI Likelihood Indicator: <strong>{(ai_likelihood_indicator * 100).toFixed(0)}%</strong>
        </Typography>
        <Typography variant="caption" sx={{ color: '#6B7280', fontStyle: 'italic' }}>
          {disclaimer}
        </Typography>
      </Box>
    </Box>
  );
};
