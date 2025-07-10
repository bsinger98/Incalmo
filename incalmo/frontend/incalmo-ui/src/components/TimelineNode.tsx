import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography, Tooltip } from '@mui/material';

// Node for high-level actions
export const HighLevelActionNode = ({ data }) => (
  <Box sx={{
    padding: '10px',
    borderRadius: '4px',
    backgroundColor: '#e3f2fd',
    border: '3px solid #2196f3',
    width: 200,
  }}>
    <Handle type="target" position={Position.Top} />
    <Handle type="target" position={Position.Left} id = "left"/>
    <Typography variant="subtitle2" sx={{ 
        color: '#0d47a1',
        fontWeight: 'bold',
    }}>{data.label}</Typography>
    <Typography variant="caption" sx={{ 
        color: '#0d47a1',
        fontWeight: 'normal',
        display: 'block'
    }}>Completed at {data.time}</Typography>
    <Handle type="source" position={Position.Right} id = "right"/>
    <Handle type="source" position={Position.Bottom} id="events" />
  </Box>
);

// Node for Low-level actions
export const LowLevelActionNode = ({ data }) => (
  <Tooltip 
  title={
    <Box>
      <Typography variant="subtitle2">Parameters:</Typography>
      <pre style={{ maxHeight: '200px', overflow: 'auto' }}>
        {JSON.stringify(data.params, null, 2)}
      </pre>
      {data.results && (
        <>
          <Typography variant="subtitle2">Results:</Typography>
          <pre style={{ maxHeight: '200px', overflow: 'auto' }}>
            {JSON.stringify(data.results, null, 2)}
          </pre>
        </>
      )}
    </Box>
  } 
  placement="top"
  >
    <Box sx={{
      padding: '8px',
      borderRadius: '4px',
      backgroundColor: '#e8f5e9',
      border: '2px solid #4caf50',
      width: 180,
    }}>
      <Typography variant="body2" sx={{ 
          color: '#2e7d32',
          fontWeight: 'bold',
          fontSize: '0.8rem'
      }}>{data.label}</Typography>
      <Typography variant="caption" sx={{ 
          color: '#2e7d32',
          fontSize: '0.7rem',
          display: 'block'
      }}>{data.time}</Typography>
      <Handle type="source" position={Position.Bottom} />
    </Box>
  </Tooltip>
);

// Node for "Events Generated" connector
export const EventsGeneratedNode = ({ data }) => (
  <Box sx={{
    padding: '10px',
    borderRadius: '4px',
    backgroundColor: '#f3e5f5',
    border: '2px solid #9c27b0',
    width: 180,
  }}>
    <Handle type="target" position={Position.Top} />
    <Typography variant="subtitle2" sx={{ 
        color: '#4a148c',
        fontWeight: 'bold',
    }}>{data.label}</Typography>
    <Handle type="source" position={Position.Bottom} />
  </Box>
);

// Node for individual events
export const EventNode = ({ data }) => (
  <Tooltip title={<pre>{JSON.stringify(data.details, null, 2)}</pre>} placement="bottom">
    <Box sx={{
      padding: '10px',
      borderRadius: '4px',
      backgroundColor: '#fff9c4',
      border: '2px solid #ffc107',
      width: 200,
    }}>
      <Handle type="target" position={Position.Top} />
      <Typography variant="subtitle2" sx={{ 
          color: '#ff6f00',
          fontWeight: 'bold',
      }}>{data.label}</Typography>
      <Typography variant="caption" sx={{ 
          color: '#ff6f00',
          fontWeight: 'normal',
          display: 'block'
      }}>Hover for details</Typography>
      <Handle type="source" position={Position.Bottom} />
    </Box>
  </Tooltip>
);
