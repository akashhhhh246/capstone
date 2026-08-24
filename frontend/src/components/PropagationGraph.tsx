import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Box, Paper, Typography, Chip } from '@mui/material';

interface PropagationGraphProps {
  nodes: any[];
  edges: any[];
  filterPlatform?: string;
  onSelectNode?: (nodeData: any) => void;
}

export const PropagationGraph: React.FC<PropagationGraphProps> = ({
  nodes: rawNodes,
  edges: rawEdges,
  filterPlatform = 'ALL',
  onSelectNode,
}) => {
  // Filter nodes if a specific platform is selected
  const filteredRawNodes = useMemo(() => {
    if (filterPlatform === 'ALL') return rawNodes;
    return rawNodes.filter((n) => {
      if (n.type === 'CAMPAIGN') return true;
      if (n.type === 'PLATFORM') return (n.name || '').toLowerCase().includes(filterPlatform.toLowerCase());
      if (n.platform) return (n.platform || '').toLowerCase().includes(filterPlatform.toLowerCase());
      return true;
    });
  }, [rawNodes, filterPlatform]);

  const activeNodeIds = useMemo(() => new Set(filteredRawNodes.map((n) => n.id)), [filteredRawNodes]);

  // Clean, spacious multi-column layout (Platforms -> Accounts -> Posts)
  const flowNodes: Node[] = useMemo(() => {
    // Separate by type for clear tier lanes
    const campaignNodes = filteredRawNodes.filter((n) => n.type === 'CAMPAIGN');
    const platformNodes = filteredRawNodes.filter((n) => n.type === 'PLATFORM');
    const accountNodes = filteredRawNodes.filter((n) => n.type === 'SYNTHETIC_ACCOUNT');
    const postNodes = filteredRawNodes.filter((n) => n.type === 'POST');

    const result: Node[] = [];

    // Lane 1: Campaign Root (Top Center)
    campaignNodes.forEach((n, idx) => {
      result.push({
        id: n.id,
        position: { x: 380 + idx * 280, y: 30 },
        data: {
          label: (
            <Box sx={{ p: 1.2, minWidth: 180, textAlign: 'center' }}>
              <Chip size="small" label="CAMPAIGN ROOT" sx={{ bgcolor: 'rgba(239, 68, 68, 0.2)', color: '#F87171', fontWeight: 800, mb: 0.5 }} />
              <Typography variant="body2" sx={{ fontWeight: 800, color: '#FFF' }}>
                {n.name || n.id}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#1E1B4B',
          border: '2px solid #EF4444',
          borderRadius: 12,
          boxShadow: '0 0 20px rgba(239, 68, 68, 0.35)',
        },
      });
    });

    // Lane 2: Platforms (Row 2)
    platformNodes.forEach((n, idx) => {
      result.push({
        id: n.id,
        position: { x: 60 + idx * 240, y: 170 },
        data: {
          label: (
            <Box sx={{ p: 1, minWidth: 150, textAlign: 'center' }}>
              <Chip size="small" label="PLATFORM" sx={{ bgcolor: 'rgba(6, 182, 212, 0.2)', color: '#22D3EE', fontWeight: 700, mb: 0.4 }} />
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#F3F4F6' }}>
                {n.name || n.id}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#0F172A',
          border: '1.5px solid #06B6D4',
          borderRadius: 10,
        },
      });
    });

    // Lane 3: Synthetic Accounts (Row 3)
    accountNodes.forEach((n, idx) => {
      const isBot = (n.bot_probability || 0) > 0.6;
      result.push({
        id: n.id,
        position: { x: 40 + (idx % 4) * 250, y: 300 + Math.floor(idx / 4) * 110 },
        data: {
          label: (
            <Box sx={{ p: 1, minWidth: 160 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.3 }}>
                <Chip size="small" label={isBot ? 'BOT NODE' : 'ACCOUNT'} sx={{ fontSize: '0.62rem', height: 18, bgcolor: isBot ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)', color: isBot ? '#FBBF24' : '#34D399', fontWeight: 700 }} />
                {n.bot_probability !== undefined && (
                  <Typography variant="caption" sx={{ color: isBot ? '#F87171' : '#34D399', fontWeight: 700 }}>
                    {(n.bot_probability * 100).toFixed(0)}% Bot
                  </Typography>
                )}
              </Box>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
                {n.handle || n.name || n.id}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#111827',
          border: `1.5px solid ${isBot ? '#F59E0B' : '#10B981'}`,
          borderRadius: 8,
        },
      });
    });

    // Lane 4: Posts & Relays (Row 4)
    postNodes.forEach((n, idx) => {
      result.push({
        id: n.id,
        position: { x: 50 + (idx % 4) * 250, y: 480 + Math.floor(idx / 4) * 120 },
        data: {
          label: (
            <Box sx={{ p: 1, minWidth: 160 }}>
              <Chip size="small" label={n.post_type || 'POST'} sx={{ fontSize: '0.62rem', height: 18, bgcolor: 'rgba(139, 92, 246, 0.2)', color: '#DDD6FE', fontWeight: 700, mb: 0.3 }} />
              <Typography variant="caption" sx={{ color: '#E5E7EB', display: 'block', fontWeight: 600 }}>
                {n.id.substring(0, 14)}
              </Typography>
              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                Likes: {n.likes || 0} • Shares: {n.reshares || 0}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#1E1B4B',
          border: '1.5px solid #8B5CF6',
          borderRadius: 8,
        },
      });
    });

    return result;
  }, [filteredRawNodes]);

  const flowEdges: Edge[] = useMemo(() => {
    return rawEdges
      .filter((e) => activeNodeIds.has(e.source) && activeNodeIds.has(e.target))
      .map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        animated: true,
        style: { stroke: '#818CF8', strokeWidth: 1.5 },
        labelStyle: { fill: '#C7D2FE', fontSize: 10, fontWeight: 600 },
        labelBgStyle: { fill: '#0F172A', fillOpacity: 0.9 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#818CF8',
        },
      }));
  }, [rawEdges, activeNodeIds]);

  return (
    <Paper
      sx={{
        width: '100%',
        height: 560,
        backgroundColor: '#070B14',
        borderRadius: 3,
        border: '1px solid rgba(255, 255, 255, 0.08)',
        overflow: 'hidden',
      }}
    >
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        onNodeClick={(_, node) => {
          if (onSelectNode && node.data?.raw) {
            onSelectNode(node.data.raw);
          }
        }}
        fitView
      >
        <Background color="#1E293B" gap={20} />
        <Controls style={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', color: '#FFF' }} />
        <MiniMap
          nodeColor={(n) => (n.style?.borderColor as string) || '#8B5CF6'}
          maskColor="rgba(0, 0, 0, 0.75)"
          style={{ backgroundColor: '#0F172A', border: '1px solid rgba(255,255,255,0.1)' }}
        />
      </ReactFlow>
    </Paper>
  );
};
