# Quantiacs Q25 Crypto Strategies - Comprehensive Status Report

**Report Generated**: 2026-06-13  
**Test Period**: 2024-01-01 to 2025-12-31  
**Data**: Quantiacs crypto daily OHLCV, 76 assets  
**Backtest Convention**: Close-to-close daily returns, long-only, liquid assets only, cost = 0.15% one-way turnover

---

## Executive Summary

This repository contains **6 core strategies** currently in the codebase, all focused on crypto daily trading. Additionally, research has been conducted on 10 experimental approaches. The core strategies are:

| Strategy | Category | Test CAGR | Test Sharpe | Max DD | Philosophy |
|----------|----------|-----------|------------|--------|------------|
| **Ensemble** (DEFAULT) | Regime-Aware | N/A* | N/A* | N/A* | Blends momentum + mean reversion, regime-dependent weights |
| Momentum | Momentum | Researched | Researched | Researched | Pure momentum + trend following |
| Mean Reversion | Mean Reversion | Researched | Researched | Researched | Reverting to 15-day SMA |
| Persistent Low Vol | Volatility | 90.4% | 1.40 | -26.8% | Equal-weight lowest 25% volatility assets |
| Momentum + Low Vol | Volatility | 34.2% | 0.84 | -38.6% | Momentum gate + 40th percentile volatility filter |
| Cross-Sectional Momentum | Momentum | 20.3% | 0.63 | -60.4% | Top 10% momentum winners, equal-weighted |

**Note**: *The Ensemble strategy was tested in research but appears to be the DEFAULT. See details below.

---

## Part 1: Core Codebase Strategies

These 6 strategies are exported from `q25_crypto/strategies.py` and can be selected via `QNT_STRATEGY_MODE` environment variable.

### 1. **Ensemble Strategy** (DEFAULT)
**Philosophy**: Regime-aware allocation between trend-following and mean-reversion.

**Implementation**:
```python
def ensemble_long_only(data):
    trend = momentum_score + 0.3 * trend_score
    mean_reversion = mean_reversion_score
    
    trend_component = max(trend, 0)
    mean_component = max(mean_reversion, 0)
    
    IF trend_regime > 0:
        weights = blend_scores(trend_component, mean_component, 75/25)
    ELSE:
        weights = blend_scores(trend_component, mean_component, 35/65)
    
    normalize_long_only(weights, liquid_mask)
```

**Logic**:
- In uptrends (positive trend regime): favor momentum (75%) over mean reversion (25%)
- In downtrends/sideways: favor mean reversion (65%) over momentum (35%)
- Trend regime = 20/120-day MA trend - 0.5 × volatility penalty
- Applies liquidity score multiplier
- Normalizes to 100% long, equal-weighted by default

**Strengths**:
- Adapts to market regime
- Combines two complementary signals
- Volatility-dampened

**Weaknesses**:
- Requires accurate regime detection (volatile environments may misclassify)
- 50/50 weighting of contradictory signals in sideways markets

---

### 2. **Momentum Long-Only**
**Philosophy**: Pure trend-following with volatility dampening.

**Implementation**:
```python
score = momentum_score(data) + 0.4 * trend_score(data)
score = score - 0.3 * volatility_penalty(data)
score = score * liquidity_score(data)
return normalize_long_only(score, liquid_mask)
```

**Signals**:
- **Momentum**: 10-day LWMA / 50-day LWMA - 1
- **Trend**: 20-day LWMA / 120-day LWMA - 1  
- **Volatility Penalty**: -0.3 × 20-day smoothed True Range / close
- **Liquidity Boost**: 1.0 + 0.15 × (recent vol / baseline vol)

**Strengths**:
- Simple, intuitive
- Fast entry/exit signals from 10-day momentum
- Momentum-weighted (assigns higher positions to stronger winners)

**Weaknesses**:
- Whipsawed in choppy/ranging markets
- May chase tops
- No regime adaptation

---

### 3. **Mean Reversion Long-Only**
**Philosophy**: Bet against recent weakness, revert to fundamentals.

