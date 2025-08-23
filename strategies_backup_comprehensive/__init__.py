"""
Trading Strategies Package
Contains all trading strategies for the TradingBot
"""

class PrimaryStrategy:
    """Base strategy class for compatibility"""
    
    def __init__(self):
        self.name = "PrimaryStrategy"
    
    def analyze(self, data, symbol="EURUSD"):
        """Basic analyze method"""
        try:
            if data is None or data.empty or len(data) < 10:
                return {'signal': 'HOLD', 'confidence': 0.5, 'price': 1.0}
            
            current_price = data['close'].iloc[-1]
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'price': current_price,
                'reason': 'PrimaryStrategy default'
            }
        except:
            return {'signal': 'HOLD', 'confidence': 0.5, 'price': 1.0}

# Make available for import
__all__ = ['PrimaryStrategy']
