# Debugging script to fetch and print fundamentals for NASDAQ:LITE

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'lf-screener-app/core')))
from stockdex import Ticker
import pandas as pd

def safe_float(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            val = val.strip().replace(",", "").upper()
            if val == '' or val == 'NONE':
                return None
            if val.endswith("B"):
                return float(val[:-1]) * 1_000_000_000
            elif val.endswith("M"):
                return float(val[:-1]) * 1_000_000
            elif val.endswith("K"):
                return float(val[:-1]) * 1_000
            else:
                return float(val)
        return float(val)
    except (ValueError, TypeError):
        return None

def get_latest(df, field):
    if isinstance(field, list):
        vals = [df[f].iloc[0] for f in field if f in df.columns and pd.notnull(df[f].iloc[0])]
        return sum(vals) if vals else None
    if field in df.columns:
        v = df[field].iloc[0]
        return v if pd.notnull(v) else None
    return None

if __name__ == "__main__":
    ticker = "NASDAQ:LITE"
    symbol = ticker.split(":", 1)[1] if ":" in ticker else ticker
    t = Ticker(ticker=symbol)
    fin = t.yahoo_api_financials(frequency="quarterly")
    inc = t.yahoo_api_income_statement(frequency="quarterly")
    bal = t.yahoo_api_balance_sheet(frequency="quarterly")

    print("\n[DEBUG] RAW FIELDS FOR NASDAQ:LITE:")
    print("Income Statement columns:", inc.columns.tolist())
    print("Balance Sheet columns:", bal.columns.tolist())
    print("Financials columns:", fin.columns.tolist())

    # Show last 4 quarters of EPS
    if "quarterlyBasicEPS" in inc.columns:
        print("quarterlyBasicEPS (last 4):", inc["quarterlyBasicEPS"].iloc[:4].tolist())
    # Show shares outstanding fields
    for shares_field in ["quarterlySharesOutstanding", "quarterlyOrdinarySharesNumber", "quarterlyCommonStockSharesOutstanding"]:
        if shares_field in bal.columns:
            print(f"{shares_field} (latest):", bal[shares_field].iloc[0])
    # Show tangible book value
    if "quarterlyTangibleBookValue" in bal.columns:
        print("quarterlyTangibleBookValue (latest):", bal["quarterlyTangibleBookValue"].iloc[0])

    # Calculate TTM EPS
    eps_ttm = None
    if "quarterlyBasicEPS" in inc.columns and len(inc["quarterlyBasicEPS"]) >= 4:
        eps_ttm = sum([safe_float(e) for e in inc["quarterlyBasicEPS"].iloc[:4] if safe_float(e) is not None])
    print("TTM EPS (sum last 4):", eps_ttm)

    # Price
    try:
        price_df = t.yahoo_api_price(range="1mo", dataGranularity="1d")
        price = safe_float(price_df["close"].iloc[-1])
    except Exception:
        price = None
    print("Price (close):", price)

    # Book Value Per Share
    tangible_book_total = safe_float(get_latest(bal, "quarterlyTangibleBookValue"))
    shares_out = None
    for shares_field in ["quarterlySharesOutstanding", "quarterlyOrdinarySharesNumber", "quarterlyCommonStockSharesOutstanding"]:
        shares_out = safe_float(get_latest(bal, shares_field))
        if shares_out not in (None, 0):
            break
    bvps = tangible_book_total / shares_out if tangible_book_total not in (None, 0) and shares_out not in (None, 0) else None
    print("Tangible Book Value (total):", tangible_book_total)
    print("Shares Outstanding:", shares_out)
    print("Book Value Per Share:", bvps)

    # PE Ratio
    pe_ratio = price / eps_ttm if price not in (None, 0) and eps_ttm not in (None, 0) and eps_ttm > 0 else None
    print("PE Ratio (Price / TTM EPS):", pe_ratio)

    # PB Ratio
    pb_ratio = price / bvps if price not in (None, 0) and bvps not in (None, 0) else None
    print("PB Ratio (Price / BVPS):", pb_ratio)

    # Debt/Equity
    if "quarterlyTotalDebt" in bal.columns:
        total_debt = safe_float(get_latest(bal, "quarterlyTotalDebt"))
    else:
        total_debt = safe_float(get_latest(bal, ["quarterlyLongTermDebt", "quarterlyCurrentDebt"]))
    total_equity = safe_float(get_latest(bal, "quarterlyStockholdersEquity"))
    debt_equity = total_debt / total_equity if total_debt not in (None, 0) and total_equity not in (None, 0) else None
    print("Total Debt:", total_debt)
    print("Total Equity:", total_equity)
    print("Debt/Equity:", debt_equity)

    # ROE
    net_income = safe_float(get_latest(inc, "quarterlyNetIncome"))
    roe = (net_income / total_equity) * 100 if net_income is not None and total_equity not in (None, 0) else None
    print("Net Income:", net_income)
    print("ROE (Net Income / Total Equity):", roe)

    # Net Margin
    total_revenue = safe_float(get_latest(inc, "quarterlyTotalRevenue"))
    net_margin = (net_income / total_revenue) * 100 if net_income is not None and total_revenue not in (None, 0) else None
    print("Total Revenue:", total_revenue)
    print("Net Margin (Net Income / Total Revenue):", net_margin)
