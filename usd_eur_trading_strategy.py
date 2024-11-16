import logging
import time
from typing import Dict
import requests
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
    return trade_amount <= balance * risk_threshold

def fetch_market_data() -> Dict[str, float]:
    """Fetch real-time prices and historical data for USD/EUR."""
    try:
        response = requests.get("https://api.fbs.com/market_data/usd_eur")
        response.raise_for_status()
        data = response.json()
        logging.info("Market data fetched successfully.")
        return data
    except requests.RequestException as e:
        logging.error(f"Error fetching market data: {e}")
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
    logging.info(f"Executing trade: Amount = ${trade_amount}, Leverage = {leverage}")
    # Here you would integrate with FBS API to execute the trade
    profit = trade_amount * 0.01  # Simulate a 1% profit
    fees = calculate_trading_fees(trade_amount)
    net_profit = profit - fees
    return {"amount": trade_amount, "profit": net_profit}

def simulate_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Simulate a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    logging.info(f"Simulating trade: Amount = ${trade_amount}, Leverage = {leverage}")
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

if __name__ == "__main__":
    simulate_mode = input("Enter 's' to simulate trades or 'e' to execute trades: ").strip().lower() == 's'
    trade_loop(simulate=simulate_mode)
