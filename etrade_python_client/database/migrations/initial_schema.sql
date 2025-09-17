-- Initial schema for AI Trading Assistant Database
-- This SQL script creates the initial database schema

-- Portfolio Analytics Table
CREATE TABLE IF NOT EXISTS portfolio_analytics (
    portfolio_id VARCHAR(36) PRIMARY KEY,
    account_id VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    daily_change DECIMAL(15,2) NOT NULL,
    positions JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_portfolio_account ON portfolio_analytics(account_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON portfolio_analytics(timestamp);

-- AI Decisions Table
CREATE TABLE IF NOT EXISTS ai_decisions (
    decision_id VARCHAR(36) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    decision_type VARCHAR(10) NOT NULL,
    confidence_score REAL NOT NULL,
    rationale TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    executed_at DATETIME,
    outcome_value DECIMAL(15,2),
    user_feedback VARCHAR(10),
    feedback_notes TEXT,
    feedback_timestamp DATETIME,
    price_target DECIMAL(10,2)
);

CREATE INDEX IF NOT EXISTS idx_decisions_symbol ON ai_decisions(symbol);
CREATE INDEX IF NOT EXISTS idx_decisions_created ON ai_decisions(created_at);

-- Market Sentiment Table
CREATE TABLE IF NOT EXISTS market_sentiment (
    sentiment_id VARCHAR(36) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    sentiment_score REAL NOT NULL,
    news_summary TEXT NOT NULL,
    source_count INTEGER NOT NULL,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON market_sentiment(symbol);
CREATE INDEX IF NOT EXISTS idx_sentiment_analyzed ON market_sentiment(analyzed_at);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id VARCHAR(36) PRIMARY KEY,
    risk_tolerance VARCHAR(20) NOT NULL DEFAULT 'MODERATE',
    max_trade_amount DECIMAL(10,2) NOT NULL DEFAULT 1000.00,
    notification_preferences JSON NOT NULL DEFAULT '{}',
    watchlist_symbols JSON NOT NULL DEFAULT '[]',
    auto_trading_enabled BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI Learning Context Table
CREATE TABLE IF NOT EXISTS ai_learning_context (
    context_id VARCHAR(36) PRIMARY KEY,
    version INTEGER NOT NULL,
    learning_parameters JSON NOT NULL,
    feedback_summary JSON NOT NULL,
    performance_metrics JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_learning_version ON ai_learning_context(version);

-- Backup Log Table
CREATE TABLE IF NOT EXISTS backup_logs (
    backup_id VARCHAR(36) PRIMARY KEY,
    backup_filename VARCHAR(255) NOT NULL,
    backup_path VARCHAR(500) NOT NULL,
    backup_size_bytes INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    error_message TEXT
);

-- Insert default user preferences if none exist
INSERT OR IGNORE INTO user_preferences (
    user_id,
    notification_preferences,
    watchlist_symbols
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    '{"email_enabled": true, "slack_enabled": true, "trading_alerts": true, "daily_summary": true}',
    '["AAPL", "MSFT", "GOOGL", "TSLA"]'
);

-- Insert initial AI learning context
INSERT OR IGNORE INTO ai_learning_context (
    context_id,
    version,
    learning_parameters,
    feedback_summary,
    performance_metrics,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    1,
    '{"confidence_threshold": 0.7, "max_trade_amount": 1000.0, "risk_adjustment": 1.0}',
    '{"total_feedback": 0, "positive_feedback": 0, "negative_feedback": 0}',
    '{"total_decisions": 0, "successful_trades": 0, "average_return": 0.0}',
    1
);