import React from 'react';
import { Box, Typography } from '@mui/material';
import { Security, Computer, Warning, Info } from '@mui/icons-material';

const NetworkGraphLegend: React.FC = () => {
    const legendItems = [
        {
            icon: <Security color="error" sx={{ fontSize: 12, mr: 0.5 }} />,
            text: 'Red = Compromised'
        },
        {
            icon: <Computer color="success" sx={{ fontSize: 12, mr: 0.5 }} />,
            text: 'Green = Clean'
        },
        {
            icon: <Warning color="warning" sx={{ fontSize: 12, mr: 0.5 }} />,
            text: 'Arrows = Infection Path'
        },
        {
            icon: <Info color="info" sx={{ fontSize: 12, mr: 0.5 }} />,
            text: 'Hover for details'
        }
    ];

    return (
        <Box sx={{
            backgroundColor: 'rgba(255,255,255,0.9)',
            p: 1,
            borderRadius: 1,
            border: '1px solid #ddd'
        }}>
            {legendItems.map((item, index) => (
                <Typography
                    key={index}
                    variant="caption"
                    display="block"
                    sx={{ color: 'rgba(0, 0, 0, 0.87)' }}
                >
                    {item.icon}
                    {item.text}
                </Typography>
            ))}
        </Box>
    );
};

export default NetworkGraphLegend; 