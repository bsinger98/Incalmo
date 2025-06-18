import React from 'react';
import { Container } from '@mui/material';
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

const App: React.FC = () => {
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

        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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

          <NetworkGraph
            hosts={hosts}
            loading={hostsLoading}
            error={hostsError}
            lastUpdate={lastHostsUpdate}
            onRefresh={fetchHosts}
          />

          <RunningStrategies
            runningStrategies={runningStrategies}
            stopStrategy={stopStrategy}
            getStatusColor={getStatusColor}
          />

          <ConnectedAgents agents={agents} />
          <Logs 
            logs={logs}
            isConnected={streamConnected}
            error={streamError}
          />
        </Container>
      </div>
    </ThemeProvider>
  );
};

export default App;