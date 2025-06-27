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
  const [displayedLogs, setDisplayedLogs] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const typewriterRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom whenever displayed content changes
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [displayedLogs]);

  // Typewriter effect for new log entries
  useEffect(() => {
    if (logs.length === 0) {
      setDisplayedLogs([]);
      return;
    }

    // If we have more logs than displayed, show typewriter effect for new ones
    if (logs.length > displayedLogs.length) {
      const existingLogs = logs.slice(0, displayedLogs.length);
      const newLogIndex = displayedLogs.length;
      const newLogText = logs[newLogIndex];

      // Clear any existing typewriter effect
      if (typewriterRef.current) {
        clearInterval(typewriterRef.current);
      }

      setIsTyping(true);
      let charIndex = 0;

      const typewriterInterval = setInterval(() => {
        if (charIndex <= newLogText.length) {
          const currentChar = newLogText.slice(0, charIndex);
          setDisplayedLogs([...existingLogs, currentChar]);
          charIndex++;
        } else {
          clearInterval(typewriterInterval);
          setIsTyping(false);

          // If there are more logs to process, trigger the effect again
          if (logs.length > newLogIndex + 1) {
            setTimeout(() => {
              setDisplayedLogs(logs.slice(0, newLogIndex + 1));
            }, 100);
          }
        }
      }, 30); // Adjust typing speed here (lower = faster)

      typewriterRef.current = typewriterInterval;
    }
    // If logs were cleared or reset, update immediately
    else if (logs.length < displayedLogs.length) {
      setDisplayedLogs([...logs]);
    }

    // Cleanup on unmount
    return () => {
      if (typewriterRef.current) {
        clearInterval(typewriterRef.current);
      }
    };
  }, [logs, displayedLogs]);

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
        {displayedLogs.length === 0 && !error ? (
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
              {displayedLogs.join('\n')}
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