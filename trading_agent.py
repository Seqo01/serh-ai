"""
Recall Trading Agent - Main Entry Point
"""
import time
import schedule
import signal
import sys
from typing import Optional
from config import Config
from recall_api import RecallAPI
from portfolio_manager import PortfolioManager

class TradingAgent:
    """Main trading agent class"""
    
    def __init__(self):
        self.api = RecallAPI()
        self.portfolio_manager = PortfolioManager()
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Initialize the trading agent"""
        print("Initializing...")
        
        # Check API health
        health = self.api.health_check()
        if "error" in health:
            print(f"API Health Check Failed: {health['error']}")
            return False
        
        print("API Health Check Passed")
        
        # Get agent info
        agent_info = self.api.get_agent_info()
        if "error" not in agent_info:
            print(f"Agent Info: {agent_info}")
        else:
            print(f"Could not get agent info: {agent_info.get('error', 'Unknown error')}")
        
        # Get initial portfolio
        portfolio = self.api.get_portfolio()
        if "error" not in portfolio:
            print(f"Initial Portfolio: {portfolio}")
        else:
            print(f"Could not get portfolio: {portfolio.get('error', 'Unknown error')}")
        
        # Get available competitions
        competitions = self.api.get_competitions()
        if "error" not in competitions:
            print(f"Available Competitions: {len(competitions.get('competitions', []))}")
        else:
            print(f"Could not get competitions: {competitions.get('error', 'Unknown error')}")
        
        print("Initialized Successfully")
        return True
    
    def run_single_cycle(self):
        """Run a single trading cycle"""
        try:
            self.portfolio_manager.run_trading_cycle()
        except Exception as e:
            print(f"Error in trading cycle: {e}")
    
    def run_continuous(self, interval_minutes: int = 5):
        """Run the agent continuously"""
        print(f"Starting continuous trading with {interval_minutes} minute intervals")
        
        # Schedule trading cycles
        schedule.every(interval_minutes).minutes.do(self.run_single_cycle)
        
        # Run initial cycle
        self.run_single_cycle()
        
        self.running = True
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping trading agent...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
        
        print("Trading agent stopped")
    
    def run_backtest(self, duration_hours: int = 24):
        """Run a backtest simulation"""
        print(f"Running backtest for {duration_hours} hours")
        
        cycles = duration_hours * 12  # 5-minute cycles
        
        for i in range(cycles):
            print(f"\n--- Backtest Cycle {i+1}/{cycles} ---")
            self.run_single_cycle()
            time.sleep(0.1)  # Small delay for readability
        
        print("Backtest completed")
    
    def test_api_connection(self):
        """Test API connection and basic functionality"""
        print("Testing API Connection...")
        
        # Test health check
        health = self.api.health_check()
        if "error" in health:
            print(f"Health check failed: {health['error']}")
            return False
        print("Health check passed")
        
        # Test price data
        price_data = self.api.get_price_data(Config.WETH_ADDRESS)
        if "error" in price_data:
            print(f"Price data failed: {price_data['error']}")
            return False
        print(f"Price data: {price_data}")
        
        # Test portfolio
        portfolio = self.api.get_portfolio()
        if "error" in portfolio:
            print(f"Portfolio data failed: {portfolio['error']}")
            return False
        print(f"Portfolio data: {portfolio}")
        
        return True

def main():
    """Main entry point"""
    print("Starting...")
    print(f"Environment: {Config.ENVIRONMENT}")
    
    agent = TradingAgent()
    
    # Initialize agent
    if not agent.initialize():
        print("Failed to initialize agent")
        return
    
    # Test API connection
    if not agent.test_api_connection():
        print("API connection test failed")
        return
    
    # Choose running mode
    print("\nChoose running mode:")
    print("1. Single cycle (test)")
    print("2. Continuous trading")
    print("3. Backtest simulation")
    print("4. Exit")
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            print("Running single trading cycle...")
            agent.run_single_cycle()
        elif choice == "2":
            interval = input("Enter trading interval in minutes (default 5): ").strip()
            interval = int(interval) if interval.isdigit() else 5
            agent.run_continuous(interval)
        elif choice == "3":
            duration = input("Enter backtest duration in hours (default 24): ").strip()
            duration = int(duration) if duration.isdigit() else 24
            agent.run_backtest(duration)
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
