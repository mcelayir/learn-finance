from core.config import load_config
from core.engine import Engine
from reporting.txt_reporter import GroupedTXTReporter


def main():
    cfg = load_config("config.yaml")
    engine = Engine(cfg)
    results = engine.run(cfg.get("market"))
    reporter = GroupedTXTReporter(cfg.get("output_file"))
    out = reporter.report(results)
    print(f"Report written to: {out}")

if __name__ == "__main__":
    main()
