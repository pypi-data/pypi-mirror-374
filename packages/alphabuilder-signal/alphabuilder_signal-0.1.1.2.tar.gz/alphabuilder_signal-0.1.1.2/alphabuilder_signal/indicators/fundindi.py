import numpy as np
import pandas as pd

class FundamentalIndicators:
    def __init__(self, df):
        self.df = df.copy()
        
    # VALUATION
    def price_to_earning_ratio(self):
        self.df["pe_ratio"] = self.df["Close"] / self.df["earnings"]
        return self
    
    def ev_to_ebitda(self):
        self.df["ev_ebitda"] = self.df["enterprise_value"] / self.df["ebitda"]
        return self
    
    def price_to_book(self):
        self.df["pb_ratio"] = self.df["Close"] / self.df["book_value"]
        return self
    
    def price_to_sales(self):
        self.df["ps_ratio"] = self.df["Close"] / self.df["sales"]
        return self
    
    # PROFITABILITY
    def return_on_equity(self):
        self.df["roe"] = self.df["net_income"] / self.df["equity"]
        return self
    
    def return_on_assets(self):
        self.df["roa"] = self.df["net_income"] / self.df["assets"]
        return self
    
    def gross_margin(self):
        self.df["gross_margin"] = self.df["gross_profit"] / self.df["sales"]
        return self
    
    def operating_margin(self):
        self.df["operating_margin"] = self.df["operating_income"] / self.df["sales"]
        return self
    
    # GROWTH
    def eps_growth(self):
        self.df["eps_growth"] = self.df["eps"].pct_change(periods=4) 
        return self
    
    def sales_growth(self):
        self.df["sales_growth"] = self.df["sales"].pct_change(periods=4)
        return self
    
    # LEVERAGE
    def debt_to_equity(self):
        self.df["de_ratio"] = self.df["debt"] / self.df["equity"]
        return self
    
    def interest_coverage(self):
        self.df["interest_coverage"] = self.df["ebit"] / self.df["interest_expense"]
        return self
    
    # CASH FLOW
    def free_cash_flow_yield(self):
        self.df["fcf_yield"] = self.df["free_cash_flow"] / self.df["market_cap"]
        return self
    
    def operating_cash_flow_ratio(self):
        self.df["ocf_ratio"] = self.df["operating_cash_flow"] / self.df["current_liabilities"]
        return self
    
    # QUALITY
    def accruals_ratio(self):
        self.df["accruals_ratio"] = (self.df["net_income"] - self.df["operating_cash_flow"]) / self.df["assets"]
        return self
    
    def earnings_persistence(self):
        self.df["earnings_persistence"] = self.df["eps"].shift(1) / self.df["eps"]
        return self
    
    def get_df(self):
        return self.df