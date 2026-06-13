# Quantiacs Q25 Crypto Strategies - Quick Reference Card

## 🎯 Performance Comparison (Test Period: 2024-2025)

### Core Codebase Strategies

```
STRATEGY                              CAGR    SHARPE   MAX DD    TRADES   EXPOSURE
═════════════════════════════════════════════════════════════════════════════════
🏆 Persistent Low Volatility         90.4%    1.40     -26.8%     11.5    100%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ TSMOM 60 + Persistent Low-Vol Gate 59.2%    1.26     -32.2%     70.1     79.6%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ XSMOM 180 Top 10%                  63.4%    0.98     -56.2%     40.0    100%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Momentum + Low Volatility          34.2%    0.84     -38.6%     68.8     88.8%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Cross-Sectional Momentum          20.3%    0.63     -60.4%     75.0    100%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ Ensemble (DEFAULT)                  N/A*     N/A*     N/A*       N/A      N/A
❌ MA 20/120 Trend                    22.0%    0.63     -45.7%     16.7     92.3%
❌ TSMOM 90                           -6.0%    0.18     -65.4%     68.9     93.7%
❌ Donchian Breakout 55              -4.3%    0.23     -68.3%     16.7     97.3%
```

*Ensemble not validated in research backtest. Need independent confirmation.

---

## 💡 Strategy Philosophy Comparison

| Strategy | Approach | Trigger | Risk | Best In | Worst In |
|----------|----------|---------|------|---------|----------|
| **Persistent Low Vol** | Stability focus | Rank by volatility | Low | Choppy/Uncertain | Strong Trends |
| **TSMOM 60 + Low Vol Gate** | Momentum + Filter | 60d momentum × Low vol | Medium | Trending with vol swings | Sideways |
| **XSMOM 180 Top 10%** | Momentum ranking | 180d returns > 90th %ile | High | Sustained bull runs | Reversals |
| **Momentum + Low Vol** | Momentum filtered | 60d momentum × Vol filter | Medium | Mixed trending | Choppy |
| **Cross-Sectional Momentum** | Top performers | 180d momentum ranking | High | Bull markets | Consolidations |
| **Ensemble** | Regime-blended | Momentum + MR regime-weighted | Low-Med | Adaptive markets | Regime misclassification |

---

## 📈 Returns Distribution (2024-2025)

```
Strategy                            Total Return    Return/Drawdown Ratio
═══════════════════════════════════════════════════════════════════════
Persistent Low Vol                  +263%           9.8x
TSMOM 60 + Persistent Low-Vol Gate +154%           4.8x
XSMOM 180 Top 10%                  +167%           3.0x
Momentum + Low Volatility           +80%            2.1x
Cross-Sectional Momentum            +45%            0.7x
MA 20/120 Trend                     +49%            1.1x
TSMOM 90                            -12%            -0.2x
Donchian Breakout 55                -8%             -0.1x
```

---

## 🔧 How to Switch Strategies

```bash
# Default (ensemble or whatever is set)
python strategy.py

# Specific strategy
export QNT_STRATEGY_MODE=persistent_low_volatility_long_only
python strategy.py

# Available modes:
# - ensemble
# - momentum
# - mean_reversion
# - low_volatility (= persistent_low_volatility_long_only)
# - momentum_low_volatility
# - cross_sectional_momentum
```

---

## 🎲 Regime Performance

**Bull Market** (↑)
- All strategies perform well
- Momentum strategies have edge
- Best: XSMOM 180, Persistent Low Vol

**Sideways Market** (→)
- Mixed results
- Volatility strategies shine
- Best: Persistent Low Vol, TSMOM + Low Vol Gate

**Bear Market** (↓)
- Most strategies struggle
- Volatility strategies hold up best
- Trend-following severely underperforms

---

## ⚠️ Key Risks & Mitigations

