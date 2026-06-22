# MT5 Python Bot - Setup Guide

## Prerequisites

### 1. Install MetaTrader 5
- Download from: https://www.metatrader5.com/download
- Install on Windows
- Create a demo or live account
- **Important:** Keep MT5 running while using the bot

### 2. Install Python
- Download Python 3.10+ from: https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"
- Verify installation:
  ```bash
  python --version
  pip --version
  ```

## Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/vitizelamabuza-ops/forex.git
cd forex
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MT5 Connection

1. Open MetaTrader 5
2. Log into your account
3. Enable Algo Trading:
   - File → Account
   - Check "Enable DLL imports" and "Enable WebRequest"
   - Restart MT5

### Step 5: Verify Installation

Create a test file `test_mt5.py`:

```python
import MetaTrader5 as mt5

print("Testing MT5 connection...")

if not mt5.initialize():
    print("❌ Failed to initialize MT5")
    exit()

print(f"✅ MT5 Version: {mt5.version()}")
print(f"✅ Account: {mt5.account_info().login}")
print(f"✅ Balance: ${mt5.account_info().balance:.2f}")

mt5.shutdown()
print("✅ Connection test successful!")
```

Run the test:
```bash
python test_mt5.py
```

You should see:
```
✅ MT5 Version: (5, 0, 5735)
✅ Account: 123456789
✅ Balance: $10000.00
✅ Connection test successful!
```

## Running the Bot

### Start the Bot
```bash
python mt5_trading_bot.py
```

You should see:
```
======================================================================
🚀 MetaTrader 5 Connected
======================================================================
Version: 5.0.5735
Account: 123456789
Server: ICMarkets-Demo
Balance: $10000.00
Equity: $10000.00
======================================================================

======================================================================
🤖 BOT RUNNING
======================================================================
Symbols: EURUSD, GBPUSD, USDJPY, AUDUSD
Check Interval: 300s
Max Trades/Day: 5
Risk/Trade: 2.0%
Max Daily Loss: 5.0%
======================================================================

⏳ Next scan in 300s...
```

### Stop the Bot
Press `Ctrl+C` to gracefully stop the bot

## Troubleshooting

### "MT5 initialization failed"
- Make sure MT5 is open and running
- Make sure you're logged into an account
- Restart MT5 and try again

### "No rates returned for EURUSD"
- Symbol might not exist or spelling is wrong
- Try: `EURUSD` (not `EUR_USD`)
- Check if symbol is available in your broker

### "Order failed"
- Verify you have enough balance for the position size
- Check if market is open
- Verify stop loss and take profit are set correctly

### Python not found
- Add Python to PATH during installation
- Or use full path: `C:\Python310\python.exe mt5_trading_bot.py`

## File Structure

```
forex/
├── mt5_trading_bot.py    # Main bot code
├── requirements.txt      # Python dependencies
├── .env.example          # Example configuration
├── .gitignore           # Git ignore rules
├── README.md            # Documentation
├── LICENSE              # MIT License
├── SETUP_GUIDE.md       # This file
├── trades.csv           # Trade log (auto-generated)
├── signals.csv          # Signal log (auto-generated)
├── performance.csv      # Performance log (auto-generated)
└── mt5_bot.log          # Bot log (auto-generated)
```

## Performance Monitoring

After running the bot, check:

1. **Trade Log** (`trades.csv`):
   - View all executed trades
   - Entry prices, stop loss, take profit
   - Signal strength used

2. **Signal Log** (`signals.csv`):
   - View all generated signals (even non-executed)
   - RSI, MACD, ATR values
   - Buy/Sell votes from voting system

3. **Bot Log** (`mt5_bot.log`):
   - Detailed execution logs
   - Error messages
   - Performance metrics

## Configuration Tips

### For Conservative Trading
```python
bot = MT5TradingBot(
    risk_per_trade=0.01,        # 1% per trade (lower risk)
    max_daily_loss=0.02,        # 2% daily loss limit
    max_trades_per_day=3,       # Fewer trades
)
```

### For Aggressive Trading
```python
bot = MT5TradingBot(
    risk_per_trade=0.05,        # 5% per trade (higher risk)
    max_daily_loss=0.10,        # 10% daily loss limit
    max_trades_per_day=10,      # More trades
)
```

### For Testing (Demo Account)
```python
bot = MT5TradingBot(
    symbols=['EURUSD', 'GBPUSD'],  # Start with 2 symbols
    risk_per_trade=0.02,
    max_daily_loss=0.05,
    max_trades_per_day=5,
)
```

## Next Steps

1. **Test on Demo Account First**
   - Verify bot works correctly
   - Monitor signals and trades
   - Adjust parameters as needed

2. **Backtest Strategy**
   - Use MT5's built-in tester
   - Test on historical data
   - Verify profitability

3. **Monitor Live Trading**
   - Start with small position sizes
   - Watch for unexpected behavior
   - Adjust risk parameters

4. **Optimize Performance**
   - Adjust check intervals
   - Fine-tune indicator settings
   - Add more symbols

## Support & Documentation

- MT5 Python API Docs: https://www.mql5.com/en/docs/python_metatrader5
- GitHub Issues: https://github.com/vitizelamabuza-ops/forex/issues
- PyPI MetaTrader5: https://pypi.org/project/MetaTrader5/

---

**Happy Trading! 🚀**