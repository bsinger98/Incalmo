import React from 'react';
import { Box, Typography, Chip, IconButton, Tooltip } from '@mui/material';
import { Refresh } from '@mui/icons-material';

interface NetworkStats {
    totalHosts: number;
    infectedHosts: number;
    cleanHosts: number;
    totalAgents: number;
}

interface NetworkGraphHeaderProps {
    stats: NetworkStats;
    loading: boolean;
    onRefresh: () => void;
}

const NetworkGraphHeader: React.FC<NetworkGraphHeaderProps> = ({
    stats,
    loading,
    onRefresh
}) => {
    return (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6">Network Attack Graph</Typography>

            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Chip label={`${stats.totalHosts} Hosts`} color="default" size="small" />
                <Chip label={`${stats.infectedHosts} Infected`} color="error" size="small" />
                <Chip label={`${stats.cleanHosts} Clean`} color="success" size="small" />
                <Chip label={`${stats.totalAgents} Agents`} color="primary" size="small" />

                <Tooltip title="Refresh">
                    <IconButton onClick={onRefresh} disabled={loading}>
                        <Refresh />
                    </IconButton>
                </Tooltip>
            </Box>
        </Box>
    );
};

export default NetworkGraphHeader; 