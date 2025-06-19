import React from 'react';
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Box,
  Divider
} from '@mui/material';
import { Stop } from '@mui/icons-material';

import { RunningStrategiesProps } from '../types';

const RunningStrategies = ({
  runningStrategies,
  stopStrategy,
  getStatusColor,
}: RunningStrategiesProps) => {
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="subtitle1" gutterBottom fontWeight="medium">
        Running Strategies ({Object.keys(runningStrategies).length})
      </Typography>
      
      <Divider sx={{ mb: 1 }} />
      
      {Object.keys(runningStrategies).length === 0 ? (
        <Typography color="text.secondary" variant="body2" sx={{ py: 2, textAlign: 'center' }}>
          No strategies currently running
        </Typography>
      ) : (
        <List dense sx={{ 
          overflow: 'auto', 
          flex: 1,
          '& .MuiListItem-root': {
            py: 1
          }
        }}>
          {Object.entries(runningStrategies).map(([strategyName, strategyInfo]) => (
            <ListItem 
              key={strategyName} 
              divider
              secondaryAction={
                <IconButton
                  edge="end"
                  onClick={() => stopStrategy(strategyName)}
                  color="error"
                  size="small"
                  title="Stop Strategy"
                >
                  <Stop fontSize="small" />
                </IconButton>
              }
            >
              <ListItemText
                primary={strategyName}
                slotProps={{
                  primary: { variant: 'body2', fontWeight: 'medium' }
                }}
                secondary={
                  <React.Fragment>
                    <Chip
                      label={strategyInfo.state}
                      color={getStatusColor(strategyInfo.state)}
                      size="small"
                      sx={{ mr: 1, mt: 0.5, height: 20, '& .MuiChip-label': { px: 1, fontSize: '0.7rem' } }}
                    />
                    <Typography variant="caption" component="span" color="text.secondary">
                      ID: {strategyInfo.task_id.substring(0, 8)}...
                    </Typography>
                  </React.Fragment>
                }
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default RunningStrategies;