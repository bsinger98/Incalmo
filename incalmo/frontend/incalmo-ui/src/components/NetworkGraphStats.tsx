import React from 'react';
import { Box, Chip, IconButton, Tooltip } from '@mui/material';
import { Refresh } from '@mui/icons-material';

import { NetworkStats } from '../types';

interface NetworkGraphStatsProps {
    stats: NetworkStats;
    loading: boolean;
    onRefresh: () => void;
}

const NetworkGraphStats: React.FC<NetworkGraphStatsProps> = ({
    stats,
    loading,
    onRefresh,
}) => {
    return (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
                label={`${stats.totalHosts} Hosts`}
                color="default"
                size="small"
            />
            <Chip
                label={`${stats.infectedHosts} Infected`}
                color="error"
                size="small"
            />
            <Chip
                label={`${stats.cleanHosts} Clean`}
                color="success"
                size="small"
            />
            <Chip
                label={`${stats.totalAgents} Agents`}
                color="primary"
                size="small"
            />

            <Tooltip title="Refresh">
                <IconButton onClick={onRefresh} disabled={loading}>
                    <Refresh />
                </IconButton>
            </Tooltip>
        </Box>
    );
};

export default NetworkGraphStats; 