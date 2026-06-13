from __future__ import annotations

import numpy as np
import xarray as xr

import qnt.ta as qnta


def _field(data: xr.DataArray, name: str) -> xr.DataArray:
    available = set(str(x) for x in data.coords["field"].values)
    if name not in available:
        return xr.zeros_like(data.sel(field="close"))
    return data.sel(field=name)


def liquid_mask(data: xr.DataArray) -> xr.DataArray:
    return _field(data, "is_liquid").fillna(0)


def momentum_score(data: xr.DataArray) -> xr.DataArray:
    close = data.sel(field="close")
    fast = qnta.lwma(close, 10)
    slow = qnta.lwma(close, 50)
    return (fast / slow) - 1.0


def trend_score(data: xr.DataArray) -> xr.DataArray:
    close = data.sel(field="close")
    medium = qnta.lwma(close, 20)
    long = qnta.lwma(close, 120)
    return (medium / long) - 1.0


def mean_reversion_score(data: xr.DataArray) -> xr.DataArray:
    close = data.sel(field="close")
    reference = qnta.sma(close, 15)
    return -(close / reference - 1.0)


def volatility_penalty(data: xr.DataArray) -> xr.DataArray:
    high = data.sel(field="high")
    low = data.sel(field="low")
    close = data.sel(field="close")
    volatility = qnta.tr(high, low, close) / close
    smoothed = qnta.lwma(volatility, 20)
    return smoothed.where(np.isfinite(smoothed), 0.0)


def volume_score(data: xr.DataArray) -> xr.DataArray:
    volume = _field(data, "vol")
    recent = qnta.sma(volume, 5)
    baseline = qnta.sma(volume, 60)
    score = recent / baseline
    return score.where(np.isfinite(score), 0.0)


def liquidity_score(data: xr.DataArray) -> xr.DataArray:
    liquid = liquid_mask(data)
    volume = volume_score(data)
    return liquid * (1.0 + 0.15 * volume)

