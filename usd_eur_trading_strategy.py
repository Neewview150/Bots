import logging
import time
from typing import Dict, List, Tuple
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from colorama import init, Fore

# Configure logging
logging.basicConfig(filename='trade_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='w')
init(autoreset=True)

# Constants
LEVERAGE = 100
TRADE_AMOUNT = 2  # Base trade amount in USD
MAX_LEVERAGE_TRADE = TRADE_AMOUNT * LEVERAGE

def calculate_leverage(amount: float) -> float:
    """Calculate the leveraged amount."""
    return amount * LEVERAGE

def risk_management(trade_amount: float, balance: float) -> bool:
    """Ensure the trade does not exceed a certain percentage of the balance."""
    risk_threshold = 0.02  # Risk 2% of the balance
    return trade_amount <= balance * risk_threshold and trade_amount <= MAX_LEVERAGE_TRADE

def fetch_market_data() -> Dict[str, float]:
    """Fetch real-time prices and historical data for USD/EUR using OANDA API."""
    try:
        url = "https://api-fxpractice.oanda.com/v3/instruments/EUR_USD/candles"
        headers = {
            "Authorization": "Bearer <YOUR_OANDA_API_TOKEN>"
        }
        params = {
            "count": 1,
            "granularity": "M1"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info("Market data fetched successfully.")
        return data
    except requests.RequestException as e:
        logging.error(f"Error fetching market data: {e}", exc_info=True)
        return {}

def calculate_trading_fees(trade_amount: float) -> float:
    """Calculate trading fees."""
    fee_percentage = 0.001  # 0.1% trading fee
    return trade_amount * fee_percentage

def execute_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Execute a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    # Simulate trade execution
    logging.info(f"Executing trade: Amount = ${trade_amount}, Leverage = {leverage}, Balance before trade: ${balance}")
    # Here you would integrate with FBS API to execute the trade
    profit = trade_amount * 0.01  # Simulate a 1% profit
    fees = calculate_trading_fees(trade_amount)
    net_profit = profit - fees
    return {"amount": trade_amount, "profit": net_profit}

def simulate_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Simulate a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    logging.info(f"Simulating trade: Amount = ${trade_amount}, Leverage = {leverage}, Balance before simulation: ${balance}")
    return {"amount": trade_amount, "profit": trade_amount * 0.01}  # Simulate a 1% profit

def trade_loop(simulate: bool = True):
    """Continuously execute or simulate trades until stopped by the user."""
    balance = 1000  # Starting balance in USD
    open_orders = 0
    while True:
        market_data = fetch_market_data()
        if not market_data:
            print(Fore.BLUE + "Failed to fetch market data. Retrying...")
            continue
        
        if risk_management(TRADE_AMOUNT, balance) and open_orders < 5:
            if simulate:
                result = simulate_trade(TRADE_AMOUNT, leverage=True)
            else:
                result = execute_trade(TRADE_AMOUNT, leverage=True)
            balance += result["profit"]
            open_orders += 1
            logging.info(f"Trade result: {result}, New balance: ${balance}")
            print(Fore.BLUE + f"Trade executed. New balance: ${balance}")
        else:
            logging.warning("Trade exceeds risk management limits or max open orders reached.")
        
        print(Fore.BLUE + "Press Enter to stop or wait for the next trade...")
        try:
            time.sleep(5)  # Wait for 5 seconds before the next trade
        except KeyboardInterrupt:
            break

class StrategyBacktester:
    def __init__(self, symbol: str, start_date: str, end_date: str, initial_balance: float = 10000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.ema_period = 200
        self.g_channel_length = 10
        self.trade_amount = 5000
        self.take_profit_amount = 1
        self.stop_loss_amount = 250
        self.trades: List[Dict] = []
        self.position = 0
        self.entry_price = None
        self.data = None

    def fetch_historical_data(self) -> pd.DataFrame:
        """Fetch historical data from OANDA"""
        try:
            start = datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')
            end = datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')
            
            url = f"https://api-fxpractice.oanda.com/v3/instruments/{self.symbol}/candles"
            params = {
                'from': start,
                'to': end,
                'granularity': 'M15',
                'price': 'MBA'
            }
            headers = {
                'Authorization': 'Bearer YOUR_OANDA_API_TOKEN'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            candles = response.json()['candles']
            
            data = []
            for candle in candles:
                data.append({
                    'timestamp': pd.to_datetime(candle['time']),
                    'bid': float(candle['bid']['c']),
                    'ask': float(candle['ask']['c']),
                    'mid': float(candle['mid']['c'])
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            raise

    def calculate_ema(self, prices: pd.Series) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=self.ema_period, adjust=False).mean()

    def calculate_g_channel(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate G-Channel signals"""
        a = b = prices.iloc[0]
        a_values = []
        b_values = []
        
        for price in prices:
            a = max(price, a) - (a - b) / self.g_channel_length
            b = min(price, b) + (a - b) / self.g_channel_length
            a_values.append(a)
            b_values.append(b)
            
        return pd.Series(a_values, index=prices.index), pd.Series(b_values, index=prices.index)

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on strategy"""
        df = self.data.copy()
        
        df['ema'] = self.calculate_ema(df['mid'])
        a_line, b_line = self.calculate_g_channel(df['mid'])
        df['g_channel_avg'] = (a_line + b_line) / 2
        
        df['signal'] = 0
        df['signal'] = np.where((df['mid'] > df['g_channel_avg']) & 
                              (df['mid'].shift(1) <= df['g_channel_avg']), 1, df['signal'])
        df['signal'] = np.where((df['mid'] < df['g_channel_avg']) & 
                              (df['mid'].shift(1) >= df['g_channel_avg']), -1, df['signal'])
        
        return df

    def run_backtest(self):
        """Run the backtest simulation"""
        logging.info("Starting backtest...")
        
        self.data = self.fetch_historical_data()
        df = self.generate_signals()
        
        current_position = 0
        entry_price = None
        
        for i in range(1, len(df)):
            current_price = df.iloc[i]
            
            if current_position != 0:
                pnl = (current_price['mid'] - entry_price) * current_position * self.trade_amount
                
                if pnl >= self.take_profit_amount:
                    self.close_position(current_price, 'take_profit', pnl)
                    current_position = 0
                    entry_price = None
                    continue
                
                if pnl <= -self.stop_loss_amount:
                    self.close_position(current_price, 'stop_loss', pnl)
                    current_position = 0
                    entry_price = None
                    continue
            
            if current_position == 0 and current_price['signal'] != 0:
                if current_price['signal'] == 1:
                    current_position = 1
                    entry_price = current_price['ask']
                    self.open_position(current_price, 'buy')
                elif current_price['signal'] == -1:
                    current_position = -1
                    entry_price = current_price['bid']
                    self.open_position(current_price, 'sell')
        
        self.generate_report()

    def open_position(self, price_data: pd.Series, direction: str):
        """Record opening of a position"""
        self.trades.append({
            'timestamp': price_data.name,
            'type': direction,
            'entry_price': price_data['ask'] if direction == 'buy' else price_data['bid'],
            'position_size': self.trade_amount,
            'status': 'open'
        })

    def close_position(self, price_data: pd.Series, reason: str, pnl: float):
        """Record closing of a position"""
        last_trade = self.trades[-1]
        last_trade.update({
            'exit_price': price_data['bid'] if last_trade['type'] == 'buy' else price_data['ask'],
            'exit_time': price_data.name,
            'pnl': pnl,
            'reason': reason,
            'status': 'closed'
        })
        self.balance += pnl

    def generate_report(self):
        """Generate and display backtest results"""
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        
        total_trades = len(closed_trades)
        profitable_trades = len([t for t in closed_trades if t['pnl'] > 0])
        total_profit = sum(t['pnl'] for t in closed_trades)
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        
        print("\n=== Backtest Results ===")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Balance: ${self.initial_balance:,.2f}")
        print(f"Final Balance: ${self.balance:,.2f}")
        print(f"Total Return: {((self.balance - self.initial_balance) / self.initial_balance * 100):,.2f}%")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Profit/Loss: ${total_profit:,.2f}")
        
        self.plot_equity_curve()

    def plot_equity_curve(self):
        """Plot equity curve and drawdown"""
        closed_trades = [t for t in self.trades if t['status'] == 'closed']
        
        if not closed_trades:
            return
        
        equity = [self.initial_balance]
        dates = [closed_trades[0]['timestamp']]
        
        for trade in closed_trades:
            equity.append(equity[-1] + trade['pnl'])
            dates.append(trade['exit_time'])
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, equity, label='Equity Curve')
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Account Value ($)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    simulate_mode = input("Enter 's' to simulate trades or 'e' to execute trades: ").strip().lower() == 's'
    if simulate_mode:
        trade_loop(simulate=simulate_mode)
    else:
        backtest = StrategyBacktester(
            symbol="EUR_USD",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_balance=10000
        )
        backtest.run_backtest()