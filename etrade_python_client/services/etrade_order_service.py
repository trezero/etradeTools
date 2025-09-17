"""E*TRADE Order Services for trade execution."""

import json
import logging
import random
from typing import Dict, List, Any, Optional
from decimal import Decimal

from .etrade_auth import ETradeAuth

logger = logging.getLogger(__name__)

class ETradeOrderService:
    """Service for interacting with E*TRADE order APIs."""
    
    def __init__(self, auth_service: ETradeAuth):
        self.auth_service = auth_service
    
    def preview_equity_order(
        self, 
        account_id_key: str,
        symbol: str,
        order_action: str,
        quantity: int,
        price_type: str = "MARKET",
        order_term: str = "GOOD_FOR_DAY",
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Preview an equity order.
        
        Args:
            account_id_key: The accountIdKey for the account
            symbol: Stock symbol
            order_action: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            quantity: Number of shares
            price_type: MARKET, LIMIT
            order_term: GOOD_FOR_DAY, IMMEDIATE_OR_CANCEL, FILL_OR_KILL
            limit_price: Limit price (required for LIMIT orders)
            
        Returns:
            Dictionary containing preview information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/orders/preview.json"
            
            # Add parameters and header information
            from ..utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            headers = {"Content-Type": "application/xml", "consumerKey": config_manager.get_consumer_key()}
            
            # Generate client order ID
            client_order_id = str(random.randint(1000000000, 9999999999))
            
            # Create XML payload
            payload = f"""<PreviewOrderRequest>
                <orderType>EQ</orderType>
                <clientOrderId>{client_order_id}</clientOrderId>
                <Order>
                    <allOrNone>false</allOrNone>
                    <priceType>{price_type}</priceType>
                    <orderTerm>{order_term}</orderTerm>
                    <marketSession>REGULAR</marketSession>
                    <stopPrice></stopPrice>
                    <limitPrice>{limit_price if limit_price else ""}</limitPrice>
                    <Instrument>
                        <Product>
                            <securityType>EQ</securityType>
                            <symbol>{symbol}</symbol>
                        </Product>
                        <orderAction>{order_action}</orderAction>
                        <quantityType>QUANTITY</quantityType>
                        <quantity>{quantity}</quantity>
                    </Instrument>
                </Order>
            </PreviewOrderRequest>"""
            
            # Make API call for POST request
            response = session.post(url, header_auth=True, headers=headers, data=payload)
            logger.debug("Request Header: %s", response.request.headers)
            logger.debug("Request payload: %s", payload)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "PreviewOrderResponse" in data:
                    return data["PreviewOrderResponse"]
                else:
                    raise Exception("Failed to preview order with E*TRADE API")
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to preview equity order: {e}")
            raise
    
    def place_equity_order(
        self,
        account_id_key: str,
        symbol: str,
        order_action: str,
        quantity: int,
        price_type: str = "MARKET",
        order_term: str = "GOOD_FOR_DAY",
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place an equity order.
        
        Args:
            account_id_key: The accountIdKey for the account
            symbol: Stock symbol
            order_action: BUY, SELL, BUY_TO_COVER, SELL_SHORT
            quantity: Number of shares
            price_type: MARKET, LIMIT
            order_term: GOOD_FOR_DAY, IMMEDIATE_OR_CANCEL, FILL_OR_KILL
            limit_price: Limit price (required for LIMIT orders)
            
        Returns:
            Dictionary containing order placement information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            # First preview the order to get preview ID
            preview_response = self.preview_equity_order(
                account_id_key, symbol, order_action, quantity, price_type, order_term, limit_price
            )
            
            # Extract preview ID
            if "PreviewIds" in preview_response and len(preview_response["PreviewIds"]) > 0:
                preview_id = preview_response["PreviewIds"][0]["previewId"]
            else:
                raise Exception("Failed to get preview ID from E*TRADE API")
            
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/orders/place.json"
            
            # Add parameters and header information
            from ..utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            headers = {"Content-Type": "application/xml", "consumerKey": config_manager.get_consumer_key()}
            
            # Create XML payload
            payload = f"""<PlaceOrderRequest>
                <previewIds>
                    <previewId>{preview_id}</previewId>
                </previewIds>
                <orderType>EQ</orderType>
                <Order>
                    <allOrNone>false</allOrNone>
                    <priceType>{price_type}</priceType>
                    <orderTerm>{order_term}</orderTerm>
                    <marketSession>REGULAR</marketSession>
                    <stopPrice></stopPrice>
                    <limitPrice>{limit_price if limit_price else ""}</limitPrice>
                    <Instrument>
                        <Product>
                            <securityType>EQ</securityType>
                            <symbol>{symbol}</symbol>
                        </Product>
                        <orderAction>{order_action}</orderAction>
                        <quantityType>QUANTITY</quantityType>
                        <quantity>{quantity}</quantity>
                    </Instrument>
                </Order>
            </PlaceOrderRequest>"""
            
            # Make API call for POST request
            response = session.post(url, header_auth=True, headers=headers, data=payload)
            logger.debug("Request Header: %s", response.request.headers)
            logger.debug("Request payload: %s", payload)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "PlaceOrderResponse" in data:
                    return data["PlaceOrderResponse"]
                else:
                    raise Exception("Failed to place order with E*TRADE API")
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to place equity order: {e}")
            raise
    
    def get_order_list(self, account_id_key: str, status: str = "OPEN") -> Dict[str, Any]:
        """
        Retrieve list of orders.
        
        Args:
            account_id_key: The accountIdKey for the account
            status: Order status (OPEN, EXECUTED, CANCELLED, INDIVIDUAL_FILLS, REJECTED, EXPIRED)
            
        Returns:
            Dictionary containing order list information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/orders.json"
            
            # Add parameters and header information
            from ..utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            params = {"status": status}
            headers = {"consumerkey": config_manager.get_consumer_key()}
            
            # Make API call for GET request
            response = session.get(url, header_auth=True, params=params, headers=headers)
            logger.debug("Request Header: %s", response.request.headers)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "OrdersResponse" in data:
                    return data["OrdersResponse"]
                else:
                    raise Exception("Failed to retrieve order list from E*TRADE API")
            elif response is not None and response.status_code == 204:
                # No content - no orders
                return {}
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to get order list: {e}")
            raise
    
    def cancel_order(self, account_id_key: str, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            account_id_key: The accountIdKey for the account
            order_id: The order ID to cancel
            
        Returns:
            Dictionary containing cancellation information
        """
        if not self.auth_service.is_authenticated():
            raise ValueError("Not authenticated with E*TRADE. Complete OAuth flow first.")
        
        try:
            session = self.auth_service.get_session()
            base_url = self.auth_service.get_base_url()
            
            # URL for the API endpoint
            url = f"{base_url}/v1/accounts/{account_id_key}/orders/cancel.json"
            
            # Add parameters and header information
            from ..utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            headers = {"Content-Type": "application/xml", "consumerKey": config_manager.get_consumer_key()}
            
            # Create XML payload
            payload = f"""<CancelOrderRequest>
                <orderId>{order_id}</orderId>
            </CancelOrderRequest>"""
            
            # Make API call for PUT request
            response = session.put(url, header_auth=True, headers=headers, data=payload)
            logger.debug("Request Header: %s", response.request.headers)
            logger.debug("Request payload: %s", payload)
            
            # Handle and parse response
            if response is not None and response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                
                if data is not None and "CancelOrderResponse" in data:
                    return data["CancelOrderResponse"]
                else:
                    raise Exception("Failed to cancel order with E*TRADE API")
            else:
                raise Exception(f"E*TRADE API request failed with status code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            raise