import dagre from 'dagre';
import { Node, Edge } from 'reactflow';
import { Host } from '../types';

// Graph layout constants
export const GRAPH_CONFIG = {
    NODE_WIDTH: 220,
    NODE_HEIGHT: 100,
    NODES_SEPARATION: 50,
    RANKS_SEPARATION: 100,
    LAYOUT_DIRECTION: 'TB' as const,
} as const;

// Create dagre graph instance
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

/**
 * Generate a unique ID for each host based on hostname or IP
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
 * Apply tree layout to nodes using dagre algorithm
 */
export const getTreeLayoutedElements = (
    nodes: Node[],
    edges: Edge[],
    savedPositions: Map<string, { x: number, y: number }>
): Node[] => {
    const nodesToLayout = nodes.filter(node => !savedPositions.has(node.id));
    const nodesWithSavedPositions = nodes.filter(node => savedPositions.has(node.id));

    // Configure graph layout
    dagreGraph.setGraph({
        rankdir: GRAPH_CONFIG.LAYOUT_DIRECTION,
        nodesep: GRAPH_CONFIG.NODES_SEPARATION,
        ranksep: GRAPH_CONFIG.RANKS_SEPARATION
    });

    // Add nodes to layout
    nodesToLayout.forEach((node) => {
        dagreGraph.setNode(node.id, {
            width: GRAPH_CONFIG.NODE_WIDTH,
            height: GRAPH_CONFIG.NODE_HEIGHT
        });
    });

    // Add edges to layout
    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    // Calculate layout
    dagre.layout(dagreGraph);

    // Apply layout positions to nodes
    const layoutedNodes = nodesToLayout.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
            ...node,
            position: {
                x: nodeWithPosition.x - GRAPH_CONFIG.NODE_WIDTH / 2,
                y: nodeWithPosition.y - GRAPH_CONFIG.NODE_HEIGHT / 2,
            },
        };
    });

    return [...layoutedNodes, ...nodesWithSavedPositions];
};

/**
 * Calculate network statistics from hosts data
 */
export const calculateNetworkStats = (hosts: Host[]) => {
    const totalHosts = hosts?.length || 0;
    const infectedHosts = hosts?.filter(h => h.infected).length || 0;
    const cleanHosts = totalHosts - infectedHosts;
    const totalAgents = hosts?.reduce((sum, h) => sum + (h.agents?.length || 0), 0) || 0;

    return {
        totalHosts,
        infectedHosts,
        cleanHosts,
        totalAgents
    };
}; 