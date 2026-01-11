from datetime import datetime, timedelta
import pandas as pd
import requests
import numpy as np
import os
import warnings


class IgTradesFetcher:
    def __init__(
            self,
            username,
            password,
            api_key,
            trades_file_path,
            base_url="https://api.ig.com/gateway/deal"
    ):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.trades_file_path = trades_file_path
        self.base_url = base_url
        self.account_response = None

    def connect(self) -> requests.Response:
        """
        Connect to IG API and get account response
        """

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=UTF-8',
            'X-IG-API-KEY': self.api_key,
            'Version': '2'
        }
        payload = {
            'identifier': self.username,
            'password': self.password
        }
        response = requests.post(
            f"{self.base_url}/session", headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"Unable to get response! status code: {response.status_code}")
        else:
            self.account_response = response
        return response

    def get_transactions(self, from_date=None, to_date=None) -> pd.DataFrame:
        """
        Get transactions from IG API
        """
        if to_date is None:
            to_date = datetime.now()

        if from_date is None:
            from_date = to_date - timedelta(days=1)

        if not self.account_response:
            raise Exception("Not connected. Call connect() first.")

        cst_token = self.account_response.headers.get('CST')
        security_token = self.account_response.headers.get('X-SECURITY-TOKEN')
        session_headers_v2 = {
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=UTF-8',
            'X-IG-API-KEY': self.api_key,
            'CST': cst_token,
            'X-SECURITY-TOKEN': security_token,
            'Version': '2'
        }
        transactions_url = f"{self.base_url}/history/transactions"
        all_transactions = []
        params = {
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'pageSize': 100
        }
        history_response = requests.get(
            transactions_url, headers=session_headers_v2, params=params)
        data = history_response.json()
        all_transactions.extend(data['transactions'])

        metadata = data.get('metadata', {})
        total_pages = metadata.get('pageData', {}).get('totalPages', 1)

        # Get remaining pages if present
        for page in range(2, total_pages + 1):
            params['pageNumber'] = page
            history_response = requests.get(
                transactions_url,
                headers=session_headers_v2, params=params)
            data = history_response.json()
            all_transactions.extend(data.get('transactions', []))

        df = pd.DataFrame(all_transactions)
        if df.empty:
            return pd.DataFrame()
        else:
            df = df[df['transactionType'] == 'DEAL']
            return df

    def clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean dataframe columns
        """
        # Symbol name mapping dictionary
        symbol_mapping = {
            'US Tech 100': 'NASDAQ',
            'SPOT GOLD': 'XAUUSD',
        }

        # First, convert data types
        df['dateUtc'] = pd.to_datetime(df['dateUtc'])
        df['openDateUtc'] = pd.to_datetime(df['openDateUtc'])
        df['size'] = pd.to_numeric(df['size'], errors='coerce')
        df['openLevel'] = pd.to_numeric(df['openLevel'], errors='coerce')
        df['closeLevel'] = pd.to_numeric(df['closeLevel'], errors='coerce')

        # Clean profitAndLoss (remove £ and convert to float)
        df['profitAndLoss'] = (
            df['profitAndLoss'].str.replace('£', '').astype(float)
        )

        # Rename symbols based on mapping dictionary
        if 'instrumentName' in df.columns:
            def map_symbol(name):
                if pd.isna(name):
                    return name
                name_str = str(name)
                name_upper = name_str.upper()
                # Check for exact matches first
                if name_str in symbol_mapping:
                    return symbol_mapping[name_str]
                # Check for case-insensitive exact matches
                for key, value in symbol_mapping.items():
                    if name_upper == key.upper():
                        return value
                # Check if key appears at the start of the name
                # (e.g., "Spot Gold" matches "Spot Gold - Cash")
                for key, value in symbol_mapping.items():
                    if name_upper.startswith(key.upper()):
                        return value
                return name

            df['instrumentName'] = df['instrumentName'].apply(map_symbol)

        # Sort by dateUtc to get latest records first
        df = df.sort_values('dateUtc', ascending=False).reset_index(drop=True)
        return df

    # Group by openDateUtc and instrumentName, then combine
    @staticmethod
    def combine_trades(group):
        """
        Group and combine trade data for each openDateUtc and instrumentName.
        Returns a pd.Series summarizing the group.
        """
        # Sum profitAndLoss and size
        total_pnl = group['profitAndLoss'].sum()
        total_size = group['size'].sum()

        # Get the latest record (first one after sorting)
        latest = group.iloc[0]

        # Combine references if multiple
        references = '; '.join(group['reference'].unique())

        return pd.Series({
            'instrumentName': latest['instrumentName'],
            'openDateUtc': latest['openDateUtc'],
            'dateUtc': latest['dateUtc'],  # Latest close date
            'openLevel': latest['openLevel'],
            'closeLevel': latest['closeLevel'],  # Latest close level
            'size': total_size,
            'profitAndLoss': total_pnl,
            'reference': references,
            'transactionType': latest['transactionType'],
            'currency': latest['currency']
        })

    @staticmethod
    def format_for_mypnl(row):
        """
        Format trade data for MyPnL
        """
        # Determine trade type from size sign
        trade_type = 'sell' if row['size'] < 0 else 'buy'

        # Format dates to YYYY.MM.DD HH:MM:SS
        closed_at = row['dateUtc'].strftime('%Y.%m.%d %H:%M:%S')
        opened_at = row['openDateUtc'].strftime('%Y.%m.%d %H:%M:%S')

        # Get symbol (uppercase, replace spaces)
        symbol = row['instrumentName'].upper()

        return pd.Series({
            'symbol': symbol,
            'trade_type': trade_type,
            'entry_price': row['openLevel'],
            'exit_price': row['closeLevel'],
            'lot_size': abs(row['size']),  # Absolute value
            'pnl': row['profitAndLoss'],
            'closed_at': closed_at,
            'opened_at': opened_at,
            'strategy': np.nan,
            'notes': row['reference'],
            'stop_loss': np.nan,
            'target_price': np.nan,
            'commission': np.nan
        })

    def format_df_for_mypnl(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format dataframe for MyPnL
        """
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=FutureWarning)
            df_combined = df.groupby(
                ['openDateUtc', 'instrumentName'], as_index=False).apply(
                    self.combine_trades).reset_index(drop=True)
        df_formatted = df_combined.apply(self.format_for_mypnl, axis=1)
        return df_formatted

    def check_for_new_trades(self, df_formatted: pd.DataFrame) -> pd.DataFrame:
        """
        Check for new trades
        """
        if not os.path.exists(self.trades_file_path):
            existing_df = pd.DataFrame()
        else:
            existing_df = pd.read_csv(self.trades_file_path)

        if existing_df.empty:
            df_new = df_formatted
            print(
                "No existing trades file or file is empty. "
                "All records are considered new."
            )
            return df_new

        # Use the columns that are shared between both
        # dataframes for comparison
        common_columns = list(existing_df.columns)
        df_formatted_aligned = df_formatted[common_columns]

        new_records = df_formatted_aligned.merge(
            existing_df,
            on=common_columns,
            how='left',
            indicator=True
        )

        df_new = new_records[new_records['_merge'] == 'left_only'].drop(
            columns=['_merge'])
        print(f"New records: {len(df_new)}")

        return df_new

    def save_new_trades(self, df_new: pd.DataFrame) -> None:
        """
        Save new trades to file
        """
        # Save new trades to file
        if len(df_new) > 0:
            print("\nNew records:")
            print(df_new)
            df_new.to_csv(self.trades_file_path, index=False)
        else:
            print("\nNo new records - all records already"
                  "exist in the existing trades file")
