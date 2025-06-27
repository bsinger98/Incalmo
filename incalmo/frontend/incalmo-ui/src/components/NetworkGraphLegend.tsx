import React from 'react';
import { Panel } from 'reactflow';
import { Box, Typography } from '@mui/material';
import { Security, Computer, Warning, Info } from '@mui/icons-material';

const NetworkGraphLegend: React.FC = () => {
    return (
        <Panel position="top-left">
            <Box sx={{
                backgroundColor: 'rgba(255,255,255,0.9)',
                p: 1,
                borderRadius: 1,
                border: '1px solid #ddd'
            }}>
                <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                    <Security color="error" sx={{ fontSize: 12, mr: 0.5 }} />
                    Red = Compromised
                </Typography>
                <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                    <Computer color="success" sx={{ fontSize: 12, mr: 0.5 }} />
                    Green = Clean
                </Typography>
                <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                    <Warning color="warning" sx={{ fontSize: 12, mr: 0.5 }} />
                    Arrows = Infection Path
                </Typography>
                <Typography variant="caption" display="block" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                    <Info color="info" sx={{ fontSize: 12, mr: 0.5 }} />
                    Hover for details
                </Typography>
            </Box>
        </Panel>
    );
};

export default NetworkGraphLegend; 