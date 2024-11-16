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

MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

def fetch_market_data() -> Dict[str, float]:
    """Fetch real-time prices and historical data for USD/EUR with retry mechanism."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get("https://api.fbs.com/market_data/usd_eur")
            response.raise_for_status()
            data = response.json()
            logging.info("Market data fetched successfully.")
            return data
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logging.error("All retry attempts failed. Unable to fetch market data.")
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
    logging.info(f"Starting trade loop. Mode: {'Simulation' if simulate else 'Execution'}")
    logging.info(f"Starting trade loop. Mode: {'Simulation' if simulate else 'Execution'}")
    balance = 1000  # Starting balance in USD
    open_orders = 0
    market_data = fetch_market_data()
    for day_data in market_data:
        logging.info(f"Simulating day {day_data['day']} with price {day_data['price']}")
            print(Fore.BLUE + "Retrying to fetch market data...")
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
            print(Fore.RED + "Trade skipped: Risk management limits exceeded or max open orders reached.")
        
        logging.info(f"End of day {day_data['day']}. Current balance: ${balance}")
        print(Fore.GREEN + f"End of day {day_data['day']}. Current balance: ${balance}")
    logging.info("Simulation completed.")
    print(Fore.YELLOW + "Simulation completed.")
    logging.info("Trade loop terminated.")
    print(Fore.YELLOW + "Trade loop terminated.")

if __name__ == "__main__":
    simulate_mode = input("Enter 's' to simulate trades or 'e' to execute trades: ").strip().lower() == 's'
    trade_loop(simulate=simulate_mode)
