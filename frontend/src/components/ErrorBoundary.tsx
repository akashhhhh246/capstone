import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in React component tree:', error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
            p: 3,
          }}
        >
          <Paper
            elevation={3}
            sx={{
              maxWidth: 600,
              width: '100%',
              p: 4,
              borderRadius: 3,
              bgcolor: 'background.paper',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                display: 'inline-flex',
                p: 2,
                borderRadius: '50%',
                bgcolor: 'rgba(239, 68, 68, 0.1)',
                color: 'error.main',
                mb: 2,
              }}
            >
              <AlertTriangle size={40} />
            </Box>

            <Typography variant="h5" component="h2" sx={{ fontWeight: 700, mb: 1 }}>
              {this.props.fallbackTitle || 'Component Execution Error'}
            </Typography>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              An unexpected error occurred while rendering this interface module. 
              The system protected the rest of your investigative session from crashing.
            </Typography>

            {this.state.error && (
              <Box
                sx={{
                  textAlign: 'left',
                  p: 2,
                  mb: 3,
                  borderRadius: 2,
                  bgcolor: 'rgba(0, 0, 0, 0.4)',
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  color: '#f87171',
                  overflowX: 'auto',
                }}
              >
                {this.state.error.toString()}
              </Box>
            )}

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<RefreshCw size={16} />}
                onClick={this.handleReset}
                sx={{ textTransform: 'none' }}
              >
                Retry Component
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<Home size={16} />}
                onClick={this.handleReload}
                sx={{ textTransform: 'none' }}
              >
                Reload Dashboard
              </Button>
            </Box>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}
