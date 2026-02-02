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
        data = data_provider.fetch_data(ticker)
        price = data.get("price")
        ma150 = data.get("ma150")
        ma200 = data.get("ma200")
        roe = data.get("roe")
        debt_equity = data.get("debt_equity")
        atr_current = data.get("atr_current")
        atr_20 = data.get("atr_20")
        volume = data.get("volume")
        vol_20 = data.get("vol_20")

        technical_ok = price > ma150 and price > ma200 and ma150 > ma200
        fundamental_ok = roe is not None and debt_equity is not None and roe >= 15 and debt_equity <= 1.0
        vcp_ok = atr_current < atr_20
        bonus_ok = volume > 1.5 * vol_20

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
