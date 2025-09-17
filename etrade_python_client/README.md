# E*TRADE API Integration for AI Trading Assistant

This document provides detailed information about the E*TRADE API integration implemented for the AI Trading Assistant project.

## Overview

The E*TRADE API integration enables the AI Trading Assistant to:

1. Authenticate with E*TRADE accounts using OAuth 1.0a
2. Retrieve real-time account information and portfolio data
3. Execute trades based on AI recommendations
4. Synchronize portfolio data with the local database
5. Display comprehensive account information in the frontend

## Architecture

The integration follows a service-oriented architecture with clearly separated components:

### Backend Services

1. **ETradeAuth** (`services/etrade_auth.py`)
   - Implements OAuth 1.0a authentication flow
   - Manages authentication tokens and session state
   - Supports both sandbox and production environments

2. **ETradeAccountService** (`services/etrade_account_service.py`)
   - Retrieves account lists, balances, and portfolio data
   - Processes E*TRADE API responses into structured data
   - Handles error conditions and API limitations

3. **ETradeOrderService** (`services/etrade_order_service.py`)
   - Implements order preview and placement functionality
   - Supports market and limit orders with various terms
   - Manages order lifecycle (preview, place, list, cancel)

4. **Celery Tasks** (`services/tasks.py`)
   - `sync_etrade_portfolio`: Periodic portfolio synchronization
   - `execute_etrade_trades`: Automated trade execution based on AI decisions

### Frontend Components

1. **ETradeWidget** (`frontend/src/components/ETradeWidget.tsx`)
   - Displays account information and portfolio data
   - Handles OAuth authentication flow
   - Provides account selection for users with multiple accounts

2. **ETradeTradeWidget** (`frontend/src/components/ETradeTradeWidget.tsx`)
   - Interface for executing trades
   - Order preview functionality
   - Support for different order types (market, limit)

## API Endpoints

### Authentication

- `POST /api/etrade/oauth/initiate` - Initiate OAuth flow
  - Parameters: `use_sandbox` (boolean, default: true)
  - Returns: Authorization URL for E*TRADE

- `POST /api/etrade/oauth/complete` - Complete OAuth flow
  - Body: `{ "verification_code": "string" }`
  - Returns: Success confirmation

- `GET /api/etrade/auth/status` - Check authentication status
  - Returns: `{ "authenticated": boolean }`

### Account Information

- `GET /api/etrade/accounts` - List E*TRADE accounts
  - Returns: List of accounts with basic information

- `GET /api/etrade/accounts/{account_id_key}/balance` - Get account balance
  - Returns: Detailed account balance information including buying power

- `GET /api/etrade/accounts/{account_id_key}/portfolio` - Get portfolio data
  - Returns: List of positions with market values and gains

### Order Management

- `POST /api/etrade/accounts/{account_id_key}/orders/preview` - Preview an order
  - Body: 
    ```json
    {
      "symbol": "string",
      "order_action": "BUY|SELL|BUY_TO_COVER|SELL_SHORT",
      "quantity": integer,
      "price_type": "MARKET|LIMIT",
      "order_term": "GOOD_FOR_DAY|IMMEDIATE_OR_CANCEL|FILL_OR_KILL",
      "limit_price": number (optional)
    }
    ```
  - Returns: Order preview with estimated costs

- `POST /api/etrade/accounts/{account_id_key}/orders/place` - Place an order
  - Body: Same as preview endpoint
  - Returns: Confirmation of order placement

- `GET /api/etrade/accounts/{account_id_key}/orders` - List orders
  - Parameters: `status` (OPEN, EXECUTED, CANCELLED, etc.)
  - Returns: List of orders with status information

- `POST /api/etrade/accounts/{account_id_key}/orders/cancel` - Cancel an order
  - Body: `{ "order_id": "string" }`
  - Returns: Cancellation confirmation

## Setup and Configuration

### Prerequisites

1. E*TRADE Developer Account - Register at https://us.etrade.com
2. E*TRADE API Credentials (Consumer Key and Secret)
3. Redis Server (for background task processing)

### Configuration

The integration uses the existing `config.ini` configuration file:

```ini
[DEFAULT]
CONSUMER_KEY = your_consumer_key
CONSUMER_SECRET = your_consumer_secret
SANDBOX_BASE_URL = https://apisb.etrade.com
PROD_BASE_URL = https://api.etrade.com

[AI_SERVICES]
AUTO_TRADING_ENABLED = true
AI_CONFIDENCE_THRESHOLD = 0.7
```

### Starting the Services

1. **Start the FastAPI backend**:
   ```bash
   python run_server.py
   ```

2. **Start Redis server** (in a separate terminal):
   ```bash
   redis-server
   ```

3. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A etrade_python_client.services.celery_app worker --loglevel=info
   ```

4. **Start Celery beat** (in a separate terminal):
   ```bash
   celery -A etrade_python_client.services.celery_app beat --loglevel=info
   ```

5. **Start the React frontend** (in a separate terminal):
   ```bash
   cd frontend
   npm start
   ```

## Usage Guide

### Authentication Flow

1. Open the web interface at `http://localhost:3000`
2. Navigate to the E*TRADE Account widget
3. Click "Connect E*TRADE" to begin the authentication process
4. Choose between sandbox (testing) and production environments
5. Complete the OAuth flow in the E*TRADE window that opens
6. Enter the verification code in the dialog
7. Authentication is now complete and persistent for the session

### Viewing Account Information

Once authenticated, the E*TRADE Account widget will display:
- Account selection dropdown (for users with multiple accounts)
- Account balance information (total value, cash balance, buying power)
- Portfolio positions with current values and gains
- Real-time updates every 15 minutes via background tasks

### Executing Trades

To execute trades manually:

1. Navigate to the E*TRADE Trading widget
2. Select the account to use for trading
3. Enter the stock symbol
4. Choose order action (Buy/Sell)
5. Specify quantity
6. Select price type (Market/Limit)
7. For limit orders, specify limit price and order term
8. Click "Preview Order" to review details
9. Confirm and place the order

### Automated Trading

The system can automatically execute trades based on AI recommendations:

1. AI decisions are generated based on market analysis
2. High-confidence decisions (above threshold) are queued for execution
3. The `execute_etrade_trades` Celery task runs every 30 minutes
4. Eligible trades are executed automatically
5. Execution results are recorded in the system

## Security Considerations

### Authentication Security

- OAuth tokens are stored in memory only and never written to disk
- All API communication uses HTTPS encryption
- Consumer key and secret are stored in `config.ini` which should be protected
- Access tokens are not exposed to the frontend

### Data Protection

- Account data is only accessible to authenticated users
- Portfolio information is stored locally and not shared externally
- Trade execution requires explicit user authentication

### Best Practices

1. Use the sandbox environment for testing
2. Never commit `config.ini` with real credentials to version control
3. Regularly review and rotate API credentials
4. Monitor account activity for unauthorized trades

## Limitations and Considerations

### Current Limitations

1. **Single Account Support**: Currently only supports one E*TRADE account per session
2. **Equity Orders Only**: Does not support options, mutual funds, or other security types
3. **Sandbox Focus**: Primarily tested with E*TRADE sandbox environment
4. **Rate Limits**: E*TRADE API rate limits may affect functionality during heavy usage

### Performance Considerations

1. **API Rate Limits**: E*TRADE imposes rate limits on API calls
2. **Background Processing**: Portfolio sync and trade execution happen asynchronously
3. **Network Latency**: API response times may vary based on E*TRADE system performance

### Error Handling

The integration includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid credentials or expired tokens
- Insufficient funds or margin
- Market data availability

## Development and Extensibility

### Code Structure

The E*TRADE integration follows the existing project patterns:

```
etrade_python_client/
├── services/
│   ├── etrade_auth.py
│   ├── etrade_account_service.py
│   └── etrade_order_service.py
├── web/
│   └── main.py (API endpoints)
└── services/
    └── tasks.py (Celery tasks)
```

### Extending Functionality

To add new E*TRADE features:

1. Create new methods in the appropriate service class
2. Add new API endpoints in `web/main.py`
3. Update the frontend components as needed
4. Add new Celery tasks for background processing

### Testing

The integration has been tested with:
- E*TRADE sandbox environment
- Various order types and scenarios
- Error conditions and edge cases
- Performance under normal usage patterns

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify consumer key/secret are correct
   - Ensure using sandbox for testing
   - Check E*TRADE account API access is enabled

2. **Portfolio Sync Issues**:
   - Confirm authentication is active
   - Check Redis and Celery are running
   - Review logs for API errors

3. **Order Execution Problems**:
   - Verify sufficient buying power
   - Check for market hours restrictions
   - Review order parameters for validity

### Log Locations

- Backend logs: Console output from `run_server.py`
- Celery logs: Console output from worker and beat processes
- Frontend logs: Browser developer tools console

## Future Enhancements

Planned improvements include:
1. Support for multiple E*TRADE accounts
2. Additional order types (options, mutual funds)
3. Enhanced risk management features
4. Improved error handling and retry mechanisms
5. Trade confirmation notifications
6. Advanced order types (stop-loss, trailing stop)

## API Documentation

Detailed API documentation is available at `http://localhost:8001/docs` when the backend is running. This interactive documentation allows you to:
- View all available endpoints
- See request/response schemas
- Test API calls directly
- Download API specification