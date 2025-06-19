import React from 'react';
import { Container, Paper, Box } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { darkTheme } from './themes/theme';
import { useIncalmoApi } from './hooks/interfaceIncalmoApi';
import Header from './components/Header';
import StrategyLauncher from './components/StrategyLauncher';
import RunningStrategies from './components/RunningStrategies';
import ConnectedAgents from './components/ConnectedAgents';
import NetworkGraph from './components/NetworkGraph';
import Logs from './components/Logs';

const App = () => {
  const {
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
    fetchHosts,
    deleteAgent,
    setSelectedStrategy,
    startStrategy,
    stopStrategy,
    fetchRunningStrategies,
    getStatusColor
  } = useIncalmoApi();

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="App">
        <Header agentCount={Object.keys(agents).length} />

        <Container 
          disableGutters  
          maxWidth={false} 
          sx={{ 
            height: 'calc(100vh - 64px)',
            px: 2, 
            mt: 2, 
            mb: 2 
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            gap: 2, 
            height: '100%'
          }}>
            {/* Left Panel - Strategy Controls */}
            <Box sx={{ width: '25%', flexShrink: 0 }}>
              <Paper sx={{ 
                p: 2, 
                height: '100%', 
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper', 
                borderRadius: 2,
                overflow: 'hidden'
              }}>
                <Box sx={{ mb: 2 }}>
                  <StrategyLauncher
                    selectedStrategy={selectedStrategy}
                    setSelectedStrategy={setSelectedStrategy}
                    strategies={strategies}
                    loading={loading}
                    startStrategy={startStrategy}
                    fetchRunningStrategies={fetchRunningStrategies}
                    message={message}
                    messageType={messageType}
                  />
                </Box>
                
                <Box sx={{ flex: 1, overflow: 'auto' }}>
                  <RunningStrategies
                    runningStrategies={runningStrategies}
                    stopStrategy={stopStrategy}
                    getStatusColor={getStatusColor}
                  />
                </Box>
              </Paper>
            </Box>
            
            {/* Center Panel - Network Visualization */}
            <Box sx={{ width: '50%', flexShrink: 0 }}>
              <Paper sx={{ 
                p: 2, 
                height: '100%', 
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper',
                borderRadius: 2,
                overflow: 'hidden'
              }}>
                <Box sx={{ height: '65%', 
                    mb: 2, 
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column' 
                }}>
                  <NetworkGraph
                    hosts={hosts}
                    loading={hostsLoading}
                    error={hostsError}
                    lastUpdate={lastHostsUpdate}
                    onRefresh={fetchHosts}
                  />
                </Box>
                
                <Box sx={{ height: '35%', 
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column' 
                }}>
                  <ConnectedAgents agents={agents} deleteAgent={deleteAgent}/>
                </Box>
              </Paper>
            </Box>
            
            {/* Right Panel - Logs */}
            <Box sx={{ width: '25%', flexShrink: 0 }}>
              <Paper sx={{ 
                height: '100%', 
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper',
                borderRadius: 2,
                overflow: 'hidden'
              }}>
                <Logs 
                  logs={logs}
                  isConnected={streamConnected}
                  error={streamError}
                />
              </Paper>
            </Box>
          </Box>
        </Container>
      </div>
    </ThemeProvider>
  );
};

export default App;