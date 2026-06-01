# Trading Bot - Binance Futures Testnet

A production-ready Python trading bot for placing orders on Binance Futures Testnet (USDT-M Futures).

## ✨ Features

- **Order Types**: MARKET and LIMIT orders
- **Order Sides**: BUY and SELL
- **CLI Interface**: Interactive menu, quick orders, and batch processing
- **API Wrapper**: Clean, reusable Binance client
- **Input Validation**: Comprehensive validation of all inputs
- **Error Handling**: Graceful handling of API errors and validation failures
- **Logging**: Structured logging to file and console
- **Testnet Ready**: Pre-configured for Binance Futures Testnet

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- pip

### 2. Setup

Clone or download the project:

```bash
cd Trading\ Bot
```

Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Get API Credentials

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Register and create account
3. Go to Account → API Management
4. Create new API key (testnet key)
5. Copy **API Key** and **Secret Key**

### 4. Configure Credentials

Create `.env` file in project root:

```bash
cat > .env << EOF
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
EOF
```

Or set environment variables:

```bash
export BINANCE_API_KEY='your_api_key'
export BINANCE_API_SECRET='your_api_secret'
```

## 📖 Usage

### Interactive Menu

Start the trading bot with interactive menu:

```bash
python cli.py
```

This opens a menu where you can:
1. Place Market Orders
2. Place Limit Orders
3. Enter Interactive Mode (multiple orders)
4. Exit

### Quick Command: Market Order

Place a market order from command line:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Quick Command: Limit Order

Place a limit order from command line:

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 2300.00
```

### Interactive Mode

Place multiple orders in a loop:

```bash
python cli.py --interactive
```

### Help

View all options:

```bash
python cli.py --help
```

## 🏗️ Project Structure

```
Trading Bot/
├── bot/
│   ├── __init__.py              # Package initialization
│   ├── client.py                # Binance API wrapper (HMAC signing, requests)
│   ├── orders.py                # Order management (validation, placement, formatting)
│   ├── validators.py            # Input validation (symbol, side, quantity, price)
│   └── logging_config.py        # Logging setup (file + console)
├── cli.py                       # Command-line interface
├── test_phase_1_2.py           # Unit tests (validators, client, logging)
├── test_integration.py         # Integration tests (simulated orders)
├── test_real_api.py            # Real API tests (requires credentials)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .env                         # API credentials (create this)
└── logs/                        # Log files (auto-generated)
    └── trading_bot_YYYYMMDD_HHMMSS.log
```

## 📋 Core Modules

### `bot/validators.py`

Validates all user inputs before sending to API:

```python
from bot.validators import InputValidator

validator = InputValidator()
symbol, side, order_type, qty, price = validator.validate_all(
    symbol="btcusdt",
    side="BUY", 
    order_type="LIMIT",
    quantity="0.1",
    price="45000"
)
```

**Validation Rules:**
- Symbol: Min 6 chars, ends with USDT/BUSD/USDC
- Side: BUY or SELL
- Order Type: MARKET or LIMIT
- Quantity: Positive, minimum 0.001
- Price: Positive for LIMIT, optional for MARKET

### `bot/client.py`

RESTful Binance API wrapper:

```python
from bot.client import BinanceClient

client = BinanceClient(api_key="xxx", api_secret="yyy")

# Place MARKET order
response = client.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity=0.001
)

# Get order status
order = client.get_order_status(symbol="BTCUSDT", order_id=123456)

# Get account info
account = client.get_account_info()

client.close()
```

### `bot/orders.py`

High-level order management:

```python
from bot.orders import OrderManager

manager = OrderManager(api_key="xxx", api_secret="yyy")

# Place order (validates + sends + formats)
result = manager.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity="0.001"
)

# Result structure:
# {
#     'success': True,
#     'order_id': 8389765432101,
#     'status': 'FILLED',
#     'message': '✓ Order placed successfully! Order ID: ...',
#     'order_details': {...}
# }

