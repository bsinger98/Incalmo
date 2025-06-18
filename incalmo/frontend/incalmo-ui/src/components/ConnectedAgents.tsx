import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent
} from '@mui/material';

import { ConnectedAgentsProps } from '../types';

const ConnectedAgents = ({ agents } : ConnectedAgentsProps) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Connected Agents ({Object.keys(agents).length})
      </Typography>
      
      {Object.keys(agents).length === 0 ? (
        <Typography color="textSecondary">
          No agents connected
        </Typography>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {Object.entries(agents).map(([paw, agentInfo]) => (
            <Card key={paw} sx={{ minWidth: 200 }}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="primary">
                  {paw}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  User: {agentInfo.username || 'Unknown'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Privilege: {agentInfo.privilege || 'Unknown'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  IPs: {agentInfo.host_ip_addrs?.join(', ') || 'Unknown'}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Paper>
  );
};

export default ConnectedAgents;