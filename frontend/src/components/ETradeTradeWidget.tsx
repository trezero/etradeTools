// E*TRADE Trade Execution Widget for AI Trading Assistant

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  CircularProgress,
  Alert,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText
} from '@mui/material';
import {
  PlayArrow,
  SwapHoriz,
  CheckCircle,
  Error,
  Link
} from '@mui/icons-material';

import api from '../services/api';

interface ETradeAccount {
  accountId: string;
  accountIdKey: string;
  accountDesc: string;
  institutionType: string;
  accountStatus: string;
}

interface ETradeOrderPreview {
  PreviewIds: Array<{ previewId: string }>;
  Order: Array<{
    Instrument: Array<{
      orderAction: string;
      quantity: number;
      Product: {
        symbol: string;
      };
      symbolDescription: string;
    }>;
    priceType: string;
    limitPrice?: number;
    orderTerm: string;
    estimatedCommission: number;
    estimatedTotalAmount: number;
  }>;
}

const ETradeTradeWidget: React.FC = () => {
  // State management
  const [accounts, setAccounts] = useState<ETradeAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<ETradeAccount | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<boolean>(false);
  const [symbol, setSymbol] = useState('');
  const [orderAction, setOrderAction] = useState('BUY');
  const [quantity, setQuantity] = useState(1);
  const [priceType, setPriceType] = useState('MARKET');
  const [orderTerm, setOrderTerm] = useState('GOOD_FOR_DAY');
  const [limitPrice, setLimitPrice] = useState<number | null>(null);
  const [preview, setPreview] = useState<ETradeOrderPreview | null>(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [confirmationDialogOpen, setConfirmationDialogOpen] = useState(false);
  const [orderResult, setOrderResult] = useState<{ success: boolean; message: string } | null>(null);

  const loadAccounts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/api/etrade/accounts');
      setAccounts(response.data.accounts);
      
      // Select the first account by default
      if (response.data.accounts.length > 0) {
        setSelectedAccount(response.data.accounts[0]);
      }
    } catch (error) {
      console.error('Failed to load E*TRADE accounts:', error);
      setError('Failed to load E*TRADE accounts');
    } finally {
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = useCallback(async () => {
    try {
      const response = await api.get('/api/etrade/auth/status');
      setAuthStatus(response.data.authenticated);
      
      if (response.data.authenticated) {
        loadAccounts();
      }
    } catch (error) {
      console.error('Failed to check E*TRADE auth status:', error);
      setError('Failed to check E*TRADE authentication status');
    }
  }, [loadAccounts]);

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const handleAccountChange = (event: any) => {
    const accountIdKey = event.target.value;
    const account = accounts.find(acc => acc.accountIdKey === accountIdKey) || null;
    setSelectedAccount(account);
  };

  const previewOrder = async () => {
    if (!selectedAccount || !symbol) {
      setError('Please select an account and enter a symbol');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post(`/api/etrade/accounts/${selectedAccount.accountIdKey}/orders/preview`, {
        symbol: symbol.toUpperCase(),
        order_action: orderAction,
        quantity: quantity,
        price_type: priceType,
        order_term: orderTerm,
        limit_price: priceType === 'LIMIT' ? limitPrice : null
      });
      
      setPreview(response.data);
      setPreviewDialogOpen(true);
    } catch (error: any) {
      console.error('Failed to preview order:', error);
      setError(error.response?.data?.detail || 'Failed to preview order');
    } finally {
      setLoading(false);
    }
  };

  const placeOrder = async () => {
    if (!selectedAccount || !symbol || !preview) {
      setError('Missing required information to place order');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setPreviewDialogOpen(false);
      
      const response = await api.post(`/api/etrade/accounts/${selectedAccount.accountIdKey}/orders/place`, {
        symbol: symbol.toUpperCase(),
        order_action: orderAction,
        quantity: quantity,
        price_type: priceType,
        order_term: orderTerm,
        limit_price: priceType === 'LIMIT' ? limitPrice : null
      });
      
      setOrderResult({
        success: true,
        message: `Order placed successfully. Order ID: ${response.data.Order[0].OrderDetail[0].orderId}`
      });
    } catch (error: any) {
      console.error('Failed to place order:', error);
      setOrderResult({
        success: false,
        message: error.response?.data?.detail || 'Failed to place order'
      });
    } finally {
      setLoading(false);
      setConfirmationDialogOpen(true);
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

  if (!authStatus) {
    return (
      <Card sx={{ bgcolor: 'background.paper' }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" gap={2} sx={{ mb: 3 }}>
            <Link sx={{ color: 'text.secondary' }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                E*TRADE Trading
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Connect your E*TRADE account to execute trades
              </Typography>
            </Box>
          </Box>
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Please connect your E*TRADE account in the E*TRADE Account widget first.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ bgcolor: 'background.paper' }}>
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" gap={2} sx={{ mb: 3 }}>
          <Link sx={{ color: 'text.secondary' }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              E*TRADE Trading
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Connect your E*TRADE account to execute trades
            </Typography>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {orderResult && (
          <Alert 
            severity={orderResult.success ? "success" : "error"} 
            sx={{ mb: 2 }}
            onClose={() => setOrderResult(null)}
          >
            {orderResult.message}
          </Alert>
        )}
        
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Typography variant="body2" color="text.secondary">
            Please connect your E*TRADE account in the E*TRADE Account widget first.
          </Typography>
        </Box>
      </CardContent>
      
      {/* Order Preview Dialog */}
      <Dialog open={previewDialogOpen} onClose={() => setPreviewDialogOpen(false)}>
        <DialogTitle>Order Preview</DialogTitle>
        <DialogContent>
          {preview && preview.Order && preview.Order.length > 0 && (
            <Box>
              <DialogContentText>
                Please review your order details before placing:
              </DialogContentText>
              
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Symbol" 
                    secondary={preview.Order[0].Instrument[0].Product.symbol} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Action" 
                    secondary={preview.Order[0].Instrument[0].orderAction} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Quantity" 
                    secondary={preview.Order[0].Instrument[0].quantity} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Price Type" 
                    secondary={preview.Order[0].priceType} 
                  />
                </ListItem>
                {preview.Order[0].limitPrice && (
                  <ListItem>
                    <ListItemText 
                      primary="Limit Price" 
                      secondary={formatCurrency(preview.Order[0].limitPrice)} 
                    />
                  </ListItem>
                )}
                <ListItem>
                  <ListItemText 
                    primary="Order Term" 
                    secondary={preview.Order[0].orderTerm} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Estimated Commission" 
                    secondary={formatCurrency(preview.Order[0].estimatedCommission)} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Estimated Total" 
                    secondary={formatCurrency(preview.Order[0].estimatedTotalAmount)} 
                  />
                </ListItem>
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={placeOrder} 
            variant="contained"
            startIcon={<PlayArrow />}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Place Order'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Order Confirmation Dialog */}
      <Dialog open={confirmationDialogOpen} onClose={() => setConfirmationDialogOpen(false)}>
        <DialogTitle>
          {orderResult?.success ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle color="success" />
              Order Placed Successfully
            </Box>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Error color="error" />
              Order Failed
            </Box>
          )}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {orderResult?.message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setConfirmationDialogOpen(false);
              setOrderResult(null);
              setPreview(null);
            }}
            variant="contained"
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default ETradeTradeWidget;