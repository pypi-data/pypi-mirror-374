"""
Plot configuration builder for spatial analysis.

This module provides a flexible builder pattern for creating and managing
plot configurations with validation and defaults.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np


@dataclass
class PlotConfig:
    """
    Configuration container for spatial plots.
    
    This dataclass holds all configuration parameters for spatial analysis
    plots with validation and default values.
    """
    
    # Basic plot parameters
    plot_type: str = 'lulc'
    title: Optional[str] = None
    subtitle: Optional[str] = None
    
    # Figure parameters
    figsize: Tuple[float, float] = (12, 8)
    dpi: int = 300
    facecolor: str = 'white'
    
    # Data parameters
    images_data: Dict[str, Union[str, np.ndarray]] = field(default_factory=dict)
    class_names: Optional[Dict[int, str]] = None
    exclude_classes: List[int] = field(default_factory=list)
    
    # Visual parameters
    colormap: Optional[str] = None
    custom_colors: Optional[List[str]] = None
    alpha: float = 1.0
    interpolation: str = 'nearest'
    
    # Layout parameters
    show_legend: bool = True
    legend_location: str = 'upper right'
    show_scale_bar: bool = False
    show_north_arrow: bool = False
    grid_layout: Optional[Tuple[int, int]] = None
    
    # Analysis parameters
    persistence_threshold: float = 0.8
    change_threshold: int = 1
    min_persistence_years: int = 3
    trajectory_method: str = 'sequence'
    
    # Output parameters
    save_path: Optional[Path] = None
    save_format: str = 'png'
    save_dpi: Optional[int] = None
    save_transparent: bool = False
    
    # Advanced parameters
    pixel_size: Optional[float] = None
    coordinate_system: Optional[str] = None
    extent: Optional[Tuple[float, float, float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing parameters
    parallel_processing: bool = True
    chunk_size: Optional[int] = None
    memory_efficient: bool = True
    
    # Additional custom parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration parameters."""
        # Validate plot type
        valid_plot_types = [
            'lulc', 'persistence', 'change_frequency', 
            'trajectory', 'contingency', 'pontius'
        ]
        if self.plot_type not in valid_plot_types:
            raise ValueError(f"plot_type must be one of {valid_plot_types}")
            
        # Validate figure parameters
        if len(self.figsize) != 2 or any(x <= 0 for x in self.figsize):
            raise ValueError("figsize must be a tuple of two positive numbers")
            
        if self.dpi <= 0:
            raise ValueError("dpi must be positive")
            
        # Validate alpha
        if not 0 <= self.alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
            
        # Validate thresholds
        if not 0 <= self.persistence_threshold <= 1:
            raise ValueError("persistence_threshold must be between 0 and 1")
            
        if self.change_threshold < 0:
            raise ValueError("change_threshold must be non-negative")
            
        if self.min_persistence_years < 1:
            raise ValueError("min_persistence_years must be at least 1")
            
        # Validate trajectory method
        valid_trajectory_methods = ['sequence', 'pattern', 'frequency']
        if self.trajectory_method not in valid_trajectory_methods:
            raise ValueError(f"trajectory_method must be one of {valid_trajectory_methods}")
            
        # Validate save format
        valid_formats = ['png', 'jpg', 'jpeg', 'pdf', 'svg', 'tiff']
        if self.save_format.lower() not in valid_formats:
            raise ValueError(f"save_format must be one of {valid_formats}")


