import React, { useRef, useEffect } from 'react';
import { Box, Paper, Typography, Chip, Badge } from '@mui/material';
import { SimulationEventPayload } from '../types';

interface LiveEventStreamProps {
  events: SimulationEventPayload[];
  maxItems?: number;
}

export const LiveEventStream: React.FC<LiveEventStreamProps> = ({ events, maxItems = 50 }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0; // Auto-scroll to latest event
    }
  }, [events]);

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'POST':
        return '#3B82F6';
      case 'RESHARE':
        return '#10B981';
      case 'REPLY':
        return '#8B5CF6';
      case 'QUOTE':
        return '#EC4899';
      case 'CROSS_PLATFORM_SHARE':
        return '#F59E0B';
      case 'CONTENT_VARIANT':
        return '#EF4444';
      default:
        return '#9CA3AF';
    }
  };

  return (
    <Paper
      ref={containerRef}
      sx={{
        p: 2,
        height: 380,
        overflowY: 'auto',
        backgroundColor: '#090D16',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 1.2,
      }}
    >
      {events.length === 0 ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <Typography variant="body2" sx={{ color: '#6B7280', fontStyle: 'italic' }}>
            Awaiting real-time propagation events from simulator...
          </Typography>
        </Box>
      ) : (
        events.slice(0, maxItems).map((ev) => {
          const color = getEventTypeColor(ev.event_type);
          const time = new Date(ev.timestamp).toLocaleTimeString();

          return (
            <Box
              key={ev.event_id}
              sx={{
                p: 1.2,
                borderRadius: '6px',
                backgroundColor: '#111827',
                borderLeft: `4px solid ${color}`,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: '#1F2937',
                },
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={ev.event_type}
                    size="small"
                    sx={{
                      fontSize: '0.65rem',
                      height: 18,
                      bgcolor: `${color}22`,
                      color: color,
                      fontWeight: 700,
                    }}
                  />
                  <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 600 }}>
                    {ev.account_handle}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                    on <strong>{ev.platform_name}</strong>
                  </Typography>
                </Box>
                <Typography variant="caption" sx={{ color: '#6B7280', fontFamily: 'monospace' }}>
                  {time}
                </Typography>
              </Box>

              <Typography variant="body2" sx={{ color: '#E5E7EB', fontSize: '0.82rem', mb: 0.5 }}>
                {ev.content_snippet}
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                  Velocity: <strong>{ev.velocity} ev/hr</strong>
                </Typography>
                <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                  Audience Reach: <strong>{ev.total_reach.toLocaleString()}</strong>
                </Typography>
                <Typography variant="caption" sx={{ color: ev.risk_score > 0.7 ? '#F87171' : '#34D399' }}>
                  Risk: <strong>{(ev.risk_score * 100).toFixed(0)}%</strong>
                </Typography>
              </Box>
            </Box>
          );
        })
      )}
    </Paper>
  );
};
