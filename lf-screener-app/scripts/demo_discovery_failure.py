#!/usr/bin/env python3
"""Demo script: force a discovery failure and write the failure report."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import load_config
from core.engine import Engine
from reporting.txt_reporter import GroupedTXTReporter


def main():
    cfg = load_config("config.yaml")
    # Use a market string that will not be discovered to simulate failure
    market = "NO_SUCH_MARKET"
    engine = Engine(cfg)
    reporter = GroupedTXTReporter(cfg.get("output_file"))
    try:
        engine.run(market)
    except RuntimeError as e:
        out = reporter.report_failure(market, str(e))
        print(f"Wrote discovery failure report to: {out}")


if __name__ == '__main__':
    main()
