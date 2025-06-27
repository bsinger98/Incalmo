import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Node,
  Edge,
  NodeChange,
  Connection,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Typography,
  Box,
  Alert,
} from '@mui/material';

import { Host, NetworkGraphProps } from '../types';
import HostNode from './HostNode';
import NetworkGraphLegend from './NetworkGraphLegend';
import NetworkGraphHeader from './NetworkGraphHeader';
import NetworkGraphLoading from './NetworkGraphLoading';
import { useResizeObserverErrorSuppression } from '../hooks/useResizeObserverErrorSuppression';
import {
  getHostId,
  getTreeLayoutedElements,
  calculateNetworkStats,
  generateInfectionEdges,
} from '../utils/networkGraphUtils';

const nodeTypes = {
  hostNode: HostNode,
};

const NetworkGraph = ({ hosts, loading, error, lastUpdate, onRefresh }: NetworkGraphProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [nodePositions, setNodePositions] = useState<Map<string, { x: number; y: number }>>(new Map());
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Suppress ResizeObserver errors
  useResizeObserverErrorSuppression();

  // Convert hosts to ReactFlow nodes with persistent positions
  const hostNodes = useMemo(() => {
    if (!hosts || hosts.length === 0) return [];

    return hosts.map((host, index) => {
      const hostId = getHostId(host, index);

      return {
        id: hostId,
        type: 'hostNode',
        position: { x: 0, y: 0 },
        data: { ...host },
        draggable: true,
      } as Node<Host>;
    });
  }, [hosts, nodePositions]);

  const handleNodesChange = useCallback((changes: NodeChange[]) => {
    changes.forEach((change) => {
      if (change.type === 'position' && change.position) {
        setNodePositions(prev => new Map(prev.set(change.id, change.position!)));
      }
    });
    onNodesChange(changes);
  }, [onNodesChange]);

  // Convert infection relationships to ReactFlow edges
  const infectionEdges = useMemo(() => generateInfectionEdges(hosts || []), [hosts]);

  const [layoutedNodes, layoutedEdges] = useMemo(() => {
    if (!hostNodes.length) return [[], []];
    const layouted = getTreeLayoutedElements(hostNodes, infectionEdges);
    return [layouted, infectionEdges];
  }, [hostNodes, infectionEdges]);

  // Debounced update function
  const updateNodesAndEdges = useCallback((newNodes: Node<Host>[], newEdges: Edge[]) => {
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    updateTimeoutRef.current = setTimeout(() => {
      setNodes(newNodes);
      setEdges(newEdges);
    }, 100);
  }, [setNodes, setEdges]);

  // Update nodes and edges when hosts change
  useEffect(() => {
    if (!loading && hosts && hosts.length > 0) {
      updateNodesAndEdges(hostNodes, infectionEdges);
      setIsInitialized(true);
    }
  }, [hostNodes, infectionEdges, loading, updateNodesAndEdges]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const stats = useMemo(() => calculateNetworkStats(hosts || []), [hosts]);

  // Don't render ReactFlow until we have initial data
  if (!isInitialized && loading) {
    return <NetworkGraphLoading />;
  }

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: '100%'
    }}>
      <NetworkGraphHeader
        stats={stats}
        loading={loading}
        onRefresh={onRefresh}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}

      {lastUpdate && (
        <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
          Last updated: {lastUpdate} • Hover over nodes for details
        </Typography>
      )}

      <Box sx={{
        flex: 1, // Take up remaining space
        border: '1px solid #ddd',
        borderRadius: 1,
        overflow: 'hidden', // Prevent overflow
        minHeight: 0 // Critical for flexbox children to scroll properly
      }}>
        <ReactFlow
          nodes={layoutedNodes}
          edges={layoutedEdges}
          onNodesChange={handleNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView={layoutedNodes.length > 0}
          fitViewOptions={{ padding: 0.1 }}
          style={{ width: '100%', height: '100%' }}
          proOptions={{ hideAttribution: true }}
        >
          <Background />
          <Controls />
          <NetworkGraphLegend />
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