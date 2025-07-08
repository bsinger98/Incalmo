import React from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Typography } from '@mui/material';

export const DiscoveryNode = ({ data }) => (
  <Box sx={{
    padding: '10px',
    borderRadius: '4px',
    backgroundColor: '#e8f5e9',
    border: '3px solid #4caf50',
    width: 180,
  }}>
    <Handle type="target" position={Position.Left} />
    <Typography variant="subtitle2"sx={{ 
        color: '#1b5e20',
        fontWeight: 'bold',
    }}>{data.label}</Typography>
    <Typography variant="caption" sx={{ 
        color: '#1b5e20',
        fontWeight: 'normal',
    }}>{data.time}</Typography>
    <Handle type="source" position={Position.Right} />
  </Box>
);

export const InfectionNode = ({ data }) => (
  <Box sx={{
    padding: '10px',
    backgroundColor: '#ffebee',
    border: '3px solid #f44336',
    width: 180,
  }}>
    <Handle type="target" position={Position.Left} />
    <Typography variant="subtitle2"sx={{ 
        color: '#630000',
        fontWeight: 'bold',
    }}>{data.label}</Typography>
    <Typography variant="caption" sx={{ 
        color: '#630000',
        fontWeight: 'normal',
    }}>{data.time}</Typography>
    <Handle type="source" position={Position.Right} />
  </Box>
);