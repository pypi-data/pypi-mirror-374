"""
Shared utilities and dependencies for visualization modules.

This module contains common functions, constants, and dependencies
used across all visualization modules.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set matplotlib style for publication-quality plots with accessibility
plt.style.use('default')

# Configure matplotlib for accessibility and academic standards
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 16,
    'axes.linewidth': 1.5,
    'grid.linewidth': 0.5,
    'lines.linewidth': 2,
    'lines.markersize': 6,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.facecolor': 'white',
    'figure.facecolor': 'white'
})

# Optional dependencies
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not available. Only matplotlib plots will be generated.")

# Geospatial dependencies
try:
    import geopandas as gpd
    import rasterio
    from rasterio.features import shapes
    from shapely.geometry import shape
    HAS_GEOSPATIAL = True
except ImportError:
    HAS_GEOSPATIAL = False
    warnings.warn("Geospatial libraries not available (geopandas, rasterio). Geospatial maps will not be generated.")

try:
    import contextily as ctx
    HAS_CONTEXTILY = True
except ImportError:
    HAS_CONTEXTILY = False

# Academic colorblind-safe color palette following WCAG 2.2 AA standards
# Colors chosen for high contrast and accessibility
CATEGORY_COLORS = [
    '#1F77B4',  # Blue - high contrast, accessible
    '#FF7F0E',  # Orange - distinct from blue
    '#2CA02C',  # Green - nature/vegetation
    '#D62728',  # Red - warnings/changes
    '#9467BD',  # Purple - distinct category
    '#8C564B',  # Brown - soil/urban
    '#E377C2',  # Pink - alternative class
    '#7F7F7F',  # Gray - neutral/persistence
    '#BCBD22',  # Olive - secondary vegetation
    '#17BECF'   # Cyan - water bodies
]

# High contrast transition colors for accessibility
TRANSITION_COLORS = {
    'gain': '#2E8B57',      # Sea Green - positive change
    'loss': '#DC143C',      # Crimson - negative change
    'persistent': '#696969', # Dim Gray - neutral state
    'change': '#FF8C00'     # Dark Orange - general change
}

# Pontius methodology color schemes - colorblind-safe and accessible
PONTIUS_COLORS = {
    'persistence': ['#F8F8F8', '#E0E0E0', '#C8C8C8', '#A8A8A8'],  # Light to dark grays
    'change_frequency': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6', '#2171B5'],  # Sequential blues
    'land_transitions': ['#8C510A', '#D8B365', '#F6E8C3', '#C7EAE5', '#5AAE61', '#1B7837'],  # Brown to green
    'temporal_change': ['#FDE725', '#B5DE2B', '#6DCD59', '#35B779', '#1F9E89', '#26828E', '#31688E', '#3E4989', '#482777', '#440154']  # Viridis
}


def ensure_output_dir(output_dir: Union[str, Path]) -> Path:
    """Ensure output directory exists."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_category_colors(n_categories: int) -> List[str]:
    """Get color palette for categories."""
    if n_categories <= len(CATEGORY_COLORS):
        return CATEGORY_COLORS[:n_categories]
    else:
        # Generate additional colors using seaborn
        return sns.color_palette("husl", n_categories).as_hex()


def format_title(title: str) -> str:
    """Format title for plots."""
    return title.replace('_', ' ').title()


def create_category_labels(
    data: pd.DataFrame,
    legend: pd.DataFrame,
    custom_labels: Optional[Dict[str, str]] = None
) -> Dict[int, str]:
    """
    Create category labels from data and legend.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data containing category information
    legend : pd.DataFrame
        Legend DataFrame with category mappings
    custom_labels : dict, optional
        Custom labels for categories
        
    Returns
    -------
    dict
        Mapping of category values to labels
    """
    # Create category labels
    if not legend.empty and 'CategoryValue' in legend.columns:
        if 'CategoryName' in legend.columns:
            label_map = dict(zip(legend['CategoryValue'], legend['CategoryName']))
        else:
            label_map = {val: f"Class_{val}" for val in legend['CategoryValue']}
    else:
        # Get unique categories from data
        if 'From' in data.columns and 'To' in data.columns:
            categories = sorted(set(data['From'].unique()) | set(data['To'].unique()))
        else:
            categories = sorted(data.index.unique() if hasattr(data, 'index') else [])
        label_map = {cat: f"Class_{cat}" for cat in categories}
    
    # Apply custom labels if provided
    if custom_labels:
        label_map.update(custom_labels)
    
    return label_map


