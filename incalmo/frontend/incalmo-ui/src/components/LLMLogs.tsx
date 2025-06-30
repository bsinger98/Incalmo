import React, { useRef, useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { LLMLogsProps } from '../types';

const LLMLogs = ({ logs, isConnected, error }: LLMLogsProps) => {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [fullyDisplayedCount, setFullyDisplayedCount] = useState(0);
  const [currentLogText, setCurrentLogText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const typewriterRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom whenever content changes
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [fullyDisplayedCount, currentLogText]);

  // Typewriter effect - process one log at a time
  useEffect(() => {
    // Clear any existing interval
    if (typewriterRef.current) {
      clearInterval(typewriterRef.current);
      typewriterRef.current = null;
    }

    // If we have more logs than fully displayed, start typing the next one
    if (logs.length > fullyDisplayedCount) {
      const logToType = logs[fullyDisplayedCount];
      setIsTyping(true);
      setCurrentLogText('');

      let charIndex = 0;

      const typewriterInterval = setInterval(() => {
        if (charIndex <= logToType.length) {
          setCurrentLogText(logToType.slice(0, charIndex));
          charIndex += 2; // Type 3 characters at once for much faster effect
        } else {
          // Finished typing this log
          clearInterval(typewriterInterval);
          setIsTyping(false);
          setCurrentLogText('');
          setFullyDisplayedCount(prev => prev + 1);
        }
      }, 5); // Also reduced interval to 2ms

      typewriterRef.current = typewriterInterval;
    } else {
      setIsTyping(false);
      setCurrentLogText('');
    }

    // Cleanup on unmount
    return () => {
      if (typewriterRef.current) {
        clearInterval(typewriterRef.current);
      }
    };
  }, [logs.length, fullyDisplayedCount]);

  // Reset when logs are cleared
  useEffect(() => {
    if (logs.length === 0) {
      setFullyDisplayedCount(0);
      setCurrentLogText('');
      setIsTyping(false);
    }
  }, [logs.length]);

  // Get the text to display
  const getDisplayText = () => {
    const fullyDisplayedLogs = logs.slice(0, fullyDisplayedCount);
    if (currentLogText && isTyping) {
      return [...fullyDisplayedLogs, currentLogText].join('\n');
    }
    return fullyDisplayedLogs.join('\n');
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Box sx={{
        p: 1.5,
        backgroundColor: 'secondary.dark',
        color: 'secondary.contrastText',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h6">LLM Logs</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isTyping && (
            <CircularProgress size={16} sx={{ color: 'secondary.contrastText' }} />
          )}
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            size="small"
          />
        </Box>
      </Box>

      <Divider />

      {error && (
        <Alert severity="error" sx={{ m: 1 }}>{error}</Alert>
      )}

      <Box
        sx={{
          flex: 1,
          overflow: 'hidden',
          p: 0.5,
          backgroundColor: 'background.default',
        }}
      >
        {logs.length === 0 && !error ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography color="text.secondary">Waiting for LLM logs...</Typography>
          </Box>
        ) : (
          <Box
            ref={logContainerRef}
            sx={{
              backgroundColor: 'background.paper',
              borderRadius: 1,
              borderLeft: 4,
              borderColor: 'secondary.main',
              p: 1.5,
              height: '100%',
              overflow: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
                height: '8px',
              },
              '&::-webkit-scrollbar-track': {
                backgroundColor: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '4px',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                },
              },
            }}
          >
            <pre style={{
              margin: 0,
              fontSize: '0.75rem',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              height: 'auto',
            }}>
              {getDisplayText()}
              {isTyping && (
                <span style={{
                  animation: 'blink 1s infinite',
                  opacity: 0.7
                }}>|</span>
              )}
            </pre>
          </Box>
        )}
      </Box>

      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
    </Box>
  );
};

export default LLMLogs;