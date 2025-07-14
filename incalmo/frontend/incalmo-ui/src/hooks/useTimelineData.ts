import { Node, Edge } from 'reactflow';
import { HighLevelLogEntry, LowLevelLogEntry, Event } from '../types';

interface TimelineData {
  nodes: Node[];
  edges: Edge[];
}

export const createTimelineFromLogs = (highLevelLogs: HighLevelLogEntry[], lowLevelLogs: LowLevelLogEntry[]): TimelineData => {
  // Sort logs by timestamp
  const sortedLowLevelLogs = [...lowLevelLogs].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
  const sortedHighLevelLogs = [...highLevelLogs].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
  
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  // Map to track low level action node IDs by their action_id
  const lowLevelActionNodes: Record<string, string> = {};
  
  // Position tracking for low-level actions
  let xPosLow = 100;
  const xGapLow = 200; 
  const yPosLow = 100; 
  
  // Position tracking - vertical spacing
  let lastHighLevelX = 100; // Track last high level position
  const xGapHigh = 400;
  const yPosHigh = 300;
  const yGapEvents = 150;
  const yGapEventsNode = 100;
  
  const lowLevelPositions: Record<string, number> = {};
 
  sortedLowLevelLogs.forEach((log, index) => {
    const actionId = `low-${log.low_level_action_id}`;
    lowLevelActionNodes[log.low_level_action_id] = actionId;
    lowLevelPositions[log.low_level_action_id] = xPosLow;

    // Add the low-level action node
    nodes.push({
      id: actionId,
      type: 'lowLevelActionNode',
      position: { x: xPosLow, y: yPosLow },
      data: {...log}
    });
    
    xPosLow += xGapLow;
  });
  
  // Process each high-level action log
  sortedHighLevelLogs.forEach((log, index) => {
    const actionId = `high-${log.high_level_action_id}`;
    const eventsNodeId = `events-${log.high_level_action_id}`;

    // Find all related low level node positions
    const relatedNodePositions = log.low_level_action_ids
      .map(id => lowLevelPositions[id])
      .filter(pos => pos !== undefined);
    
    let xPosHigh;
    if (relatedNodePositions.length > 0) {
      const minX = Math.min(...relatedNodePositions);
      const maxX = Math.max(...relatedNodePositions);
      xPosHigh = minX + (maxX - minX) / 2;
      xPosHigh = Math.max(xPosHigh, lastHighLevelX + xGapHigh);
    }else {
      xPosHigh = lastHighLevelX + xGapHigh;
    }
    
    // Add the high-level action node
    console.log('Adding High Level Log Node:', log);
    nodes.push({
      id: actionId,
      type: 'highLevelActionNode',
      position: { x: xPosHigh, y: yPosHigh },
      data: { ...log }
    });
    
    // Add the "Events generated" node below it
    nodes.push({
      id: eventsNodeId,
      type: 'eventsGeneratedNode',
      position: { x: xPosHigh, y: 100 + yPosHigh + yGapEventsNode },
      data: {}
    });
    
    // Connect action node to events node
    edges.push({
      id: `edge-${actionId}-${eventsNodeId}`,
      source: actionId,
      target: eventsNodeId,
      sourceHandle: 'events',
      label: 'Events',
      type: 'default'
    });
    
    // Connect with previous action if not the first one
    if (index > 0) {
      const prevActionId = `high-${sortedHighLevelLogs[index-1].high_level_action_id}`;
      edges.push({
        id: `edge-${prevActionId}-${actionId}`,
        source: prevActionId,
        target: actionId,
        sourceHandle: 'right',
        targetHandle: 'left',
        animated: true,
        type: 'smoothstep'
      });
    }

    // Connect high-level action to its low-level actions
    log.low_level_action_ids.forEach(lowLevelId => {
      const lowNodeId = lowLevelActionNodes[lowLevelId];
      if (lowNodeId) {
        edges.push({
          id: `edge-${actionId}-${lowNodeId}`,
          target: actionId,
          source: lowNodeId,
          type: 'default',
        });
      }
    });
    
    // Process individual events
    if (log.action_results) {
      // Convert action_results object to array of events
      const events: Event[] = Object.entries(log.action_results).map(([eventName, eventData]) => ({
        event_name: eventName,
        event_properties: eventData
      }));

      const eventCount = events.length;
      const eventTotalWidth = Math.max(400, eventCount * 150);
      const eventStart = xPosHigh - (eventTotalWidth / 2);
      const eventGap = eventTotalWidth / Math.max(1, eventCount - 1);
      
      events.forEach((event, eventIndex) => {
        const eventId = `event-${log.high_level_action_id}-${eventIndex}`;
        const xPosEvent = eventCount === 1 ? xPosHigh : eventStart + (eventGap * eventIndex);
        
        // Add event node
        nodes.push({
          id: eventId,
          type: 'eventNode',
          position: { x: xPosEvent, y: 100 + yPosHigh + yGapEventsNode + yGapEvents},
          data: {...event}
        });
        
        // Connect events node to this event
        edges.push({
          id: `edge-${eventsNodeId}-${eventId}`,
          source: eventsNodeId,
          target: eventId,
          type: 'default'
        });
        
      });
    }

  });
  
  return { nodes, edges };
};