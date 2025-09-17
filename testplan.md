# EtradePythonClient AI Trading Assistant - End-to-End Test Plan

This document provides a comprehensive step-by-step test plan for performing complete end-to-end testing of the EtradePythonClient AI Trading Assistant application, covering all components from installation to UI functionality.

## Prerequisites

Before beginning the testing process, ensure you have the following:

1. Python 3.8 or higher installed
2. Node.js 14 or higher with npm installed
3. Redis Server installed and accessible
4. An E*TRADE account (sandbox for testing)
5. Google Gemini API key
6. Optional: SMTP server credentials for email notifications
7. Optional: Slack bot token for Slack notifications
8. Git installed (if cloning from repository)

## Test Plan Overview

The test plan is divided into the following phases:
1. Installation and Setup
2. Configuration
3. Service Startup and Verification
4. UI Component Testing
5. Integration Testing
6. Functional Testing
7. Notification Testing
8. Background Task Testing
9. E*TRADE Integration Testing
10. AI Functionality Testing
11. Edge Case and Error Handling Testing

## 1. Installation and Setup

### 1.1 Clone Repository (if applicable)
```bash
git clone <repository-url>
cd EtradePythonClient
```

### 1.2 Backend Setup
1. Create and activate a Python virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### 1.3 Frontend Setup
1. Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### 1.4 Verify Installation
1. Check that all required packages are installed by running:
   ```bash
   pip list
   ```
2. In the frontend directory, verify node_modules were created:
   ```bash
   ls node_modules
   ```

## 2. Configuration

### 2.1 Create Configuration File
1. Copy the template configuration file:
   ```bash
   cp etrade_python_client/config.ini.template etrade_python_client/config.ini
   ```

2. Edit the config.ini file to add your credentials:
   ```bash
   nano etrade_python_client/config.ini
   ```

3. Update the following required fields:
   - `[DEFAULT]` section:
     - `CONSUMER_KEY = your_etrade_consumer_key`
     - `CONSUMER_SECRET = your_etrade_consumer_secret`
   - `[AI_SERVICES]` section:
     - `GEMINI_API_KEY = your_gemini_api_key`
   - Optional fields for notifications:
     - `[NOTIFICATIONS]` section:
       - `smtp_username = your_email@gmail.com`
       - `smtp_password = your_app_password`
       - `slack_bot_token = your_slack_bot_token`

### 2.2 Verify Configuration
1. Run a simple test to verify configuration can be loaded:
   ```bash
   python -c "from etrade_python_client.utils.config_manager import ConfigManager; cm = ConfigManager(); print('Config loaded successfully')"
   ```

## 3. Service Startup and Verification

### 3.1 Start Redis Server
1. Start Redis server in a new terminal:
   ```bash
   redis-server redis.conf
   ```
2. Verify Redis is running by checking for a message like "Ready to accept connections"

### 3.2 Start Celery Worker
1. In a new terminal, navigate to the project root directory
2. Ensure the virtual environment is activated
3. Start the Celery worker:
   ```bash
   celery -A etrade_python_client.services.celery_app worker --loglevel=info
   ```
4. Verify the worker starts successfully with no errors

### 3.3 Start Celery Beat Scheduler
1. In a new terminal, navigate to the project root directory
2. Ensure the virtual environment is activated
3. Start the Celery beat scheduler:
   ```bash
   celery -A etrade_python_client.services.celery_app beat --loglevel=info
   ```
4. Verify the scheduler starts successfully with no errors

### 3.4 Start the FastAPI Backend
1. In a new terminal, navigate to the project root directory
2. Ensure the virtual environment is activated
3. Start the FastAPI backend:
   ```bash
   python run_server.py
   ```
4. Verify the server starts successfully:
   - Check for message like "Uvicorn running on http://127.0.0.1:8001"
   - Verify no error messages in the console

### 3.5 Start the React Frontend
1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start the React development server:
   ```bash
   npm start
   ```
3. Verify the frontend starts successfully:
   - Check for message like "Local: http://localhost:3000"
   - Verify the browser automatically opens or you can manually navigate to http://localhost:3000

### 3.6 Verify All Services Are Running
1. Confirm all services are running in separate terminals:
   - Redis server (typically on port 6379)
   - Celery worker (no specific port)
   - Celery beat (no specific port)
   - FastAPI backend (port 8001)
   - React frontend (port 3000)
2. Check that no services are reporting errors in their consoles

## 4. UI Component Testing

### 4.1 Dashboard Component
1. Navigate to http://localhost:3000
2. Verify the dashboard loads without errors
3. Check that all widgets are displayed:
   - Market Overview Widget
   - Portfolio Widget
   - Watchlist Widget
   - AI Decisions Widget
   - E*TRADE Account Widget
   - E*TRADE Trading Widget

### 4.2 Market Overview Widget
1. Locate the Market Overview Widget on the dashboard
2. Verify that market indices are displayed (e.g., S&P 500, Dow Jones, NASDAQ)
3. Check that the data is updating (if real-time functionality is working)
4. Verify the visual representation (charts, if applicable)

