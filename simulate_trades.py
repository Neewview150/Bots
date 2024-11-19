import logging
from typing import Dict, List
import requests
from colorama import init, Fore

# Configure logging
logging.basicConfig(filename='simulation_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='w')
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

def fetch_historical_data() -> List[Dict[str, float]]:
    """Fetch historical prices for USD/EUR."""
    try:
        response = requests.get("https://api.fbs.com/historical_data/usd_eur")
        response.raise_for_status()
        data = response.json()
        logging.info("Historical data fetched successfully.")
        return data
    except requests.RequestException as e:
        logging.error(f"Error fetching historical data: {e}")
        return []

def calculate_trading_fees(trade_amount: float) -> float:
    """Calculate trading fees."""
    fee_percentage = 0.001  # 0.1% trading fee
    return trade_amount * fee_percentage

def simulate_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Simulate a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    logging.info(f"Simulating trade: Amount = ${trade_amount}, Leverage = {leverage}")
    profit = trade_amount * 0.01  # Simulate a 1% profit
    fees = calculate_trading_fees(trade_amount)
    net_profit = profit - fees
    return {"amount": trade_amount, "profit": net_profit}

def simulate_trades():
    """Simulate trades using historical data."""
    balance = 1000  # Starting balance in USD
    historical_data = fetch_historical_data()
    if not historical_data:
        print(Fore.BLUE + "Failed to fetch historical data.")
        return

    for data_point in historical_data:
        if risk_management(TRADE_AMOUNT, balance):
            result = simulate_trade(TRADE_AMOUNT, leverage=True)
            balance += result["profit"]
            logging.info(f"Simulated trade result: {result}, New balance: ${balance}")
            print(Fore.BLUE + f"Simulated trade executed. New balance: ${balance}")
        else:
            logging.warning("Trade exceeds risk management limits.")

if __name__ == "__main__":
    simulate_trades()