"""Celery tasks for background processing."""

import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
from decimal import Decimal

from celery import Task
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .celery_app import celery_app
from ..database.database import get_db_session, init_database
from ..database.models import (
    PortfolioAnalytics, AIDecision, MarketSentiment, UserPreferences, 
    AILearningContext, BackupLog, DecisionType, UserFeedback
)
from ..utils.config_manager import ConfigManager
from .market_data_service import MarketDataService
from .ai_trading_service import AITradingService
from .etrade_auth import ETradeAuth
from .etrade_account_service import ETradeAccountService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
config_manager = ConfigManager()
market_service = MarketDataService()
ai_service = AITradingService()

# E*TRADE services
etrade_auth = ETradeAuth()
etrade_account_service = ETradeAccountService(etrade_auth)


class AsyncTask(Task):
    """Base task class that handles async operations."""
    
    def __call__(self, *args, **kwargs):
        """Execute async task function."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run(*args, **kwargs))
        finally:
            loop.close()
    
    async def run(self, *args, **kwargs):
        """Override this method in subclasses."""
        raise NotImplementedError


@celery_app.task(bind=True, base=AsyncTask)
async def backup_database(self):
    """Create a backup of the database."""
    try:
        logger.info("🗄️ Starting database backup...")
        
        # Create backup directory if it doesn't exist
        backup_dir = config_manager.get_backup_location()
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"trading_assistant_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Get database path
        db_url = config_manager.get_database_url()
        if db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # Remove 'sqlite:///'
            
            # Copy database file
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                backup_size = os.path.getsize(backup_path)
                
                logger.info(f"✅ Database backup created: {backup_path} ({backup_size} bytes)")
                
                # Record backup in database
                await init_database()
                async with get_db_session().__anext__() as session:
                    backup_log = BackupLog(
                        backup_filename=backup_filename,
                        backup_path=backup_path,
                        backup_size_bytes=backup_size,
                        status="completed"
                    )
                    session.add(backup_log)
                    await session.commit()
                
                # Clean up old backups
                await cleanup_old_backups()
                
                return {
                    "status": "success",
                    "backup_path": backup_path,
                    "backup_size": backup_size,
                    "timestamp": timestamp
                }
            else:
                error_msg = f"Database file not found: {db_path}"
                logger.error(f"❌ {error_msg}")
                return {"status": "error", "message": error_msg}
        else:
            error_msg = f"Unsupported database URL: {db_url}"
            logger.error(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}
            
    except Exception as e:
        error_msg = f"Database backup failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Log failed backup
        try:
            await init_database()
            async with get_db_session().__anext__() as session:
                backup_log = BackupLog(
                    backup_filename=f"failed_backup_{timestamp}",
                    backup_path="",
                    backup_size_bytes=0,
                    status="failed",
                    error_message=error_msg
                )
                session.add(backup_log)
                await session.commit()
        except Exception as log_error:
            logger.error(f"❌ Failed to log backup error: {log_error}")
        
        return {"status": "error", "message": error_msg}


async def cleanup_old_backups():
    """Clean up old backup files."""
    try:
        backup_dir = config_manager.get_backup_location()
        retention_count = config_manager.get_backup_retention_count()
        
        if not os.path.exists(backup_dir):
            return
        
        # Get all backup files sorted by modification time (newest first)
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('trading_assistant_backup_') and filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                backup_files.append((filepath, os.path.getmtime(filepath)))
        
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        files_to_remove = backup_files[retention_count:]
        for filepath, _ in files_to_remove:
            try:
                os.remove(filepath)
                logger.info(f"🗑️ Removed old backup: {os.path.basename(filepath)}")
            except Exception as e:
                logger.error(f"❌ Failed to remove backup {filepath}: {e}")
                
    except Exception as e:
        logger.error(f"❌ Backup cleanup failed: {e}")


@celery_app.task(bind=True, base=AsyncTask)
async def cleanup_old_data(self):
    """Clean up old data based on retention policies."""
    try:
        logger.info("🧹 Starting data cleanup...")
        
        await init_database()
        async with get_db_session().__anext__() as session:
            retention_days = config_manager.get_data_retention_days()
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Clean up old portfolio analytics
            result = await session.execute(
                delete(PortfolioAnalytics).where(
                    PortfolioAnalytics.timestamp < cutoff_date
                )
            )
            portfolio_deleted = result.rowcount
            
            # Clean up old market sentiment data
            result = await session.execute(
                delete(MarketSentiment).where(
                    MarketSentiment.analyzed_at < cutoff_date
                )
            )
            sentiment_deleted = result.rowcount
            
            # Clean up old AI decisions (keep decisions with feedback)
            result = await session.execute(
                delete(AIDecision).where(
                    AIDecision.created_at < cutoff_date,
                    AIDecision.user_feedback.is_(None)
                )
            )
            decisions_deleted = result.rowcount
            
            await session.commit()
            
            logger.info(f"✅ Data cleanup completed:")
            logger.info(f"   - Portfolio records: {portfolio_deleted}")
            logger.info(f"   - Sentiment records: {sentiment_deleted}")
            logger.info(f"   - AI decisions: {decisions_deleted}")
            
            return {
                "status": "success",
                "deleted_counts": {
                    "portfolio_analytics": portfolio_deleted,
                    "market_sentiment": sentiment_deleted,
                    "ai_decisions": decisions_deleted
                },
                "cutoff_date": cutoff_date.isoformat()
            }
            
    except Exception as e:
        error_msg = f"Data cleanup failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


@celery_app.task(bind=True, base=AsyncTask)
async def update_market_sentiment(self):
    """Update market sentiment for watchlist symbols."""
    try:
        logger.info("📊 Updating market sentiment...")
        
        await init_database()
        async with get_db_session().__anext__() as session:
            # Get user watchlist
            result = await session.execute(select(UserPreferences).limit(1))
            preferences = result.scalar_one_or_none()
            
            if not preferences or not preferences.watchlist_symbols:
                logger.info("ℹ️ No watchlist symbols configured")
                return {"status": "success", "message": "No watchlist symbols to update"}
            
            # Update sentiment for watchlist symbols
            sentiment_results = await market_service.analyze_market_sentiment_batch(
                preferences.watchlist_symbols, session
            )
            
            logger.info(f"✅ Market sentiment updated for {len(sentiment_results)} symbols")
            
            return {
                "status": "success",
                "updated_symbols": len(sentiment_results),
                "sentiment_scores": sentiment_results
            }
            
    except Exception as e:
        error_msg = f"Market sentiment update failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


@celery_app.task(bind=True, base=AsyncTask)
async def optimize_ai_learning(self):
    """Optimize AI learning based on user feedback."""
    try:
        logger.info("🧠 Optimizing AI learning...")
        
        await init_database()
        async with get_db_session().__anext__() as session:
            # Get recent decisions with feedback
            result = await session.execute(
                select(AIDecision).where(
                    AIDecision.user_feedback.is_not(None),
                    AIDecision.feedback_timestamp > datetime.now() - timedelta(days=30)
                )
            )
            decisions_with_feedback = result.scalars().all()
            
            if not decisions_with_feedback:
                logger.info("ℹ️ No recent feedback to learn from")
                return {"status": "success", "message": "No feedback data available"}
            
            # Analyze feedback patterns
            total_feedback = len(decisions_with_feedback)
            positive_feedback = len([d for d in decisions_with_feedback 
                                   if d.user_feedback == UserFeedback.POSITIVE])
            negative_feedback = len([d for d in decisions_with_feedback 
                                   if d.user_feedback == UserFeedback.NEGATIVE])
            
            # Calculate performance metrics
            accuracy_rate = positive_feedback / total_feedback if total_feedback > 0 else 0
            
            # Get or create learning context
            result = await session.execute(
                select(AILearningContext).where(AILearningContext.is_active == True)
            )
            learning_context = result.scalar_one_or_none()
            
            if learning_context:
                # Update existing context
                learning_context.is_active = False
                
            # Create new learning context
            new_learning_params = {
                "confidence_threshold": max(0.5, min(0.9, 0.7 + (accuracy_rate - 0.5))),
                "max_trade_amount": float(config_manager.get_max_trade_amount()),
                "risk_adjustment": 1.0 + (accuracy_rate - 0.5) * 0.2
            }
            
            feedback_summary = {
                "total_feedback": total_feedback,
                "positive_feedback": positive_feedback,
                "negative_feedback": negative_feedback,
                "accuracy_rate": accuracy_rate
            }
            
            performance_metrics = {
                "total_decisions": total_feedback,
                "successful_trades": positive_feedback,
                "accuracy_rate": accuracy_rate,
                "last_optimization": datetime.now().isoformat()
            }
            
            new_context = AILearningContext(
                version=(learning_context.version + 1) if learning_context else 1,
                learning_parameters=new_learning_params,
                feedback_summary=feedback_summary,
                performance_metrics=performance_metrics,
                is_active=True
            )
            
            session.add(new_context)
            await session.commit()
            
            # Process individual decisions for learning
            for decision in decisions_with_feedback:
                await ai_service.learn_from_feedback(decision)
            
            logger.info(f"✅ AI learning optimization completed:")
            logger.info(f"   - Total feedback: {total_feedback}")
            logger.info(f"   - Accuracy rate: {accuracy_rate:.2%}")
            logger.info(f"   - New confidence threshold: {new_learning_params['confidence_threshold']:.2f}")
            
            return {
                "status": "success",
                "learning_context_version": new_context.version,
                "feedback_summary": feedback_summary,
                "performance_metrics": performance_metrics,
                "new_parameters": new_learning_params
            }
            
    except Exception as e:
        error_msg = f"AI learning optimization failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


@celery_app.task(bind=True)
def health_check(self):
    """Perform system health check."""
    try:
        logger.info("💚 Performing health check...")
        
        health_status = {
            "celery_worker": "healthy",
            "database": "unknown",
            "redis": "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test Redis connection
        try:
            from redis import Redis
            redis_client = Redis.from_url(config_manager.get_celery_broker_url())
            redis_client.ping()
            health_status["redis"] = "healthy"
        except Exception as e:
            health_status["redis"] = f"error: {str(e)}"
            logger.warning(f"⚠️ Redis health check failed: {e}")
        
        # Test database connection (simplified for sync task)
        try:
            db_url = config_manager.get_database_url()
            if db_url.startswith('sqlite:///'):
                db_path = db_url[10:]
                if os.path.exists(db_path):
                    health_status["database"] = "healthy"
                else:
                    health_status["database"] = "database file not found"
            else:
                health_status["database"] = "unsupported database type"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
            logger.warning(f"⚠️ Database health check failed: {e}")
        
        logger.info(f"✅ Health check completed: {health_status}")
        return health_status
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


# Manual task triggers (can be called via API)
@celery_app.task(bind=True, base=AsyncTask)
async def sync_etrade_portfolio(self):
    """Synchronize E*TRADE portfolio data with local database."""
    try:
        logger.info("💰 Starting E*TRADE portfolio synchronization...")
        
        # Check if E*TRADE is authenticated
        if not etrade_auth.is_authenticated():
            logger.info("ℹ️ E*TRADE not authenticated, skipping portfolio sync")
            return {"status": "skipped", "message": "E*TRADE not authenticated"}
        
        await init_database()
        async with get_db_session().__anext__() as session:
            # Get E*TRADE account list
            accounts = etrade_account_service.get_account_list()
            
            if not accounts:
                logger.info("ℹ️ No E*TRADE accounts found")
                return {"status": "skipped", "message": "No E*TRADE accounts found"}
            
            # Process each account
            for account in accounts:
                account_id = account.get("accountId", "")
                account_id_key = account.get("accountIdKey", "")
                
                if not account_id_key:
                    continue
                
                try:
                    # Get portfolio data
                    portfolio_data = etrade_account_service.get_portfolio(account_id_key)
                    
                    # Create portfolio analytics record
                    if "AccountPortfolio" in portfolio_data:
                        # Calculate total value and positions
                        total_value = 0.0
                        daily_change = 0.0
                        positions = {}
                        
                        for account_portfolio in portfolio_data["AccountPortfolio"]:
                            if "Position" in account_portfolio:
                                for position in account_portfolio["Position"]:
                                    symbol = position.get("symbolDescription", "")
                                    market_value = position.get("marketValue", 0.0)
                                    total_gain = position.get("totalGain", 0.0)
                                    
                                    positions[symbol] = {
                                        "quantity": position.get("quantity", 0),
                                        "market_value": market_value,
                                        "total_gain": total_gain,
                                        "price_paid": position.get("pricePaid", 0.0),
                                        "last_trade": position.get("Quick", {}).get("lastTrade", 0.0) if position.get("Quick") else 0.0
                                    }
                                    
                                    total_value += market_value
                                    daily_change += total_gain
                        
                        # Create portfolio analytics record
                        portfolio_analytics = PortfolioAnalytics(
                            account_id=account_id,
                            total_value=total_value,
                            daily_change=daily_change,
                            positions=positions
                        )
                        
                        session.add(portfolio_analytics)
                
                except Exception as account_error:
                    logger.error(f"❌ Failed to sync portfolio for account {account_id}: {account_error}")
                    continue
            
            await session.commit()
            
            logger.info(f"✅ E*TRADE portfolio synchronization completed for {len(accounts)} accounts")
            return {
                "status": "success",
                "accounts_synced": len(accounts)
            }
            
    except Exception as e:
        error_msg = f"E*TRADE portfolio synchronization failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


@celery_app.task(bind=True, base=AsyncTask)
async def execute_etrade_trades(self):
    """Execute E*TRADE trades based on AI decisions."""
    try:
        logger.info("💰 Starting E*TRADE trade execution...")
        
        # Check if E*TRADE is authenticated
        if not etrade_auth.is_authenticated():
            logger.info("ℹ️ E*TRADE not authenticated, skipping trade execution")
            return {"status": "skipped", "message": "E*TRADE not authenticated"}
        
        # Check if auto-trading is enabled
        if not config_manager.is_auto_trading_enabled():
            logger.info("ℹ️ Auto-trading disabled, skipping trade execution")
            return {"status": "skipped", "message": "Auto-trading disabled"}
        
        await init_database()
        async with get_db_session().__anext__() as session:
            # Get user preferences
            result = await session.execute(select(UserPreferences).limit(1))
            user_preferences = result.scalar_one_or_none()
            
            if not user_preferences:
                logger.info("ℹ️ No user preferences found, skipping trade execution")
                return {"status": "skipped", "message": "No user preferences found"}
            
            # Get E*TRADE account list
            accounts = etrade_account_service.get_account_list()
            
            if not accounts:
                logger.info("ℹ️ No E*TRADE accounts found, skipping trade execution")
                return {"status": "skipped", "message": "No E*TRADE accounts found"}
            
            # Use the first account for trading (in a real implementation, you might want to select a specific account)
            account_id_key = accounts[0].get("accountIdKey", "")
            
            if not account_id_key:
                logger.info("ℹ️ No valid account ID key found, skipping trade execution")
                return {"status": "skipped", "message": "No valid account ID key found"}
            
            # Get recent AI decisions with high confidence that haven't been executed yet
            result = await session.execute(
                select(AIDecision)
                .where(
                    AIDecision.confidence_score >= config_manager.get_ai_confidence_threshold(),
                    AIDecision.executed_at.is_(None),
                    AIDecision.decision_type.in_([DecisionType.BUY, DecisionType.SELL])
                )
                .order_by(AIDecision.created_at.desc())
                .limit(5)  # Limit to 5 trades at a time
            )
            ai_decisions = result.scalars().all()
            
            if not ai_decisions:
                logger.info("ℹ️ No eligible AI decisions for trade execution")
                return {"status": "success", "message": "No eligible AI decisions for trade execution", "trades_executed": 0}
            
            # Execute trades
            trades_executed = 0
            
            # Initialize E*TRADE order service
            etrade_order_service = ETradeOrderService(etrade_auth)
            
            for decision in ai_decisions:
                try:
                    # Determine order parameters
                    symbol = decision.symbol
                    order_action = "BUY" if decision.decision_type == DecisionType.BUY else "SELL"
                    quantity = 1  # Default quantity, in a real implementation you might calculate this based on portfolio and risk tolerance
                    
                    # For SELL orders, check if we have the position
                    if order_action == "SELL":
                        # Get current portfolio to check if we have the position
                        portfolio_data = etrade_account_service.get_portfolio(account_id_key)
                        position_found = False
                        
                        if "AccountPortfolio" in portfolio_data:
                            for account_portfolio in portfolio_data["AccountPortfolio"]:
                                if "Position" in account_portfolio:
                                    for position in account_portfolio["Position"]:
                                        if position.get("symbolDescription", "") == symbol:
                                            position_found = True
                                            # Use the actual quantity from the position for selling
                                            quantity = min(quantity, int(position.get("quantity", 0)))
                                            break
                                if position_found:
                                    break
                        
                        if not position_found:
                            logger.info(f"ℹ️ No position found for {symbol}, skipping SELL order")
                            continue
                    
                    # Preview the order
                    preview = etrade_order_service.preview_equity_order(
                        account_id_key=account_id_key,
                        symbol=symbol,
                        order_action=order_action,
                        quantity=quantity,
                        price_type="MARKET"
                    )
                    
                    # Place the order
                    placed_order = etrade_order_service.place_equity_order(
                        account_id_key=account_id_key,
                        symbol=symbol,
                        order_action=order_action,
                        quantity=quantity,
                        price_type="MARKET"
                    )
                    
                    # Update the AI decision with execution information
                    decision.executed_at = datetime.now()
                    # In a real implementation, you would get the actual execution price from the order response
                    # decision.outcome_value = Decimal(str(execution_price))
                    
                    await session.commit()
                    
                    trades_executed += 1
                    logger.info(f"✅ Executed {order_action} order for {symbol} (quantity: {quantity})")
                    
                except Exception as trade_error:
                    logger.error(f"❌ Failed to execute trade for {decision.symbol}: {trade_error}")
                    # Continue with other trades
                    continue
            
            logger.info(f"✅ E*TRADE trade execution completed: {trades_executed} trades executed")
            return {
                "status": "success",
                "trades_executed": trades_executed
            }
            
    except Exception as e:
        error_msg = f"E*TRADE trade execution failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}


@celery_app.task(bind=True, base=AsyncTask)
async def manual_backup(self):
    """Manually trigger database backup."""
    return await backup_database.run()


@celery_app.task(bind=True, base=AsyncTask)
async def analyze_symbol_background(self, symbol: str):
    """Background task for symbol analysis."""
    try:
        logger.info(f"🤖 Background analysis for {symbol}...")
        
        await init_database()
        async with get_db_session().__anext__() as session:
            # Get user preferences
            result = await session.execute(select(UserPreferences).limit(1))
            user_preferences = result.scalar_one_or_none()
            
            if not user_preferences:
                return {"status": "error", "message": "User preferences not found"}
            
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
            session.add(market_sentiment)
            
            # Generate trading decision
            portfolio_data = {}  # Would get from E*TRADE API in full implementation
            sentiment_data = {'sentiment_score': sentiment_score, 'summary': sentiment_summary}
            
            ai_decision = await ai_service.generate_trading_decision(
                symbol, portfolio_data, quote_data, sentiment_data, user_preferences
            )
            
            if ai_decision:
                session.add(ai_decision)
                await session.commit()
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "decision_id": ai_decision.decision_id,
                    "decision_type": ai_decision.decision_type.value,
                    "confidence": ai_decision.confidence_score,
                    "sentiment_score": sentiment_score
                }
            else:
                await session.commit()
                return {
                    "status": "success",
                    "symbol": symbol,
                    "message": "No trading decision generated",
                    "sentiment_score": sentiment_score
                }
                
    except Exception as e:
        error_msg = f"Background symbol analysis failed for {symbol}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg, "symbol": symbol}