"""
Trading Strategy Implementation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradingSignal:
    signal: Signal
    confidence: float
    reason: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

class TechnicalAnalysis:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return np.mean(prices[-period:])
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return current_price, current_price, current_price
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[float, float, float]:
        """Calculate MACD"""
        if len(prices) < slow_period:
            return 0, 0, 0
        
        ema_fast = TechnicalAnalysis.calculate_ema(prices, fast_period)
        ema_slow = TechnicalAnalysis.calculate_ema(prices, slow_period)
        
        macd_line = ema_fast - ema_slow
        
        # For signal line, we need more historical data
        if len(prices) < slow_period + signal_period:
            signal_line = macd_line
        else:
            # Simplified signal line calculation
            signal_line = macd_line * 0.9  # Approximation
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

class TradingStrategy:
    """Main trading strategy class"""
    
    def __init__(self):
        self.ta = TechnicalAnalysis()
        # We'll get price history from API calls, not store locally
    
    def get_price_history_from_api(self, api_client, symbol: str, period: int = 50) -> List[float]:
        """Get price history from API for technical analysis"""
        # This would need to be implemented based on Recall API's historical data endpoint
        # For now, we'll use a simplified approach with current price
        try:
            price_data = api_client.get_price_data(self.get_token_address(symbol))
            if "error" not in price_data and "price" in price_data:
                current_price = float(price_data["price"])
                # Return a simple array with current price for basic analysis
                return [current_price] * min(period, 20)  # Simplified for now
        except:
            pass
        return []
    
    def get_token_address(self, symbol: str) -> str:
        """Get token address for symbol"""
        from config import Config
        for pair in Config.TRADING_PAIRS:
            if pair["symbol"] == symbol:
                return pair["to"]
        return Config.USDC_ADDRESS
    
    def analyze_symbol(self, symbol: str, api_client) -> TradingSignal:
        """Analyze a symbol and generate trading signal"""
        # Get price history from API
        prices = self.get_price_history_from_api(api_client, symbol)
        
        if len(prices) < 5:  # Minimum data for basic analysis
            return TradingSignal(
                signal=Signal.HOLD,
                confidence=0.0,
                reason="Insufficient price history from API"
            )
        
        current_price = prices[-1]
        
        # Calculate technical indicators
        rsi = self.ta.calculate_rsi(prices)
        sma_20 = self.ta.calculate_sma(prices, 20)
        sma_50 = self.ta.calculate_sma(prices, 50)
        upper_bb, middle_bb, lower_bb = self.ta.calculate_bollinger_bands(prices)
        macd, signal_line, histogram = self.ta.calculate_macd(prices)
        
        # Generate signals based on multiple indicators
        signals = []
        confidence_scores = []
        
        # RSI signals
        if rsi < 30:
            signals.append(Signal.BUY)
            confidence_scores.append(0.7)
        elif rsi > 70:
            signals.append(Signal.SELL)
            confidence_scores.append(0.7)
        else:
            signals.append(Signal.HOLD)
            confidence_scores.append(0.3)
        
        # Moving average signals
        if sma_20 > sma_50 and current_price > sma_20:
            signals.append(Signal.BUY)
            confidence_scores.append(0.6)
        elif sma_20 < sma_50 and current_price < sma_20:
            signals.append(Signal.SELL)
            confidence_scores.append(0.6)
        else:
            signals.append(Signal.HOLD)
            confidence_scores.append(0.4)
        
        # Bollinger Bands signals
        if current_price <= lower_bb:
            signals.append(Signal.BUY)
            confidence_scores.append(0.8)
        elif current_price >= upper_bb:
            signals.append(Signal.SELL)
            confidence_scores.append(0.8)
        else:
            signals.append(Signal.HOLD)
            confidence_scores.append(0.5)
        
        # MACD signals
        if macd > signal_line and histogram > 0:
            signals.append(Signal.BUY)
            confidence_scores.append(0.6)
        elif macd < signal_line and histogram < 0:
            signals.append(Signal.SELL)
            confidence_scores.append(0.6)
        else:
            signals.append(Signal.HOLD)
            confidence_scores.append(0.4)
        
        # Calculate weighted signal
        buy_count = signals.count(Signal.BUY)
        sell_count = signals.count(Signal.SELL)
        hold_count = signals.count(Signal.HOLD)
        
        # Calculate average confidence
        avg_confidence = np.mean(confidence_scores)
        
        # Determine final signal
        if buy_count > sell_count and buy_count > hold_count:
            final_signal = Signal.BUY
            confidence = avg_confidence * (buy_count / len(signals))
            reason = f"Buy signal: RSI={rsi:.1f}, Price vs SMA20={current_price/sma_20:.3f}, BB position={((current_price-lower_bb)/(upper_bb-lower_bb)):.3f}"
        elif sell_count > buy_count and sell_count > hold_count:
            final_signal = Signal.SELL
            confidence = avg_confidence * (sell_count / len(signals))
            reason = f"Sell signal: RSI={rsi:.1f}, Price vs SMA20={current_price/sma_20:.3f}, BB position={((current_price-lower_bb)/(upper_bb-lower_bb)):.3f}"
        else:
            final_signal = Signal.HOLD
            confidence = avg_confidence * (hold_count / len(signals))
            reason = f"Hold signal: Mixed indicators, RSI={rsi:.1f}, Price vs SMA20={current_price/sma_20:.3f}"
        
        # Calculate target price and stop loss
        target_price = None
        stop_loss = None
        
        if final_signal == Signal.BUY:
            target_price = current_price * 1.15  # 15% profit target
            stop_loss = current_price * 0.95     # 5% stop loss
        elif final_signal == Signal.SELL:
            target_price = current_price * 0.85  # 15% profit target
            stop_loss = current_price * 1.05     # 5% stop loss
        
        return TradingSignal(
            signal=final_signal,
            confidence=confidence,
            reason=reason,
            target_price=target_price,
            stop_loss=stop_loss
        )
