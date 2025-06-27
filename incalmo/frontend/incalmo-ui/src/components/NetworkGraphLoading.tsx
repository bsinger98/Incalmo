import React from 'react';
import { Paper, Box, Typography } from '@mui/material';

const NetworkGraphLoading: React.FC = () => {
    return (
        <Paper sx={{ p: 3, mb: 3, height: 700 }}>
            <Box sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%'
            }}>
                <Typography>Loading network graph...</Typography>
            </Box>
        </Paper>
    );
};

export default NetworkGraphLoading; 