class PlotConfigBuilder:
    """
    Builder for creating plot configurations.
    
    This class provides a fluent interface for building plot configurations
    with method chaining and validation.
    """
    
    def __init__(self):
        """Initialize the builder with default configuration."""
        self.config = PlotConfig()
        
    def reset(self) -> 'PlotConfigBuilder':
        """Reset to default configuration."""
        self.config = PlotConfig()
        return self
        
    def plot_type(self, plot_type: str) -> 'PlotConfigBuilder':
        """Set plot type."""
        self.config.plot_type = plot_type
        return self
        
    def title(self, title: str, subtitle: Optional[str] = None) -> 'PlotConfigBuilder':
        """Set plot title and optional subtitle."""
        self.config.title = title
        if subtitle is not None:
            self.config.subtitle = subtitle
        return self
        
    def figure_size(self, width: float, height: float) -> 'PlotConfigBuilder':
        """Set figure size."""
        self.config.figsize = (width, height)
        return self
        
    def resolution(self, dpi: int) -> 'PlotConfigBuilder':
        """Set figure resolution."""
        self.config.dpi = dpi
        return self
        
    def data(self, 
            images_data: Dict[str, Union[str, np.ndarray]], 
            class_names: Optional[Dict[int, str]] = None) -> 'PlotConfigBuilder':
        """Set input data."""
        self.config.images_data = images_data
        if class_names is not None:
            self.config.class_names = class_names
        return self
        
    def colors(self, 
              colormap: Optional[str] = None, 
              custom_colors: Optional[List[str]] = None) -> 'PlotConfigBuilder':
        """Set color scheme."""
        if colormap is not None:
            self.config.colormap = colormap
        if custom_colors is not None:
            self.config.custom_colors = custom_colors
        return self
        
    def visual_style(self, 
                    alpha: float = 1.0, 
                    interpolation: str = 'nearest') -> 'PlotConfigBuilder':
        """Set visual styling parameters."""
        self.config.alpha = alpha
        self.config.interpolation = interpolation
        return self
        
    def legend(self, 
              show: bool = True, 
              location: str = 'upper right') -> 'PlotConfigBuilder':
        """Configure legend display."""
        self.config.show_legend = show
        self.config.legend_location = location
        return self
        
    def cartographic_elements(self, 
                            scale_bar: bool = False,
                            north_arrow: bool = False,
                            pixel_size: Optional[float] = None) -> 'PlotConfigBuilder':
        """Configure cartographic elements."""
        self.config.show_scale_bar = scale_bar
        self.config.show_north_arrow = north_arrow
        if pixel_size is not None:
            self.config.pixel_size = pixel_size
        return self
        
    def layout(self, grid: Optional[Tuple[int, int]] = None) -> 'PlotConfigBuilder':
        """Configure plot layout."""
        self.config.grid_layout = grid
        return self
        
    def analysis_parameters(self, 
                          persistence_threshold: Optional[float] = None,
                          change_threshold: Optional[int] = None,
                          min_persistence_years: Optional[int] = None,
                          trajectory_method: Optional[str] = None) -> 'PlotConfigBuilder':
        """Set analysis parameters."""
        if persistence_threshold is not None:
            self.config.persistence_threshold = persistence_threshold
        if change_threshold is not None:
            self.config.change_threshold = change_threshold
        if min_persistence_years is not None:
            self.config.min_persistence_years = min_persistence_years
        if trajectory_method is not None:
            self.config.trajectory_method = trajectory_method
        return self
        
    def output(self, 
              save_path: Optional[Path] = None,
              format: str = 'png',
              dpi: Optional[int] = None,
              transparent: bool = False) -> 'PlotConfigBuilder':
        """Configure output parameters."""
        if save_path is not None:
            self.config.save_path = Path(save_path)
        self.config.save_format = format
        if dpi is not None:
            self.config.save_dpi = dpi
        self.config.save_transparent = transparent
        return self
        
    def geospatial(self, 
                  coordinate_system: Optional[str] = None,
                  extent: Optional[Tuple[float, float, float, float]] = None) -> 'PlotConfigBuilder':
        """Set geospatial parameters."""
        if coordinate_system is not None:
            self.config.coordinate_system = coordinate_system
        if extent is not None:
            self.config.extent = extent
        return self
        
    def metadata(self, **metadata) -> 'PlotConfigBuilder':
        """Add metadata."""
        self.config.metadata.update(metadata)
        return self
        
    def performance(self, 
                   parallel: bool = True,
                   chunk_size: Optional[int] = None,
                   memory_efficient: bool = True) -> 'PlotConfigBuilder':
        """Configure performance parameters."""
        self.config.parallel_processing = parallel
        self.config.chunk_size = chunk_size
        self.config.memory_efficient = memory_efficient
        return self
        
    def exclude_classes(self, *classes: int) -> 'PlotConfigBuilder':
        """Exclude specific classes from analysis."""
        self.config.exclude_classes.extend(classes)
        return self
        
    def add_parameter(self, key: str, value: Any) -> 'PlotConfigBuilder':
        """Add a custom parameter to the configuration."""
        self.config.parameters[key] = value
        return self
        
    def parameters(self, **kwargs) -> 'PlotConfigBuilder':
        """Add multiple parameters at once."""
        self.config.parameters.update(kwargs)
        return self
    
    def output_path(self, path: Optional[Union[str, Path]]) -> 'PlotConfigBuilder':
        """Set output file path."""
        if path is not None:
            self.config.save_path = Path(path)
        return self
        
    def build(self) -> PlotConfig:
        """Build and validate the configuration."""
        # Create a copy to avoid modifying the builder's config
        final_config = PlotConfig(
            plot_type=self.config.plot_type,
            title=self.config.title,
            subtitle=self.config.subtitle,
            figsize=self.config.figsize,
            dpi=self.config.dpi,
            facecolor=self.config.facecolor,
            images_data=self.config.images_data.copy(),
            class_names=self.config.class_names.copy() if self.config.class_names else None,
            exclude_classes=self.config.exclude_classes.copy(),
            colormap=self.config.colormap,
            custom_colors=self.config.custom_colors.copy() if self.config.custom_colors else None,
            alpha=self.config.alpha,
            interpolation=self.config.interpolation,
            show_legend=self.config.show_legend,
            legend_location=self.config.legend_location,
            show_scale_bar=self.config.show_scale_bar,
            show_north_arrow=self.config.show_north_arrow,
            grid_layout=self.config.grid_layout,
            persistence_threshold=self.config.persistence_threshold,
            change_threshold=self.config.change_threshold,
            min_persistence_years=self.config.min_persistence_years,
            trajectory_method=self.config.trajectory_method,
            save_path=self.config.save_path,
            save_format=self.config.save_format,
            save_dpi=self.config.save_dpi,
            save_transparent=self.config.save_transparent,
            pixel_size=self.config.pixel_size,
            coordinate_system=self.config.coordinate_system,
            extent=self.config.extent,
            metadata=self.config.metadata.copy(),
            parallel_processing=self.config.parallel_processing,
            chunk_size=self.config.chunk_size,
            memory_efficient=self.config.memory_efficient
        )
        
        return final_config
        
    def copy_from(self, other_config: PlotConfig) -> 'PlotConfigBuilder':
        """Copy configuration from another PlotConfig."""
        self.config = PlotConfig(
            plot_type=other_config.plot_type,
            title=other_config.title,
            subtitle=other_config.subtitle,
            figsize=other_config.figsize,
            dpi=other_config.dpi,
            facecolor=other_config.facecolor,
            images_data=other_config.images_data.copy(),
            class_names=other_config.class_names.copy() if other_config.class_names else None,
            exclude_classes=other_config.exclude_classes.copy(),
            colormap=other_config.colormap,
            custom_colors=other_config.custom_colors.copy() if other_config.custom_colors else None,
            alpha=other_config.alpha,
            interpolation=other_config.interpolation,
            show_legend=other_config.show_legend,
            legend_location=other_config.legend_location,
            show_scale_bar=other_config.show_scale_bar,
            show_north_arrow=other_config.show_north_arrow,
            grid_layout=other_config.grid_layout,
            persistence_threshold=other_config.persistence_threshold,
            change_threshold=other_config.change_threshold,
            min_persistence_years=other_config.min_persistence_years,
            trajectory_method=other_config.trajectory_method,
            save_path=other_config.save_path,
            save_format=other_config.save_format,
            save_dpi=other_config.save_dpi,
            save_transparent=other_config.save_transparent,
            pixel_size=other_config.pixel_size,
            coordinate_system=other_config.coordinate_system,
            extent=other_config.extent,
            metadata=other_config.metadata.copy(),
            parallel_processing=other_config.parallel_processing,
            chunk_size=other_config.chunk_size,
            memory_efficient=other_config.memory_efficient
        )
        return self


