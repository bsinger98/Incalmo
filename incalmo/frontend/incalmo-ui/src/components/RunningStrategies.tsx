import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
} from '@mui/material';
import { Stop } from '@mui/icons-material';

interface StrategyInfo {
  state: string;
  task_id: string;
}

interface RunningStrategiesProps {
  runningStrategies: Record<string, StrategyInfo>;
  stopStrategy: (strategyName: string) => void;
  getStatusColor: (state: string) => 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

const RunningStrategies: React.FC<RunningStrategiesProps> = ({
  runningStrategies,
  stopStrategy,
  getStatusColor,
}) => {
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Running Strategies ({Object.keys(runningStrategies).length})
      </Typography>
      
      {Object.keys(runningStrategies).length === 0 ? (
        <Typography color="textSecondary">
          No strategies currently running
        </Typography>
      ) : (
        <List>
          {Object.entries(runningStrategies).map(([strategyName, strategyInfo]) => (
            <ListItem key={strategyName} divider>
              <ListItemText
                primary={strategyName}
                secondary={
                  // Use React.Fragment instead of Box to avoid div-in-p nesting
                  <React.Fragment>
                    <Chip
                      label={strategyInfo.state}
                      color={getStatusColor(strategyInfo.state)}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    Task ID: {strategyInfo.task_id}
                  </React.Fragment>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => stopStrategy(strategyName)}
                  color="error"
                  title="Stop Strategy"
                >
                  <Stop />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default RunningStrategies;