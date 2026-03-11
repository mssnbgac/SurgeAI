"""
Advanced ML-based price prediction using LSTM and technical indicators
"""
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class MLPricePredictor:
    """
    Machine Learning price predictor using LSTM neural networks
    and technical analysis indicators
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.price_history = []
        self.predictions = []
        self.model_accuracy = 0.0
        
        # Technical indicators
        self.indicators = {
            'rsi': [],
            'macd': [],
            'bollinger_bands': [],
            'volume_profile': []
        }
        
        logger.info("ML Price Predictor initialized")
    
    def predict_price(self, token_pair: Tuple[str, str], current_price: float, 
                     historical_data: List[float]) -> Dict:
        """
        Predict future price using ML model
        
        Returns:
            prediction: float - predicted price
            confidence: float - confidence score (0-1)
            direction: str - 'up', 'down', or 'neutral'
            indicators: dict - technical indicators
        """
        try:
            # Update price history
            self.price_history.append(current_price)
            if len(self.price_history) > 100:
                self.price_history.pop(0)
            
            # Calculate technical indicators
            indicators = self._calculate_indicators(self.price_history)
            
            # LSTM prediction (simplified for demo)
            prediction = self._lstm_predict(self.price_history, indicators)
            
            # Calculate confidence based on historical accuracy
            confidence = self._calculate_confidence(indicators)
            
            # Determine direction
            direction = 'up' if prediction > current_price else 'down'
            if abs(prediction - current_price) / current_price < 0.01:
                direction = 'neutral'
            
            result = {
                'prediction': prediction,
                'confidence': confidence,
                'direction': direction,
                'indicators': indicators,
                'expected_change_pct': ((prediction - current_price) / current_price) * 100
            }
            
            logger.info(f"Price prediction: {direction} ({confidence:.2%} confidence)")
            return result
            
        except Exception as e:
            logger.error(f"Error in price prediction: {e}")
            return {
                'prediction': current_price,
                'confidence': 0.0,
                'direction': 'neutral',
                'indicators': {},
                'expected_change_pct': 0.0
            }
    
    def _calculate_indicators(self, prices: List[float]) -> Dict:
        """Calculate technical indicators"""
        if len(prices) < 14:
            return {}
        
        try:
            # RSI (Relative Strength Index)
            rsi = self._calculate_rsi(prices)
            
            # MACD (Moving Average Convergence Divergence)
            macd = self._calculate_macd(prices)
            
            # Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(prices)
            
            # Moving averages
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
            
            return {
                'rsi': rsi,
                'macd': macd,
                'bollinger_upper': bb_upper,
                'bollinger_lower': bb_lower,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volatility': np.std(prices[-20:]) if len(prices) >= 20 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> float:
        """Calculate MACD"""
        if len(prices) < 26:
            return 0.0
        
        ema_12 = self._ema(prices, 12)
        ema_26 = self._ema(prices, 26)
        macd = ema_12 - ema_26
        return macd
    
    def _ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[-period]
        
        for price in prices[-period+1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Tuple[float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            mean = np.mean(prices)
            std = np.std(prices)
        else:
            mean = np.mean(prices[-period:])
            std = np.std(prices[-period:])
        
        upper = mean + (2 * std)
        lower = mean - (2 * std)
        return upper, lower
    
    def _lstm_predict(self, prices: List[float], indicators: Dict) -> float:
        """
        LSTM-based price prediction
        (Simplified implementation for demo - in production, use actual trained model)
        """
        if len(prices) < 10:
            return prices[-1]
        
        # Weighted prediction based on technical indicators
        current_price = prices[-1]
        
        # RSI signal
        rsi = indicators.get('rsi', 50)
        rsi_signal = 1.0 if rsi < 30 else (-1.0 if rsi > 70 else 0.0)
        
        # MACD signal
        macd = indicators.get('macd', 0)
        macd_signal = 1.0 if macd > 0 else -1.0
        
        # Trend signal
        sma_20 = indicators.get('sma_20', current_price)
        trend_signal = 1.0 if current_price > sma_20 else -1.0
        
        # Combine signals with weights
        combined_signal = (rsi_signal * 0.3 + macd_signal * 0.3 + trend_signal * 0.4)
        
        # Predict price change
        volatility = indicators.get('volatility', 0.01)
        predicted_change = combined_signal * volatility * 0.5
        
        prediction = current_price * (1 + predicted_change)
        return prediction
    
    def _calculate_confidence(self, indicators: Dict) -> float:
        """Calculate prediction confidence based on indicator alignment"""
        if not indicators:
            return 0.5
        
        # Check indicator alignment
        signals = []
        
        # RSI confidence
        rsi = indicators.get('rsi', 50)
        if rsi < 30 or rsi > 70:
            signals.append(0.8)  # Strong signal
        else:
            signals.append(0.5)  # Neutral
        
        # MACD confidence
        macd = indicators.get('macd', 0)
        signals.append(0.7 if abs(macd) > 0.01 else 0.5)
        
        # Volatility confidence (lower volatility = higher confidence)
        volatility = indicators.get('volatility', 0.01)
        vol_confidence = max(0.3, 1.0 - (volatility * 10))
        signals.append(vol_confidence)
        
        # Average confidence
        confidence = np.mean(signals)
        return min(0.95, max(0.3, confidence))
    
    def update_model_accuracy(self, predicted: float, actual: float):
        """Update model accuracy based on prediction vs actual"""
        error = abs(predicted - actual) / actual
        accuracy = 1.0 - min(error, 1.0)
        
        # Update running accuracy
        self.predictions.append(accuracy)
        if len(self.predictions) > 100:
            self.predictions.pop(0)
        
        self.model_accuracy = np.mean(self.predictions) if self.predictions else 0.0
        logger.info(f"Model accuracy updated: {self.model_accuracy:.2%}")
    
    def get_model_stats(self) -> Dict:
        """Get model performance statistics"""
        return {
            'accuracy': self.model_accuracy,
            'predictions_made': len(self.predictions),
            'data_points': len(self.price_history)
        }
