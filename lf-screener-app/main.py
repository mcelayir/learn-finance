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
        # Instead of aborting silently, write a short failure report for visibility
        msg = str(e)
        print(msg)
        out = reporter.report_failure(market, msg)
        print(f"Discovery failure report written to: {out}")
        return

    out = reporter.report(results)
    print(f"Report written to: {out}")

if __name__ == "__main__":
    main()
