// Watchlist widget showing tracked symbols

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  IconButton
} from '@mui/material';
import {
  Visibility,
  TrendingUp,
  TrendingDown,
  Analytics,
  Error as ErrorIcon
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

  const formatPrice = (price: number): string => {
    return price.toFixed(2);
  };

  const formatChange = (change: number, changePercent: number): string => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
  };

  const getChangeColor = (change: number): string => {
    return change >= 0 ? '#0ECB81' : '#F6465D';
  };

  if (loading) {
    return (
      <Card sx={{ 
        bgcolor: '#1A1E29', 
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 2
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" sx={{ mb: 3 }}>
            <Visibility sx={{ mr: 1.5, color: '#6B7280' }} />
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 600, 
                color: '#F9FAFB',
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              Watchlist
            </Typography>
          </Box>
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <CircularProgress sx={{ color: '#3B82F6' }} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card sx={{ 
        bgcolor: '#1A1E29', 
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 2
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" sx={{ mb: 3 }}>
            <Visibility sx={{ mr: 1.5, color: '#6B7280' }} />
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 600, 
                color: '#F9FAFB',
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              Watchlist
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Visibility sx={{ fontSize: 48, color: '#6B7280', mb: 2 }} />
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#9CA3AF', 
                mb: 1,
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              No watchlist symbols configured
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#6B7280',
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              Add symbols to your watchlist in preferences
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ 
      bgcolor: '#1A1E29', 
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 2
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center">
            <Visibility sx={{ mr: 1.5, color: '#6B7280' }} />
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 600, 
                color: '#F9FAFB',
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              Watchlist
            </Typography>
          </Box>
          <Typography 
            variant="body2" 
            sx={{ 
              color: '#6B7280',
              fontFamily: 'IBM Plex Mono, monospace',
              bgcolor: 'rgba(59, 130, 246, 0.1)',
              px: 1.5,
              py: 0.5,
              borderRadius: 1
            }}
          >
            {data.length} symbols
          </Typography>
        </Box>

        <Box sx={{ '& > *:not(:last-child)': { mb: 2 } }}>
          {data.map((item) => {
            if ('error' in item || !item.quote) {
              return (
                <Box 
                  key={item.symbol}
                  sx={{
                    p: 2.5,
                    bgcolor: 'rgba(244, 70, 93, 0.1)',
                    border: '1px solid rgba(244, 70, 93, 0.2)',
                    borderRadius: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <Box display="flex" alignItems="center">
                    <ErrorIcon sx={{ mr: 1.5, color: '#F6465D', fontSize: 20 }} />
                    <Box>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 600, 
                          mb: 0.5,
                          color: '#F9FAFB',
                          fontFamily: 'Inter, system-ui, sans-serif'
                        }}
                      >
                        {item.symbol}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#F6465D',
                          fontFamily: 'Inter, system-ui, sans-serif'
                        }}
                      >
                        Failed to load data
                      </Typography>
                    </Box>
                  </Box>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      color: '#6B7280',
                      fontFamily: 'IBM Plex Mono, monospace'
                    }}
                  >
                    ERROR
                  </Typography>
                </Box>
              );
            }

            const quote = item.quote;
            const change = quote.change || 0;
            const changePercent = quote.change_percent || 0;
            const price = quote.current_price || 0;

            return (
              <Box 
                key={item.symbol}
                sx={{
                  p: 2.5,
                  bgcolor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: 1.5,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                    borderColor: 'rgba(59, 130, 246, 0.3)'
                  }
                }}
              >
                <Box display="flex" alignItems="center" flex={1}>
                  {change >= 0 ? (
                    <TrendingUp sx={{ mr: 1.5, color: '#0ECB81', fontSize: 20 }} />
                  ) : (
                    <TrendingDown sx={{ mr: 1.5, color: '#F6465D', fontSize: 20 }} />
                  )}
                  <Box flex={1}>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        fontWeight: 600, 
                        mb: 0.5,
                        color: '#F9FAFB',
                        fontFamily: 'Inter, system-ui, sans-serif'
                      }}
                    >
                      {item.symbol}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#9CA3AF',
                        fontFamily: 'Inter, system-ui, sans-serif'
                      }}
                    >
                      {item.symbol} Stock
                    </Typography>
                  </Box>
                </Box>

                <Box display="flex" alignItems="center" gap={2}>
                  <Box textAlign="right">
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        fontWeight: 600,
                        color: '#F9FAFB',
                        fontFamily: 'IBM Plex Mono, monospace',
                        mb: 0.5
                      }}
                    >
                      ${formatPrice(price)}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: getChangeColor(change),
                        fontFamily: 'IBM Plex Mono, monospace',
                        fontWeight: 500
                      }}
                    >
                      {formatChange(change, changePercent)}
                    </Typography>
                  </Box>

                  {onAnalyzeSymbol && (
                    <IconButton
                      size="small"
                      onClick={() => onAnalyzeSymbol(item.symbol)}
                      sx={{
                        color: '#6B7280',
                        '&:hover': {
                          color: '#3B82F6',
                          bgcolor: 'rgba(59, 130, 246, 0.1)'
                        }
                      }}
                    >
                      <Analytics fontSize="small" />
                    </IconButton>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

export default WatchlistWidget;