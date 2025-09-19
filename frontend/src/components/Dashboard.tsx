// Main dashboard component for AI Trading Assistant

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Badge,
  Alert,
  CircularProgress,
  Chip,
  Fab
} from '@mui/material';
import {
  Notifications,
  Settings,
  Psychology,
  ShowChart,
  TrendingUp,
  AccountBalanceWallet,
  Link,
  Chat,
} from '@mui/icons-material';

import { MarketOverview, PortfolioAnalytics, AIDecision, WatchlistItem } from '../types';
import { marketApi, portfolioApi, aiApi } from '../services/api';
import webSocketService from '../services/websocket';

import MarketOverviewWidget from './MarketOverviewWidget';
import PortfolioWidget from './PortfolioWidget';
import WatchlistWidget from './WatchlistWidget';
import AIDecisionsWidget from './AIDecisionsWidget';
import AIAnalysisDialog from './AIAnalysisDialog';
import ETradeWidget from './ETradeWidget';
import ETradeTradeWidget from './ETradeTradeWidget';

const Dashboard: React.FC = () => {
  // State management
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioAnalytics | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [recentDecisions, setRecentDecisions] = useState<AIDecision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  const [newDecisionCount, setNewDecisionCount] = useState(0);
  const [aiAnalysisOpen, setAiAnalysisOpen] = useState(false);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
    setupWebSocket();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);

    return () => {
      clearInterval(interval);
      webSocketService.disconnect();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all dashboard data in parallel
      const [marketData, portfolioData, watchlistData, decisionsData] = await Promise.allSettled([
        marketApi.getMarketOverview(),
        portfolioApi.getLatestPortfolio(),
        marketApi.getWatchlistData(),
        aiApi.getDecisions(undefined, 10)
      ]);

      // Handle market overview
      if (marketData.status === 'fulfilled') {
        setMarketOverview(marketData.value);
      } else {
        console.error('Failed to load market data:', marketData.reason);
      }

      // Handle portfolio
      if (portfolioData.status === 'fulfilled') {
        setPortfolio(portfolioData.value);
      } else {
        console.error('Failed to load portfolio:', portfolioData.reason);
      }

      // Handle watchlist
      if (watchlistData.status === 'fulfilled') {
        setWatchlist(watchlistData.value.watchlist || []);
      } else {
        console.error('Failed to load watchlist:', watchlistData.reason);
      }

      // Handle decisions
      if (decisionsData.status === 'fulfilled') {
        setRecentDecisions(decisionsData.value);
      } else {
        console.error('Failed to load decisions:', decisionsData.reason);
      }

    } catch (error) {
      console.error('Dashboard data loading error:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    setConnectionStatus('connecting');

    // Setup WebSocket event handlers
    webSocketService.on('connected', () => {
      setConnectionStatus('connected');
      console.log('✅ Dashboard connected to WebSocket');
    });

    webSocketService.on('new_decision', (event) => {
      console.log('🤖 New AI decision received:', event.data);
      setNewDecisionCount(prev => prev + 1);
      // Refresh decisions
      aiApi.getDecisions(undefined, 10).then(setRecentDecisions);
    });

    webSocketService.on('preferences_updated', () => {
      console.log('⚙️ Preferences updated');
      // Refresh watchlist as it may have changed
      marketApi.getWatchlistData().then(data => setWatchlist(data.watchlist || []));
    });

    webSocketService.on('feedback_updated', () => {
      console.log('💬 Decision feedback updated');
      // Refresh decisions
      aiApi.getDecisions(undefined, 10).then(setRecentDecisions);
    });

    // Connect to WebSocket
    webSocketService.connect();
  };

  const handleDecisionNotificationClick = () => {
    setNewDecisionCount(0);
    // Could navigate to decisions page or show decisions dialog
  };


  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'disconnected': return 'error';
      default: return 'default';
    }
  };

  if (loading && !marketOverview) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress size={50} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading AI Trading Assistant...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      flexGrow: 1, 
      bgcolor: 'background.default', 
      minHeight: '100vh',
      p: 2 
    }}>
      {/* Modern App Bar */}
      <AppBar 
        position="static" 
        sx={{ 
          bgcolor: 'primary.main',
          borderRadius: '0.5rem',
          mb: 2,
          position: 'relative',
          width: '100%',
          mx: 0
        }}
      >
        <Toolbar sx={{ px: 3 }}>
          <TrendingUp sx={{ mr: 2, color: 'white' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            AI Trading Assistant
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Connection Status with animated indicator */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  position: 'relative',
                  width: 12,
                  height: 12,
                }}
              >
                {connectionStatus === 'connecting' && (
                  <Box
                    sx={{
                      position: 'absolute',
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      bgcolor: 'success.main',
                      opacity: 0.75,
                      animation: 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',
                      '@keyframes ping': {
                        '75%, 100%': {
                          transform: 'scale(2)',
                          opacity: 0,
                        },
                      },
                    }}
                  />
                )}
                <Box
                  sx={{
                    position: 'relative',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    bgcolor: connectionStatus === 'connected' ? 'success.main' : 
                             connectionStatus === 'connecting' ? 'warning.main' : 'error.main',
                  }}
                />
              </Box>
              <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                {connectionStatus === 'connected' ? 'Connected' : 
                 connectionStatus === 'connecting' ? 'Connecting' : 'Disconnected'}
              </Typography>
            </Box>
            
            <IconButton 
              color="inherit" 
              onClick={handleDecisionNotificationClick}
              sx={{ 
                p: 1.5,
                borderRadius: '50%',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <Badge badgeContent={newDecisionCount} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <IconButton 
              color="inherit"
              sx={{ 
                p: 1.5,
                borderRadius: '50%',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <Settings />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Dashboard Grid */}
      <Box>
        <Grid container spacing={3}>
          {/* Market Overview - Full Width */}
          <Grid xs={12}>
            <MarketOverviewWidget data={marketOverview} loading={loading} />
          </Grid>

          {/* Portfolio Summary */}
          <Grid xs={12} lg={4}>
            <PortfolioWidget data={portfolio} loading={loading} />
          </Grid>

          {/* Watchlist and AI Decisions */}
          <Grid xs={12} lg={8}>
            <Grid container spacing={3}>
              {/* Watchlist */}
              <Grid xs={12} md={6}>
                <WatchlistWidget data={watchlist} loading={loading} />
              </Grid>

              {/* Recent AI Decisions */}
              <Grid xs={12} md={6}>
                <AIDecisionsWidget 
                  decisions={recentDecisions} 
                  loading={loading}
                  onFeedbackSubmit={(decisionId, feedback) => {
                    aiApi.submitFeedback(decisionId, feedback)
                      .then(() => {
                        console.log('✅ Feedback submitted');
                        // Refresh decisions
                        aiApi.getDecisions(undefined, 10).then(setRecentDecisions);
                      })
                      .catch(error => {
                        console.error('❌ Failed to submit feedback:', error);
                      });
                  }}
                />
              </Grid>
            </Grid>
          </Grid>

          {/* E*TRADE Account and Trading */}
          <Grid xs={12}>
            <Grid container spacing={3}>
              {/* E*TRADE Account */}
              <Grid xs={12} md={6}>
                <ETradeWidget />
              </Grid>

              {/* E*TRADE Trading */}
              <Grid xs={12} md={6}>
                <ETradeTradeWidget />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Box>

      {/* Floating Action Button for AI Chat */}
      <Fab 
        color="primary" 
        aria-label="ai-chat"
        sx={{ 
          position: 'fixed', 
          bottom: 24, 
          right: 24,
          width: 64,
          height: 64,
          boxShadow: '0 8px 32px rgba(59, 130, 246, 0.3)',
          '&:hover': {
            transform: 'scale(1.05)',
            transition: 'transform 0.2s ease-in-out',
          }
        }}
        onClick={() => setAiAnalysisOpen(true)}
      >
        <Chat sx={{ fontSize: 28 }} />
      </Fab>

      {/* AI Analysis Dialog */}
      <AIAnalysisDialog 
        open={aiAnalysisOpen}
        onClose={() => setAiAnalysisOpen(false)}
        onAnalysisComplete={(result) => {
          console.log('🤖 AI Analysis completed:', result);
          // Refresh decisions and watchlist
          aiApi.getDecisions(undefined, 10).then(setRecentDecisions);
          marketApi.getWatchlistData().then(data => setWatchlist(data.watchlist || []));
        }}
      />
    </Box>
  );
};

export default Dashboard;