class ConfigPresets:
    """
    Predefined configuration presets for common use cases.
    """
    
    @staticmethod
    def persistence_analysis() -> PlotConfigBuilder:
        """Preset for persistence analysis."""
        return (PlotConfigBuilder()
                .plot_type('persistence')
                .title('Multi-Year Persistence Analysis')
                .analysis_parameters(persistence_threshold=0.8, min_persistence_years=3)
                .colors(colormap='Reds')
                .legend(show=True, location='upper right')
                .cartographic_elements(scale_bar=True))
                
    @staticmethod
    def change_frequency() -> PlotConfigBuilder:
        """Preset for change frequency analysis."""
        return (PlotConfigBuilder()
                .plot_type('change_frequency')
                .title('Land Use Change Frequency')
                .analysis_parameters(change_threshold=1)
                .colors(colormap='Blues')
                .legend(show=True))
                
    @staticmethod
    def trajectory_analysis() -> PlotConfigBuilder:
        """Preset for trajectory analysis."""
        return (PlotConfigBuilder()
                .plot_type('trajectory')
                .title('Land Use Change Trajectories')
                .analysis_parameters(trajectory_method='sequence')
                .legend(show=True))
                
    @staticmethod
    def contingency_analysis() -> PlotConfigBuilder:
        """Preset for contingency table analysis."""
        return (PlotConfigBuilder()
                .plot_type('contingency')
                .title('Multi-Year Transition Analysis')
                .legend(show=True))
                
    @staticmethod
    def publication_quality() -> PlotConfigBuilder:
        """Preset for publication-quality plots."""
        return (PlotConfigBuilder()
                .figure_size(12, 8)
                .resolution(300)
                .cartographic_elements(scale_bar=True, north_arrow=True)
                .output(format='pdf', dpi=300)
                .metadata(quality='publication'))
                
    @staticmethod
    def presentation() -> PlotConfigBuilder:
        """Preset for presentation slides."""
        return (PlotConfigBuilder()
                .figure_size(16, 9)
                .resolution(150)
                .legend(show=True, location='upper right')
                .output(format='png', dpi=150, transparent=True))
                
    @staticmethod
    def web_display() -> PlotConfigBuilder:
        """Preset for web display."""
        return (PlotConfigBuilder()
                .figure_size(10, 6)
                .resolution(96)
                .output(format='png', dpi=96)
                .metadata(quality='web'))


