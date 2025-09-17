"""Celery application for background tasks."""

import os
import logging
from celery import Celery
from celery.schedules import crontab

from ..utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
config_manager = ConfigManager()

# Create Celery app
celery_app = Celery(
    'trading_assistant',
    broker=config_manager.get_celery_broker_url(),
    backend=config_manager.get_celery_result_backend(),
    include=['etrade_python_client.services.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=config_manager.get_celery_timezone(),
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Nightly database backup
    'nightly-backup': {
        'task': 'etrade_python_client.services.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
    
    # Data cleanup (remove old records)
    'weekly-cleanup': {
        'task': 'etrade_python_client.services.tasks.cleanup_old_data',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sundays at 3:00 AM
    },
    
    # Update market sentiment for watchlist
    'market-sentiment-update': {
        'task': 'etrade_python_client.services.tasks.update_market_sentiment',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes during market hours
    },
    
    # AI learning optimization
    'ai-learning-optimization': {
        'task': 'etrade_python_client.services.tasks.optimize_ai_learning',
        'schedule': crontab(hour=1, minute=0),  # 1:00 AM daily
    },
    
    # Health check
    'health-check': {
        'task': 'etrade_python_client.services.tasks.health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    
    # E*TRADE portfolio synchronization
    'etrade-portfolio-sync': {
        'task': 'etrade_python_client.services.tasks.sync_etrade_portfolio',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes during market hours
    },
    
    # E*TRADE trade execution
    'etrade-trade-execution': {
        'task': 'etrade_python_client.services.tasks.execute_etrade_trades',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes during market hours
    },
}

# Task routes (optional - for task distribution)
celery_app.conf.task_routes = {
    'etrade_python_client.services.tasks.backup_database': {'queue': 'maintenance'},
    'etrade_python_client.services.tasks.cleanup_old_data': {'queue': 'maintenance'},
    'etrade_python_client.services.tasks.update_market_sentiment': {'queue': 'market_data'},
    'etrade_python_client.services.tasks.optimize_ai_learning': {'queue': 'ai_processing'},
    'etrade_python_client.services.tasks.health_check': {'queue': 'monitoring'},
    'etrade_python_client.services.tasks.sync_etrade_portfolio': {'queue': 'market_data'},
    'etrade_python_client.services.tasks.execute_etrade_trades': {'queue': 'trading'},
}

if __name__ == '__main__':
    celery_app.start()