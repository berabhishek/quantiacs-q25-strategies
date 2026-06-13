# Q25 Quantiacs Crypto Scaffold

This repository is set up as a Quantiacs Q25 crypto submission workspace.

What I mirrored from the public Quantiacs GitHub examples:

- Small repo footprint: most public strategy repos are just `LICENSE` plus `strategy.ipynb`, sometimes with a short `README.md`.
- Notebook-first execution: the recurring pattern is one notebook entrypoint that imports a strategy module or defines the strategy inline.
- Single backtest entrypoint: Quantiacs examples usually end in one `qnt.backtester.backtest(...)` or `qnt.output.write(...)` flow.
- Long-only crypto contest API: the current Q25 contest is `crypto_daily_long`, and the toolbox exposes `qnt.data.cryptodaily.load_data(...)`.

Public repos I checked:

- [quantiacs/toolbox](https://github.com/quantiacs/toolbox) - 82 stars
- [quantiacs/strategy-ml-crypto-long-short](https://github.com/quantiacs/strategy-ml-crypto-long-short) - 6 stars
- [quantiacs/strategy-ml-backtester](https://github.com/quantiacs/strategy-ml-backtester) - 3 stars
- [quantiacs/strategy-first-crypto-daily-long](https://github.com/quantiacs/strategy-first-crypto-daily-long) - 2 stars
- [quantiacs/Q24-crypto-guide](https://github.com/quantiacs/Q24-crypto-guide) - 0 stars

This scaffold adds a bit more structure than the public examples so the strategy ideas stay modular:

- `strategy.ipynb` - notebook entrypoint
- `strategy.py` - executable submission script
- `q25_crypto/` - reusable strategy code
- `QNT_STRATEGY_MODE` - optional environment switch: `ensemble`, `momentum`, `mean_reversion`, `low_volatility`, `momentum_low_volatility`, or `cross_sectional_momentum`

## Strategy ideas included

- Momentum long-only
- Mean reversion long-only
- Regime-aware ensemble long-only
- Persistent low-volatility long-only
- Momentum with a low-volatility gate
- Cross-sectional momentum long-only

These are intentionally simple, stable starting points:

- they use only the toolbox and common indicators
- they stay long-only
- they normalize exposure across liquid assets
- they can be swapped in or recombined quickly

## Local use

The Quantiacs toolbox is the main dependency. A typical local setup is:

```bash
pip install git+https://github.com/quantiacs/toolbox.git
```

Then run the notebook or import `strategy.py` in a Quantiacs-style notebook session.
