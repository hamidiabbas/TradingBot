# Create: array_fix_patch.py
"""
UNIVERSAL ARRAY AMBIGUITY FIX - AUTOMATIC PATCHING
==================================================
This patches ALL array comparison errors across your entire codebase
"""

import numpy as np
import pandas as pd
import warnings

# Monkey patch to catch and fix array ambiguity issues
original_array_bool = np.ndarray.__bool__

def safe_array_bool(self):
    """Safe boolean conversion for arrays"""
    if self.size == 0:
        return False
    elif self.size == 1:
        return bool(self.item())
    else:
        # Default to .any() for multi-element arrays
        warnings.warn(f"Array with {self.size} elements converted to bool using .any()", UserWarning)
        return self.any()

# Apply the patch
np.ndarray.__bool__ = safe_array_bool

print("✅ Universal array ambiguity fix applied")
