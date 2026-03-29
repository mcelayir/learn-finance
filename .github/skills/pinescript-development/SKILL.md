---
name: pinescript-development
description: "Expert guide for writing, debugging, and optimizing PineScript v6 indicators, strategies, and libraries for TradingView. Use this skill when asked to create or modify TradingView indicators, trading strategies, alerts, Pine Script code, oscillators, moving averages, backtesting scripts, or any TradingView chart logic."
---

# PineScript v6 Development for TradingView

This skill provides expert guidance for developing **PineScript v6** scripts on TradingView. All code must use `// @version=6`. Do not produce v5 syntax.

---

## Key v6 Breaking Changes (vs v5)

These are mandatory — v5 patterns will cause compile errors in v6:

| Area | v5 (old — do NOT use) | v6 (correct) |
|---|---|---|
| Version annotation | `//@version=5` | `//@version=6` |
| Bool from int/float | `if myInt` (implicit cast) | `if myInt != 0` (explicit) |
| Bool can be `na` | `bool b = na` | Not allowed — bools are strictly `true` or `false` |
| `na()` on bools | `na(myBool)` | Not allowed; remove or restructure |
| `strategy.*` `when` param | `strategy.entry("L", strategy.long, when=cond)` | `if cond\n    strategy.entry("L", strategy.long)` |
| `transp` param | `plot(x, transp=50)` | `plot(x, color=color.new(color.blue, 50))` |
| History of literals | `1.0[1]` | Not allowed — assign to a variable first |
| `for` loop end boundary | evaluated once | evaluated **before every iteration** (dynamic) |
| Const int division | `5 / 2 == 2` (integer) | `5 / 2 == 2.5` (float) |
| `timeframe.period` | `"D"` (no multiplier) | `"1D"` (always includes multiplier) |
| Strategy trade limit | error at 9000 trades | oldest orders trimmed automatically |
| `strategy.exit` params | absolute params silenced relative ones | both evaluated; nearest level wins |
| Dynamic requests | opt-in (`dynamic_requests=true`) | **always on** by default |
| Array negative index | not supported | `array.get(arr, -1)` returns last element |

---

## Script Type Declarations

```pine
//@version=6

// Indicator
indicator("My Indicator", overlay=true, shorttitle="MyInd", precision=2)

// Strategy (note: no `when` param anywhere)
strategy("My Strategy", overlay=true, initial_capital=10000,
         default_qty_type=strategy.percent_of_equity, default_qty_value=10,
         commission_type=strategy.commission.percent, commission_value=0.1,
         margin_long=100, margin_short=100)

// Library
library("MyLibrary", overlay=true)
```

---

## Type System and Variable Declarations

```pine
//@version=6
indicator("Types demo", overlay=true)

// Explicit types are required in typed contexts (functions, UDTs)
float myPrice  = close
int   myLen    = 14
bool  isUp     = close > open        // must be explicitly bool — never int/float

// Correct bool checks (no implicit casting)
int count = 5
if count != 0                        // correct: explicit comparison
    label.new(bar_index, high, "ok")
// if count  <- compile error in v6

// var  – initialized once, persists across bars
var float cumSum = 0.0
cumSum += close

// varip – persists across real-time tick updates within the same bar
varip int tickCount = 0
tickCount += 1

// Series variable (recalculates every bar, no keyword needed)
float ema20 = ta.ema(close, 20)
```

---

## Enums (v6 New Feature)

```pine
//@version=6
indicator("Enum demo", overlay=true)

enum Signal
    Buy
    Sell
    Neutral

Signal currentSignal = close > ta.sma(close, 20) ? Signal.Buy :
                       close < ta.sma(close, 20) ? Signal.Sell :
                       Signal.Neutral

if currentSignal == Signal.Buy
    label.new(bar_index, low, "BUY", color=color.green)
```

---

## Common Technical Analysis Built-ins

```pine
//@version=6
indicator("TA built-ins", overlay=false)

float sma14  = ta.sma(close, 14)
float ema20  = ta.ema(close, 20)
float wma10  = ta.wma(close, 10)
float hma9   = ta.hma(close, 9)
float vwma20 = ta.vwma(close, 20)

float atr14 = ta.atr(14)
[float bbMid, float bbUpper, float bbLower] = ta.bb(close, 20, 2.0)

float rsi14 = ta.rsi(close, 14)
[float macdLine, float signalLine, float hist] = ta.macd(close, 12, 26, 9)
[float diPlus, float diMinus, float adxVal]   = ta.dmi(14, 14)
float stochK = ta.stoch(close, high, low, 14)

float obvVal = ta.obv

// Pivot functions return na on non-pivot bars — always guard with na check
float ph = ta.pivothigh(high, 5, 5)
float pl = ta.pivotlow(low, 5, 5)
```

