import React from 'react';
import { Alert, AlertTitle, Typography, Box } from '@mui/material';
import { ShieldAlert, Info } from 'lucide-react';

interface DisclaimerAlertProps {
  type?: 'detection' | 'general' | 'privacy';
}

export const DisclaimerAlert: React.FC<DisclaimerAlertProps> = ({ type = 'detection' }) => {
  if (type === 'privacy') {
    return (
      <Alert
        severity="info"
        icon={<Info size={20} />}
        sx={{
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          color: '#E0F2FE',
          borderRadius: 2,
          mb: 3,
        }}
      >
        <AlertTitle sx={{ fontWeight: 700, color: '#38BDF8' }}>
          AI Content Integrity Research & Civil Liberties Safeguards
        </AlertTitle>
        <Typography variant="body2" sx={{ color: '#BAE6FD', fontSize: '0.85rem' }}>
          This system operates exclusively with <strong>synthetic, pseudonymized, and public benchmark data</strong>. It does not perform surveillance, scrape private social media accounts, deanonymize individuals, or generate real-world disinformation.
        </Typography>
      </Alert>
    );
  }

  return (
    <Alert
      severity="warning"
      icon={<ShieldAlert size={20} />}
      sx={{
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        color: '#FEF3C7',
        borderRadius: 2,
        mb: 3,
      }}
    >
      <AlertTitle sx={{ fontWeight: 700, color: '#FBBF24' }}>
        Statistical Estimation Notice — Human Analyst Review Required
      </AlertTitle>
      <Typography variant="body2" sx={{ color: '#FDE68A', fontSize: '0.85rem' }}>
        <strong>AI-generated probability ≠ proof of AI generation.</strong> Stylometric anomalies, token probability tiers, and watermark signals are decision-support heuristics subject to false positives (e.g. non-native speakers, technical jargon) and adversarial evasion. Always require human investigative validation before attribution.
      </Typography>
    </Alert>
  );
};
