from core.config import load_config
from core.engine import Engine
from reporting.txt_reporter import GroupedTXTReporter


def main():
    cfg = load_config("config.yaml")
    engine = Engine(cfg)
    reporter = GroupedTXTReporter(cfg.get("output_file"))
    try:
        results = engine.run(cfg.get("market"))
    except RuntimeError as e:
        # Instead of aborting silently, write a short failure report for visibility
        msg = str(e)
        print(msg)
        out = reporter.report_failure(cfg.get("market"), msg)
        print(f"Discovery failure report written to: {out}")
        return

    out = reporter.report(results)
    print(f"Report written to: {out}")

if __name__ == "__main__":
    main()