---

## Boolean Logic — Lazy Evaluation (v6)

In v6, `and` and `or` are **lazy** (short-circuit). The right side only evaluates if needed. This enables safe array-bounds guards in a single expression:

```pine
//@version=6
indicator("Lazy bool demo", overlay=true)

var float[] prices = array.new<float>()
prices.push(close)

// Safe in v6 — if size is 0, first() never executes
if prices.size() != 0 and prices.first() > 0
    label.new(bar_index, high, "positive")
```

---

## Arrays (v6 Enhancements)

```pine
//@version=6
indicator("Arrays v6", overlay=true)

// Typed array declaration
array<float> prices = array.new<float>(0)

// Push and access
prices.push(close)
prices.push(open)

// Direct indexing (v6) — replaces array.get / array.set for simple access
float last  = prices[-1]           // last element via negative index
float first = prices[0]
prices[0]  := high                 // direct assignment

// array.from shorthand
array<float> levels = array.from(1.0, 1.5, 2.0)

// for-in loop over array
for val in prices
    float dummy = val * 2          // process val

// range() replaces `for i = 0 to N-1`
for i in range(0, prices.size())
    float v = prices[i]

// Negative index on built-in functions
float secondLast = array.get(prices, -2)
```

---

## Dynamic Requests — Multi-Symbol / Multi-Timeframe (v6)

In v6, `request.*()` works **inside loops and conditionals by default** — no `dynamic_requests=true` needed.

```pine
//@version=6
indicator("Dynamic requests", overlay=false)

// Multi-symbol loop (impossible in v5 without workarounds)
array<string> symbols = array.from("NASDAQ:AAPL", "NASDAQ:MSFT", "NYSE:SPY")
array<float>  closes  = array.new<float>(0)

for sym in symbols
    float c = request.security(sym, timeframe.period, close)
    closes.push(c)

// Standard single-symbol MTF — confirmed bars only (anti-repainting)
float htfClose = request.security(syminfo.tickerid, "1D", close[1],
                                   lookahead=barmerge.lookahead_off)
float htfSMA   = request.security(syminfo.tickerid, "1W", ta.sma(close, 20))
```

> `timeframe.period` now always includes a multiplier (`"1D"` not `"D"`). Update any string comparisons accordingly.

---

## Strategy Orders (v6 — No `when` Parameter)

```pine
//@version=6
strategy("v6 Strategy", overlay=true,
         default_qty_type=strategy.percent_of_equity, default_qty_value=10,
         commission_type=strategy.commission.percent, commission_value=0.075)

float ema20 = ta.ema(close, 20)
float sma50 = ta.sma(close, 50)
float atr14 = ta.atr(14)

// v6: wrap entries in if blocks — no `when` parameter exists
if ta.crossover(ema20, sma50)
    strategy.entry("Long", strategy.long)

if ta.crossunder(ema20, sma50)
    strategy.close("Long")

// In v6, both absolute and relative exit params are evaluated — nearest level wins
if strategy.position_size > 0
    strategy.exit("Long Exit", "Long",
                  profit = atr14 * 2 / syminfo.mintick,
                  loss   = atr14     / syminfo.mintick)

// Short entry
if ta.crossunder(ema20, sma50)
    strategy.entry("Short", strategy.short)

// Access oldest non-trimmed trade index (v6 — replaces hard 9000 error)
int firstIdx = strategy.closedtrades.first_index
```

---

## Plotting and Visuals

```pine
//@version=6
indicator("Visuals", overlay=true)

float sma20 = ta.sma(close, 20)

plot(sma20, "SMA 20", color=color.blue, linewidth=2)

// Conditional color — must be explicit bool comparison
color barCol = close > open ? color.green : color.red
barcolor(barCol)

// Shapes
bool buySignal = ta.crossover(close, sma20)
plotshape(buySignal, style=shape.triangleup, location=location.belowbar,
          color=color.green, size=size.small)

// Hlines
hline(70, "OB", color=color.red,   linestyle=hline.style_dashed)
hline(30, "OS", color=color.green, linestyle=hline.style_dashed)

// Fill between two plots
p1 = plot(ta.bb(close, 20, 2).upper, color=color.blue)
p2 = plot(ta.bb(close, 20, 2).lower, color=color.blue)
fill(p1, p2, color=color.new(color.blue, 90))

// Background — no `transp` param in v6, always use color.new()
bgcolor(close > sma20 ? color.new(color.green, 92) : na)

// Labels — v6 supports numeric typographic point sizes
if buySignal
    label.new(bar_index, low, "Buy", color=color.green,
              textcolor=color.white, size=size.small)
```

