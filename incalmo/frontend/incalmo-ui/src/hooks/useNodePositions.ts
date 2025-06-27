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
        setNodePositions(prev => new Map(prev.set(nodeId, position)));
    }, []);

    const handleNodesChange = useCallback((changes: NodeChange[], originalOnNodesChange: (changes: NodeChange[]) => void) => {
        changes.forEach((change) => {
            if (change.type === 'position' && change.position) {
                updateNodePosition(change.id, change.position);
            }
        });
        originalOnNodesChange(changes);
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