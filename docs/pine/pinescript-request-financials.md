# Pine Script Financial Data Retrieval: Agile Reference

## Purpose
This document provides a concise, actionable reference for retrieving and calculating financial metrics in Pine Script using `request.financial`. It is tailored for agile teams and practitioners seeking robust, maintainable TradingView indicators.

---

## 1. Directly Usable Financial Keywords
The following table lists the most relevant keywords for use with `request.financial(symbol, keyword, period)` in Pine Script. These enable direct access to fundamental data fields.

| Metric                        | Keyword (2nd arg)                                 | Typical Period | Description                                 |
|-------------------------------|--------------------------------------------------|---------------|---------------------------------------------|
| Earnings Per Share            | EARNINGS_PER_SHARE                               | TTM           | Trailing 12M EPS                            |
| Book Value Per Share          | BOOK_VALUE_PER_SHARE                             | FQ            | Quarterly book value per share               |
| Total Debt                    | TOTAL_DEBT                                       | FQ            | Total debt (quarterly)                      |
| Total Equity                  | TOTAL_EQUITY                                     | FQ            | Total equity (quarterly)                    |
| Return on Equity              | RETURN_ON_EQUITY                                 | FQ            | ROE (%)                                     |
| Net Margin                    | NET_MARGIN                                       | FQ            | Net profit margin (%)                       |
| Revenue Growth (YoY)          | REVENUE_ONE_YEAR_GROWTH                          | FQ            | Revenue growth, year over year (%)          |
| EPS Growth (YoY)              | EARNINGS_PER_SHARE_BASIC_ONE_YEAR_GROWTH         | FQ            | EPS growth, year over year (%)              |

> For the full list, see TradingView’s [official documentation](https://tr.tradingview.com/pine-script-docs/en/v5/concepts/Request.html#requestfinancial).
> - [Comprehensive list of request.financial keywords (TradingView Help)](https://tr.tradingview.com/?solution=43000564727)

---

## 2. Calculating Derived Metrics
Some financial ratios are not available as a single field and must be calculated using available keywords. Below are the formulas used in our implementation:

| Metric           | Formula (Pine Script)                                                                                 |
|------------------|------------------------------------------------------------------------------------------------------|
| PE Ratio         | `pe_ratio = not na(eps) and eps != 0 ? close / eps : na`<br>where `eps = request.financial(..., "EARNINGS_PER_SHARE", "TTM")` |
| PB Ratio         | `pb_ratio = not na(bvps) and bvps != 0 ? close / bvps : na`<br>where `bvps = request.financial(..., "BOOK_VALUE_PER_SHARE", "FQ")` |
| Debt/Equity      | `debt_equity = not na(debt) and not na(equity) and equity != 0 ? debt / equity : na`<br>where `debt = request.financial(..., "TOTAL_DEBT", "FQ")`, `equity = request.financial(..., "TOTAL_EQUITY", "FQ")` |

---

## 3. Agile Usage Guidelines
- **Fail gracefully:** Always check for `na()` when using financial data. Not all tickers or timeframes provide all fields.
- **Document assumptions:** Clearly state which fields are required and how missing data is handled in your code.
- **Keep formulas transparent:** Use explicit, readable calculations for derived metrics.
- **Reference source:** Link to TradingView documentation for maintainability.

---

## 4. Example Usage
```pinescript
// Retrieve and calculate PE Ratio
var eps = request.financial(syminfo.tickerid, "EARNINGS_PER_SHARE", "TTM")
var pe_ratio = not na(eps) and eps != 0 ? close / eps : na
```

---

## 5. References
- [TradingView Pine Script Docs: request.financial](https://tr.tradingview.com/pine-script-docs/en/v5/concepts/Request.html#requestfinancial)
- [MCSA Pine Script Implementation](../../code/pine/mcsa.pine)

---

*This document is maintained in accordance with agile documentation standards: concise, actionable, and always up-to-date with implementation.*
