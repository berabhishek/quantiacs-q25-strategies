# 📊 Quantiacs Q25 Crypto Strategies - Analysis Index

## 🎯 What You'll Find Here

This analysis package contains **three comprehensive documents** and references to the **research data** that support informed strategy selection and deployment decisions.

---

## 📄 Main Documents

### 1. **STRATEGIES_STATUS_REPORT.md** (546 lines, 18 KB)
**The comprehensive reference** - Read this for deep understanding

**Contents**:
- Executive summary of 6 core strategies
- Detailed breakdown of each strategy (philosophy, code, strengths, weaknesses, test metrics)
- 10 experimental strategies from research
- Shared architecture and components
- Key insights and recommendations
- Architecture recommendations for improvement
- Data quality and assumptions
- Detailed conclusions with next steps

**Best for**: 
- ✅ Understanding how each strategy works
- ✅ Why certain strategies outperform
- ✅ Data quality and backtest assumptions
- ✅ Detailed risk analysis
- ✅ Strategic decision-making

**When to read**: First time, background research, detailed analysis

---

### 2. **STRATEGIES_QUICK_REFERENCE.md** (216 lines, 9 KB)
**The decision-maker's guide** - Use this for quick lookup

**Contents**:
- Performance comparison table (6 strategies)
- Philosophy comparison matrix
- Returns distribution
- Strategy switching commands
- Regime performance breakdown
- Risk/mitigation table
- Use-case recommendations
- Signal components cheat sheet
- Next steps and action items

**Best for**:
- ✅ Quick performance lookup
- ✅ Strategy selection by use case
- ✅ Risk assessment
- ✅ Regime-aware decision making
- ✅ Command reference

**When to use**: Daily reference, quick decisions, deployment planning

---

### 3. **This File: ANALYSIS_INDEX.md**
**The navigation guide** - You are reading it now

---

## 🎯 Quick Decision Matrix

### "I have 2 minutes. What should I do?"

| Your Goal | Recommendation | Sharpe Ratio | Risk |
|-----------|---|----------|------|
| **Max Returns** | Persistent Low Vol | 1.40 | Low |
| **Best Risk-Adjusted** | Persistent Low Vol | 1.40 | Low |
| **Trends + Stability** | TSMOM 60 + Low Vol Gate | 1.26 | Med |
| **Sustained Trends** | XSMOM 180 Top 10% | 0.98 | High |
| **Balanced** | Momentum + Low Vol | 0.84 | Med |
| **Simplest** | Persistent Low Vol | 1.40 | Low |

**→ Deploy Persistent Low Volatility** unless you have specific trend exposure needs.

---

### "I have 30 minutes. What should I know?"

1. Read **STRATEGIES_QUICK_REFERENCE.md** (7 min)
2. Check the Performance Comparison table (2 min)
3. Review Recommendations by Use Case (5 min)
4. Scan Next Steps section (2 min)
5. Keep it bookmarked for daily reference (0 min, but invaluable)

**Total**: 16 minutes + bookmarking

---

### "I have 2 hours. Deep dive."

1. Read **STRATEGIES_STATUS_REPORT.md** - Part 1 to 4 (45 min)
2. Read **STRATEGIES_QUICK_REFERENCE.md** (15 min)
3. Review research data in `research_outputs/` (20 min)
4. Make deployment decision (10 min)
5. Plan implementation (20 min)
6. Document learnings (10 min)

**Total**: ~120 minutes for full understanding

---

## 📊 Performance Summary at a Glance

### Top 3 Performers (Test 2024-2025)

| Rank | Strategy | CAGR | Sharpe | Max DD | Recommendation |
|------|----------|------|--------|--------|-----------------|
| 🥇 | Persistent Low Vol | 90.4% | 1.40 | -26.8% | **DEPLOY NOW** |
| 🥈 | XSMOM 180 Top 10% | 63.4% | 0.98 | -56.2% | High upside, high risk |
| 🥉 | TSMOM 60 + Low Vol Gate | 59.2% | 1.26 | -32.2% | Good middle ground |

### All 6 Core Strategies

```
Strategy                          CAGR      Sharpe    Max DD      Status
────────────────────────────────────────────────────────────────────────
✅ Persistent Low Volatility     90.4%      1.40      -26.8%      PROVEN
⭐ TSMOM 60 + Low Vol Gate       59.2%      1.26      -32.2%      PROVEN
✅ XSMOM 180 Top 10%             63.4%      0.98      -56.2%      PROVEN
⚡ Momentum + Low Volatility     34.2%      0.84      -38.6%      PROVEN
📊 Cross-Sectional Momentum      20.3%      0.63      -60.4%      PROVEN
❓ Ensemble (DEFAULT)            UNKNOWN    UNKNOWN   UNKNOWN     NEEDS VALIDATION
```

---

## 🔍 Data Sources Used

All analysis is based on:
- **Repository**: `research_outputs/` directory
- **Research Report**: `research_outputs/research_report.md` (detailed analysis)
- **Summary Data**: `research_outputs/research_summary.json` (10 strategies)
- **Metrics**: `research_outputs/strategy_metrics_by_split.csv` (quantitative results)
- **Sensitivity**: `research_outputs/*_sensitivity.csv` (parameter tuning)

**Period**: Test results 2024-01-01 through 2025-12-31 (2-year period)
**Universe**: 76 Quantiacs crypto assets
**Method**: Daily close-to-close returns, long-only, liquid-only, 0.15% turnover cost

---

## 🚀 Next Actions

### Immediate (Today)

