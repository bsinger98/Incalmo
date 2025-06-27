import React from 'react';
import { Container, Paper, Box, Divider } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { darkTheme } from './themes/theme';
import { useIncalmoApi } from './hooks/interfaceIncalmoApi';
import Header from './components/Header';
import StrategyLauncher from './components/StrategyLauncher';
import RunningStrategies from './components/RunningStrategies';
import ConnectedAgents from './components/ConnectedAgents';
import NetworkGraph from './components/NetworkGraph';
import ActionLogs from './components/ActionLogs';
import LLMLogs from './components/LLMLogs';

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
    actionLogs,
    actionStreamConnected,
    actionStreamError,
    llmLogs,
    llmStreamConnected,
    llmStreamError,
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
            height: 'calc(87vh)',
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
            <Box sx={{ width: '20%', flexShrink: 0 }}>
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
                <Box sx={{
                  height: '65%',
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

                <Box sx={{
                  height: '35%',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  <ConnectedAgents agents={agents} deleteAgent={deleteAgent} />
                </Box>
              </Paper>
            </Box>

            {/* Right Panel - Logs */}
            <Box sx={{ width: '28%', flexShrink: 0 }}>
              <Paper sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper',
                borderRadius: 2,
                overflow: 'hidden'
              }}>
                <Box sx={{ height: '50%', overflow: 'hidden' }}>
                  <ActionLogs
                    logs={actionLogs}
                    isConnected={actionStreamConnected}
                    error={actionStreamError}
                  />
                </Box>
                <Divider />
                <Box sx={{ height: '50%', overflow: 'hidden' }}>
                  <LLMLogs
                    logs={llmLogs}
                    isConnected={llmStreamConnected}
                    error={llmStreamError}
                  />
                </Box>
              </Paper>
            </Box>
          </Box>
        </Container>
      </div>
    </ThemeProvider>
  );
};

export default App;