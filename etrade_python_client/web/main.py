"""FastAPI web application for AI Trading Assistant."""

from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

# Import our database components
from ..database.database import init_database, get_db_session, close_database
from ..database.models import (
    PortfolioAnalytics, AIDecision, UserPreferences, MarketSentiment,
    DecisionType, RiskTolerance, UserFeedback
)
from ..utils.config_manager import ConfigManager
from ..services.ai_trading_service import AITradingService
from ..services.market_data_service import MarketDataService
from ..services.notification_service import notification_service
from ..services.etrade_auth import ETradeAuth
from ..services.etrade_account_service import ETradeAccountService
from ..services.etrade_order_service import ETradeOrderService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration and services
config_manager = ConfigManager()
ai_service = AITradingService()
market_service = MarketDataService()

# E*TRADE services
etrade_auth = ETradeAuth()
etrade_account_service = ETradeAccountService(etrade_auth)
etrade_order_service = ETradeOrderService(etrade_auth)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting AI Trading Assistant...")
    await init_database()
    logger.info("✅ Database initialized")
    
    # Create backup directory
    import os
    backup_dir = config_manager.get_backup_location()
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"✅ Backup directory ready: {backup_dir}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Trading Assistant...")
    await close_database()
    logger.info("✅ Database connections closed")


# FastAPI app instance
app = FastAPI(
    title="AI Trading Assistant",
    description="AI-powered trading assistant built on E*TRADE API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class PortfolioResponse(BaseModel):
    portfolio_id: str
    account_id: str
    timestamp: datetime
    total_value: Decimal
    daily_change: Decimal
    positions: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class AIDecisionResponse(BaseModel):
    decision_id: str
    symbol: str
    decision_type: DecisionType
    confidence_score: float
    rationale: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    outcome_value: Optional[Decimal] = None
    user_feedback: Optional[UserFeedback] = None
    feedback_notes: Optional[str] = None
    price_target: Optional[Decimal] = None

    class Config:
        from_attributes = True


class UserPreferencesResponse(BaseModel):
    user_id: str
    risk_tolerance: RiskTolerance
    max_trade_amount: Decimal
    notification_preferences: Dict[str, Any]
    watchlist_symbols: List[str]
    auto_trading_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    risk_tolerance: Optional[RiskTolerance] = None
    max_trade_amount: Optional[Decimal] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    watchlist_symbols: Optional[List[str]] = None
    auto_trading_enabled: Optional[bool] = None


class DecisionFeedback(BaseModel):
    user_feedback: UserFeedback
    feedback_notes: Optional[str] = None


class MarketSentimentResponse(BaseModel):
    sentiment_id: str
    symbol: str
    sentiment_score: float
    news_summary: str
    source_count: int
    analyzed_at: datetime

    class Config:
        from_attributes = True


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📡 WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"📡 WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"❌ Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSockets."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"❌ Failed to broadcast to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected WebSockets
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "connected"
    }


