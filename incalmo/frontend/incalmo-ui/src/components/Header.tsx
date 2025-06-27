import React from 'react';
import { AppBar, Toolbar, Typography, Chip } from '@mui/material';
import { Security } from '@mui/icons-material';
import { HeaderProps } from '../types';

const Header = ({ agentCount }: HeaderProps) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Security sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Incalmo
        </Typography>
        <Chip
          label={`${agentCount} Agents`}
          color="primary"
          variant="outlined"
        />
      </Toolbar>
    </AppBar>
  );
};

export default Header;