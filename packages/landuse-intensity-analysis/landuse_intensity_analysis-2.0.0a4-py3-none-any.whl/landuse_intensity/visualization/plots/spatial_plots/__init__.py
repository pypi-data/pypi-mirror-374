"""
Spatial plots module with object-oriented architecture.

This module provides a comprehensive framework for spatial analysis
of land use change data with multiple analysis types and visualization options.
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import all components
from .base import (
    SpatialAnalyzerBase,
    GeospatialDataManager,
    CartographicElements,
    PlotConfig,
    PlotConfigBuilder,
    ConfigPresets,
    AnalysisResult,
    AnalysisError
)

from .analyzers import (
    PersistenceAnalyzer,
    TrajectoryAnalyzer,
    FrequencyAnalyzer,
    PontiusAnalyzer
)

from .strategies import (
    SpatialAnalyzerFactory,
    AnalyzerType,
    create_analyzer,
    create_analyzer_from_config,
    get_available_analyzer_types
)

# Export main classes and functions
__all__ = [
    # Core classes
    'SpatialAnalyzerBase',
    'GeospatialDataManager', 
    'CartographicElements',
    'PlotConfig',
    'PlotConfigBuilder',
    'ConfigPresets',
    'AnalysisResult',
    'AnalysisError',
    
    # Analyzer classes
    'PersistenceAnalyzer',
    'TrajectoryAnalyzer', 
    'FrequencyAnalyzer',
    'PontiusAnalyzer',
    
    # Factory classes
    'SpatialAnalyzerFactory',
    'AnalyzerType',
    
    # Convenience functions
    'create_analyzer',
    'create_spatial_plot',
    'analyze_persistence',
    'analyze_trajectory',
    'analyze_change_frequency',
    'analyze_pontius',
    'get_available_plot_types',
    
    # Legacy compatibility functions
    'create_persistence_plot',
    'create_trajectory_plot', 
    'create_frequency_plot'
]


def create_spatial_plot(data: np.ndarray,
                       plot_type: str,
                       output_path: Optional[str] = None,
                       config: Optional[PlotConfig] = None,
                       **kwargs) -> AnalysisResult:
    """
    Create a spatial plot using the new modular system.
    
    This is the main entry point for creating spatial plots with the 
    object-oriented architecture.
    
    Parameters
    ----------
    data : np.ndarray
        Input data array with shape (n_years, height, width)
    plot_type : str
        Type of analysis/plot to create ('persistence', 'trajectory', 'change_frequency')
    output_path : Optional[str]
        Path to save the output plot
    config : Optional[PlotConfig]
        Configuration object. If None, default config will be created
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    AnalysisResult
        Result containing analysis data and metadata
        
    Examples
    --------
    >>> # Basic persistence analysis
    >>> result = create_spatial_plot(data, 'persistence', 'output.png')
    
    >>> # Trajectory analysis with custom config
    >>> config = PlotConfigBuilder().plot_type('trajectory').colormap('viridis').build()
    >>> result = create_spatial_plot(data, 'trajectory', config=config)
    
    >>> # Change frequency with custom parameters
    >>> result = create_spatial_plot(
    ...     data, 'change_frequency', 
    ...     output_path='frequency.png',
    ...     title='Land Use Change Frequency',
    ...     colormap='RdYlBu'
    ... )
    """
    try:
        # Create configuration if not provided
        if config is None:
            builder = PlotConfigBuilder().plot_type(plot_type)
            
            # Apply kwargs to configuration
            if output_path:
                builder = builder.output_path(output_path)
            if 'title' in kwargs:
                builder = builder.title(kwargs['title'])
            if 'colormap' in kwargs:
                builder = builder.colormap(kwargs['colormap'])
            if 'figsize' in kwargs:
                builder = builder.figsize(kwargs['figsize'])
            if 'dpi' in kwargs:
                builder = builder.dpi(kwargs['dpi'])
                
            config = builder.build()
        
        # Create analyzer using factory
        analyzer = create_analyzer_from_config(config)
        
        # Run analysis - prepare kwargs without conflicting with images_data
        kwargs = {k: v for k, v in config.__dict__.items() if k != 'images_data'}
        result = analyzer.run_analysis(data, **kwargs)
        
        print(f"✅ Successfully created {plot_type} analysis")
        if output_path:
            print(f"📁 Saved to: {output_path}")
            
        return result
        
    except Exception as e:
        raise AnalysisError(f"Failed to create spatial plot: {e}")


def analyze_persistence(data: np.ndarray,
                       output_path: Optional[str] = None,
                       threshold: float = 0.7,
                       **kwargs) -> AnalysisResult:
    """
    Analyze land use persistence patterns.
    
    Parameters
    ----------
    data : np.ndarray
        Input data array
    output_path : Optional[str] 
        Output file path
    threshold : float
        Persistence threshold (0.0 to 1.0)
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    AnalysisResult
        Persistence analysis result
    """
    config = (PlotConfigBuilder()
              .plot_type('persistence')
              .output_path(output_path)
              .add_parameter('persistence_threshold', threshold)
              .build())
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return create_spatial_plot(data, 'persistence', output_path, config)


def analyze_trajectory(data: np.ndarray,
                      output_path: Optional[str] = None,
                      method: str = 'sequence',
                      **kwargs) -> AnalysisResult:
    """
    Analyze land use change trajectories.
    
    Parameters
    ----------
    data : np.ndarray
        Input data array
    output_path : Optional[str]
        Output file path
    method : str
        Trajectory calculation method ('sequence', 'pattern', 'frequency')
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    AnalysisResult
        Trajectory analysis result
    """
    config = (PlotConfigBuilder()
              .plot_type('trajectory')
              .output_path(output_path)
              .add_parameter('trajectory_method', method)
              .build())
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return create_spatial_plot(data, 'trajectory', output_path, config)


def analyze_change_frequency(data: np.ndarray,
                           output_path: Optional[str] = None,
                           **kwargs) -> AnalysisResult:
    """
    Analyze land use change frequency.
    
    Parameters
    ----------
    data : np.ndarray
        Input data array
    output_path : Optional[str]
        Output file path
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    AnalysisResult
        Change frequency analysis result
    """
    config = (PlotConfigBuilder()
              .plot_type('change_frequency')
              .output_path(output_path)
              .build())
    
    # Apply additional kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return create_spatial_plot(data, 'change_frequency', output_path, config)


def analyze_pontius(contingency_matrix: np.ndarray,
                   output_path: Optional[str] = None,
                   **kwargs) -> AnalysisResult:
    """
    Analyze land use change using Pontius framework.

    Parameters
    ----------
    contingency_matrix : np.ndarray
        Contingency table with rows as 'from' classes, columns as 'to' classes
    output_path : Optional[str]
        Output file path
    **kwargs
        Additional configuration parameters

    Returns
    -------
    AnalysisResult
        Pontius analysis result
    """
    config = (PlotConfigBuilder()
              .plot_type('pontius')
              .output_path(output_path)
              .build())

    # Apply additional kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    # Create analyzer directly for Pontius since it works with contingency data
    analyzer = PontiusAnalyzer()
    analyzer.config = config

    # Prepare loaded data format expected by analyzer
    loaded_data = {
        'contingency_matrix': contingency_matrix,
        'metadata': {'analysis_type': 'pontius'}
    }

    return analyzer.run_analysis(loaded_data, **kwargs)


def get_available_plot_types() -> List[str]:
    """
    Get list of available plot types.
    
    Returns
    -------
    List[str]
        Available plot types
    """
    return get_available_analyzer_types()


# Legacy compatibility functions for backward compatibility
def create_persistence_plot(data: np.ndarray,
                          output_path: str = "persistence_plot.png",
                          title: str = "Land Use Persistence Analysis",
                          threshold: float = 0.7,
                          colormap: str = "RdYlGn",
                          figsize: Tuple[int, int] = (12, 8),
                          dpi: int = 300) -> Dict[str, Any]:
    """
    Legacy function for creating persistence plots.
    
    This function maintains backward compatibility with the original API
    while using the new modular system internally.
    """
    try:
        result = analyze_persistence(
            data=data,
            output_path=output_path,
            threshold=threshold,
            title=title,
            colormap=colormap,
            figsize=figsize,
            dpi=dpi
        )
        
        # Return legacy format
        return {
            'status': 'success',
            'output_path': output_path,
            'analysis_type': 'persistence',
            'statistics': result.statistics,
            'metadata': result.metadata
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error_message': str(e),
            'analysis_type': 'persistence'
        }


def create_trajectory_plot(data: np.ndarray,
                         output_path: str = "trajectory_plot.png",
                         title: str = "Land Use Trajectory Analysis",
                         method: str = "sequence",
                         colormap: str = "tab20",
                         figsize: Tuple[int, int] = (12, 8),
                         dpi: int = 300) -> Dict[str, Any]:
    """
    Legacy function for creating trajectory plots.
    
    This function maintains backward compatibility with the original API
    while using the new modular system internally.
    """
    try:
        result = analyze_trajectory(
            data=data,
            output_path=output_path,
            method=method,
            title=title,
            colormap=colormap,
            figsize=figsize,
            dpi=dpi
        )
        
        # Return legacy format
        return {
            'status': 'success',
            'output_path': output_path,
            'analysis_type': 'trajectory',
            'statistics': result.statistics,
            'metadata': result.metadata
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error_message': str(e),
            'analysis_type': 'trajectory'
        }


def create_frequency_plot(data: np.ndarray,
                        output_path: str = "frequency_plot.png",
                        title: str = "Land Use Change Frequency",
                        colormap: str = "RdYlBu",
                        figsize: Tuple[int, int] = (12, 8),
                        dpi: int = 300) -> Dict[str, Any]:
    """
    Legacy function for creating frequency plots.
    
    This function maintains backward compatibility with the original API
    while using the new modular system internally.
    """
    try:
        result = analyze_change_frequency(
            data=data,
            output_path=output_path,
            title=title,
            colormap=colormap,
            figsize=figsize,
            dpi=dpi
        )
        
        # Return legacy format
        return {
            'status': 'success',
            'output_path': output_path,
            'analysis_type': 'frequency',
            'statistics': result.statistics,
            'metadata': result.metadata
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error_message': str(e),
            'analysis_type': 'frequency'
        }


# Module information
__version__ = "2.0.0"
__author__ = "OpenLand Development Team"
__description__ = "Object-oriented spatial analysis framework for land use change data"
