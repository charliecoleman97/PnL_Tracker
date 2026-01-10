# PnL Tracker

A Python tool to fetch and track trading transactions from IG (IG.com) API and format them for MyPnL.

## Features

- Fetches trade transactions from IG API
- Cleans and formats transaction data
- Tracks new trades and saves them to CSV that is correctly formatted to work with the csv upload
   on myPnL.com
- Supports date range filtering

## Prerequisites

- Python 3.7 or higher
- IG API credentials (username, password, API key)

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd PnL_Tracker
   ```

2. **Set up the virtual environment and install dependencies:**
   ```bash
   make setup
   ```

   This will:
   - Create a virtual environment (`.venv`)
   - Install all required dependencies

3. **Set environment variables:**

   **Recommended: Use system environment variables** (more secure, no plain text files):

   ```bash
   export IG_USERNAME='your_ig_username'
   export IG_PASSWORD='your_ig_password'
   export IG_API_KEY='your_ig_api_key'
   export TRADES_FILE_PATH='transaction_history_files/ig_transactions_formatted.csv'
   ```

   To make these persistent, add them to your shell profile (e.g., `~/.zshrc` or `~/.bashrc`):
   ```bash
   echo 'export IG_USERNAME="your_ig_username"' >> ~/.zshrc
   echo 'export IG_PASSWORD="your_ig_password"' >> ~/.zshrc
   echo 'export IG_API_KEY="your_ig_api_key"' >> ~/.zshrc
   echo 'export TRADES_FILE_PATH="transaction_history_files/ig_transactions_formatted.csv"' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Optional: `.env` file** (for local development convenience only):

   If you prefer using a `.env` file for local development, you can create one. However, this is **not recommended** as it stores credentials in plain text. The code will automatically detect and use a `.env` file if it exists, but system environment variables take precedence.

   **Important:** Never commit your `.env` file - it's gitignored for safety, but using system environment variables is more secure.

## Usage

### Run with default settings (last 1 day):
```bash
make run
```

or

```bash
make fetch-trades
```

### Run with custom date range:
```bash
make run FROM_DATE=2026-01-01 TO_DATE=2026-01-31
```

### Run with only start date (end date defaults to today):
```bash
make fetch-trades FROM_DATE=2026-01-01
```

## Makefile Commands

- `make setup` - Set up virtual environment and install dependencies
- `make install` - Install/update dependencies
- `make run` - Run the driver script
- `make fetch-trades` - Alias for `make run`
- `make clean` - Remove virtual environment
- `make help` - Show all available commands

## Project Structure

```
PnL_Tracker/
├── driver.py                 # Main entry point
├── fetch_ig_trades.py        # IG API client and data processing
├── requirements.txt          # Python dependencies
├── Makefile                  # Automation commands
├── .gitignore               # Git ignore rules
└── transaction_history_files/
    └── ig_transactions_formatted.csv  # Output file
```

## Security Notes

- **Use system environment variables** - This is the recommended and most secure approach
- Credentials are never stored in plain text files
- System environment variables are loaded from your shell environment, not from files
- The `.env` file is optional and only for local development convenience
- If you use a `.env` file, it's automatically excluded from git via `.gitignore`
- Never commit credentials in any form

## Dependencies

- `trading-ig>=0.0.10` - IG API client
- `pandas>=1.5.0` - Data manipulation
- `python-dotenv>=0.19.0` - Optional: For `.env` file support (only used if `.env` exists)
