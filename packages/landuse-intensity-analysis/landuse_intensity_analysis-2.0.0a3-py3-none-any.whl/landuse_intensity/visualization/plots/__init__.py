"""
Visualization plots subpackage for land use transition analysis.

This subpackage provides modular visualization functions organized by plot type:
- sankey_plots: Sankey diagrams for transition flows
- matrix_plots: Heatmaps and matrix visualizations
- bar_plots: Bar charts for area analysis
- spatial_plots: Geospatial maps and spatial analysis
- intensity_plots: Transition intensity analysis
- plot_utils: Shared utilities and dependencies

All functions are re-exported at the package level for convenience.
"""

# Import plot utilities first (contains shared dependencies)
from .plot_utils import (
    ensure_output_dir,
    get_category_colors,
    format_title,
    create_category_labels,
    prepare_transition_matrix,
    save_plot_files,
    validate_contingency_data,
    extract_data_for_plot,
    HAS_PLOTLY,
    HAS_GEOSPATIAL,
    HAS_CONTEXTILY,
    CATEGORY_COLORS,
    TRANSITION_COLORS,
    PONTIUS_COLORS
)

# Import Sankey diagram functions
from .sankey_plots import (
    plot_sankey,  # Unified Sankey function
)

# Import matrix visualization functions
from .matrix_plots import (
    plot_transition_matrix_heatmap,
    plot_contingency_table,
    plot_diagonal_analysis
)

# Import bar chart functions
from .bar_plots import (
    plot_barplot_lulc,
    plot_change_frequency
)

# Check for optional spatial modules
try:
    # Import from the new OO spatial system
    from .spatial_plots import (
        create_spatial_plot,
        analyze_persistence,
        analyze_trajectory,
        analyze_change_frequency,
        analyze_pontius,
        # Legacy compatibility functions
        create_persistence_plot,
        create_trajectory_plot,
        create_frequency_plot
    )
    _HAS_SPATIAL = True
except ImportError:
    _HAS_SPATIAL = False

# Define spatial functions with conditional logic
def plot_spatial_change_map(*args, **kwargs):
    """Compatibility wrapper for old API."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    # This would need implementation to match old API
    print("⚠️ plot_spatial_change_map is deprecated. Use analyze_trajectory instead.")
    return None

def plot_persistence_map(*args, **kwargs):
    """Compatibility wrapper for old API."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return create_persistence_plot(*args, **kwargs)

def create_geospatial_transitions(*args, **kwargs):
    """Compatibility wrapper for old API."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    print("⚠️ create_geospatial_transitions is deprecated. Use analyze_trajectory instead.")
    return None

def plot_pontius_analysis(*args, **kwargs):
    """Compatibility wrapper for old API."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    print("⚠️ plot_pontius_analysis is deprecated. Use analyze_pontius instead.")
    return None

def create_spatial_plot(*args, **kwargs):
    """Create spatial plot."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return create_spatial_plot(*args, **kwargs)

def analyze_persistence(*args, **kwargs):
    """Analyze persistence."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return analyze_persistence(*args, **kwargs)

def analyze_trajectory(*args, **kwargs):
    """Analyze trajectory."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return analyze_trajectory(*args, **kwargs)

def analyze_change_frequency(*args, **kwargs):
    """Analyze change frequency."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return analyze_change_frequency(*args, **kwargs)

def analyze_pontius(*args, **kwargs):
    """Analyze Pontius."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return analyze_pontius(*args, **kwargs)

def create_persistence_plot(*args, **kwargs):
    """Create persistence plot."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return create_persistence_plot(*args, **kwargs)

