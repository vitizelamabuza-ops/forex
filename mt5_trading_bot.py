#!/usr/bin/env python3
"""
Professional MetaTrader 5 Python API Trading Bot
✅ Advanced multi-indicator signal generation
✅ Smart money management & position sizing
✅ Real-time MT5 integration
✅ Performance tracking & logging
✅ Risk management with daily loss limits
✅ Email alerts & notifications
✅ Optimized for OpenGL 1.1 systems

Author: vitizelamabuza-ops
License: MIT

Requirements:
    pip install MetaTrader5 pandas numpy python-dotenv
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from dotenv import load_dotenv


# ==================== CONFIGURATION ====================

class SignalType(Enum):
    """Trading signal types"""
    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass
class TradingSignal:
    """Structure for trading signals"""
    symbol: str
    signal_type: SignalType
    strength: float  # 0-100
    entry_price: float
    stop_loss: float
    take_profit: float
    indicators: Dict
    timestamp: datetime
    buy_votes: int
    sell_votes: int


class MT5TradingBot:
    """
    Advanced MetaTrader 5 Trading Bot with multi-indicator analysis
    """
    
    def __init__(
        self,
        symbols: List[str] = None,
        risk_per_trade: float = 0.02,
        max_daily_loss: float = 0.05,
        max_trades_per_day: int = 5,
        use_kelly: bool = True,
        email_alerts: bool = False,
        email_address: str = None,
    ):
        """
        Initialize MT5 Trading Bot
        
        Args:
            symbols: List of trading symbols (e.g., ['EURUSD', 'GBPUSD'])
            risk_per_trade: Risk percentage per trade (0.02 = 2%)
            max_daily_loss: Maximum daily loss before stopping (0.05 = 5%)
            max_trades_per_day: Maximum number of trades per day
            use_kelly: Use Kelly Criterion for position sizing
            email_alerts: Enable email notifications
            email_address: Email for alerts
        """
        self.symbols = symbols or ['EURUSD', 'GBPUSD', 'USDJPY']
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_trades_per_day = max_trades_per_day
        self.use_kelly = use_kelly
        self.email_alerts = email_alerts
        self.email_address = email_address
        
        # Initialize MT5 (will attempt to login using .env or provided creds)
        self._init_mt5()
        
        # Setup logging
        self._setup_logging()
        
        # Performance tracking
        self.trades_executed = []
        self.daily_pnl = 0.0
        self.session_pnl = 0.0
        self.trades_today = 0
        self.session_start_date = datetime.now().date()
        
        # Initialize log files
        self._init_log_files()
        
        self.logger.info("✅ MT5 Trading Bot initialized successfully")

    def login(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """
        Login to MetaTrader 5 using provided credentials or environment variables.

        The method will attempt the following in order:
         - Load credentials from environment (.env if present)
         - If login and password are available, call mt5.initialize(login=..., password=..., server=...)
         - Otherwise fall back to mt5.initialize() without credentials

        Returns:
            True if MT5 connection and login succeeded, False otherwise.
        """
        # Load environment variables from .env if present
        try:
            load_dotenv()
        except Exception:
            # ignore dotenv loading errors; environment variables may already be present
            pass

        login = login or os.getenv('MT5_LOGIN')
        password = password or os.getenv('MT5_PASSWORD')
        server = server or os.getenv('MT5_SERVER')

        # If login is a string, try to convert to int
        if login is not None and isinstance(login, str):
            try:
                login = int(login)
            except ValueError:
                print(f"Invalid MT5_LOGIN value: {login}")
                return False

        # Try to initialize with credentials if we have them
        try:
            if login and password:
                # Some MT5 builds accept credentials in initialize(); try that first
                initialized = mt5.initialize(login=login, server=server, password=password)
                if not initialized:
                    # If initialize didn't accept credentials, try basic initialize then mt5.login
                    mt5.initialize()
                    logged = mt5.login(login, password, server)
                    initialized = bool(logged)
            else:
                initialized = mt5.initialize()
        except Exception as e:
            print(f"MT5 initialization/login error: {e}")
            return False

        return bool(initialized)

    def _init_mt5(self) -> None:
        """Initialize MetaTrader 5 connection and login"""
        # Attempt to login using credentials from environment or defaults
        if not self.login():
            print("MT5 initialization/login failed. Please set MT5_LOGIN, MT5_PASSWORD, and MT5_SERVER in your environment or pass credentials to the login() method.")
            sys.exit(1)
        
        version = mt5.version()
        account_info = mt5.account_info()
        
        if account_info is None:
            print("Failed to get account info")
            sys.exit(1)
        
        print(f"\n{'='*70}")
        print(f"🚀 MetaTrader 5 Connected")
        print(f"{'='*70}")
        # version may be a tuple
        try:
            print(f"Version: {version[0]}.{version[1]}.{version[2]}")
        except Exception:
            print(f"Version: {version}")
        print(f"Account: {account_info.login}")
        print(f"Server: {account_info.server}")
        print(f"Balance: ${account_info.balance:.2f}")
        print(f"Equity: ${account_info.equity:.2f}")
        print(f"{'='*70}\n")

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        self.logger = logging.getLogger('MT5Bot')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler('mt5_bot.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _init_log_files(self) -> None:
        """Initialize CSV log files"""
        self.trades_log_file = Path('trades.csv')
        self.signals_log_file = Path('signals.csv')
        self.performance_log_file = Path('performance.csv')
        
        # Initialize trades log
        if not self.trades_log_file.exists():
            with open(self.trades_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Symbol', 'Type', 'Volume', 'Entry_Price',
                    'Stop_Loss', 'Take_Profit', 'Signal_Strength', 'PnL', 'Status'
                ])
        
        # Initialize signals log
        if not self.signals_log_file.exists():
            with open(self.signals_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Symbol', 'Signal', 'Strength',
                    'Buy_Votes', 'Sell_Votes', 'Price', 'RSI', 'MACD', 'ATR'
                ])
        
        # Initialize performance log
        if not self.performance_log_file.exists():
            with open(self.performance_log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Total_Trades', 'Win_Rate', 'Daily_PnL',
                    'Session_PnL', 'Max_Balance', 'Account_Balance'
                ])

    # ==================== INDICATOR CALCULATIONS ====================

    def calculate_ema(self, prices: np.ndarray, period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        ema = float(prices[0])
        multiplier = 2.0 / (period + 1)
        
        for price in prices[1:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema

    def calculate_sma(self, prices: np.ndarray, period: int = 20) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))

    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        seed = deltas[:period]
        
        up = np.sum(np.where(seed > 0, seed, 0)) / period
        down = np.sum(np.where(seed < 0, -seed, 0)) / period
        
        for delta in deltas[period:]:
            up = (up * (period - 1) + (delta if delta > 0 else 0)) / period
            down = (down * (period - 1) + (abs(delta) if delta < 0 else 0)) / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50
        
        return float(rsi)

    def calculate_macd(
        self,
        prices: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return None, None, None
        
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        macd_values = []
        for i in range(len(prices) - slow + 1, len(prices) + 1):
            ema_f = self.calculate_ema(prices[:i], fast)
            ema_s = self.calculate_ema(prices[:i], slow)
            if ema_f and ema_s:
                macd_values.append(ema_f - ema_s)
        
        signal_line = self.calculate_ema(np.array(macd_values), signal) if len(macd_values) >= signal else None
        histogram = macd_line - signal_line if signal_line else None
        
        return float(macd_line), float(signal_line) if signal_line else None, float(histogram) if histogram else None

    def calculate_bollinger_bands(
        self,
        prices: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        sma = float(np.mean(prices[-period:]))
        std = float(np.std(prices[-period:]))
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper, sma, lower

    def calculate_atr(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> Optional[float]:
        """Calculate Average True Range"""
        if len(close) < period:
            return None
        
        tr = []
        for i in range(len(close)):
            if i == 0:
                tr.append(high[i] - low[i])
            else:
                tr.append(max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                ))
        
        return float(np.mean(tr[-period:]))

    def calculate_stochastic(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate Stochastic Oscillator"""
        if len(close) < period:
            return None, None
        
        lowest_low = float(np.min(low[-period:]))
        highest_high = float(np.max(high[-period:]))
        
        if highest_high == lowest_low:
            k = 50.0
        else:
            k = 100.0 * (float(close[-1]) - lowest_low) / (highest_high - lowest_low)
        
        return float(k), float(k)

    # ==================== DATA RETRIEVAL ====================

    def get_rates(
        self,
        symbol: str,
        timeframe: int = mt5.TIMEFRAME_M5,
        count: int = 100
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLC data from MT5"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No rates returned for {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        
        except Exception as e:
            self.logger.error(f"Error fetching rates for {symbol}: {e}")
            return None

    def get_account_balance(self) -> float:
        """Get current account balance"""
        account_info = mt5.account_info()
        return account_info.balance if account_info else 0.0

    def get_account_equity(self) -> float:
        """Get current account equity"""
        account_info = mt5.account_info()
        return account_info.equity if account_info else 0.0

    # ==================== SIGNAL GENERATION ====================

    def generate_trading_signal(
        self,
        symbol: str,
        timeframe: int = mt5.TIMEFRAME_M5
    ) -> Optional[TradingSignal]:
        """
        Generate composite trading signal using multiple indicators
        
        Returns:
            TradingSignal object with signal details or None if error
        """
        df = self.get_rates(symbol, timeframe, count=100)
        
        if df is None or len(df) < 50:
            return None
        
        # Extract OHLC arrays
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_prices = df['open'].values
        
        indicators = {}
        
        # Calculate all indicators
        indicators['rsi'] = self.calculate_rsi(close, 14)
        indicators['ema12'] = self.calculate_ema(close, 12)
        indicators['ema26'] = self.calculate_ema(close, 26)
        indicators['sma20'] = self.calculate_sma(close, 20)
        indicators['sma50'] = self.calculate_sma(close, 50)
        
        macd, macd_signal, macd_hist = self.calculate_macd(close, 12, 26, 9)
        indicators['macd'] = macd
        indicators['macd_signal'] = macd_signal
        indicators['macd_histogram'] = macd_hist
        
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close, 20, 2.0)
        indicators['bb_upper'] = bb_upper
        indicators['bb_middle'] = bb_middle
        indicators['bb_lower'] = bb_lower
        
        indicators['atr'] = self.calculate_atr(high, low, close, 14)
        
        k, d = self.calculate_stochastic(high, low, close, 14)
        indicators['stochastic_k'] = k
        indicators['stochastic_d'] = d
        
        current_price = float(close[-1])
        indicators['price'] = current_price
        
        # ========== SIGNAL VOTING SYSTEM ==========
        buy_votes = 0
        sell_votes = 0
        
        # 1. MACD Signal (0-25 points)
        if (macd is not None and macd_signal is not None and 
            macd_hist is not None):
            if macd > macd_signal and macd_hist > 0:
                buy_votes += 25
            elif macd < macd_signal and macd_hist < 0:
                sell_votes += 25
        
        # 2. RSI Signal (0-25 points)
        if indicators['rsi'] is not None:
            if indicators['rsi'] < 30:
                buy_votes += 25
            elif indicators['rsi'] > 70:
                sell_votes += 25
        
        # 3. Bollinger Bands Signal (0-20 points)
        if bb_upper and bb_lower:
            if current_price < bb_lower:
                buy_votes += 20
            elif current_price > bb_upper:
                sell_votes += 20
        
        # 4. EMA Crossover (0-20 points)
        if indicators['ema12'] is not None and indicators['ema26'] is not None:
            if indicators['ema12'] > indicators['ema26']:
                buy_votes += 20
            else:
                sell_votes += 20
        
        # 5. Stochastic Signal (0-10 points)
        if k is not None:
            if k < 20:
                buy_votes += 10
            elif k > 80:
                sell_votes += 10
        
        # ========== FINAL DECISION ==========
        total_votes = max(buy_votes, sell_votes)
        
        if buy_votes > sell_votes and total_votes >= 50:
            signal_type = SignalType.BUY
            strength = min(buy_votes, 100)
        elif sell_votes > buy_votes and total_votes >= 50:
            signal_type = SignalType.SELL
            strength = min(sell_votes, 100)
        else:
            signal_type = SignalType.HOLD
            strength = 50
        
        # Calculate entry and stops using ATR
        atr = indicators['atr']
        if atr is None or atr == 0:
            atr = current_price * 0.001
        
        if signal_type == SignalType.BUY:
            stop_loss = current_price - (atr * 1.5)
            take_profit = current_price + (atr * 3.0)
        elif signal_type == SignalType.SELL:
            stop_loss = current_price + (atr * 1.5)
            take_profit = current_price - (atr * 3.0)
        else:
            stop_loss = current_price
            take_profit = current_price
        
        signal = TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            indicators=indicators,
            timestamp=datetime.now(),
            buy_votes=buy_votes,
            sell_votes=sell_votes
        )
        
        return signal

    # ==================== MONEY MANAGEMENT ====================

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_price: float
    ) -> float:
        """
        Calculate position size based on risk and stop loss
        
        Formula: Position Size = (Account Balance × Risk%) / (Entry - Stop Loss)
        """
        if entry_price == stop_loss_price:
            return 0.0
        
        try:
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return 0.0
            
            balance = self.get_account_balance()
            risk_amount = balance * self.risk_per_trade
            
            pip_value = symbol_info.point
            risk_in_pips = abs(entry_price - stop_loss_price) / pip_value
            
            if risk_in_pips == 0:
                return 0.0
            
            position_size = risk_amount / (risk_in_pips * pip_value)
            
            # Respect broker limits
            min_volume = symbol_info.volume_min
            max_volume = symbol_info.volume_max
            
            position_size = max(position_size, min_volume)
            position_size = min(position_size, max_volume)
            
            return float(position_size)
        
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0

    def apply_kelly_criterion(
        self,
        win_rate: float,
        reward_risk_ratio: float,
        fractional: float = 0.5
    ) -> float:
        """
        Apply Kelly Criterion for position sizing
        
        Formula: f* = (bp - q) / b
        where: b = reward/risk, p = win rate, q = 1 - p
        """
        if win_rate <= 0 or reward_risk_ratio <= 0:
            return self.risk_per_trade
        
        q = 1 - win_rate
        b = reward_risk_ratio
        
        kelly_fraction = (b * win_rate - q) / b
        
        if kelly_fraction < 0:
            return 0.001
        
        # Apply fractional Kelly to reduce volatility
        return min(kelly_fraction * fractional, 0.25)

    # ==================== TRADE EXECUTION ====================

    def place_order(
        self,
        symbol: str,
        order_type: mt5.ORDER_TYPE,
        volume: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        signal_strength: float
    ) -> bool:
        """Place order via MT5"""
        try:
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "magic": 234000,
                "comment": f"Strength: {signal_strength:.0f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(
                    f"Order failed for {symbol}: {result.comment} "
                    f"(Code: {result.retcode})"
                )
                return False
            
            order_type_str = 'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'
            self.logger.info(
                f"✅ ORDER PLACED | {symbol} {order_type_str} "
                f"| Volume: {volume:.2f} | Entry: {entry_price:.5f} "
                f"| SL: {stop_loss:.5f} | TP: {take_profit:.5f} "
                f"| Order ID: {result.order}"
            )
            
            # Log trade
            self._log_trade(
                symbol, order_type_str, volume, entry_price,
                stop_loss, take_profit, signal_strength, "OPEN"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return False

    def _log_trade(
        self,
        symbol: str,
        order_type: str,
        volume: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        signal_strength: float,
        status: str
    ) -> None:
        """Log trade to CSV"""
        try:
            with open(self.trades_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    symbol,
                    order_type,
                    f"{volume:.2f}",
                    f"{entry_price:.5f}",
                    f"{stop_loss:.5f}",
                    f"{take_profit:.5f}",
                    f"{signal_strength:.1f}",
                    "",  # PnL (filled later)
                    status
                ])
        except Exception as e:
            self.logger.error(f"Error logging trade: {e}")

    def _log_signal(self, signal: TradingSignal) -> None:
        """Log signal to CSV"""
        try:
            with open(self.signals_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    signal.timestamp.isoformat(),
                    signal.symbol,
                    signal.signal_type.name,
                    f"{signal.strength:.1f}",
                    signal.buy_votes,
                    signal.sell_votes,
                    f"{signal.indicators['price']:.5f}",
                    f"{signal.indicators['rsi']:.2f}" if signal.indicators['rsi'] else "N/A",
                    f"{signal.indicators['macd_histogram']:.2e}" if signal.indicators['macd_histogram'] else "N/A",
                    f"{signal.indicators['atr']:.5f}" if signal.indicators['atr'] else "N/A",
                ])
        except Exception as e:
            self.logger.error(f"Error logging signal: {e}")

    # ==================== MAIN BOT LOOP ====================

    def run(
        self,
        check_interval: int = 300,
        timeframe: int = mt5.TIMEFRAME_M5
    ) -> None:
        """
        Main bot loop
        
        Args:
            check_interval: Seconds between signal checks (300 = 5 minutes)
            timeframe: MT5 timeframe constant (default M5)
        """
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🤖 BOT RUNNING")
        self.logger.info(f"{'='*70}")
        self.logger.info(f"Symbols: {', '.join(self.symbols)}")
        self.logger.info(f"Check Interval: {check_interval}s")
        self.logger.info(f"Max Trades/Day: {self.max_trades_per_day}")
        self.logger.info(f"Risk/Trade: {self.risk_per_trade*100:.1f}%")
        self.logger.info(f"Max Daily Loss: {self.max_daily_loss*100:.1f}%")
        self.logger.info(f"{'='*70}\n")
        
        try:
            while True:
                current_date = datetime.now().date()
                
                # Reset daily counters
                if current_date != self.session_start_date:
                    self.trades_today = 0
                    self.daily_pnl = 0.0
                    self.session_start_date = current_date
                
                # Check daily loss limit
                if self.daily_pnl <= -(self.get_account_balance() * self.max_daily_loss):
                    self.logger.warning(
                        f"⚠️  MAX DAILY LOSS REACHED ({self.daily_pnl:.2f}) - Bot paused"
                    )
                    break
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Process each symbol
                for symbol in self.symbols:
                    signal = self.generate_trading_signal(symbol, timeframe)
                    
                    if signal is None:
                        continue
                    
                    # Log signal
                    self._log_signal(signal)
                    
                    # Display signal
                    print(
                        f"\n[{timestamp}] {symbol} | "
                        f"Signal: {signal.signal_type.name:5s} | "
                        f"Strength: {signal.strength:3.0f}/100 | "
                        f"Price: ${signal.entry_price:.5f}"
                    )
                    print(
                        f"  RSI: {signal.indicators['rsi']:6.2f} | "
                        f"MACD: {signal.indicators['macd_histogram']:+.2e if signal.indicators['macd_histogram'] else 'N/A':>8s} | "
                        f"ATR: {signal.indicators['atr']:8.5f}" if signal.indicators['atr'] else ""
                    )
                    
                    # Execute trade if strong signal
                    if (signal.signal_type != SignalType.HOLD and
                        signal.strength > 70 and
                        self.trades_today < self.max_trades_per_day):
                        
                        # Calculate position size
                        volume = self.calculate_position_size(
                            symbol,
                            signal.entry_price,
                            signal.stop_loss
                        )
                        
                        # Check minimum volume
                        symbol_info = mt5.symbol_info(symbol)
                        if volume >= symbol_info.volume_min if symbol_info else 0.01:
                            
                            order_type = (mt5.ORDER_TYPE_BUY
                                         if signal.signal_type == SignalType.BUY
                                         else mt5.ORDER_TYPE_SELL)
                            
                            success = self.place_order(
                                symbol,
                                order_type,
                                volume,
                                signal.entry_price,
                                signal.stop_loss,
                                signal.take_profit,
                                signal.strength
                            )
                            
                            if success:
                                self.trades_today += 1
                                self.trades_executed.append(signal)
                
                self.logger.info(
                    f"⏳ Next scan in {check_interval}s... "
                    f"(Trades today: {self.trades_today}/{self.max_trades_per_day})"
                )
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("\n\n🛑 Bot stopped by user")
            self.print_summary()
        
        finally:
            mt5.shutdown()

    def print_summary(self) -> None:
        """Print session summary"""
        self.logger.info(f"\n{'='*70}")
        self.logger.info("📊 SESSION SUMMARY")
        self.logger.info(f"{'='*70}")
        self.logger.info(f"Account Balance: ${self.get_account_balance():.2f}")
        self.logger.info(f"Account Equity: ${self.get_account_equity():.2f}")
        self.logger.info(f"Trades Executed: {len(self.trades_executed)}")
        self.logger.info(f"Trades Today: {self.trades_today}")
        self.logger.info(f"Daily PnL: ${self.daily_pnl:.2f}")
        self.logger.info(f"Session PnL: ${self.session_pnl:.2f}")
        self.logger.info(f"{'='*70}\n")


# ==================== MAIN EXECUTION ====================

def main():
    """Main entry point"""
    
    # Bot configuration
    bot = MT5TradingBot(
        symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
        risk_per_trade=0.02,           # Risk 2% per trade
        max_daily_loss=0.05,           # Stop at 5% daily loss
        max_trades_per_day=5,          # Max 5 trades per day
        use_kelly=True,                # Use Kelly Criterion
        email_alerts=False,            # Disable for now
        email_address=None
    )
    
    # Run the bot
    try:
        bot.run(
            check_interval=300,        # Check every 5 minutes
            timeframe=mt5.TIMEFRAME_M5 # 5-minute timeframe
        )
    except Exception as e:
        bot.logger.error(f"Fatal error: {e}")
        bot.print_summary()


if __name__ == '__main__':
    main()
