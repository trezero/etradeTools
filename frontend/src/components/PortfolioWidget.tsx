// Portfolio summary widget

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  TrendingDown
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

  const getDailyChangeColor = (change: number): 'success' | 'error' | 'default' => {
    if (change > 0) return 'success';
    if (change < 0) return 'error';
    return 'default';
  };

  const getDailyChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp color="success" fontSize="small" />;
    if (change < 0) return <TrendingDown color="error" fontSize="small" />;
    return null;
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
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <AccountBalance sx={{ mr: 1 }} />
          Portfolio Summary
        </Typography>

        {/* Total Value */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="div" gutterBottom>
            {formatCurrency(data.total_value)}
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            {getDailyChangeIcon(data.daily_change)}
            <Chip
              label={`${data.daily_change > 0 ? '+' : ''}${formatCurrency(data.daily_change)}`}
              color={getDailyChangeColor(data.daily_change)}
              size="small"
            />
            <Typography variant="body2" color="text.secondary">
              ({dailyChangePercent > 0 ? '+' : ''}{dailyChangePercent.toFixed(2)}%) today
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Top Holdings */}
        <Typography variant="subtitle2" gutterBottom>
          Top Holdings
        </Typography>
        
        <List dense>
          {sortedPositions.slice(0, 5).map(({ symbol, quantity, current_price, market_value }) => (
            <ListItem key={symbol} disablePadding>
              <ListItemText
                primary={
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" fontWeight="medium">
                      {symbol}
                    </Typography>
                    <Typography variant="body2">
                      {formatCurrency(market_value)}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      {quantity} shares @ {formatCurrency(current_price)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatPercentage(market_value, data.total_value)}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>

        {sortedPositions.length > 5 && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            +{sortedPositions.length - 5} more positions
          </Typography>
        )}

        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
          Account: {data.account_id} • Updated: {new Date(data.timestamp).toLocaleString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default PortfolioWidget;