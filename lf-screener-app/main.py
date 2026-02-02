from core.config import load_config
from core.engine import Engine
from reporting.txt_reporter import GroupedTXTReporter


def main():
    cfg = load_config("config.yaml")
    engine = Engine(cfg)
    try:
        results = engine.run(cfg.get("market"))
    except RuntimeError as e:
        # Abort early when no tickers discovered to avoid empty reports
        print(str(e))
        return

    reporter = GroupedTXTReporter(cfg.get("output_file"))
    out = reporter.report(results)
    print(f"Report written to: {out}")

if __name__ == "__main__":
    main()
