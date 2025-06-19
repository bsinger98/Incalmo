import { Agents, Strategy, MessageType, StrategyInfo, LogEntry } from './api.types';

// Header
export interface HeaderProps {
  agentCount: number;
}

// Connected Agents
export interface ConnectedAgentsProps {
  agents: Agents;
  deleteAgent: (paw: string) => Promise<void>;
}

// Strategy Launcher
export interface StrategyLauncherProps {
  selectedStrategy: string;
  setSelectedStrategy: (strategy: string) => void;
  strategies: Strategy[];
  loading: boolean;
  startStrategy: () => void;
  fetchRunningStrategies: () => void;
  message: string;
  messageType: MessageType;
}

// Running Strategies
export interface RunningStrategiesProps {
  runningStrategies: Record<string, StrategyInfo>;
  stopStrategy: (strategyName: string) => void;
  getStatusColor: (state: string) => 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

// Network Graph
export interface Host {
  hostname?: string;
  ip_addresses?: string[];
  infected?: boolean;
  infected_by?: string;
  agents?: string[];
}

export interface NetworkGraphProps {
  hosts: Host[];
  loading: boolean;
  error?: string;
  lastUpdate?: string;
  onRefresh: () => void;
}

export interface HostNodeProps {
  data: Host;
}

// Logs
export interface LogsProps {
  logs: LogEntry[];
  isConnected: boolean;
  error: string | null;
}