- [ ] **Read**: `STRATEGIES_QUICK_REFERENCE.md` (decide which strategy to deploy)
- [ ] **Option A**: Deploy `persistent_low_volatility_long_only` (recommended)
- [ ] **Option B**: Backtest `ensemble_long_only` first, then decide

### Short-term (This Week)

- [ ] **Validation**: If deploying, run backtest with live data
- [ ] **Monitoring**: Set up performance dashboard
- [ ] **Documentation**: Update deployment docs with strategy choice
- [ ] **Testing**: Small live allocation ($) to test execution

### Medium-term (This Month)

- [ ] **Optimization**: Test parameter variations (lookback periods)
- [ ] **Risk Management**: Add max volatility cutoffs
- [ ] **Diversification**: Consider running 2 complementary strategies

### Long-term (Next Quarter)

- [ ] **Enhancement**: Develop mean reversion standalone strategy
- [ ] **Research**: Explore short selling / pair trading
- [ ] **Expansion**: Test on additional asset classes
- [ ] **Learning**: Document live performance vs. backtest

---

## 💡 Key Insights (Summary)

1. **Volatility-based strategies dominate** the 2024-2025 test period
   - Persistent Low Vol: 90% CAGR
   - Volatility filtering is powerful
   - Suggests period was choppy/uncertain

2. **Trend-following underperforms** in the test period
   - MA 20/120: only +22% CAGR
   - TSMOM 90: negative returns
   - Suggests bear-dominated or choppy trends

3. **Longer lookbacks outperform** shorter ones
   - 180-day CSM > 90-day CSM
   - 120-day slow MA > 60-day MA
   - Reduces noise, captures true trends

4. **Equal-weight beats score-weighting** in this period
   - Binary inclusion strategies perform better
   - Suggests sector/asset selection > position sizing

5. **The Ensemble strategy lacks validation**
   - Default choice but untested in research period
   - Needs independent backtesting before trust

6. **Low volatility has lowest drawdown**
   - Max DD: -26.8% vs -60%+ for momentum strategies
   - Important for risk-averse deployment

7. **Trade frequency matters**
   - Persistent Low Vol: 11.5 trades (low slippage risk)
   - TSMOM strategies: 69 trades (high slippage risk)
   - Consider transaction costs when choosing

---

## 📚 File Structure

```
Repository Root
├── strategy.py                              ← Main entry point
├── q25_crypto/
│   ├── strategies.py                        ← 6 core strategies
│   ├── features.py                          ← Technical indicators
│   └── portfolio.py                         ← Portfolio utilities
├── research_outputs/
│   ├── research_report.md                   ← Detailed experimental strategies
│   ├── research_summary.json                ← Machine-readable summary
│   ├── strategy_metrics_by_split.csv        ← Performance by train/val/test
│   └── *_sensitivity.csv                    ← Parameter tuning results
├── data-cache/                              ← Local Quantiacs data cache
│
├── STRATEGIES_STATUS_REPORT.md              ← Full analysis (you should read)
├── STRATEGIES_QUICK_REFERENCE.md            ← Quick lookup (bookmark this)
├── ANALYSIS_INDEX.md                        ← This file (navigation)
└── README.md                                ← Original repo info
```

---

## ❓ FAQ

**Q: Which strategy should I deploy right now?**  
A: **Persistent Low Volatility** - 90.4% CAGR, 1.40 Sharpe, -26.8% max DD. Proven performer with lowest drawdown.

**Q: Why isn't the default Ensemble strategy being recommended?**  
A: It hasn't been backtested in the research period. Theory is good (regime-blending), but empirical validation is missing. Backtest it first.

**Q: What if I want trend exposure?**  
A: Deploy **XSMOM 180 Top 10%** (63% CAGR, 0.98 Sharpe) or **TSMOM 60 + Low Vol Gate** (59% CAGR, 1.26 Sharpe). Both capture trends better.

**Q: What's the biggest risk?**  
A: High drawdowns in strong bear markets. Max DD ranges from -26% (Low Vol) to -68% (Donchian Breakout). Consider position sizing.

**Q: Can I run multiple strategies together?**  
A: Yes, but they're correlated (same crypto universe). Better to run different asset classes or add short legs.

**Q: What about mean reversion?**  
A: Only used as component in Ensemble. Standalone strategy not backtested in research period. Likely profitable in choppy/sideways markets.

**Q: How do I switch strategies?**  
A: Set environment variable: `export QNT_STRATEGY_MODE=persistent_low_volatility_long_only && python strategy.py`

**Q: How often are strategies rebalanced?**  
A: Daily at close. Positions entered at next day's open. All backtests assume daily rebalancing.

**Q: What's the transaction cost assumption?**  
A: 0.15% one-way turnover. This covers both fees (0.05%) and slippage (0.10%). Higher for high-turnover strategies.

---

## 📞 Support & Questions

**For strategy questions**: See `STRATEGIES_STATUS_REPORT.md` Part 1-4

**For quick lookups**: See `STRATEGIES_QUICK_REFERENCE.md`

**For detailed analysis**: See `research_outputs/research_report.md`

**For code questions**: See `q25_crypto/strategies.py` docstrings and feature implementations

---

## 📋 Version Info

- **Analysis Date**: 2026-06-13
- **Data Through**: 2025-12-31
- **Test Period**: 2024-01-01 to 2025-12-31
- **Strategies Analyzed**: 6 core + 10 research variants = 16 total
- **Status**: Complete, ready for decision-making

---

**🎯 TL;DR**: Read the QUICK REFERENCE. Deploy Persistent Low Volatility. Monitor performance. Plan next experiments.

---

*Last updated: 2026-06-13*  
*Questions? See the relevant reference document above.*