# Portfolio endpoints
@app.get("/api/portfolio/latest", response_model=Optional[PortfolioResponse])
async def get_latest_portfolio(
    account_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get the latest portfolio analytics."""
    query = select(PortfolioAnalytics).order_by(desc(PortfolioAnalytics.timestamp))
    
    if account_id:
        query = query.where(PortfolioAnalytics.account_id == account_id)
    
    result = await db.execute(query.limit(1))
    portfolio = result.scalar_one_or_none()
    
    return portfolio


@app.get("/api/portfolio/history", response_model=List[PortfolioResponse])
async def get_portfolio_history(
    account_id: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db_session)
):
    """Get portfolio history for the specified number of days."""
    since_date = datetime.now() - timedelta(days=days)
    
    query = select(PortfolioAnalytics).where(
        PortfolioAnalytics.timestamp >= since_date
    ).order_by(desc(PortfolioAnalytics.timestamp))
    
    if account_id:
        query = query.where(PortfolioAnalytics.account_id == account_id)
    
    result = await db.execute(query)
    portfolios = result.scalars().all()
    
    return portfolios


# AI Decision endpoints
@app.get("/api/decisions", response_model=List[AIDecisionResponse])
async def get_ai_decisions(
    symbol: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """Get AI trading decisions."""
    query = select(AIDecision).order_by(desc(AIDecision.created_at)).limit(limit)
    
    if symbol:
        query = query.where(AIDecision.symbol == symbol)
    
    result = await db.execute(query)
    decisions = result.scalars().all()
    
    return decisions


@app.get("/api/decisions/{decision_id}", response_model=AIDecisionResponse)
async def get_ai_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get specific AI decision by ID."""
    result = await db.execute(
        select(AIDecision).where(AIDecision.decision_id == decision_id)
    )
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decision


@app.post("/api/decisions/{decision_id}/feedback")
async def submit_decision_feedback(
    decision_id: str,
    feedback: DecisionFeedback,
    db: AsyncSession = Depends(get_db_session)
):
    """Submit feedback for an AI decision."""
    result = await db.execute(
        select(AIDecision).where(AIDecision.decision_id == decision_id)
    )
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    # Update decision with feedback
    decision.user_feedback = feedback.user_feedback
    decision.feedback_notes = feedback.feedback_notes
    decision.feedback_timestamp = datetime.now()
    
    await db.commit()
    
    # Broadcast feedback update via WebSocket
    await manager.broadcast(f"feedback_updated:{decision_id}:{feedback.user_feedback.value}")
    
    return {"message": "Feedback submitted successfully"}


# User preferences endpoints
@app.get("/api/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(db: AsyncSession = Depends(get_db_session)):
    """Get user preferences."""
    result = await db.execute(select(UserPreferences).limit(1))
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return preferences


@app.put("/api/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    updates: UserPreferencesUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update user preferences."""
    result = await db.execute(select(UserPreferences).limit(1))
    preferences = result.scalar_one_or_none()
    
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Update fields if provided
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)
    
    preferences.updated_at = datetime.now()
    await db.commit()
    
    # Broadcast preferences update
    await manager.broadcast("preferences_updated")
    
    return preferences


# Market sentiment endpoints
@app.get("/api/sentiment", response_model=List[MarketSentimentResponse])
async def get_market_sentiment(
    symbol: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """Get market sentiment analysis."""
    query = select(MarketSentiment).order_by(desc(MarketSentiment.analyzed_at)).limit(limit)
    
    if symbol:
        query = query.where(MarketSentiment.symbol == symbol)
    
    result = await db.execute(query)
    sentiments = result.scalars().all()
    
    return sentiments


# Market data endpoints
@app.get("/api/market/quote/{symbol}")
async def get_real_time_quote(symbol: str):
    """Get real-time quote for a symbol."""
    quote_data = await market_service.get_real_time_quote(symbol.upper())
    return quote_data


@app.get("/api/market/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """Get historical data for technical analysis."""
    historical_data = await market_service.get_historical_data(
        symbol.upper(), period, interval
    )
    return historical_data


@app.get("/api/market/news/{symbol}")
async def get_news_headlines(symbol: str, limit: int = 10):
    """Get recent news headlines for a symbol."""
    news = await market_service.get_news_headlines(symbol.upper(), limit)
    return {"symbol": symbol.upper(), "news": news}


@app.get("/api/market/overview")
async def get_market_overview():
    """Get market overview with major indices."""
    overview = await market_service.get_market_overview()
    return overview


@app.get("/api/market/watchlist")
async def get_watchlist_data(db: AsyncSession = Depends(get_db_session)):
    """Get comprehensive data for user's watchlist symbols."""
    # Get user preferences to find watchlist
    result = await db.execute(select(UserPreferences).limit(1))
    preferences = result.scalar_one_or_none()
    
    if not preferences or not preferences.watchlist_symbols:
        return {"watchlist": [], "message": "No watchlist symbols configured"}
    
    watchlist_data = await market_service.get_watchlist_data(preferences.watchlist_symbols)
    return {"watchlist": watchlist_data}


# AI analysis endpoints
@app.post("/api/ai/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Trigger AI analysis for a symbol and generate trading decision."""
    try:
        symbol = symbol.upper()
        
        # Get user preferences
        result = await db.execute(select(UserPreferences).limit(1))
        user_preferences = result.scalar_one_or_none()
        
        if not user_preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        # Gather market data
        quote_data = await market_service.get_real_time_quote(symbol)
        historical_data = await market_service.get_historical_data(symbol)
        news_headlines = await market_service.get_news_headlines(symbol, limit=5)
        
        # Analyze sentiment
        sentiment_score, sentiment_summary = await ai_service.analyze_market_sentiment(
            symbol, quote_data, [h.get('title', '') for h in news_headlines]
        )
        
        # Store sentiment analysis
        market_sentiment = MarketSentiment(
            symbol=symbol,
            sentiment_score=sentiment_score,
            news_summary=sentiment_summary,
            source_count=len(news_headlines)
        )
        db.add(market_sentiment)
        
        # Generate trading decision
        portfolio_data = {}  # Would get from E*TRADE API in full implementation
        sentiment_data = {'sentiment_score': sentiment_score, 'summary': sentiment_summary}
        
        ai_decision = await ai_service.generate_trading_decision(
            symbol, portfolio_data, quote_data, sentiment_data, user_preferences
        )
        
        if ai_decision:
            db.add(ai_decision)
            await db.commit()
            
            # Broadcast new decision via WebSocket
            await manager.broadcast(f"new_decision:{symbol}:{ai_decision.decision_type.value}")
            
            return {
                "symbol": symbol,
                "decision": {
                    "decision_id": ai_decision.decision_id,
                    "decision_type": ai_decision.decision_type.value,
                    "confidence": ai_decision.confidence_score,
                    "rationale": ai_decision.rationale,
                    "price_target": float(ai_decision.price_target) if ai_decision.price_target else None
                },
                "sentiment": {
                    "score": sentiment_score,
                    "summary": sentiment_summary
                },
                "market_data": quote_data
            }
        else:
            await db.commit()
            return {
                "symbol": symbol,
                "message": "No trading decision generated",
                "sentiment": {"score": sentiment_score, "summary": sentiment_summary},
                "market_data": quote_data
            }
            
    except Exception as e:
        logger.error(f"❌ AI analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/ai/sentiment-batch")
async def analyze_sentiment_batch(
    symbols: List[str],
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze sentiment for multiple symbols."""
    try:
        # Convert symbols to uppercase
        symbols = [s.upper() for s in symbols]
        
        sentiment_results = await market_service.analyze_market_sentiment_batch(symbols, db)
        
        return {
            "analyzed_symbols": len(symbols),
            "sentiment_scores": sentiment_results,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


# Notification endpoints
class NotificationRequest(BaseModel):
    """Request model for sending notifications."""
    recipients: List[str] = Field(..., description="List of email recipients")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    severity: str = Field(default="info", description="Severity level (info, warning, error, success)")


class TestAlertRequest(BaseModel):
    """Request model for testing trading alerts."""
    symbol: str = Field(..., description="Stock symbol for testing")
    recipients: List[str] = Field(..., description="List of email recipients")


@app.post("/api/notifications/test-alert")
async def test_trading_alert(
    request: TestAlertRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Test sending a trading alert notification."""
    try:
        # Get the latest AI decision for the symbol
        result = await db.execute(
            select(AIDecision)
            .where(AIDecision.symbol == request.symbol.upper())
            .order_by(desc(AIDecision.created_at))
            .limit(1)
        )
        decision = result.scalar_one_or_none()
        
        if not decision:
            # Create a mock decision for testing
            from datetime import datetime
            import uuid
            decision = AIDecision(
                decision_id=str(uuid.uuid4()),
                symbol=request.symbol.upper(),
                decision_type=DecisionType.BUY,
                confidence_score=0.85,
                rationale=f"Test trading alert for {request.symbol.upper()}. This is a mock decision for testing the notification system.",
                price_target=150.00,
                created_at=datetime.now()
            )
        
        # Get mock market data
        market_data = {
            'current_price': 145.50,
            'change_percent': 2.3,
            'volume': 1250000
        }
        
        # Send notification
        result = await notification_service.send_trading_alert(
            decision=decision,
            market_data=market_data,
            recipients=request.recipients
        )
        
        return {
            "message": "Test trading alert sent",
            "symbol": request.symbol.upper(),
            "notification_results": result,
            "decision_id": decision.decision_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send test trading alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test alert: {str(e)}")


@app.post("/api/notifications/system-alert")
async def send_system_alert(request: NotificationRequest):
    """Send a system alert notification."""
    try:
        result = await notification_service.send_system_alert(
            title=request.title,
            message=request.message,
            severity=request.severity,
            recipients=request.recipients
        )
        
        return {
            "message": "System alert sent",
            "notification_results": result,
            "severity": request.severity
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send system alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send system alert: {str(e)}")


@app.post("/api/notifications/portfolio-summary")
async def send_portfolio_summary_notification(
    recipients: List[str],
    db: AsyncSession = Depends(get_db_session)
):
    """Send portfolio summary notification."""
    try:
        # Get the latest portfolio analytics
        result = await db.execute(
            select(PortfolioAnalytics)
            .order_by(desc(PortfolioAnalytics.timestamp))
            .limit(1)
        )
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            # Create mock analytics for testing
            from datetime import datetime
            analytics = PortfolioAnalytics(
                total_value=100000.00,
                cash_balance=15000.00,
                total_gain_loss=5000.00,
                total_gain_loss_percent=5.26,
                daily_gain_loss=250.00,
                daily_gain_loss_percent=0.25,
                risk_score=0.65,
                diversification_score=0.82,
                beta=1.05,
                timestamp=datetime.now()
            )
        
        # Send notification
        result = await notification_service.send_portfolio_summary(
            analytics=analytics,
            recipients=recipients
        )
        
        return {
            "message": "Portfolio summary sent",
            "notification_results": result,
            "portfolio_value": analytics.total_value
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send portfolio summary: {str(e)}")


@app.get("/api/notifications/status")
async def get_notification_status():
    """Get notification service status."""
    try:
        status = {
            "email_configured": notification_service.smtp_config is not None,
            "slack_configured": notification_service.slack_client is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        if notification_service.smtp_config:
            status["email_host"] = notification_service.smtp_config["host"]
            status["email_port"] = notification_service.smtp_config["port"]
        
        if notification_service.slack_client:
            status["slack_channel"] = notification_service.slack_channel
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get notification status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notification status: {str(e)}")


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text("connected")
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Echo received messages (can be enhanced for specific commands)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Static files for React frontend (when built)
import os as _os
if _os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static", html=True), name="static")


# E*TRADE Authentication endpoints
class OAuthInitiateResponse(BaseModel):
    authorization_url: str

class OAuthCompleteRequest(BaseModel):
    verification_code: str

@app.post("/api/etrade/oauth/initiate", response_model=OAuthInitiateResponse)
async def initiate_etrade_oauth(use_sandbox: bool = True):
    """Initiate E*TRADE OAuth flow."""
    try:
        authorization_url = etrade_auth.initiate_oauth(use_sandbox=use_sandbox)
        return {"authorization_url": authorization_url}
    except Exception as e:
        logger.error(f"Failed to initiate E*TRADE OAuth: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth initiation failed: {str(e)}")

@app.post("/api/etrade/oauth/complete")
async def complete_etrade_oauth(request: OAuthCompleteRequest):
    """Complete E*TRADE OAuth flow."""
    try:
        success = etrade_auth.complete_oauth(request.verification_code)
        if success:
            return {"message": "E*TRADE authentication completed successfully"}
        else:
            raise HTTPException(status_code=500, detail="OAuth completion failed")
    except Exception as e:
        logger.error(f"Failed to complete E*TRADE OAuth: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth completion failed: {str(e)}")

@app.get("/api/etrade/auth/status")
async def get_etrade_auth_status():
    """Get E*TRADE authentication status."""
    return {"authenticated": etrade_auth.is_authenticated()}

# E*TRADE Account endpoints
@app.get("/api/etrade/accounts")
async def get_etrade_accounts():
    """Get list of E*TRADE accounts."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        accounts = etrade_account_service.get_account_list()
        return {"accounts": accounts}
    except Exception as e:
        logger.error(f"Failed to get E*TRADE accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")

@app.get("/api/etrade/accounts/{account_id_key}/balance")
async def get_etrade_account_balance(account_id_key: str):
    """Get E*TRADE account balance."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        balance = etrade_account_service.get_account_balance(account_id_key)
        return balance
    except Exception as e:
        logger.error(f"Failed to get E*TRADE account balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {str(e)}")

@app.get("/api/etrade/accounts/{account_id_key}/portfolio")
async def get_etrade_portfolio(account_id_key: str):
    """Get E*TRADE account portfolio."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        portfolio = etrade_account_service.get_portfolio(account_id_key)
        return portfolio
    except Exception as e:
        logger.error(f"Failed to get E*TRADE portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

# E*TRADE Order endpoints
class EquityOrderRequest(BaseModel):
    symbol: str
    order_action: str  # BUY, SELL, BUY_TO_COVER, SELL_SHORT
    quantity: int
    price_type: str = "MARKET"  # MARKET, LIMIT
    order_term: str = "GOOD_FOR_DAY"  # GOOD_FOR_DAY, IMMEDIATE_OR_CANCEL, FILL_OR_KILL
    limit_price: Optional[float] = None

class OrderCancelRequest(BaseModel):
    order_id: str

@app.post("/api/etrade/accounts/{account_id_key}/orders/preview")
async def preview_etrade_order(account_id_key: str, order: EquityOrderRequest):
    """Preview an E*TRADE equity order."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        preview = etrade_order_service.preview_equity_order(
            account_id_key=account_id_key,
            symbol=order.symbol,
            order_action=order.order_action,
            quantity=order.quantity,
            price_type=order.price_type,
            order_term=order.order_term,
            limit_price=order.limit_price
        )
        return preview
    except Exception as e:
        logger.error(f"Failed to preview E*TRADE order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to preview order: {str(e)}")

@app.post("/api/etrade/accounts/{account_id_key}/orders/place")
async def place_etrade_order(account_id_key: str, order: EquityOrderRequest):
    """Place an E*TRADE equity order."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        placed_order = etrade_order_service.place_equity_order(
            account_id_key=account_id_key,
            symbol=order.symbol,
            order_action=order.order_action,
            quantity=order.quantity,
            price_type=order.price_type,
            order_term=order.order_term,
            limit_price=order.limit_price
        )
        return placed_order
    except Exception as e:
        logger.error(f"Failed to place E*TRADE order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@app.get("/api/etrade/accounts/{account_id_key}/orders")
async def get_etrade_orders(account_id_key: str, status: str = "OPEN"):
    """Get list of E*TRADE orders."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        orders = etrade_order_service.get_order_list(account_id_key, status)
        return orders
    except Exception as e:
        logger.error(f"Failed to get E*TRADE orders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@app.post("/api/etrade/accounts/{account_id_key}/orders/cancel")
async def cancel_etrade_order(account_id_key: str, request: OrderCancelRequest):
    """Cancel an E*TRADE order."""
    if not etrade_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with E*TRADE")
    
    try:
        cancellation = etrade_order_service.cancel_order(account_id_key, request.order_id)
        return cancellation
    except Exception as e:
        logger.error(f"Failed to cancel E*TRADE order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve React frontend."""
    if _os.path.exists("frontend/build/index.html"):
        try:
            with open("frontend/build/index.html", "r") as f:
                return HTMLResponse(content=f.read())
        except Exception as e:
            logger.error(f"Failed to serve frontend: {e}")
    
    # Default landing page when frontend is not built
    return HTMLResponse(
        content="""
        <html>
            <head>
                <title>AI Trading Assistant</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                    .status { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 4px; margin: 20px 0; }
                    .links { display: flex; gap: 20px; margin: 20px 0; }
                    .link { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
                    .link:hover { background: #2980b9; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 AI Trading Assistant</h1>
                    <div class="status">
                        ✅ Backend server is running successfully!
                    </div>
                    <p>The FastAPI backend with AI trading capabilities is now active. The React frontend is not built yet.</p>
                    <div class="links">
                        <a href="/docs" class="link">📚 API Documentation</a>
                        <a href="/health" class="link">💚 Health Check</a>
                        <a href="/api/market/overview" class="link">📊 Market Overview</a>
                    </div>
                    <h3>Available Features:</h3>
                    <ul>
                        <li>🔄 Real-time market data (Yahoo Finance)</li>
                        <li>🤖 AI trading analysis (Google Gemini)</li>
                        <li>📈 Portfolio analytics tracking</li>
                        <li>📊 Market sentiment analysis</li>
                        <li>⚡ WebSocket real-time updates</li>
                        <li>👤 User preferences management</li>
                        <li>💰 E*TRADE API integration (authentication, accounts, orders)</li>
                    </ul>
                </div>
            </body>
        </html>
        """
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config_manager.get_web_app_host(),
        port=config_manager.get_web_app_port(),
        reload=config_manager.is_debug_enabled(),
        log_level="info"
    )