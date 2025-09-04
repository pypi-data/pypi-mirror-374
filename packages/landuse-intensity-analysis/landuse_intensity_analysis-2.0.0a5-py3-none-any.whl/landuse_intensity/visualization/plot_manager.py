"""
Plot Manager for centralized plot creation and management.

This module implements the Manager pattern to centralize plot creation,
eliminating duplication and providing a unified interface for all plot types.
"""

from typing import Any, Dict, Optional, Union, Type
import numpy as np
import pandas as pd
from ..core.base import PlotBase, DataValidator


class PlotManager:
    """
    Centralized manager for all plot types following the Manager pattern.

    This class eliminates duplication by providing a unified interface for
    creating and managing different types of plots (spatial, matrix, sankey, etc.).
    """

    def __init__(self):
        self._plot_classes: Dict[str, Type[PlotBase]] = {}
        self._load_plot_classes()

    def _load_plot_classes(self):
        """Load plot classes dynamically to avoid circular imports."""
        # Import plot classes only when needed
        try:
            from .plots.spatial_plots import SpatialPlot
            self._plot_classes['spatial'] = SpatialPlot
        except ImportError:
            pass

        try:
            from .plots.matrix_plots import MatrixPlot
            self._plot_classes['matrix'] = MatrixPlot
        except ImportError:
            pass

        try:
            from .plots.sankey_plots import SankeyPlot
            self._plot_classes['sankey'] = SankeyPlot
        except ImportError:
            pass

        try:
            from .plots.intensity_plots import IntensityPlot
            self._plot_classes['intensity'] = IntensityPlot
        except ImportError:
            pass

    def create_plot(self, plot_type: str, config: Optional[Dict[str, Any]] = None) -> PlotBase:
        """
        Create a plot instance of the specified type.

        Args:
            plot_type: Type of plot ('spatial', 'matrix', 'sankey', 'intensity')
            config: Configuration dictionary for the plot

        Returns:
            Plot instance

        Raises:
            ValueError: If plot type is not supported or not available
        """
        if plot_type not in self._plot_classes:
            available_types = list(self._plot_classes.keys())
            raise ValueError(f"Plot type '{plot_type}' not supported. "
                           f"Available types: {available_types}")

        plot_class = self._plot_classes[plot_type]
        return plot_class(config)

    def plot_data(self, plot_type: str, data: Union[np.ndarray, pd.DataFrame],
                  config: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Create and execute a plot in one step.

        Args:
            plot_type: Type of plot to create
            data: Data to plot
            config: Plot configuration
            **kwargs: Additional plot parameters

        Returns:
            Plot result

        Raises:
            ValueError: If plot type is not supported or data is invalid
        """
        plot_instance = self.create_plot(plot_type, config)

        # Validate data before plotting
        if not plot_instance.validate_data(data):
            raise ValueError(f"Invalid data for {plot_type} plot")

        return plot_instance.plot(data, **kwargs)

    def get_available_plot_types(self) -> list[str]:
        """Get list of available plot types."""
        return list(self._plot_classes.keys())

    def get_plot_config_template(self, plot_type: str) -> Dict[str, Any]:
        """
        Get configuration template for a plot type.

        Args:
            plot_type: Type of plot

        Returns:
            Configuration template dictionary
        """
        if plot_type not in self._plot_classes:
            return {}

        plot_instance = self._plot_classes[plot_type]()
        return plot_instance.get_default_config()

    def batch_plot(self, plot_configs: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Create multiple plots in batch.

        Args:
            plot_configs: List of plot configurations
                Each config should have 'plot_type', 'data', and optional 'config'

        Returns:
            List of results with success status and plot objects
        """
        results = []
        for config in plot_configs:
            try:
                plot_type = config['plot_type']
                data = config['data']
                plot_config = config.get('config', {})
                kwargs = config.get('kwargs', {})

                plot_result = self.plot_data(plot_type, data, config=plot_config, **kwargs)
                results.append({
                    'success': True,
                    'plot_type': plot_type,
                    'result': plot_result
                })

            except Exception as e:
                results.append({
                    'success': False,
                    'plot_type': config.get('plot_type'),
                    'error': str(e)
                })

        return results


# Global instance for convenience
_plot_manager = None

def get_plot_manager() -> PlotManager:
    """Get the global plot manager instance."""
    global _plot_manager
    if _plot_manager is None:
        _plot_manager = PlotManager()
    return _plot_manager


# Convenience functions for backward compatibility
def plot_spatial_change_map(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Any:
    """Convenience function for spatial plots."""
    return get_plot_manager().plot_data('spatial', data, **kwargs)

def plot_contingency_table(data: pd.DataFrame, **kwargs) -> Any:
    """Convenience function for matrix/contingency plots."""
    return get_plot_manager().plot_data('matrix', data, **kwargs)

def plot_sankey(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Any:
    """Convenience function for sankey plots."""
    return get_plot_manager().plot_data('sankey', data, **kwargs)

def plot_intensity_analysis(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Any:
    """Convenience function for intensity plots."""
    return get_plot_manager().plot_data('intensity', data, **kwargs)
