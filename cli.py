#!/usr/bin/env python3
"""
Command-line interface for Trading Bot
Handles user input and orchestrates order placement
"""

import sys
import os
from pathlib import Path
import click
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bot.orders import OrderManager
from bot.validators import ValidationError
from bot.logging_config import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TradingBotCLI:
    """Command-line interface for trading bot"""
    
    def __init__(self):
        """Initialize CLI"""
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.manager = None
    
    def validate_credentials(self) -> bool:
        """
        Validate API credentials are available.
        
        Returns:
            True if credentials available, False otherwise
        """
        if not self.api_key or not self.api_secret:
            click.secho(
                "❌ API credentials not found!",
                fg='red',
                bold=True
            )
            click.echo("\nPlease set environment variables:")
            click.echo("  export BINANCE_API_KEY='your_api_key'")
            click.echo("  export BINANCE_API_SECRET='your_api_secret'")
            click.echo("\nOr create a .env file in the project root:")
            click.echo("  BINANCE_API_KEY=your_api_key")
            click.echo("  BINANCE_API_SECRET=your_api_secret")
            return False
        
        return True
    
    def initialize_manager(self) -> bool:
        """
        Initialize OrderManager with API credentials.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.manager = OrderManager(self.api_key, self.api_secret)
            return True
        except Exception as e:
            click.secho(f"❌ Failed to initialize manager: {str(e)}", fg='red')
            logger.error(f"Failed to initialize manager: {str(e)}")
            return False
    
    def display_welcome(self):
        """Display welcome banner"""
        click.clear()
        click.secho("╔" + "═"*58 + "╗", fg='cyan')
        click.secho("║" + " "*58 + "║", fg='cyan')
        click.secho("║" + "BINANCE FUTURES TRADING BOT - TESTNET".center(58) + "║", fg='cyan', bold=True)
        click.secho("║" + " "*58 + "║", fg='cyan')
        click.secho("╚" + "═"*58 + "╝", fg='cyan')
        click.echo()
    
    def display_menu(self):
        """Display main menu"""
        click.secho("📋 Main Menu", fg='yellow', bold=True)
        click.echo("=" * 60)
        click.echo("1. Place Market Order")
        click.echo("2. Place Limit Order")
        click.echo("3. Interactive Mode")
        click.echo("4. Exit")
        click.echo("=" * 60)
    
    def prompt_market_order(self) -> Optional[dict]:
        """
        Prompt user for market order details.
        
        Returns:
            Order parameters or None if cancelled
        """
        click.echo()
        click.secho("📊 Market Order Details", fg='green', bold=True)
        click.echo("-" * 60)
        
        try:
            symbol = click.prompt("  Symbol (e.g., BTCUSDT)", type=str).strip().upper()
            if not symbol:
                click.secho("❌ Symbol cannot be empty", fg='red')
                return None
            
            side = click.prompt("  Side (BUY/SELL)", type=click.Choice(['BUY', 'SELL'], case_sensitive=False)).upper()
            
            quantity = click.prompt("  Quantity", type=str).strip()
            if not quantity:
                click.secho("❌ Quantity cannot be empty", fg='red')
                return None
            
            return {
                'symbol': symbol,
                'side': side,
                'order_type': 'MARKET',
                'quantity': quantity,
                'price': None
            }
        
        except click.exceptions.Abort:
            click.secho("\n⏸️  Cancelled", fg='yellow')
            return None
        except Exception as e:
            click.secho(f"❌ Error: {str(e)}", fg='red')
            logger.error(f"Error in market order prompt: {str(e)}")
            return None
    
    def prompt_limit_order(self) -> Optional[dict]:
        """
        Prompt user for limit order details.
        
        Returns:
            Order parameters or None if cancelled
        """
        click.echo()
        click.secho("📊 Limit Order Details", fg='green', bold=True)
        click.echo("-" * 60)
        
        try:
            symbol = click.prompt("  Symbol (e.g., BTCUSDT)", type=str).strip().upper()
            if not symbol:
                click.secho("❌ Symbol cannot be empty", fg='red')
                return None
            
            side = click.prompt("  Side (BUY/SELL)", type=click.Choice(['BUY', 'SELL'], case_sensitive=False)).upper()
            
            quantity = click.prompt("  Quantity", type=str).strip()
            if not quantity:
                click.secho("❌ Quantity cannot be empty", fg='red')
                return None
            
            price = click.prompt("  Price", type=str).strip()
            if not price:
                click.secho("❌ Price cannot be empty for LIMIT orders", fg='red')
                return None
            
            return {
                'symbol': symbol,
                'side': side,
                'order_type': 'LIMIT',
                'quantity': quantity,
                'price': price
            }
        
        except click.exceptions.Abort:
            click.secho("\n⏸️  Cancelled", fg='yellow')
            return None
        except Exception as e:
            click.secho(f"❌ Error: {str(e)}", fg='red')
            logger.error(f"Error in limit order prompt: {str(e)}")
            return None
    
    def display_order_result(self, result: dict):
        """
        Display formatted order result.
        
        Args:
            result: Order placement result
        """
        formatted = self.manager.format_order_output(result)
        
        if result['success']:
            click.secho(formatted, fg='green')
        else:
            click.secho(formatted, fg='red')
    
    def interactive_mode(self):
        """Interactive order placement loop"""
        click.secho("\n🔄 Interactive Mode (type 'quit' to exit)", fg='cyan', bold=True)
        
        while True:
            try:
                click.echo()
                order_type = click.prompt(
                    "Order type",
                    type=click.Choice(['market', 'limit', 'quit'], case_sensitive=False)
                ).lower()
                
                if order_type == 'quit':
                    break
                elif order_type == 'market':
                    params = self.prompt_market_order()
                else:  # limit
                    params = self.prompt_limit_order()
                
                if params:
                    result = self.manager.place_order(**params)
                    self.display_order_result(result)
                    
                    # Ask if user wants to place another order
                    another = click.confirm("\n📌 Place another order?", default=False)
                    if not another:
                        break
            
            except click.exceptions.Abort:
                break
            except Exception as e:
                click.secho(f"❌ Error: {str(e)}", fg='red')
                logger.error(f"Error in interactive mode: {str(e)}")
    
    def run(self):
        """Main CLI loop"""
        self.display_welcome()
        
        if not self.validate_credentials():
            sys.exit(1)
        
        if not self.initialize_manager():
            sys.exit(1)
        
        click.secho(
            "✅ Connected to Binance Futures Testnet",
            fg='green',
            bold=True
        )
        click.echo()
        
        while True:
            self.display_menu()
            
            try:
                choice = click.prompt("Select option", type=click.Choice(['1', '2', '3', '4']))
                
                if choice == '1':
                    params = self.prompt_market_order()
                    if params:
                        click.secho("\n⏳ Placing order...", fg='yellow')
                        result = self.manager.place_order(**params)
                        self.display_order_result(result)
                
                elif choice == '2':
                    params = self.prompt_limit_order()
                    if params:
                        click.secho("\n⏳ Placing order...", fg='yellow')
                        result = self.manager.place_order(**params)
                        self.display_order_result(result)
                
                elif choice == '3':
                    self.interactive_mode()
                
                elif choice == '4':
                    click.secho("\n👋 Goodbye!", fg='cyan', bold=True)
                    self.manager.close()
                    sys.exit(0)
            
            except click.exceptions.Abort:
                click.secho("\n⏸️  Cancelled", fg='yellow')
            except KeyboardInterrupt:
                click.secho("\n\n⚠️  Interrupted by user", fg='yellow')
                self.manager.close()
                sys.exit(0)
            except Exception as e:
                click.secho(f"❌ Error: {str(e)}", fg='red')
                logger.error(f"Error in main loop: {str(e)}")
            
            click.echo()


@click.command()
@click.option(
    '--symbol',
    type=str,
    help='Trading symbol (e.g., BTCUSDT)',
    default=None
)
@click.option(
    '--side',
    type=click.Choice(['BUY', 'SELL'], case_sensitive=False),
    help='Order side',
    default=None
)
@click.option(
    '--type',
    'order_type',
    type=click.Choice(['MARKET', 'LIMIT'], case_sensitive=False),
    help='Order type',
    default=None
)
@click.option(
    '--quantity',
    type=str,
    help='Order quantity',
    default=None
)
@click.option(
    '--price',
    type=str,
    help='Order price (required for LIMIT)',
    default=None
)
@click.option(
    '--interactive',
    is_flag=True,
    help='Start in interactive mode',
    default=False
)
@click.version_option(version='1.0.0', prog_name='Trading Bot')
def main(symbol, side, order_type, quantity, price, interactive):
    """
    Binance Futures Trading Bot - TESTNET
    
    Place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).
    
    Examples:
    
        # Interactive menu
        python cli.py
        
        # Interactive mode
        python cli.py --interactive
        
        # Quick market order
        python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
        
        # Quick limit order
        python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 2300.00
    """
    
    cli = TradingBotCLI()
    
    # If all parameters provided, execute single order and exit
    if symbol and side and order_type and quantity:
        if not cli.validate_credentials():
            sys.exit(1)
        
        if not cli.initialize_manager():
            sys.exit(1)
        
        click.secho(
            "✅ Connected to Binance Futures Testnet",
            fg='green',
            bold=True
        )
        
        # Validate order type specific requirements
        if order_type.upper() == 'LIMIT' and not price:
            click.secho("❌ Price is required for LIMIT orders", fg='red')
            sys.exit(1)
        
        click.secho("\n⏳ Placing order...", fg='yellow')
        
        result = cli.manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        cli.display_order_result(result)
        cli.manager.close()
        sys.exit(0 if result['success'] else 1)
    
    # Otherwise start interactive CLI
    if interactive:
        cli.validate_credentials()
        cli.initialize_manager()
        click.secho(
            "✅ Connected to Binance Futures Testnet",
            fg='green',
            bold=True
        )
        cli.interactive_mode()
        cli.manager.close()
        sys.exit(0)
    
    # Start normal menu
    cli.run()


if __name__ == '__main__':
    main()
