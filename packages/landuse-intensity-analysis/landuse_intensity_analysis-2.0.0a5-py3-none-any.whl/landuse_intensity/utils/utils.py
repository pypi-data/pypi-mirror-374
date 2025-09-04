"""
Essential utility functions for land use intensity analysis.

Simplified and modernized utility functions focusing on core functionality.
"""

import numpy as np
import pandas as pd
import re
import os
from typing import Union, Dict, List, Tuple


def demo_landscape(size: int = 100, 
                   classes: List[int] = None, 
                   fractions: List[float] = None) -> np.ndarray:
    """
    Generate demo landscape data for testing and examples.
    
    Parameters
    ----------
    size : int, default 100
        Size of the square landscape (size x size)
    classes : list of int, optional
        Land use classes to use (default: [1, 2, 3, 4])
    fractions : list of float, optional
        Fractions for each class (default: [0.4, 0.3, 0.2, 0.1])
    
    Returns
    -------
    np.ndarray
        Generated landscape array
    """
    if classes is None:
        classes = [1, 2, 3, 4]
    if fractions is None:
        fractions = [0.4, 0.3, 0.2, 0.1]
    
    # Ensure fractions sum to 1
    fractions = np.array(fractions)
    fractions = fractions / fractions.sum()
    
    # Generate landscape
    landscape = np.random.choice(classes, size=(size, size), p=fractions)
    
    return landscape





def validate_data(data: Union[np.ndarray, pd.DataFrame]) -> bool:
    """
    Validate contingency table or raster data.
    
    Parameters
    ----------
    data : array-like
        Data to validate
        
    Returns
    -------
    bool
        True if data is valid, False otherwise
    """
    if data is None:
        return False
    
    if isinstance(data, pd.DataFrame):
        data_array = data.values
    else:
        data_array = np.asarray(data)
    
    # Check for negative values
    if (data_array < 0).any():
        return False
    
    # Check for NaN or infinite values
    if not np.isfinite(data_array).all():
        return False
    
    return True