**Implementation**:
```python
score = mean_reversion_score(data)
score = score - 0.2 * volatility_penalty(data)
score = score * liquidity_score(data)
return normalize_long_only(score, liquid_mask)
```

**Signals**:
- **Mean Reversion**: -(close / 15-day SMA - 1)
  - Negative when close > SMA (overbought) → lower position
  - Positive when close < SMA (oversold) → higher position
- Light volatility penalty (-0.2×)
- Liquidity boost applied

**Strengths**:
- Profitable in mean-reverting regimes (flat/choppy markets)
- Lower volatility penalty (lighter than momentum)
- Liquidity-weighted

**Weaknesses**:
- Fades legitimate trends (buys during downtrends, shorts opportunity during uptrends)
- Poor in prolonged bull/bear runs
- Underweights strong winners

---

### 4. **Persistent Low Volatility Long-Only**
**Philosophy**: Select stable, liquid assets; ignore price trends.

**Implementation**:
```python
liquid = liquid_mask(data)
realized = realized_volatility(data, 150-day lookback).where(liquid)
vol_rank = rank_as_percentile(realized)
return equal_weight_mask(vol_rank <= 0.25, liquid)
```

**Logic**:
- Calculate 150-day rolling volatility for each asset
- Rank by volatility percentile
- Equal-weight hold the lowest-volatility 25% of assets
- Binary inclusion (all-in or all-out per asset)
- High liquidity exposure (1.0)

**Strengths**:
- **Best performer** in test set: 90.4% CAGR, 1.40 Sharpe
- Lowest max drawdown: -26.8%
- Highly stable, mechanical
- Minimal turnover (11.5 trades/2-year period)
- Works in volatile regimes

**Weaknesses**:
- Momentum-agnostic (may hold falling assets if vol low)
- Concentration risk if many assets achieve low vol
- Whipsaws if vol spikes

**Test Metrics (2024-2025)**:
| Metric | Value |
|--------|-------|
| CAGR | 90.4% |
| Sharpe | 1.40 |
| Sortino | 2.88 |
| Max Drawdown | -26.8% |
| Profit Factor | 1.31 |
| Win Rate | 53.6% |
| Avg Trade | 6.8% |
| Trades | 11.5 |
| Exposure | 100% |
| Total Return | 263% |

---

### 5. **Momentum + Low Volatility Gate**
**Philosophy**: Momentum filter through a low-volatility screen.

**Implementation**:
```python
close = data.sel(field="close")
liquid = liquid_mask(data)
momentum = close / close.shift(60-days) - 1
realized = realized_volatility(data, 45-day lookback).where(liquid)
vol_rank = rank_as_percentile(realized)
return equal_weight_mask((momentum > 0) & (vol_rank <= 0.40), liquid)
```

**Logic**:
- Entry: momentum positive (60-day returns > 0) AND volatility in bottom 40%
- Exit: momentum negative OR volatility spike above 40th percentile
- Equal-weight holdings
- Combines trending with stability

**Strengths**:
- Balances momentum and risk
- Medium-term momentum (60-day) reduces whipsaws
- Volatility filter catches stability-shifts
- Test CAGR: 34.2%, Sharpe: 0.84

**Weaknesses**:
- More complex logic, harder to diagnose
- May miss sustained momentum in high-vol assets
- Double-filter could be too restrictive in certain regimes

**Test Metrics (2024-2025)**:
| Metric | Value |
|--------|-------|
| CAGR | 34.2% |
| Sharpe | 0.84 |
| Max Drawdown | -38.6% |
| Profit Factor | 1.14 |
| Trades | 68.8 |
| Exposure | 88.8% |

---

### 6. **Cross-Sectional Momentum Long-Only**
**Philosophy**: Rank assets by long-term momentum, hold top 10%.

**Implementation**:
```python
close = data.sel(field="close")
liquid = liquid_mask(data)
momentum = (close / close.shift(180-days) - 1).where(liquid)
momentum_rank = rank_as_percentile(momentum)
return equal_weight_mask(momentum_rank > 0.90, liquid)
```

