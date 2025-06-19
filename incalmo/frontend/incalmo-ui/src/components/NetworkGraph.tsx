import React, { useState, useEffect, useMemo, useCallback, useRef, MouseEvent } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Panel,
  Handle,
  Position,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Paper,
  Typography,
  Box,
  Chip,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Alert,
  Popover,
} from '@mui/material';
import {
  Computer,
  Security,
  Warning,
  Refresh,
  Info,
} from '@mui/icons-material';

import { Host, NetworkGraphProps, HostNodeProps } from '../types';

// Suppress ResizeObserver errors
const suppressResizeObserverError = () => {
  const resizeObserverErrorHandler = (e: ErrorEvent) => {
    if (e.message === 'ResizeObserver loop completed with undelivered notifications.') {
      e.stopImmediatePropagation();
    }
  };
  window.addEventListener('error', resizeObserverErrorHandler);
  return () => window.removeEventListener('error', resizeObserverErrorHandler);
};

const HostNode = React.memo(({ data }: HostNodeProps) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [showPopover, setShowPopover] = useState(false);

  const handleMouseEnter = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    setShowPopover(true);
  };

  const handleMouseLeave = () => {
    setShowPopover(false);
    setAnchorEl(null);
  };

  const getHostDisplayName = (host: Host) => {
    if (host.hostname && host.hostname.trim()) {
      return host.hostname;
    }
    if (host.ip_addresses && host.ip_addresses.length > 0) {
      const firstIp = host.ip_addresses[0];
      const lastOctet = firstIp.split('.').pop();
      return `Host-${lastOctet}`;
    }
    return 'Unknown-Host';
  };

  const displayName = getHostDisplayName(data);

  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: '#f44336',
          width: 8,
          height: 8,
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: '#4caf50',
          width: 8,
          height: 8,
        }}
      />
      <Card
        sx={{
          minWidth: 180,
          maxWidth: 220,
          border: data.infected ? '3px solid #f44336' : '3px solid #4caf50',
          backgroundColor: data.infected ? '#ffebee' : '#e8f5e9',
          cursor: 'pointer',
          transition: 'all 0.3s ease-in-out',
          position: 'relative',
          '&:hover': {
            boxShadow: 6,
            transform: 'scale(1.05)',
          },
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <CardContent sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            {data.infected ? (
              <Security color="error" sx={{ mr: 1, fontSize: 20 }} />
            ) : (
              <Computer color="success" sx={{ mr: 1, fontSize: 20 }} />
            )}
            <Typography variant="subtitle1" sx={{ flexGrow: 1, fontWeight: 'bold', color: data.infected ? '#630000' : '#1b5e20'  }}>
              {displayName}
            </Typography>
          </Box>

          <Typography 
            variant="caption" 
            sx={{ display: 'block', mb: 1, color: 'rgba(0, 0, 0, 0.87)' }} >
            {data.ip_addresses?.join(', ') || 'No IPs'}
          </Typography>

          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            <Chip
              label={data.infected ? 'Compromised' : 'Clean'}
              color={data.infected ? 'error' : 'success'}
              size="small"
            />
            {data.agents && data.agents.length > 0 && (
              <Chip
                label={`${data.agents.length} Agent${data.agents.length > 1 ? 's' : ''}`}
                color="primary"
                size="small"
              />
            )}
          </Box>
        </CardContent>
      </Card>

      <Popover
        open={showPopover}
        anchorEl={anchorEl}
        onClose={handleMouseLeave}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        sx={{ pointerEvents: 'none' }}
        disableRestoreFocus
      >
        <Card sx={{ maxWidth: 350, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            {displayName}
          </Typography>

          <Typography variant="body2" color="textSecondary" gutterBottom>
            <strong>IPs:</strong> {data.ip_addresses?.join(', ') || 'None'}
          </Typography>

          <Typography variant="body2" gutterBottom>
            <strong>Status:</strong>
            <Chip
              label={data.infected ? 'Compromised' : 'Clean'}
              color={data.infected ? 'error' : 'success'}
              size="small"
              sx={{ ml: 1 }}
            />
          </Typography>

          {data.infected_by && (
            <Typography variant="body2" color="error" gutterBottom>
              <strong>Infected by Agent:</strong> {data.infected_by}
            </Typography>
          )}

          {data.agents && data.agents.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" fontWeight="bold">Agents:</Typography>
              {data.agents.map((agentPaw, idx) => (
                <Typography key={idx} variant="caption" display="block" sx={{ ml: 1 }}>
                  • {agentPaw}
                </Typography>
              ))}
            </Box>
          )}

          {(!data.agents || data.agents.length === 0) && (
            <Typography variant="body2" color="textSecondary" gutterBottom>
              <strong>Agents:</strong> None
            </Typography>
          )}
        </Card>
      </Popover>
    </>
  );
});

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
  useEffect(() => {
    const cleanup = suppressResizeObserverError();
    return cleanup;
  }, []);

  // Generate a unique ID for each host
  const getHostId = (host: Host, index: number): string => {
    if (host.hostname && host.hostname.trim()) {
      return host.hostname;
    }
    if (host.ip_addresses && host.ip_addresses.length > 0) {
      return `host-${host.ip_addresses[0].replace(/\./g, '-')}`;
    }
    return `host-${index}`;
  };

  // Convert hosts to ReactFlow nodes with persistent positions
  const hostNodes = useMemo(() => {
    if (!hosts || hosts.length === 0) return [];

    return hosts.map((host, index) => {
      const hostId = getHostId(host, index);

      let position;
      if (nodePositions.has(hostId)) {
        position = nodePositions.get(hostId)!;
      } else {
        const angle = (index / hosts.length) * 2 * Math.PI;
        const radius = Math.max(200, hosts.length * 30);
        const centerX = 400;
        const centerY = 300;

        position = {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        };

        setNodePositions(prev => new Map(prev.set(hostId, position)));
      }

      return {
        id: hostId,
        type: 'hostNode',
        position,
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
  const infectionEdges = useMemo(() => {
    if (!hosts || hosts.length === 0) return [];

    const edges: Edge[] = [];

    hosts.forEach((targetHost, targetIndex) => {
      if (targetHost.infected && targetHost.infected_by) {
        const sourceHostIndex = hosts.findIndex(h =>
          h.agents && h.agents.includes(targetHost.infected_by!)
        );

        if (sourceHostIndex !== -1) {
          const sourceHost = hosts[sourceHostIndex];
          const sourceHostId = getHostId(sourceHost, sourceHostIndex);
          const targetHostId = getHostId(targetHost, targetIndex);

          if (sourceHostId !== targetHostId) {
            edges.push({
              id: `${sourceHostId}->${targetHostId}`,
              source: sourceHostId,
              target: targetHostId,
              type: 'smoothstep',
              animated: true,
              style: {
                stroke: '#f44336',
                strokeWidth: 4,
              },
              label: targetHost.infected_by,
              labelStyle: {
                fontSize: 12,
                fontWeight: 'bold',
                fill: '#f44336'
              },
              markerEnd: {
                type: 'arrowclosed',
                color: '#f44336',
              },
            } as Edge);
          }
        }
      }
    });

    return edges;
  }, [hosts]);

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

  const stats = useMemo(() => {
    const totalHosts = hosts?.length || 0;
    const infectedHosts = hosts?.filter(h => h.infected).length || 0;
    const cleanHosts = totalHosts - infectedHosts;
    const totalAgents = hosts?.reduce((sum, h) => sum + (h.agents?.length || 0), 0) || 0;

    return { totalHosts, infectedHosts, cleanHosts, totalAgents };
  }, [hosts]);

  // Don't render ReactFlow until we have initial data
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">Network Attack Graph</Typography>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip label={`${stats.totalHosts} Hosts`} color="default" size="small" />
          <Chip label={`${stats.infectedHosts} Infected`} color="error" size="small" />
          <Chip label={`${stats.cleanHosts} Clean`} color="success" size="small" />
          <Chip label={`${stats.totalAgents} Agents`} color="primary" size="small" />

          <Tooltip title="Refresh">
            <IconButton onClick={onRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

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
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          connectionLineType={ConnectionLineType.SmoothStep}
          fitView={nodes.length === 0}
          fitViewOptions={{ padding: 0.1 }}
          style={{ width: '100%', height: '100%' }} // Ensure ReactFlow fills the container
        >
          <Background />
          <Controls />
          <MiniMap
            nodeStrokeColor={(n) => n.data?.infected ? '#f44336' : '#4caf50'}
            nodeColor={(n) => n.data?.infected ? '#ffcdd2' : '#c8e6c9'}
            nodeBorderRadius={2}
          />

          <Panel position="top-left">
            <Box sx={{
              backgroundColor: 'rgba(255,255,255,0.9)',
              p: 1,
              borderRadius: 1,
              border: '1px solid #ddd'
            }}>
              <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                <Security color="error" sx={{ fontSize: 12, mr: 0.5 }} />
                Red = Compromised
              </Typography>
              <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                <Computer color="success" sx={{ fontSize: 12, mr: 0.5 }} />
                Green = Clean
              </Typography>
              <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                <Warning color="warning" sx={{ fontSize: 12, mr: 0.5 }} />
                Arrows = Infection Path
              </Typography>
              <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                <Info color="info" sx={{ fontSize: 12, mr: 0.5 }} />
                Hover for details
              </Typography>
            </Box>
          </Panel>
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