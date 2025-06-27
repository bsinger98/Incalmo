import React, { useState, MouseEvent } from 'react';
import { Handle, Position } from 'reactflow';
import {
    Paper,
    Typography,
    Box,
    Chip,
    Card,
    CardContent,
    Popover,
} from '@mui/material';
import {
    Computer,
    Security,
} from '@mui/icons-material';

import { Host, HostNodeProps } from '../types';

const getHostDisplayName = (host: Host): string => {
    if (host.hostname && host.hostname.trim()) {
        return host.hostname;
    }
    if (host.ip_addresses && host.ip_addresses.length > 0) {
        const firstIp = host.ip_addresses[0];
        const lastOctet = firstIp.split('.').pop();
        return `Host-${lastOctet}`;
    }
    return 'Unknown-Host';
};

const HostNode = React.memo(({ data }: HostNodeProps) => {
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const [showPopover, setShowPopover] = useState(false);

    const handleMouseEnter = (event: MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
        setShowPopover(true);
    };

    const handleMouseLeave = () => {
        setShowPopover(false);
        setAnchorEl(null);
    };

    const displayName = getHostDisplayName(data);

    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
                style={{
                    background: '#f44336',
                    width: 8,
                    height: 8,
                }}
            />
            <Handle
                type="source"
                position={Position.Bottom}
                style={{
                    background: '#4caf50',
                    width: 8,
                    height: 8,
                }}
            />
            <Card
                sx={{
                    minWidth: 180,
                    maxWidth: 220,
                    border: data.infected ? '3px solid #f44336' : '3px solid #4caf50',
                    backgroundColor: data.infected ? '#ffebee' : '#e8f5e9',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease-in-out',
                    position: 'relative',
                    '&:hover': {
                        boxShadow: 6,
                        transform: 'scale(1.05)',
                    },
                }}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
            >
                <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {data.infected ? (
                            <Security color="error" sx={{ mr: 1, fontSize: 20 }} />
                        ) : (
                            <Computer color="success" sx={{ mr: 1, fontSize: 20 }} />
                        )}
                        <Typography
                            variant="subtitle1"
                            sx={{
                                flexGrow: 1,
                                fontWeight: 'bold',
                                color: data.infected ? '#630000' : '#1b5e20'
                            }}
                        >
                            {displayName}
                        </Typography>
                    </Box>

                    <Typography
                        variant="caption"
                        sx={{
                            display: 'block',
                            mb: 1,
                            color: 'rgba(0, 0, 0, 0.87)'
                        }}
                    >
                        {data.ip_addresses?.join(', ') || 'No IPs'}
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        <Chip
                            label={data.infected ? 'Compromised' : 'Clean'}
                            color={data.infected ? 'error' : 'success'}
                            size="small"
                        />
                        {data.agents && data.agents.length > 0 && (
                            <Chip
                                label={`${data.agents.length} Agent${data.agents.length > 1 ? 's' : ''}`}
                                color="primary"
                                size="small"
                            />
                        )}
                    </Box>
                </CardContent>
            </Card>

            <Popover
                open={showPopover}
                anchorEl={anchorEl}
                onClose={handleMouseLeave}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                sx={{ pointerEvents: 'none' }}
                disableRestoreFocus
            >
                <Card sx={{ maxWidth: 350, p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        {displayName}
                    </Typography>

                    <Typography variant="body2" color="textSecondary" gutterBottom>
                        <strong>IPs:</strong> {data.ip_addresses?.join(', ') || 'None'}
                    </Typography>

                    <Typography variant="body2" gutterBottom>
                        <strong>Status:</strong>
                        <Chip
                            label={data.infected ? 'Compromised' : 'Clean'}
                            color={data.infected ? 'error' : 'success'}
                            size="small"
                            sx={{ ml: 1 }}
                        />
                    </Typography>

                    {data.infected_by && (
                        <Typography variant="body2" color="error" gutterBottom>
                            <strong>Infected by Agent:</strong> {data.infected_by}
                        </Typography>
                    )}

                    {data.agents && data.agents.length > 0 && (
                        <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" fontWeight="bold">Agents:</Typography>
                            {data.agents.map((agentPaw, idx) => (
                                <Typography key={idx} variant="caption" display="block" sx={{ ml: 1 }}>
                                    • {agentPaw}
                                </Typography>
                            ))}
                        </Box>
                    )}

                    {(!data.agents || data.agents.length === 0) && (
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                            <strong>Agents:</strong> None
                        </Typography>
                    )}
                </Card>
            </Popover>
        </>
    );
});

HostNode.displayName = 'HostNode';

export default HostNode; 