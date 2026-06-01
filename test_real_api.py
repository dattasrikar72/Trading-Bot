#!/usr/bin/env python3
"""
Phase 4: Real API Testing
Tests with actual Binance Futures Testnet API
Requires valid API credentials in .env file
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.orders import OrderManager
from bot.client import BinanceAPIError
from bot.logging_config import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RealAPITester:
    """Tests using real Binance Futures Testnet API"""
    
    def __init__(self):
        """Initialize tester"""
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.manager = None
        self.test_results = []
    
    def check_credentials(self) -> bool:
        """
        Check if API credentials are available.
        
        Returns:
            True if credentials available
        """
        if not self.api_key or not self.api_secret:
            print("\n❌ API CREDENTIALS NOT FOUND")
            print("=" * 60)
            print("Please set the following environment variables:")
            print("  export BINANCE_API_KEY='your_api_key'")
            print("  export BINANCE_API_SECRET='your_api_secret'")
            print("\nOr create a .env file:")
            print("  BINANCE_API_KEY=your_api_key")
            print("  BINANCE_API_SECRET=your_api_secret")
            print("=" * 60)
            return False
        
        print("\n✅ API credentials found")
        return True
    
    def initialize(self) -> bool:
        """
        Initialize manager with real credentials.
        
        Returns:
            True if successful
        """
        try:
            self.manager = OrderManager(self.api_key, self.api_secret)
            print("✅ OrderManager initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize: {str(e)}")
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """
        Log test result.
        
        Args:
            test_name: Name of test
            success: Whether test passed
            details: Additional details
        """
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} | {test_name}")
        if details:
            print(f"     {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_account_connection(self) -> bool:
        """
        Test basic account connection.
        
        Returns:
            True if connection successful
        """
        print("\n" + "="*60)
        print("TEST 1: Account Connection")
        print("="*60)
        
        try:
            account_info = self.manager.client.get_account_info()
            
            print(f"✅ Successfully connected to Binance Testnet")
            print(f"  Account info retrieved")
            print(f"  Positions: {len(account_info.get('positions', []))}")
            
            self.log_test_result(
                "Account Connection",
                True,
                f"Positions count: {len(account_info.get('positions', []))}"
            )
            return True
            
        except BinanceAPIError as e:
            error_msg = str(e)
            print(f"❌ Connection failed: {error_msg}")
            self.log_test_result("Account Connection", False, error_msg)
            return False
    
    def test_market_order(self, symbol: str = "BTCUSDT", side: str = "BUY", 
                         quantity: str = "0.001") -> bool:
        """
        Test placing a MARKET order.
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            
        Returns:
            True if order placed successfully
        """
        print("\n" + "="*60)
        print(f"TEST 2: MARKET Order ({side} {quantity} {symbol})")
        print("="*60)
        
        try:
            result = self.manager.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=quantity
            )
            
            print(self.manager.format_order_output(result))
            
            if result['success']:
                self.log_test_result(
                    f"MARKET Order ({side} {quantity} {symbol})",
                    True,
                    f"Order ID: {result['order_id']}, Status: {result['status']}"
                )
                return True
            else:
                self.log_test_result(
                    f"MARKET Order ({side} {quantity} {symbol})",
                    False,
                    result['message']
                )
                return False
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.log_test_result(
                f"MARKET Order ({side} {quantity} {symbol})",
                False,
                str(e)
            )
            return False
    
    def test_limit_order(self, symbol: str = "ETHUSDT", side: str = "SELL", 
                        quantity: str = "0.5", price: str = "2300.00") -> bool:
        """
        Test placing a LIMIT order.
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            price: Limit price
            
        Returns:
            True if order placed successfully
        """
        print("\n" + "="*60)
        print(f"TEST 3: LIMIT Order ({side} {quantity} {symbol} @ {price})")
        print("="*60)
        
        try:
            result = self.manager.place_order(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                quantity=quantity,
                price=price
            )
            
            print(self.manager.format_order_output(result))
            
            if result['success']:
                self.log_test_result(
                    f"LIMIT Order ({side} {quantity} {symbol} @ {price})",
                    True,
                    f"Order ID: {result['order_id']}, Status: {result['status']}"
                )
                return True
            else:
                self.log_test_result(
                    f"LIMIT Order ({side} {quantity} {symbol} @ {price})",
                    False,
                    result['message']
                )
                return False
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.log_test_result(
                f"LIMIT Order ({side} {quantity} {symbol} @ {price})",
                False,
                str(e)
            )
            return False
    
    def test_invalid_inputs(self) -> bool:
        """
        Test handling of invalid inputs.
        
        Returns:
            True if validation works correctly
        """
        print("\n" + "="*60)
        print("TEST 4: Invalid Input Handling")
        print("="*60)
        
        all_passed = True
        
        # Test 1: Invalid quantity
        print("\n  Test 4.1: Negative quantity")
        result = self.manager.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity="-0.1"
        )
        
        if not result['success'] and "Validation Error" in result['message']:
            print(f"  ✓ Correctly rejected: {result['message']}")
            self.log_test_result(
                "Invalid Input - Negative Quantity",
                True,
                "Correctly rejected"
            )
        else:
            print(f"  ✗ Should have rejected negative quantity")
            all_passed = False
            self.log_test_result(
                "Invalid Input - Negative Quantity",
                False,
                "Failed to reject"
            )
        
        # Test 2: Missing price for LIMIT
        print("\n  Test 4.2: Missing price for LIMIT order")
        result = self.manager.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="LIMIT",
            quantity="0.1",
            price=None
        )
        
        if not result['success'] and "Validation Error" in result['message']:
            print(f"  ✓ Correctly rejected: {result['message']}")
            self.log_test_result(
                "Invalid Input - Missing LIMIT Price",
                True,
                "Correctly rejected"
            )
        else:
            print(f"  ✗ Should have required price for LIMIT")
            all_passed = False
            self.log_test_result(
                "Invalid Input - Missing LIMIT Price",
                False,
                "Failed to reject"
            )
        
        # Test 3: Invalid side
        print("\n  Test 4.3: Invalid side")
        result = self.manager.place_order(
            symbol="BTCUSDT",
            side="INVALID",
            order_type="MARKET",
            quantity="0.1"
        )
        
        if not result['success'] and "Validation Error" in result['message']:
            print(f"  ✓ Correctly rejected: {result['message']}")
            self.log_test_result(
                "Invalid Input - Invalid Side",
                True,
                "Correctly rejected"
            )
        else:
            print(f"  ✗ Should have rejected invalid side")
            all_passed = False
            self.log_test_result(
                "Invalid Input - Invalid Side",
                False,
                "Failed to reject"
            )
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if not self.test_results:
            print("No tests ran")
            return
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        # Save results to file
        results_file = Path("logs") / "api_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📝 Results saved to: {results_file}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█" + "PHASE 4: REAL API TESTING".center(58) + "█")
        print("█" + "Binance Futures Testnet".center(58) + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        
        if not self.check_credentials():
            return False
        
        if not self.initialize():
            return False
        
        print("\n⏳ Running tests...\n")
        
        # Run tests
        try:
            self.test_account_connection()
            self.test_market_order()
            self.test_limit_order()
            self.test_invalid_inputs()
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            logger.error(f"Unexpected error during tests: {str(e)}")
        
        finally:
            if self.manager:
                self.manager.close()
        
        # Print summary
        self.print_summary()
        
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█" + "TESTING COMPLETE".center(58) + "█")
        print("█" + " "*58 + "█")
        print("█"*60 + "\n")


def main():
    """Main entry point"""
    tester = RealAPITester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
