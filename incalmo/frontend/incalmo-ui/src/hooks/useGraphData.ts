import { useMemo } from 'react';
import { Node, Edge, Position } from 'reactflow';
import { Host } from '../types';
import { getHostId } from '../utils/graphUtils';

interface UseGraphDataProps {
    hosts: Host[];
    nodePositions?: Map<string, { x: number; y: number }>;
}

/**
 * Custom hook for transforming hosts data into ReactFlow nodes and edges
 */
export const useGraphData = ({ hosts }: UseGraphDataProps) => {
    // Convert hosts to ReactFlow nodes
    const hostNodes = useMemo((): Node<Host>[] => {
        if (!hosts || hosts.length === 0) return [];

        return hosts.map((host, index) => {
            const hostId = getHostId(host, index);
            return {
                id: hostId,
                type: 'hostNode',
                position: { x: 0, y: 0 }, // overridden by layout / saved positions
                data: { ...host },
                draggable: true,
                sourcePosition: Position.Bottom,
                targetPosition: Position.Top,
            } as Node<Host>;
        });
    }, [hosts]);

    // Convert infection relationships to ReactFlow edges
    const infectionEdges = useMemo((): Edge[] => {
        if (!hosts || hosts.length === 0) return [];

        const edges: Edge[] = [];

        hosts.forEach((targetHost, targetIndex) => {
            if (targetHost.infected && targetHost.infected_by) {
                const sourceHostIndex = hosts.findIndex(h =>
                    h.agents && h.agents.includes(targetHost.infected_by!)
                );

                if (sourceHostIndex !== -1) {
                    const sourceHost = hosts[sourceHostIndex];
                    const sourceHostId = getHostId(sourceHost, sourceHostIndex);
                    const targetHostId = getHostId(targetHost, targetIndex);

                    // Avoid self-loops
                    if (sourceHostId !== targetHostId) {
                        edges.push({
                            id: `${sourceHostId}->${targetHostId}`,
                            source: sourceHostId,
                            target: targetHostId,
                            type: 'smoothstep',
                            animated: false,
                            style: {
                                stroke: '#f44336',
                                strokeWidth: 3,
                                strokeDasharray: '6 3',
                            },
                            label: targetHost.infected_by,
                            labelStyle: {
                                fontSize: 12,
                                fontWeight: 'bold',
                                fill: '#f44336'
                            },
                            markerEnd: {
                                type: 'arrowclosed',
                                color: '#f44336',
                                width: 20,
                                height: 20,
                            },
                        } as Edge);
                    }
                }
            }
        });

        return edges;
    }, [hosts]);

    return {
        nodes: hostNodes,
        edges: infectionEdges,
    };
}; 