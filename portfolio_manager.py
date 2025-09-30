"""
Portfolio Management System
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import Config
from recall_api import RecallAPI
from trading_strategy import TradingStrategy, Signal, TradingSignal

@dataclass
class Position:
    symbol: str
    amount: float
    entry_price: float
    current_price: float
    timestamp: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PortfolioManager:
    """Manages portfolio and trading decisions"""
    
    def __init__(self):
        self.api = RecallAPI()
        self.strategy = TradingStrategy()
        self.positions: Dict[str, Position] = {}
        self.max_position_size = Config.MAX_POSITION_SIZE
        self.risk_tolerance = Config.RISK_TOLERANCE
        self.portfolio_data = None
        
    def get_portfolio_value(self) -> float:
        """Get portfolio value from Recall API"""
        portfolio = self.api.get_portfolio()
        if "error" not in portfolio and "totalValue" in portfolio:
            return float(portfolio["totalValue"])
        elif "error" not in portfolio and "balance" in portfolio:
            return float(portfolio["balance"])
        else:
            print(f"Could not get portfolio value: {portfolio.get('error', 'Unknown error')}")
            return 0.0
    
    def get_available_balance(self) -> float:
        """Get available balance from Recall API"""
        portfolio = self.api.get_portfolio()
        if "error" not in portfolio and "balance" in portfolio:
            return float(portfolio["balance"])
        elif "error" not in portfolio and "availableBalance" in portfolio:
            return float(portfolio["availableBalance"])
        else:
            print(f"Could not get balance: {portfolio.get('error', 'Unknown error')}")
            return 0.0
    
    def get_position_size(self, symbol: str, price: float) -> float:
        """Calculate position size based on risk management"""
        portfolio_value = self.get_portfolio_value()
        available_balance = self.get_available_balance()
        max_position_value = portfolio_value * self.max_position_size
        
        # Calculate position size based on risk tolerance
        risk_amount = portfolio_value * self.risk_tolerance
        stop_loss_distance = price * 0.05  # 5% stop loss
        
        if stop_loss_distance > 0:
            position_size = min(risk_amount / stop_loss_distance, max_position_value / price)
        else:
            position_size = max_position_value / price
        
        # Ensure we don't exceed available balance
        return min(position_size, available_balance / price)
    
    def should_open_position(self, symbol: str, signal: TradingSignal) -> bool:
        """Determine if we should open a new position"""
        if signal.signal == Signal.HOLD:
            return False
        
        if signal.confidence < 0.6:  # Minimum confidence threshold
            return False
        
        # Check if we already have a position in this symbol (from API)
        portfolio = self.api.get_portfolio()
        if "error" not in portfolio and "positions" in portfolio:
            for position in portfolio["positions"]:
                if position.get("symbol") == symbol and float(position.get("amount", 0)) > 0:
                    return False
        
        # Check if we have enough balance
        position_size = self.get_position_size(symbol, signal.target_price or 0)
        if position_size <= 0:
            return False
        
        return True
    
    def should_close_position(self, symbol: str, current_price: float) -> bool:
        """Determine if we should close an existing position"""
        # Get current positions from API
        portfolio = self.api.get_portfolio()
        if "error" in portfolio or "positions" not in portfolio:
            return False
        
        # Find position for this symbol
        position_data = None
        for position in portfolio["positions"]:
            if position.get("symbol") == symbol and float(position.get("amount", 0)) > 0:
                position_data = position
                break
        
        if not position_data:
            return False
        
        entry_price = float(position_data.get("entryPrice", 0))
        if entry_price <= 0:
            return False
        
        # Check stop loss (5% loss)
        stop_loss_price = entry_price * 0.95
        if current_price <= stop_loss_price:
            return True
        
        # Check take profit (15% profit)
        take_profit_price = entry_price * 1.15
        if current_price >= take_profit_price:
            return True
        
        # Check if position is profitable and we want to take profits (10% profit)
        profit_percentage = (current_price - entry_price) / entry_price
        if profit_percentage > 0.1:
            return True
        
        return False
    
    def execute_trade(self, from_token: str, to_token: str, amount: float, reason: str) -> bool:
        """Execute a trade through Recall API"""
        try:
            result = self.api.execute_trade(
                from_token=from_token,
                to_token=to_token,
                amount=str(amount),
                reason=reason
            )
            
            if "error" not in result:
                print(f"Trade executed: {reason}")
                return True
            else:
                print(f"Trade failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Trade execution error: {e}")
            return False
    
    def open_position(self, symbol: str, signal: TradingSignal, current_price: float):
        """Open a new position"""
        position_size = self.get_position_size(symbol, current_price)
        
        if position_size <= 0:
            print(f"Cannot open position for {symbol}: insufficient balance")
            return
        
        # Execute buy trade (USDC to target token)
        from_token = Config.USDC_ADDRESS
        to_token = self.get_token_address(symbol)
        
        trade_amount = position_size * current_price
        
        if self.execute_trade(from_token, to_token, trade_amount, f"Buy {symbol}: {signal.reason}"):
            print(f"Opened position: {symbol}, Size: {position_size:.4f}, Price: {current_price:.2f}")
            # Position will be tracked by Recall API, no need for local tracking
    
    def close_position(self, symbol: str, current_price: float):
        """Close an existing position"""
        # Get current positions from API
        portfolio = self.api.get_portfolio()
        if "error" in portfolio or "positions" not in portfolio:
            return
        
        # Find position for this symbol
        position_data = None
        for position in portfolio["positions"]:
            if position.get("symbol") == symbol and float(position.get("amount", 0)) > 0:
                position_data = position
                break
        
        if not position_data:
            return
        
        # Execute sell trade (target token to USDC)
        from_token = self.get_token_address(symbol)
        to_token = Config.USDC_ADDRESS
        
        trade_amount = float(position_data.get("amount", 0))
        entry_price = float(position_data.get("entryPrice", 0))
        
        if self.execute_trade(from_token, to_token, trade_amount, f"Sell {symbol} at {current_price:.2f}"):
            # Calculate P&L
            pnl = (current_price - entry_price) * trade_amount
            pnl_percentage = (current_price - entry_price) / entry_price * 100 if entry_price > 0 else 0
            
            print(f"Closed position: {symbol}, P&L: {pnl:.2f} ({pnl_percentage:.2f}%)")
    
    def get_token_address(self, symbol: str) -> str:
        """Get token address for symbol"""
        for pair in Config.TRADING_PAIRS:
            if pair["symbol"] == symbol:
                return pair["to"]
        return Config.USDC_ADDRESS
    
    def update_positions(self):
        """Update current prices for all positions from API"""
        # Get current portfolio from API
        portfolio = self.api.get_portfolio()
        if "error" in portfolio or "positions" not in portfolio:
            return
        
        for position_data in portfolio["positions"]:
            symbol = position_data.get("symbol")
            amount = float(position_data.get("amount", 0))
            
            if not symbol or amount <= 0:
                continue
            
            try:
                # Get current price
                price_data = self.api.get_price_data(self.get_token_address(symbol))
                if "error" not in price_data and "price" in price_data:
                    current_price = float(price_data["price"])
                    
                    # Check if we should close this position
                    if self.should_close_position(symbol, current_price):
                        self.close_position(symbol, current_price)
                        
            except Exception as e:
                print(f"Error updating position {symbol}: {e}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\nRunning trading cycle - Portfolio Value: ${self.get_portfolio_value():.2f}")
        
        # Update existing positions
        self.update_positions()
        
        # Analyze each trading pair
        for pair in Config.TRADING_PAIRS:
            symbol = pair["symbol"]
            
            try:
                # Get current price
                price_data = self.api.get_price_data(pair["to"])
                if "error" in price_data:
                    print(f"Error getting price for {symbol}: {price_data['error']}")
                    continue
                
                current_price = float(price_data["price"])
                
                # Generate trading signal
                signal = self.strategy.analyze_symbol(symbol, self.api)
                
                print(f"{symbol}: Price=${current_price:.2f}, Signal={signal.signal.value}, Confidence={signal.confidence:.2f}")
                
                # Check if we should open a new position
                if self.should_open_position(symbol, signal):
                    self.open_position(symbol, signal, current_price)
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        # Print portfolio summary
        self.print_portfolio_summary()
    
    def print_portfolio_summary(self):
        """Print current portfolio summary from API"""
        portfolio = self.api.get_portfolio()
        if "error" in portfolio:
            print(f"\nPortfolio Summary: Error - {portfolio['error']}")
            return
        
        balance = portfolio.get("balance", 0)
        total_value = portfolio.get("totalValue", 0)
        positions = portfolio.get("positions", [])
        
        print(f"\nPortfolio Summary:")
        print(f"   Balance: ${balance:.2f}")
        print(f"   Total Value: ${total_value:.2f}")
        print(f"   Positions: {len(positions)}")
        
        for position_data in positions:
            symbol = position_data.get("symbol", "Unknown")
            amount = float(position_data.get("amount", 0))
            entry_price = float(position_data.get("entryPrice", 0))
            current_price = float(position_data.get("currentPrice", 0))
            
            if amount > 0 and entry_price > 0:
                pnl = (current_price - entry_price) * amount
                pnl_percentage = (current_price - entry_price) / entry_price * 100
                print(f"   {symbol}: {amount:.4f} @ ${current_price:.2f} (P&L: ${pnl:.2f}, {pnl_percentage:.2f}%)")
