#!/usr/bin/env python3
"""
Compatibility utilities for strategy system
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

class CompatibilityLayer:
    """Compatibility layer for different data formats"""
    
    def __init__(self):
        self.supported_formats = ['MT5', 'CSV', 'JSON']
    
    def normalize_data(self, data: Any, source_format: str = 'MT5') -> pd.DataFrame:
        """Normalize data from different sources"""
        if isinstance(data, pd.DataFrame):
            return self.normalize_dataframe(data)
        elif isinstance(data, dict):
            return self.dict_to_dataframe(data)
        elif isinstance(data, list):
            return self.list_to_dataframe(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame columns"""
        # Standardize column names
        column_mapping = {
            'Open': 'open', 'HIGH': 'high', 'Low': 'low', 'Close': 'close',
            'Volume': 'volume', 'Time': 'time', 'Timestamp': 'time'
        }
        
        df_normalized = df.copy()
        df_normalized.columns = [column_mapping.get(col, col.lower()) for col in df.columns]
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df_normalized.columns:
                df_normalized[col] = df_normalized.get('close', 0)
        
        return df_normalized
    
    def dict_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """Convert dictionary to DataFrame"""
        return pd.DataFrame([data])
    
    def list_to_dataframe(self, data: List) -> pd.DataFrame:
        """Convert list to DataFrame"""
        if all(isinstance(item, dict) for item in data):
            return pd.DataFrame(data)
        else:
            return pd.DataFrame({'value': data})
    
    def validate_compatibility(self, df: pd.DataFrame) -> bool:
        """Validate data compatibility"""
        required_columns = ['open', 'high', 'low', 'close']
        return all(col in df.columns for col in required_columns)
