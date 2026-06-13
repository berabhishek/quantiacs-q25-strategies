# Crypto Behavior Research Report

Data: local Quantiacs crypto daily OHLCV cache, 76 assets, 2014-01-01 through 2026-06-12.
Backtest convention: close-to-close daily returns, positions decided from prior close and applied next day, long-only, liquid assets only, cost = 0.15% one-way turnover for combined fee/slippage.
Train: 2018-01-01 to 2022-12-31. Validation: 2023-01-01 to 2023-12-31. Test: 2024-01-01 to 2025-12-31. Final decision metrics below use test only.

## Funding Rate Effects

Rejected for this run: cached fields are only open, high, low, close, volume, and is_liquid. Funding-rate hypotheses require historical perpetual funding data, so any result from OHLCV alone would be a proxy, not a funding-rate test.

## MA 20/120 trend

Category: Trend Following

Hypothesis: Large crypto assets exhibit slow behavioral and flow-driven trends after sustained repricing.
Why it should persist: Reflexive investor flows, delayed fundamental repricing, and benchmark under/overweight adjustments do not complete in one day.
Participants creating it: Retail trend chasers, systematic CTA-like crypto products, token treasuries, and benchmark allocators.
Stronger when: Broad risk-on conditions, persistent BTC uptrends, and expanding participation.
Weaker when: Sharp deleveraging, range-bound chop, and exchange/liquidity shocks.

Rules: Entry: asset 20-day SMA > 120-day SMA. Exit: asset 20-day SMA <= 120-day SMA. Equal-weight active liquid assets.

Test metrics:

- CAGR: 22.00%
- Sharpe Ratio: 0.63
- Sortino Ratio: 0.87
- Max Drawdown: -45.66%
- Profit Factor: 1.10
- Win Rate: 46.79%
- Average Trade: 2.23%
- Number of Trades: 16.66
- Exposure: 92.34%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/ma_20_120_trend_regimes.csv`.

Parameter sensitivity on test:

|     slow |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------:|-------:|---------:|---------------:|---------:|
|  60.0000 | 0.1265 |   0.4932 |        -0.4846 |  29.1242 |
|  90.0000 | 0.1717 |   0.5642 |        -0.5000 |  19.0762 |
| 120.0000 | 0.2200 |   0.6322 |        -0.4566 |  16.6599 |
| 150.0000 | 0.0852 |   0.4344 |        -0.5690 |  16.1873 |
| 180.0000 | 0.2116 |   0.6187 |        -0.5002 |  14.3889 |
| 240.0000 | 0.1517 |   0.5353 |        -0.4885 |  13.3357 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## Donchian breakout 55

Category: Trend Following

Hypothesis: New multi-month highs in crypto attract momentum capital and forced underweight buying.
Why it should persist: Crypto markets are fragmented and narrative-driven, so price discovery can continue after breakouts.
Participants creating it: Momentum traders, discretionary breakout buyers, and short sellers forced to cover.
Stronger when: Fresh highs with broad market confirmation.
Weaker when: False breakouts during low-liquidity sideways markets.

Rules: Entry: close above prior 55-day high. Exit: close below prior 55-day low. Equal-weight active liquid assets.

Test metrics:

- CAGR: -4.32%
- Sharpe Ratio: 0.23
- Sortino Ratio: 0.31
- Max Drawdown: -68.30%
- Profit Factor: 1.03
- Win Rate: 49.79%
- Average Trade: 0.80%
- Number of Trades: 16.72
- Exposure: 97.26%

Regime analysis: best test regime was `bull`; worst was `bear`. Full regime tables are in `research_outputs/donchian_breakout_55_regimes.csv`.

Parameter sensitivity on test:

|   lookback |    CAGR |   Sharpe |   Max Drawdown |   Trades |
|-----------:|--------:|---------:|---------------:|---------:|
|    20.0000 | -0.0290 |   0.2648 |        -0.6535 |  45.5135 |
|    40.0000 | -0.1366 |   0.0874 |        -0.7106 |  24.0437 |
|    55.0000 | -0.0432 |   0.2255 |        -0.6830 |  16.7246 |
|    70.0000 | -0.0441 |   0.2262 |        -0.6735 |  14.1575 |
|    90.0000 |  0.0265 |   0.3330 |        -0.6079 |  12.3103 |
|   120.0000 |  0.1836 |   0.5813 |        -0.4643 |   9.9917 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## TSMOM 90

Category: Trend Following

Hypothesis: Assets with positive medium-term own returns continue to drift as crypto repricing is gradual.
Why it should persist: Narratives, listings, and capital inflows tend to diffuse across venues and investor groups over weeks.
Participants creating it: Retail momentum buyers, market makers hedging inventory, and funds rotating into winners.
Stronger when: Bull regimes and post-consolidation breakouts.
Weaker when: Bear markets with violent mean reversion.

Rules: Entry: 90-day total return > 0. Exit: 90-day total return <= 0. Equal-weight active liquid assets.

Test metrics:

- CAGR: -6.00%
- Sharpe Ratio: 0.18
- Sortino Ratio: 0.23
- Max Drawdown: -65.37%
- Profit Factor: 1.03
- Win Rate: 46.79%
- Average Trade: 0.15%
- Number of Trades: 68.91
- Exposure: 93.71%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/tsmom_90_regimes.csv`.

