// Watchlist widget showing tracked symbols

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  LinearProgress,
  Collapse
} from '@mui/material';
import {
  Visibility,
  ExpandMore,
  ExpandLess,
  Psychology,
  TrendingUp,
  TrendingDown,
  TrendingFlat
} from '@mui/icons-material';

import { WatchlistItem } from '../types';

interface WatchlistWidgetProps {
  data: WatchlistItem[];
  loading: boolean;
  onAnalyzeSymbol?: (symbol: string) => void;
}

const WatchlistWidget: React.FC<WatchlistWidgetProps> = ({ 
  data, 
  loading, 
  onAnalyzeSymbol 
}) => {
  const [expandedSymbol, setExpandedSymbol] = useState<string | null>(null);

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
    if (changePercent > 0.5) return <TrendingUp color="success" fontSize="small" />;
    if (changePercent < -0.5) return <TrendingDown color="error" fontSize="small" />;
    return <TrendingFlat color="disabled" fontSize="small" />;
  };

  const getTrendColor = (changePercent: number): 'success' | 'error' | 'default' => {
    if (changePercent > 0) return 'success';
    if (changePercent < 0) return 'error';
    return 'default';
  };

    const getRSIChipColor = (rsi?: number): 'success' | 'warning' | 'error' | 'default' => {
    if (!rsi) return 'default';
    if (rsi > 70) return 'error';  // Overbought
    if (rsi < 30) return 'success'; // Oversold
    if (rsi > 60 || rsi < 40) return 'warning';
    return 'default';
  };

  const getRSILinearProgressColor = (rsi?: number): 'success' | 'warning' | 'error' | 'inherit' => {
    if (!rsi) return 'inherit';
    if (rsi > 70) return 'error';  // Overbought
    if (rsi < 30) return 'success'; // Oversold
    if (rsi > 60 || rsi < 40) return 'warning';
    return 'inherit';
  };

  const getRSILabel = (rsi?: number): string => {
    if (!rsi) return 'N/A';
    if (rsi > 70) return 'Overbought';
    if (rsi < 30) return 'Oversold';
    return 'Normal';
  };

  const handleSymbolClick = (symbol: string) => {
    setExpandedSymbol(expandedSymbol === symbol ? null : symbol);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Visibility sx={{ mr: 1 }} />
            Watchlist
          </Typography>
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Visibility sx={{ mr: 1 }} />
            Watchlist
          </Typography>
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No watchlist symbols configured
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            Add symbols to your watchlist in preferences
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Visibility sx={{ mr: 1 }} />
          Watchlist ({data.length})
        </Typography>

        <List dense>
          {data.map((item) => {
            if ('error' in item || !item.quote) {
              return (
                <ListItem key={item.symbol}>
                  <ListItemText
                    primary={item.symbol}
                    secondary="Error loading data"
                  />
                </ListItem>
              );
            }

            const isExpanded = expandedSymbol === item.symbol;
            const rsi = item.historical?.technical_indicators?.rsi;

            return (
              <React.Fragment key={item.symbol}>
                <ListItem
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'grey.50' },
                    borderRadius: 1
                  }}
                  onClick={() => handleSymbolClick(item.symbol)}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body1" fontWeight="medium">
                            {item.symbol}
                          </Typography>
                          {getTrendIcon(item.quote.change_percent)}
                        </Box>
                        <Typography variant="body1" fontWeight="medium">
                          {formatCurrency(item.quote.current_price)}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip
                            label={formatPercentage(item.quote.change_percent)}
                            color={getTrendColor(item.quote.change_percent)}
                            size="small"
                          />
                          {rsi && (
                            <Chip
                              label={`RSI: ${rsi.toFixed(0)}`}
                              color={getRSIChipColor(rsi)}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Box display="flex" alignItems="center">
                          {onAnalyzeSymbol && (
                            <Tooltip title="AI Analysis">
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onAnalyzeSymbol(item.symbol);
                                }}
                              >
                                <Psychology fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {isExpanded ? <ExpandLess /> : <ExpandMore />}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>

                <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                  <Box sx={{ pl: 2, pr: 2, pb: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="caption" color="text.secondary">
                        Day Range
                      </Typography>
                      <Typography variant="caption">
                        {formatCurrency(item.quote.day_low)} - {formatCurrency(item.quote.day_high)}
                      </Typography>
                    </Box>

                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="caption" color="text.secondary">
                        Volume
                      </Typography>
                      <Typography variant="caption">
                        {item.quote?.volume?.toLocaleString() ?? 'N/A'}
                      </Typography>
                    </Box>

                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="caption" color="text.secondary">
                        Market Cap
                      </Typography>
                      <Typography variant="caption">
                        {item.quote.market_cap ? 
                          `$${(item.quote.market_cap / 1e9).toFixed(1)}B` : 
                          'N/A'
                        }
                      </Typography>
                    </Box>

                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="caption" color="text.secondary">
                        P/E Ratio
                      </Typography>
                      <Typography variant="caption">
                        {item.quote.pe_ratio ? item.quote.pe_ratio.toFixed(2) : 'N/A'}
                      </Typography>
                    </Box>

                    {/* Technical Indicators */}
                    {item.historical?.technical_indicators && (
                      <Box mt={2}>
                        <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                          Technical Indicators
                        </Typography>
                        
                        {rsi && (
                          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                            <Typography variant="caption">RSI (14)</Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              <LinearProgress
                                variant="determinate"
                                value={rsi}
                                sx={{ width: 60, height: 4 }}
                                color={getRSILinearProgressColor(rsi)}
                              />
                              <Typography variant="caption">
                                {rsi.toFixed(1)} ({getRSILabel(rsi)})
                              </Typography>
                            </Box>
                          </Box>
                        )}

                        {item.historical.technical_indicators.sma_20 && (
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="caption">SMA 20</Typography>
                            <Typography variant="caption">
                              {formatCurrency(item.historical.technical_indicators.sma_20)}
                            </Typography>
                          </Box>
                        )}

                        {item.historical.technical_indicators.sma_50 && (
                          <Box display="flex" justifyContent="space-between">
                            <Typography variant="caption">SMA 50</Typography>
                            <Typography variant="caption">
                              {formatCurrency(item.historical.technical_indicators.sma_50)}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    )}

                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      {item.timestamp && `Updated: ${new Date(item.timestamp).toLocaleTimeString()}`}
                    </Typography>
                  </Box>
                </Collapse>
              </React.Fragment>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
};

export default WatchlistWidget;