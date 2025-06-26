import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

import {
  Host,
  RunningStrategies,
  Agents,
  Strategy,
  LogEntry,
  MessageType
} from '../types'



const API_BASE_URL = 'http://localhost:8888';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Hook to manage Incalmo API interactions
export const useIncalmoApi = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [messageType, setMessageType] = useState<MessageType>('info');
  const [agents, setAgents] = useState<Agents>({});
  const [runningStrategies, setRunningStrategies] = useState<RunningStrategies>({});
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [hosts, setHosts] = useState<Host[]>([]);
  const [hostsLoading, setHostsLoading] = useState<boolean>(false);
  const [hostsError, setHostsError] = useState<string>('');
  const [lastHostsUpdate, setLastHostsUpdate] = useState<string>('');

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [streamConnected, setStreamConnected] = useState<boolean>(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    fetchAgents();
    fetchRunningStrategies();
    fetchStrategies();
    fetchHosts();
    //connectToLogStream();
    
    // Set up polling interval
    const interval = setInterval(() => {
      fetchAgents();
      fetchRunningStrategies();
      fetchStrategies();
      fetchHosts();
    }, 10000);

    return () => {
      clearInterval(interval);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  const fetchAgents = async (): Promise<void> => {
    try {
      const response = await api.get('/agents');
      setAgents(response.data || {});
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const deleteAgent = async (paw: string): Promise<void> => {
    try {
      await api.delete(`/agent/delete/${paw}`);
      await fetchAgents();
      } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const fetchRunningStrategies = async (): Promise<void> => {
    try {
      const response = await api.get('/running_strategies');
      setRunningStrategies(response.data || {});
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    }
  };

  const fetchStrategies = async (): Promise<void> => {
    try {
      const response = await api.get('/available_strategies');
      setStrategies(response.data.strategies || []);
    } catch (error) {
      console.error('Failed to fetch available strategies:', error);
    }
  };

  const startStrategy = async (): Promise<void> => {
    if (!selectedStrategy) {
      setMessage('Please select a strategy first');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');
    setLogs([]);

    try {
      const config = {
        name: "react-ui-session",
        strategy: {
          llm: selectedStrategy,
          abstraction: "incalmo"
        },
        environment: "EquifaxLarge",
        c2c_server: "http://host.docker.internal:8888",
      };

      const response = await api.post('/startup', config);

      setMessage(`Strategy ${selectedStrategy} started successfully! Task ID: ${response.data.task_id}`);
      setMessageType('success');
      setSelectedStrategy('');

      fetchRunningStrategies();
      setTimeout(() => {
        connectToLogStream();
      }, 5000);

    } catch (error: any) {
      const errorMsg = error.response?.data?.error || error.message || 'Failed to start strategy';
      setMessage(`Error: ${errorMsg}`);
      setMessageType('error');
      console.error('Strategy start error:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopStrategy = async (strategyName: string): Promise<void> => {
    try {
      await api.post(`/cancel_strategy/${strategyName}`);
      setMessage(`Strategy ${strategyName} stopped successfully`);
      setMessageType('success');
      fetchRunningStrategies();
    } catch (error: any) {
      const errorMsg = error.response?.data?.error || error.message || 'Failed to stop strategy';
      setMessage(`Error stopping strategy: ${errorMsg}`);
      setMessageType('error');
    }
  };

  const getStatusColor = (state: string): 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
  switch (state) {
    case 'SUCCESS': return 'success';
    case 'FAILURE': return 'error';
    case 'PENDING': return 'warning';
    case 'PROGRESS': return 'info';
    default: return 'primary';
  }
};

const fetchHosts = async () => {
  setHostsLoading(true);
  setHostsError('');
  
  try {
    const response = await api.get('/hosts');
    const data = response.data;
    
    setHosts(data.hosts || []);
    setLastHostsUpdate(new Date().toLocaleTimeString());
  } catch (err) {
    setHostsError(`Network error: ${err.message}`);
    console.error('[API] Error fetching hosts:', err);
  } finally {
    setHostsLoading(false);
  }
};

  const connectToLogStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      const eventSource = new EventSource(`${API_BASE_URL}/stream_logs`);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.status) {
            console.log('Log stream status:', data.status);
            return;
          }
          
          if (data.error) {
            setStreamError(data.error);
            return;
          }
          
          if (data.type === 'LowLevelAction') {
            setLogs(prevLogs => {
              const newLogs = [...prevLogs, data];
              if (newLogs.length > 200) {
                return newLogs.slice(-200);
              }
              return newLogs;
            });
          }
        } catch (e) {
          console.error('Error parsing log data:', e);
        }
      };
      
      eventSource.onopen = () => {
        setStreamConnected(true);
        setStreamError(null);
      };
      
      eventSource.onerror = () => {
        setStreamConnected(false);
        setStreamError('Connection to log stream failed. Will try to reconnect...');
        
        setTimeout(() => {
          if (eventSourceRef.current === eventSource) {
            connectToLogStream();
          }
        }, 5000);
      };
    } catch (error) {
      console.error('Failed to connect to log stream:', error);
      setStreamError('Failed to establish log stream connection');
    }
  };


  return {
    selectedStrategy,
    loading,
    message,
    messageType,
    agents,
    runningStrategies,
    strategies,
    hosts,              
    hostsLoading,       
    hostsError,         
    lastHostsUpdate, 
    logs,                
    streamConnected,     
    streamError, 
    
    // Actions
    setSelectedStrategy,
    startStrategy,
    stopStrategy,
    fetchAgents,
    deleteAgent,
    fetchRunningStrategies,
    fetchStrategies,
    fetchHosts,
    getStatusColor
  };
};