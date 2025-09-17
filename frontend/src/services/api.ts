// API service for communicating with FastAPI backend

import axios from 'axios';
import { 
  Quote, 
  HistoricalData, 
  NewsHeadline, 
  PortfolioAnalytics, 
  AIDecision, 
  UserPreferences, 
  MarketSentiment, 
  MarketOverview, 
  WatchlistItem, 
  AIAnalysisResult, 
  HealthStatus,
  ETradeAccount,
  ETradeBalance,
  ETradePortfolio
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`🔌 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

// Health and Status
export const healthApi = {
  getHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/health');
    return response.data;
  },
};

// Market Data APIs
export const marketApi = {
  getQuote: async (symbol: string): Promise<Quote> => {
    const response = await api.get(`/api/market/quote/${symbol}`);
    return response.data;
  },

  getHistoricalData: async (
    symbol: string, 
    period: string = '1mo', 
    interval: string = '1d'
  ): Promise<HistoricalData> => {
    const response = await api.get(`/api/market/historical/${symbol}`, {
      params: { period, interval }
    });
    return response.data;
  },

  getNews: async (symbol: string, limit: number = 10): Promise<{ symbol: string; news: NewsHeadline[] }> => {
    const response = await api.get(`/api/market/news/${symbol}`, {
      params: { limit }
    });
    return response.data;
  },

  getMarketOverview: async (): Promise<MarketOverview> => {
    const response = await api.get('/api/market/overview');
    return response.data;
  },

  getWatchlistData: async (): Promise<{ watchlist: WatchlistItem[] }> => {
    const response = await api.get('/api/market/watchlist');
    return response.data;
  },
};

// Portfolio APIs
export const portfolioApi = {
  getLatestPortfolio: async (accountId?: string): Promise<PortfolioAnalytics | null> => {
    const response = await api.get('/api/portfolio/latest', {
      params: accountId ? { account_id: accountId } : {}
    });
    return response.data;
  },

  getPortfolioHistory: async (
    accountId?: string, 
    days: number = 30
  ): Promise<PortfolioAnalytics[]> => {
    const response = await api.get('/api/portfolio/history', {
      params: { 
        ...(accountId && { account_id: accountId }),
        days 
      }
    });
    return response.data;
  },
};

// AI Decision APIs
export const aiApi = {
  getDecisions: async (symbol?: string, limit: number = 50): Promise<AIDecision[]> => {
    const response = await api.get('/api/decisions', {
      params: { 
        ...(symbol && { symbol }),
        limit 
      }
    });
    return response.data;
  },

  getDecision: async (decisionId: string): Promise<AIDecision> => {
    const response = await api.get(`/api/decisions/${decisionId}`);
    return response.data;
  },

  submitFeedback: async (
    decisionId: string, 
    feedback: { 
      user_feedback: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'; 
      feedback_notes?: string; 
    }
  ): Promise<{ message: string }> => {
    const response = await api.post(`/api/decisions/${decisionId}/feedback`, feedback);
    return response.data;
  },

  analyzeSymbol: async (symbol: string): Promise<AIAnalysisResult> => {
    const response = await api.post(`/api/ai/analyze/${symbol}`);
    return response.data;
  },

  analyzeSentimentBatch: async (symbols: string[]): Promise<{
    analyzed_symbols: number;
    sentiment_scores: Record<string, number>;
    timestamp: string;
  }> => {
    const response = await api.post('/api/ai/sentiment-batch', symbols);
    return response.data;
  },
};

// User Preferences APIs
export const preferencesApi = {
  getPreferences: async (): Promise<UserPreferences> => {
    const response = await api.get('/api/preferences');
    return response.data;
  },

  updatePreferences: async (updates: Partial<UserPreferences>): Promise<UserPreferences> => {
    const response = await api.put('/api/preferences', updates);
    return response.data;
  },
};

// Market Sentiment APIs
export const sentimentApi = {
  getSentiment: async (symbol?: string, limit: number = 50): Promise<MarketSentiment[]> => {
    const response = await api.get('/api/sentiment', {
      params: { 
        ...(symbol && { symbol }),
        limit 
      }
    });
    return response.data;
  },
};

// E*TRADE APIs
export const etradeApi = {
  getAuthStatus: async (): Promise<{ authenticated: boolean }> => {
    const response = await api.get('/api/etrade/auth/status');
    return response.data;
  },

  initiateOAuth: async (useSandbox: boolean = true): Promise<{ authorization_url: string }> => {
    const response = await api.post('/api/etrade/oauth/initiate', null, {
      params: { use_sandbox: useSandbox }
    });
    return response.data;
  },

  completeOAuth: async (verificationCode: string): Promise<{ message: string }> => {
    const response = await api.post('/api/etrade/oauth/complete', {
      verification_code: verificationCode
    });
    return response.data;
  },

  getAccounts: async (): Promise<{ accounts: ETradeAccount[] }> => {
    const response = await api.get('/api/etrade/accounts');
    return response.data;
  },

  getAccountBalance: async (accountIdKey: string): Promise<ETradeBalance> => {
    const response = await api.get(`/api/etrade/accounts/${accountIdKey}/balance`);
    return response.data;
  },

  getPortfolio: async (accountIdKey: string): Promise<ETradePortfolio> => {
    const response = await api.get(`/api/etrade/accounts/${accountIdKey}/portfolio`);
    return response.data;
  },
};

// Export default api instance for custom requests
export default api;