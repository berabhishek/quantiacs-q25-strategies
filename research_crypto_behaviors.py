from __future__ import annotations

import gzip
import io
import json
import math
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import xarray as xr


ROOT = Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data-cache" / "acd49a1cf2ff5cd5fe8ed83710b43b7630e05fe0.value.pickle.gz"
OUT_DIR = ROOT / "research_outputs"
ONE_WAY_COST = 0.0015
TRAIN = ("2018-01-01", "2022-12-31")
VALIDATION = ("2023-01-01", "2023-12-31")
TEST = ("2024-01-01", "2025-12-31")


@dataclass(frozen=True)
class Experiment:
    name: str
    category: str
    hypothesis: str
    why_persist: str
    participants: str
    stronger_when: str
    weaker_when: str
    rules: str
    weights: Callable[[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict], pd.DataFrame]
    base_params: dict
    sensitivity_param: str | None = None
    sensitivity_values: tuple | None = None


def load_cached_data() -> dict[str, pd.DataFrame]:
    with gzip.open(CACHE_FILE, "rb") as f:
        raw = pickle.load(f)
    data = xr.open_dataarray(io.BytesIO(raw), engine="scipy").sortby("time")

    frames = {}
    for field in ["open", "high", "low", "close", "vol", "is_liquid"]:
        frames[field] = data.sel(field=field).to_pandas().sort_index()
        frames[field].index = pd.to_datetime(frames[field].index)
    for field in ["open", "high", "low", "close"]:
        frames[field] = frames[field].where(frames[field] > 0)
    frames["is_liquid"] = frames["is_liquid"].where(frames["close"].notna(), 0.0)
    return frames


def normalize_long_only(score: pd.DataFrame, liquid: pd.DataFrame) -> pd.DataFrame:
    score = score.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    positive = score.clip(lower=0.0).where(liquid > 0, 0.0)
    total = positive.sum(axis=1)
    fallback = (liquid > 0).astype(float)
    fallback_total = fallback.sum(axis=1).replace(0.0, np.nan)
    fallback_w = fallback.div(fallback_total, axis=0).fillna(0.0)
    weights = positive.div(total.replace(0.0, np.nan), axis=0)
    return weights.where(total.gt(0), fallback_w).fillna(0.0)


def equal_weight_mask(mask: pd.DataFrame, liquid: pd.DataFrame) -> pd.DataFrame:
    eligible = mask.fillna(False) & liquid.gt(0)
    count = eligible.sum(axis=1).replace(0, np.nan)
    return eligible.astype(float).div(count, axis=0).fillna(0.0)


def top_quantile_weights(score: pd.DataFrame, liquid: pd.DataFrame, quantile: float) -> pd.DataFrame:
    score = score.where(liquid > 0)
    ranks = score.rank(axis=1, pct=True, method="first")
    return equal_weight_mask(ranks > 1.0 - quantile, liquid)


