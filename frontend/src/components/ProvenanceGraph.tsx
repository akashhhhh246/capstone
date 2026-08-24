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
import { ProvenanceGraphResponse } from '../types';

interface ProvenanceGraphProps {
  data: ProvenanceGraphResponse;
  relationshipFilter?: string;
  onSelectNode?: (nodeData: any) => void;
}

export const ProvenanceGraph: React.FC<ProvenanceGraphProps> = ({
  data,
  relationshipFilter = 'ALL',
  onSelectNode,
}) => {
  const { nodes: rawNodes, edges: rawEdges } = data;

  // Filter nodes based on selected relationship filter
  const filteredNodes = useMemo(() => {
    if (relationshipFilter === 'ALL') return rawNodes;
    return rawNodes.filter((n) => {
      if (n.is_target) return true; // always keep target root
      if (n.relationship === relationshipFilter) return true;
      return false;
    });
  }, [rawNodes, relationshipFilter]);

  const activeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  // Clean, Centered Top-to-Bottom Tree Layout with Zero Collisions
  const flowNodes: Node[] = useMemo(() => {
    const rootNodes = filteredNodes.filter((n) => n.is_target);
    const nonRootNodes = filteredNodes.filter((n) => !n.is_target);

    const result: Node[] = [];
    const nodeWidth = 260;
    const spacing = 80;
    const count = Math.max(1, nonRootNodes.length);
    const totalRowWidth = count * nodeWidth + (count - 1) * spacing;
    const startX = 100;
    const rootX = startX + totalRowWidth / 2 - nodeWidth / 2;

    // Level 0: Root Node Centered at Top (y=60)
    rootNodes.forEach((n) => {
      result.push({
        id: n.id,
        position: { x: rootX, y: 60 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.5, width: nodeWidth - 30, textAlign: 'center' }}>
              <Chip
                size="small"
                label="👑 ORIGINAL ROOT SEED"
                sx={{ bgcolor: 'rgba(59, 130, 246, 0.25)', color: '#60A5FA', fontWeight: 800, mb: 0.8 }}
              />
              <Typography variant="body2" sx={{ fontWeight: 800, color: '#FFF', mb: 0.5 }}>
                {n.platform ? `Published on ${n.platform}` : 'Original Seed'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#D1D5DB',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  lineHeight: 1.4,
                }}
              >
                "{n.full_text || n.text}"
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#1E1B4B',
          border: '2px solid #3B82F6',
          borderRadius: 12,
          boxShadow: '0 0 24px rgba(59, 130, 246, 0.4)',
        },
      });
    });

    // Level 1: Derived Nodes Arranged in Balanced Row Below Root (y=320)
    nonRootNodes.forEach((n, idx) => {
      let borderColor = '#8B5CF6';
      let tagBg = 'rgba(139, 92, 246, 0.2)';
      let tagText = '#DDD6FE';
      let tagLabel = 'MUTATED VARIANT';

      const rel = n.relationship || 'PARAPHRASED_DERIVATIVE';
      const simPercent = Math.round((n.similarity || 0.7) * 100);

      if (rel === 'EXACT_COPY' || simPercent >= 95) {
        borderColor = '#10B981';
        tagBg = 'rgba(16, 185, 129, 0.2)';
        tagText = '#34D399';
        tagLabel = 'EXACT REPOST';
      } else if (rel === 'RELATED_NARRATIVE' || simPercent < 68) {
        borderColor = '#F59E0B';
        tagBg = 'rgba(245, 158, 11, 0.2)';
        tagText = '#FBBF24';
        tagLabel = 'RELATED THEME';
      }

      const posX = startX + idx * (nodeWidth + spacing);

      result.push({
        id: n.id,
        position: { x: posX, y: 320 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          label: (
            <Box sx={{ p: 1.2, width: nodeWidth - 30 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Chip
                  size="small"
                  label={tagLabel}
                  sx={{ fontSize: '0.65rem', height: 18, bgcolor: tagBg, color: tagText, fontWeight: 700 }}
                />
                <Typography variant="caption" sx={{ color: tagText, fontWeight: 800 }}>
                  {simPercent}% Match
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 600, display: 'block', mb: 0.5 }}>
                {n.platform ? `Platform: ${n.platform}` : 'Derivative'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#D1D5DB',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  lineHeight: 1.3,
                }}
              >
                "{n.full_text || n.text}"
              </Typography>
            </Box>
          ),
          raw: n,
        },
        style: {
          backgroundColor: '#111827',
          border: `1.5px solid ${borderColor}`,
          borderRadius: 10,
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        },
      });
    });

    return result;
  }, [filteredNodes]);

  // Clean Edges with Non-Overlapping Styling
  const flowEdges: Edge[] = useMemo(() => {
    return rawEdges
      .filter((e) => activeIds.has(e.source) && activeIds.has(e.target))
      .map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: '#60A5FA', strokeWidth: 2.2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#60A5FA',
        },
      }));
  }, [rawEdges, activeIds]);

  return (
    <Paper
      sx={{
        width: '100%',
        height: 580,
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
        fitViewOptions={{ padding: 0.35, maxZoom: 1.1 }}
      >
        <Background color="#1E293B" gap={20} />
        <Controls style={{ backgroundColor: '#111827', borderColor: 'rgba(255,255,255,0.1)', color: '#FFF' }} />
        <MiniMap
          nodeColor={(n) => (n.style?.borderColor as string) || '#3B82F6'}
          maskColor="rgba(0, 0, 0, 0.75)"
          style={{ backgroundColor: '#0F172A', border: '1px solid rgba(255,255,255,0.1)' }}
        />
      </ReactFlow>
    </Paper>
  );
};
