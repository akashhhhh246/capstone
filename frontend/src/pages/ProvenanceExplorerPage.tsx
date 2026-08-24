import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  Paper,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Chip,
  Tabs,
  Tab,
  ButtonGroup,
  Button,
  Divider,
} from '@mui/material';
import {
  GitBranch,
  Clock,
  User,
  Share2,
  Layers,
  Compass,
  Network,
  Sparkles,
  ArrowDown,
  Copy,
  FileText,
} from 'lucide-react';
import { api } from '../services/api';
import { ProvenanceGraphResponse, ContentItem } from '../types';
import { ProvenanceGraph } from '../components/ProvenanceGraph';
import { DisclaimerAlert } from '../components/DisclaimerAlert';

export const ProvenanceExplorerPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialContentId = searchParams.get('contentId') || '';

  const [contents, setContents] = useState<ContentItem[]>([]);
  const [selectedContentId, setSelectedContentId] = useState<string>(initialContentId);
  const [graphData, setGraphData] = useState<ProvenanceGraphResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<number>(0);
  const [relationFilter, setRelationFilter] = useState<string>('ALL');

  useEffect(() => {
    const fetchContents = async () => {
      try {
        const list = await api.listContents(25);
        setContents(list);
        if (!selectedContentId && list.length > 0) {
          setSelectedContentId(list[0].id);
        }
      } catch (e) {
        console.error('Failed to load content list:', e);
      }
    };
    fetchContents();
  }, []);

  useEffect(() => {
    if (!selectedContentId) return;
    setSearchParams({ contentId: selectedContentId });
    const fetchProvenance = async () => {
      try {
        setLoading(true);
        const data = await api.getProvenanceGraph(selectedContentId);
        setGraphData(data);
        setSelectedNode(null);
      } catch (e) {
        console.error('Failed to load provenance DAG:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchProvenance();
  }, [selectedContentId]);

  // Extract root seed content node
  const rootNode = useMemo(() => {
    if (!graphData) return null;
    return graphData.nodes.find((n) => n.is_target) || graphData.nodes[0] || null;
  }, [graphData]);

  // Extract only derived variants (excluding the target root itself)
  const contentDerivatives = useMemo(() => {
    if (!graphData) return [];
    return graphData.nodes.filter((n) => !n.is_target);
  }, [graphData]);

  const exactCopies = useMemo(
    () => contentDerivatives.filter((n) => n.relationship === 'EXACT_COPY' || (n.similarity && n.similarity >= 0.95)),
    [contentDerivatives]
  );
  const paraphrasedVariants = useMemo(
    () =>
      contentDerivatives.filter(
        (n) => n.relationship === 'PARAPHRASED_DERIVATIVE' || (n.similarity && n.similarity >= 0.68 && n.similarity < 0.95)
      ),
    [contentDerivatives]
  );
  const relatedNarratives = useMemo(
    () => contentDerivatives.filter((n) => !exactCopies.includes(n) && !paraphrasedVariants.includes(n)),
    [contentDerivatives, exactCopies, paraphrasedVariants]
  );

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#F9FAFB' }}>
            Content Provenance & Lineage Tracker
          </Typography>
          <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
            Track where stories originated, identify word-for-word mirrors, and detect AI-mutated narrative variants.
          </Typography>
        </Box>

        {/* Content Ingestion Selector */}
        <Box sx={{ minWidth: 280 }}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ color: '#9CA3AF' }}>Select Ingested Content</InputLabel>
            <Select
              value={selectedContentId}
              label="Select Ingested Content"
              onChange={(e) => setSelectedContentId(e.target.value)}
              sx={{
                backgroundColor: '#111827',
                color: '#FFF',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.1)' },
              }}
            >
              {contents.map((c) => (
                <MenuItem key={c.id} value={c.id}>
                  {c.raw_text.substring(0, 42)}... ({c.id.substring(0, 8)})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Safety Notice */}
      <DisclaimerAlert type="privacy" />

      {/* Executive Provenance Story Box (Plain English) */}
      <Paper
        sx={{
          p: 2.5,
          mb: 3,
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: 2.5,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <Compass size={20} color="#60A5FA" />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#F9FAFB' }}>
            Lineage Summary & Narrative Origin
          </Typography>
          {graphData && (
            <Chip
              size="small"
              label={`${contentDerivatives.length} Mutated Derivatives Found`}
              sx={{ bgcolor: 'rgba(59, 130, 246, 0.2)', color: '#93C5FD', fontWeight: 700 }}
            />
          )}
        </Box>
        <Typography variant="body2" sx={{ color: '#D1D5DB', lineHeight: 1.6 }}>
          {rootNode
            ? `Target text registered in repository. Identified ${paraphrasedVariants.length} paraphrased AI variants, ${exactCopies.length} word-for-word mirrors, and ${relatedNarratives.length} related thematic narratives.`
            : 'Select a content entry above to view its provenance lineage.'}
        </Typography>
      </Paper>

      {/* View Switcher: Step-by-Step Story vs Interactive Graph */}
      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.08)', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, val) => setActiveTab(val)}
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab
            label="1. Visual Lineage Tree & Mutation Comparison (Easy to Read)"
            icon={<Compass size={18} />}
            iconPosition="start"
            sx={{ fontWeight: 700, textTransform: 'none', color: '#D1D5DB' }}
          />
          <Tab
            label="2. Interactive Lineage Graph Canvas"
            icon={<Network size={18} />}
            iconPosition="start"
            sx={{ fontWeight: 700, textTransform: 'none', color: '#D1D5DB' }}
          />
        </Tabs>
      </Box>

      {/* TAB 1: Visual Lineage Story & Side-by-Side Comparison */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={selectedNode ? 8 : 12}>
            {loading ? (
              <Paper sx={{ p: 6, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <CircularProgress />
              </Paper>
            ) : rootNode ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* 1. ORIGINAL SEED ROOT */}
                <Paper
                  sx={{
                    p: 3,
                    backgroundColor: '#0F172A',
                    border: '2px solid #3B82F6',
                    borderRadius: 2.5,
                    boxShadow: '0 0 20px rgba(59, 130, 246, 0.2)',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Chip
                        label="👑 ORIGINAL SEED CONTENT"
                        sx={{ bgcolor: 'rgba(59, 130, 246, 0.25)', color: '#60A5FA', fontWeight: 800 }}
                      />
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                        ID: {rootNode.id}
                      </Typography>
                    </Box>
                    <Chip
                      size="small"
                      label="100% Original Source"
                      sx={{ bgcolor: 'rgba(59, 130, 246, 0.2)', color: '#93C5FD', fontWeight: 700 }}
                    />
                  </Box>

                  <Typography variant="body1" sx={{ color: '#F9FAFB', fontWeight: 600, fontSize: '0.95rem', mb: 1.5, lineHeight: 1.6 }}>
                    "{rootNode.full_text || rootNode.text}"
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    {rootNode.platform && (
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                        Origin Platform: <strong>{rootNode.platform}</strong>
                      </Typography>
                    )}
                    {rootNode.created_at && (
                      <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                        Registered: <strong>{new Date(rootNode.created_at).toLocaleString()}</strong>
                      </Typography>
                    )}
                  </Box>
                </Paper>

                {/* Downward Lineage Flow Arrow (if derivatives exist) */}
                {contentDerivatives.length > 0 && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: -1 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        px: 2,
                        py: 0.5,
                        borderRadius: 4,
                        bgcolor: '#1E293B',
                        border: '1px solid rgba(255,255,255,0.1)',
                      }}
                    >
                      <ArrowDown size={16} color="#60A5FA" />
                      <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 700 }}>
                        Mutations & Text Paraphrases Detected
                      </Typography>
                    </Box>
                  </Box>
                )}

                {/* 2. PARAPHRASED MUTATIONS SECTION */}
                {paraphrasedVariants.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#DDD6FE', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      🧬 Paraphrased & Mutated Variants ({paraphrasedVariants.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {paraphrasedVariants.map((item) => (
                        <Paper
                          key={item.id}
                          onClick={() => setSelectedNode(item)}
                          sx={{
                            p: 2.5,
                            backgroundColor: '#111827',
                            border: '1.5px solid #8B5CF6',
                            borderRadius: 2,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                            '&:hover': {
                              transform: 'translateX(4px)',
                              boxShadow: '0 0 16px rgba(139, 92, 246, 0.25)',
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Chip
                                size="small"
                                label="MUTATED VARIANT"
                                sx={{ bgcolor: 'rgba(139, 92, 246, 0.2)', color: '#DDD6FE', fontWeight: 700 }}
                              />
                              <Typography variant="caption" sx={{ color: '#9CA3AF' }}>
                                Platform: {item.platform || 'SimuTelegram'}
                              </Typography>
                            </Box>
                            <Chip
                              size="small"
                              label={`${item.similarity ? Math.round(item.similarity * 100) : 80}% Semantic Match`}
                              sx={{ bgcolor: 'rgba(139, 92, 246, 0.25)', color: '#C4B5FD', fontWeight: 800 }}
                            />
                          </Box>
                          <Typography variant="body2" sx={{ color: '#E5E7EB', lineHeight: 1.5 }}>
                            "{item.full_text || item.text}"
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* 3. EXACT REPOSTS & ECHOES SECTION */}
                {exactCopies.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#34D399', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      🔁 Exact Reposts & Direct Mirrors ({exactCopies.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {exactCopies.map((item) => (
                        <Paper
                          key={item.id}
                          onClick={() => setSelectedNode(item)}
                          sx={{
                            p: 2.5,
                            backgroundColor: '#111827',
                            border: '1.5px solid #10B981',
                            borderRadius: 2,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                            '&:hover': {
                              transform: 'translateX(4px)',
                              boxShadow: '0 0 16px rgba(16, 185, 129, 0.25)',
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Chip
                              size="small"
                              label="EXACT REPOST"
                              sx={{ bgcolor: 'rgba(16, 185, 129, 0.2)', color: '#34D399', fontWeight: 700 }}
                            />
                            <Chip
                              size="small"
                              label="100% Match"
                              sx={{ bgcolor: 'rgba(16, 185, 129, 0.25)', color: '#6EE7B7', fontWeight: 800 }}
                            />
                          </Box>
                          <Typography variant="body2" sx={{ color: '#E5E7EB', lineHeight: 1.5 }}>
                            "{item.full_text || item.text}"
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* 4. BROADER RELATED NARRATIVES */}
                {relatedNarratives.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#FBBF24', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      🌐 Thematically Related Narratives ({relatedNarratives.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {relatedNarratives.map((item) => (
                        <Paper
                          key={item.id}
                          onClick={() => setSelectedNode(item)}
                          sx={{
                            p: 2.5,
                            backgroundColor: '#111827',
                            border: '1.5px solid #F59E0B',
                            borderRadius: 2,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                            '&:hover': {
                              transform: 'translateX(4px)',
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Chip
                              size="small"
                              label="RELATED THEME"
                              sx={{ bgcolor: 'rgba(245, 158, 11, 0.2)', color: '#FBBF24', fontWeight: 700 }}
                            />
                            <Typography variant="caption" sx={{ color: '#FBBF24', fontWeight: 700 }}>
                              {item.similarity ? `${Math.round(item.similarity * 100)}% Match` : 'Related'}
                            </Typography>
                          </Box>
                          <Typography variant="body2" sx={{ color: '#D1D5DB' }}>
                            "{item.full_text || item.text}"
                          </Typography>
                        </Paper>
                      ))}
                    </Box>
                  </Box>
                )}

                {/* If this content is standalone without mutations */}
                {contentDerivatives.length === 0 && (
                  <Paper sx={{ p: 3, textAlign: 'center', backgroundColor: '#111827', border: '1px dashed rgba(255,255,255,0.15)', borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ color: '#9CA3AF' }}>
                      This content is an independent, standalone submission. No derivative mutations or cross-platform copies were detected in the database.
                    </Typography>
                  </Paper>
                )}
              </Box>
            ) : (
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#6B7280' }}>
                  No provenance relationships found for this content.
                </Typography>
              </Paper>
            )}
          </Grid>

          {/* Side-by-Side Comparison Inspector Drawer */}
          {selectedNode && rootNode && (
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, border: '1.5px solid #60A5FA', borderRadius: 2.5, position: 'sticky', top: 80 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#60A5FA', mb: 2 }}>
                  Side-by-Side Mutation Comparison
                </Typography>

                {/* Original Root Text Preview */}
                <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 700, textTransform: 'uppercase' }}>
                  Original Seed Root:
                </Typography>
                <Paper sx={{ p: 1.8, backgroundColor: '#090D16', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: 2, my: 1 }}>
                  <Typography variant="body2" sx={{ color: '#E0F2FE', fontSize: '0.85rem' }}>
                    "{rootNode.full_text || rootNode.text}"
                  </Typography>
                </Paper>

                {/* Selected Mutation Preview */}
                <Typography variant="caption" sx={{ color: '#C4B5FD', fontWeight: 700, textTransform: 'uppercase', mt: 2, display: 'block' }}>
                  Selected Mutation Variant ({selectedNode.platform || 'Platform'}):
                </Typography>
                <Paper sx={{ p: 1.8, backgroundColor: '#090D16', border: '1px solid rgba(139, 92, 246, 0.4)', borderRadius: 2, my: 1 }}>
                  <Typography variant="body2" sx={{ color: '#EDE9FE', fontSize: '0.85rem' }}>
                    "{selectedNode.full_text || selectedNode.text}"
                  </Typography>
                </Paper>

                {/* Similarity Match */}
                {selectedNode.similarity !== undefined && (
                  <Box sx={{ mt: 2, p: 1.5, borderRadius: 2, backgroundColor: '#1E293B', textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Semantic Match Score</Typography>
                    <Typography variant="h5" sx={{ color: '#34D399', fontWeight: 800, fontFamily: 'monospace' }}>
                      {(selectedNode.similarity * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                )}

                <Button
                  fullWidth
                  size="small"
                  variant="outlined"
                  onClick={() => setSelectedNode(null)}
                  sx={{ mt: 2, color: '#9CA3AF', borderColor: 'rgba(255,255,255,0.1)' }}
                >
                  Close Comparison
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* TAB 2: Interactive Lineage Graph */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={selectedNode ? 8 : 12}>
            <Paper sx={{ p: 2.5 }}>
              {/* Relationship Filter Buttons */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" sx={{ color: '#9CA3AF', fontWeight: 600 }}>
                    Filter Tier:
                  </Typography>
                  <ButtonGroup size="small" variant="outlined">
                    {[
                      { label: 'ALL', val: 'ALL' },
                      { label: 'Exact Reposts', val: 'EXACT_COPY' },
                      { label: 'Paraphrased', val: 'PARAPHRASED_DERIVATIVE' },
                      { label: 'Related', val: 'RELATED_NARRATIVE' },
                    ].map((f) => (
                      <Button
                        key={f.val}
                        onClick={() => setRelationFilter(f.val)}
                        variant={relationFilter === f.val ? 'contained' : 'outlined'}
                        sx={{ fontSize: '0.75rem' }}
                      >
                        {f.label}
                      </Button>
                    ))}
                  </ButtonGroup>
                </Box>
                <Typography variant="caption" sx={{ color: '#6B7280' }}>
                  Hierarchy: Root Seed ──► Reposts ──► Paraphrases ──► Related
                </Typography>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 580 }}>
                  <CircularProgress />
                </Box>
              ) : graphData && graphData.nodes.length > 0 ? (
                <ProvenanceGraph
                  data={graphData}
                  relationshipFilter={relationFilter}
                  onSelectNode={(node) => setSelectedNode(node)}
                />
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 580 }}>
                  <Typography variant="body2" sx={{ color: '#6B7280' }}>
                    No provenance relationships found for this content.
                  </Typography>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Node Inspector Drawer */}
          {selectedNode && (
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#60A5FA', mb: 2 }}>
                  Selected Node Inspector
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Node Classification:</Typography>
                  <Typography variant="h6" sx={{ color: '#F3F4F6', fontWeight: 700 }}>
                    {selectedNode.is_target ? '👑 Original Root Seed' : selectedNode.relationship?.replace('_', ' ') || 'Derivative Variant'}
                  </Typography>
                </Box>

                {selectedNode.platform && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Publishing Platform:</Typography>
                    <Typography variant="body1" sx={{ color: '#60A5FA', fontWeight: 600 }}>
                      {selectedNode.platform}
                    </Typography>
                  </Box>
                )}

                {selectedNode.full_text && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Full Text Content:</Typography>
                    <Paper sx={{ p: 1.5, backgroundColor: '#090D16', color: '#E5E7EB', fontSize: '0.85rem', mt: 0.5 }}>
                      "{selectedNode.full_text}"
                    </Paper>
                  </Box>
                )}

                {selectedNode.similarity !== undefined && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#9CA3AF' }}>Semantic Similarity:</Typography>
                    <Typography variant="h5" sx={{ color: '#34D399', fontWeight: 800, fontFamily: 'monospace' }}>
                      {(selectedNode.similarity * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
};
