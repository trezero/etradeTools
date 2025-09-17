"""E*TRADE Account Services for portfolio and balance information."""

import json
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal

from .etrade_auth import ETradeAuth

logger = logging.getLogger(__name__)

class ETradeAccountService:
    """Service for interacting with E*TRADE account APIs."""
    
    def __init__(self, auth_service: ETradeAuth):
        self.auth_service = auth_service
    
    def get_account_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of E*TRADE accounts.
        
        Returns:
            List of account dictionaries
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/list.json"
            
            # Make API call for GET request
            response = session.get(url, header_auth=True)
            logger.debug("Request Header: %s", response.request.headers)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                
                data = response.json()
                if data is not None and "AccountListResponse" in data and "Accounts" in data["AccountListResponse"] \
                        and "Account" in data["AccountListResponse"]["Accounts"]:
                    accounts = data["AccountListResponse"]["Accounts"]["Account"]
                    # Filter out closed accounts
                    accounts = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                    return accounts
                else:
                    raise Exception("Failed to retrieve account list from E*TRADE API")
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get account list: {e}")
            raise
    
    def get_account_balance(self, account_id_key: str) -> Dict[str, Any]:
        """
        Retrieve account balance information.
        
        Args:
            account_id_key: The accountIdKey for the account
            
        Returns:
            Dictionary containing balance information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/balance.json"
            
            # Add parameters and header information
            from ..utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            params = {"instType": "BROKERAGE", "realTimeNAV": "true"}
            headers = {"consumerkey": config_manager.get_consumer_key()}
            
            # Make API call for GET request
            response = session.get(url, header_auth=True, params=params, headers=headers)
            logger.debug("Request url: %s", url)
            logger.debug("Request Header: %s", response.request.headers)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "BalanceResponse" in data:
                    return data["BalanceResponse"]
                else:
                    raise Exception("Failed to retrieve balance information from E*TRADE API")
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            raise
    
    def get_portfolio(self, account_id_key: str) -> Dict[str, Any]:
        """
        Retrieve portfolio positions for an account.
        
        Args:
            account_id_key: The accountIdKey for the account
            
        Returns:
            Dictionary containing portfolio information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/portfolio.json"
            
            # Make API call for GET request
            response = session.get(url, header_auth=True)
            logger.debug("Request Header: %s", response.request.headers)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "PortfolioResponse" in data:
                    return data["PortfolioResponse"]
                else:
                    raise Exception("Failed to retrieve portfolio information from E*TRADE API")
            elif response is not None and response.status_code == 204:
                # No content - empty portfolio
                return {}
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            raise