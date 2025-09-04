"""
Analyzer Factory for centralized analyzer creation and management.

This module implements the Factory pattern to centralize analyzer creation,
eliminating duplication and providing a unified interface for all analyzer types.
"""

from typing import Any, Dict, Optional, Union, Type
import numpy as np
import pandas as pd
from .base import AnalyzerBase, DataValidator


class AnalyzerFactory:
    """
    Factory for creating analyzer instances following the Factory pattern.

    This class centralizes analyzer creation, eliminating duplication and
    providing a unified interface for different analysis types (frequency,
    persistence, trajectory, etc.).
    """

    def __init__(self):
        self._analyzer_classes: Dict[str, Type[AnalyzerBase]] = {}
        self._load_analyzer_classes()

    def _load_analyzer_classes(self):
        """Load analyzer classes dynamically to avoid circular imports."""
        # Import analyzer classes only when needed
        try:
            from .plots.spatial_plots.analyzers.frequency_analyzer import FrequencyAnalyzer
            self._analyzer_classes['frequency'] = FrequencyAnalyzer
        except ImportError:
            pass

        try:
            from .plots.spatial_plots.analyzers.persistence_analyzer import PersistenceAnalyzer
            self._analyzer_classes['persistence'] = PersistenceAnalyzer
        except ImportError:
            pass

        try:
            from .plots.spatial_plots.analyzers.trajectory_analyzer import TrajectoryAnalyzer
            self._analyzer_classes['trajectory'] = TrajectoryAnalyzer
        except ImportError:
            pass

    def create_analyzer(self, analyzer_type: str,
                       config: Optional[Dict[str, Any]] = None) -> AnalyzerBase:
        """
        Create an analyzer instance of the specified type.

        Args:
            analyzer_type: Type of analyzer ('frequency', 'persistence', 'trajectory')
            config: Configuration dictionary for the analyzer

        Returns:
            Analyzer instance

        Raises:
            ValueError: If analyzer type is not supported or not available
        """
        if analyzer_type not in self._analyzer_classes:
            available_types = list(self._analyzer_classes.keys())
            raise ValueError(f"Analyzer type '{analyzer_type}' not supported. "
                           f"Available types: {available_types}")

        analyzer_class = self._analyzer_classes[analyzer_type]
        return analyzer_class(config)

    def analyze_data(self, analyzer_type: str, data: Union[np.ndarray, pd.DataFrame],
                    config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Create analyzer and perform analysis in one step.

        Args:
            analyzer_type: Type of analyzer to create
            data: Data to analyze
            config: Analyzer configuration
            **kwargs: Additional analysis parameters

        Returns:
            Analysis results dictionary

        Raises:
            ValueError: If analyzer type is not supported or data is invalid
        """
        analyzer_instance = self.create_analyzer(analyzer_type, config)

        # Validate data before analysis
        if not analyzer_instance.validate_input(data):
            raise ValueError(f"Invalid data for {analyzer_type} analyzer")

        return analyzer_instance.analyze(data, **kwargs)

    def get_available_analyzer_types(self) -> list[str]:
        """Get list of available analyzer types."""
        return list(self._analyzer_classes.keys())

    def get_analyzer_config_template(self, analyzer_type: str) -> Dict[str, Any]:
        """
        Get configuration template for an analyzer type.

        Args:
            analyzer_type: Type of analyzer

        Returns:
            Configuration template dictionary
        """
        if analyzer_type not in self._analyzer_classes:
            return {}

        analyzer_instance = self._analyzer_classes[analyzer_type]()
        return analyzer_instance.get_analysis_metadata()

    def validate_analyzer_config(self, analyzer_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for an analyzer type.

        Args:
            analyzer_type: Type of analyzer
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        # Basic validation - can be extended per analyzer type
        if not isinstance(config, dict):
            return False

        required_keys = ['analysis_type', 'parameters']
        return all(key in config for key in required_keys)


# Global instance for convenience
_analyzer_factory = None

def get_analyzer_factory() -> AnalyzerFactory:
    """Get the global analyzer factory instance."""
    global _analyzer_factory
    if _analyzer_factory is None:
        _analyzer_factory = AnalyzerFactory()
    return _analyzer_factory


# Convenience functions for backward compatibility
def create_frequency_analyzer(config: Optional[Dict[str, Any]] = None) -> AnalyzerBase:
    """Convenience function for frequency analyzer."""
    return get_analyzer_factory().create_analyzer('frequency', config)

def create_persistence_analyzer(config: Optional[Dict[str, Any]] = None) -> AnalyzerBase:
    """Convenience function for persistence analyzer."""
    return get_analyzer_factory().create_analyzer('persistence', config)

def create_trajectory_analyzer(config: Optional[Dict[str, Any]] = None) -> AnalyzerBase:
    """Convenience function for trajectory analyzer."""
    return get_analyzer_factory().create_analyzer('trajectory', config)
