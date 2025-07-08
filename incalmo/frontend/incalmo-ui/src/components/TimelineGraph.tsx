import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ReactFlowInstance,
  Panel,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Typography,
  Box,
  Alert,
  Chip,
} from '@mui/material';

import { TimelineGraphProps } from '../types';
import { useErrorSuppression } from '../hooks/useErrorSuppression';
import { useEventTimestamps } from '../hooks/useEventTimestamps';
import { useTimelineData } from '../hooks/useTimelineData';
import { DiscoveryNode, InfectionNode } from './TimelineNode';

const nodeTypes = {
  discoveryNode: DiscoveryNode,
  infectionNode: InfectionNode,
};

const TimelineGraph = ({ hosts, loading, error, lastUpdate, onRefresh }: TimelineGraphProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);
  
  const { eventTimestamps, recordEventTime } = useEventTimestamps();
  useErrorSuppression();
  
  // Generate timeline data
  const { nodes: timelineNodes, edges: timelineEdges } = useTimelineData({
    hosts,
    eventTimestamps,
    recordEventTime
  });
  
  // Update ReactFlow state when timeline data changes
  useEffect(() => {
    if (timelineNodes.length > 0) {
      setNodes(timelineNodes);
      setEdges(timelineEdges);
      
      if (!isInitialized && !loading) {
        setIsInitialized(true);
      }
      
      // Fit view when nodes change
      if (reactFlowInstance.current && isInitialized) {
        setTimeout(() => {
          reactFlowInstance.current?.fitView({ padding: 0.2, duration: 1000 });
        }, 100);
      }
    }
  }, [timelineNodes, timelineEdges, loading, setNodes, setEdges, isInitialized]);
  
  // Handle ReactFlow initialization
  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstance.current = instance;
    
    // Fit view on initialization
    setTimeout(() => {
      instance.fitView({ padding: 0.2 });
    }, 100);
  }, []);
  
  // Loading state
  if (!isInitialized && loading) {
    return (
      <Box sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%'
      }}>
        <Typography>Loading timeline data...</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: '100%'
    }}>

      {/* Error alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}

      {/* Last update info */}
      {lastUpdate && (
        <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
          Last updated: {lastUpdate} • Scroll horizontally to view entire timeline
        </Typography>
      )}

      {/* Timeline container */}
      <Box sx={{
        flex: 1,
        border: '1px solid #444',
        borderRadius: 1,
        minHeight: 0
      }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={onInit}
          nodeTypes={nodeTypes}
          fitView={true}
          fitViewOptions={{ padding: 0.2, duration: 800 }}
          style={{ width: '100%', height: '100%' }}
          proOptions={{ hideAttribution: true }}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Background color="#aaa" gap={16} />
          <Controls />
        </ReactFlow>
      </Box>

      {/* Empty state */}
      {(!hosts || hosts.length === 0) && !loading && (
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Typography color="textSecondary">
            No timeline data available. Start a strategy to see the attack timeline.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default TimelineGraph;