// AI Decisions widget showing recent AI trading decisions

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  PauseCircle,
  ThumbUp,
  ThumbDown,
  Psychology
} from '@mui/icons-material';

import { AIDecision } from '../types';

interface AIDecisionsWidgetProps {
  decisions: AIDecision[];
  loading: boolean;
  onFeedbackSubmit?: (
    decisionId: string, 
    feedback: { user_feedback: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'; feedback_notes?: string }
  ) => void;
}

const AIDecisionsWidget: React.FC<AIDecisionsWidgetProps> = ({ 
  decisions, 
  loading, 
  onFeedbackSubmit 
}) => {
  const [feedbackDialog, setFeedbackDialog] = useState<{
    open: boolean;
    decision: AIDecision | null;
  }>({ open: false, decision: null });
  const [feedbackForm, setFeedbackForm] = useState<{
    user_feedback: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
    feedback_notes: string;
  }>({ user_feedback: 'NEUTRAL', feedback_notes: '' });

  const getDecisionIcon = (decisionType: string) => {
    switch (decisionType) {
      case 'BUY': return <TrendingUp color="success" />;
      case 'SELL': return <TrendingDown color="error" />;
      case 'HOLD': return <PauseCircle color="disabled" />;
      default: return <PauseCircle color="disabled" />;
    }
  };

  const getDecisionColor = (decisionType: string): 'success' | 'error' | 'default' => {
    switch (decisionType) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      case 'HOLD': return 'default';
      default: return 'default';
    }
  };

  const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getFeedbackIcon = (feedback?: string) => {
    switch (feedback) {
      case 'POSITIVE': return <ThumbUp color="success" fontSize="small" />;
      case 'NEGATIVE': return <ThumbDown color="error" fontSize="small" />;
      default: return null;
    }
  };

  const handleFeedbackClick = (decision: AIDecision) => {
    setFeedbackDialog({ open: true, decision });
    setFeedbackForm({
      user_feedback: decision.user_feedback || 'NEUTRAL',
      feedback_notes: decision.feedback_notes || ''
    });
  };

  const handleFeedbackSubmit = () => {
    if (feedbackDialog.decision && onFeedbackSubmit) {
      onFeedbackSubmit(feedbackDialog.decision.decision_id, feedbackForm);
      setFeedbackDialog({ open: false, decision: null });
      setFeedbackForm({ user_feedback: 'NEUTRAL', feedback_notes: '' });
    }
  };

  const handleFeedbackClose = () => {
    setFeedbackDialog({ open: false, decision: null });
    setFeedbackForm({ user_feedback: 'NEUTRAL', feedback_notes: '' });
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
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const timeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Psychology sx={{ mr: 1 }} />
            AI Decisions
          </Typography>
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!decisions || decisions.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Psychology sx={{ mr: 1 }} />
            AI Decisions
          </Typography>
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No AI decisions yet
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            AI will analyze market conditions and generate trading recommendations
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Count pending feedback
  const pendingFeedback = decisions.filter(d => !d.user_feedback).length;

  return (
    <>
      <Card sx={{ bgcolor: 'background.paper', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ p: 3, flex: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              AI Decisions
            </Typography>
            {pendingFeedback > 0 && (
              <Button 
                variant="text" 
                size="small"
                sx={{ 
                  color: 'primary.main',
                  '&:hover': { bgcolor: 'transparent' },
                  fontSize: '0.875rem'
                }}
              >
                Feedback Needed
              </Button>
            )}
          </Box>

          <Box sx={{ 
            '& > *:not(:last-child)': { mb: 2 },
            overflowY: 'auto',
            flex: 1,
            pr: 1
          }}>
            {decisions.slice(0, 2).map((decision) => (
              <Box
                key={decision.decision_id}
                sx={{
                  p: 2,
                  borderRadius: 1,
                  bgcolor: 'rgba(128, 128, 128, 0.1)'
                }}
              >
                {/* Header with icon and decision */}
                <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getDecisionIcon(decision.decision_type)}
                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                      {decision.symbol}
                    </Typography>
                    <Chip
                      label={decision.decision_type}
                      sx={{
                        bgcolor: decision.decision_type === 'BUY' ? 'success.main' : 'error.main',
                        color: decision.decision_type === 'BUY' ? 'black' : 'white',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        height: 24
                      }}
                      size="small"
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {timeAgo(decision.created_at)}
                  </Typography>
                </Box>

                {/* Confidence indicator with circular progress */}
                <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      position: 'relative',
                      display: 'inline-flex',
                      mr: 2
                    }}
                  >
                    <CircularProgress
                      variant="determinate"
                      value={decision.confidence_score * 100}
                      size={48}
                      thickness={4}
                      sx={{
                        color: 'success.main',
                        '& .MuiCircularProgress-circle': {
                          strokeLinecap: 'round',
                        },
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexDirection: 'column'
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{ 
                          fontSize: '0.625rem',
                          fontWeight: 'bold',
                          lineHeight: 1
                        }}
                      >
                        {Math.round(decision.confidence_score * 100)}%
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{ 
                          fontSize: '0.5rem',
                          lineHeight: 1
                        }}
                      >
                        confident
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    {decision.price_target && (
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        Target: <Typography component="span" sx={{ 
                          fontFamily: '"IBM Plex Mono", monospace',
                          fontWeight: 600
                        }}>
                          {formatCurrency(decision.price_target)}
                        </Typography>
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary">
                      {decision.rationale}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>

          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ 
              mt: 2, 
              display: 'block',
              textAlign: 'center',
              fontSize: '0.75rem'
            }}
          >
            Showing {decisions.length} recent decisions
          </Typography>
        </CardContent>
      </Card>

      {/* Feedback Dialog */}
      <Dialog 
        open={feedbackDialog.open} 
        onClose={handleFeedbackClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Provide Feedback on AI Decision
        </DialogTitle>
        <DialogContent>
          {feedbackDialog.decision && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Decision: {feedbackDialog.decision.decision_type} {feedbackDialog.decision.symbol} 
                ({formatPercentage(feedbackDialog.decision.confidence_score)} confidence)
              </Typography>
              
              <Typography variant="body2" sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                {feedbackDialog.decision.rationale}
              </Typography>

              <TextField
                select
                label="Your Feedback"
                value={feedbackForm.user_feedback}
                onChange={(e) => setFeedbackForm(prev => ({ 
                  ...prev, 
                  user_feedback: e.target.value as 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' 
                }))}
                fullWidth
                margin="normal"
              >
                <MenuItem value="POSITIVE">👍 Positive - Good decision</MenuItem>
                <MenuItem value="NEUTRAL">😐 Neutral - Acceptable</MenuItem>
                <MenuItem value="NEGATIVE">👎 Negative - Poor decision</MenuItem>
              </TextField>

              <TextField
                label="Additional Notes (Optional)"
                value={feedbackForm.feedback_notes}
                onChange={(e) => setFeedbackForm(prev => ({ 
                  ...prev, 
                  feedback_notes: e.target.value 
                }))}
                multiline
                rows={3}
                fullWidth
                margin="normal"
                placeholder="Share your thoughts on this decision..."
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleFeedbackClose}>Cancel</Button>
          <Button onClick={handleFeedbackSubmit} variant="contained">
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AIDecisionsWidget;