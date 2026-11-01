# copysim

Backtests copy trading on Binance and Bitget lead traders using their public 90-day performance data. Applies leverage caps, slippage, taker fees, profit share and stop rules to see what a copier would actually keep.

## Usage

```sh
pip install requests
python3 fetch_positions.py   # Binance leaders + closed positions
python3 fetch_bitget.py      # Bitget leaders
python3 simulate.py          # writes results.csv
```

Only leaders still listed are visible, so results have survivorship bias. Bitget doesn't expose trade size, so its cost estimate is rough.

Not financial advice.
