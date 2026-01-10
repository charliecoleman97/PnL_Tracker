from fetch_ig_trades import IgTradesFetcher

import os
import argparse
import sys
from datetime import datetime


def validate_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = ['IG_USERNAME', 'IG_PASSWORD', 'IG_API_KEY',
                     'TRADES_FILE_PATH']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these as system environment variables.")
        print("Example:")
        print("  export IG_USERNAME='your_username'")
        print("  export IG_PASSWORD='your_password'")
        print("  export IG_API_KEY='your_api_key'")
        print("  export TRADES_FILE_PATH='transaction_history_files/"
              "ig_transactions_formatted.csv'")
        print("\nOr create a .env file (not recommended for production).")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and process IG trades'
    )
    parser.add_argument(
        '--from-date',
        type=str,
        help='Start date in YYYY-MM-DD format (default: yesterday)'
    )
    parser.add_argument(
        '--to-date',
        type=str,
        help='End date in YYYY-MM-DD format (default: today)'
    )
    args = parser.parse_args()

    # Parse dates if provided
    from_date = None
    to_date = None
    if args.from_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d')
    if args.to_date:
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d')

    # Validate environment variables before proceeding
    validate_env_vars()

    ig_trades_fetcher = IgTradesFetcher(
        username=os.getenv('IG_USERNAME'),
        password=os.getenv('IG_PASSWORD'),
        api_key=os.getenv('IG_API_KEY'),
        trades_file_path=os.getenv('TRADES_FILE_PATH')
    )
    # Connect to IG API
    ig_trades_fetcher.connect()

    # Get transactions from IG API
    transactions_df = ig_trades_fetcher.get_transactions(
        from_date=from_date,
        to_date=to_date
    )
    print("Transactions saved to DF...")

    if transactions_df.empty:
        print("No transactions found. Exiting...")
        return

    # Clean transactions dataframe
    clean_df = ig_trades_fetcher.clean_df(transactions_df)
    print("Transactions cleaned...")
    # Format transactions dataframe for MyPnL
    my_pnl_df = ig_trades_fetcher.format_df_for_mypnl(clean_df)
    print("Transactions formatted for MyPnL...")
    # Check for new trades
    new_trades_df = ig_trades_fetcher.check_for_new_trades(my_pnl_df)
    print("New trades checked...")
    # Save new trades to file
    ig_trades_fetcher.save_new_trades(new_trades_df)
    print("New trades saved to file...")
    print("Done!")


if __name__ == "__main__":
    main()
