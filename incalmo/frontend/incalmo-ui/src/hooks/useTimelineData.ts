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
  const sortedLogs = [...highLevelLogs].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
  
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  // Map to track low level action node IDs by their action_id
  const lowLevelActionNodes: Record<string, string> = {};
  
  // Position tracking for low-level actions
  let xPosLow = 100;
  const xGapLow = 200; // horizontal gap between low-level action nodes
  const yPosLow = 100; // y-position for low-level actions
  
  // Position tracking for high-level actions
  let xPosHigh = 150; // offset slightly from low-level
  const xGapHigh = 400; // more space for high-level actions
  const yPosHigh = 300; // y-position for high-level actions
  const yGapEvents = 150; // vertical gap to events

  sortedLowLevelLogs.forEach((log, index) => {
    const actionId = `low-${log.low_level_action_id}`;
    lowLevelActionNodes[log.low_level_action_id] = actionId;
    
    // Format timestamp
    const timeString = new Date(log.timestamp).toLocaleTimeString();
    
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
  sortedLogs.forEach((log, index) => {
    const actionId = `high-${log.high_level_action_id}`;
    const eventsNodeId = `events-${log.high_level_action_id}`;
    
    // Format timestamp
    const timeString = new Date(log.timestamp).toLocaleTimeString();
    
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
      position: { x: xPosHigh, y: 100 + yPosHigh + yGapEvents },
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
      const prevActionId = `high-${sortedLogs[index-1].high_level_action_id}`;
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
      let eventXOffset = -100;
      const eventXGap = 200;

      // Convert action_results object to array of events
      const events: Event[] = Object.entries(log.action_results).map(([eventName, eventData]) => ({
        event_name: eventName,
        event_properties: eventData
      }));
      
      events.forEach((event, eventIndex) => {
        const eventId = `event-${log.high_level_action_id}-${eventIndex}`;
        
        // Add event node
        nodes.push({
          id: eventId,
          type: 'eventNode',
          position: { x: xPosHigh + eventXOffset, y: yPosHigh + yGapEvents * 2 },
          data: {...event}
        });
        
        // Connect events node to this event
        edges.push({
          id: `edge-${eventsNodeId}-${eventId}`,
          source: eventsNodeId,
          target: eventId,
          type: 'default'
        });
        
        eventXOffset += eventXGap;
      });
    }
    
    // Move x position for next action
    xPosHigh += xGapHigh;
  });
  
  return { nodes, edges };
};