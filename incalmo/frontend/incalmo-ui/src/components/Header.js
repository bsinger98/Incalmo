import React from 'react';
import { AppBar, Toolbar, Typography, Chip } from '@mui/material';
import { Security } from '@mui/icons-material';

const Header = ({ agentCount }) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Security sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Incalmo C2 Server Control Panel
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