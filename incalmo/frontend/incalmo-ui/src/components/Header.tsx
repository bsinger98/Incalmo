import React from 'react';
import { AppBar, Toolbar, Typography, Chip } from '@mui/material';
import { HeaderProps } from '../types';

const Header = ({ agentCount }: HeaderProps) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h4" component="div" sx={{ flexGrow: 1, fontFamily: 'Poppins' }}>
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