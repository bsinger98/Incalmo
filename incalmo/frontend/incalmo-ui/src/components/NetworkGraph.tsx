import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Panel,
  Connection,
  ReactFlowInstance,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Paper,
  Typography,
  Box,
  Alert,
} from '@mui/material';

import { NetworkGraphProps } from '../types';
import HostNode from './HostNode';
import NetworkGraphStats from './NetworkGraphStats';
import NetworkGraphLegend from './NetworkGraphLegend';
import { useNodePositions } from '../hooks/useNodePositions';
import { useErrorSuppression } from '../hooks/useErrorSuppression';
import { useGraphData } from '../hooks/useGraphData';
import { getTreeLayoutedElements, calculateNetworkStats } from '../utils/graphUtils';

const nodeTypes = {
  hostNode: HostNode,
};

const NetworkGraph = ({ hosts, loading, error, lastUpdate, onRefresh }: NetworkGraphProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);

  // Custom hooks for managing component state and behavior
  const { nodePositions, handleNodesChange } = useNodePositions();
  useErrorSuppression();

  // Transform hosts data into graph nodes and edges
  const { nodes: hostNodes, edges: infectionEdges } = useGraphData({
    hosts,
    nodePositions
  });

  // Apply layout algorithm to position nodes
  const [layoutedNodes, layoutedEdges] = useMemo(() => {
    if (!hostNodes.length) return [[], []];

    const allLayoutedNodes = getTreeLayoutedElements(hostNodes, infectionEdges, nodePositions);
    const finalNodes = allLayoutedNodes.map(node => {
      if (nodePositions.has(node.id)) {
        return {
          ...node,
          position: nodePositions.get(node.id)!
        };
      }
      return node;
    });

    return [finalNodes, infectionEdges];
  }, [hostNodes, infectionEdges, nodePositions]);

  // Update ReactFlow state when layout changes
  useEffect(() => {
    if (layoutedNodes.length > 0) {
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);

      if (!isInitialized && !loading) {
        setIsInitialized(true);
      }

      // Trigger fitView when nodes or edges change (after initialization)
      if (reactFlowInstance.current && isInitialized) {
        setTimeout(() => {
          reactFlowInstance.current?.fitView({ padding: 0.1, duration: 1000 });
        }, 100); // Small delay to ensure nodes are rendered
      }
    }
  }, [layoutedNodes, layoutedEdges, loading, setNodes, setEdges, isInitialized]);

  // Handle edge connections
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Handle node position changes
  const onNodesChangeHandler = useCallback((changes) => {
    handleNodesChange(changes, onNodesChange);
  }, [handleNodesChange, onNodesChange]);

  // Handle ReactFlow initialization
  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstance.current = instance;
  }, []);

  // Calculate network statistics
  const stats = useMemo(() => calculateNetworkStats(hosts), [hosts]);

  // Show loading state until initialized
  if (!isInitialized && loading) {
    return (
      <Paper sx={{ p: 3, mb: 3, height: 700 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <Typography>Loading network graph...</Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: '100%'
    }}>
      {/* Header with title and stats */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">Network Attack Graph</Typography>
        <NetworkGraphStats
          stats={stats}
          loading={loading}
          onRefresh={onRefresh}
        />
      </Box>

      {/* Error alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}

      {/* Last update info */}
      {lastUpdate && (
        <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
          Last updated: {lastUpdate} • Hover over nodes for details
        </Typography>
      )}

      {/* Main graph container */}
      <Box sx={{
        flex: 1,
        border: '1px solid #ddd',
        borderRadius: 1,
        overflow: 'hidden',
        minHeight: 0
      }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChangeHandler}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={onInit}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView={true}
          fitViewOptions={{ padding: 0.1, duration: 1000 }}
          style={{ width: '100%', height: '100%' }}
          proOptions={{ hideAttribution: true }}
        >
          <Background />
          <Controls />

          {/* Legend panel */}
          <Panel position="top-left">
            <NetworkGraphLegend />
          </Panel>
        </ReactFlow>
      </Box>

      {/* Empty state */}
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