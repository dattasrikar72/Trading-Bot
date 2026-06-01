"""Order management and placement logic"""

from typing import Dict, Any, Optional
from bot.client import BinanceClient, BinanceAPIError
from bot.validators import InputValidator, ValidationError
from bot.logging_config import logger


class OrderManager:
    """Manages order placement and tracking"""
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize OrderManager with API credentials.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.client = BinanceClient(api_key, api_secret)
        self.validator = InputValidator()
        logger.info("OrderManager initialized")
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: str, price: str = None) -> Dict[str, Any]:
        """
        Place an order with validation.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Limit price (optional for MARKET)
            
        Returns:
            Order placement result with status and details
            
        Example:
            >>> result = manager.place_order('BTCUSDT', 'BUY', 'MARKET', '0.001')
            >>> print(result['order_id'], result['status'])
        """
        logger.info(f"Attempting to place order: {side} {quantity} {symbol} ({order_type})")
        
        result = {
            'success': False,
            'order_id': None,
            'status': None,
            'message': '',
            'order_details': {}
        }
        
        try:
            # Validate inputs
            validated_symbol, validated_side, validated_order_type, validated_qty, validated_price = \
                self.validator.validate_all(symbol, side, order_type, quantity, price)
            
            logger.info(f"✓ Inputs validated: {validated_symbol} {validated_qty} {validated_side} {validated_order_type}")
            
            # Place order
            response = self.client.place_order(
                symbol=validated_symbol,
                side=validated_side,
                order_type=validated_order_type,
                quantity=validated_qty,
                price=validated_price if validated_price > 0 else None
            )
            
            # Process response
            result['success'] = True
            result['order_id'] = response.get('orderId')
            result['status'] = response.get('status')
            result['order_details'] = {
                'orderId': response.get('orderId'),
                'symbol': response.get('symbol'),
                'side': response.get('side'),
                'type': response.get('type'),
                'quantity': response.get('origQty'),
                'price': response.get('price'),
                'executedQty': response.get('executedQty'),
                'avgPrice': response.get('avgPrice'),
                'status': response.get('status'),
                'timeInForce': response.get('timeInForce'),
                'updateTime': response.get('updateTime'),
            }
            
            result['message'] = f"✓ Order placed successfully! Order ID: {result['order_id']}"
            logger.info(result['message'])
            
            return result
            
        except ValidationError as e:
            result['message'] = f"✗ Validation Error: {str(e)}"
            logger.error(result['message'])
            return result
            
        except BinanceAPIError as e:
            result['message'] = f"✗ API Error: {str(e)}"
            logger.error(result['message'])
            return result
            
        except Exception as e:
            result['message'] = f"✗ Unexpected Error: {str(e)}"
            logger.error(result['message'])
            return result
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get the status of a placed order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Order status details
        """
        try:
            logger.info(f"Fetching order status for {symbol} order {order_id}")
            response = self.client.get_order_status(symbol=symbol, order_id=order_id)
            
            return {
                'success': True,
                'order_id': response.get('orderId'),
                'status': response.get('status'),
                'executed_qty': response.get('executedQty'),
                'avg_price': response.get('avgPrice'),
                'details': response
            }
        except BinanceAPIError as e:
            logger.error(f"Failed to fetch order status: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def format_order_output(self, result: Dict[str, Any]) -> str:
        """
        Format order result for display.
        
        Args:
            result: Order placement result
            
        Returns:
            Formatted string for display
        """
        output = [
            "\n" + "="*60,
            "ORDER PLACEMENT RESULT",
            "="*60
        ]
        
        output.append(f"Status: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}")
        output.append(f"Message: {result['message']}")
        
        if result['success'] and result['order_details']:
            details = result['order_details']
            output.extend([
                "\nOrder Details:",
                f"  Order ID:      {details.get('orderId')}",
                f"  Symbol:        {details.get('symbol')}",
                f"  Side:          {details.get('side')}",
                f"  Type:          {details.get('type')}",
                f"  Quantity:      {details.get('quantity')}",
                f"  Price:         {details.get('price') or 'Market Price'}",
                f"  Executed Qty:  {details.get('executedQty')}",
                f"  Avg Price:     {details.get('avgPrice')}",
                f"  Status:        {details.get('status')}",
                f"  Time In Force: {details.get('timeInForce')}",
                f"  Update Time:   {details.get('updateTime')}",
            ])
        
        output.append("="*60 + "\n")
        return "\n".join(output)
    
    def close(self):
        """Close the client connection"""
        self.client.close()
        logger.info("OrderManager closed")
