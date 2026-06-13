from __future__ import annotations

import os

import qnt.backtester as qnbt
import qnt.data as qndata
import qnt.output as qnout
import qnt.stats as qnstats

from q25_crypto.strategies import (
    DEFAULT_STRATEGY,
    cross_sectional_momentum_long_only,
    ensemble_long_only,
    mean_reversion_long_only,
    momentum_long_only,
    momentum_low_volatility_long_only,
    persistent_low_volatility_long_only,
)


CONTEST_TYPE = "crypto_daily_long"
START_DATE = "2014-01-01"
DATA_MIN_DATE = "2013-04-01"

STRATEGY_NAME = os.environ.get("QNT_STRATEGY_MODE", "ensemble").strip().lower()
STRATEGY_MAP = {
    "ensemble": ensemble_long_only,
    "momentum": momentum_long_only,
    "mean_reversion": mean_reversion_long_only,
    "low_volatility": persistent_low_volatility_long_only,
    "momentum_low_volatility": momentum_low_volatility_long_only,
    "cross_sectional_momentum": cross_sectional_momentum_long_only,
}


def strategy(data):
    return STRATEGY_MAP.get(STRATEGY_NAME, DEFAULT_STRATEGY)(data)


def _run_single_pass() -> None:
    data = qndata.cryptodaily.load_data(min_date=DATA_MIN_DATE)
    output = strategy(data)
    output = qnout.clean(output, data, CONTEST_TYPE)
    qnout.check(output, data, CONTEST_TYPE)
    qnout.write(output)

    stats = qnstats.calc_stat(data, output.sel(time=slice(START_DATE, None)))
    print(stats.to_pandas().tail())


def _run_multi_pass() -> None:
    qnbt.backtest(
        competition_type=CONTEST_TYPE,
        lookback_period=365,
        start_date=START_DATE,
        strategy=strategy,
        analyze=True,
        build_plots=True,
    )


if os.environ.get("QNT_RUN_MULTI_PASS") == "1":
    _run_multi_pass()
else:
    _run_single_pass()
