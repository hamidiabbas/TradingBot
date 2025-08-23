<<<<<<< HEAD
"""Utils package"""
=======
"""
Utilities package for TradingBot v1.0
"""

# Import commonly used functions for easy access
try:
    from .logger import setup_logging, Logger, get_logger, set_log_level
    from .price_action import calculate_fibonacci_retracements, calculate_fibonacci_extensions
    from .technical_indicators import calculate_sma, calculate_ema, calculate_rsi
except ImportError as e:
    print(f"Warning: Could not import some utility functions: {e}")

__version__ = "1.0.0"
__all__ = [
    'setup_logging', 'Logger', 'get_logger', 'set_log_level',
    'calculate_fibonacci_retracements', 'calculate_fibonacci_extensions',
    'calculate_sma', 'calculate_ema', 'calculate_rsi'
]
>>>>>>> 8f626e2ef1a5d0198eacb62ca49d93985fc3b2f3