---

## Inputs

```pine
//@version=6
indicator("Inputs", overlay=false)

int    lengthInput = input.int(14, "RSI Length", minval=1, maxval=500)
float  srcInput    = input.source(close, "Source")
float  multInput   = input.float(2.0, "Multiplier", step=0.1)
bool   showSigs    = input.bool(true, "Show Signals")
string maType      = input.string("EMA", "MA Type", options=["SMA","EMA","WMA","HMA"])
color  bullColor   = input.color(color.green, "Bull Color")
string htfInput    = input.timeframe("D", "Higher Timeframe")
```

---

## User-Defined Types (UDTs)

```pine
//@version=6
indicator("UDT demo", overlay=true)

type SignalData
    float price
    bool  isLong
    int   barIdx

SignalData sig = SignalData.new(close, true, bar_index)

float entryPrice = sig.price

// History on UDT fields directly is NOT allowed in v6
// Assign field to a local variable first, then reference history
float prevPrice = sig.price
float histPrice = prevPrice[1]   // correct
// float histPrice = sig.price[1]  <- compile error in v6
```

---

## Methods (Dot Syntax on Built-ins)

```pine
//@version=6
indicator("Methods", overlay=false)

// Method syntax on series (v6)
float rsi = close.ta.rsi(14)
float sma  = close.ta.sma(20)

// String method
string ticker = syminfo.ticker.str.lower()
```

---

## Typed Function Signatures (v6 Best Practice)

```pine
//@version=6
indicator("Typed functions", overlay=false)

// Explicit param and return types
calcBands(float src, int len, float mult) =>
    float basis = ta.sma(src, len)
    float dev   = ta.stdev(src, len) * mult
    [basis, basis + dev, basis - dev]

[float mid, float upper, float lower] = calcBands(close, 20, 2.0)

myRsi(float src, int len) => float
    ta.rsi(src, len)
```

---

## Loops

```pine
//@version=6
indicator("Loops", overlay=false)

// for-in over array
array<float> vals = array.from(1.0, 2.0, 3.0)
float total = 0.0
for v in vals
    total += v

// range() — cleaner than `for i = 0 to N-1`
for i in range(0, 5)
    total += i

// while loop
int n = 0
while n < 10
    n += 1

// IMPORTANT: for-loop end boundary is re-evaluated before every iteration in v6
// If the upper bound variable changes inside the loop, iterations adjust accordingly
```

---

## Alerts

```pine
//@version=6
indicator("Alerts", overlay=false)

float sma20   = ta.sma(close, 20)
bool  crossUp = ta.crossover(close, sma20)

// alertcondition — user sets the alert in TradingView UI
alertcondition(crossUp, title="Cross Up",
               message="{{ticker}} crossed above SMA on {{interval}}")

// alert() — fires programmatically
if crossUp
    alert("Buy: " + syminfo.ticker, alert.freq_once_per_bar)
```

---

## Bid / Ask Variables (v6 — 1T Timeframe Only)

```pine
//@version=6
indicator("Bid Ask", overlay=true)

// Only available on the "1T" (tick) timeframe
if timeframe.period == "1T"
    float currentBid = bid
    float currentAsk = ask
    float spread     = ask - bid
```

---

## Anti-Repainting Best Practices

```pine
//@version=6
indicator("Anti-repaint", overlay=true)

// Use barstate.isconfirmed to signal only on closed bars
bool buySignal = ta.crossover(ta.ema(close, 20), ta.sma(close, 50))
             and barstate.isconfirmed

// MTF: request close[1] with lookahead off to avoid peeking into future bars
float htfClose = request.security(syminfo.tickerid, "1D", close[1],
                                   lookahead=barmerge.lookahead_off)

// timeframe.period now always has multiplier in v6
if timeframe.period == "1D"            // correct
    label.new(bar_index, high, "Daily bar")
```

---

## Debugging