**Logic**:
- Calculate 180-day returns
- Rank each asset
- Hold top 10% (momentum_rank > 90th percentile) equal-weighted
- Binary inclusion

**Strengths**:
- Simple, replicable
- Long-term perspective reduces noise
- Typically profitable (20.3% CAGR in test)
- 1.0 exposure (always fully invested)

**Weaknesses**:
- Concentration (only ~7-8 assets in typical universe)
- Whipsaws on 180-day reversals
- May hold falling leaders
- High max drawdown: -60.4%

**Test Metrics (2024-2025)**:
| Metric | Value |
|--------|-------|
| CAGR | 20.3% |
| Sharpe | 0.63 |
| Max Drawdown | -60.4% |
| Profit Factor | 1.10 |
| Win Rate | 49.2% |
| Trades | 75 |
| Exposure | 100% |

---

## Part 2: Research Strategies (Experimental)

Research has been conducted on 10 additional experimental strategies. These are **not** in the default codebase but documented in `research_outputs/`.

### Research Strategy Performance Summary

| Name | Category | Test CAGR | Test Sharpe | Best Regime | Worst Regime |
|------|----------|-----------|------------|------------|--------------|
| MA 20/120 Trend | Trend Following | 22.0% | 0.63 | Bull | Sideways |
| Donchian Breakout 55 | Trend Following | -4.3% | 0.23 | Bull | Bear |
| TSMOM 90 | Trend Following | -6.0% | 0.18 | Bull | Sideways |
| XSMOM Top 10% | X-Sectional Mom | 20.3% | 0.63 | Bull | Sideways |
| Low Vol Carry | Volatility | 21.4% | 0.68 | Bull | Sideways |
| TSMOM 90 + Low-Vol Filter | Volatility | 34.2% | 0.84 | Bull | Bear |
| Persistent Low Vol 150/25 | Volatility | **90.4%** | **1.40** | Bull | Sideways |
| TSMOM 60 + Persistent Low-Vol Gate | Volatility | 59.2% | 1.26 | Bull | Sideways |
| XSMOM 180 Top 10% | X-Sectional Mom | 63.4% | 0.98 | Bull | Sideways |
| TSMOM 90 gated by BTC 200MA | Market Regime | 1.0% | 0.29 | Bull | Sideways |
| Alt Relative Strength Top 10% | Relative Strength | 16.3% | 0.59 | Bull | Sideways |

**Key Findings**:
- **Best performer**: Persistent Low Volatility (90.4% CAGR, 1.40 Sharpe, -26.8% max DD)
- **Worst performer**: Donchian Breakout 55 (-4.3% CAGR, -68.3% max DD)
- **Volatility-based strategies** dominate: top 5 performers are all volatility or vol-filtered approaches
- **Trend-following** approaches underperform or lose money in test period (likely bear-dominant period 2024-2025)

---

## Part 3: Shared Architecture & Components

All strategies use common building blocks from `q25_crypto/features.py` and `q25_crypto/portfolio.py`:

### Features (Technical Indicators)

**Momentum Score**
```
fast_MA = 10-day LWMA
slow_MA = 50-day LWMA
momentum = (fast / slow) - 1
Range: [-inf, +inf], typically [-0.3, +0.3]
```

**Trend Score**
```
medium_MA = 20-day LWMA
long_MA = 120-day LWMA
trend = (medium / long) - 1
Range: [-0.5, +0.5] typically
```

**Mean Reversion Score**
```
reference = 15-day SMA
reversion = -(close / reference - 1)
Positive when close < reference (oversold)
Negative when close > reference (overbought)
```

**Volatility Penalty**
```
tr = True Range (high - low)
volatility = tr / close
smoothed = 20-day LWMA(volatility)
Used to dampen scores in high-vol regimes
```

**Liquidity Score**
```
liquid_base = is_liquid field (0 or 1)
volume_boost = 1 + 0.15 × (recent_vol_5day / baseline_vol_60day)
score = liquid_base × volume_boost
Amplifies liquid, high-volume assets
```

### Portfolio Utilities

