"""
Recall Trading Agent Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration - Get from environment variables
    SANDBOX_API_KEY = os.getenv("RECALL_SANDBOX_API_KEY", "")
    PRODUCTION_API_KEY = os.getenv("RECALL_PRODUCTION_API_KEY", "")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")
    
    # API URLs
    SANDBOX_BASE_URL = "https://api.sandbox.competitions.recall.network"
    PRODUCTION_BASE_URL = "https://api.competitions.recall.network"
    
    # Trading Configuration - Get from environment variables
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))  # 10% of portfolio
    RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", "0.02"))    # 2% risk per trade
    STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", "0.05"))  # 5% stop loss
    TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", "0.15"))  # 15% take profit
    
    # Token Addresses (Mainnet)
    USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    
    # Trading Pairs
    TRADING_PAIRS = [
        {"from": USDC_ADDRESS, "to": WETH_ADDRESS, "symbol": "WETH"},
        {"from": USDC_ADDRESS, "to": WBTC_ADDRESS, "symbol": "WBTC"},
        {"from": USDC_ADDRESS, "to": USDT_ADDRESS, "symbol": "USDT"}
    ]
    
    @classmethod
    def get_api_key(cls):
        if cls.ENVIRONMENT == "production":
            api_key = cls.PRODUCTION_API_KEY
        else:
            api_key = cls.SANDBOX_API_KEY
        
        if not api_key:
            raise ValueError(f"API key not found for environment: {cls.ENVIRONMENT}. Please set RECALL_{cls.ENVIRONMENT.upper()}_API_KEY environment variable.")
        
        return api_key
    
    @classmethod
    def get_base_url(cls):
        if cls.ENVIRONMENT == "production":
            return cls.PRODUCTION_BASE_URL
        return cls.SANDBOX_BASE_URL
