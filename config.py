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
    
    # Popular Tokens - Major Cryptocurrencies
    LINK_ADDRESS = "0x514910771AF9Ca656af840dff83E8264EcF986CA"  # Chainlink
    UNI_ADDRESS = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"  # Uniswap
    AAVE_ADDRESS = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"  # Aave
    MATIC_ADDRESS = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"  # Polygon (MATIC)
    AVAX_ADDRESS = "0x85f138bfEE4ef8e540890CFb48F620571d67Eda3"  # Avalanche (WAVAX on Ethereum)
    SOL_ADDRESS = "0xD31a59c85aE9D8edEFeC411D448f90841571b89c"  # Solana (Wrapped SOL on Ethereum)
    ADA_ADDRESS = "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47"  # Cardano (Wrapped ADA on Ethereum)
    DOT_ADDRESS = "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402"  # Polkadot (Wrapped DOT on Ethereum)
    ATOM_ADDRESS = "0x8D983cb9388EaC77af0474fA441C4815500Cb7BB"  # Cosmos (Wrapped ATOM on Ethereum)
    BNB_ADDRESS = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"  # Binance Coin (Wrapped BNB on Ethereum)
    
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