**normalize_long_only(score, liquid_mask)**
- Ensures weights sum to 100%
- Forces holdings to liquid assets
- Handles NaN and negative scores
- Falls back to equal-weight if all scores < 0

**blend_scores(score1, score2, weights=(w1, w2))**
- Linear combination: w1 × score1 + w2 × score2
- Used by ensemble for regime-weighted blending

**_rank_pct_by_asset(score)**
- Ranks each asset's score as percentile (0-1)
- Used for signal-based inclusion (e.g., "top 10%")

---

## Part 4: Key Insights & Recommendations

### What Works (Test Period 2024-2025):

1. **Volatility-Based Strategies Dominate**
   - Persistent Low Vol: 90% CAGR
   - TSMOM 60 + Persistent Low Vol Gate: 59% CAGR
   - TSMOM 90 + Low Vol Filter: 34% CAGR
   - **Why**: 2024-2025 was a volatile bear/choppy period; avoiding volatility = profit

2. **Cross-Sectional Momentum 180-day Outperforms**
   - 63.4% CAGR vs. 20.3% CAGR (short-term CSM)
   - Longer lookback reduces noise, catches sustained trends

3. **Equal-Weight Allocation > Momentum-Weighted (in this period)**
   - Persistent Low Vol (equal-weight, 90% CAGR) >> Momentum (score-weighted, research shows underperformance)
   - May reflect period where "boring beats flashy"

### What Doesn't Work (Test Period):

1. **Pure Trend-Following Strategies**
   - MA 20/120: +22% (barely positive)
   - TSMOM 90: -6% (negative)
   - Donchian Breakout: -4.3% (negative)
   - **Why**: Test period was bear/choppy; trends didn't persist

2. **Market Regime Gating (BTC 200MA)**
   - Only +1% CAGR
   - Regime gate may have been too restrictive

3. **Mean Reversion Standalone**
   - Not researched in isolation on test, but theory suggests: struggles in trending markets

### Market Regime Analysis

**Bull Regime**:
- All strategies perform better in bull regimes (best performance)
- Momentum strategies have edge

**Sideways Regime**
- Second-best for most strategies
- Mean reversion should theoretically shine (but not tested)

**Bear Regime**
- Most strategies suffer
- Volatility-based strategies hold up better
- Trend-following strategies collapse (buying falling trends)

---

## Part 5: Architecture Recommendations

### For Immediate Improvement (low risk):

1. **Switch default strategy from Ensemble to Persistent Low Vol**
   - Current: Ensemble (unknown test performance)
   - Recommendation: Persistent Low Vol (90% CAGR, 1.40 Sharpe)
   - Risk: Concentration if only few assets have low vol

2. **Consider TSMOM 60 + Persistent Low Vol Gate**
   - Middle-ground: captures momentum + stability
   - Test results: 59% CAGR, 1.26 Sharpe
   - Better upside than pure vol strategy, similar drawdown

3. **Test Ensemble on Research Data**
   - Current Ensemble code exists but wasn't included in research report
   - Need backtests to validate current regime-awareness logic

### For Medium-Term Experimentation:

1. **Extend Lookback on Cross-Sectional Momentum**
   - 180-day CSM (63% CAGR) >> 90-day CSM (20% CAGR)
   - Test 220-day, 250-day to optimize

2. **Add Mean Reversion in Sideways Detection**
   - Ensemble partially does this, but could formalize
   - Detect sideways periods → boost mean reversion weight

3. **Hybrid: Vol Filter + Momentum Gate**
   - Only buy momentum signals if vol < 40th percentile
   - Already exists as "TSMOM 90 + Low Vol Filter" (34% test CAGR)

### For Risk Management:

1. **Add Max Volatility Cutoff**
   - Highest max drawdown: Donchian Breakout (-68%)
   - Lowest: Persistent Low Vol (-27%)
   - Consider hard stops at vol > Nth percentile

2. **Position Sizing by Vol**
   - Currently: equal-weight after binary inclusion
   - Alternative: size inversely by asset volatility