Parameter sensitivity on test:

|   lookback |    CAGR |   Sharpe |   Max Drawdown |   Trades |
|-----------:|--------:|---------:|---------------:|---------:|
|    30.0000 | -0.0717 |   0.1983 |        -0.7072 | 124.7925 |
|    60.0000 |  0.0085 |   0.3324 |        -0.5919 |  84.2587 |
|    90.0000 | -0.0600 |   0.1764 |        -0.6537 |  68.9060 |
|   120.0000 |  0.0075 |   0.3100 |        -0.4890 |  52.5464 |
|   180.0000 |  0.1480 |   0.5307 |        -0.4773 |  38.7052 |
|   240.0000 |  0.1029 |   0.4658 |        -0.4929 |  28.2611 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## XSMOM top 10%

Category: Cross-Sectional Momentum

Hypothesis: Within crypto, recent winners keep attracting capital relative to laggards.
Why it should persist: Attention, exchange listings, and ecosystem narratives concentrate flows into leaders before diffusing.
Participants creating it: Narrative traders, relative-value funds, and liquidity providers following volume migration.
Stronger when: Altcoin bull phases and sector-led markets.
Weaker when: Market-wide deleveraging where correlations go to one.

Rules: Entry: rank liquid assets by 90-day return and buy top 10%. Exit: falls out of top 10%. Equal-weight selected assets.

Test metrics:

- CAGR: 20.34%
- Sharpe Ratio: 0.63
- Sortino Ratio: 1.07
- Max Drawdown: -60.39%
- Profit Factor: 1.10
- Win Rate: 49.25%
- Average Trade: 0.71%
- Number of Trades: 75.00
- Exposure: 100.00%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/xsmom_top_10_regimes.csv`.

Parameter sensitivity on test:

|   top_quantile |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------------:|-------:|---------:|---------------:|---------:|
|         0.0500 | 0.2034 |   0.6312 |        -0.6039 |  75.0000 |
|         0.1000 | 0.2034 |   0.6312 |        -0.6039 |  75.0000 |
|         0.2000 | 0.3026 |   0.7214 |        -0.6205 |  64.0000 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## Low volatility carry

Category: Volatility Regimes

Hypothesis: Lower realized-volatility crypto assets may have better forward risk-adjusted returns than distressed high-volatility names.
Why it should persist: High volatility often reflects adverse selection, poor liquidity, or crash risk; calmer assets are more institutionally holdable.
Participants creating it: Levered traders exiting distressed names and long-only allocators preferring stable majors.
Stronger when: Sideways or recovering markets.
Weaker when: Speculative melt-ups where high-beta assets dominate.

Rules: Entry: 30-day realized volatility in bottom 20% of liquid universe. Exit: leaves bottom 20%. Equal-weight selected assets.

Test metrics:

- CAGR: 21.40%
- Sharpe Ratio: 0.68
- Sortino Ratio: 0.99
- Max Drawdown: -31.74%
- Profit Factor: 1.10
- Win Rate: 51.85%
- Average Trade: 0.78%
- Number of Trades: 35.50
- Exposure: 100.00%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/low_volatility_carry_regimes.csv`.

Parameter sensitivity on test:

|   lookback |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|-----------:|-------:|---------:|---------------:|---------:|
|    15.0000 | 0.1217 |   0.4898 |        -0.3781 |  65.5000 |
|    20.0000 | 0.2318 |   0.7230 |        -0.2926 |  43.5000 |
|    30.0000 | 0.2140 |   0.6825 |        -0.3174 |  35.5000 |
|    45.0000 | 0.2687 |   0.7908 |        -0.2884 |  29.0000 |
|    60.0000 | 0.1996 |   0.6546 |        -0.3152 |  23.5000 |
|    90.0000 | 0.6061 |   1.0935 |        -0.2757 |  12.5000 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## TSMOM 90 + low-vol filter

