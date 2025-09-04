"""
Base components for spatial analysis plotting.

This module provides the foundational components for the modular
spatial analysis system including abstract base classes, data management,
cartographic elements, and configuration building.
"""

from .analyzer_base import (
    SpatialAnalyzerBase,
    AnalysisResult,
    AnalysisError
)

from .data_manager import GeospatialDataManager

from .cartographic import CartographicElements

from .plot_builder import (
    PlotConfig,
    PlotConfigBuilder,
    ConfigPresets,
    create_config_from_dict,
    validate_config_compatibility
)

__all__ = [
    # Base classes
    'SpatialAnalyzerBase',
    'AnalysisResult',
    'AnalysisError',
    
    # Data management
    'GeospatialDataManager',
    
    # Cartographic elements
    'CartographicElements',
    
    # Configuration
    'PlotConfig',
    'PlotConfigBuilder',
    'ConfigPresets',
    'create_config_from_dict',
    'validate_config_compatibility'
]
