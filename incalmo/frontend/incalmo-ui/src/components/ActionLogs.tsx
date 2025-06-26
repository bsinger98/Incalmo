import React, { useRef, useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  Divider,
  List,
  ListItem,
  Alert,
  CircularProgress,
  IconButton,
  Collapse,
  Tooltip
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { ActionLogsProps } from '../types';

const ActionLogs = ({ logs, isConnected, error }: ActionLogsProps) => {
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
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Box sx={{ 
        p: 1.5, 
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
          p: 0.5,
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
                  mb: 0.5, 
                  p: 1, 
                  backgroundColor: 'background.paper',
                  borderRadius: 1,
                  borderLeft: 4,
                  borderColor: 'primary.main',
                  display: 'block'
                }}
              >
                {/* Time and action name */}
                <Box sx={{ mb: 0.5, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                  </Typography>
                  {hasExpandableContent(log) && (
                    <Tooltip title={expandedLogs[index] ? "Hide details" : "Show details"}>
                      <IconButton 
                        size="small" 
                        onClick={() => toggleExpand(index)}
                        sx={{ p: 0, ml: 0.5, height: 20, width: 20 }}
                      >
                        {expandedLogs[index] ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
                
                {/* Action name and PAW */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'medium', maxWidth: '65%' }} noWrap>
                    {log.action_name}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip
                      label={log.action_params?.agent?.paw || 'N/A'}
                      size="small"
                      variant="outlined"
                      color="primary"
                      sx={{ 
                        height: 20, 
                        fontSize: '0.7rem',
                        '& .MuiChip-label': { px: 1 }
                      }}
                    />
                  </Box>
                </Box>
                
                {/* Collapsible stdout/stderr section */}
                {hasExpandableContent(log) && (
                  <Collapse in={expandedLogs[index] === true} timeout="auto" unmountOnExit>
                    <Box sx={{ mt: 1 }}>
                      {log.action_results?.stdout && (
                        <Box sx={{ 
                          p: 1, 
                          backgroundColor: 'action.hover', 
                          borderRadius: 1, 
                          mb: 1,
                          maxHeight: '150px',
                          overflow: 'auto'
                        }}>
                          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                            Output:
                          </Typography>
                          <pre style={{ 
                            margin: 0, 
                            fontSize: '0.75rem',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-all',
                            overflowWrap: 'break-word'
                          }}>
                            {log.action_results.stdout}
                          </pre>
                        </Box>
                      )}
                      
                      {log.action_results?.stderr && (
                        <Box sx={{ 
                          p: 1, 
                          backgroundColor: 'error.main', 
                          color: 'error.contrastText', 
                          borderRadius: 1,
                          maxHeight: '150px',
                          overflow: 'auto'
                        }}>
                          <Typography variant="caption" display="block" gutterBottom>
                            Error:
                          </Typography>
                          <pre style={{ 
                            margin: 0, 
                            fontSize: '0.75rem',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-all',
                            overflowWrap: 'break-word'
                          }}>
                            {log.action_results.stderr}
                          </pre>
                        </Box>
                      )}
                    </Box>
                  </Collapse>
                )}
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </Box>
  );
};

export default ActionLogs;