import { useMemo } from 'react';
import { Node, Edge, Position } from 'reactflow';
import { Host } from '../types';
import { getHostId } from '../utils/graphUtils';

interface UseTimelineDataProps {
  hosts: Host[];
  eventTimestamps: Map<string, Date>;
  recordEventTime: (eventId: string, time?: Date) => void;
}

export const useTimelineData = ({ hosts, eventTimestamps, recordEventTime }: UseTimelineDataProps) => {
  const { nodes, edges } = useMemo(() => {
    if (!hosts || hosts.length === 0) return { nodes: [], edges: [] };

    const timelineNodes: Node[] = [];
    const timelineEdges: Edge[] = [];
    let lastNodeId = '';
    let xPosition = 0;
    const xIncrement = 250; // Horizontal spacing between nodes
    const baseY = 100;      // Vertical position

    // First, add a "start" node
    const startId = 'timeline-start';
    
    // Record timestamp for start if not already recorded
    recordEventTime(startId);
    const startTime = eventTimestamps.get(startId) || new Date();
    
    lastNodeId = startId;
    xPosition += xIncrement;
    
    hosts.forEach((host, index) => {
      const hostId = getHostId(host, index);
      
      // Host discovery event
      const discoveryId = `discovery-${hostId}`;
      
      // Record timestamp if not already recorded
      recordEventTime(discoveryId);
      const discoveryTime = eventTimestamps.get(discoveryId) || new Date();
      
      timelineNodes.push({
        id: discoveryId,
        type: 'discoveryNode',
        data: { 
          label: `${hostId} Discovered`,
          host,
          time: discoveryTime.toLocaleTimeString(),
        },
        position: { x: xPosition, y: baseY },
        draggable: false,
        // sourcePosition: Position.Left,
        // targetPosition: Position.Right
      });
      
      // Add edge from previous node
      timelineEdges.push({
        id: `edge-${lastNodeId}-${discoveryId}`,
        source: lastNodeId,
        target: discoveryId,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#2196f3', strokeWidth: 2 },
      });
      
      lastNodeId = discoveryId;
      xPosition += xIncrement;
      
      if (host.infected) {
        const infectionId = `infection-${hostId}`;

        recordEventTime(infectionId);
        const infectionTime = eventTimestamps.get(infectionId) || new Date();
        
        timelineNodes.push({
          id: infectionId,
          type: 'infectionNode',
          data: { 
            label: `${hostId} Infected`,
            host,
            time: infectionTime.toLocaleTimeString(),
          },
          position: { x: xPosition, y: baseY },
          draggable: false,
        });
        
        timelineEdges.push({
          id: `edge-${lastNodeId}-${infectionId}`,
          source: lastNodeId,
          target: infectionId,
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#f44336', strokeWidth: 2 },
        });
        
        lastNodeId = infectionId;
        xPosition += xIncrement;
      }
    });
    
    return { nodes: timelineNodes, edges: timelineEdges };
  }, [hosts, eventTimestamps, recordEventTime]);

  return { nodes, edges };
};