def create_config_from_dict(config_dict: Dict[str, Any]) -> PlotConfig:
    """
    Create configuration from dictionary.
    
    Parameters
    ----------
    config_dict : Dict[str, Any]
        Configuration dictionary
        
    Returns
    -------
    PlotConfig
        Plot configuration object
    """
    builder = PlotConfigBuilder()
    
    # Basic parameters
    if 'plot_type' in config_dict:
        builder.plot_type(config_dict['plot_type'])
        
    if 'title' in config_dict:
        builder.title(config_dict['title'], config_dict.get('subtitle'))
        
    # Figure parameters
    if 'figsize' in config_dict:
        width, height = config_dict['figsize']
        builder.figure_size(width, height)
        
    if 'dpi' in config_dict:
        builder.resolution(config_dict['dpi'])
        
    # Data parameters
    if 'images_data' in config_dict:
        builder.data(config_dict['images_data'], config_dict.get('class_names'))
        
    # Visual parameters
    if 'colormap' in config_dict or 'custom_colors' in config_dict:
        builder.colors(config_dict.get('colormap'), config_dict.get('custom_colors'))
        
    # Analysis parameters
    analysis_params = {}
    for param in ['persistence_threshold', 'change_threshold', 
                  'min_persistence_years', 'trajectory_method']:
        if param in config_dict:
            analysis_params[param] = config_dict[param]
    if analysis_params:
        builder.analysis_parameters(**analysis_params)
        
    # Output parameters
    if any(key in config_dict for key in ['save_path', 'save_format', 'save_dpi']):
        builder.output(
            config_dict.get('save_path'),
            config_dict.get('save_format', 'png'),
            config_dict.get('save_dpi'),
            config_dict.get('save_transparent', False)
        )
        
    return builder.build()


def validate_config_compatibility(config: PlotConfig) -> List[str]:
    """
    Validate configuration compatibility and return warnings.
    
    Parameters
    ----------
    config : PlotConfig
        Configuration to validate
        
    Returns
    -------
    List[str]
        List of warning messages
    """
    warnings = []
    
    # Check data availability for plot type
    if not config.images_data:
        warnings.append("No image data provided")
        
    # Check threshold compatibility
    if config.plot_type == 'persistence' and config.persistence_threshold <= 0.5:
        warnings.append("Low persistence threshold may result in noisy output")
        
    # Check memory requirements
    if len(config.images_data) > 10 and not config.memory_efficient:
        warnings.append("Large dataset detected - consider enabling memory_efficient mode")
        
    # Check output compatibility
    if config.save_format == 'pdf' and config.save_transparent:
        warnings.append("PDF format does not support transparency")
        
    return warnings