def prepare_transition_matrix(
    data: pd.DataFrame,
    value_column: str = 'km2',
    from_column: str = 'From',
    to_column: str = 'To'
) -> pd.DataFrame:
    """
    Create transition matrix from contingency data.
    
    Parameters
    ----------
    data : pd.DataFrame
        Contingency data
    value_column : str
        Column containing transition values
    from_column : str
        Column containing source categories
    to_column : str
        Column containing target categories
        
    Returns
    -------
    pd.DataFrame
        Transition matrix
    """
    return data.pivot_table(
        index=from_column,
        columns=to_column,
        values=value_column,
        fill_value=0
    )


def save_plot_files(
    fig,
    output_path: Path,
    filename: str,
    save_png: bool = True,
    save_html: bool = False,
    dpi: int = 300,
    is_plotly: bool = False
) -> Dict[str, str]:
    """
    Save plot files in multiple formats.
    
    Parameters
    ----------
    fig
        Figure object (matplotlib or plotly)
    output_path : Path
        Output directory path
    filename : str
        Base filename
    save_png : bool
        Save PNG version
    save_html : bool
        Save HTML version
    dpi : int
        DPI for PNG output
    is_plotly : bool
        Whether figure is plotly or matplotlib
        
    Returns
    -------
    dict
        Dictionary with paths to saved files
    """
    saved_files = {}
    
    if is_plotly and HAS_PLOTLY:
        if save_html:
            html_path = output_path / f"{filename}.html"
            fig.write_html(html_path)
            saved_files['html'] = str(html_path)
            print(f"✅ HTML saved: {html_path}")
        
        if save_png:
            png_path = output_path / f"{filename}.png"
            try:
                fig.write_image(png_path, width=1200, height=800, scale=2)
                saved_files['png'] = str(png_path)
                print(f"✅ PNG saved: {png_path}")
            except Exception as e:
                print(f"⚠️ Could not save PNG: {e}")
    else:
        # Matplotlib figure
        if save_png:
            png_path = output_path / f"{filename}.png"
            plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
            saved_files['png'] = str(png_path)
            print(f"✅ PNG saved: {png_path}")
        
        # Only close matplotlib figures, not Plotly figures
        if hasattr(fig, 'number') or 'matplotlib' in str(type(fig)):
            plt.close(fig)
    
    return saved_files


def validate_contingency_data(contingency_data: Dict) -> bool:
    """
    Validate that contingency data contains required fields.
    
    Parameters
    ----------
    contingency_data : dict
        Contingency data from ContingencyTable
        
    Returns
    -------
    bool
        True if data is valid
    """
    if not isinstance(contingency_data, dict):
        return False
    
    required_keys = ['lulc_MultiStep', 'lulc_SingleStep', 'tb_legend']
    has_multistep = 'lulc_MultiStep' in contingency_data
    has_singlestep = 'lulc_SingleStep' in contingency_data
    
    return has_multistep or has_singlestep


def extract_data_for_plot(
    contingency_data: Dict,
    prefer_singlestep: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract plot data and legend from contingency results.
    
    Parameters
    ----------
    contingency_data : dict
        Contingency data from ContingencyTable
    prefer_singlestep : bool
        Whether to prefer single-step over multi-step data
        
    Returns
    -------
    tuple
        (plot_data, legend) DataFrames
    """
    if prefer_singlestep and 'lulc_SingleStep' in contingency_data:
        plot_data = contingency_data['lulc_SingleStep'].copy()
    elif 'lulc_MultiStep' in contingency_data:
        plot_data = contingency_data['lulc_MultiStep'].copy()
    elif 'lulc_SingleStep' in contingency_data:
        plot_data = contingency_data['lulc_SingleStep'].copy()
    else:
        raise ValueError("No suitable data found in contingency_data")
    
    legend = contingency_data.get('tb_legend', pd.DataFrame())
    
    # Data compatibility - simple format check
    if isinstance(plot_data, pd.DataFrame):
        # Ensure we have the right column names
        if 'From' in plot_data.columns and 'To' in plot_data.columns:
            # Data is already in the right format
            pass
        elif 'class_from' in plot_data.columns and 'class_to' in plot_data.columns:
            # Convert from contingency format
            plot_data = plot_data.rename(columns={
                'class_from': 'From',
                'class_to': 'To',
                'count': 'km2'
            })
    
    return plot_data, legend


# Export utilities
__all__ = [
    'ensure_output_dir',
    'get_category_colors',
    'format_title',
    'create_category_labels',
    'prepare_transition_matrix',
    'save_plot_files',
    'validate_contingency_data',
    'extract_data_for_plot',
    'HAS_PLOTLY',
    'HAS_GEOSPATIAL',
    'HAS_CONTEXTILY',
    'CATEGORY_COLORS',
    'TRANSITION_COLORS',
    'PONTIUS_COLORS',
    'plt',
    'pd',
    'np',
    'sns'
]
