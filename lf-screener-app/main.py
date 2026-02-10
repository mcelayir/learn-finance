from core.config import load_config
from core.engine import Engine
from reporting.txt_reporter import GroupedTXTReporter
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Run MCSA Screener")
    parser.add_argument("--market", type=str, help="Market/index to screen (e.g. BIST, NASDAQ)")
    args = parser.parse_args()

    # Always load config.yaml relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.yaml")
    cfg = load_config(config_path)
    market = args.market or cfg.get("market", "BIST")

    # Set output file to include market name
    output_dir = os.path.dirname(cfg.get("output_file", "reports/screener_output.txt"))
    if not output_dir:
        output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"screener-output-{market.upper()}.txt")

    engine = Engine(cfg)
    reporter = GroupedTXTReporter(output_file)
    try:
        results = engine.run(market)
    except RuntimeError as e:
        msg = str(e)
        print(msg)
        out = reporter.report_failure(market, msg)
        print(f"Discovery failure report written to: {out}")
        return

    out = reporter.report(results)
    print(f"Report written to: {out}")

    # Write fundamentals for each stock to stock_fundamentals_MARKET.txt
    fundamentals_file = os.path.join(output_dir, f"stock_fundamentals_{market.upper()}.txt")
    with open(fundamentals_file, "w") as f:
        f.write(f"Stock Fundamentals Report - {market.upper()} - {os.path.basename(output_file)}\n")
        f.write("Ticker | Fundamentals\n")
        f.write("-"*80 + "\n")
        # Sort results by ticker alphabetically
        sorted_results = sorted(results, key=lambda x: x.get("ticker", ""))
        for r in sorted_results:
            ticker = r.get("ticker", "")
            raw = r.get("raw", {})
            # Only show fundamental fields, now including standard_pb_ratio
            fund_keys = ["pe_ratio", "pb_ratio", "standard_pb_ratio", "debt_equity", "roe", "net_margin", "rev_growth_qoq", "earnings_growth_qoq"]
            fundamentals = {k: raw.get(k) for k in fund_keys if k in raw}
            f.write(f"{ticker}: {fundamentals}\n")
    print(f"Fundamentals written to: {fundamentals_file}")

if __name__ == "__main__":
    main()
