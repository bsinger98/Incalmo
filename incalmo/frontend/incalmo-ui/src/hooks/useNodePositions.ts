import { useState, useCallback } from 'react';
import { NodeChange } from 'reactflow';

export interface Position {
    x: number;
    y: number;
}

/**
 * Custom hook for managing node positions in the network graph
 */
export const useNodePositions = () => {
    const [nodePositions, setNodePositions] = useState<Map<string, Position>>(new Map());

    const updateNodePosition = useCallback((nodeId: string, position: Position) => {
        setNodePositions(prev => {
            const next = new Map(prev);
            next.set(nodeId, position);
            return next;
        });
    }, []);

    const handleNodesChange = useCallback((changes: NodeChange[], originalOnNodesChange: (changes: NodeChange[]) => void) => {
        // Apply the React Flow nodes change first so the graph updates immediately,
        // then persist the positions for layout persistence.
        originalOnNodesChange(changes);

        changes.forEach((change) => {
            if (change.type === 'position' && change.position) {
                updateNodePosition(change.id, change.position);
            }
        });
    }, [updateNodePosition]);

    const getNodePosition = useCallback((nodeId: string): Position | undefined => {
        return nodePositions.get(nodeId);
    }, [nodePositions]);

    const hasPosition = useCallback((nodeId: string): boolean => {
        return nodePositions.has(nodeId);
    }, [nodePositions]);

    return {
        nodePositions,
        updateNodePosition,
        handleNodesChange,
        getNodePosition,
        hasPosition,
    };
}; 