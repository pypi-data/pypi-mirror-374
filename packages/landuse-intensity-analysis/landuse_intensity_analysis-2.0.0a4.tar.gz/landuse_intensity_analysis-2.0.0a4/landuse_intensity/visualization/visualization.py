"""
Unified Land Use and Land Cover (LULC) Change Visualization Interface

This module provides a unified interface to all LULC visualization capabilities,
importing functions from specialized plot modules for backward compatibility.

For direct access to specific plot types:
- landuse_intensity.plots.sankey_plots
- landuse_intensity.plots.matrix_plots  
- landuse_intensity.plots.bar_plots
- landuse_intensity.plots.spatial_plots
- landuse_intensity.plots.intensity_plots
"""

# Import all visualization functions from modular plots
from .plots import (
    # Unified Sankey interface
    plot_sankey,  # Main unified function
    
    # Matrix visualizations
    plot_transition_matrix_heatmap,
    plot_contingency_table,
    plot_diagonal_analysis,
    
    # Bar charts
    plot_barplot_lulc,
    plot_change_frequency,
    
    # Spatial maps (placeholders if dependencies missing)
    plot_spatial_change_map,
    plot_persistence_map,
    create_geospatial_transitions,
    plot_pontius_analysis,
    
    # Intensity analysis (placeholders)
    plot_intensity_analysis,
    plot_gain_loss_analysis,
    plot_net_change_analysis,
    create_intensity_summary,
    
    # Utilities
    get_available_functions,
    print_module_status
)

# All available functions for backward compatibility
__all__ = [
    # Unified Sankey interface
    'plot_sankey',  # Main unified function
    
    # Other plotting functions
    'plot_barplot_lulc',
    'plot_transition_matrix_heatmap',
    'plot_contingency_table',
    'plot_diagonal_analysis',
    'plot_change_frequency',
    'plot_spatial_change_map',
    'plot_persistence_map'
]


