import React from 'react';
import { Card, CardContent, Typography, Box, Skeleton } from '@mui/material';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: string;
  loading?: boolean;
  trend?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = '#3B82F6',
  loading = false,
  trend,
}) => {
  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        transition: 'transform 0.2s ease, border-color 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          borderColor: `${color}88`,
        },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
          <Typography variant="body2" sx={{ color: '#9CA3AF', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {title}
          </Typography>
          <Box
            sx={{
              p: 1,
              borderRadius: '8px',
              backgroundColor: `${color}15`,
              color: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>

        {loading ? (
          <Skeleton variant="text" width="60%" height={40} />
        ) : (
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB', fontFamily: '"JetBrains Mono", monospace' }}>
            {value}
          </Typography>
        )}

        {subtitle && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 0.5 }}>
            {trend && (
              <Typography variant="caption" sx={{ color: color, fontWeight: 700 }}>
                {trend}
              </Typography>
            )}
            <Typography variant="caption" sx={{ color: '#6B7280' }}>
              {subtitle}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
