"""
Minervini-Chartist Scoring Algorithm (MCSA)
Comprehensive implementation based on the provided guide.
"""
from typing import Dict, Any

class MCSA:
    def __init__(self, data: Dict[str, Any]):
        """
        data: dict containing all required metrics for a single stock
        Expected keys:
            - price, ma_50, ma_150, ma_200
            - ma_200_trend_up_1m (bool)
            - low_52w, high_52w
            - pe_ratio, pb_ratio, debt_equity, roe, net_margin
            - rev_growth_qoq, earnings_growth_qoq
            - atr, atr_20, atr_50
            - price_range_3w, price_range_prev_3w
            - volume_quiet, volume_50d_avg
        """
        self.data = data

    def technical_score(self) -> float:
        d = self.data
        score = 0
        checks = [
            d['price'] > d['ma_150'],
            d['price'] > d['ma_200'],
            d['ma_150'] > d['ma_200'],
            d['ma_200_trend_up_1m'],
            d['ma_50'] > d['ma_150'],
            d['ma_50'] > d['ma_200'],
            d['price'] > d['ma_50'],
            (d['price'] > d['low_52w'] * 1.3) and (d['price'] >= d['high_52w'] * 0.75)
        ]
        score = sum(checks) / len(checks)
        return score

    def fundamental_score(self) -> float:
        d = self.data
        checks = [
            5 <= d['pe_ratio'] <= 50,
            d['pb_ratio'] <= 5,
            d['debt_equity'] <= 1.0,
            d['roe'] >= 15,
            d['net_margin'] >= 10,
            d['rev_growth_qoq'] > 0,
            d['earnings_growth_qoq'] > 0
        ]
        score = sum(checks) / len(checks)
        return score

    def vcp_score(self) -> float:
        d = self.data
        checks = [
            d['atr'] < d['atr_20'] < d['atr_50'],
            d['price_range_3w'] <= d['price_range_prev_3w'] * 0.8,
            d['volume_quiet'] <= d['volume_50d_avg'] * 0.8,
            abs(d['price'] - d['ma_50']) <= d['ma_50'] * 0.05
        ]
        score = sum(checks) / len(checks)
        return score

    def bonus_score(self) -> float:
        d = self.data
        bonus = 0
        # First Signal: Stock has just entered the "Template" within the last 20 days
        if d.get('entered_template_last_20d', False):
            bonus += 10
        # Volume Breakout: Daily volume >150% of 50-day average during a price breakout
        if d.get('volume_breakout', False):
            bonus += 5
        return min(bonus, 15)

    def total_score(self) -> float:
        tech = self.technical_score()
        fund = self.fundamental_score()
        vcp = self.vcp_score()
        bonus = self.bonus_score()
        total = tech * 40 + fund * 35 + vcp * 15 + bonus
        return total

    def decision_category(self) -> str:
        score = self.total_score()
        if score >= 85:
            return "Mükemmel Setup"
        elif score >= 70:
            return "Güçlü Setup"
        elif score >= 55:
            return "Orta Setup"
        else:
            return "Zayıf Setup"

if __name__ == "__main__":
    # Example usage with dummy data
    example_data = {
        'price': 120,
        'ma_50': 115,
        'ma_150': 110,
        'ma_200': 105,
        'ma_200_trend_up_1m': True,
        'low_52w': 80,
        'high_52w': 130,
        'pe_ratio': 25,
        'pb_ratio': 3,
        'debt_equity': 0.5,
        'roe': 18,
        'net_margin': 12,
        'rev_growth_qoq': 0.05,
        'earnings_growth_qoq': 0.07,
        'atr': 2.0,
        'atr_20': 2.5,
        'atr_50': 3.0,
        'price_range_3w': 5,
        'price_range_prev_3w': 7,
        'volume_quiet': 80000,
        'volume_50d_avg': 120000,
        'entered_template_last_20d': True,  # Bonus example
        'volume_breakout': True            # Bonus example
    }
    mcsa = MCSA(example_data)
    print(f"Technical Score: {mcsa.technical_score():.2f}")
    print(f"Fundamental Score: {mcsa.fundamental_score():.2f}")
    print(f"VCP Score: {mcsa.vcp_score():.2f}")
    print(f"Bonus Score: {mcsa.bonus_score():.2f}")
    print(f"Total Score: {mcsa.total_score():.2f}")
    print(f"Decision Category: {mcsa.decision_category()}")
