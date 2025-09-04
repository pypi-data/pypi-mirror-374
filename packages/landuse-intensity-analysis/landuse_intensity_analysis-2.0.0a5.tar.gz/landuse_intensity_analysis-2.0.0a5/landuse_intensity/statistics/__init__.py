"""
Statistics module for land use change analysis.

This module provides statistical analysis functions for land use change data,
including transition statistics, change intensity metrics, and summary statistics.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import os
import re


class LandUseStatistics:
    """
    Statistical analysis class for land use change data.

    Provides methods for calculating various statistics on land use transitions,
    including change intensities, persistence rates, and summary metrics.
    """

    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialize with land use transition data.

        Args:
            data: DataFrame with transition data (From, To, km2 columns)
        """
        self.data = data

    def load_data(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]):
        """Load transition data."""
        # Simple data loading without format adapter
        if isinstance(data, pd.DataFrame):
            self.data = data
        else:
            self.data = pd.DataFrame(data)

    def calculate_change_intensity(self) -> pd.DataFrame:
        """
        Calculate change intensity for each land use class.

        Returns:
            DataFrame with change intensity metrics
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")

        # Calculate total area for each class
        from_totals = self.data.groupby('From')['km2'].sum()
        to_totals = self.data.groupby('To')['km2'].sum()

        # Calculate change intensity
        results = []

        for class_name in set(self.data['From'].unique()) | set(self.data['To'].unique()):
            from_area = from_totals.get(class_name, 0)
            to_area = to_totals.get(class_name, 0)

            # Change intensity = (gains + losses) / (2 * average area)
            gains = self.data[(self.data['From'] != class_name) &
                            (self.data['To'] == class_name)]['km2'].sum()
            losses = self.data[(self.data['From'] == class_name) &
                             (self.data['To'] != class_name)]['km2'].sum()

            avg_area = (from_area + to_area) / 2
            if avg_area > 0:
                intensity = (gains + losses) / (2 * avg_area)
            else:
                intensity = 0

            results.append({
                'class': class_name,
                'from_area': from_area,
                'to_area': to_area,
                'gains': gains,
                'losses': losses,
                'change_intensity': intensity
            })

        return pd.DataFrame(results)

    def calculate_persistence_rate(self) -> pd.DataFrame:
        """
        Calculate persistence rate for each land use class.

        Returns:
            DataFrame with persistence rates
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")

        results = []

        for class_name in self.data['From'].unique():
            # Persistence = area that stayed the same
            persistence = self.data[(self.data['From'] == class_name) &
                                  (self.data['To'] == class_name)]['km2'].sum()

            total_from = self.data[self.data['From'] == class_name]['km2'].sum()

            if total_from > 0:
                persistence_rate = persistence / total_from
            else:
                persistence_rate = 0

            results.append({
                'class': class_name,
                'persistence_area': persistence,
                'total_from_area': total_from,
                'persistence_rate': persistence_rate
            })

        return pd.DataFrame(results)

    def calculate_transition_matrix(self) -> pd.DataFrame:
        """
        Calculate transition matrix showing flows between classes.

        Returns:
            Pivot table with transition matrix
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")

        return self.data.pivot_table(
            values='km2',
            index='From',
            columns='To',
            aggfunc='sum',
            fill_value=0
        )

    def calculate_net_change(self) -> pd.DataFrame:
        """
        Calculate net change for each land use class.

        Returns:
            DataFrame with net change metrics
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")

        results = []

        for class_name in set(self.data['From'].unique()) | set(self.data['To'].unique()):
            gains = self.data[(self.data['From'] != class_name) &
                            (self.data['To'] == class_name)]['km2'].sum()
            losses = self.data[(self.data['From'] == class_name) &
                             (self.data['To'] != class_name)]['km2'].sum()

            net_change = gains - losses

            results.append({
                'class': class_name,
                'gains': gains,
                'losses': losses,
                'net_change': net_change
            })

        return pd.DataFrame(results)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics.

        Returns:
            Dictionary with various summary statistics
        """
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")

        total_area = self.data['km2'].sum()
        total_transitions = len(self.data)
        unique_classes = len(set(self.data['From'].unique()) | set(self.data['To'].unique()))

        # Calculate change metrics
        change_data = self.data[self.data['From'] != self.data['To']]
        total_change_area = change_data['km2'].sum()
        change_percentage = (total_change_area / total_area) * 100 if total_area > 0 else 0

        return {
            'total_area': total_area,
            'total_transitions': total_transitions,
            'unique_classes': unique_classes,
            'total_change_area': total_change_area,
            'change_percentage': change_percentage,
            'persistence_area': total_area - total_change_area,
            'persistence_percentage': 100 - change_percentage
        }


def calculate_change_intensity(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Convenience function to calculate change intensity.

    Args:
        data: Transition data

    Returns:
        DataFrame with change intensity metrics
    """
    stats = LandUseStatistics()
    stats.load_data(data)
    return stats.calculate_change_intensity()