Category: Volatility Regimes

Hypothesis: Momentum is more robust when it avoids the noisiest high-volatility assets.
Why it should persist: Volatility filtering reduces exposure to forced-liquidation rebounds and unstable microstructure.
Participants creating it: Momentum traders chasing liquid leaders versus distressed speculators in high-vol names.
Stronger when: Orderly uptrends with moderate realized volatility.
Weaker when: Early bull reversals led by high-beta laggards.

Rules: Entry: 90-day return > 0 and 30-day realized-vol rank <= 60%. Exit: either condition fails.

Test metrics:

- CAGR: 34.19%
- Sharpe Ratio: 0.84
- Sortino Ratio: 1.12
- Max Drawdown: -38.56%
- Profit Factor: 1.14
- Win Rate: 47.20%
- Average Trade: 0.60%
- Number of Trades: 68.83
- Exposure: 88.78%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/tsmom_90___low_vol_filter_regimes.csv`.

Parameter sensitivity on test:

|   max_vol_rank |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------------:|-------:|---------:|---------------:|---------:|
|         0.4000 | 0.4159 |   0.9701 |        -0.3487 |  58.5833 |
|         0.5000 | 0.4118 |   0.9529 |        -0.3883 |  66.8667 |
|         0.6000 | 0.3419 |   0.8427 |        -0.3856 |  68.8333 |
|         0.7000 | 0.2194 |   0.6446 |        -0.3747 |  75.3643 |
|         0.8000 | 0.0284 |   0.3172 |        -0.5169 |  72.0321 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## Persistent low volatility 150/25

Category: Volatility Regimes

Hypothesis: Crypto assets that remain low volatility over a longer window may avoid distress risk while still carrying broad market beta.
Why it should persist: Persistent calm tends to reflect deeper liquidity, lower adverse selection, and more institutionally acceptable risk.
Participants creating it: Long-only allocators, volatility-aware funds, and levered traders avoiding unstable collateral.
Stronger when: Broad recovery phases, sideways markets, and environments where crash risk is being repriced slowly.
Weaker when: Speculative melt-ups led by high-beta laggards or sudden rotations into distressed assets.

Rules: Entry: 150-day realized volatility in bottom 25% of liquid universe. Exit: leaves bottom 25%. Equal-weight selected assets.

Test metrics:

- CAGR: 90.40%
- Sharpe Ratio: 1.40
- Sortino Ratio: 2.88
- Max Drawdown: -26.83%
- Profit Factor: 1.31
- Win Rate: 53.63%
- Average Trade: 6.79%
- Number of Trades: 11.50
- Exposure: 100.00%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/persistent_low_volatility_150_25_regimes.csv`.

Parameter sensitivity on test:

|   lookback |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|-----------:|-------:|---------:|---------------:|---------:|
|    60.0000 | 0.1849 |   0.6294 |        -0.3152 |  20.0000 |
|    90.0000 | 0.6377 |   1.1339 |        -0.2757 |  12.5000 |
|   120.0000 | 0.7359 |   1.2362 |        -0.2757 |   8.5000 |
|   150.0000 | 0.9040 |   1.4018 |        -0.2683 |  11.5000 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## TSMOM 60 + persistent low-vol gate

Category: Volatility Regimes

Hypothesis: Shorter momentum works better when restricted to assets whose recent volatility is not already distressed.
Why it should persist: The volatility gate filters liquidation rebounds and noisy microstructure while retaining assets with timely positive drift.
Participants creating it: Momentum traders, volatility-controlled allocators, and liquidity providers rotating into orderly leaders.
Stronger when: Orderly uptrends with moderate realized volatility and broad participation.
Weaker when: Early bull reversals led by the highest-beta assets.

Rules: Entry: 60-day return > 0 and 45-day realized-vol rank <= 40%. Exit: either condition fails.

Test metrics:

