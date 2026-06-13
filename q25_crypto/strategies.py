from __future__ import annotations

import numpy as np
import xarray as xr

from .features import (
    liquidity_score,
    liquid_mask,
    mean_reversion_score,
    momentum_score,
    trend_score,
    volatility_penalty,
)
from .portfolio import blend_scores, normalize_long_only


def _rank_pct_by_asset(score: xr.DataArray) -> xr.DataArray:
    count = score.count("asset")
    ranked = score.rank("asset")
    return xr.where(count > 0, ranked / count, 0.0).fillna(0.0)


def _equal_weight_mask(mask: xr.DataArray, liquid: xr.DataArray) -> xr.DataArray:
    eligible = xr.where((mask.fillna(False)) & (liquid > 0), 1.0, 0.0)
    count = eligible.sum("asset")
    return xr.where(count > 0, eligible / count, 0.0).fillna(0.0)


def _realized_volatility(data: xr.DataArray, lookback: int) -> xr.DataArray:
    close = data.sel(field="close")
    returns = close / close.shift(time=1) - 1.0
    return returns.rolling(time=lookback, min_periods=lookback).std()


def _trend_regime(data: xr.DataArray) -> xr.DataArray:
    trend = trend_score(data)
    vol = volatility_penalty(data)
    return trend - 0.5 * vol


def momentum_long_only(data: xr.DataArray) -> xr.DataArray:
    score = momentum_score(data) + 0.4 * trend_score(data)
    score = score - 0.3 * volatility_penalty(data)
    score = score * liquidity_score(data)
    return normalize_long_only(score, liquid_mask(data))


def mean_reversion_long_only(data: xr.DataArray) -> xr.DataArray:
    score = mean_reversion_score(data)
    score = score - 0.2 * volatility_penalty(data)
    score = score * liquidity_score(data)
    return normalize_long_only(score, liquid_mask(data))


def ensemble_long_only(data: xr.DataArray) -> xr.DataArray:
    trend = momentum_score(data) + 0.3 * trend_score(data)
    mean_reversion = mean_reversion_score(data)
    regime = _trend_regime(data)

    trend_component = xr.where(trend > 0, trend, 0.0)
    mean_component = xr.where(mean_reversion > 0, mean_reversion, 0.0)

    blended = xr.where(
        regime > 0,
        blend_scores(trend_component, mean_component, weights=(0.75, 0.25)),
        blend_scores(trend_component, mean_component, weights=(0.35, 0.65)),
    )
    blended = blended * liquidity_score(data)
    blended = blended.where(np.isfinite(blended), 0.0)
    return normalize_long_only(blended, liquid_mask(data))


def persistent_low_volatility_long_only(data: xr.DataArray) -> xr.DataArray:
    liquid = liquid_mask(data)
    realized = _realized_volatility(data, 150).where(liquid > 0)
    vol_rank = _rank_pct_by_asset(realized)
    return _equal_weight_mask(vol_rank <= 0.25, liquid)


def momentum_low_volatility_long_only(data: xr.DataArray) -> xr.DataArray:
    close = data.sel(field="close")
    liquid = liquid_mask(data)
    momentum = close / close.shift(time=60) - 1.0
    realized = _realized_volatility(data, 45).where(liquid > 0)
    vol_rank = _rank_pct_by_asset(realized)
    return _equal_weight_mask((momentum > 0) & (vol_rank <= 0.40), liquid)


def cross_sectional_momentum_long_only(data: xr.DataArray) -> xr.DataArray:
    close = data.sel(field="close")
    liquid = liquid_mask(data)
    momentum = (close / close.shift(time=180) - 1.0).where(liquid > 0)
    momentum_rank = _rank_pct_by_asset(momentum)
    return _equal_weight_mask(momentum_rank > 0.90, liquid)


DEFAULT_STRATEGY = ensemble_long_only
