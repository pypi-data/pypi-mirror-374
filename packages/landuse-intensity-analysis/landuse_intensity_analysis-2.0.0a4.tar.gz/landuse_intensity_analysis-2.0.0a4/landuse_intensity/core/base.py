"""
Base classes and interfaces for landuse_intensity package following Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Union, Optional
import numpy as np
import pandas as pd


class PlotBase(ABC):
    """
    Abstract base class for all plot implementations.

    This class defines the common interface for all visualization components,
    ensuring consistency and enabling polymorphism across different plot types.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def plot(self, data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Any:
        """
        Abstract method for creating plots.

        Args:
            data: Input data for plotting
            **kwargs: Additional plotting parameters

        Returns:
            Plot object or figure
        """
        pass

    @abstractmethod
    def validate_data(self, data: Union[np.ndarray, pd.DataFrame]) -> bool:
        """
        Validate input data for this plot type.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this plot type."""
        return {
            'figsize': (10, 6),
            'dpi': 100,
            'style': 'default'
        }


class AnalyzerBase(ABC):
    """
    Abstract base class for all analyzer implementations.

    This class defines the common interface for all analysis components,
    following the Strategy pattern for different analysis types.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def analyze(self, data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Dict[str, Any]:
        """
        Abstract method for performing analysis.

        Args:
            data: Input data for analysis
            **kwargs: Additional analysis parameters

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    def validate_input(self, data: Union[np.ndarray, pd.DataFrame]) -> bool:
        """
        Validate input data for this analyzer.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    def get_analysis_metadata(self) -> Dict[str, Any]:
        """Get metadata about this analysis type."""
        return {
            'analyzer_type': self.__class__.__name__,
            'version': '2.0',
            'description': self.__doc__ or 'No description available'
        }


class DataValidator:
    """
    Centralized data validation utilities.

    This class consolidates all validation logic to eliminate duplication
    across different modules and ensure consistent validation behavior.
    """

    @staticmethod
    def validate_contingency_data(data: pd.DataFrame) -> bool:
        """Validate contingency table data."""
        if not isinstance(data, pd.DataFrame):
            return False
        if data.empty:
            return False
        # Check for numeric data
        return data.select_dtypes(include=[np.number]).shape[1] > 0

    @staticmethod
    def validate_raster_data(data: np.ndarray) -> bool:
        """Validate raster data."""
        if not isinstance(data, np.ndarray):
            return False
        if data.size == 0:
            return False
        # Check for valid numeric data
        return np.issubdtype(data.dtype, np.number)

    @staticmethod
    def validate_config_for_plot(config: Dict[str, Any], plot_type: str) -> bool:
        """Validate configuration for specific plot type."""
        required_keys = {
            'spatial': ['crs', 'bounds'],
            'matrix': ['cmap', 'vmin', 'vmax'],
            'sankey': ['node_colors', 'link_colors'],
            'intensity': ['thresholds', 'colors']
        }

        if plot_type not in required_keys:
            return False

        return all(key in config for key in required_keys[plot_type])


class AreaCalculator:
    """
    Centralized area calculation utilities.

    This class consolidates all area-related calculations to eliminate
    duplication and ensure consistent area computations.
    """

    @staticmethod
    def calculate_area_matrix(contingency_table: pd.DataFrame,
                            pixel_area: float = 1.0) -> pd.DataFrame:
        """Convert contingency table from pixel counts to area units."""
        return contingency_table * pixel_area

    @staticmethod
    def format_area_label(area: float, units: str = "pixels") -> str:
        """Format area value for display."""
        if area >= 1e6:
            return ".2f"
        elif area >= 1e3:
            return ".1f"
        else:
            return ".0f"

    @staticmethod
    def get_total_area(contingency_table: pd.DataFrame) -> float:
        """Calculate total area from contingency table."""
        return contingency_table.values.sum()

    @staticmethod
    def get_change_percent(contingency_table: pd.DataFrame) -> float:
        """Calculate percentage of change area."""
        total_area = AreaCalculator.get_total_area(contingency_table)
        persistence = np.diag(contingency_table.values).sum()
        change_area = total_area - persistence
        return (change_area / total_area) * 100 if total_area > 0 else 0.0
