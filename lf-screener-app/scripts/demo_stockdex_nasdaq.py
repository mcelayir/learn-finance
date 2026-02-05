"""
Demo: Fetch NASDAQ fundamentals using stockdex
"""
from stockdex import Ticker
import pandas as pd

# Example NASDAQ ticker
TICKER = "AAPL"

# Fetch income statement (quarterly)
ticker = Ticker(ticker=TICKER)
income_df = ticker.yahoo_api_income_statement(frequency="quarterly")
print("Income Statement (quarterly):")
print(income_df.head())

# Fetch balance sheet (quarterly)
balance_df = ticker.yahoo_api_balance_sheet(frequency="quarterly")
print("Balance Sheet (quarterly):")
print(balance_df.head())

# Fetch cash flow (quarterly)
cashflow_df = ticker.yahoo_api_cash_flow(frequency="quarterly")
print("Cash Flow (quarterly):")
print(cashflow_df.head())

# Fetch financials (quarterly)
financials_df = ticker.yahoo_api_financials(frequency="quarterly")
print("Financials (quarterly):")
print(financials_df.head())
