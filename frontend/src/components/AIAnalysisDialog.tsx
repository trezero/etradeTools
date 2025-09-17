// AI Analysis dialog for triggering symbol analysis

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  TrendingDown,
  PauseCircle,
  ShowChart
} from '@mui/icons-material';

import { AIAnalysisResult } from '../types';
import { aiApi } from '../services/api';

interface AIAnalysisDialogProps {
  open: boolean;
  onClose: () => void;
  onAnalysisComplete: (result: AIAnalysisResult) => void;
}

const AIAnalysisDialog: React.FC<AIAnalysisDialogProps> = ({
  open,
  onClose,
  onAnalysisComplete
}) => {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AIAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSymbolChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSymbol(event.target.value.toUpperCase());
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!symbol.trim()) {
      setError('Please enter a symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await aiApi.analyzeSymbol(symbol.trim());
      setResult(analysisResult);
      onAnalysisComplete(analysisResult);
    } catch (error: any) {
      console.error('AI analysis failed:', error);
      setError(
        error.response?.data?.detail || 
        error.message || 
        'Analysis failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSymbol('');
    setResult(null);
    setError(null);
    setLoading(false);
    onClose();
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !loading) {
      handleAnalyze();
    }
  };

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
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
      signDisplay: 'always'
    }).format(value / 100);
  };

  const getDecisionIcon = (decisionType?: string) => {
    switch (decisionType) {
      case 'BUY': return <TrendingUp color="success" />;
      case 'SELL': return <TrendingDown color="error" />;
      case 'HOLD': return <PauseCircle color="disabled" />;
      default: return <ShowChart color="disabled" />;
    }
  };

  const getDecisionColor = (decisionType?: string): 'success' | 'error' | 'default' => {
    switch (decisionType) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      case 'HOLD': return 'default';
      default: return 'default';
    }
  };

  const getConfidenceColor = (confidence?: number): 'success' | 'warning' | 'error' => {
    if (!confidence) return 'error';
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getSentimentColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score > 0.3) return 'success';
    if (score > -0.3) return 'warning';
    return 'error';
  };

  const getSentimentLabel = (score: number): string => {
    if (score > 0.5) return 'Very Positive';
    if (score > 0.3) return 'Positive';
    if (score > -0.3) return 'Neutral';
    if (score > -0.5) return 'Negative';
    return 'Very Negative';
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '400px' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Psychology color="primary" />
          AI Market Analysis
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <TextField
            label="Stock Symbol"
            value={symbol}
            onChange={handleSymbolChange}
            onKeyPress={handleKeyPress}
            placeholder="e.g., AAPL, MSFT, GOOGL"
            fullWidth
            autoFocus
            disabled={loading}
            helperText="Enter a stock symbol to analyze"
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" py={4}>
            <CircularProgress />
            <Typography variant="body2" sx={{ ml: 2 }}>
              Analyzing {symbol}... This may take a few moments.
            </Typography>
          </Box>
        )}

        {result && (
          <Box>
            {/* Market Data Summary */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {result.symbol} - Market Data
                </Typography>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h4">
                    {formatCurrency(result.market_data.current_price)}
                  </Typography>
                  <Chip
                    label={formatPercentage(result.market_data.change_percent)}
                    color={result.market_data.change_percent > 0 ? 'success' : 'error'}
                  />
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    Day Range
                  </Typography>
                  <Typography variant="body2">
                    {formatCurrency(result.market_data.day_low)} - {formatCurrency(result.market_data.day_high)}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Volume
                  </Typography>
                  <Typography variant="body2">
                    {result.market_data.volume.toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>

            {/* AI Decision */}
            {result.decision ? (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Trading Decision
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    {getDecisionIcon(result.decision.decision_type)}
                    <Chip
                      label={result.decision.decision_type}
                      color={getDecisionColor(result.decision.decision_type)}
                      size="medium"
                    />
                    <Chip
                      label={`${(result.decision.confidence * 100).toFixed(0)}% Confident`}
                      color={getConfidenceColor(result.decision.confidence)}
                      variant="outlined"
                    />
                  </Box>

                  {result.decision.price_target && (
                    <Box mb={2}>
                      <Typography variant="body2" color="text.secondary">
                        Price Target: {formatCurrency(result.decision.price_target)}
                      </Typography>
                    </Box>
                  )}

                  <Typography variant="body1" sx={{ 
                    p: 2, 
                    bgcolor: 'grey.50', 
                    borderRadius: 1,
                    border: 1,
                    borderColor: 'grey.200'
                  }}>
                    {result.decision.rationale}
                  </Typography>
                </CardContent>
              </Card>
            ) : (
              result.message && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  {result.message}
                </Alert>
              )
            )}

            {/* Market Sentiment */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Sentiment Analysis
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Chip
                    label={`${getSentimentLabel(result.sentiment.score)} (${result.sentiment.score.toFixed(2)})`}
                    color={getSentimentColor(result.sentiment.score)}
                  />
                </Box>
                <Typography variant="body1">
                  {result.sentiment.summary}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          Close
        </Button>
        <Button 
          onClick={handleAnalyze} 
          variant="contained" 
          disabled={loading || !symbol.trim()}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AIAnalysisDialog;