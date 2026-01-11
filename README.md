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

   **For development: `.env` file in `dev/` folder:**

   The development script (`dev/fetch_trades_dev.py`) uses a `.env` file for convenience during development. To set this up:

   1. Copy the example file:
      ```bash
      cp dev/.env_example dev/.env
      ```

   2. Edit `dev/.env` and add your actual credentials:
      ```
      IG_USERNAME=your_actual_username
      IG_PASSWORD=your_actual_password
      IG_API_KEY=your_actual_api_key
      TRADES_FILE_PATH=transaction_history_files/ig_transactions_formatted.csv
      ```

   The `.env` file is automatically ignored by git (see `.gitignore`). The main `driver.py` script still uses system environment variables only.

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
├── dev/
│   ├── fetch_trades_dev.py  # Development script (uses .env file)
│   └── .env_example         # Example .env file template
└── transaction_history_files/
    └── ig_transactions_formatted.csv  # Output file
```

## Security Notes

- **Production (`driver.py`)**: Uses system environment variables only - the recommended and most secure approach
- **Development (`dev/fetch_trades_dev.py`)**: Uses a `.env` file in the `dev/` folder for convenience
- The `.env` file is automatically excluded from git via `.gitignore`
- Never commit credentials in any form
- System environment variables take precedence over `.env` file values if both are set

## Dependencies

- `trading-ig>=0.0.10` - IG API client
- `pandas>=1.5.0` - Data manipulation
- `python-dotenv>=0.19.0` - Optional: For `.env` file support (only used if `.env` exists)