# Display formatted output
print(manager.format_order_output(result))

manager.close()
```

### `bot/logging_config.py`

Structured logging to file and console:

```python
from bot.logging_config import logger

logger.info("Order placed successfully")
logger.error("API connection failed")
logger.debug("Full request details")
```

**Log Format:**
```
2026-06-01 22:19:13 - trading_bot - INFO - [place_order:43] - Order placed
```

**Log Location:**
```
logs/trading_bot_20260601_221913.log
```

## 🧪 Testing

### Unit Tests

Test validators, logging, and client initialization:

```bash
python test_phase_1_2.py
```

**Coverage:**
- Input validation (10 tests)
- Logging configuration (4 tests)
- Module imports (3 tests)
- Client initialization (2 tests)
- Order manager (3 tests)

### Integration Tests

Test order placement with simulated responses:

```bash
python test_integration.py
```

**Coverage:**
- MARKET order success
- LIMIT order success
- API error handling
- Validation error handling
- Missing price validation

### Real API Tests

Test with actual Binance Testnet API (requires credentials):

```bash
python test_real_api.py
```

**Tests:**
1. Account connection
2. MARKET order placement
3. LIMIT order placement
4. Invalid input handling

**Output:**
```
TEST SUMMARY
============================================================
✅ Passed: 4/4
Success Rate: 100.0%

