from __future__ import annotations

import numpy as np
import xarray as xr


def _zero_like_weights(reference: xr.DataArray) -> xr.DataArray:
    return xr.zeros_like(reference)


def normalize_long_only(score: xr.DataArray, liquid_mask: xr.DataArray | None = None) -> xr.DataArray:
    cleaned = score.where(np.isfinite(score), 0.0)
    if liquid_mask is not None:
        cleaned = cleaned.where(liquid_mask > 0, 0.0)

    positive = xr.where(cleaned > 0, cleaned, 0.0)
    total = positive.sum("asset")

    if liquid_mask is not None:
        fallback = xr.where(liquid_mask > 0, 1.0, 0.0)
    else:
        fallback = xr.where(cleaned.isnull(), 0.0, 1.0)

    fallback_total = fallback.sum("asset")
    fallback_weights = xr.where(fallback_total > 0, fallback / fallback_total, _zero_like_weights(fallback))

    weights = xr.where(total > 0, positive / total, fallback_weights)
    return weights.fillna(0.0)


def blend_scores(*scores: xr.DataArray, weights: list[float] | tuple[float, ...]) -> xr.DataArray:
    if len(scores) != len(weights):
        raise ValueError("scores and weights must have the same length")

    total = None
    for score, w in zip(scores, weights):
        component = score * float(w)
        total = component if total is None else total + component
    return total

