import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path so we can import fetch_ig_trades
# Get the absolute path of the parent directory (project root)
if '__file__' in globals():
    project_root = Path(__file__).parent.parent
else:
    project_root = Path('..').resolve()
sys.path.insert(0, str(project_root))

# Load environment variables from .env file if it exists (dev only)
try:
    from dotenv import load_dotenv  # noqa: E402
    # Load .env from dev directory
    if '__file__' in globals():
        dev_dir = Path(__file__).parent
    else:
        dev_dir = Path('.')
    env_path = dev_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"No .env file found at {env_path}")
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

from fetch_ig_trades import IgTradesFetcher  # noqa: E402


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

username = os.getenv('IG_USERNAME')
password = os.getenv('IG_PASSWORD')
api_key = os.getenv('IG_API_KEY')
trades_file_path = os.getenv('TRADES_FILE_PATH')

# Fetch trades from IG
ig_trades_fetcher = IgTradesFetcher(
    username=username,
    password=password,
    api_key=api_key,
    trades_file_path=trades_file_path
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


