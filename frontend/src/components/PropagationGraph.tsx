import React, { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
  Position,
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
  // 1. Filter nodes based on selected platform filter
  const filteredRawNodes = useMemo(() => {
    if (filterPlatform === 'ALL') return rawNodes;
    const filterLower = filterPlatform.toLowerCase();
    return rawNodes.filter((n) => {
      if (n.type === 'CAMPAIGN') return true;
      if (n.type === 'PLATFORM') return (n.name || '').toLowerCase().includes(filterLower);
      if (n.platform_id) {
        // Match platform ID or platform name
        const matchPlat = rawNodes.find((p) => p.type === 'PLATFORM' && p.id === n.platform_id);
        if (matchPlat && (matchPlat.name || '').toLowerCase().includes(filterLower)) return true;
      }
      if (n.platform) return (n.platform || '').toLowerCase().includes(filterLower);
      return false;
    });
  }, [rawNodes, filterPlatform]);

  const activeNodeIds = useMemo(() => new Set(filteredRawNodes.map((n) => n.id)), [filteredRawNodes]);

  // 2. Compute Spacious, Columnar Swimlane Layout
  // Columns: Campaign (Top Center) -> Platforms (Lanes) -> Accounts (under platform) -> Posts (under account)
  const flowNodes: Node[] = useMemo(() => {
    const campaignNodes = filteredRawNodes.filter((n) => n.type === 'CAMPAIGN');
    const platformNodes = filteredRawNodes.filter((n) => n.type === 'PLATFORM');
    const accountNodes = filteredRawNodes.filter((n) => n.type === 'SYNTHETIC_ACCOUNT');
    const postNodes = filteredRawNodes.filter((n) => n.type === 'POST');

    const result: Node[] = [];

    // Layout configuration constants
    const cardWidth = 240;
    const colWidth = 270;
    const colGap = 90;
    const totalPlatforms = Math.max(1, platformNodes.length);
    const totalWidth = totalPlatforms * colWidth + (totalPlatforms - 1) * colGap;
    const startX = 60;

    // Helper map: platform ID -> column index (0, 1, 2, ...)
    const platformColIndex = new Map<string, number>();
    platformNodes.forEach((p, idx) => {
      platformColIndex.set(p.id, idx);
    });

    // Helper map: account ID -> platform column index
    const accountColIndex = new Map<string, number>();
    accountNodes.forEach((a, idx) => {
      let col = platformColIndex.get(a.platform_id || '');
      if (col === undefined) {
        // Fallback: search by name matching or distribute evenly
        const matchedPlat = platformNodes.find(
          (p) => (a.handle || '').toLowerCase().includes((p.name || '').toLowerCase().replace('simu', ''))
        );
        col = matchedPlat ? (platformColIndex.get(matchedPlat.id) ?? (idx % totalPlatforms)) : (idx % totalPlatforms);
      }
      accountColIndex.set(a.id, col);
    });

    // Helper map: post ID -> column index
    const postColIndex = new Map<string, number>();
    postNodes.forEach((p, idx) => {
      let col = p.platform_id ? platformColIndex.get(p.platform_id) : undefined;
      if (col === undefined && p.account_id) {
        col = accountColIndex.get(p.account_id);
      }
      if (col === undefined) {
        col = idx % totalPlatforms;
      }
      postColIndex.set(p.id, col);
    });

    // --- ROW 1: Campaign Root (Top Center) ---
    const campaignCenterX = startX + Math.max(0, (totalWidth - 300) / 2);
    campaignNodes.forEach((n, idx) => {
      result.push({
        id: n.id,
        position: { x: campaignCenterX + idx * 320, y: 30 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.5, textAlign: 'center', width: '100%', boxSizing: 'border-box' }}>
              <Chip
                size="small"
                label="CAMPAIGN ROOT"
                sx={{
                  bgcolor: 'rgba(239, 68, 68, 0.25)',
                  color: '#F87171',
                  fontWeight: 800,
                  fontSize: '0.68rem',
                  height: 20,
                  mb: 0.6,
                }}
              />
              <Typography variant="body1" sx={{ fontWeight: 800, color: '#FFF', fontSize: '0.92rem' }}>
                {n.name || n.id}
              </Typography>
              <Typography variant="caption" sx={{ color: '#FCA5A5', fontSize: '0.7rem' }}>
                Coordinated Disinformation Target
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          width: 300,
          backgroundColor: '#1C1917',
          border: '2px solid #EF4444',
          borderRadius: 12,
          boxShadow: '0 0 25px rgba(239, 68, 68, 0.4)',
          overflow: 'hidden',
          padding: 0,
        },
      });
    });

    // --- ROW 2: Platforms (Lanes across) ---
    platformNodes.forEach((n, idx) => {
      const colX = startX + idx * (colWidth + colGap);
      result.push({
        id: n.id,
        position: { x: colX, y: 190 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.2, textAlign: 'center', width: '100%', boxSizing: 'border-box' }}>
              <Chip
                size="small"
                label="PLATFORM VECTOR"
                sx={{
                  bgcolor: 'rgba(6, 182, 212, 0.2)',
                  color: '#22D3EE',
                  fontWeight: 800,
                  fontSize: '0.65rem',
                  height: 18,
                  mb: 0.4,
                }}
              />
              <Typography variant="body2" sx={{ fontWeight: 800, color: '#F3F4F6' }}>
                {n.name || n.id}
              </Typography>
              <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem' }}>
                {n.platform_type || 'Social Network'}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          width: cardWidth,
          backgroundColor: '#0F172A',
          border: '1.5px solid #06B6D4',
          borderRadius: 10,
          boxShadow: '0 4px 16px rgba(6, 182, 212, 0.2)',
          overflow: 'hidden',
          padding: 0,
        },
      });
    });

    // Track vertical placement count per platform column for accounts and posts
    const accountCountsPerCol = new Array(totalPlatforms).fill(0);

    // --- ROW 3: Synthetic Accounts (Grouped cleanly by platform column) ---
    accountNodes.forEach((n) => {
      const col = accountColIndex.get(n.id) ?? 0;
      const countInCol = accountCountsPerCol[col]++;
      const colX = startX + col * (colWidth + colGap);
      const isBot = (n.bot_probability || 0) > 0.6;

      result.push({
        id: n.id,
        position: { x: colX, y: 340 + countInCol * 125 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.2, width: '100%', boxSizing: 'border-box' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.4 }}>
                <Chip
                  size="small"
                  label={isBot ? 'BOT CLUSTER' : 'VERIFIED ACCOUNT'}
                  sx={{
                    fontSize: '0.62rem',
                    height: 18,
                    bgcolor: isBot ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                    color: isBot ? '#FBBF24' : '#34D399',
                    fontWeight: 800,
                  }}
                />
                {n.bot_probability !== undefined && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: isBot ? '#F87171' : '#34D399',
                      fontWeight: 800,
                      fontFamily: 'monospace',
                    }}
                  >
                    {(n.bot_probability * 100).toFixed(0)}% Bot
                  </Typography>
                )}
              </Box>
              <Typography variant="body2" sx={{ fontWeight: 800, color: '#F9FAFB', fontSize: '0.82rem' }}>
                {n.handle || n.name || n.id}
              </Typography>
              <Typography variant="caption" sx={{ color: '#9CA3AF', fontSize: '0.7rem' }}>
                {isBot ? 'Automated Amplifier' : 'Legitimate Identity'}
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          width: cardWidth,
          backgroundColor: '#111827',
          border: `1.5px solid ${isBot ? '#F59E0B' : '#10B981'}`,
          borderRadius: 8,
          boxShadow: isBot ? '0 2px 10px rgba(245, 158, 11, 0.2)' : '0 2px 10px rgba(16, 185, 129, 0.2)',
          overflow: 'hidden',
          padding: 0,
        },
      });
    });

    // Track vertical placement count per platform column for posts
    const postCountsPerCol = new Array(totalPlatforms).fill(0);

    // --- ROW 4: Posts & Relays (Spaced comfortably below accounts) ---
    // Calculate the maximum height reached by accounts across all columns
    const maxAccountCount = Math.max(1, ...accountCountsPerCol);
    const postBaseY = Math.max(580, 340 + maxAccountCount * 125 + 40);

    postNodes.forEach((n) => {
      const col = postColIndex.get(n.id) ?? 0;
      const countInCol = postCountsPerCol[col]++;
      const colX = startX + col * (colWidth + colGap);

      result.push({
        id: n.id,
        position: { x: colX, y: postBaseY + countInCol * 135 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.2, width: '100%', boxSizing: 'border-box' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.4 }}>
                <Chip
                  size="small"
                  label={n.post_type || 'POST'}
                  sx={{
                    fontSize: '0.62rem',
                    height: 18,
                    bgcolor: 'rgba(139, 92, 246, 0.2)',
                    color: '#DDD6FE',
                    fontWeight: 800,
                  }}
                />
                <Typography variant="caption" sx={{ color: '#64748B', fontFamily: 'monospace' }}>
                  {n.id.substring(0, 11)}
                </Typography>
              </Box>
              <Typography
                variant="caption"
                sx={{
                  color: '#E2E8F0',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  lineHeight: 1.3,
                  mb: 0.5,
                  fontSize: '0.74rem',
                }}
              >
                {n.content_snippet || `Propagation artifact emitted across nodes...`}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.68rem' }}>
                  ❤️ {n.likes || 0}
                </Typography>
                <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.68rem' }}>
                  🔁 {n.reshares || 0}
                </Typography>
              </Box>
            </Box>
          ),
          raw: n,
        },
        style: {
          width: cardWidth,
          backgroundColor: '#1E1B4B',
          border: '1.5px solid #8B5CF6',
          borderRadius: 8,
          boxShadow: '0 2px 12px rgba(139, 92, 246, 0.25)',
          overflow: 'hidden',
          padding: 0,
        },
      });
    });

    return result;
  }, [filteredRawNodes]);

  // 3. Compute Clean, Smoothstep Edges with uncluttered styling
  const flowEdges: Edge[] = useMemo(() => {
    return rawEdges
      .filter((e) => activeNodeIds.has(e.source) && activeNodeIds.has(e.target))
      .map((e) => {
        const isCrossPlatform =
          e.type === 'CROSS_PLATFORM_SHARE' || (e.label && e.label.includes('CROSS_PLATFORM'));
        const isDerivative =
          e.type === 'CONTENT_VARIANT' || e.type === 'RESHARE' || e.type === 'QUOTE';
        const isStructural = e.type === 'DEPLOYED_ON' || e.type === 'HOSTS_ACCOUNT' || e.type === 'POSTED';

        let strokeColor = '#64748B';
        let strokeWidth = 1.5;
        let animated = false;

        if (isCrossPlatform) {
          strokeColor = '#F59E0B';
          strokeWidth = 2.4;
          animated = true;
        } else if (isDerivative) {
          strokeColor = '#A855F7';
          strokeWidth = 2.0;
          animated = true;
        } else if (isStructural) {
          strokeColor = '#38BDF8';
          strokeWidth = 1.6;
        }

        return {
          id: e.id,
          source: e.source,
          target: e.target,
          type: 'smoothstep',
          // Only show labels on action/propagation edges to prevent cluttering
          label: isCrossPlatform ? 'CROSS-PLATFORM' : isDerivative ? e.label : undefined,
          animated,
          style: { stroke: strokeColor, strokeWidth },
          labelStyle: { fill: '#FFF', fontSize: 9, fontWeight: 700 },
          labelBgStyle: { fill: '#090D16', fillOpacity: 0.95, rx: 4, ry: 4 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: strokeColor,
          },
        };
      });
  }, [rawEdges, activeNodeIds]);

  return (
    <Paper
      sx={{
        width: '100%',
        height: 680,
        backgroundColor: '#070B14',
        borderRadius: 3,
        border: '1px solid rgba(255, 255, 255, 0.08)',
        overflow: 'hidden',
        position: 'relative',
        // Dark theme overrides for React Flow controls, minimap & handles
        '& .react-flow__controls': {
          backgroundColor: '#0F172A',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6)',
        },
        '& .react-flow__controls-button': {
          backgroundColor: '#1E293B',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          fill: '#94A3B8',
          color: '#94A3B8',
          transition: 'all 0.15s ease',
          '&:hover': {
            backgroundColor: '#334155',
            fill: '#60A5FA',
          },
          '& svg': {
            fill: '#94A3B8',
          },
        },
        '& .react-flow__handle': {
          backgroundColor: '#38BDF8',
          border: '2px solid #0F172A',
          width: 8,
          height: 8,
          borderRadius: '50%',
        },
        '& .react-flow__node': {
          padding: 0,
        },
        '& .react-flow__attribution': {
          display: 'none',
        },
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
        fitViewOptions={{ padding: 0.18 }}
      >
        <Background color="#1E293B" gap={24} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(n) => (n.style?.borderColor as string) || '#38BDF8'}
          maskColor="rgba(0, 0, 0, 0.75)"
          style={{ backgroundColor: '#0F172A', border: '1px solid rgba(255,255,255,0.1)' }}
        />
      </ReactFlow>
    </Paper>
  );
};
