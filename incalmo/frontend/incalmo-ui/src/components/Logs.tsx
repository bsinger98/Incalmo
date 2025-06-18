import React, { useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Divider,
  List,
  ListItem,
  Alert,
  CircularProgress,
  IconButton,
  Collapse
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { LogsProps } from '../types';

const Logs = ({ logs, isConnected, error }: LogsProps) => {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [expandedLogs, setExpandedLogs] = useState<Record<number, boolean>>({});

  const toggleExpand = (index: number) => {
    setExpandedLogs(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const hasExpandableContent = (log: any) => {
    return log.action_results?.stdout || log.action_results?.stderr;
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Box sx={{ 
        p: 2, 
        backgroundColor: 'primary.dark', 
        color: 'primary.contrastText',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h6">Action Logs</Typography>
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
          p: 1,
          backgroundColor: 'background.default'
        }}
      >
        {logs.length === 0 && !error ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography color="text.secondary">Waiting for logs...</Typography>
          </Box>
        ) : (
          <List sx={{ p: 0 }}>
            {logs.map((log, index) => (
              <ListItem 
                key={index} 
                sx={{ 
                  mb: 1, 
                  p: 2, 
                  backgroundColor: 'background.paper',
                  borderRadius: 1,
                  borderLeft: 4, 
                }}
              >
                <Box sx={{ width: '100%' }}>
                  {/* Main log info always visible */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1, fontSize: '0.8rem' }}>
                      {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                    </Typography>
                    <Typography variant="subtitle2" sx={{ ml: 2, fontWeight: 'bold', flexGrow: 1 }}>
                      {log.action_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
                      {log.action_params.agent.paw || 'N/A'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
                      {log.type}
                    </Typography>
                    
                    {/* Only show expand button if action_results contains stdout or stderr */}
                    {hasExpandableContent(log) && (
                      <IconButton 
                        size="small" 
                        onClick={() => toggleExpand(index)}
                        sx={{ ml: 1 }}
                      >
                        {expandedLogs[index] ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    )}
                  </Box>
                  
                  {/* Collapsible stdout/stderr section from action_results */}
                  {hasExpandableContent(log) && (
                    <Collapse in={expandedLogs[index] === true} timeout="auto" unmountOnExit>
                      <Box sx={{ ml: 2, mt: 1 }}>
                        {log.action_results?.stdout && (
                          <Box sx={{ mt: 1, p: 1, backgroundColor: 'action.hover', borderRadius: 1, overflow: 'auto' }}>
                            <Typography variant="caption" color="text.secondary">Output:</Typography>
                            <pre style={{ margin: 0, fontSize: '0.8rem' }}>{log.action_results.stdout}</pre>
                          </Box>
                        )}
                        
                        {log.action_results?.stderr && (
                          <Box sx={{ mt: 1, p: 1, backgroundColor: 'error.main', color: 'error.contrastText', borderRadius: 1, overflow: 'auto' }}>
                            <Typography variant="caption">Error:</Typography>
                            <pre style={{ margin: 0, fontSize: '0.8rem' }}>{log.action_results.stderr}</pre>
                          </Box>
                        )}
                      </Box>
                    </Collapse>
                  )}
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </Paper>
  );
};

export default Logs;