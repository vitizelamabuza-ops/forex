# MetaTrader 5 Advanced Trading Bot

A professional-grade automated forex trading bot using MetaTrader 5 Python API with advanced multi-indicator signal generation, intelligent money management, and comprehensive risk controls.

## Features

✅ **Advanced Indicators**
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
- ATR (Average True Range)
- Stochastic Oscillator
- EMA & SMA Crossovers

✅ **Smart Money Management**
- Kelly Criterion position sizing
- Risk percentage per trade
- Daily loss limits
- Max trades per day
- ATR-based stop loss/take profit

✅ **Real-time MT5 Integration**
- Direct MT5 API connection
- Live account balance tracking
- Automatic trade execution
- Multiple symbol support

✅ **Performance Tracking**
- CSV trade logging
- Signal logging with strength analysis
- Performance metrics
- Session summaries

## Requirements

- Windows OS (MT5 Python API works on Windows)
- MetaTrader 5 installed and running
- Python 3.8+
- Active MT5 trading account

## Installation

```bash
# Clone repository
git clone https://github.com/vitizelamabuza-ops/forex.git
cd forex

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the bot
python mt5_trading_bot.py
```

## Configuration

Edit settings in `mt5_trading_bot.py`:

```python
bot = MT5TradingBot(
    symbols=['EURUSD', 'GBPUSD', 'USDJPY'],
    risk_per_trade=0.02,           # 2% risk per trade
    max_daily_loss=0.05,           # 5% daily loss limit
    max_trades_per_day=5,          # Max 5 trades/day
    use_kelly=True,                # Kelly Criterion
)
```

## Output Files

- `mt5_bot.log` - Detailed bot logs
- `trades.csv` - Trade history
- `signals.csv` - Signal history
- `performance.csv` - Performance metrics

## Risk Warning

⚠️ **Trading involves risk. Past performance is not indicative of future results.**

- Start with small position sizes
- Use proper risk management
- Test thoroughly before live trading
- Never risk more than you can afford to lose

## License

MIT License - See LICENSE file

## Support

For issues and questions, please open an issue on GitHub.

---

**Author:** vitizelamabuza-ops
**Last Updated:** 2025-06-22