import React from 'react';
import {
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  IconButton,
  Alert,
  CircularProgress
} from '@mui/material';
import { PlayArrow, Refresh } from '@mui/icons-material';

import { StrategyLauncherProps } from '../types';

const StrategyLauncher: React.FC<StrategyLauncherProps> = ({
  selectedStrategy,
  setSelectedStrategy,
  strategies,
  loading,
  startStrategy,
  fetchRunningStrategies,
  message,
  messageType
}) => {
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Launch Incalmo Strategy
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
        <FormControl sx={{ minWidth: 300 }}>
          <InputLabel>Select Strategy</InputLabel>
          <Select
            value={selectedStrategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
            label="Select Strategy"
            disabled={loading}
          >
            {strategies.map((strategy) => (
              <MenuItem key={strategy.name} value={strategy.name}>
                {strategy.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
          onClick={startStrategy}
          disabled={loading || !selectedStrategy}
          size="large"
        >
          {loading ? 'Starting...' : 'Start Strategy'}
        </Button>

        <IconButton onClick={fetchRunningStrategies} title="Refresh">
          <Refresh />
        </IconButton>
      </Box>

      {message && (
        <Alert severity={messageType} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
    </Paper>
  );
};

export default StrategyLauncher;