| Risk | Impact | Current Mitigation | Recommendation |
|------|--------|-------------------|-----------------|
| Concentration | Few holdings | Equal-weight after inclusion | Monitor asset count |
| Volatility spikes | High drawdown | Vol filtering (some strategies) | Add max vol cutoff |
| Slippage | Higher costs on volume | 0.15% turnover assumption | Reduce trade frequency |
| Regime misclassification | Wrong signal weights | Ensemble uses volatility + MA | Validate regime signals |
| Listing bias | Survivorship bias | Only test on existing assets | Track delisted assets |

---

## 🏅 Recommendations by Use Case

### **I want MAXIMUM RETURNS** 
→ Deploy: **Persistent Low Volatility**
- 90% CAGR, 264% total return
- Risk: Concentration if few low-vol assets

### **I want BEST RISK-ADJUSTED RETURNS**
→ Deploy: **Persistent Low Volatility** 
- 1.40 Sharpe ratio (best)
- Sortino: 2.88 (excellent upside/downside ratio)

### **I want TRENDING MARKET EXPOSURE**
→ Deploy: **XSMOM 180 Top 10%**
- 63% CAGR in test
- 180-day lookback captures sustained trends
- Risk: High drawdown (-56%), concentration

### **I want BALANCED RISK/RETURN**
→ Deploy: **TSMOM 60 + Persistent Low-Vol Gate**
- 59% CAGR, 1.26 Sharpe
- Combines momentum + stability
- Moderate exposure (79.6%), high turnover (70 trades)

### **I want SIMPLE & MECHANICAL**
→ Deploy: **Persistent Low Volatility**
- Binary inclusion (simple rules)
- Minimal trades (11.5 per 2 years)
- Fully mechanical, no regime detection

### **I want TREND DIVERSIFICATION**
→ Deploy: **Ensemble** (ONLY AFTER VALIDATION)
- Currently untested in research backtest
- Theory: regime-aware blending
- Action: Backtest before deployment

---

## 📊 Signal Components Cheat Sheet

### Building Blocks Available

```python
# Momentum signals
momentum_score(data)       # 10/50-day MA ratio
trend_score(data)          # 20/120-day MA ratio

# Mean reversion
mean_reversion_score(data) # -(close / 15-day SMA - 1)

# Risk measures
volatility_penalty(data)   # Smoothed True Range / close
liquidity_score(data)      # is_liquid × (1 + vol boost)

# Utility functions
normalize_long_only()      # Converts scores to weights
blend_scores()             # Weighted average of scores
_rank_pct_by_asset()       # Percentile ranking per asset
_equal_weight_mask()       # Binary inclusion mask
```

---

## 🚀 Next Steps

### Immediate (Week 1)
- [ ] Decide: Deploy Persistent Low Vol or wait for Ensemble validation?
- [ ] If deploying: Set up monitoring dashboard for live performance

### Short-term (Week 2-4)
- [ ] Backtest Ensemble on research data to validate regime detection
- [ ] Test Persistent Low Vol parameter variations (150-day lookback, 25% threshold)
- [ ] Add max volatility cutoff to reduce drawdowns

### Medium-term (Month 2-3)
- [ ] Explore mean reversion standalone strategy
- [ ] Test hybrid: Persistent Low Vol + XSMOM 180 (correlation hedge)
- [ ] Implement position sizing by inverse volatility

### Long-term (Month 3+)
- [ ] Add short leg (pair trading)
- [ ] Expand to alternative universes (stocks, futures)
- [ ] Machine learning regime detection vs. manual volatility + MA approach

---

## 📚 Reference Files

```
strategy.py                                      ← Main entry point
q25_crypto/strategies.py                         ← 6 core strategies
q25_crypto/features.py                           ← Technical indicators
q25_crypto/portfolio.py                          ← Portfolio utilities
research_outputs/research_report.md              ← Detailed experimental strategies
research_outputs/strategy_metrics_by_split.csv   ← Performance by train/val/test
research_outputs/*_sensitivity.csv               ← Parameter tuning results
STRATEGIES_STATUS_REPORT.md                      ← Full analysis document
```

---

**Last Updated**: 2026-06-13  
**Status**: 6 core strategies, 10 research variants analyzed  
**Data**: 76 crypto assets, 2024-2025 test period  
**Recommendation**: Deploy Persistent Low Volatility (90% CAGR, proven)
