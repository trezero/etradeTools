"""E*TRADE OAuth 1.0a Authentication Service."""

import os
import json
import logging
from typing import Optional, Dict, Any
from rauth import OAuth1Service
from ..utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ETradeAuth:
    """E*TRADE OAuth 1.0a Authentication Service."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.session = None
        self.base_url = None
        self.account_id_key = None
        
    def initiate_oauth(self, use_sandbox: bool = True) -> str:
        """
        Initiate OAuth 1.0a flow and return authorization URL.
        
        Args:
            use_sandbox: Whether to use E*TRADE sandbox environment
            
        Returns:
            Authorization URL for user to visit
        """
        try:
            # Configure OAuth service
            etrade = OAuth1Service(
                name="etrade",
                consumer_key=self.config_manager.get_consumer_key(),
                consumer_secret=self.config_manager.get_consumer_secret(),
                request_token_url="https://api.etrade.com/oauth/request_token",
                access_token_url="https://api.etrade.com/oauth/access_token",
                authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
                base_url="https://api.etrade.com"
            )
            
            # Update URLs for sandbox if needed
            if use_sandbox:
                self.base_url = self.config_manager.get_sandbox_base_url()
                etrade.request_token_url = "https://apisb.etrade.com/oauth/request_token"
                etrade.access_token_url = "https://apisb.etrade.com/oauth/access_token"
                etrade.authorize_url = "https://us.etrade.com/e/t/etws/authorize?key={}&token={}"
            else:
                self.base_url = self.config_manager.get_prod_base_url()
            
            # Step 1: Get OAuth 1 request token and secret
            request_token, request_token_secret = etrade.get_request_token(
                params={"oauth_callback": "oob", "format": "json"}
            )
            
            # Step 2: Generate authorization URL
            authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
            
            # Store tokens for later use
            self.request_token = request_token
            self.request_token_secret = request_token_secret
            self.etrade_service = etrade
            
            logger.info(f"OAuth authorization URL generated: {authorize_url}")
            return authorize_url
            
        except Exception as e:
            logger.error(f"Failed to initiate OAuth: {e}")
            raise
    
    def complete_oauth(self, verification_code: str) -> bool:
        """
        Complete OAuth 1.0a flow with verification code.
        
        Args:
            verification_code: Verification code from E*TRADE authorization
            
        Returns:
            True if authentication successful
        """
        try:
            # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
            self.session = self.etrade_service.get_auth_session(
                self.request_token,
                self.request_token_secret,
                params={"oauth_verifier": verification_code}
            )
            
            logger.info("OAuth authentication completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete OAuth: {e}")
            raise
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with E*TRADE."""
        return self.session is not None
    
    def get_session(self):
        """Get the authenticated session."""
        return self.session
    
    def get_base_url(self) -> str:
        """Get the base URL for API calls."""
        return self.base_url
    
    def save_credentials(self, filepath: str = "etrade_credentials.json"):
        """
        Save OAuth credentials to a file for future use.
        
        Args:
            filepath: Path to save credentials file
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Complete OAuth flow first.")
        
        credentials = {
            "base_url": self.base_url,
            "access_token": self.session.access_token,
            "access_token_secret": self.session.access_token_secret
        }
        
        with open(filepath, "w") as f:
            json.dump(credentials, f)
        
        logger.info(f"Credentials saved to {filepath}")
    
    def load_credentials(self, filepath: str = "etrade_credentials.json"):
        """
        Load OAuth credentials from a file.
        
        Args:
            filepath: Path to credentials file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Credentials file not found: {filepath}")
        
        with open(filepath, "r") as f:
            credentials = json.load(f)
        
        # Configure OAuth service
        etrade = OAuth1Service(
            name="etrade",
            consumer_key=self.config_manager.get_consumer_key(),
            consumer_secret=self.config_manager.get_consumer_secret(),
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com"
        )
        
        # Update URLs for sandbox if needed
        self.base_url = credentials["base_url"]
        if "sandbox" in self.base_url:
            etrade.request_token_url = "https://apisb.etrade.com/oauth/request_token"
            etrade.access_token_url = "https://apisb.etrade.com/oauth/access_token"
        
        # Recreate session
        self.session = etrade.get_session(
            (credentials["access_token"], credentials["access_token_secret"])
        )
        
        self.etrade_service = etrade
        
        logger.info(f"Credentials loaded from {filepath}")