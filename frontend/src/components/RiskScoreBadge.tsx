import React from 'react';
import { Chip, Box, Tooltip, Typography } from '@mui/material';

interface RiskScoreBadgeProps {
  score: number;
  severity?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  showReasonsTooltip?: boolean;
  reasons?: string[];
}

export const RiskScoreBadge: React.FC<RiskScoreBadgeProps> = ({
  score,
  severity,
  showReasonsTooltip = false,
  reasons = [],
}) => {
  const sev = severity || (score >= 0.8 ? 'CRITICAL' : score >= 0.6 ? 'HIGH' : score >= 0.4 ? 'MEDIUM' : 'LOW');

  const getColor = () => {
    switch (sev) {
      case 'CRITICAL':
        return { bg: 'rgba(239, 68, 68, 0.2)', border: '#EF4444', text: '#F87171' };
      case 'HIGH':
        return { bg: 'rgba(245, 158, 11, 0.2)', border: '#F59E0B', text: '#FBBF24' };
      case 'MEDIUM':
        return { bg: 'rgba(59, 130, 246, 0.2)', border: '#3B82F6', text: '#60A5FA' };
      default:
        return { bg: 'rgba(16, 185, 129, 0.2)', border: '#10B981', text: '#34D399' };
    }
  };

  const style = getColor();

  const badgeContent = (
    <Chip
      label={`${sev} (${score.toFixed(2)})`}
      sx={{
        bgcolor: style.bg,
        border: `1px solid ${style.border}`,
        color: style.text,
        fontWeight: 700,
        fontSize: '0.75rem',
        letterSpacing: '0.04em',
      }}
    />
  );

  if (!showReasonsTooltip || reasons.length === 0) {
    return badgeContent;
  }

  return (
    <Tooltip
      title={
        <Box sx={{ p: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: style.text, mb: 0.5 }}>
            Explainable Risk Factors ({sev}):
          </Typography>
          <ul style={{ margin: 0, paddingLeft: 16 }}>
            {reasons.map((r, i) => (
              <li key={i}>
                <Typography variant="caption" sx={{ color: '#E5E7EB' }}>
                  {r}
                </Typography>
              </li>
            ))}
          </ul>
        </Box>
      }
      arrow
    >
      <Box component="span" sx={{ display: 'inline-block', cursor: 'pointer' }}>
        {badgeContent}
      </Box>
    </Tooltip>
  );
};
