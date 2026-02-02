# Quick test for FMP fundamentals fetcher
from dotenv import load_dotenv
load_dotenv()
from core.fmp_fundamentals import fetch_fmp_fundamentals

# Example BIST tickers (as used in screener_output.txt)
tickers = [
    "BIST:THYAO", "BIST:HALKB", "BIST:KTLEV", "BIST:KLRHO", "BIST:PEKGY", "BIST:TERA"
]

for t in tickers:
    print(f"Testing FMP fetch for {t}...")
    data = fetch_fmp_fundamentals(t)
    print(f"Result for {t}: {data}\n")