Results saved to: logs/api_test_results.json
```

## 🔧 Configuration

### Environment Variables

```bash
export BINANCE_API_KEY='your_api_key'
export BINANCE_API_SECRET='your_api_secret'
```

### .env File

Create `.env` in project root:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

### API Base URL

Current testnet URL (pre-configured):
```
https://testnet.binancefuture.com
```

To use mainnet (production), modify [bot/client.py](bot/client.py):
```python
BASE_URL = "https://fapi.binance.com"  # Mainnet
```

⚠️ **WARNING**: Never use mainnet with test credentials or logic!

## 📝 Logging

Logs are stored in `logs/` directory with timestamp:

```
logs/trading_bot_20260601_221913.log
```

### Log Levels

- **DEBUG**: Detailed API requests, responses, and internal flow
- **INFO**: Order placement, validation passes, connection status
- **WARNING**: Non-critical issues (e.g., price ignored for MARKET)
- **ERROR**: Validation failures, API errors, exceptions

### View Logs

```bash
# View latest log
tail -50 logs/*.log

# Search for errors
grep ERROR logs/*.log

# Follow real-time logs
tail -f logs/*.log
```

## 🛠️ Development

### Running Unit Tests

```bash
source venv/bin/activate
python test_phase_1_2.py
```

### Running Integration Tests

```bash
python test_integration.py
```

### Running Real API Tests

```bash
# Requires .env file with credentials
python test_real_api.py
```

### Code Structure

```
bot/
├── client.py          # REST API implementation
│   ├── BinanceClient  # Main API client class
│   └── BinanceAPIError # Custom exception
├── orders.py          # Business logic
│   └── OrderManager   # High-level order management
├── validators.py      # Input validation
│   └── InputValidator # Validation rules
└── logging_config.py  # Logging setup
    └── setup_logging() # Logger factory
```

## 📊 API Response Examples

### Successful Market Order

```json
{
    "orderId": 8389765432101,
    "symbol": "BTCUSDT",
    "status": "FILLED",
    "side": "BUY",
    "type": "MARKET",
    "origQty": "0.001",
    "executedQty": "0.001",
    "avgPrice": "45250.50",
    "timeInForce": "IOC",
    "updateTime": 1685097897123
}
```

### Successful Limit Order

```json
{
    "orderId": 8389765432102,
    "symbol": "ETHUSDT",
    "status": "NEW",
    "side": "SELL",
    "type": "LIMIT",
    "price": "2300.00",
    "origQty": "0.5",
    "executedQty": "0",
    "avgPrice": "0",
    "timeInForce": "GTC",
    "updateTime": 1685097900000
}
```

## ❌ Error Handling

### Validation Errors

```python
result = manager.place_order(
    symbol="BTCUSDT",
    side="INVALID",  # Will be rejected
    order_type="MARKET",
    quantity="0.001"
)

# result['success'] = False
# result['message'] = "✗ Validation Error: Invalid side: INVALID. Must be BUY or SELL"
```

### API Errors

```python
result = manager.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity="0.001"
)

# If API key is invalid:
# result['success'] = False
# result['message'] = "✗ API Error: HTTP 401: Unauthorized - Invalid API key or secret"
```

### Handled Exceptions

1. **ValidationError**: Input validation failures
2. **BinanceAPIError**: HTTP errors, timeouts, malformed responses
3. **General Exception**: Unexpected errors (logged and reported)

## 🔒 Security

### API Credentials

- ✅ Use environment variables (not hardcoded)
- ✅ Use `.env` file (add to `.gitignore`)
- ✅ Never commit credentials
- ✅ Use testnet credentials for testing
- ✅ Rotate credentials regularly

### Request Signing

All authenticated requests use HMAC-SHA256 signature with:
- Current server time
- Request parameters
- API secret key

### Connection

- HTTPS only (pre-configured)
- 10-second timeout per request
- Automatic server time synchronization

## 📋 Order Parameters

### MARKET Order

```python
manager.place_order(
    symbol="BTCUSDT",    # Required: Trading pair
    side="BUY",          # Required: BUY or SELL
    order_type="MARKET", # Required: MARKET
    quantity="0.001"     # Required: Amount in base asset
)
```

### LIMIT Order

```python
manager.place_order(
    symbol="ETHUSDT",    # Required: Trading pair
    side="SELL",         # Required: BUY or SELL
    order_type="LIMIT",  # Required: LIMIT
    quantity="0.5",      # Required: Amount in base asset
    price="2300.00"      # Required: Limit price
)
```

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **Memory**: 100 MB minimum
- **Storage**: 1 MB for logs
- **Network**: HTTPS to `testnet.binancefuture.com`

## 🐛 Troubleshooting

### "API credentials not found"

```bash
# Set environment variables
export BINANCE_API_KEY='your_key'
export BINANCE_API_SECRET='your_secret'

# Or create .env file
cat > .env << EOF
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
EOF
```

### "HTTP 401: Unauthorized"

- API key or secret is invalid
- Testnet credentials don't match
- API key has expired (regenerate)

### "Price is required for LIMIT orders"

- Add `--price` parameter for LIMIT orders
- Example: `--type LIMIT --quantity 0.5 --price 2300.00`

### "Quantity too small"

- Minimum quantity is 0.001
- Try increasing quantity

### "Invalid symbol"

- Use correct symbol format: BTCUSDT, ETHUSDT, etc.
- Must end with USDT, BUSD, or USDC
- Use uppercase

## 📚 References

- [Binance Futures API Docs](https://binance-docs.github.io/apidocs/futures/en/)
- [Binance Testnet](https://testnet.binancefuture.com)
- [HMAC-SHA256 Signing](https://binance-docs.github.io/apidocs/futures/en/#signed-trade-user_data-endpoint)

## 📄 License

This project is provided as-is for educational and testing purposes.

## ✉️ Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review log files in `logs/` directory
3. Verify API credentials and connectivity
4. Test with `test_real_api.py` for detailed diagnostics

## 🎯 Next Steps

1. **Test**: Run `test_real_api.py` with valid credentials
2. **Experiment**: Place test orders on testnet
3. **Monitor**: Check logs and API responses
4. **Extend**: Add additional order types (Stop-Limit, OCO, etc.)

---

**Version**: 1.0.0  
**Last Updated**: June 2026  
**Status**: ✅ Production Ready for Testnet
