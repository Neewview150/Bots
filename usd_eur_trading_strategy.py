import logging
import time
from typing import Dict

# Configure logging
logging.basicConfig(filename='trade_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

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

def execute_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Execute a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    # Simulate trade execution
    logging.info(f"Executing trade: Amount = ${trade_amount}, Leverage = {leverage}")
    # Here you would integrate with FBS API to execute the trade
    return {"amount": trade_amount, "profit": trade_amount * 0.01}  # Simulate a 1% profit

def simulate_trade(trade_amount: float, leverage: bool = False) -> Dict[str, float]:
    """Simulate a trade with or without leverage."""
    if leverage:
        trade_amount = calculate_leverage(trade_amount)
    logging.info(f"Simulating trade: Amount = ${trade_amount}, Leverage = {leverage}")
    return {"amount": trade_amount, "profit": trade_amount * 0.01}  # Simulate a 1% profit

def trade_loop(simulate: bool = True):
    """Continuously execute or simulate trades until stopped by the user."""
    balance = 1000  # Starting balance in USD
    while True:
        if risk_management(TRADE_AMOUNT, balance):
            if simulate:
                result = simulate_trade(TRADE_AMOUNT, leverage=True)
            else:
                result = execute_trade(TRADE_AMOUNT, leverage=True)
            balance += result["profit"]
            logging.info(f"Trade result: {result}, New balance: ${balance}")
        else:
            logging.warning("Trade exceeds risk management limits.")
        
        print("Press Enter to stop or wait for the next trade...")
        try:
            time.sleep(5)  # Wait for 5 seconds before the next trade
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    simulate_mode = input("Enter 's' to simulate trades or 'e' to execute trades: ").strip().lower() == 's'
    trade_loop(simulate=simulate_mode)
