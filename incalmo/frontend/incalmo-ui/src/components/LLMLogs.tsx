import React, { useRef } from 'react';
import {
  Box,
  Typography,
  Chip,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { LLMLogsProps } from '../types';

const LLMLogs = ({ logs, isConnected, error }: LLMLogsProps) => {
  const logContainerRef = useRef<HTMLDivElement>(null);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Box sx={{ 
        p: 1.5, 
        backgroundColor: 'secondary.dark', 
        color: 'secondary.contrastText',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h6">LLM Logs</Typography>
        <Chip 
          label={isConnected ? 'Connected' : 'Disconnected'} 
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>
      
      <Divider />
      
      {error && (
        <Alert severity="error" sx={{ m: 1 }}>{error}</Alert>
      )}
      
      <Box 
        ref={logContainerRef}
        sx={{ 
          flex: 1, 
          overflow: 'auto',
          p: 0.5,
          backgroundColor: 'background.default'
        }}
      >
        {logs.length === 0 && !error ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography color="text.secondary">Waiting for LLM logs...</Typography>
          </Box>
        ) : (
          <Box 
            sx={{ 
              backgroundColor: 'background.paper',
              borderRadius: 1,
              borderLeft: 4,
              borderColor: 'secondary.main',
              p: 1.5,
              height: '100%'
            }}
          >
            <pre style={{ 
              margin: 0, 
              fontSize: '0.75rem',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              height: '100%',
              overflowY: 'auto'
            }}>
              {logs.join('\n')}
            </pre>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default LLMLogs;