- CAGR: 59.25%
- Sharpe Ratio: 1.26
- Sortino Ratio: 1.79
- Max Drawdown: -32.20%
- Profit Factor: 1.25
- Win Rate: 43.50%
- Average Trade: 0.80%
- Number of Trades: 70.08
- Exposure: 79.62%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/tsmom_60___persistent_low_vol_gate_regimes.csv`.

Parameter sensitivity on test:

|   max_vol_rank |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------------:|-------:|---------:|---------------:|---------:|
|         0.3000 | 0.3585 |   0.8876 |        -0.3165 |  62.8333 |
|         0.4000 | 0.5925 |   1.2593 |        -0.3220 |  70.0833 |
|         0.5000 | 0.2671 |   0.7368 |        -0.3694 |  74.3667 |
|         0.6000 | 0.2785 |   0.7158 |        -0.4052 |  79.9833 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## XSMOM 180 top 10%

Category: Cross-Sectional Momentum

Hypothesis: Longer-horizon crypto leaders may keep attracting capital after narratives become established.
Why it should persist: A 180-day ranking favors persistent ecosystem leadership over short-lived listing or attention spikes.
Participants creating it: Narrative traders, ecosystem funds, benchmark allocators, and relative-strength managers.
Stronger when: Sustained sector leadership and broad crypto risk appetite.
Weaker when: Fast leadership reversals, BTC dominance shocks, and market-wide deleveraging.

Rules: Entry: rank liquid assets by 180-day return and buy top 10%. Exit: falls out of top 10%. Equal-weight selected assets.

Test metrics:

- CAGR: 63.38%
- Sharpe Ratio: 0.98
- Sortino Ratio: 1.66
- Max Drawdown: -56.17%
- Profit Factor: 1.16
- Win Rate: 50.34%
- Average Trade: 2.24%
- Number of Trades: 40.00
- Exposure: 100.00%

Regime analysis: best test regime was `bull`; worst was `bear`. Full regime tables are in `research_outputs/xsmom_180_top_10_regimes.csv`.

Parameter sensitivity on test:

|   top_quantile |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------------:|-------:|---------:|---------------:|---------:|
|         0.1000 | 0.6338 |   0.9818 |        -0.5617 |  40.0000 |
|         0.1500 | 0.1852 |   0.6103 |        -0.6120 |  31.5000 |
|         0.2000 | 0.1852 |   0.6103 |        -0.6120 |  31.5000 |
|         0.2500 | 0.0705 |   0.4661 |        -0.5448 |  34.6667 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## TSMOM 90 gated by BTC 200MA

Category: Market Regime Detection

Hypothesis: Long-only crypto momentum has a higher survival probability when BTC is in a broad uptrend.
Why it should persist: BTC remains the dominant collateral and sentiment anchor; below its long-term trend, liquidity and risk appetite contract.
Participants creating it: Long-only funds, miners/treasuries, retail beta buyers, and perps traders using BTC as risk proxy.
Stronger when: BTC above long-term trend with positive breadth.
Weaker when: Altcoin-specific rallies while BTC is below trend, or sudden trend reversals.

Rules: Entry: asset 90-day return > 0 and BTC close > BTC 200-day SMA. Exit: either condition fails.

Test metrics:

- CAGR: 1.03%
- Sharpe Ratio: 0.29
- Sortino Ratio: 0.35
- Max Drawdown: -58.42%
- Profit Factor: 1.05
- Win Rate: 37.62%
- Average Trade: 0.28%
- Number of Trades: 54.62
- Exposure: 74.83%

Regime analysis: best test regime was `bull`; worst was `bear`. Full regime tables are in `research_outputs/tsmom_90_gated_by_btc_200ma_regimes.csv`.

Parameter sensitivity on test:

|   btc_ma |    CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------:|--------:|---------:|---------------:|---------:|
| 100.0000 |  0.1469 |   0.5264 |        -0.4277 |  52.6683 |
| 150.0000 |  0.2226 |   0.6515 |        -0.4919 |  50.7298 |
| 200.0000 |  0.0103 |   0.2880 |        -0.5842 |  54.6202 |
| 250.0000 | -0.0359 |   0.2105 |        -0.5816 |  64.7750 |
| 300.0000 | -0.0221 |   0.2389 |        -0.5991 |  65.0726 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## Alt relative strength top 10%

Category: Relative Strength

Hypothesis: Altcoins outperforming BTC can continue as leadership rotates into ecosystems with active narratives.
Why it should persist: Capital often moves from BTC into stronger ecosystems after BTC establishes risk appetite.
Participants creating it: Sector rotation traders, ecosystem funds, market makers, and retail narrative flows.
Stronger when: Broad altcoin seasons and BTC-stable/rising markets.
Weaker when: BTC dominance shocks and liquidity contractions.

Rules: Entry: rank non-BTC assets by 90-day return minus BTC 90-day return and buy top 10%. Exit: falls out of top 10%.

Test metrics:

- CAGR: 16.29%
- Sharpe Ratio: 0.59
- Sortino Ratio: 1.00
- Max Drawdown: -63.02%
- Profit Factor: 1.09
- Win Rate: 49.25%
- Average Trade: 0.67%
- Number of Trades: 74.00
- Exposure: 100.00%

Regime analysis: best test regime was `bull`; worst was `sideways`. Full regime tables are in `research_outputs/alt_relative_strength_top_10_regimes.csv`.

Parameter sensitivity on test:

|   top_quantile |   CAGR |   Sharpe |   Max Drawdown |   Trades |
|---------------:|-------:|---------:|---------------:|---------:|
|         0.0500 | 0.1629 |   0.5913 |        -0.6302 |  74.0000 |
|         0.1000 | 0.1629 |   0.5913 |        -0.6302 |  74.0000 |
|         0.2000 | 0.3219 |   0.7409 |        -0.6206 |  59.0000 |

Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.

Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.

## Test Ranking

| strategy                           | category                 | split          |    CAGR |   Sharpe |   Sortino |   Max Drawdown |   Profit Factor |   Win Rate |   Average Trade |   Number of Trades |   Exposure |   Total Return |
|:-----------------------------------|:-------------------------|:---------------|--------:|---------:|----------:|---------------:|----------------:|-----------:|----------------:|-------------------:|-----------:|---------------:|
| Persistent low volatility 150/25   | Volatility Regimes       | test_2024_2025 |  0.9040 |   1.4018 |    2.8840 |        -0.2683 |          1.3094 |     0.5363 |          0.0679 |            11.5000 |     1.0000 |         2.6285 |
| TSMOM 60 + persistent low-vol gate | Volatility Regimes       | test_2024_2025 |  0.5925 |   1.2593 |    1.7893 |        -0.3220 |          1.2510 |     0.4350 |          0.0080 |            70.0833 |     0.7962 |         1.5376 |
| XSMOM 180 top 10%                  | Cross-Sectional Momentum | test_2024_2025 |  0.6338 |   0.9818 |    1.6648 |        -0.5617 |          1.1604 |     0.5034 |          0.0224 |            40.0000 |     1.0000 |         1.6711 |
| TSMOM 90 + low-vol filter          | Volatility Regimes       | test_2024_2025 |  0.3419 |   0.8427 |    1.1187 |        -0.3856 |          1.1434 |     0.4720 |          0.0060 |            68.8333 |     0.8878 |         0.8015 |
| Low volatility carry               | Volatility Regimes       | test_2024_2025 |  0.2140 |   0.6825 |    0.9877 |        -0.3174 |          1.1040 |     0.5185 |          0.0078 |            35.5000 |     1.0000 |         0.4743 |
| MA 20/120 trend                    | Trend Following          | test_2024_2025 |  0.2200 |   0.6322 |    0.8694 |        -0.4566 |          1.1017 |     0.4679 |          0.0223 |            16.6599 |     0.9234 |         0.4887 |
| XSMOM top 10%                      | Cross-Sectional Momentum | test_2024_2025 |  0.2034 |   0.6312 |    1.0718 |        -0.6039 |          1.0981 |     0.4925 |          0.0071 |            75.0000 |     1.0000 |         0.4485 |
| Alt relative strength top 10%      | Relative Strength        | test_2024_2025 |  0.1629 |   0.5913 |    0.9976 |        -0.6302 |          1.0916 |     0.4925 |          0.0067 |            74.0000 |     1.0000 |         0.3526 |
| TSMOM 90 gated by BTC 200MA        | Market Regime Detection  | test_2024_2025 |  0.0103 |   0.2880 |    0.3463 |        -0.5842 |          1.0492 |     0.3762 |          0.0028 |            54.6202 |     0.7483 |         0.0208 |
| Donchian breakout 55               | Trend Following          | test_2024_2025 | -0.0432 |   0.2255 |    0.3097 |        -0.6830 |          1.0334 |     0.4979 |          0.0080 |            16.7246 |     0.9726 |        -0.0847 |
| TSMOM 90                           | Trend Following          | test_2024_2025 | -0.0600 |   0.1764 |    0.2340 |        -0.6537 |          1.0267 |     0.4679 |          0.0015 |            68.9060 |     0.9371 |        -0.1165 |
