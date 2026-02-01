# Minervini-Chartist Scoring Algorithm (MCSA)
**Comprehensive Implementation Guide: From Fundamentals to Expert Execution**

---

## 1. Introduction & Philosophy
The **MCSA** is a quantitative "Momentum & Growth" model. It is designed to filter out market noise and identify stocks that are both fundamentally strong and technically ready to move. It follows the **Trend Template** philosophy: "Buy strength, sell weakness, and prioritize timing."

---

## 2. Phase One: The Technical Filter (40% Weight)
*A stock must be in a "Stage 2" (Advancing Phase) to be considered.*

| # | Criterion | Rule |
| :--- | :--- | :--- |
| 1 | **Price vs 150 MA** | Current Price > 150-Day Moving Average |
| 2 | **Price vs 200 MA** | Current Price > 200-Day Moving Average |
| 3 | **Trend Alignment** | 150-Day MA > 200-Day MA |
| 4 | **200 MA Trend** | 200-Day MA must be trending up for at least 1 month |
| 5 | **Speed Alignment** | 50-Day MA > 150-Day MA |
| 6 | **Momentum Stack** | 50-Day MA > 200-Day MA |
| 7 | **Price vs 50 MA** | Current Price > 50-Day Moving Average |
| 8 | **52-Week Range** | Price > 30% above 52W Low AND within 25% of 52W High |

---

## 3. Phase Two: The Fundamental Filter (35% Weight)
*Measures the internal engine and financial health of the company.*

* **Valuation Range:** P/E Ratio between **5 and 50**.
* **Asset Pricing:** P/B Ratio **≤ 5**.
* **Financial Safety:** Debt/Equity Ratio **≤ 1.0**.
* **Profitability:** ROE (Return on Equity) **≥ 15%**.
* **Efficiency:** Net Profit Margin **≥ 10%**.
* **Growth (The Spark):** Positive Revenue and Earnings Growth (Quarter-over-Quarter).

---

## 4. Phase Three: VCP & Timing (15% Weight)
*The Volatility Contraction Pattern (VCP) identifies the "Entry Trigger."*

* **ATR Contraction:** Current ATR < 20-Day ATR < 50-Day ATR.
* **Tightness:** Price range over the last 3 weeks is at least 20% narrower than the previous 3 weeks.
* **Volume Dry-up:** Volume on "quiet" days should be 20-30% below the 50-day average.
* **The Launchpad:** Price should be within **5%** of the 50-Day Moving Average.

---

## 5. Phase Four: Scoring & Bonus System

**The Formula:**
$Total Score = (Tech \% \times 40) + (Fund \% \times 35) + (VCP \% \times 15) + Bonuses$

**The Bonus Multipliers (+15 Points Max):**
1. **First Signal (+10 pts):** Stock has just entered the "Template" within the last 20 days.
2. **Volume Breakout (+5 pts):** Daily volume is >150% of the 50-day average during a price breakout.

---

## 6. Phase Five: Decision Matrix

| Score Range | Category | Action Plan |
| :--- | :--- | :--- |
| **85 - 100** | **Mükemmel Setup** | High Conviction. Standard position size. Ready to buy. |
| **70 - 84** | **Güçlü Setup** | Good opportunity. Monitor the "missing" criteria closely. |
| **55 - 69** | **Orta Setup** | "Wait & See." Do not enter yet; let the trend mature. |
| **0 - 54** | **Zayıf Setup** | Avoid. High risk of failure or stagnation. |

---

## 7. Appendix: Financial Glossary & Abbreviations

### P/E Ratio (Price-to-Earnings)
The market price of one share divided by the annual earnings per share (EPS). It indicates how much investors are paying for every $1 of profit.

### P/B Ratio (Price-to-Book)
Compares the market value to the "book value" (net worth). A high P/B means the market expects high future growth, while a low P/B suggests the company is valued closer to its physical assets.

### Debt/Equity Ratio (D/E)
Calculated by dividing total liabilities by shareholder equity. It measures financial leverage. Stocks with **D/E > 1.0** are considered risky in high-interest environments.

### ROE (Return on Equity)
The "Efficiency King." It shows how much profit a company generates with every dollar of shareholders' money. **ROE ≥ 15%** is the benchmark for high-quality management.

### ATR (Average True Range)
A volatility indicator that shows how much an asset price moves on average. In VCP, we look for **falling ATR**, which signals that price "swings" are tightening before a breakout.

### RS Rating (Relative Strength)
A score ranking a stock's 12-month price performance against the entire market. It identifies "Leaders" vs "Laggards."