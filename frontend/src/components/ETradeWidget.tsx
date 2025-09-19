// E*TRADE Account Widget for AI Trading Assistant

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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton
} from '@mui/material';
import {
  AccountBalance,
  Link,
  LinkOff,
  Refresh,
  AccountBalanceWallet,
  MoreVert,
} from '@mui/icons-material';

import api from '../services/api';

interface ETradeAccount {
  accountId: string;
  accountIdKey: string;
  accountDesc: string;
  institutionType: string;
  accountStatus: string;
}

interface ETradeBalance {
  accountId: string;
  accountDescription: string;
  Computed: {
    RealTimeValues: {
      totalAccountValue: number;
      cashBalance: number;
    };
    marginBuyingPower: number;
    cashBuyingPower: number;
  };
}

interface ETradePosition {
  symbolDescription: string;
  quantity: number;
  pricePaid: number;
  marketValue: number;
  totalGain: number;
  Quick: {
    lastTrade: number;
  };
}

interface ETradePortfolio {
  AccountPortfolio: Array<{
    Position: ETradePosition[];
  }>;
}

const ETradeWidget: React.FC = () => {
  // State management
  const [accounts, setAccounts] = useState<ETradeAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<ETradeAccount | null>(null);
  const [balance, setBalance] = useState<ETradeBalance | null>(null);
  const [portfolio, setPortfolio] = useState<ETradePortfolio | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<boolean>(false);
  const [authStep, setAuthStep] = useState<'initial' | 'awaiting_code' | 'authenticated'>('initial');
  const [verificationCode, setVerificationCode] = useState('');

  const loadAccountData = useCallback(async (account: ETradeAccount) => {
    try {
      setLoading(true);
      setError(null);
      
      // Load balance
      const balanceResponse = await api.get(`/api/etrade/accounts/${account.accountIdKey}/balance`);
      setBalance(balanceResponse.data);
      
      // Load portfolio
      const portfolioResponse = await api.get(`/api/etrade/accounts/${account.accountIdKey}/portfolio`);
      setPortfolio(portfolioResponse.data);
    } catch (error) {
      console.error('Failed to load E*TRADE account data:', error);
      setError('Failed to load E*TRADE account data');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAccounts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/api/etrade/accounts');
      setAccounts(response.data.accounts);
      
      // Select the first account by default
      if (response.data.accounts.length > 0) {
        setSelectedAccount(response.data.accounts[0]);
        loadAccountData(response.data.accounts[0]);
      }
    } catch (error) {
      console.error('Failed to load E*TRADE accounts:', error);
      setError('Failed to load E*TRADE accounts');
    } finally {
      setLoading(false);
    }
  }, [loadAccountData]);

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
    
    if (account) {
      loadAccountData(account);
    }
  };

  const initiateOAuth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post('/api/etrade/oauth/initiate', null, {
        params: { use_sandbox: true }
      });
      
      // Open authorization URL in new tab
      window.open(response.data.authorization_url, '_blank');
      
      // Move to the next step in the auth flow
      setAuthStep('awaiting_code');
    } catch (error) {
      console.error('Failed to initiate E*TRADE OAuth:', error);
      setError('Failed to initiate E*TRADE authentication');
    } finally {
      setLoading(false);
    }
  };

  const completeOAuth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await api.post('/api/etrade/oauth/complete', {
        verification_code: verificationCode
      });
      
      setAuthStep('authenticated');
      setVerificationCode('');
      
      // Check auth status and load accounts
      await checkAuthStatus();
    } catch (error) {
      console.error('Failed to complete E*TRADE OAuth:', error);
      setError('Failed to complete E*TRADE authentication');
    } finally {
      setLoading(false);
    }
  };

  const disconnectETrade = async () => {
    try {
      // In a real implementation, you would revoke the OAuth tokens
      setAuthStatus(false);
      setAccounts([]);
      setSelectedAccount(null);
      setBalance(null);
      setPortfolio(null);
    } catch (error) {
      console.error('Failed to disconnect E*TRADE:', error);
      setError('Failed to disconnect E*TRADE');
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

  const formatPercentage = (value: number, total: number): string => {
    const percentage = (value / total) * 100;
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(percentage / 100);
  };

  if (authStep !== 'authenticated') {
    return (
      <Card>
        <CardHeader
          title="E*TRADE Account"
          subheader="Connect your E*TRADE account to view portfolio data"
          avatar={<AccountBalance />}
        />
        <CardContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          
                    {authStep === 'initial' && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" gutterBottom>
                Connect your E*TRADE account to view real-time portfolio data and execute trades.
              </Typography>
              <Button
                variant="contained"
                startIcon={<Link />}
                onClick={initiateOAuth}
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Connect E*TRADE'}
              </Button>
              <Typography variant="caption" display="block" sx={{ mt: 2 }}>
                You will be redirected to E*TRADE to authorize this application.
              </Typography>
            </Box>
          )}

          {authStep === 'awaiting_code' && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" gutterBottom>
                Enter the verification code from E*TRADE to complete the connection.
              </Typography>
              <TextField
                autoFocus
                margin="dense"
                label="Verification Code"
                variant="outlined"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                sx={{ mt: 1, mb: 2, maxWidth: 300, mx: 'auto' }}
              />
              <Button
                variant="contained"
                onClick={completeOAuth}
                disabled={!verificationCode || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Complete Authentication'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ bgcolor: 'background.paper' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <AccountBalanceWallet sx={{ color: 'text.secondary' }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                E*TRADE Account
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Real-time portfolio and account information
              </Typography>
            </Box>
          </Box>
          <Box>
            <IconButton sx={{ color: 'text.secondary' }}>
              <Refresh />
            </IconButton>
            <IconButton sx={{ color: 'text.secondary', ml: 1 }}>
              <MoreVert />
            </IconButton>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {loading && !accounts.length && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress />
          </Box>
        )}
        
        {accounts.length > 0 && (
          <>
            {/* Account Selector */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Account
              </Typography>
              <Select
                value={selectedAccount?.accountIdKey || ''}
                onChange={handleAccountChange}
                fullWidth
                size="small"
                sx={{
                  bgcolor: 'rgba(128, 128, 128, 0.1)',
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:focus': {
                    outline: 'none',
                    borderColor: 'primary.main'
                  }
                }}
              >
                {accounts.map((account) => (
                  <MenuItem key={account.accountIdKey} value={account.accountIdKey}>
                    Brokerage ({account.accountId})
                  </MenuItem>
                ))}
              </Select>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default ETradeWidget;