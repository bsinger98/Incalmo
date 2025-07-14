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

export interface LowLevelLogEntry {
  type: string;
  timestamp: string;
  high_level_action_id: string;
  low_level_action_id: string;
  action_name: string;
  action_params?: {
    agent?: {
      paw?: string;
      username?: string;
      privilege?: string;
      pid?: string;            
      host_ip_addrs?: string[];
      hostname?: string;
    };
    [key: string]: any;
  };
  action_results?: {
    stdout?: string;
    stderr?: string;
    results?: Record<string, any>;
  };
}


export interface Event{
  event_name: string;
  event_properties: {
    [key: string]: any;
  };
}

export interface HighLevelLogEntry {
  type: string;
  timestamp: string;
  high_level_action_id: string;
  low_level_action_ids: string[];
  action_name: string;
  action_params?: Record<string, any>;
  action_results?: Record<string, any>;
}

export interface CommandResult {
  exit_code: string;
  id: string;
  output: string;
  pid: number;
  status: string;
  stderr: string;
}

export type MessageType = 'info' | 'error' | 'success' | 'warning';