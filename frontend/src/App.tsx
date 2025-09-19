import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/Dashboard';

// Create a custom dark theme for the modern trading app
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3B82F6', // Blue from the design
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#6366F1', // Indigo accent
    },
    background: {
      default: '#10121A', // Main background color
      paper: '#1A1E29', // Widget background color
    },
    success: {
      main: '#0ECB81', // Positive/green color
      contrastText: '#000000',
    },
    error: {
      main: '#F6465D', // Negative/red color
      contrastText: '#ffffff',
    },
    warning: {
      main: '#F59E0B', // Warning yellow
    },
    text: {
      primary: '#E1E3E6', // Main text color
      secondary: '#848E9C', // Secondary text color
    },
    divider: '#2D3748',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    allVariants: {
      color: '#E1E3E6',
    },
    h1: {
      fontWeight: 700,
      color: '#E1E3E6',
    },
    h2: {
      fontWeight: 600,
      color: '#E1E3E6',
    },
    h3: {
      fontWeight: 600,
      color: '#E1E3E6',
    },
    h4: {
      fontWeight: 600,
      color: '#E1E3E6',
    },
    h5: {
      fontWeight: 600,
      color: '#E1E3E6',
    },
    h6: {
      fontWeight: 600,
      color: '#E1E3E6',
    },
    body1: {
      fontSize: '0.875rem',
      color: '#E1E3E6',
    },
    body2: {
      fontSize: '0.75rem',
      color: '#848E9C',
    },
    // Monospace font for numbers and data
    subtitle1: {
      fontFamily: '"IBM Plex Mono", "Courier New", monospace',
      fontWeight: 500,
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '@font-face': [
          {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: '400 700',
            src: 'url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap")',
          },
          {
            fontFamily: 'IBM Plex Mono',
            fontStyle: 'normal',
            fontDisplay: 'swap',
            fontWeight: '400 500',
            src: 'url("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap")',
          },
        ],
        body: {
          backgroundColor: '#10121A',
          color: '#E1E3E6',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1E29',
          borderRadius: '0.5rem',
          boxShadow: 'none',
          border: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1E29',
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#3B82F6',
          borderRadius: '0.5rem',
          margin: '1rem',
          width: 'calc(100% - 2rem)',
          position: 'relative',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
        colorSuccess: {
          backgroundColor: '#0ECB81',
          color: '#000000',
        },
        colorError: {
          backgroundColor: '#F6465D',
          color: '#ffffff',
        },
      },
    },
    MuiFab: {
      styleOverrides: {
        root: {
          backgroundColor: '#3B82F6',
          color: '#ffffff',
          '&:hover': {
            backgroundColor: '#2563EB',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;
