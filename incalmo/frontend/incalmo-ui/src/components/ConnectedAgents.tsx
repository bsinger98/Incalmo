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
  CircularProgress
} from '@mui/material';
import { Delete, Computer, PersonOutline } from '@mui/icons-material';

import { ConnectedAgentsProps } from '../types';

const ConnectedAgents = ({ agents, deleteAgent } : ConnectedAgentsProps) => {

  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const handleDeleteClick = (paw: string) => {
    setAgentToDelete(paw);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!agentToDelete) return; 
    setIsDeleting(true);
    await deleteAgent(agentToDelete);
    setIsDeleting(false);
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
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
              py: 0.5,
              px: 1,
              pb: 2,
              height: 'fit-content', 
              position: 'relative',
            }}>
              <IconButton 
                size="small" 
                sx={{ 
                  position: 'absolute', 
                  bottom: 2, 
                  right: 2,
                  padding: 0.5,
                  '&:hover': { color: 'error.main' }
                }}
                onClick={() => handleDeleteClick(paw)}
              >
                <Delete fontSize="small" />
              </IconButton>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Computer color="primary" sx={{ fontSize: 16, mr: 0.5 }} />
                <Typography variant="subtitle2" color="primary.main" noWrap sx={{ flex: 1, lineHeight: 1.2 }}>
                  {paw}
                </Typography>
                <Chip 
                  size="small"
                  label={agentInfo.privilege === "Elevated" ? "Admin" : "User"}
                  color={agentInfo.privilege === "Elevated" ? "error" : "info"}
                  sx={{ 
                    height: 18, 
                    fontSize: '0.65rem',
                    '& .MuiChip-label': { px: 0.5 }
                  }}
                />
              </Box>
              
              {/* User info  */}
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonOutline sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.2 }}>
                  {agentInfo.username || 'Unknown'}
                </Typography>
              </Box>
              
              <Typography 
                variant="caption" 
                color="text.secondary" 
                sx={{ 
                  display: 'block', 
                  lineHeight: 1.2, 
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  mb: 0 
                }}
              >
                {agentInfo.host_ip_addrs?.join(', ') || 'No IP'}
              </Typography>
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
        </Box>
      )}
    </Box>
  );
};

export default ConnectedAgents;