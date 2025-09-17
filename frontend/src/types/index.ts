// TypeScript types for AI Trading Assistant

export interface Quote {
  symbol: string;
  current_price: number;
  previous_close: number;
  day_high: number;
  day_low: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

export interface HistoricalData {
  symbol: string;
  period: string;
  interval: string;
  data_points: number;
  latest_close: number;
  latest_volume: number;
  high_52w: number;
  low_52w: number;
  avg_volume: number;
  technical_indicators: TechnicalIndicators;
  timestamp: string;
}

export interface TechnicalIndicators {
  sma_20?: number;
  sma_50?: number;
  rsi?: number;
  bb_upper?: number;
  bb_lower?: number;
  bb_width?: number;
  price_position?: number;
}

export interface NewsHeadline {
  title: string;
  summary: string;
  publisher: string;
  publish_time: string;
  url: string;
  symbol: string;
}

export interface PortfolioAnalytics {
  portfolio_id: string;
  account_id: string;
  timestamp: string;
  total_value: number;
  daily_change: number;
  positions: Record<string, Position>;
  created_at: string;
}

export interface Position {
  quantity: number;
  current_price: number;
  market_value: number;
}

export interface AIDecision {
  decision_id: string;
  symbol: string;
  decision_type: 'BUY' | 'SELL' | 'HOLD';
  confidence_score: number;
  rationale: string;
  created_at: string;
  executed_at?: string;
  outcome_value?: number;
  user_feedback?: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  feedback_notes?: string;
  price_target?: number;
}

export interface UserPreferences {
  user_id: string;
  risk_tolerance: 'CONSERVATIVE' | 'MODERATE' | 'AGGRESSIVE';
  max_trade_amount: number;
  notification_preferences: NotificationPreferences;
  watchlist_symbols: string[];
  auto_trading_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  slack_enabled: boolean;
  trading_alerts: boolean;
  daily_summary?: boolean;
}

export interface MarketSentiment {
  sentiment_id: string;
  symbol: string;
  sentiment_score: number;
  news_summary: string;
  source_count: number;
  analyzed_at: string;
}

export interface MarketOverview {
  'S&P 500': MarketIndex;
  'Dow Jones': MarketIndex;
  'NASDAQ': MarketIndex;
  'Russell 2000': MarketIndex;
  'VIX': MarketIndex;
  timestamp: string;
}

export interface MarketIndex {
  price: number;
  change: number;
  change_percent: number;
}

export interface WatchlistItem {
  symbol: string;
  quote: Quote;
  historical: HistoricalData;
  timestamp: string;
}

export interface AIAnalysisResult {
  symbol: string;
  decision?: {
    decision_id: string;
    decision_type: string;
    confidence: number;
    rationale: string;
    price_target?: number;
  };
  sentiment: {
    score: number;
    summary: string;
  };
  market_data: Quote;
  message?: string;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface ApiError {
  detail: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  database: string;
}

// E*TRADE Types
export interface ETradeAccount {
  accountId: string;
  accountIdKey: string;
  accountDesc: string;
  institutionType: string;
  accountStatus: string;
}

export interface ETradeBalance {
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

export interface ETradePosition {
  symbolDescription: string;
  quantity: number;
  pricePaid: number;
  marketValue: number;
  totalGain: number;
  Quick: {
    lastTrade: number;
  };
}

export interface ETradePortfolio {
  AccountPortfolio: Array<{
    Position: ETradePosition[];
  }>;
}