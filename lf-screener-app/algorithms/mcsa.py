from .base import BaseAlgorithm

class MCSAAlgorithm(BaseAlgorithm):
    """PoC MCSA algorithm implementing simplified scoring rules.

    Scoring (out of 100):
    - Technical (40%): price > ma150 and price > ma200 and ma150 > ma200 -> 100 else 0
    - Fundamental (35%): roe >= 15 and debt_equity <= 1.0 -> 100 else 0
    - VCP (15%): atr_current < atr_20 -> 100 else 0
    - Bonus (10%): volume > 1.5 * vol_20 -> 100 else 0
    """

    def run(self, ticker: str, data_provider) -> dict:
        import yaml
        import os
        # Load config.yaml for thresholds
        config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        thresholds = config.get('mcsa_thresholds', {})
        pe_ratio_min = thresholds.get('pe_ratio_min', 5)
        pe_ratio_max = thresholds.get('pe_ratio_max', 50)
        pb_ratio_max = thresholds.get('pb_ratio_max', 5)
        roe_min = thresholds.get('roe_min', 15)
        net_margin_min = thresholds.get('net_margin_min', 10)
        debt_equity_max = thresholds.get('debt_equity_max', 1.0)

        data = data_provider.fetch_data(ticker)
        price = data.get("price")
        ma150 = data.get("ma150")
        ma200 = data.get("ma200")
        pe_ratio = data.get("pe_ratio")
        pb_ratio = data.get("standard_pb_ratio")
        roe = data.get("roe")
        net_margin = data.get("net_margin")
        debt_equity = data.get("debt_equity")
        atr_current = data.get("atr_current")
        atr_20 = data.get("atr_20")
        volume = data.get("volume")
        vol_20 = data.get("vol_20")

        # Debug: Print all fundamental values for diagnostics
        print(f"[MCSA] {ticker} Fundamentals: PE={pe_ratio}, StandardPB={pb_ratio}, ROE={roe}, NetMargin={net_margin}, Debt/Equity={debt_equity}")

        # Technical: price > ma150 and price > ma200 and ma150 > ma200
        technical_ok = price is not None and ma150 is not None and ma200 is not None and price > ma150 and price > ma200 and ma150 > ma200

        # Fundamental: all checks must pass
        fundamental_checks = [
            pe_ratio is not None and pe_ratio_min <= pe_ratio <= pe_ratio_max,
            pb_ratio is not None and pb_ratio <= pb_ratio_max,
            roe is not None and roe >= roe_min,
            net_margin is not None and net_margin >= net_margin_min,
            debt_equity is not None and debt_equity <= debt_equity_max,
        ]
        fundamental_ok = all(fundamental_checks)

        vcp_ok = atr_current is not None and atr_20 is not None and atr_current < atr_20
        bonus_ok = volume is not None and vol_20 is not None and volume > 1.5 * vol_20

        technical_score = 100 if technical_ok else 0
        fundamental_score = 100 if fundamental_ok else 0
        vcp_score = 100 if vcp_ok else 0
        bonus_score = 100 if bonus_ok else 0

        total = (
            technical_score * 0.40
            + fundamental_score * 0.35
            + vcp_score * 0.15
            + bonus_score * 0.10
        )

        total = round(total, 2)

        # Determine category
        if total >= 85:
            category = "Excellent Setup"
        elif total >= 70:
            category = "Strong Setup"
        elif total >= 55:
            category = "Average Setup"
        else:
            category = "Weak Setup"

        return {
            "ticker": ticker,
            "score": total,
            "category": category,
            "components": {
                "technical": technical_score,
                "fundamental": fundamental_score,
                "vcp": vcp_score,
                "bonus": bonus_score,
            },
            "raw": data,
        }
