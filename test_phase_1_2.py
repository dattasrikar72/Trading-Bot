"""
Test script to validate Phase 1 & 2 implementation
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.validators import InputValidator, ValidationError
from bot.logging_config import logger
from bot.client import BinanceClient, BinanceAPIError
from bot.orders import OrderManager


def test_validators():
    """Test input validation"""
    print("\n" + "="*60)
    print("TEST 1: INPUT VALIDATORS")
    print("="*60)
    
    validator = InputValidator()
    
    # Test valid symbol
    try:
        symbol = validator.validate_symbol("btcusdt")
        print(f"✓ Symbol validation: '{symbol}' (converted to uppercase)")
    except ValidationError as e:
        print(f"✗ Symbol validation failed: {e}")
    
    # Test invalid symbol
    try:
        validator.validate_symbol("BTC")
        print("✗ Should have rejected short symbol")
    except ValidationError as e:
        print(f"✓ Correctly rejected short symbol: {e}")
    
    # Test valid side
    try:
        side = validator.validate_side("buy")
        print(f"✓ Side validation: '{side}' (converted to uppercase)")
    except ValidationError as e:
        print(f"✗ Side validation failed: {e}")
    
    # Test invalid side
    try:
        validator.validate_side("INVALID")
        print("✗ Should have rejected invalid side")
    except ValidationError as e:
        print(f"✓ Correctly rejected invalid side: {e}")
    
    # Test valid order type
    try:
        order_type = validator.validate_order_type("limit")
        print(f"✓ Order type validation: '{order_type}'")
    except ValidationError as e:
        print(f"✗ Order type validation failed: {e}")
    
    # Test valid quantity
    try:
        qty = validator.validate_quantity("0.5")
        print(f"✓ Quantity validation: {qty}")
    except ValidationError as e:
        print(f"✗ Quantity validation failed: {e}")
    
    # Test invalid quantity
    try:
        validator.validate_quantity("-1")
        print("✗ Should have rejected negative quantity")
    except ValidationError as e:
        print(f"✓ Correctly rejected negative quantity: {e}")
    
    # Test price for MARKET
    try:
        price = validator.validate_price("100", "MARKET")
        print(f"✓ Market order price validation: {price} (ignored for MARKET)")
    except ValidationError as e:
        print(f"✗ Price validation failed: {e}")
    
    # Test price for LIMIT
    try:
        price = validator.validate_price("45000", "LIMIT")
        print(f"✓ Limit order price validation: {price}")
    except ValidationError as e:
        print(f"✗ Price validation failed: {e}")
    
    # Test missing price for LIMIT
    try:
        validator.validate_price(None, "LIMIT")
        print("✗ Should have rejected missing price for LIMIT")
    except ValidationError as e:
        print(f"✓ Correctly rejected missing price for LIMIT: {e}")
    
    # Test validate_all
    try:
        sym, side, order_type, qty, price = validator.validate_all(
            "btcusdt", "BUY", "LIMIT", "0.1", "45000"
        )
        print(f"✓ Full validation passed: {sym} {qty} {side} {order_type} @ {price}")
    except ValidationError as e:
        print(f"✗ Full validation failed: {e}")


def test_logging():
    """Test logging setup"""
    print("\n" + "="*60)
    print("TEST 2: LOGGING CONFIGURATION")
    print("="*60)
    
    try:
        # Check if logger is configured
        print(f"✓ Logger name: {logger.name}")
        print(f"✓ Logger level: {logger.level}")
        print(f"✓ Number of handlers: {len(logger.handlers)}")
        
        for i, handler in enumerate(logger.handlers):
            print(f"  Handler {i}: {handler.__class__.__name__}")
        
        # Test logging
        logger.info("✓ Info message test")
        logger.debug("✓ Debug message test")
        logger.warning("✓ Warning message test")
        
        print("✓ Logging configured successfully")
        
        # Check if logs directory exists
        logs_path = Path("logs")
        if logs_path.exists():
            log_files = list(logs_path.glob("*.log"))
            print(f"✓ Found {len(log_files)} log file(s)")
            if log_files:
                print(f"  Latest: {log_files[-1].name}")
        
    except Exception as e:
        print(f"✗ Logging test failed: {e}")


def test_imports():
    """Test all imports"""
    print("\n" + "="*60)
    print("TEST 3: MODULE IMPORTS")
    print("="*60)
    
    try:
        from bot import BinanceClient, OrderManager, InputValidator
        print("✓ Successfully imported from bot package")
        print(f"  - BinanceClient: {BinanceClient.__module__}")
        print(f"  - OrderManager: {OrderManager.__module__}")
        print(f"  - InputValidator: {InputValidator.__module__}")
    except ImportError as e:
        print(f"✗ Import failed: {e}")


def test_binance_client_initialization():
    """Test BinanceClient initialization"""
    print("\n" + "="*60)
    print("TEST 4: BINANCE CLIENT INITIALIZATION")
    print("="*60)
    
    try:
        # Test with empty credentials (should fail)
        try:
            client = BinanceClient("", "")
            print("✗ Should have rejected empty credentials")
        except ValueError as e:
            print(f"✓ Correctly rejected empty credentials: {e}")
        
        # Test with dummy credentials (should succeed)
        client = BinanceClient("test_key", "test_secret")
        print(f"✓ BinanceClient initialized successfully")
        print(f"  Base URL: {client.BASE_URL}")
        print(f"  API Key: {client.api_key[:10]}...")
        client.close()
        print("✓ Client closed successfully")
        
    except Exception as e:
        print(f"✗ Client initialization test failed: {e}")


def test_order_manager_initialization():
    """Test OrderManager initialization"""
    print("\n" + "="*60)
    print("TEST 5: ORDER MANAGER INITIALIZATION")
    print("="*60)
    
    try:
        manager = OrderManager("test_key", "test_secret")
        print("✓ OrderManager initialized successfully")
        
        # Test format_order_output
        dummy_result = {
            'success': True,
            'order_id': 123456,
            'message': 'Order placed successfully! Order ID: 123456',
            'order_details': {
                'orderId': 123456,
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'type': 'MARKET',
                'quantity': '0.1',
                'price': '0',
                'executedQty': '0.1',
                'avgPrice': '45000',
                'status': 'FILLED',
                'timeInForce': 'IOC',
                'updateTime': 1234567890,
            }
        }
        
        formatted = manager.format_order_output(dummy_result)
        print("✓ Order output formatting works:")
        print(formatted)
        
        manager.close()
        print("✓ OrderManager closed successfully")
        
    except Exception as e:
        print(f"✗ OrderManager test failed: {e}")


def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "TRADING BOT - PHASE 1 & 2 VALIDATION TESTS".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    test_imports()
    test_validators()
    test_logging()
    test_binance_client_initialization()
    test_order_manager_initialization()
    
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "ALL TESTS COMPLETED".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")


if __name__ == "__main__":
    main()
