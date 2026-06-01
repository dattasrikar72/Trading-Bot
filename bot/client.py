"""Binance Futures API Client wrapper"""

import os
import hashlib
import hmac
import time
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
from bot.logging_config import logger


class BinanceAPIError(Exception):
    """Binance API error"""
    pass


class BinanceClient:
    """
    Binance Futures API Client for testnet.
    Uses direct REST calls instead of python-binance for better control.
    """
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            
        Raises:
            ValueError: If credentials are empty
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
        logger.info(f"Binance client initialized with base URL: {self.BASE_URL}")
    
    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC SHA256 signature for request.
        
        Args:
            query_string: Query string to sign
            
        Returns:
            Hex digest signature
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_server_time(self) -> int:
        """
        Get current server time from Binance.
        
        Returns:
            Server timestamp in milliseconds
            
        Raises:
            BinanceAPIError: If request fails
        """
        try:
            response = requests.get(f"{self.BASE_URL}/fapi/v1/time", timeout=10)
            response.raise_for_status()
            return response.json()["serverTime"]
        except Exception as e:
            logger.error(f"Failed to get server time: {str(e)}")
            raise BinanceAPIError(f"Failed to get server time: {str(e)}")
    
    def _request(self, method: str, endpoint: str, params: Dict = None, 
                signed: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (e.g., /fapi/v1/order)
            params: Query/body parameters
            signed: Whether request requires signature
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response
            
        Raises:
            BinanceAPIError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        
        # Add timestamp and signature for signed requests
        if signed:
            params['timestamp'] = int(self._get_server_time())
            params['recvWindow'] = 5000
            
            query_string = urlencode(params)
            params['signature'] = self._generate_signature(query_string)
        
        headers = {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        logger.debug(f"[{method}] {endpoint} - Params: {params if not signed else {k: v for k, v in params.items() if k != 'signature'}}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params if method == 'GET' else None,
                data=params if method != 'GET' else None,
                headers=headers,
                timeout=10,
                **kwargs
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"API request failed: {error_msg}")
                raise BinanceAPIError(error_msg)
            
            result = response.json()
            logger.debug(f"Response: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: float = None, **kwargs) -> Dict[str, Any]:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            **kwargs: Additional parameters
            
        Returns:
            Order response from Binance
            
        Raises:
            BinanceAPIError: If order placement fails
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
        }
        
        if order_type == 'LIMIT':
            if not price:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = kwargs.get('timeInForce', 'GTC')
        
        # Add any additional parameters
        for key in ['positionSide', 'stopPrice', 'clientOrderId']:
            if key in kwargs:
                params[key] = kwargs[key]
        
        logger.info(f"Placing {order_type} {side} order: {symbol} {quantity} @ {price if price else 'market price'}")
        
        try:
            response = self._request(
                method='POST',
                endpoint='/fapi/v1/order',
                params=params,
                signed=True
            )
            
            logger.info(f"Order placed successfully: {response.get('orderId')}")
            return response
            
        except BinanceAPIError as e:
            logger.error(f"Failed to place order: {str(e)}")
            raise
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account info
            
        Raises:
            BinanceAPIError: If request fails
        """
        logger.info("Fetching account information")
        return self._request(
            method='GET',
            endpoint='/fapi/v2/account',
            signed=True
        )
    
    def get_order_status(self, symbol: str, order_id: int = None, 
                        client_order_id: str = None) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            client_order_id: Client order ID
            
        Returns:
            Order details
            
        Raises:
            BinanceAPIError: If request fails
        """
        params = {'symbol': symbol}
        
        if order_id:
            params['orderId'] = order_id
        elif client_order_id:
            params['origClientOrderId'] = client_order_id
        else:
            raise ValueError("Either orderId or clientOrderId must be provided")
        
        logger.debug(f"Fetching order status for {symbol}: {params}")
        return self._request(
            method='GET',
            endpoint='/fapi/v1/order',
            params=params,
            signed=True
        )
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("Binance client session closed")
