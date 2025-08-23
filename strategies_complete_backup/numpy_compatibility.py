"""
NumPy Compatibility Module
Provides NaN and other deprecated numpy imports for legacy code
"""

import numpy as np
import warnings

# Suppress numpy warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Provide NaN compatibility
try:
    from numpy import NaN
except ImportError:
    NaN = np.nan

try:
    from numpy import Inf
except ImportError:
    Inf = np.inf

# Additional compatibility
NINF = np.NINF if hasattr(np, 'NINF') else -np.inf
PZERO = 0.0
NZERO = -0.0

# Export all
__all__ = ['NaN', 'Inf', 'NINF', 'PZERO', 'NZERO', 'np']
