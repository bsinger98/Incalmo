import React , {useState} from 'react';
import {
  Typography,
  Box,
  Card,
  Divider,
  Chip,
  IconButton, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button,
  CircularProgress,
  TextField
} from '@mui/material';
import { Delete, Computer, PersonOutline } from '@mui/icons-material';

import { ConnectedAgentsProps } from '../types';

const ConnectedAgents = ({ agents, deleteAgent, sendCommandToAgent } : ConnectedAgentsProps) => {

  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const [commandDialogOpen, setCommandDialogOpen] = useState<boolean>(false);
  const [currentAgentPaw, setCurrentAgentPaw] = useState<string | null>(null);
  const [command, setCommand] = useState<string>('');
  const [commandOutput, setCommandOutput] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  const handleDeleteClick = (paw: string) => {
    setAgentToDelete(paw);
    setDeleteDialogOpen(true);
  };

  const handleCommandClick = (paw: string) => {
    setCurrentAgentPaw(paw);
    setCommandDialogOpen(true);
    setCommand('');
    setCommandOutput('');
  };

  const confirmDelete = async () => {
    if (!agentToDelete) return; 
    setIsDeleting(true);
    await deleteAgent(agentToDelete);
    setIsDeleting(false);
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
  };

  const handleCommandExecute = async () => {
    if (!currentAgentPaw || !command) return;
    setIsExecuting(true);
    try {
      const response = await sendCommandToAgent(currentAgentPaw, command);
      if (response) {
        setCommandOutput(response.output);
        if (response.stderr) {
          setCommandOutput(prev => prev + '\n\nErrors:\n' + response.stderr);
        }
      } else {
        setCommandOutput('Command sent but received no response from the server.');
      }
    } catch (error) {
      console.error('Failed to execute command:', error);
      setCommandOutput(`Failed to execute command: ${error.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="subtitle1" gutterBottom fontWeight="medium">
        Connected Agents ({Object.keys(agents).length})
      </Typography>
      
      <Divider sx={{ mb: 1 }} />
      
      {Object.keys(agents).length === 0 ? (
        <Typography color="text.secondary" variant="body2" sx={{ py: 1 }}>
          No agents connected
        </Typography>
      ) : (
        <Box sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 1, 
          overflow: 'auto',
          flex: 1,
          pl: 0.5, 
          pr: 0.5  
        }}>
          {Object.entries(agents).map(([paw, agentInfo]) => (
            <Card key={paw} variant="outlined" sx={{ 
              width: 'calc(50% - 8px)',
              minWidth: '160px',
              mb: 1,
              p: 1,
              height: 'fit-content', 
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
            }}>
              {/* Header with Agent ID and Privilege Badge */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, overflow: 'hidden' }}>
                  <Computer color="primary" sx={{ fontSize: 16, mr: 0.5 }} />
                  <Typography variant="subtitle2" color="primary.main" noWrap>
                    {paw}
                  </Typography>
                </Box>
                <Chip 
                  size="small"
                  label={agentInfo.privilege === "Elevated" ? "Admin" : "User"}
                  color={agentInfo.privilege === "Elevated" ? "error" : "info"}
                  sx={{ 
                    height: 18, 
                    fontSize: '0.65rem',
                    '& .MuiChip-label': { px: 0.5 },
                    ml: 0.5
                  }}
                />
              </Box>
              
              {/* User info */}
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <PersonOutline sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {agentInfo.username || 'Unknown'}
                </Typography>
              </Box>
              
              {/* IP Address */}
              <Typography 
                variant="caption" 
                color="text.secondary" 
                sx={{ 
                  display: 'block', 
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  mb: 1
                }}
              >
                {agentInfo.host_ip_addrs?.join(', ') || 'No IP'}
              </Typography>
              
              {/* Action Buttons at Bottom */}
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                mt: 'auto', 
                pt: 0.5,
                borderTop: '1px solid rgba(255, 255, 255, 0.12)'
              }}>
                <Button
                  size="small"
                  variant="outlined"
                  color="primary"
                  onClick={() => handleCommandClick(paw)}
                  sx={{ fontSize: '0.7rem', py: 0, minWidth: 'auto', flex: 1, mr: 1 }}
                >
                  Command
                </Button>
                <IconButton 
                  size="small" 
                  color="error"
                  sx={{ padding: 0.5 }}
                  onClick={() => handleDeleteClick(paw)}
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Box>
            </Card>
          ))}
          <Dialog
            open={deleteDialogOpen}
            onClose={() => setDeleteDialogOpen(false)}
            aria-labelledby="delete-dialog-title"
          >
            <DialogTitle id="delete-dialog-title">Delete Agent</DialogTitle>
            <DialogContent>
              <Typography>
                Are you sure you want to delete agent {agentToDelete}? 
                This will terminate the agent process on the remote machine.
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDeleteDialogOpen(false)} disabled={isDeleting}>
                Cancel
              </Button>
              <Button 
                onClick={confirmDelete} 
                color="error" 
                disabled={isDeleting}
                startIcon={isDeleting ? <CircularProgress size={16} /> : null}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </DialogActions>
          </Dialog>
          <Dialog
            open={commandDialogOpen}
            onClose={() => {
              setCommandDialogOpen(false);
              setCommand('');
              setCommandOutput('');
            }}
            fullWidth
            maxWidth="md"
            aria-labelledby="command-dialog-title"
          >
            <DialogTitle id="command-dialog-title">
              Execute Command on Agent {currentAgentPaw}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2, mt: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Enter command to execute:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField 
                    fullWidth
                    size="small"
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    disabled={isExecuting}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleCommandExecute();
                      }
                    }}
                  />
                  <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={handleCommandExecute}
                    disabled={!command || isExecuting}
                    startIcon={isExecuting ? <CircularProgress size={16} /> : null}
                  >
                    {isExecuting ? 'Running...' : 'Execute'}
                  </Button>
                </Box>
                
                <Typography variant="subtitle2" gutterBottom>
                  Output:
                </Typography>
                <Box 
                  sx={{ 
                    backgroundColor: 'black',
                    color: '#00FF00',
                    fontFamily: 'monospace',
                    p: 1,
                    borderRadius: 1,
                    height: '300px',
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {commandOutput || <Typography color="gray" variant="body2">Command output will appear here...</Typography>}
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                setCommandDialogOpen(false);
                setCommand('');
                setCommandOutput('');
              }}>
                Close
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      )}
    </Box>
  );
};

export default ConnectedAgents;