// Portfolio summary widget

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  AccountBalance,
  ArrowUpward
} from '@mui/icons-material';

import { PortfolioAnalytics } from '../types';

interface PortfolioWidgetProps {
  data: PortfolioAnalytics | null;
  loading: boolean;
}

const PortfolioWidget: React.FC<PortfolioWidgetProps> = ({ data, loading }) => {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value: number, totalValue: number): string => {
    const percentage = (value / totalValue) * 100;
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1
    }).format(percentage / 100);
  };


  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <AccountBalance sx={{ mr: 1 }} />
            Portfolio Summary
          </Typography>
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <AccountBalance sx={{ mr: 1 }} />
            Portfolio Summary
          </Typography>
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No portfolio data available
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            Connect your E*TRADE account to view portfolio analytics
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Calculate daily change percentage
  const dailyChangePercent = data.total_value > 0 ? 
    (data.daily_change / (data.total_value - data.daily_change)) * 100 : 0;

  // Sort positions by market value (largest first)
  const sortedPositions = Object.entries(data.positions)
    .map(([symbol, position]) => ({ symbol, ...position }))
    .sort((a, b) => b.market_value - a.market_value);

  return (
    <Card sx={{ bgcolor: 'background.paper' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header with Market Sentiment */}
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Portfolio Summary
          </Typography>
          <Chip
            label="Bearish Market"
            sx={{
              bgcolor: 'rgba(244, 70, 93, 0.2)',
              color: 'error.main',
              fontSize: '0.75rem',
              fontWeight: 600,
              border: 'none'
            }}
            size="small"
          />
        </Box>

        {/* Total Portfolio Value */}
        <Typography 
          variant="h3" 
          sx={{ 
            fontFamily: '"IBM Plex Mono", monospace',
            fontWeight: 'bold',
            mb: 1,
            color: 'text.primary'
          }}
        >
          {formatCurrency(data.total_value)}
        </Typography>
        
        {/* Daily Change */}
        <Box display="flex" alignItems="center" gap={1} sx={{ mb: 3 }}>
          <ArrowUpward 
            sx={{ 
              color: 'success.main', 
              fontSize: 16 
            }} 
          />
          <Typography
            sx={{
              fontFamily: '"IBM Plex Mono", monospace',
              color: data.daily_change >= 0 ? 'success.main' : 'error.main',
              ml: 0.5
            }}
          >
            {data.daily_change > 0 ? '+' : ''}{formatCurrency(data.daily_change)} ({dailyChangePercent > 0 ? '+' : ''}{dailyChangePercent.toFixed(2)}%) today
          </Typography>
        </Box>

        {/* Top Holdings */}
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 600, 
            mb: 2,
            fontSize: '1rem'
          }}
        >
          Top Holdings
        </Typography>
        
        <Box sx={{ '& > *:not(:last-child)': { mb: 2 } }}>
          {sortedPositions.slice(0, 2).map(({ symbol, quantity, current_price, market_value }) => (
            <Box key={symbol}>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 500, mb: 0.5 }}>
                    {symbol}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {quantity} shares @ {formatCurrency(current_price)}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontFamily: '"IBM Plex Mono", monospace',
                      fontWeight: 500,
                      mb: 0.5
                    }}
                  >
                    {formatCurrency(market_value)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatPercentage(market_value, data.total_value)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          ))}
        </Box>

        {/* Account Info */}
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            mt: 3, 
            display: 'block',
            fontSize: '0.75rem'
          }}
        >
          Account: {data.account_id} - Updated: {new Date(data.timestamp).toLocaleString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default PortfolioWidget;