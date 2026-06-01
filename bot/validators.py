"""Input validation for Trading Bot"""

from typing import Tuple
from bot.logging_config import logger


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validates user inputs for order placement"""
    
    # Valid order sides
    VALID_SIDES = {"BUY", "SELL"}
    
    # Valid order types
    VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
    
    # Minimum values
    MIN_QUANTITY = 0.001
    MIN_PRICE = 0.00000001
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> str:
        """
        Validate trading symbol format.
        
        Args:
            symbol: Symbol (e.g., BTCUSDT)
            
        Returns:
            Validated symbol in uppercase
            
        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol:
            raise ValidationError("Symbol cannot be empty")
        
        symbol = symbol.upper().strip()
        
        if len(symbol) < 6:
            raise ValidationError(f"Invalid symbol: {symbol}. Must be at least 6 characters (e.g., BTCUSDT)")
        
        if not symbol.endswith(("USDT", "BUSD", "USDC")):
            logger.warning(f"Symbol {symbol} may not be a standard futures pair")
        
        return symbol
    
    @classmethod
    def validate_side(cls, side: str) -> str:
        """
        Validate order side.
        
        Args:
            side: Order side (BUY/SELL)
            
        Returns:
            Validated side in uppercase
            
        Raises:
            ValidationError: If side is invalid
        """
        if not side:
            raise ValidationError("Side cannot be empty")
        
        side = side.upper().strip()
        
        if side not in cls.VALID_SIDES:
            raise ValidationError(f"Invalid side: {side}. Must be BUY or SELL")
        
        return side
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> str:
        """
        Validate order type.
        
        Args:
            order_type: Order type (MARKET/LIMIT)
            
        Returns:
            Validated order type in uppercase
            
        Raises:
            ValidationError: If order type is invalid
        """
        if not order_type:
            raise ValidationError("Order type cannot be empty")
        
        order_type = order_type.upper().strip()
        
        if order_type not in cls.VALID_ORDER_TYPES:
            raise ValidationError(f"Invalid order type: {order_type}. Must be MARKET or LIMIT")
        
        return order_type
    
    @classmethod
    def validate_quantity(cls, quantity: str) -> float:
        """
        Validate order quantity.
        
        Args:
            quantity: Order quantity as string
            
        Returns:
            Validated quantity as float
            
        Raises:
            ValidationError: If quantity is invalid
        """
        try:
            qty = float(quantity)
        except ValueError:
            raise ValidationError(f"Invalid quantity: {quantity}. Must be a valid number")
        
        if qty <= 0:
            raise ValidationError(f"Quantity must be positive, got {qty}")
        
        if qty < cls.MIN_QUANTITY:
            raise ValidationError(f"Quantity too small: {qty}. Minimum is {cls.MIN_QUANTITY}")
        
        return qty
    
    @classmethod
    def validate_price(cls, price: str, order_type: str) -> float:
        """
        Validate order price.
        
        Args:
            price: Order price as string
            order_type: Order type (MARKET/LIMIT)
            
        Returns:
            Validated price as float
            
        Raises:
            ValidationError: If price is invalid
        """
        if order_type.upper() == "MARKET":
            if price:
                logger.warning("Price is ignored for MARKET orders")
            return 0.0
        
        if not price:
            raise ValidationError("Price is required for LIMIT orders")
        
        try:
            p = float(price)
        except ValueError:
            raise ValidationError(f"Invalid price: {price}. Must be a valid number")
        
        if p <= 0:
            raise ValidationError(f"Price must be positive, got {p}")
        
        if p < cls.MIN_PRICE:
            raise ValidationError(f"Price too small: {p}. Minimum is {cls.MIN_PRICE}")
        
        return p
    
    @classmethod
    def validate_all(cls, symbol: str, side: str, order_type: str, 
                    quantity: str, price: str = None) -> Tuple[str, str, str, float, float]:
        """
        Validate all input parameters at once.
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (optional for MARKET)
            
        Returns:
            Tuple of validated (symbol, side, order_type, quantity, price)
            
        Raises:
            ValidationError: If any parameter is invalid
        """
        logger.debug(f"Validating inputs: symbol={symbol}, side={side}, type={order_type}, qty={quantity}, price={price}")
        
        try:
            validated_symbol = cls.validate_symbol(symbol)
            validated_side = cls.validate_side(side)
            validated_order_type = cls.validate_order_type(order_type)
            validated_quantity = cls.validate_quantity(quantity)
            validated_price = cls.validate_price(price, order_type)
            
            logger.debug("All inputs validated successfully")
            return validated_symbol, validated_side, validated_order_type, validated_quantity, validated_price
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