def ma_crossover(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    fast = close.rolling(params["fast"]).mean()
    slow = close.rolling(params["slow"]).mean()
    return equal_weight_mask(fast > slow, liquid)


def donchian_breakout(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    lookback = params["lookback"]
    prior_high = close.rolling(lookback).max().shift(1)
    prior_low = close.rolling(lookback).min().shift(1)
    raw = pd.DataFrame(False, index=close.index, columns=close.columns)
    in_pos = pd.Series(False, index=close.columns)
    for t in close.index:
        enter = close.loc[t] > prior_high.loc[t]
        exit_ = close.loc[t] < prior_low.loc[t]
        in_pos = (in_pos | enter.fillna(False)) & ~exit_.fillna(False)
        raw.loc[t] = in_pos
    return equal_weight_mask(raw, liquid)


def time_series_momentum(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    ret = close.pct_change(params["lookback"], fill_method=None)
    return equal_weight_mask(ret > 0, liquid)


def cross_sectional_momentum(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    ret = close.pct_change(params["lookback"], fill_method=None)
    return top_quantile_weights(ret, liquid, params["top_quantile"])


def low_volatility_carry(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    realized = close.pct_change(fill_method=None).rolling(params["lookback"]).std()
    ranks = realized.where(liquid > 0).rank(axis=1, pct=True, method="first")
    return equal_weight_mask(ranks <= params["bottom_quantile"], liquid)


def momentum_low_vol_filter(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    mom = close.pct_change(params["lookback"], fill_method=None)
    realized = close.pct_change(fill_method=None).rolling(params["vol_lookback"]).std()
    vol_rank = realized.where(liquid > 0).rank(axis=1, pct=True, method="first")
    return equal_weight_mask((mom > 0) & (vol_rank <= params["max_vol_rank"]), liquid)


def btc_regime_momentum(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    base = time_series_momentum(close, liquid, _vol, params)
    btc = close["BTC"]
    active = btc > btc.rolling(params["btc_ma"]).mean()
    return base.where(active, 0.0).fillna(0.0)


def alt_relative_strength(close: pd.DataFrame, liquid: pd.DataFrame, _vol: pd.DataFrame, params: dict) -> pd.DataFrame:
    ret = close.pct_change(params["lookback"], fill_method=None)
    btc_ret = ret["BTC"]
    score = ret.sub(btc_ret, axis=0)
    score["BTC"] = np.nan
    return top_quantile_weights(score, liquid, params["top_quantile"])


def backtest(close: pd.DataFrame, weights: pd.DataFrame, start: str, end: str) -> dict:
    returns = close.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    weights = weights.reindex_like(close).fillna(0.0)
    shifted = weights.shift(1).fillna(0.0)
    gross = (shifted * returns).sum(axis=1)
    turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
    net = gross - turnover * ONE_WAY_COST
    net = net.loc[start:end]
    weights_period = weights.loc[start:end]
    turnover_period = turnover.loc[start:end]
    equity = (1.0 + net).cumprod()
    years = len(net) / 365.25
    total_return = equity.iloc[-1] - 1.0 if len(equity) else np.nan
    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 and len(equity) else np.nan
    vol = net.std(ddof=0) * math.sqrt(365.25)
    sharpe = net.mean() / net.std(ddof=0) * math.sqrt(365.25) if net.std(ddof=0) else np.nan
    downside = net[net < 0].std(ddof=0)
    sortino = net.mean() / downside * math.sqrt(365.25) if downside else np.nan
    drawdown = equity / equity.cummax() - 1.0
    max_dd = drawdown.min() if len(drawdown) else np.nan
    positive = net[net > 0].sum()
    negative = -net[net < 0].sum()
    profit_factor = positive / negative if negative else np.nan
    win_rate = (net > 0).mean() if len(net) else np.nan
    avg_trade = net.sum() / turnover_period.sum() if turnover_period.sum() else np.nan
    exposure = weights_period.abs().sum(axis=1).gt(0).mean() if len(weights_period) else np.nan
    num_trades = (turnover_period / 2.0).sum()
    monthly = (1.0 + net).resample("ME").prod() - 1.0
    yearly = (1.0 + net).resample("YE").prod() - 1.0
    return {
        "cagr": cagr,
        "total_return": total_return,
        "ann_vol": vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_dd,
        "profit_factor": profit_factor,
        "win_rate": win_rate,
        "avg_trade": avg_trade,
        "num_trades": num_trades,
        "exposure": exposure,
        "daily_returns": net,
        "monthly": monthly,
        "yearly": yearly,
    }


def btc_regimes(close: pd.DataFrame) -> pd.Series:
    btc = close["BTC"]
    ma = btc.rolling(200).mean()
    rv = btc.pct_change().rolling(60).std() * math.sqrt(365.25)
    fwd60 = btc.pct_change(60)
    regime = pd.Series("sideways", index=close.index)
    regime[(btc > ma) & (fwd60 > 0.05)] = "bull"
    regime[(btc < ma) & (fwd60 < -0.05)] = "bear"
    regime[rv > rv.quantile(0.80)] = regime[rv > rv.quantile(0.80)] + "_high_vol"
    return regime


def summarize_regimes(daily_returns: pd.Series, regimes: pd.Series) -> pd.DataFrame:
    rows = []
    aligned = pd.concat([daily_returns.rename("ret"), regimes.rename("regime")], axis=1).dropna()
    for name, group in aligned.groupby("regime"):
        if len(group) < 30:
            continue
        ret = group["ret"]
        sharpe = ret.mean() / ret.std(ddof=0) * math.sqrt(365.25) if ret.std(ddof=0) else np.nan
        rows.append(
            {
                "regime": name,
                "days": len(ret),
                "return": (1.0 + ret).prod() - 1.0,
                "sharpe": sharpe,
                "win_rate": (ret > 0).mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("sharpe", ascending=False)


def metric_row(name: str, category: str, split: str, stats: dict) -> dict:
    return {
        "strategy": name,
        "category": category,
        "split": split,
        "CAGR": stats["cagr"],
        "Sharpe": stats["sharpe"],
        "Sortino": stats["sortino"],
        "Max Drawdown": stats["max_drawdown"],
        "Profit Factor": stats["profit_factor"],
        "Win Rate": stats["win_rate"],
        "Average Trade": stats["avg_trade"],
        "Number of Trades": stats["num_trades"],
        "Exposure": stats["exposure"],
        "Total Return": stats["total_return"],
    }


def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x:.2%}"


def fmt_num(x: float) -> str:
    if pd.isna(x):
        return "n/a"
    return f"{x:.2f}"


def run() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    frames = load_cached_data()
    close = frames["close"]
    liquid = frames["is_liquid"].reindex_like(close).fillna(0.0)
    vol = frames["vol"]
    regimes = btc_regimes(close)

    experiments = [
        Experiment(
            "MA 20/120 trend",
            "Trend Following",
            "Large crypto assets exhibit slow behavioral and flow-driven trends after sustained repricing.",
            "Reflexive investor flows, delayed fundamental repricing, and benchmark under/overweight adjustments do not complete in one day.",
            "Retail trend chasers, systematic CTA-like crypto products, token treasuries, and benchmark allocators.",
            "Broad risk-on conditions, persistent BTC uptrends, and expanding participation.",
            "Sharp deleveraging, range-bound chop, and exchange/liquidity shocks.",
            "Entry: asset 20-day SMA > 120-day SMA. Exit: asset 20-day SMA <= 120-day SMA. Equal-weight active liquid assets.",
            ma_crossover,
            {"fast": 20, "slow": 120},
            "slow",
            (60, 90, 120, 150, 180, 240),
        ),
        Experiment(
            "Donchian breakout 55",
            "Trend Following",
            "New multi-month highs in crypto attract momentum capital and forced underweight buying.",
            "Crypto markets are fragmented and narrative-driven, so price discovery can continue after breakouts.",
            "Momentum traders, discretionary breakout buyers, and short sellers forced to cover.",
            "Fresh highs with broad market confirmation.",
            "False breakouts during low-liquidity sideways markets.",
            "Entry: close above prior 55-day high. Exit: close below prior 55-day low. Equal-weight active liquid assets.",
            donchian_breakout,
            {"lookback": 55},
            "lookback",
            (20, 40, 55, 70, 90, 120),
        ),
        Experiment(
            "TSMOM 90",
            "Trend Following",
            "Assets with positive medium-term own returns continue to drift as crypto repricing is gradual.",
            "Narratives, listings, and capital inflows tend to diffuse across venues and investor groups over weeks.",
            "Retail momentum buyers, market makers hedging inventory, and funds rotating into winners.",
            "Bull regimes and post-consolidation breakouts.",
            "Bear markets with violent mean reversion.",
            "Entry: 90-day total return > 0. Exit: 90-day total return <= 0. Equal-weight active liquid assets.",
            time_series_momentum,
            {"lookback": 90},
            "lookback",
            (30, 60, 90, 120, 180, 240),
        ),
        Experiment(
            "XSMOM top 10%",
            "Cross-Sectional Momentum",
            "Within crypto, recent winners keep attracting capital relative to laggards.",
            "Attention, exchange listings, and ecosystem narratives concentrate flows into leaders before diffusing.",
            "Narrative traders, relative-value funds, and liquidity providers following volume migration.",
            "Altcoin bull phases and sector-led markets.",
            "Market-wide deleveraging where correlations go to one.",
            "Entry: rank liquid assets by 90-day return and buy top 10%. Exit: falls out of top 10%. Equal-weight selected assets.",
            cross_sectional_momentum,
            {"lookback": 90, "top_quantile": 0.10},
            "top_quantile",
            (0.05, 0.10, 0.20),
        ),
        Experiment(
            "Low volatility carry",
            "Volatility Regimes",
            "Lower realized-volatility crypto assets may have better forward risk-adjusted returns than distressed high-volatility names.",
            "High volatility often reflects adverse selection, poor liquidity, or crash risk; calmer assets are more institutionally holdable.",
            "Levered traders exiting distressed names and long-only allocators preferring stable majors.",
            "Sideways or recovering markets.",
            "Speculative melt-ups where high-beta assets dominate.",
            "Entry: 30-day realized volatility in bottom 20% of liquid universe. Exit: leaves bottom 20%. Equal-weight selected assets.",
            low_volatility_carry,
            {"lookback": 30, "bottom_quantile": 0.20},
            "lookback",
            (15, 20, 30, 45, 60, 90),
        ),
        Experiment(
            "TSMOM 90 + low-vol filter",
            "Volatility Regimes",
            "Momentum is more robust when it avoids the noisiest high-volatility assets.",
            "Volatility filtering reduces exposure to forced-liquidation rebounds and unstable microstructure.",
            "Momentum traders chasing liquid leaders versus distressed speculators in high-vol names.",
            "Orderly uptrends with moderate realized volatility.",
            "Early bull reversals led by high-beta laggards.",
            "Entry: 90-day return > 0 and 30-day realized-vol rank <= 60%. Exit: either condition fails.",
            momentum_low_vol_filter,
            {"lookback": 90, "vol_lookback": 30, "max_vol_rank": 0.60},
            "max_vol_rank",
            (0.40, 0.50, 0.60, 0.70, 0.80),
        ),
        Experiment(
            "Persistent low volatility 150/25",
            "Volatility Regimes",
            "Crypto assets that remain low volatility over a longer window may avoid distress risk while still carrying broad market beta.",
            "Persistent calm tends to reflect deeper liquidity, lower adverse selection, and more institutionally acceptable risk.",
            "Long-only allocators, volatility-aware funds, and levered traders avoiding unstable collateral.",
            "Broad recovery phases, sideways markets, and environments where crash risk is being repriced slowly.",
            "Speculative melt-ups led by high-beta laggards or sudden rotations into distressed assets.",
            "Entry: 150-day realized volatility in bottom 25% of liquid universe. Exit: leaves bottom 25%. Equal-weight selected assets.",
            low_volatility_carry,
            {"lookback": 150, "bottom_quantile": 0.25},
            "lookback",
            (60, 90, 120, 150),
        ),
        Experiment(
            "TSMOM 60 + persistent low-vol gate",
            "Volatility Regimes",
            "Shorter momentum works better when restricted to assets whose recent volatility is not already distressed.",
            "The volatility gate filters liquidation rebounds and noisy microstructure while retaining assets with timely positive drift.",
            "Momentum traders, volatility-controlled allocators, and liquidity providers rotating into orderly leaders.",
            "Orderly uptrends with moderate realized volatility and broad participation.",
            "Early bull reversals led by the highest-beta assets.",
            "Entry: 60-day return > 0 and 45-day realized-vol rank <= 40%. Exit: either condition fails.",
            momentum_low_vol_filter,
            {"lookback": 60, "vol_lookback": 45, "max_vol_rank": 0.40},
            "max_vol_rank",
            (0.30, 0.40, 0.50, 0.60),
        ),
        Experiment(
            "XSMOM 180 top 10%",
            "Cross-Sectional Momentum",
            "Longer-horizon crypto leaders may keep attracting capital after narratives become established.",
            "A 180-day ranking favors persistent ecosystem leadership over short-lived listing or attention spikes.",
            "Narrative traders, ecosystem funds, benchmark allocators, and relative-strength managers.",
            "Sustained sector leadership and broad crypto risk appetite.",
            "Fast leadership reversals, BTC dominance shocks, and market-wide deleveraging.",
            "Entry: rank liquid assets by 180-day return and buy top 10%. Exit: falls out of top 10%. Equal-weight selected assets.",
            cross_sectional_momentum,
            {"lookback": 180, "top_quantile": 0.10},
            "top_quantile",
            (0.10, 0.15, 0.20, 0.25),
        ),
        Experiment(
            "TSMOM 90 gated by BTC 200MA",
            "Market Regime Detection",
            "Long-only crypto momentum has a higher survival probability when BTC is in a broad uptrend.",
            "BTC remains the dominant collateral and sentiment anchor; below its long-term trend, liquidity and risk appetite contract.",
            "Long-only funds, miners/treasuries, retail beta buyers, and perps traders using BTC as risk proxy.",
            "BTC above long-term trend with positive breadth.",
            "Altcoin-specific rallies while BTC is below trend, or sudden trend reversals.",
            "Entry: asset 90-day return > 0 and BTC close > BTC 200-day SMA. Exit: either condition fails.",
            btc_regime_momentum,
            {"lookback": 90, "btc_ma": 200},
            "btc_ma",
            (100, 150, 200, 250, 300),
        ),
        Experiment(
            "Alt relative strength top 10%",
            "Relative Strength",
            "Altcoins outperforming BTC can continue as leadership rotates into ecosystems with active narratives.",
            "Capital often moves from BTC into stronger ecosystems after BTC establishes risk appetite.",
            "Sector rotation traders, ecosystem funds, market makers, and retail narrative flows.",
            "Broad altcoin seasons and BTC-stable/rising markets.",
            "BTC dominance shocks and liquidity contractions.",
            "Entry: rank non-BTC assets by 90-day return minus BTC 90-day return and buy top 10%. Exit: falls out of top 10%.",
            alt_relative_strength,
            {"lookback": 90, "top_quantile": 0.10},
            "top_quantile",
            (0.05, 0.10, 0.20),
        ),
    ]

    metric_rows = []
    report_blocks = []
    all_monthly = {}
    all_yearly = {}
    robustness = {}

    for exp in experiments:
        weights = exp.weights(close, liquid, vol, exp.base_params)
        stats_by_split = {
            "train_2018_2022": backtest(close, weights, *TRAIN),
            "validation_2023": backtest(close, weights, *VALIDATION),
            "test_2024_2025": backtest(close, weights, *TEST),
        }
        for split, stats in stats_by_split.items():
            metric_rows.append(metric_row(exp.name, exp.category, split, stats))
        test_stats = stats_by_split["test_2024_2025"]
        all_monthly[exp.name] = test_stats["monthly"]
        all_yearly[exp.name] = test_stats["yearly"]
        reg = summarize_regimes(test_stats["daily_returns"], regimes)
        robustness[exp.name] = reg

        sens_rows = []
        if exp.sensitivity_param and exp.sensitivity_values:
            for value in exp.sensitivity_values:
                params = dict(exp.base_params)
                params[exp.sensitivity_param] = value
                w = exp.weights(close, liquid, vol, params)
                s = backtest(close, w, *TEST)
                sens_rows.append(
                    {
                        exp.sensitivity_param: value,
                        "CAGR": s["cagr"],
                        "Sharpe": s["sharpe"],
                        "Max Drawdown": s["max_drawdown"],
                        "Trades": s["num_trades"],
                    }
                )
        sens = pd.DataFrame(sens_rows)
        sens.to_csv(OUT_DIR / f"{slug(exp.name)}_sensitivity.csv", index=False)
        reg.to_csv(OUT_DIR / f"{slug(exp.name)}_regimes.csv", index=False)

        best_regime = "n/a"
        worst_regime = "n/a"
        if not reg.empty:
            best_regime = reg.sort_values("sharpe", ascending=False).iloc[0]["regime"]
            worst_regime = reg.sort_values("sharpe", ascending=True).iloc[0]["regime"]

        report_blocks.append(
            {
                "name": exp.name,
                "category": exp.category,
                "hypothesis": exp.hypothesis,
                "why_persist": exp.why_persist,
                "participants": exp.participants,
                "stronger_when": exp.stronger_when,
                "weaker_when": exp.weaker_when,
                "rules": exp.rules,
                "test_metrics": metric_row(exp.name, exp.category, "test_2024_2025", test_stats),
                "best_regime": best_regime,
                "worst_regime": worst_regime,
                "sensitivity": sens.to_dict(orient="records"),
            }
        )

    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(OUT_DIR / "strategy_metrics_by_split.csv", index=False)
    pd.DataFrame(all_monthly).to_csv(OUT_DIR / "test_monthly_returns.csv")
    pd.DataFrame(all_yearly).to_csv(OUT_DIR / "test_yearly_returns.csv")
    with open(OUT_DIR / "research_summary.json", "w") as f:
        json.dump(report_blocks, f, indent=2, default=float)
    write_markdown_report(report_blocks, metrics)


def slug(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_")


def write_markdown_report(blocks: list[dict], metrics: pd.DataFrame) -> None:
    lines = [
        "# Crypto Behavior Research Report",
        "",
        f"Data: local Quantiacs crypto daily OHLCV cache, 76 assets, 2014-01-01 through 2026-06-12.",
        f"Backtest convention: close-to-close daily returns, positions decided from prior close and applied next day, long-only, liquid assets only, cost = {ONE_WAY_COST:.2%} one-way turnover for combined fee/slippage.",
        f"Train: {TRAIN[0]} to {TRAIN[1]}. Validation: {VALIDATION[0]} to {VALIDATION[1]}. Test: {TEST[0]} to {TEST[1]}. Final decision metrics below use test only.",
        "",
        "## Funding Rate Effects",
        "",
        "Rejected for this run: cached fields are only open, high, low, close, volume, and is_liquid. Funding-rate hypotheses require historical perpetual funding data, so any result from OHLCV alone would be a proxy, not a funding-rate test.",
        "",
    ]
    for block in blocks:
        m = block["test_metrics"]
        lines.extend(
            [
                f"## {block['name']}",
                "",
                f"Category: {block['category']}",
                "",
                f"Hypothesis: {block['hypothesis']}",
                f"Why it should persist: {block['why_persist']}",
                f"Participants creating it: {block['participants']}",
                f"Stronger when: {block['stronger_when']}",
                f"Weaker when: {block['weaker_when']}",
                "",
                f"Rules: {block['rules']}",
                "",
                "Test metrics:",
                "",
                f"- CAGR: {fmt_pct(m['CAGR'])}",
                f"- Sharpe Ratio: {fmt_num(m['Sharpe'])}",
                f"- Sortino Ratio: {fmt_num(m['Sortino'])}",
                f"- Max Drawdown: {fmt_pct(m['Max Drawdown'])}",
                f"- Profit Factor: {fmt_num(m['Profit Factor'])}",
                f"- Win Rate: {fmt_pct(m['Win Rate'])}",
                f"- Average Trade: {fmt_pct(m['Average Trade'])}",
                f"- Number of Trades: {fmt_num(m['Number of Trades'])}",
                f"- Exposure: {fmt_pct(m['Exposure'])}",
                "",
                f"Regime analysis: best test regime was `{block['best_regime']}`; worst was `{block['worst_regime']}`. Full regime tables are in `research_outputs/{slug(block['name'])}_regimes.csv`.",
                "",
                "Parameter sensitivity on test:",
                "",
            ]
        )
        if block["sensitivity"]:
            sens = pd.DataFrame(block["sensitivity"])
            lines.append(sens.to_markdown(index=False, floatfmt=".4f"))
        else:
            lines.append("No sensitivity grid configured.")
        lines.extend(
            [
                "",
                "Failure modes: correlation spikes, exchange-specific liquidity gaps, sudden BTC dominance shocks, high turnover during choppy ranges, and survivorship/listing effects in the contest universe.",
                "",
                "Recommended next experiment: keep the same train/validation/test split and add exactly one improvement only if raw validation and test behavior are coherent.",
                "",
            ]
        )

    test = metrics[metrics["split"] == "test_2024_2025"].copy()
    test = test.sort_values("Sharpe", ascending=False)
    lines.extend(["## Test Ranking", "", test.to_markdown(index=False, floatfmt=".4f"), ""])
    (OUT_DIR / "research_report.md").write_text("\n".join(lines))


if __name__ == "__main__":
    run()