```pine
//@version=6
indicator("Debug", overlay=false)

float rsi14 = ta.rsi(close, 14)

// Data Window (invisible on chart, visible in Data Window panel)
plot(rsi14, "RSI debug", display=display.data_window)

// log.*() — native runtime logging in v6
if barstate.islast
    log.info("Last bar RSI: {0}", rsi14)
    log.warning("Close: {0}, Open: {1}", close, open)

// On-chart debug table
var table dbg = table.new(position.top_right, 2, 3,
                           bgcolor=color.white, border_width=1)
if barstate.islast
    table.cell(dbg, 0, 0, "RSI",   text_color=color.black)
    table.cell(dbg, 1, 0, str.tostring(rsi14, "#.##"), text_color=color.black)
    table.cell(dbg, 0, 1, "Close", text_color=color.black)
    table.cell(dbg, 1, 1, str.tostring(close, "#.##"), text_color=color.black)
```

---

## Recommended Script Structure

```pine
//@version=6
indicator("Script Name", overlay=true)

// 1. Inputs
int    length = input.int(14, "Length")
string maType = input.string("EMA", "MA Type", options=["SMA","EMA"])

// 2. Calculations
float ma = switch maType
    "SMA" => ta.sma(close, length)
    "EMA" => ta.ema(close, length)
    =>       ta.ema(close, length)

// 3. Conditions — explicit bool, confirmed bars only
bool crossUp = ta.crossover(close, ma) and barstate.isconfirmed

// 4. Visuals
plot(ma, "MA", color=color.blue)
plotshape(crossUp, style=shape.triangleup, location=location.belowbar,
          color=color.green, size=size.small)

// 5. Alerts
alertcondition(crossUp, "Cross Up", "{{ticker}} crossed above MA")
```

---

## Common v6 Pitfalls

- **No implicit bool casting** — write `x != 0`, `not na(x)`, or `x > 0` instead of using a numeric directly in a condition.
- **No `when` in strategy calls** — wrap every `strategy.entry/close/exit` in an `if` block.
- **No `transp` parameter** — use `color.new(col, transparency)` everywhere.
- **`timeframe.period` includes multiplier** — compare against `"1D"`, `"1W"`, `"60"`, never bare `"D"` or `"W"`.
- **History on UDT fields** — assign the field to a local variable first, then apply `[n]` on that variable.
- **Dynamic `for` end boundary** — the upper bound is re-evaluated before every iteration, not once at the start.
- **`na` on booleans** — not allowed; restructure logic with explicit fallback values.
- **Array negative indices** — `arr[-1]` is the last element; useful but easy to confuse with the bar history operator `close[-1]` (which is a future bar reference, usually illegal).
- **Drawing object limits** — `line`, `label`, `box`, `table` are capped at 500 per type by default; delete old objects inside loops.
- **Const int division** — `5 / 2` now returns `2.5`, not `2`; use `int(5 / 2)` if you need integer division.

---

## Reference Library

This skill includes the official PineScript v6 documentation chunked for LLM
consumption. Before writing any code, consult `references/LLM_MANIFEST.md`
to locate the correct reference file for the task at hand.

### When to load each file

| Task | Load this file |
|---|---|
| Indicators — RSI, EMA, pivots, any `ta.*` function | `references/reference/functions/ta.md` |
| Strategies — entries, exits, stop-loss, backtesting | `references/reference/functions/strategy.md` |
| Multi-timeframe / multi-symbol data (`request.*`) | `references/reference/functions/request.md` |
| Visuals — `plot`, `line`, `box`, `label`, `polyline` | `references/reference/functions/drawing.md` |
| Arrays, matrices, maps | `references/reference/functions/collections.md` |
| Built-in variables (`close`, `open`, `syminfo.*`) | `references/reference/variables.md` |
| Built-in constants (`color.red`, `strategy.long`) | `references/reference/constants.md` |
| Execution model, series vs simple, bar evaluation | `references/concepts/` |
| Debugging, style guide, optimization | `references/writing_scripts/` |
| Unsure which file to open | `references/LLM_MANIFEST.md` |

### Rules for using these references

1. Always check `references/LLM_MANIFEST.md` first when the task spans
   multiple namespaces — it maps every topic to its file.
2. Load only the file(s) relevant to the current task. Do not load all
   references at once.
3. If a function is not found in the reference files, it does not exist
   in v6 or has been renamed. Do not invent syntax.
4. All generated code must start with `//@version=6`.