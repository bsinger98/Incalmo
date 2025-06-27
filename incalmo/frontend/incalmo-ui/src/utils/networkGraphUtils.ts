import dagre from '@dagrejs/dagre';
import { Node, Edge, Position } from 'reactflow';
import { Host } from '../types';

// Constants
export const LAYOUT_CONFIG = {
    nodeWidth: 220,
    nodeHeight: 100,
    nodeSpacing: 50,
    rankSpacing: 100,
    direction: 'TB' as const,
} as const;

export const EDGE_STYLES = {
    stroke: '#f44336',
    strokeWidth: 4,
    animated: true,
} as const;

export const HANDLE_STYLES = {
    target: {
        background: '#f44336',
        width: 8,
        height: 8,
    },
    source: {
        background: '#4caf50',
        width: 8,
        height: 8,
    },
} as const;

// Tree layout configuration
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

/**
 * Generate a unique ID for each host
 */
export const getHostId = (host: Host, index: number): string => {
    if (host.hostname && host.hostname.trim()) {
        return host.hostname;
    }
    if (host.ip_addresses && host.ip_addresses.length > 0) {
        return `host-${host.ip_addresses[0].replace(/\./g, '-')}`;
    }
    return `host-${index}`;
};

/**
 * Apply tree layout to nodes and edges using dagre
 */
export const getTreeLayoutedElements = (nodes: Node[], edges: Edge[]) => {
    const { nodeWidth, nodeHeight, nodeSpacing, rankSpacing, direction } = LAYOUT_CONFIG;

    dagreGraph.setGraph({
        rankdir: direction,
        nodesep: nodeSpacing,
        ranksep: rankSpacing
    });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    return nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
            ...node,
            position: {
                x: nodeWithPosition.x - nodeWidth / 2,
                y: nodeWithPosition.y - nodeHeight / 2,
            },
            sourcePosition: Position.Bottom,
            targetPosition: Position.Top,
        };
    });
};

/**
 * Calculate network statistics from hosts data
 */
export const calculateNetworkStats = (hosts: Host[]) => {
    const totalHosts = hosts?.length || 0;
    const infectedHosts = hosts?.filter(h => h.infected).length || 0;
    const cleanHosts = totalHosts - infectedHosts;
    const totalAgents = hosts?.reduce((sum, h) => sum + (h.agents?.length || 0), 0) || 0;

    return { totalHosts, infectedHosts, cleanHosts, totalAgents };
};

/**
 * Generate infection edges from hosts data
 */
export const generateInfectionEdges = (hosts: Host[]): Edge[] => {
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

                if (sourceHostId !== targetHostId) {
                    edges.push({
                        id: `${sourceHostId}->${targetHostId}`,
                        source: sourceHostId,
                        target: targetHostId,
                        type: 'smoothstep',
                        animated: EDGE_STYLES.animated,
                        style: {
                            stroke: EDGE_STYLES.stroke,
                            strokeWidth: EDGE_STYLES.strokeWidth,
                        },
                        label: targetHost.infected_by,
                        labelStyle: {
                            fontSize: 12,
                            fontWeight: 'bold',
                            fill: EDGE_STYLES.stroke,
                        },
                        markerEnd: {
                            type: 'arrowclosed',
                            color: EDGE_STYLES.stroke,
                        },
                    } as Edge);
                }
            }
        }
    });

    return edges;
}; 