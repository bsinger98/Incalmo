import React from 'react';
import {
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

const StrategyLauncher = ({
  selectedStrategy,
  setSelectedStrategy,
  strategies,
  loading,
  startStrategy,
  fetchRunningStrategies,
  message,
  messageType
}:StrategyLauncherProps) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Launch Incalmo Strategy
      </Typography>
      
      {/* Changed to vertical layout */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 2 }}>
        <FormControl fullWidth>
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
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            onClick={startStrategy}
            disabled={loading || !selectedStrategy}
            size="large"
            fullWidth
          >
            {loading ? 'Starting...' : 'Start Strategy'}
          </Button>

          <IconButton onClick={fetchRunningStrategies} title="Refresh">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {message && (
        <Alert severity={messageType} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
    </Box>
  );
};

export default StrategyLauncher;