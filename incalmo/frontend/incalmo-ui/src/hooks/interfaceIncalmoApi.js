import { useState, useEffect } from 'react';
import axios from 'axios';

// Point to Docker container's Flask server
const API_BASE_URL = 'http://localhost:8888';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request/response interceptors for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const useIncalmoApi = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [agents, setAgents] = useState({});
  const [runningStrategies, setRunningStrategies] = useState({});
  const [strategies, setStrategies] = useState([]);
  const [hosts, setHosts] = useState([]);
  const [hostsLoading, setHostsLoading] = useState(false);
  const [hostsError, setHostsError] = useState('');
  const [lastHostsUpdate, setLastHostsUpdate] = useState(null);

  const fetchAgents = async () => {
    try {
      const response = await api.get('/agents');
      setAgents(response.data || {});
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const fetchRunningStrategies = async () => {
    try {
      const response = await api.get('/running_strategies');
      setRunningStrategies(response.data || {});
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    }
  };

  const fetchStrategies = async () => {
  try {
    const response = await api.get('/available_strategies');
    setStrategies(response.data.strategies || []);
    console.log('[API] Available strategies:', response.data);
  } catch (error) {
    console.error('Failed to fetch available strategies:', error);
  }
};

  const startStrategy = async () => {
    if (!selectedStrategy) {
      setMessage('Please select a strategy first');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');

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
      
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || 'Failed to start strategy';
      setMessage(`Error: ${errorMsg}`);
      setMessageType('error');
      console.error('Strategy start error:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopStrategy = async (strategyName) => {
    try {
      await api.post(`/cancel_strategy/${strategyName}`);
      setMessage(`Strategy ${strategyName} stopped successfully`);
      setMessageType('success');
      fetchRunningStrategies();
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || 'Failed to stop strategy';
      setMessage(`Error stopping strategy: ${errorMsg}`);
      setMessageType('error');
    }
  };

  const getStatusColor = (state) => {
    switch (state) {
      case 'SUCCESS': return 'success';
      case 'FAILURE': return 'error';
      case 'PENDING': return 'warning';
      case 'PROGRESS': return 'info';
      default: return 'default';
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
    console.log('[API] Fetched hosts:', data.hosts);
  } catch (err) {
    setHostsError(`Network error: ${err.message}`);
    console.error('[API] Error fetching hosts:', err);
  } finally {
    setHostsLoading(false);
  }
};

  useEffect(() => {
    fetchAgents();
    fetchRunningStrategies();
    fetchStrategies();
    fetchHosts();
    
    const interval = setInterval(() => {
      fetchAgents();
      fetchRunningStrategies();
      fetchStrategies();
      fetchHosts();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return {
    // State
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
    
    // Actions
    setSelectedStrategy,
    startStrategy,
    stopStrategy,
    fetchAgents,
    fetchRunningStrategies,
    fetchStrategies,
    fetchHosts,
    getStatusColor
  };
};