### 4.3 Portfolio Widget
1. Locate the Portfolio Widget on the dashboard
2. Initially, it may show "No portfolio data" if not connected to E*TRADE
3. After E*TRADE connection (see section 9), verify:
   - Account balances are displayed
   - Portfolio positions are shown
   - Performance charts are rendered

### 4.4 Watchlist Widget
1. Locate the Watchlist Widget on the dashboard
2. Verify that default watchlist symbols are displayed (if configured)
3. Check that price information is shown for each symbol
4. Verify that the watchlist can be updated (add/remove symbols)

### 4.5 AI Decisions Widget
1. Locate the AI Decisions Widget on the dashboard
2. Initially, it may be empty or show sample data
3. After AI processing (see section 10), verify:
   - AI trading decisions are displayed
   - Each decision shows symbol, type (buy/sell), confidence score, and rationale
   - Decision feedback options are available

### 4.6 E*TRADE Account Widget
1. Locate the E*TRADE Account Widget on the dashboard
2. Verify the "Connect E*TRADE" button is visible
3. Check that account information displays after successful connection

### 4.7 E*TRADE Trading Widget
1. Locate the E*TRADE Trading Widget on the dashboard
2. Verify that trading controls are visible (account selection, symbol input, order type, quantity)
3. Check that the order preview functionality works

## 5. Integration Testing

### 5.1 Backend API Testing
1. Navigate to http://localhost:8001/docs to access the API documentation
2. Verify that all API endpoints are accessible:
   - Market Data endpoints
   - Portfolio endpoints
   - AI Decisions endpoints
   - User Preferences endpoints
   - Market Sentiment endpoints
   - Notifications endpoints
   - E*TRADE endpoints
3. Test a few key endpoints manually through the documentation interface:
   - GET /api/market/overview
   - GET /api/portfolio/latest
   - GET /api/decisions

### 5.2 Database Integration
1. Run the existing database test:
   ```bash
   python test_database.py
   ```
2. Verify that all database operations succeed:
   - Database initialization
   - User preferences creation
   - AI decision creation
   - Portfolio analytics creation
   - Data querying

### 5.3 WebSocket Integration
1. Open browser developer tools (F12)
2. Go to the Network tab
3. Connect to E*TRADE (see section 9)
4. Verify WebSocket connections are established
5. Check that real-time updates are received in the console

## 6. Functional Testing

### 6.1 User Preferences Management
1. Navigate to the user settings area (if available) or use the UI feedback components
2. Update user preferences:
   - Risk tolerance
   - Maximum trade amount
   - Notification preferences
   - Watchlist symbols
3. Verify that preferences are saved and persist after page refresh

### 6.2 AI Decision Feedback
1. Locate an AI decision in the AI Decisions Widget
2. Provide feedback on the decision (positive, negative, neutral)
3. Add optional notes to the feedback
4. Verify that feedback is recorded (check database or backend logs)

### 6.3 Watchlist Management
1. Add new symbols to the watchlist
2. Remove symbols from the watchlist
3. Verify that changes are saved and persist after page refresh
4. Check that market data is displayed for all watchlist symbols

## 7. Notification Testing

### 7.1 Email Notifications (if configured)
1. Configure SMTP settings in config.ini (if not already done)
2. Trigger a notification event (e.g., by creating an AI decision with high confidence)
3. Check your email inbox for the notification
4. Verify that the email contains the expected information and formatting

### 7.2 Slack Notifications (if configured)
1. Configure Slack bot token in config.ini (if not already done)
2. Trigger a notification event
3. Check your Slack channel for the notification
4. Verify that the message contains the expected information

## 8. Background Task Testing

### 8.1 Celery Task Execution
1. Monitor the Celery worker terminal
2. Verify that periodic tasks are executing:
   - Database backups
   - AI learning optimization
   - Market monitoring
   - Data cleanup
3. Check that no errors are reported in the Celery logs

### 8.2 Database Backup
1. Wait for the scheduled backup time (midnight PST) or manually trigger a backup task
2. Verify that backup files are created in the configured backup location
3. Check that the backup retention policy is working (5-backup limit)

## 9. E*TRADE Integration Testing

### 9.1 OAuth Authentication
1. Click the "Connect E*TRADE" button in the E*TRADE Account Widget
2. Verify that you are redirected to the E*TRADE login page
3. Log in with your E*TRADE sandbox credentials
4. Complete the OAuth authorization process
5. Verify that you receive a verification code

### 9.2 Verification Code Entry
1. Enter the verification code in the dialog that appears
2. Submit the code
3. Verify that authentication is successful

### 9.3 Account Information Retrieval
1. After successful authentication, verify that:
   - Account list is displayed
   - Account balances are shown
   - Buying power is displayed
   - Account type information is available

### 9.4 Portfolio Data Retrieval
1. Verify that portfolio positions are retrieved and displayed
2. Check that position details are correct:
   - Symbol
   - Quantity
   - Current price
   - Market value
   - Gain/loss information

