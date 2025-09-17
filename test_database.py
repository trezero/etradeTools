"""Test script for database layer functionality."""

import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Import directly from the modules
from etrade_python_client.database.database import init_database, get_db_session, close_database
from etrade_python_client.database.models import PortfolioAnalytics, AIDecision, UserPreferences, DecisionType, RiskTolerance
from etrade_python_client.utils.config_manager import ConfigManager


async def test_database_functionality():
    """Test basic database functionality."""
    print("🧪 Testing Database Layer...")
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        # Test configuration manager
        print("\n⚙️ Testing configuration manager...")
        config_manager = ConfigManager()
        db_url = config_manager.get_database_url()
        print(f"✅ Database URL: {db_url}")
        print(f"✅ Backup location: {config_manager.get_backup_location()}")
        print(f"✅ Max trade amount: {config_manager.get_max_trade_amount()}")
        
        # Test database session
        print("\n💾 Testing database session...")
        from etrade_python_client.database.database import _db_manager
        async with _db_manager.get_session() as session:
            print("✅ Database session created successfully")
            
            # Test creating user preferences
            print("\n👤 Testing user preferences creation...")
            user_prefs = UserPreferences(
                risk_tolerance=RiskTolerance.MODERATE,
                max_trade_amount=Decimal('1500.00'),
                notification_preferences={
                    "email_enabled": True,
                    "slack_enabled": False,
                    "trading_alerts": True
                },
                watchlist_symbols=["AAPL", "MSFT", "GOOGL"]
            )
            
            session.add(user_prefs)
            await session.flush()
            print(f"✅ User preferences created with ID: {user_prefs.user_id}")
            
            # Test creating AI decision
            print("\n🤖 Testing AI decision creation...")
            ai_decision = AIDecision(
                symbol="AAPL",
                decision_type=DecisionType.BUY,
                confidence_score=0.85,
                rationale="Strong earnings outlook and positive market sentiment",
                price_target=Decimal('155.00')
            )
            
            session.add(ai_decision)
            await session.flush()
            print(f"✅ AI decision created with ID: {ai_decision.decision_id}")
            
            # Test creating portfolio analytics
            print("\n📈 Testing portfolio analytics creation...")
            portfolio_data = PortfolioAnalytics(
                account_id="test_account_123",
                timestamp=datetime.now(),
                total_value=Decimal('25000.50'),
                daily_change=Decimal('125.75'),
                positions={
                    "AAPL": {
                        "quantity": 100,
                        "current_price": 150.25,
                        "market_value": 15025.00
                    },
                    "MSFT": {
                        "quantity": 50,
                        "current_price": 200.50,
                        "market_value": 10025.00
                    }
                }
            )
            
            session.add(portfolio_data)
            await session.flush()
            print(f"✅ Portfolio analytics created with ID: {portfolio_data.portfolio_id}")
            
            # Test querying data
            print("\n🔍 Testing data queries...")
            from sqlalchemy import select
            
            # Query AI decisions
            result = await session.execute(
                select(AIDecision).where(AIDecision.symbol == "AAPL")
            )
            decisions = result.scalars().all()
            print(f"✅ Found {len(decisions)} AI decisions for AAPL")
            
            # Query user preferences
            result = await session.execute(select(UserPreferences))
            users = result.scalars().all()
            print(f"✅ Found {len(users)} user preference records")
            
            # Query portfolio analytics
            result = await session.execute(
                select(PortfolioAnalytics).where(PortfolioAnalytics.account_id == "test_account_123")
            )
            portfolios = result.scalars().all()
            print(f"✅ Found {len(portfolios)} portfolio records for test account")
            
        print("\n🎉 All database tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        raise
    
    finally:
        await close_database()
        print("🔒 Database connections closed")


if __name__ == "__main__":
    asyncio.run(test_database_functionality())