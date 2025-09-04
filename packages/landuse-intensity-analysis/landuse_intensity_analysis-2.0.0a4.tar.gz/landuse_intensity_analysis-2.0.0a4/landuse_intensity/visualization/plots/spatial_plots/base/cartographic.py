"""
Cartographic elements for spatial plotting.

This module provides utilities for creating high-quality cartographic
elements including color schemes, legends, scales, and annotations.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches


class CartographicElements:
    """
    Manager for cartographic elements in spatial plots.
    
    This class provides utilities for creating professional cartographic
    elements including color schemes, legends, scale bars, north arrows,
    and annotations for spatial analysis visualizations.
    """
    
    def __init__(self):
        """Initialize cartographic elements manager."""
        self.default_colors = self._get_default_color_schemes()
        self.default_styles = self._get_default_styles()
        
    def _get_default_color_schemes(self) -> Dict[str, Any]:
        """Get default color schemes for different plot types."""
        return {
            'lulc': {
                # Standard LULC color scheme
                'colors': [
                    '#ffffff',  # No data / Background
                    '#1f8b1f',  # Forest (dark green)
                    '#90ee90',  # Natural vegetation (light green)
                    '#ffd700',  # Agriculture (gold)
                    '#ff6b35',  # Urban (orange-red)
                    '#0080ff',  # Water (blue)
                    '#8b4513',  # Bare soil (brown)
                    '#dda0dd',  # Other (plum)
                ],
                'labels': [
                    'No Data', 'Forest', 'Natural Veg.', 
                    'Agriculture', 'Urban', 'Water', 
                    'Bare Soil', 'Other'
                ]
            },
            'persistence': {
                'colors': [
                    '#ffffff',  # No data
                    '#ffcccc',  # Low persistence (light red)
                    '#ff6666',  # Medium-low persistence
                    '#ff0000',  # Medium persistence (red)
                    '#cc0000',  # High persistence
                    '#800000',  # Very high persistence (dark red)
                ],
                'labels': [
                    'No Data', 'Low (20%)', 'Medium-Low (40%)',
                    'Medium (60%)', 'High (80%)', 'Very High (100%)'
                ]
            },
            'change_frequency': {
                'colors': [
                    '#ffffff',  # No data
                    '#ffffcc',  # No change (light yellow)
                    '#c7e9b4',  # Low change (light green)
                    '#7fcdbb',  # Medium-low change (light blue-green)
                    '#41b6c4',  # Medium change (blue)
                    '#2c7fb8',  # High change (dark blue)
                    '#253494',  # Very high change (very dark blue)
                ],
                'labels': [
                    'No Data', 'No Change', 'Low (1-2)', 
                    'Medium-Low (3-4)', 'Medium (5-6)', 
                    'High (7-8)', 'Very High (9+)'
                ]
            },
            'trajectory': {
                # Qualitative colors for different trajectory patterns
                'colors': [
                    '#ffffff',  # No data
                    '#1f77b4',  # Blue
                    '#ff7f0e',  # Orange
                    '#2ca02c',  # Green
                    '#d62728',  # Red
                    '#9467bd',  # Purple
                    '#8c564b',  # Brown
                    '#e377c2',  # Pink
                    '#7f7f7f',  # Gray
                    '#bcbd22',  # Olive
                    '#17becf',  # Cyan
                ],
                'labels': None  # Generated dynamically
            }
        }
        
    def _get_default_styles(self) -> Dict[str, Any]:
        """Get default styling parameters."""
        return {
            'figure': {
                'dpi': 300,
                'facecolor': 'white',
                'edgecolor': 'black',
                'frameon': True
            },
            'axes': {
                'facecolor': 'white',
                'edgecolor': 'black',
                'linewidth': 1.0,
                'grid': False
            },
            'text': {
                'fontsize': 10,
                'fontweight': 'normal',
                'fontfamily': 'sans-serif'
            },
            'title': {
                'fontsize': 14,
                'fontweight': 'bold',
                'pad': 20
            },
            'legend': {
                'fontsize': 9,
                'frameon': True,
                'fancybox': True,
                'shadow': True,
                'ncol': 1,
                'loc': 'upper right'
            }
        }
        
    def create_colormap(self, 
                       plot_type: str, 
                       classes: Optional[np.ndarray] = None,
                       custom_colors: Optional[List[str]] = None) -> Tuple[ListedColormap, Normalize, List[str]]:
        """
        Create colormap for specific plot type.
        
        Parameters
        ----------
        plot_type : str
            Type of plot ('lulc', 'persistence', 'change_frequency', 'trajectory')
        classes : Optional[np.ndarray]
            Unique class values
        custom_colors : Optional[List[str]]
            Custom color list
            
        Returns
        -------
        Tuple[ListedColormap, Normalize, List[str]]
            Colormap, normalizer, and labels
        """
        if plot_type not in self.default_colors:
            plot_type = 'lulc'  # Fallback
            
        color_scheme = self.default_colors[plot_type]
        
        # Use custom colors if provided
        if custom_colors:
            colors = custom_colors
        else:
            colors = color_scheme['colors']
            
        # Adjust colors and labels based on actual classes
        if classes is not None:
            classes = np.asarray(classes)
            n_classes = len(classes)
            
            # Ensure we have enough colors
            while len(colors) < n_classes:
                colors.extend(colors[1:])  # Repeat colors (skip first/nodata)
                
            colors = colors[:n_classes]
            
            # Create labels
            if plot_type == 'trajectory':
                labels = [f'Pattern {i}' for i in range(n_classes)]
            elif color_scheme['labels']:
                labels = color_scheme['labels'][:n_classes]
                # Extend labels if needed
                while len(labels) < n_classes:
                    labels.append(f'Class {len(labels)}')
            else:
                labels = [f'Class {i}' for i in range(n_classes)]
                
            # Create normalizer for actual class values
            norm = Normalize(vmin=classes.min(), vmax=classes.max())
            
        else:
            labels = color_scheme['labels'] or [f'Class {i}' for i in range(len(colors))]
            norm = Normalize(vmin=0, vmax=len(colors)-1)
            
        # Create colormap
        cmap = ListedColormap(colors)
        
        return cmap, norm, labels
        
    def add_legend(self, 
                  ax: plt.Axes, 
                  cmap: ListedColormap, 
                  labels: List[str],
                  classes: Optional[np.ndarray] = None,
                  **kwargs) -> None:
        """
        Add legend to plot.
        
        Parameters
        ----------
        ax : plt.Axes
            Matplotlib axes
        cmap : ListedColormap
            Colormap
        labels : List[str]
            Class labels
        classes : Optional[np.ndarray]
            Class values
        **kwargs
            Additional legend parameters
        """
        # Merge with default legend styles
        legend_params = self.default_styles['legend'].copy()
        legend_params.update(kwargs)
        
        # Create legend elements
        if classes is not None:
            # Use actual class values
            legend_elements = [
                mpatches.Patch(color=cmap.colors[i], label=f'{labels[i]} ({classes[i]})')
                for i in range(min(len(labels), len(classes), len(cmap.colors)))
            ]
        else:
            legend_elements = [
                mpatches.Patch(color=cmap.colors[i], label=labels[i])
                for i in range(min(len(labels), len(cmap.colors)))
            ]
            
        # Add legend
        legend = ax.legend(handles=legend_elements, **legend_params)
        legend.get_frame().set_alpha(0.9)
        
    def add_scale_bar(self, 
                     ax: plt.Axes, 
                     pixel_size: float,
                     length_km: float = 10.0,
                     location: str = 'lower right',
                     **kwargs) -> None:
        """
        Add scale bar to plot.
        
        Parameters
        ----------
        ax : plt.Axes
            Matplotlib axes
        pixel_size : float
            Pixel size in meters
        length_km : float
            Scale bar length in kilometers
        location : str
            Scale bar location
        **kwargs
            Additional styling parameters
        """
        # Calculate scale bar length in pixels
        length_m = length_km * 1000
        length_pixels = length_m / pixel_size
        
        # Get axes limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Calculate position based on location
        positions = {
            'lower right': (xlim[1] - length_pixels - (xlim[1] - xlim[0]) * 0.05,
                           ylim[0] + (ylim[1] - ylim[0]) * 0.05),
            'lower left': (xlim[0] + (xlim[1] - xlim[0]) * 0.05,
                          ylim[0] + (ylim[1] - ylim[0]) * 0.05),
            'upper right': (xlim[1] - length_pixels - (xlim[1] - xlim[0]) * 0.05,
                           ylim[1] - (ylim[1] - ylim[0]) * 0.1),
            'upper left': (xlim[0] + (xlim[1] - xlim[0]) * 0.05,
                          ylim[1] - (ylim[1] - ylim[0]) * 0.1)
        }
        
        x, y = positions.get(location, positions['lower right'])
        
        # Draw scale bar
        scale_color = kwargs.get('color', 'black')
        scale_linewidth = kwargs.get('linewidth', 3)
        
        # Main scale line
        ax.plot([x, x + length_pixels], [y, y], 
               color=scale_color, linewidth=scale_linewidth)
        
        # End markers
        marker_height = (ylim[1] - ylim[0]) * 0.01
        ax.plot([x, x], [y - marker_height, y + marker_height], 
               color=scale_color, linewidth=scale_linewidth)
        ax.plot([x + length_pixels, x + length_pixels], 
               [y - marker_height, y + marker_height], 
               color=scale_color, linewidth=scale_linewidth)
        
        # Scale text
        text_y = y + marker_height * 2
        ax.text(x + length_pixels/2, text_y, f'{length_km} km', 
               ha='center', va='bottom', 
               fontsize=kwargs.get('fontsize', 8),
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
    def add_north_arrow(self, 
                       ax: plt.Axes, 
                       location: str = 'upper left',
                       size: float = 0.05,
                       **kwargs) -> None:
        """
        Add north arrow to plot.
        
        Parameters
        ----------
        ax : plt.Axes
            Matplotlib axes
        location : str
            North arrow location
        size : float
            Arrow size as fraction of plot
        **kwargs
            Additional styling parameters
        """
        # Get axes limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Calculate arrow size
        arrow_size = min(xlim[1] - xlim[0], ylim[1] - ylim[0]) * size
        
        # Calculate position
        positions = {
            'upper left': (xlim[0] + (xlim[1] - xlim[0]) * 0.05,
                          ylim[1] - (ylim[1] - ylim[0]) * 0.05),
            'upper right': (xlim[1] - (xlim[1] - xlim[0]) * 0.05,
                           ylim[1] - (ylim[1] - ylim[0]) * 0.05),
            'lower left': (xlim[0] + (xlim[1] - xlim[0]) * 0.05,
                          ylim[0] + (ylim[1] - ylim[0]) * 0.1),
            'lower right': (xlim[1] - (xlim[1] - xlim[0]) * 0.05,
                           ylim[0] + (ylim[1] - ylim[0]) * 0.1)
        }
        
        x, y = positions.get(location, positions['upper left'])
        
        # Arrow properties
        arrow_color = kwargs.get('color', 'black')
        
        # Draw arrow
        ax.annotate('', xy=(x, y), xytext=(x, y - arrow_size),
                   arrowprops=dict(arrowstyle='->', 
                                  color=arrow_color, 
                                  lw=2, 
                                  mutation_scale=20))
        
        # Add 'N' text
        ax.text(x, y + arrow_size * 0.3, 'N', 
               ha='center', va='center',
               fontsize=kwargs.get('fontsize', 10),
               fontweight='bold',
               color=arrow_color)
        
    def add_title_block(self, 
                       fig: plt.Figure,
                       title: str,
                       subtitle: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       **kwargs) -> None:
        """
        Add professional title block to figure.
        
        Parameters
        ----------
        fig : plt.Figure
            Matplotlib figure
        title : str
            Main title
        subtitle : Optional[str]
            Subtitle
        metadata : Optional[Dict[str, Any]]
            Additional metadata to display
        **kwargs
            Additional styling parameters
        """
        # Main title
        title_params = self.default_styles['title'].copy()
        title_params.update(kwargs.get('title_style', {}))
        
        fig.suptitle(title, **title_params)
        
        # Subtitle
        if subtitle:
            subtitle_y = title_params.get('y', 0.95) - 0.03
            fig.text(0.5, subtitle_y, subtitle, 
                    ha='center', va='top',
                    fontsize=title_params['fontsize'] - 2,
                    style='italic')
            
        # Metadata block
        if metadata:
            metadata_text = self._format_metadata(metadata)
            fig.text(0.02, 0.02, metadata_text,
                    ha='left', va='bottom',
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.5', 
                             facecolor='lightgray', 
                             alpha=0.8))
            
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for display."""
        lines = []
        
        # Common metadata fields
        if 'date_range' in metadata:
            lines.append(f"Period: {metadata['date_range']}")
        if 'resolution' in metadata:
            lines.append(f"Resolution: {metadata['resolution']}")
        if 'coordinate_system' in metadata:
            lines.append(f"CRS: {metadata['coordinate_system']}")
        if 'total_area' in metadata:
            lines.append(f"Area: {metadata['total_area']}")
        if 'processing_date' in metadata:
            lines.append(f"Processed: {metadata['processing_date']}")
            
        return '\n'.join(lines)
        
    def apply_style_theme(self, 
                         fig: plt.Figure, 
                         theme: str = 'default') -> None:
        """
        Apply consistent styling theme to figure.
        
        Parameters
        ----------
        fig : plt.Figure
            Matplotlib figure
        theme : str
            Style theme ('default', 'publication', 'presentation')
        """
        if theme == 'publication':
            # High-quality publication style
            plt.rcParams.update({
                'font.size': 10,
                'axes.linewidth': 1.2,
                'axes.labelsize': 10,
                'axes.titlesize': 12,
                'xtick.labelsize': 9,
                'ytick.labelsize': 9,
                'legend.fontsize': 9,
                'figure.titlesize': 14,
                'lines.linewidth': 1.5,
                'patch.linewidth': 0.5,
                'patch.edgecolor': 'black'
            })
            
        elif theme == 'presentation':
            # Larger fonts for presentations
            plt.rcParams.update({
                'font.size': 14,
                'axes.linewidth': 2.0,
                'axes.labelsize': 16,
                'axes.titlesize': 18,
                'xtick.labelsize': 14,
                'ytick.labelsize': 14,
                'legend.fontsize': 14,
                'figure.titlesize': 20,
                'lines.linewidth': 2.0,
                'patch.linewidth': 1.0
            })
            
        # Apply figure-level styling
        fig.patch.set_facecolor('white')
        fig.patch.set_edgecolor('black')
        
    def create_grid_layout(self, 
                          n_plots: int, 
                          figsize_per_plot: Tuple[float, float] = (6, 6),
                          **kwargs) -> Tuple[plt.Figure, np.ndarray]:
        """
        Create optimal grid layout for multiple plots.
        
        Parameters
        ----------
        n_plots : int
            Number of plots
        figsize_per_plot : Tuple[float, float]
            Size per subplot
        **kwargs
            Additional figure parameters
            
        Returns
        -------
        Tuple[plt.Figure, np.ndarray]
            Figure and axes array
        """
        # Calculate optimal grid dimensions
        if n_plots == 1:
            nrows, ncols = 1, 1
        elif n_plots == 2:
            nrows, ncols = 1, 2
        elif n_plots <= 4:
            nrows, ncols = 2, 2
        elif n_plots <= 6:
            nrows, ncols = 2, 3
        elif n_plots <= 9:
            nrows, ncols = 3, 3
        else:
            ncols = int(np.ceil(np.sqrt(n_plots)))
            nrows = int(np.ceil(n_plots / ncols))
            
        # Calculate figure size
        width_per_plot, height_per_plot = figsize_per_plot
        figsize = (ncols * width_per_plot, nrows * height_per_plot)
        
        # Create figure and axes
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
        
        # Ensure axes is always an array
        if n_plots == 1:
            axes = np.array([axes])
        elif nrows == 1 or ncols == 1:
            axes = axes.reshape(-1)
        else:
            axes = axes.flatten()
            
        # Hide unused subplots
        for i in range(n_plots, len(axes)):
            axes[i].set_visible(False)
            
        plt.tight_layout()
        
        return fig, axes[:n_plots]
