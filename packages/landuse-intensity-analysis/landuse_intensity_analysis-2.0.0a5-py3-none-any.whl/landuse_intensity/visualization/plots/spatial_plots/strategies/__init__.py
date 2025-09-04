"""
Strategies module for spatial analysis.

This module contains strategy patterns and factory classes for creating
and managing spatial analyzer instances.
"""

from .analyzer_factory import (
    SpatialAnalyzerFactory,
    AnalyzerRegistry,
    AnalyzerType,
    create_analyzer,
    create_analyzer_from_config,
    get_available_analyzer_types,
    register_custom_analyzer
)

__all__ = [
    'SpatialAnalyzerFactory',
    'AnalyzerRegistry', 
    'AnalyzerType',
    'create_analyzer',
    'create_analyzer_from_config',
    'get_available_analyzer_types',
    'register_custom_analyzer'
]
