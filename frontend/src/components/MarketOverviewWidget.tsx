// Market overview widget showing major indices

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
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
        <Box key={name} sx={{ textAlign: 'center' }}>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ fontSize: '0.875rem', mb: 1 }}
          >
            {name}
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: '"IBM Plex Mono", monospace',
              fontWeight: 500,
              mb: 1,
              color: 'text.primary'
            }}
          >
            $0.00
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              fontFamily: '"IBM Plex Mono", monospace',
              color: 'error.main',
              fontSize: '0.875rem'
            }}
          >
            +0.00%
          </Typography>
        </Box>
      );
    }

    return (
      <Box key={name} sx={{ textAlign: 'center' }}>
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ fontSize: '0.875rem', mb: 1 }}
        >
          {name}
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '"IBM Plex Mono", monospace',
            fontWeight: 500,
            mb: 1,
            color: 'text.primary'
          }}
        >
          {name === 'VIX' ? index.price.toFixed(2) : formatCurrency(index.price)}
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            fontFamily: '"IBM Plex Mono", monospace',
            color: index.change_percent >= 0 ? 'success.main' : 'error.main',
            fontSize: '0.875rem'
          }}
        >
          {index.change_percent >= 0 ? '+' : ''}{formatPercentage(index.change_percent)}
        </Typography>
      </Box>
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

  // Get indices data
  const indices = Object.entries(data).filter(([key]) => key !== 'timestamp');

  return (
    <Card sx={{ bgcolor: 'background.paper' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography 
          variant="h6" 
          sx={{ 
            mb: 3,
            fontWeight: 600,
            color: 'text.primary'
          }}
        >
          Market Overview
        </Typography>

        <Grid 
          container 
          spacing={4} 
          sx={{ 
            mb: 2,
            '& > .MuiGrid-item': {
              display: 'flex',
              justifyContent: 'center'
            }
          }}
        >
          {indices.map(([name, index]) => (
            <Grid xs={12} sm={6} md={4} lg={2.4} key={name}>
              {renderIndexCard(name, index)}
            </Grid>
          ))}
        </Grid>

        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            mt: 2, 
            display: 'block',
            fontSize: '0.75rem'
          }}
        >
          Last updated: {data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default MarketOverviewWidget;