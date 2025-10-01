"""
Configuration
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
    SANDBOX_BASE_URL = "https://api.sandbox.example.com"
    PRODUCTION_BASE_URL = "https://api.example.com"
    
    # Trading Configuration - Get from environment variables
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))  # 10% of portfolio
    RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", "0.02"))    # 2% risk per trade
    STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", "0.05"))  # 5% stop loss
    TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", "0.15"))  # 15% take profit
    
    # Token Addresses
    USDC_ADDRESS = "0x0000000000000000000000000000000000000000"
    WETH_ADDRESS = "0x0000000000000000000000000000000000000000"
    WBTC_ADDRESS = "0x0000000000000000000000000000000000000000"
    USDT_ADDRESS = "0x0000000000000000000000000000000000000000"
    
    # Popular Tokens
    LINK_ADDRESS = "0x0000000000000000000000000000000000000000"
    UNI_ADDRESS = "0x0000000000000000000000000000000000000000"
    AAVE_ADDRESS = "0x0000000000000000000000000000000000000000"
    MATIC_ADDRESS = "0x0000000000000000000000000000000000000000"
    AVAX_ADDRESS = "0x0000000000000000000000000000000000000000"
    SOL_ADDRESS = "0x0000000000000000000000000000000000000000"
    ADA_ADDRESS = "0x0000000000000000000000000000000000000000"
    DOT_ADDRESS = "0x0000000000000000000000000000000000000000"
    ATOM_ADDRESS = "0x0000000000000000000000000000000000000000"
    BNB_ADDRESS = "0x0000000000000000000000000000000000000000"
    
    # Trading Pairs - Popular Tokens Only
    TRADING_PAIRS = [
        # Major Tokens
        {"from": USDC_ADDRESS, "to": WETH_ADDRESS, "symbol": "WETH"},
        {"from": USDC_ADDRESS, "to": WBTC_ADDRESS, "symbol": "WBTC"},
        {"from": USDC_ADDRESS, "to": USDT_ADDRESS, "symbol": "USDT"},
        
        # Popular Altcoins
        {"from": USDC_ADDRESS, "to": LINK_ADDRESS, "symbol": "LINK"},
        {"from": USDC_ADDRESS, "to": UNI_ADDRESS, "symbol": "UNI"},
        {"from": USDC_ADDRESS, "to": AAVE_ADDRESS, "symbol": "AAVE"},
        {"from": USDC_ADDRESS, "to": MATIC_ADDRESS, "symbol": "MATIC"},
        {"from": USDC_ADDRESS, "to": AVAX_ADDRESS, "symbol": "AVAX"},
        {"from": USDC_ADDRESS, "to": SOL_ADDRESS, "symbol": "SOL"},
        {"from": USDC_ADDRESS, "to": ADA_ADDRESS, "symbol": "ADA"},
        {"from": USDC_ADDRESS, "to": DOT_ADDRESS, "symbol": "DOT"},
        {"from": USDC_ADDRESS, "to": ATOM_ADDRESS, "symbol": "ATOM"},
        {"from": USDC_ADDRESS, "to": BNB_ADDRESS, "symbol": "BNB"},
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
