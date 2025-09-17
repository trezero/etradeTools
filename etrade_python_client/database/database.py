"""Database connection and session management for AI trading assistant."""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import sessionmaker

try:
    from ..utils.config_manager import ConfigManager
    from .models import Base
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.config_manager import ConfigManager
    from database.models import Base


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.async_session_maker: async_sessionmaker[AsyncSession] | None = None
        self.config_manager = ConfigManager()
    
    async def init_database(self):
        """Initialize database connection and create tables."""
        database_url = self.config_manager.get_database_url()
        
        # Convert SQLite URL to async format
        if database_url.startswith('sqlite:///'):
            database_url = database_url.replace('sqlite:///', 'sqlite+aiosqlite:///')
        
        self.engine = create_async_engine(
            database_url,
            echo=self.config_manager.is_debug_enabled(),
            future=True
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call init_database() first.")
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()


# Global database manager instance
_db_manager = DatabaseManager()


async def init_database():
    """Initialize the database."""
    await _db_manager.init_database()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for dependency injection."""
    async with _db_manager.get_session() as session:
        yield session


async def close_database():
    """Close database connections."""
    await _db_manager.close()


# Utility function for creating default user preferences
async def create_default_user_preferences() -> str:
    """Create default user preferences and return user_id."""
    from .models import UserPreferences
    
    async with _db_manager.get_session() as session:
        # Check if any user preferences exist
        existing_prefs = await session.execute(
            "SELECT COUNT(*) FROM user_preferences"
        )
        if existing_prefs.scalar() > 0:
            # Return existing user_id
            result = await session.execute(
                "SELECT user_id FROM user_preferences LIMIT 1"
            )
            return result.scalar()
        
        # Create new default preferences
        default_prefs = UserPreferences(
            notification_preferences={
                "email_enabled": True,
                "slack_enabled": True,
                "trading_alerts": True,
                "daily_summary": True
            },
            watchlist_symbols=["AAPL", "MSFT", "GOOGL", "TSLA"]
        )
        
        session.add(default_prefs)
        await session.flush()
        
        return default_prefs.user_id