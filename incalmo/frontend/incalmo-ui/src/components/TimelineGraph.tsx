import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ReactFlowInstance,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';

import { TimelineGraphProps } from '../types/components.types';
import { createTimelineFromLogs } from '../hooks/useTimelineData';
import { HighLevelActionNode, LowLevelActionNode, EventsGeneratedNode, EventNode } from './TimelineNode';

const nodeTypes = {
  highLevelActionNode: HighLevelActionNode,
  lowLevelActionNode: LowLevelActionNode,
  eventsGeneratedNode: EventsGeneratedNode,
  eventNode: EventNode,
};

const TimelineGraph = ({ highLevelLogs, lowLevelLogs }: TimelineGraphProps) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const reactFlowInstance = useRef<ReactFlowInstance | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Generate timeline data when logs change
  useEffect(() => {
    if ((highLevelLogs && highLevelLogs.length > 0) || (lowLevelLogs && lowLevelLogs.length > 0)) {
      setLoading(true);
      try {
        const { nodes: timelineNodes, edges: timelineEdges } = createTimelineFromLogs(highLevelLogs, lowLevelLogs);
        setNodes(timelineNodes);
        setEdges(timelineEdges);
        
        // Fit view when nodes change
        if (reactFlowInstance.current) {
          setTimeout(() => {
            reactFlowInstance.current?.fitView({ padding: 0.2, duration: 800 });
          }, 100);
        }
      } catch (error) {
        console.error('Error creating timeline:', error);
      } finally {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, [highLevelLogs, lowLevelLogs, setNodes, setEdges]);
  
  // Handle ReactFlow initialization
  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstance.current = instance;
    
    // Fit view on initialization
    setTimeout(() => {
      instance.fitView({ padding: 0.2 });
      setLoading(false);
    }, 100);
  }, []);
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Building timeline...</Typography>
      </Box>
    );
  }

  if ((!highLevelLogs || highLevelLogs.length === 0) && (!lowLevelLogs || lowLevelLogs.length === 0)) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography>No timeline data available yet. Start a strategy to see the attack timeline.</Typography>
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
          fitViewOptions={{ padding: 0.2, duration: 1000 }}
          style={{ width: '100%', height: '100%' }}
          proOptions={{ hideAttribution: true }}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={true}
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Background color="#aaa" gap={16} />
          <Controls />
        </ReactFlow>
      </Box>
    </Box>
  );
};

export default TimelineGraph;