// AI Decisions widget showing recent AI trading decisions

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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Psychology,
  ThumbUp,
  ThumbDown,
  Feedback,
  TrendingUp,
  TrendingDown,
  PauseCircle
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
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              <Psychology sx={{ mr: 1 }} />
              AI Decisions
            </Typography>
            {pendingFeedback > 0 && (
              <Badge badgeContent={pendingFeedback} color="primary">
                <Chip
                  label="Feedback Needed"
                  color="primary"
                  size="small"
                  variant="outlined"
                />
              </Badge>
            )}
          </Box>

          <List dense>
            {decisions.map((decision) => (
              <ListItem
                key={decision.decision_id}
                sx={{
                  border: 1,
                  borderColor: 'grey.200',
                  borderRadius: 1,
                  mb: 1,
                  bgcolor: 'background.paper'
                }}
              >
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getDecisionIcon(decision.decision_type)}
                        <Typography variant="body1" fontWeight="medium">
                          {decision.symbol}
                        </Typography>
                        <Chip
                          label={decision.decision_type}
                          color={getDecisionColor(decision.decision_type)}
                          size="small"
                        />
                      </Box>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getFeedbackIcon(decision.user_feedback)}
                        <Tooltip title="Provide Feedback">
                          <IconButton
                            size="small"
                            onClick={() => handleFeedbackClick(decision)}
                            color={decision.user_feedback ? 'default' : 'primary'}
                          >
                            <Feedback fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="caption" color="text.secondary">
                          Confidence: {formatPercentage(decision.confidence_score)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {timeAgo(decision.created_at)}
                        </Typography>
                      </Box>
                      
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                          label={`${formatPercentage(decision.confidence_score)} confident`}
                          color={getConfidenceColor(decision.confidence_score)}
                          size="small"
                          variant="outlined"
                        />
                        {decision.price_target && (
                          <Chip
                            label={`Target: ${formatCurrency(decision.price_target)}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>

                      <Typography variant="body2" color="text.secondary">
                        {decision.rationale}
                      </Typography>

                      {decision.user_feedback && decision.feedback_notes && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          Your feedback: {decision.feedback_notes}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
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