def calculate_persistence_rate(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Convenience function to calculate persistence rates.

    Args:
        data: Transition data

    Returns:
        DataFrame with persistence rates
    """
    stats = LandUseStatistics()
    stats.load_data(data)
    return stats.calculate_persistence_rate()


def calculate_net_change(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Convenience function to calculate net change.

    Args:
        data: Transition data

    Returns:
        DataFrame with net change metrics
    """
    stats = LandUseStatistics()
    stats.load_data(data)
    return stats.calculate_net_change()


def get_summary_statistics(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Convenience function to get summary statistics.

    Args:
        data: Transition data

    Returns:
        Dictionary with summary statistics
    """
    stats = LandUseStatistics()
    stats.load_data(data)
    return stats.get_summary_statistics()


def calculate_area_matrix(contingency_table: pd.DataFrame, 
                         pixel_area: float = 1.0) -> pd.DataFrame:
    """
    Convert contingency table from pixel counts to area units.
    
    Parameters
    ----------
    contingency_table : pd.DataFrame
        Contingency table in pixel counts
    pixel_area : float
        Area of each pixel in desired units (e.g., hectares, km²)
        
    Returns
    -------
    pd.DataFrame
        Contingency table in area units
    """
    return contingency_table * pixel_area


def get_change_summary(contingency_table: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics from contingency table.
    
    Parameters
    ----------
    contingency_table : pd.DataFrame
        Transition matrix
        
    Returns
    -------
    dict
        Summary statistics including persistence, change, gains, losses
    """
    data = contingency_table.values
    
    # Total area
    total_area = data.sum()
    
    # Persistence (diagonal)
    persistence = np.diag(data).sum()
    
    # Total change
    total_change = total_area - persistence
    
    # Per-class statistics
    gains = data.sum(axis=0) - np.diag(data)  # Column sums minus diagonal
    losses = data.sum(axis=1) - np.diag(data)  # Row sums minus diagonal
    net_change = gains - losses
    
    return {
        'total_area': total_area,
        'persistence': persistence,
        'total_change': total_change,
        'change_percent': (total_change / total_area) * 100,
        'gains': gains.tolist(),
        'losses': losses.tolist(),
        'net_change': net_change.tolist(),
        'classes': list(contingency_table.columns)
    }


def format_area_label(area: float, units: str = "pixels") -> str:
    """
    Format area value for display.
    
    Parameters
    ----------
    area : float
        Area value
    units : str
        Units (pixels, hectares, km², etc.)
        
    Returns
    -------
    str
        Formatted area string
    """
    if area >= 1e6:
        return f"{area/1e6:.2f}M {units}"
    elif area >= 1e3:
        return f"{area/1e3:.2f}K {units}"
    else:
        return f"{area:.1f} {units}"


def create_transition_names(from_classes: List, to_classes: List) -> List[str]:
    """
    Create human-readable transition names.
    
    Parameters
    ----------
    from_classes : list
        Source class names
    to_classes : list
        Target class names
        
    Returns
    -------
    list
        Transition names in format "From → To"
    """
    transitions = []
    for from_class in from_classes:
        for to_class in to_classes:
            if from_class != to_class:  # Skip persistence
                transitions.append(f"{from_class} → {to_class}")
    return transitions


def extract_time_labels_from_filenames(filenames: List[str], 
                                     label_position: Union[int, str] = "last", 
                                     separator: str = "_") -> List[str]:
    """
    Extract time labels from raster filenames based on position.
    
    Useful for automatically extracting years or time periods from filenames
    like 'landuse_1990.tif', 'region_data_2000_v1.tif', etc.
    
    Parameters
    ----------
    filenames : List[str]
        List of filenames or file paths
    label_position : int or str, default "last"
        Position of the time label in the filename:
        - "last": Last part before extension
        - "first": First part of filename
        - int: Specific position (0-based index) after splitting by separator
    separator : str, default "_"
        Character to split filename parts
        
    Returns
    -------
    List[str]
        Extracted time labels
        
    Examples
    --------
    >>> files = ['landuse_1990.tif', 'landuse_2000.tif', 'landuse_2010.tif']
    >>> extract_time_labels_from_filenames(files)
    ['1990', '2000', '2010']
    
    >>> files = ['2000_region_data.tif', '2010_region_data.tif']
    >>> extract_time_labels_from_filenames(files, label_position="first")
    ['2000', '2010']
    
    >>> files = ['data_1990_final.tif', 'data_2000_final.tif']
    >>> extract_time_labels_from_filenames(files, label_position=1)
    ['1990', '2000']
    """
    time_labels = []
    
    for filename in filenames:
        # Get basename without path
        basename = os.path.basename(filename)
        
        # Remove extension
        name_without_ext = os.path.splitext(basename)[0]
        
        # Split by separator
        parts = name_without_ext.split(separator)
        
        if len(parts) == 1:
            # No separator found, use the whole name
            label = name_without_ext
        else:
            # Extract based on position
            if label_position == "last":
                label = parts[-1]
            elif label_position == "first":
                label = parts[0]
            elif isinstance(label_position, int):
                if 0 <= label_position < len(parts):
                    label = parts[label_position]
                else:
                    # Fallback to last if position is out of range
                    label = parts[-1]
            else:
                # Fallback to last
                label = parts[-1]
        
        time_labels.append(label)
    
    return time_labels


def extract_years_from_text(text: str) -> List[str]:
    """
    Extract 4-digit years from text using regex.
    
    Parameters
    ----------
    text : str
        Text containing years
        
    Returns
    -------
    List[str]
        List of found years
        
    Examples
    --------
    >>> extract_years_from_text("landuse_1990_2000_final")
    ['1990', '2000']
    
    >>> extract_years_from_text("data_from_2010_to_2020")
    ['2010', '2020']
    """
    # Find all 4-digit numbers that look like years (1900-2099)
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    return years


def smart_extract_time_labels(filenames: List[str]) -> List[str]:
    """
    Intelligently extract time labels from filenames.
    
    Tries multiple strategies to extract meaningful time labels:
    1. Look for 4-digit years anywhere in filename
    2. Use last part of filename (split by underscore)
    3. Use filename without extension as fallback
    
    Parameters
    ----------
    filenames : List[str]
        List of filenames
        
    Returns
    -------
    List[str]
        Extracted time labels
        
    Examples
    --------
    >>> files = ['region_1990.tif', 'region_2000.tif', 'region_2010.tif']
    >>> smart_extract_time_labels(files)
    ['1990', '2000', '2010']
    
    >>> files = ['data_T1.tif', 'data_T2.tif']
    >>> smart_extract_time_labels(files)
    ['T1', 'T2']
    """
    time_labels = []
    
    for filename in filenames:
        basename = os.path.basename(filename)
        name_without_ext = os.path.splitext(basename)[0]
        
        # Strategy 1: Look for 4-digit years
        years = extract_years_from_text(name_without_ext)
        if years:
            # Use the first found year
            time_labels.append(years[0])
            continue
        
        # Strategy 2: Try last part after underscore
        parts = name_without_ext.split('_')
        if len(parts) > 1:
            last_part = parts[-1]
            # Check if it looks like a time label (contains digits)
            if re.search(r'\d', last_part):
                time_labels.append(last_part)
                continue
        
        # Strategy 3: Fallback to whole filename without extension
        time_labels.append(name_without_ext)
    
    return time_labels
