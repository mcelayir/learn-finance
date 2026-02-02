#!/usr/bin/env python3
"""Simple script to run discovery diagnostics for an index and print the results."""
import sys
import os
# Ensure project root is on sys.path for local module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_provider import DataProvider
from core.config import load_config


def main():
    cfg = load_config("config.yaml")
    dp = DataProvider(cfg)
    idx = sys.argv[1] if len(sys.argv) > 1 else cfg.get("market", "BIST")
    report = dp.debug_discovery(idx)
    print(f"Discovery report for {idx}:\n")
    for k, v in report.items():
        print(f"- {k}: count={v.get('count')}")
        if "sample" in v and v.get("sample"):
            print("  sample:", v.get("sample")[:10])
        if "error" in v:
            print("  error:", v.get("error"))
        if "trace" in v:
            print("  trace:\n", v.get("trace"))

if __name__ == '__main__':
    main()
