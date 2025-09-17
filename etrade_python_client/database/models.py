"""SQLAlchemy models for AI trading assistant database."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SQLEnum, Float, Integer, 
    String, Text, JSON, DECIMAL, UUID
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class DecisionType(str, Enum):
    """AI decision types for trading recommendations."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"


class UserFeedback(str, Enum):
    """User feedback on AI decisions."""
    GOOD = "GOOD"
    BAD = "BAD"
    NEUTRAL = "NEUTRAL"


class RiskTolerance(str, Enum):
    """User risk tolerance levels."""
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class PortfolioAnalytics(Base):
    """Portfolio analytics and historical performance tracking."""
    
    __tablename__ = "portfolio_analytics"
    
    portfolio_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    total_value: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    daily_change: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    positions: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AIDecision(Base):
    """AI trading decisions and recommendations with user feedback."""
    
    __tablename__ = "ai_decisions"
    
    decision_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    decision_type: Mapped[DecisionType] = mapped_column(SQLEnum(DecisionType), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome_value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(15, 2), nullable=True)
    user_feedback: Mapped[Optional[UserFeedback]] = mapped_column(SQLEnum(UserFeedback), nullable=True)
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    price_target: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)


class MarketSentiment(Base):
    """Market sentiment analysis from news and social media."""
    
    __tablename__ = "market_sentiment"
    
    sentiment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    news_summary: Mapped[str] = mapped_column(Text, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class UserPreferences(Base):
    """User trading preferences and risk tolerance settings."""
    
    __tablename__ = "user_preferences"
    
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_tolerance: Mapped[RiskTolerance] = mapped_column(SQLEnum(RiskTolerance), nullable=False, default=RiskTolerance.MODERATE)
    max_trade_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False, default=Decimal('1000.00'))
    notification_preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    watchlist_symbols: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    auto_trading_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AILearningContext(Base):
    """AI learning parameters and context adjustments."""
    
    __tablename__ = "ai_learning_context"
    
    context_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    version: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    learning_parameters: Mapped[dict] = mapped_column(JSON, nullable=False)
    feedback_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    performance_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BackupLog(Base):
    """Database backup operation logs."""
    
    __tablename__ = "backup_logs"
    
    backup_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    backup_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    backup_path: Mapped[str] = mapped_column(String(500), nullable=False)
    backup_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)