### 9.5 Order Preview
1. Select an account in the E*TRADE Trading Widget
2. Enter a symbol (e.g., AAPL)
3. Select order type (market or limit)
4. Enter quantity
5. Click "Preview Order"
6. Verify that order preview information is displayed:
   - Order details
   - Estimated cost
   - Account information

### 9.6 Order Placement (Sandbox Only)
1. In the E*TRADE Trading Widget, preview an order (as above)
2. Click "Place Order" (only in sandbox environment)
3. Verify that order confirmation is received
4. Check that the order appears in order history

## 10. AI Functionality Testing

### 10.1 Market Data Integration
1. Verify that Yahoo Finance integration is working:
   - Real-time quotes are displayed
   - Historical data is accessible
   - Technical indicators are calculated
   - News sentiment is analyzed

### 10.2 AI Decision Generation
1. Monitor the AI Decisions Widget
2. Verify that AI decisions are generated periodically
3. Check that decisions include:
   - Symbol
   - Decision type (buy/sell)
   - Confidence score
   - Rationale
   - Price target

### 10.3 AI Chat Interface
1. Locate the AI chat interface (if available)
2. Enter a natural language query about trading
3. Verify that the AI responds appropriately
4. Check that responses are streamed in real-time
5. Verify that portfolio context is considered in responses

### 10.4 AI Learning System
1. Provide feedback on AI decisions
2. Verify that feedback is recorded
3. Check that the AI system uses feedback for learning (may require monitoring backend logs or database)

## 11. Edge Case and Error Handling Testing

### 11.1 Network Disconnection
1. Disconnect from the internet while services are running
2. Verify that appropriate error messages are displayed in the UI
3. Reconnect to the internet
4. Verify that services reconnect automatically

### 11.2 E*TRADE API Errors
1. Temporarily invalidate your E*TRADE credentials
2. Attempt to connect to E*TRADE
3. Verify that appropriate error messages are displayed
4. Restore valid credentials and retry connection

### 11.3 Database Errors
1. Stop the database service (if possible) or simulate database connection issues
2. Verify that appropriate error handling occurs
3. Restore database connectivity
4. Verify that services recover gracefully

### 11.4 Redis Connection Errors
1. Stop the Redis server
2. Verify that background tasks handle the error appropriately
3. Restart Redis server
4. Verify that services reconnect automatically

### 11.5 Frontend Error Handling
1. Test invalid inputs in forms (e.g., negative quantities, invalid symbols)
2. Verify that appropriate validation messages are displayed
3. Test edge cases (e.g., very large numbers, special characters)

## 12. Performance Testing

### 12.1 Page Load Times
1. Measure initial page load time
2. Measure dashboard widget loading times
3. Verify that UI remains responsive during data loading

### 12.2 API Response Times
1. Test API endpoint response times through the documentation interface
2. Verify that responses are within acceptable time limits
3. Test with multiple concurrent requests if possible

### 12.3 Real-time Updates
1. Monitor WebSocket update frequency
2. Verify that real-time data updates are timely
3. Check that UI updates smoothly without flickering

## 13. Security Testing

### 13.1 Authentication Security
1. Verify that E*TRADE OAuth flow is secure
2. Check that tokens are properly managed and refreshed
3. Verify that credentials are not exposed in logs or UI

### 13.2 Data Protection
1. Verify that sensitive data is not exposed in API responses
2. Check that database connections use appropriate security measures
3. Verify that configuration files are not exposed publicly

## 14. Cleanup and Teardown

### 14.1 Service Shutdown
1. Shut down services in the following order:
   - React frontend (Ctrl+C in frontend terminal)
   - FastAPI backend (Ctrl+C in backend terminal)
   - Celery beat (Ctrl+C in beat terminal)
   - Celery worker (Ctrl+C in worker terminal)
   - Redis server (Ctrl+C in Redis terminal)

### 14.2 Environment Cleanup
1. Deactivate Python virtual environment:
   ```bash
   deactivate
   ```
2. Clean up any temporary files or test data if needed

## Test Completion Criteria

The end-to-end testing is considered complete when all of the following criteria are met:

1. All installation steps execute successfully
2. Configuration is properly set up and validated
3. All services start without errors
4. All UI components load and function correctly
5. Integration between all components works as expected
6. All functional features work as described
7. Notification systems function properly (if configured)
8. Background tasks execute without errors
9. E*TRADE integration works for all supported operations
10. AI functionality generates decisions and responds to queries
11. Error handling works appropriately for all tested edge cases
12. Performance is within acceptable limits
13. Security measures are properly implemented
14. All services can be shut down cleanly

## Test Artifacts

Document and save the following artifacts during testing:

1. Screenshots of successful UI components
2. Log files from all services
3. Test results summary
4. Any issues encountered and their resolutions
5. Performance metrics
6. Security observations

## Test Environment

- OS: [Specify your OS]
- Python Version: [Specify version]
- Node.js Version: [Specify version]
- Redis Version: [Specify version]
- Browser: [Specify browser and version]
- E*TRADE Sandbox Account: [Account details if relevant]