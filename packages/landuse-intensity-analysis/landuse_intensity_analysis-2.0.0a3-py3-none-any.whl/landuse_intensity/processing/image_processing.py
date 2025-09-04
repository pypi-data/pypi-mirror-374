"""
Essential image processing for land use change analysis.

Simplified image processing functions focusing on core functionality
needed for contingency table generation and basic spatial analysis.
"""

import numpy as np
from typing import Tuple, Optional, Dict, List
from scipy import ndimage


def create_contingency_table(raster1: np.ndarray, raster2: np.ndarray, 
                            labels1: Optional[List] = None, 
                            labels2: Optional[List] = None) -> np.ndarray:
    """
    Create contingency table from two raster arrays.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period raster
    raster2 : np.ndarray  
        Second time period raster
    labels1 : list, optional
        Labels for raster1 classes
    labels2 : list, optional
        Labels for raster2 classes
        
    Returns
    -------
    np.ndarray
        Contingency table showing transitions between time periods
    """
    # Validate inputs
    if raster1.shape != raster2.shape:
        raise ValueError("Rasters must have the same shape")
    
    # Get unique values
    unique1 = np.unique(raster1)
    unique2 = np.unique(raster2)
    
    # Create contingency table
    contingency = np.zeros((len(unique1), len(unique2)), dtype=int)
    
    for i, val1 in enumerate(unique1):
        for j, val2 in enumerate(unique2):
            mask = (raster1 == val1) & (raster2 == val2)
            contingency[i, j] = np.sum(mask)
    
    return contingency


def calculate_change_map(raster1: np.ndarray, raster2: np.ndarray) -> np.ndarray:
    """
    Calculate binary change map.
    
    Parameters
    ----------
    raster1 : np.ndarray
        First time period
    raster2 : np.ndarray
        Second time period
        
    Returns
    -------
    np.ndarray
        Binary change map (1 = change, 0 = no change)
    """
    return (raster1 != raster2).astype(int)



