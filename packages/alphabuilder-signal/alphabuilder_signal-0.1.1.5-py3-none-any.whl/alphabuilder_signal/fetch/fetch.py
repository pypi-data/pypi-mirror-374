import pandas as pd
import numpy as np
import yfinance as yf
import time
from typing import List, Optional, Union

class Fetch:
    """
    A professional asset data fetcher for AlphaBuilder.
    
    Parameters
    ----------
    tickers : list[str], optional
        List of asset tickers to download.
    start_date : str, default '2010-01-01'
        Start date for historical data.
    end_date : str, optional
        End date for historical data. Defaults to today.
    verbose : bool, default True
        Whether to print download progress.
    """

    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        start_date: str = '2010-01-01',
        end_date: Optional[str] = None,
        verbose: bool = True
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.verbose = verbose
        self.tickers = tickers or []
        self.data: dict[str, pd.DataFrame] = {}

    def _download_asset_data(self) -> None:
        """Download data for all tickers and store in self.data."""
        if not self.tickers:
            if self.verbose:
                print("No tickers provided.")
            return

        for ticker in self.tickers:
            if self.verbose:
                print(f"Downloading {ticker}...")

            try:
                df = yf.download(ticker, start=self.start_date, end=self.end_date)
                if isinstance(df.columns, pd.MultiIndex):
                    new_columns = [] 
                    for col in df.columns:
                        if col[0] != "":
                            new_columns.append(col[0])
                        else:
                            new_columns.append(col[1])  
                    df.columns = new_columns
                time.sleep(0.2) 

                if df.empty:
                    print(f"No data found for {ticker}.")
                    continue

                self.data[ticker] = df

            except Exception as e:
                print(f"Error downloading {ticker}: {e}")

        if self.verbose:
            print("Download completed.")

    def get_asset_data(self, combined: bool = False) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        """
        Retrieve downloaded asset data.

        Parameters
        ----------
        combined : bool, default False
            If True, returns a single DataFrame with multi-index (ticker, date).
            If False, returns a dictionary with tickers as keys.

        Returns
        -------
        dict or pd.DataFrame
        """
        if not self.data:
            self._download_asset_data()

        if combined:
            combined_df = pd.concat(self.data.values(), keys=self.data.keys(), names=['Ticker', 'Date'])
            return combined_df

        return self.data

#---------Testing----------