3. **Diversification Across Regime Signals**
   - Currently: one strategy rule
   - Alternative: ensemble of 2-3 strategies with cross-correlation hedge

---

## Part 6: Data Quality & Assumptions

### Cached Data
- 76 crypto assets in Quantiacs universe
- OHLCV data: open, high, low, close, volume, is_liquid
- Date range: 2013-04-01 through 2026-06-12
- Missing: funding rates, order book depth, exchange-specific gaps

### Backtest Assumptions
- **Cost**: 0.15% one-way turnover (fee + slippage)
- **Execution**: close-to-close daily
- **Entry/Exit**: decided from prior close, executed next day open
- **Survivorship**: only assets that exist throughout period (may bias upward)
- **Liquidity**: only is_liquid=1 assets

### Test Period Splits
- **Train**: 2018-2022 (bull + bear + sideways)
- **Validation**: 2023 (bear)
- **Test**: 2024-2025 (choppy/sideways with sharp bear moves)

### Known Limitations
1. No funding rates → can't test perpetual arb strategies
2. No order book depth → can't measure slippage accurately
3. Survivorship bias → assets that survived may outperform
4. Listing effects → newer assets get added to universe over time

---

## Part 7: Files Reference

### Core Code
- `strategy.py` — main submission entrypoint, strategy selector
- `q25_crypto/strategies.py` — 6 core strategies
- `q25_crypto/features.py` — technical indicators
- `q25_crypto/portfolio.py` — portfolio utilities

### Research Outputs
- `research_outputs/research_report.md` — detailed report on 10 experimental strategies
- `research_outputs/research_summary.json` — machine-readable version
- `research_outputs/strategy_metrics_by_split.csv` — performance by train/val/test split
- `research_outputs/*_regimes.csv` — regime-specific metrics per strategy
- `research_outputs/*_sensitivity.csv` — parameter tuning results

### Data
- `data-cache/` — local Quantiacs API cache (encrypted)
- `fractions.nc.gz` — possibly cached NetCDF data

---

## Part 8: Quick Reference - Strategy Selection Guide

### If You Want...

**Maximum Returns** → `persistent_low_volatility_long_only` (90% CAGR, 264% return)

**Best Risk-Adjusted** → `persistent_low_volatility_long_only` (1.40 Sharpe)

**Lowest Drawdown** → `persistent_low_volatility_long_only` (-27% max)

**Trend-Capture** → `momentum_long_only` (but underperforms in 2024-2025)

**Balanced** → `momentum_low_volatility_long_only` (34% CAGR, 0.84 Sharpe)

**Concentration Risk / Simplicity** → `cross_sectional_momentum_long_only` (20% CAGR)

**Regime Awareness (Theoretical)** → `ensemble_long_only` (needs backtesting)

---

## Conclusions

1. **Volatility-based strategies dominate the 2024-2025 test period** - this is likely a choppy/bear-market artifact.

2. **The Persistent Low Volatility strategy is the strongest on historical test data** with 90% CAGR, 1.40 Sharpe, and -27% max drawdown.

3. **The current default (Ensemble) has not been validated against the research test period** - recommend backtesting or switching to a proven performer.

4. **Mean reversion strategies are under-explored** - no standalone backtest on the research data; only composite uses.

5. **Longer lookback horizons outperform** - 180-day CSM beats 90-day CSM; 120-day slow MA beats 60-day in trend strategies.

6. **All strategies are long-only and liquidity-constrained**, limiting diversification - consider adding short legs or alternative universes.

7. **The 0.15% turnover cost is significant** - strategies with high trade counts (TSMOM 90: 69 trades) are more sensitive to slippage assumptions.

**Next Steps**:
- [ ] Decide on primary strategy (recommend Persistent Low Vol for deployment)
- [ ] Backtest Ensemble on research period to validate regime detection
- [ ] Test parameter variations (lookback periods, thresholds)
- [ ] Consider risk management enhancements (max vol cutoffs, position sizing by vol)
- [ ] Monitor live performance after deployment

---

**Report Version**: 1.0  
**Data Source**: Quantiacs research_outputs/  
**Contact**: Internal research team
