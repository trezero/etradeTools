// Market overview widget showing major indices

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  ShowChart
} from '@mui/icons-material';

import { MarketOverview, MarketIndex } from '../types';

interface MarketOverviewWidgetProps {
  data: MarketOverview | null;
  loading: boolean;
}

const MarketOverviewWidget: React.FC<MarketOverviewWidgetProps> = ({ data, loading }) => {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      signDisplay: 'always'
    }).format(value / 100);
  };

  const getTrendIcon = (changePercent: number) => {
    if (changePercent > 0) return <TrendingUp color="success" />;
    if (changePercent < 0) return <TrendingDown color="error" />;
    return <TrendingFlat color="disabled" />;
  };

  const getTrendColor = (changePercent: number): 'success' | 'error' | 'default' => {
    if (changePercent > 0) return 'success';
    if (changePercent < 0) return 'error';
    return 'default';
  };

  const renderIndexCard = (name: string, index: MarketIndex | { error: string }) => {
    if ('error' in index) {
      return (
        <Paper key={name} sx={{ p: 2, bgcolor: 'grey.100' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {name}
          </Typography>
          <Typography variant="caption" color="error">
            Error loading data
          </Typography>
        </Paper>
      );
    }

    return (
      <Paper key={name} sx={{ p: 2, cursor: 'pointer', '&:hover': { bgcolor: 'grey.50' } }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="body2" color="text.secondary">
            {name}
          </Typography>
          {getTrendIcon(index.change_percent)}
        </Box>
        
        <Typography variant="h6" component="div" gutterBottom>
          {name === 'VIX' ? index.price.toFixed(2) : formatCurrency(index.price)}
        </Typography>
        
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={formatPercentage(index.change_percent)}
            color={getTrendColor(index.change_percent)}
            size="small"
          />
          <Typography variant="caption" color="text.secondary">
            {index.change > 0 ? '+' : ''}{index.change.toFixed(2)}
          </Typography>
        </Box>
      </Paper>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <ShowChart sx={{ mr: 1 }} />
            Market Overview
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
            <ShowChart sx={{ mr: 1 }} />
            Market Overview
          </Typography>
          <Typography color="text.secondary">
            Market data unavailable
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Calculate overall market sentiment
  const indices = Object.entries(data).filter(([key]) => key !== 'timestamp');
  const positiveIndices = indices.filter(([, index]) => 
    typeof index === 'object' && 'change_percent' in index && index.change_percent > 0
  ).length;
  
  const overallSentiment = positiveIndices / indices.length;
  const sentimentColor = overallSentiment >= 0.6 ? 'success' : overallSentiment >= 0.4 ? 'warning' : 'error';
  const sentimentText = overallSentiment >= 0.6 ? 'Bullish' : overallSentiment >= 0.4 ? 'Mixed' : 'Bearish';

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            <ShowChart sx={{ mr: 1 }} />
            Market Overview
          </Typography>
          <Chip
            label={`${sentimentText} Market`}
            color={sentimentColor}
            variant="outlined"
          />
        </Box>

        <Grid container spacing={2}>
          {indices.map(([name, index]) => (
            <Grid xs={12} sm={6} md={4} lg={2.4} key={name}>
              {renderIndexCard(name, index)}
            </Grid>
          ))}
        </Grid>

        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
          Last updated: {new Date(data.timestamp).toLocaleTimeString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default MarketOverviewWidget;