import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Connection,
  ReactFlowInstance,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Typography,
  Box,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';

import { NetworkGraphProps } from '../types/components.types';
import HostNode from './HostNode';
import { useNodePositions } from '../hooks/useNodePositions';
import { useErrorSuppression } from '../hooks/useErrorSuppression';
import { useGraphData } from '../hooks/useGraphData';
import { getTreeLayoutedElements } from '../utils/graphUtils';

const nodeTypes = { hostNode: HostNode };

const NetworkGraph = ({ hosts, loading, error, lastUpdate, onRefresh }: NetworkGraphProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);
  const prevInfectedIds = useRef<string>('');
  const containerRef = useRef<HTMLDivElement>(null);

  const { nodePositions, handleNodesChange } = useNodePositions();
  // Keep a ref so the layout effect can read current positions without reacting to drags.
  const nodePositionsRef = useRef(nodePositions);
  useEffect(() => { nodePositionsRef.current = nodePositions; }, [nodePositions]);

  useErrorSuppression();

  // hostNodes and infectionEdges only change when host data changes, not on drag.
  const { nodes: hostNodes, edges: infectionEdges } = useGraphData({ hosts, nodePositions });

  // Layout only recomputes when actual host data changes (hostNodes/infectionEdges),
  // NOT when the user drags a node (nodePositions). Positions are applied from the ref.
  const layoutedNodes = useMemo(() => {
    if (!hostNodes.length) return [];
    const positions = nodePositionsRef.current;
    return getTreeLayoutedElements(hostNodes, infectionEdges, positions).map(node =>
      positions.has(node.id) ? { ...node, position: positions.get(node.id)! } : node
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hostNodes, infectionEdges]);

  // Apply layout to ReactFlow only when host data changes, never during drags.
  useEffect(() => {
    if (layoutedNodes.length > 0) {
      setNodes(layoutedNodes);
      if (!isInitialized && !loading) setIsInitialized(true);

      if (reactFlowInstance.current && isInitialized) {
        const infectedNodes = layoutedNodes.filter(n => n.data?.infected);
        const infectedKey = infectedNodes.map(n => n.id).sort().join(',');
        if (infectedKey !== prevInfectedIds.current) {
          prevInfectedIds.current = infectedKey;
          const targetNodes = infectedNodes.length > 0 ? infectedNodes : layoutedNodes;
          setTimeout(() => {
            reactFlowInstance.current?.fitView({ nodes: targetNodes, padding: 0.25, duration: 800 });
          }, 100);
        }
      }
    }
  }, [layoutedNodes, loading, setNodes, isInitialized]);

  // Edges update independently of node positions.
  useEffect(() => {
    setEdges(infectionEdges);
  }, [infectionEdges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodesChangeHandler = useCallback(
    (changes: Parameters<typeof onNodesChange>[0]) => handleNodesChange(changes, onNodesChange),
    [handleNodesChange, onNodesChange]
  );

  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstance.current = instance;
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!isFullscreen) containerRef.current?.requestFullscreen?.();
    else document.exitFullscreen?.();
  }, [isFullscreen]);

  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', handler);
    return () => document.removeEventListener('fullscreenchange', handler);
  }, []);

  if (!isInitialized && loading) {
    return (
      <Box sx={{ p: 3, height: 700, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography>Loading network graph...</Typography>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        display: 'flex', flexDirection: 'column', height: '100%', width: '100%',
        ...(isFullscreen && { background: '#fff', p: 2 }),
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">Network Attack Graph</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Refresh network graph">
            <span>
              <IconButton size="small" onClick={onRefresh} disabled={loading}>
                <Refresh />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
            <IconButton size="small" onClick={toggleFullscreen}>
              {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      {lastUpdate && (
        <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
          Last updated: {lastUpdate} • Hover over nodes for details
        </Typography>
      )}

      <Box sx={{ flex: 1, border: '1px solid #ddd', borderRadius: 1, overflow: 'hidden', minHeight: 0 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChangeHandler}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={onInit}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView
          fitViewOptions={{ padding: 0.25 }}
          style={{ width: '100%', height: '100%' }}
          proOptions={{ hideAttribution: true }}
        >
          <Background />
          <Controls />
        </ReactFlow>
      </Box>

      {(!hosts || hosts.length === 0) && !loading && (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Typography color="textSecondary">
            No hosts data available. Start a strategy to see the network graph.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default NetworkGraph;
