"""Enhanced configuration management extending existing config.ini patterns."""

import os
import configparser
from typing import Dict, List, Any, Optional
from pathlib import Path
from decimal import Decimal


class ConfigManager:
    """Enhanced configuration manager that extends existing config.ini patterns."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = configparser.ConfigParser()
        
        # Default to existing config.ini location
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        
        self.config_path = config_path
        self.load_config()
    
    def load_config(self):
        """Load configuration from config.ini file."""
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            # Create default configuration if it doesn't exist
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration with all required sections."""
        self.config['DEFAULT'] = {
            'CONSUMER_KEY': 'your_etrade_consumer_key',
            'CONSUMER_SECRET': 'your_etrade_consumer_secret',
            'SANDBOX_BASE_URL': 'https://apisb.etrade.com',
            'PROD_BASE_URL': 'https://api.etrade.com'
        }
        
        self.config['DATABASE'] = {
            'DATABASE_URL': 'sqlite:///./trading_assistant.db',
            'BACKUP_LOCATION': './backups/',
            'BACKUP_RETENTION_COUNT': '5',
            'DATA_RETENTION_DAYS': '30'
        }
        
        self.config['AI_SERVICES'] = {
            'GEMINI_API_KEY': 'your_gemini_api_key',
            'MAX_TRADE_AMOUNT': '1000.00',
            'AI_CONFIDENCE_THRESHOLD': '0.7',
            'AUTO_TRADING_ENABLED': 'true'
        }
        
        self.config['NOTIFICATIONS'] = {
            'EMAIL_SMTP_SERVER': 'smtp.gmail.com',
            'EMAIL_SMTP_PORT': '587',
            'EMAIL_USERNAME': 'your_email@gmail.com',
            'EMAIL_PASSWORD': 'your_app_password',
            'SLACK_TOKEN': 'your_slack_bot_token',
            'SLACK_CHANNEL': '#trading-alerts'
        }
        
        self.config['WEB_APP'] = {
            'HOST': 'localhost',
            'PORT': '8000',
            'DEBUG': 'true',
            'SECRET_KEY': 'your_secret_key_for_sessions'
        }
        
        self.config['CELERY'] = {
            'BROKER_URL': 'redis://localhost:6379/0',
            'RESULT_BACKEND': 'redis://localhost:6379/0',
            'TIMEZONE': 'America/Los_Angeles'
        }
        
        # Save default configuration
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
    
    # E*TRADE API Configuration
    def get_consumer_key(self) -> str:
        return self.config['DEFAULT']['CONSUMER_KEY']
    
    def get_consumer_secret(self) -> str:
        return self.config['DEFAULT']['CONSUMER_SECRET']
    
    def get_sandbox_base_url(self) -> str:
        return self.config['DEFAULT']['SANDBOX_BASE_URL']
    
    def get_prod_base_url(self) -> str:
        return self.config['DEFAULT']['PROD_BASE_URL']
    
    # Database Configuration
    def get_database_url(self) -> str:
        return self.config['DATABASE']['DATABASE_URL']
    
    def get_backup_location(self) -> str:
        return self.config['DATABASE']['BACKUP_LOCATION']
    
    def get_backup_retention_count(self) -> int:
        return int(self.config['DATABASE']['BACKUP_RETENTION_COUNT'])
    
    def get_data_retention_days(self) -> int:
        return int(self.config['DATABASE']['DATA_RETENTION_DAYS'])
    
    # AI Services Configuration
    def get_gemini_api_key(self) -> str:
        return self.config['AI_SERVICES']['GEMINI_API_KEY']
    
    def get_max_trade_amount(self) -> Decimal:
        return Decimal(self.config['AI_SERVICES']['MAX_TRADE_AMOUNT'])
    
    def get_ai_confidence_threshold(self) -> float:
        return float(self.config['AI_SERVICES']['AI_CONFIDENCE_THRESHOLD'])
    
    def is_auto_trading_enabled(self) -> bool:
        return self.config['AI_SERVICES']['AUTO_TRADING_ENABLED'].lower() == 'true'
    
    # Notification Configuration
    def get_email_smtp_server(self) -> str:
        return self.config['NOTIFICATIONS']['EMAIL_SMTP_SERVER']
    
    def get_email_smtp_port(self) -> int:
        return int(self.config['NOTIFICATIONS']['EMAIL_SMTP_PORT'])
    
    def get_email_username(self) -> str:
        return self.config['NOTIFICATIONS']['EMAIL_USERNAME']
    
    def get_email_password(self) -> str:
        return self.config['NOTIFICATIONS']['EMAIL_PASSWORD']
    
    def get_slack_token(self) -> str:
        return self.config['NOTIFICATIONS']['SLACK_TOKEN']
    
    def get_slack_channel(self) -> str:
        return self.config['NOTIFICATIONS']['SLACK_CHANNEL']
    
    # Web App Configuration
    def get_web_app_host(self) -> str:
        return self.config['WEB_APP']['HOST']
    
    def get_web_app_port(self) -> int:
        return int(self.config['WEB_APP']['PORT'])
    
    def is_debug_enabled(self) -> bool:
        return self.config['WEB_APP']['DEBUG'].lower() == 'true'
    
    def get_secret_key(self) -> str:
        return self.config['WEB_APP']['SECRET_KEY']
    
    # Celery Configuration
    def get_celery_broker_url(self) -> str:
        return os.environ.get('REDIS_URL', self.config['CELERY']['BROKER_URL'])
    
    def get_celery_result_backend(self) -> str:
        return os.environ.get('REDIS_URL', self.config['CELERY']['RESULT_BACKEND'])
    
    def get_celery_timezone(self) -> str:
        return self.config['CELERY']['TIMEZONE']
    
    # Utility methods
    def get_section(self, section_name: str) -> Dict[str, str]:
        """Get all values from a configuration section."""
        if section_name in self.config:
            return dict(self.config[section_name])
        return {}
    
    def set_value(self, section: str, key: str, value: str):
        """Set a configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def get_value(self, section: str, key: str, default: str = '') -> str:
        """Get a configuration value with optional default."""
        return self.config.get(section, key, fallback=default)