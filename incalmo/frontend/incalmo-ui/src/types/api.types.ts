// Types 
export interface AgentInfo {
  username?: string;
  privilege?: string;
  host_ip_addrs?: string[];
}

export interface StrategyInfo {
  state: string;
  task_id: string;
}

export interface RunningStrategies {
  [strategyName: string]: StrategyInfo;
}

export interface Agents {
  [paw: string]: AgentInfo;
}

export interface Strategy {
  name: string;
}

export interface LogEntry {
  type: string;
  timestamp: string;
  action_name: string;
  action_params?: {
    agent?: {
      paw?: string;
      username?: string;
      privilege?: string;
    };
    [key: string]: any;
  };
  action_results?: {
    stdout?: string;
    stderr?: string;
    results?: any;
  };
}
export type MessageType = 'info' | 'error' | 'success' | 'warning';