def create_trajectory_plot(*args, **kwargs):
    """Create trajectory plot."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return create_trajectory_plot(*args, **kwargs)

def create_frequency_plot(*args, **kwargs):
    """Create frequency plot."""
    if not _HAS_SPATIAL:
        print("⚠️ Spatial plots not available. Install geopandas and rasterio for geospatial functionality.")
        return None
    return create_frequency_plot(*args, **kwargs)

# Check for optional intensity modules
try:
    from .intensity_plots import (
        plot_intensity_analysis,
        plot_gain_loss_analysis,
        plot_net_change_analysis,
        create_intensity_summary
    )
    _HAS_INTENSITY = True
except ImportError:
    _HAS_INTENSITY = False
    
    # Create dummy functions that show warnings
    def plot_intensity_analysis(*args, **kwargs):
        print("⚠️ Intensity plots not available. Module under development.")
        return None
    
    def plot_gain_loss_analysis(*args, **kwargs):
        print("⚠️ Intensity plots not available. Module under development.")
        return None
    
    def plot_net_change_analysis(*args, **kwargs):
        print("⚠️ Intensity plots not available. Module under development.")
        return None
    
    def create_intensity_summary(*args, **kwargs):
        print("⚠️ Intensity plots not available. Module under development.")
        return None

# Version and metadata
__version__ = "2.0.0"
__author__ = "Land Change and Intensity Analysis Development Team"

# All available plot functions
__all__ = [
    # Utility functions
    'ensure_output_dir',
    'get_category_colors', 
    'format_title',
    'create_category_labels',
    'prepare_transition_matrix',
    'save_plot_files',
    'validate_contingency_data',
    'extract_data_for_plot',
    
    # Sankey diagrams
    'plot_sankey',  # Unified Sankey function
    
    # Matrix visualizations
    'plot_transition_matrix_heatmap',
    'plot_contingency_table',
    'plot_diagonal_analysis',
    
    # Bar charts
    'plot_barplot_lulc',
    'plot_change_frequency',
    
    # Spatial maps (may be dummy functions if dependencies missing)
    'plot_spatial_change_map',
    'plot_persistence_map', 
    'create_geospatial_transitions',
    'plot_pontius_analysis',
    'create_spatial_plot',
    'analyze_persistence',
    'analyze_trajectory',
    'analyze_change_frequency',
    'analyze_pontius',
    'create_persistence_plot',
    'create_trajectory_plot',
    'create_frequency_plot',
    
    # Intensity analysis (may be dummy functions if not implemented)
    'plot_intensity_analysis',
    'plot_gain_loss_analysis',
    'plot_net_change_analysis',
    'create_intensity_summary',
    
    # Constants
    'HAS_PLOTLY',
    'HAS_GEOSPATIAL',
    'HAS_CONTEXTILY',
    'CATEGORY_COLORS',
    'TRANSITION_COLORS',
    'PONTIUS_COLORS'
]

# Module availability info
AVAILABLE_MODULES = {
    'sankey_plots': True,
    'matrix_plots': True,
    'bar_plots': True,
    'spatial_plots': _HAS_SPATIAL,
    'intensity_plots': _HAS_INTENSITY,
    'plot_utils': True
}

def get_available_functions():
    """
    Get a list of available plotting functions by category.
    
    Returns
    -------
    dict
        Dictionary with categories as keys and lists of available functions as values
    """
    functions = {
        'sankey': [
            'plot_single_step_sankey',
            'plot_multi_step_sankey',
            'plot_sankey_from_contingency_table',
            'plot_all_sankey_diagrams',
            'plot_multistep_sankey_complete'
        ],
        'matrix': [
            'plot_transition_matrix_heatmap',
            'plot_contingency_table',
            'plot_diagonal_analysis'
        ],
        'bars': [
            'plot_barplot_lulc',
            'plot_change_frequency'
        ],
        'spatial': [
            'plot_spatial_change_map',
            'plot_persistence_map',
            'create_geospatial_transitions',
            'plot_pontius_analysis'
        ] if _HAS_SPATIAL else [],
        'intensity': [
            'plot_intensity_analysis',
            'plot_gain_loss_analysis',
            'plot_net_change_analysis',
            'create_intensity_summary'
        ] if _HAS_INTENSITY else [],
        'utilities': [
            'ensure_output_dir',
            'get_category_colors',
            'create_category_labels',
            'validate_contingency_data'
        ]
    }
    
    return functions

def print_module_status():
    """Print the status of all visualization modules."""
    print("📊 Visualization Modules Status:")
    print("=" * 40)
    
    for module, available in AVAILABLE_MODULES.items():
        status = "✅ Available" if available else "❌ Not Available"
        print(f"{module:<15}: {status}")
    
    print("\n📋 Dependency Status:")
    print("-" * 25)
    print(f"Plotly:      {'✅' if HAS_PLOTLY else '❌'}")
    print(f"Geospatial:  {'✅' if HAS_GEOSPATIAL else '❌'}")
    print(f"Contextily:  {'✅' if HAS_CONTEXTILY else '❌'}")

# Print status on import for user awareness
if __name__ != "__main__":
    import warnings
    if not HAS_PLOTLY:
        warnings.warn("Plotly not available. Interactive Sankey diagrams will not be generated.", ImportWarning)
    if not HAS_GEOSPATIAL:
        warnings.warn("Geospatial libraries not available. Spatial maps will not be generated.", ImportWarning)
