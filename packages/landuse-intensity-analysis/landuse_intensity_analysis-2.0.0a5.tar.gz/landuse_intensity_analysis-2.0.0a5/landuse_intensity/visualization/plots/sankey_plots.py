"""
Sankey diagram plotting functions for land use transition analysis.

This module provides unified Sankey plotting functionality supporting both
legacy dict format and modern ContingencyTable objects with step_type parameter.

Unified API:
- plot_sankey(): Main function with step_type parameter ('single', 'multi', 'complete')
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import warnings

from .plot_utils import (
    HAS_PLOTLY, ensure_output_dir, create_category_labels,
    save_plot_files, validate_contingency_data, extract_data_for_plot,
    CATEGORY_COLORS, TRANSITION_COLORS
)

def _get_academic_colors():
    """
    Generate colorblind-safe colors following remote sensing publication standards.

    Returns standardized colors that are intuitive for land use categories
    and accessible for colorblind readers, as required by academic journals.
    Following WCAG 2.2 AA standards for high contrast and accessibility.
    """
    # Academic color palette for land use - intuitive and colorblind-safe
    # Following remote sensing visualization best practices and WCAG 2.2 AA
    # Using RGB format for Plotly compatibility and opacity control
    academic_palette = [
        'rgb(34, 139, 34)',    # Forest Green - vegetation/forest (high contrast)
        'rgb(30, 144, 255)',   # Dodger Blue - water bodies (accessible)
        'rgb(255, 215, 0)',    # Gold - agriculture/cropland (distinct)
        'rgb(139, 69, 19)',    # Saddle Brown - bare soil/urban (natural)
        'rgb(255, 20, 147)',   # Deep Pink - developed areas (warning)
        'rgb(255, 140, 0)',    # Dark Orange - grassland/pasture (distinct)
        'rgb(75, 0, 130)',     # Indigo - wetlands (unique)
        'rgb(220, 20, 60)',    # Crimson - alternative class (high contrast)
        'rgb(0, 128, 128)',    # Teal - water/aquaculture (accessible)
        'rgb(128, 0, 128)',    # Purple - mixed use (distinct)
        'rgb(255, 69, 0)',     # Red Orange - disturbed areas (warning)
        'rgb(46, 139, 87)',    # Sea Green - secondary vegetation (natural)
        'rgb(218, 165, 32)',   # Goldenrod - arid areas (distinct)
        'rgb(70, 130, 180)',   # Steel Blue - permanent water (accessible)
        'rgb(154, 205, 50)'    # Yellow Green - restored areas (positive)
    ]

    return academic_palette


if HAS_PLOTLY:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots


def _calculate_border_to_center_positions(node_values_by_column):
    """
    Calculate border-to-center node positioning for Sankey diagrams.
    Larger/more important nodes are positioned towards edges, smaller ones in center.
    
    Parameters
    ----------
    node_values_by_column : dict
        Dictionary with column index as key and list of (node_index, value) tuples
        
    Returns
    -------
    tuple
        (node_x, node_y) lists for manual node positioning
    """
    node_x = []
    node_y = []
    
    for col_idx, nodes_and_values in node_values_by_column.items():
        # Sort nodes by value (descending - largest first)
        sorted_nodes = sorted(nodes_and_values, key=lambda x: x[1], reverse=True)
        num_nodes = len(sorted_nodes)
        
        if num_nodes == 1:
            # Single node goes in center
            positions = [0.5]
        elif num_nodes == 2:
            # Two nodes: edges
            positions = [0.1, 0.9]
        else:
            # Multiple nodes: border-to-center arrangement
            positions = []
            for i in range(num_nodes):
                if i == 0:
                    # Largest to top edge
                    pos = 0.05
                elif i == 1 and num_nodes > 2:
                    # Second largest to bottom edge
                    pos = 0.95
                else:
                    # Remaining nodes distributed in center
                    center_nodes = num_nodes - 2
                    center_idx = i - 2
                    if center_nodes == 1:
                        pos = 0.5
                    else:
                        # Distribute in middle space (0.2 to 0.8)
                        pos = 0.25 + (center_idx * 0.5 / (center_nodes - 1))
                positions.append(pos)
        
        # Calculate x position for this column
        x_pos = col_idx / max(1, len(node_values_by_column) - 1) if len(node_values_by_column) > 1 else 0.5
        
        # Assign positions to nodes
        for (node_idx, _), y_pos in zip(sorted_nodes, positions):
            node_x.append(x_pos)
            node_y.append(y_pos)
    
    return node_x, node_y


def _convert_contingency_table_to_legacy_format(contingency_table) -> Dict[str, pd.DataFrame]:
    """
    Convert modern ContingencyTable object to legacy dict format.
    
    Parameters
    ----------
    contingency_table : ContingencyTable
        Modern ContingencyTable object
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Legacy format dict with 'lulc_SingleStep', 'lulc_MultiStep', 'tb_legend'
    """
    try:
        # Access the results from the ContingencyTable
        results = contingency_table.results
        contingency_df = results.contingency_table
        
        # Create legend from unique classes in the data
        unique_classes_from = contingency_df['class_from'].unique()
        unique_classes_to = contingency_df['class_to'].unique()
        all_classes = list(set(list(unique_classes_from) + list(unique_classes_to)))
        
        tb_legend = pd.DataFrame({
            'Class': all_classes,
            'ClassName': [f'Class {c}' for c in all_classes]
        })
        
        # Process contingency table to extract transitions
        legacy_format = {
            'tb_legend': tb_legend
        }
        
        if contingency_df is not None and not contingency_df.empty:
            # For single-step: get transitions between first two time periods
            unique_times = sorted(contingency_df['time_from'].unique())
            if len(unique_times) >= 2:
                first_period = contingency_df[
                    (contingency_df['time_from'] == unique_times[0]) & 
                    (contingency_df['time_to'] == unique_times[1])
                ].copy()
                
                if not first_period.empty:
                    # Convert to legacy format: From, To, km2
                    single_step_data = pd.DataFrame({
                        'From': first_period['class_from'],
                        'To': first_period['class_to'],
                        'km2': first_period['count'] * 0.01  # Convert pixel count to km2 (assuming 100m pixels)
                    })
                    legacy_format['lulc_SingleStep'] = single_step_data
                else:
                    legacy_format['lulc_SingleStep'] = pd.DataFrame(columns=['From', 'To', 'km2'])
            else:
                legacy_format['lulc_SingleStep'] = pd.DataFrame(columns=['From', 'To', 'km2'])
            
            # For multi-step: aggregate ALL transitions by class (ignore time)
            # This creates a simple two-column Sankey: Origin → Destination
            multi_step_data = contingency_df.groupby(['class_from', 'class_to'])['count'].sum().reset_index()
            multi_step_data['km2'] = multi_step_data['count'] * 0.01  # Convert pixel count to km2
            
            # Rename columns to match legacy format
            multi_step_data = multi_step_data.rename(columns={'class_from': 'From', 'class_to': 'To'})
            multi_step_data = multi_step_data[['From', 'To', 'km2']]  # Reorder columns
            
            legacy_format['lulc_MultiStep'] = multi_step_data
        
        return legacy_format
        
    except Exception as e:
        warnings.warn(f"Failed to convert ContingencyTable to legacy format: {e}")
        return {
            'lulc_SingleStep': pd.DataFrame(columns=['From', 'To', 'km2']),
            'lulc_MultiStep': pd.DataFrame(columns=['From', 'To', 'km2']),
            'tb_legend': pd.DataFrame(columns=['Class', 'ClassName'])
        }


def plot_sankey(
    data: Union[Dict, Any],
    step_type: str = 'single',
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[Union[int, str], str]] = None,
    min_area_km2: float = 0.1,
    save_png: bool = True,
    save_html: bool = True,
    show_plot: bool = False,
    time_from: Optional[Union[str, int]] = None,
    time_to: Optional[Union[str, int]] = None,
    **kwargs
) -> Optional[Union[str, go.Figure]]:
    """
    Create Sankey diagrams with unified interface.
    
    This is the main function for creating all types of Sankey diagrams.
    It supports both legacy dict format and modern ContingencyTable objects.
    
    Parameters
    ----------
    data : dict or ContingencyTable
        Data for creating the Sankey diagram. Can be:
        - Dict with 'lulc_SingleStep'/'lulc_MultiStep' and 'tb_legend' keys (legacy format)
        - ContingencyTable object (modern format)
    step_type : str, default 'single'
        Type of Sankey diagram to create:
        - 'single': Single-step transitions (simple: category → category)
        - 'multi': Multi-step transitions (temporal: category-year → category-year)
    output_dir : str, default "outputs/"
        Directory to save output files
    period : str, default ""
        Period description for the plot title
    title : str, optional
        Custom title for the plot. If None, auto-generated
    custom_labels : dict, optional
        Custom labels for land use categories {class_id: label}
    min_area_km2 : float, default 0.1
        Minimum area threshold to include transitions (km²)
    save_png : bool, default True
        Whether to save PNG version
    save_html : bool, default True
        Whether to save HTML version
    show_plot : bool, default False
        Whether to display the plot
    time_from : str or int, optional
        Starting year for transition (for single-step)
    time_to : str or int, optional
        Ending year for transition (for single-step)
    **kwargs
        Additional arguments passed to plotting functions
        
    Returns
    -------
    str or None
        Path to saved HTML file if successful, None if creation failed
        
    Examples
    --------
    >>> # Single-step Sankey (simple: category → category)
    >>> plot_sankey(contingency_table, step_type='single')
    
    >>> # Multi-step Sankey (temporal: category-year → category-year)
    >>> plot_sankey(contingency_table, step_type='multi')
    """
    
    if not HAS_PLOTLY:
        print("⚠️ Plotly not available. Sankey diagrams require plotly.")
        return None
    
    # Handle different input types
    if hasattr(data, 'results') and hasattr(data.results, 'contingency_table'):
        # Modern ContingencyTable object
        contingency_df = data.results.contingency_table
    elif isinstance(data, dict):
        # Legacy dict format - extract data
        if step_type == 'single':
            legacy_data = data.get('lulc_SingleStep')
        else:
            legacy_data = data.get('lulc_MultiStep')
        
        if legacy_data is None or legacy_data.empty:
            print(f"❌ No data available for {step_type}-step Sankey")
            return None
            
        # Convert legacy to modern format for processing
        contingency_df = pd.DataFrame({
            'class_from': legacy_data['From'],
            'class_to': legacy_data['To'],
            'count': legacy_data['km2'] * 100,  # Convert back to pixel count
            'time_from': 2000,  # Default values
            'time_to': 2005
        })
    else:
        print("❌ Invalid contingency data format")
        return None
    
    if contingency_df is None or contingency_df.empty:
        print("❌ No data available for Sankey")
        return None
    
    # Create labels
    if custom_labels:
        label_map = custom_labels
    else:
        # Create simple labels
        unique_classes = list(set(contingency_df['class_from'].tolist() + contingency_df['class_to'].tolist()))
        label_map = {cls: f"Class {cls}" for cls in unique_classes}
    
    # Filter data by minimum area threshold
    contingency_df = contingency_df.copy()
    contingency_df['km2'] = contingency_df['count'] * 0.01
    filtered_data = contingency_df[contingency_df['km2'] >= min_area_km2].copy()
    
    if filtered_data.empty:
        print("❌ No significant transitions found")
        return None
    
    print(f"📊 Filtered data: {len(filtered_data)} transitions")
    print(filtered_data[['class_from', 'class_to', 'km2', 'time_from', 'time_to']].head())
    
    if step_type == 'single':
        return _create_single_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot)
    elif step_type == 'multi':
        return _create_multi_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot)
    elif step_type == 'complete':
        # Generate both single and multi-step diagrams
        print("📈 Generating complete analysis: both single-step and multi-step diagrams")
        single_result = _create_single_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot)
        multi_result = _create_multi_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot)
        return {'single_step': single_result, 'multi_step': multi_result}
    else:
        raise ValueError(f"Invalid step_type: {step_type}. Must be 'single', 'multi', or 'complete'")


def _create_single_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot):
    """Create simple single-step Sankey: category → category with professional styling and clear two-column layout"""
    
    # Aggregate by class only (ignore time) - like R onestep
    aggregated = filtered_data.groupby(['class_from', 'class_to'])['km2'].sum().reset_index()
    
    print(f"📈 Single-step aggregated: {len(aggregated)} unique transitions")
    
    # Create separate source and target nodes for clear two-column layout
    # This prevents confusion when same category appears as both source and target
    unique_sources = sorted(aggregated['class_from'].unique())
    unique_targets = sorted(aggregated['class_to'].unique())
    
    # Create node labels with clear source/target distinction (clean names without years)
    source_labels = [f"{label_map.get(cls, f'Class {cls}')}" for cls in unique_sources]
    target_labels = [f"{label_map.get(cls, f'Class {cls}')}" for cls in unique_targets]
    
    # Combine all labels (sources first, then targets)
    all_labels = source_labels + target_labels
    
    # Create mapping for indices
    source_to_index = {cls: i for i, cls in enumerate(unique_sources)}
    target_to_index = {cls: i + len(unique_sources) for i, cls in enumerate(unique_targets)}
    
    # Prepare data for Sankey with clear source→target mapping
    sources = [source_to_index[row['class_from']] for _, row in aggregated.iterrows()]
    targets = [target_to_index[row['class_to']] for _, row in aggregated.iterrows()]
    values = aggregated['km2'].tolist()
    
    print(f"📊 Two-column layout: {len(source_labels)} sources → {len(target_labels)} targets")
    print(f"   Source nodes: {source_labels[:3]}...")
    print(f"   Target nodes: {target_labels[:3]}...")
    
    # Professional color scheme with transparency
    # Create colors for all unique categories (not nodes)
    all_unique_classes = sorted(set(unique_sources + unique_targets))
    base_colors = _get_academic_colors()
    class_color_map = {cls: color for cls, color in zip(all_unique_classes, base_colors)}
    
    opacity = 0.8
    
    # Convert base colors to rgba format for nodes
    node_colors = []
    
    # Colors for source nodes
    for cls in unique_sources:
        color = class_color_map[cls]
        if color.startswith('#'):
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgba_color = f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})'
        else:
            rgba_color = color.replace('rgb(', 'rgba(').replace(')', f',{opacity})')
        node_colors.append(rgba_color)
    
    # Colors for target nodes (same logic)
    for cls in unique_targets:
        color = class_color_map[cls]
        if color.startswith('#'):
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgba_color = f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})'
        else:
            rgba_color = color.replace('rgb(', 'rgba(').replace(')', f',{opacity})')
        node_colors.append(rgba_color)
    
    # Create link colors based on source node colors with transparency
    link_opacity = 0.4
    link_colors = []
    for source_idx in sources:
        source_color = node_colors[source_idx]
        # Extract RGB from RGBA and create new RGBA with link opacity
        if source_color.startswith('rgba('):
            # Extract RGB values from rgba(R,G,B,A) format
            rgb_part = source_color.replace('rgba(', '').replace(')', '').split(',')
            r, g, b = rgb_part[0], rgb_part[1], rgb_part[2]
            link_color = f'rgba({r},{g},{b},{link_opacity})'
        else:
            # Fallback for other formats
            link_color = source_color.replace('rgb(', 'rgba(').replace(')', f',{link_opacity})')
        link_colors.append(link_color)
    
    # Create standard Sankey diagram (simplified like example)
    fig = go.Figure(data=[go.Sankey(
        valueformat=".0f",
        valuesuffix=" km²",
        # Academic node styling
        node=dict(
            pad=15,  # Standard padding
            thickness=15,  # Standard thickness
            line=dict(color="black", width=0.5),  # Standard borders
            label=all_labels,  # Use clean labels
            color=node_colors
        ),
        # Academic link styling
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    # Extract year range for title
    years = sorted(set(filtered_data['time_from'].tolist() + filtered_data['time_to'].tolist()))
    year_range = f"{min(years)} → {max(years)}" if len(years) > 1 else str(years[0])
    
    # Academic publication layout styling (simplified)
    fig_title = title or f"Single-step Land Use Transitions ({year_range})"
    fig.update_layout(
        title=dict(
            text=fig_title,
            x=0.5,
            xanchor='center',
            font=dict(
                family="Times New Roman, serif",
                size=14,
                color="black"
            )
        ),
        # Academic font styling
        font=dict(
            family="Times New Roman, serif",
            size=10,
            color="black"
        ),
        # Standard dimensions
        height=600,
        width=800,
        # Standard margins
        margin=dict(l=80, r=80, t=100, b=80),
        # Clean academic background
        paper_bgcolor='white',
        plot_bgcolor='white',
        # Remove default plotly branding
        showlegend=False
    )
    
    # Save files
    output_path = ensure_output_dir(output_dir)
    filename = "sankey_single_step"
    saved_path = save_plot_files(fig, output_path, filename, save_png, save_html, is_plotly=True)
    
    # Show plot if requested
    if show_plot and HAS_PLOTLY:
        fig.show()
    
    return saved_path


def _create_multi_step_sankey(filtered_data, label_map, output_dir, title, save_png, save_html, show_plot):
    """Create temporal multi-step Sankey: category-year → category-year"""
    
    # Create temporal nodes like R sankeyLand: "Category-Year"
    # First, create source and target nodes
    def create_node_name(class_id, time, label_map):
        label = label_map.get(class_id, f'Class {class_id}')
        return f"{label} ({time})"
    
    filtered_data['source'] = filtered_data.apply(
        lambda row: create_node_name(row['class_from'], row['time_from'], label_map), axis=1
    )
    filtered_data['target'] = filtered_data.apply(
        lambda row: create_node_name(row['class_to'], row['time_to'], label_map), axis=1
    )
    
    print(f"📈 Multi-step temporal nodes created")
    print("Source examples:", filtered_data['source'].unique()[:5])
    print("Target examples:", filtered_data['target'].unique()[:5])
    
    # Create unique nodes list and clean names (remove years)
    all_nodes = list(set(filtered_data['source'].tolist() + filtered_data['target'].tolist()))
    
    # Clean node names by removing (YEAR) part
    clean_node_names = []
    for node in all_nodes:
        if '(' in node and ')' in node:
            clean_name = node.split(' (')[0]  # Remove (YEAR) part
            clean_node_names.append(clean_name)
        else:
            clean_node_names.append(node)
    
    node_to_index = {node: i for i, node in enumerate(all_nodes)}
    
    # Extract base category for coloring
    def extract_category(node_name):
        # Extract category from "Category (year)" format or just use the clean name
        if '(' in node_name and ')' in node_name:
            return node_name.split(' (')[0]
        return node_name
    
    node_categories = [extract_category(node) for node in all_nodes]
    unique_categories = list(set(node_categories))
    base_colors = _get_academic_colors()
    
    # Professional color scheme with transparency
    opacity = 0.8
    category_color_map = {}
    for i, cat in enumerate(unique_categories):
        color = base_colors[i % len(base_colors)]
        if color.startswith('#'):
            # Convert hex to rgba
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgba_color = f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{opacity})'
        else:
            # Handle rgb format - convert to rgba
            rgba_color = color.replace('rgb(', 'rgba(').replace(')', f',{opacity})')
        category_color_map[cat] = rgba_color
    
    # Assign colors to nodes based on category
    node_colors = [category_color_map[extract_category(node)] for node in all_nodes]
    
    # Lists for Sankey
    sources = [node_to_index[row['source']] for _, row in filtered_data.iterrows()]
    targets = [node_to_index[row['target']] for _, row in filtered_data.iterrows()]
    values = filtered_data['km2'].tolist()
    
    # Create link colors based on source node colors with transparency
    link_opacity = 0.4
    link_colors = []
    for source_idx in sources:
        source_color = node_colors[source_idx]
        # Extract RGB from RGBA and create new RGBA with link opacity
        if source_color.startswith('rgba('):
            # Extract RGB values from rgba(R,G,B,A) format
            rgb_part = source_color.replace('rgba(', '').replace(')', '').split(',')
            r, g, b = rgb_part[0], rgb_part[1], rgb_part[2]
            link_color = f'rgba({r},{g},{b},{link_opacity})'
        else:
            # Fallback for other formats
            link_color = source_color.replace('rgb(', 'rgba(').replace(')', f',{link_opacity})')
        link_colors.append(link_color)
    
    # Create standard Sankey diagram (like Plotly example)
    fig = go.Figure(data=[go.Sankey(
        valueformat=".0f",
        valuesuffix=" km²",
        # Academic node styling following remote sensing publication standards
        node=dict(
            pad=15,  # Standard padding
            thickness=15,  # Standard thickness
            line=dict(color="black", width=0.5),  # Standard borders
            label=clean_node_names,  # Use clean names without (YEAR)
            color=node_colors
        ),
        # Academic link styling with enhanced visibility
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    # Extract year range for title
    years = sorted(set(filtered_data['time_from'].tolist() + filtered_data['time_to'].tolist()))
    year_range = f"{min(years)} → {max(years)}"
    
    # Academic publication layout styling (simplified)
    fig_title = title or f"Complete Multi-step Land Use Transitions ({year_range})"
    fig.update_layout(
        title=dict(
            text=fig_title,
            x=0.5,
            xanchor='center',
            font=dict(
                family="Times New Roman, serif",
                size=14,
                color="black"
            )
        ),
        # Academic font styling
        font=dict(
            family="Times New Roman, serif",
            size=10,
            color="black"
        ),
        # Standard dimensions
        height=600,
        width=800,
        # Standard margins
        margin=dict(l=80, r=80, t=100, b=80),
        # Clean academic background
        paper_bgcolor='white',
        plot_bgcolor='white',
        # Remove default plotly branding
        showlegend=False
    )
    
    # Save files
    output_path = ensure_output_dir(output_dir)
    filename = "sankey_multi_step"
    saved_path = save_plot_files(fig, output_path, filename, save_png, save_html, is_plotly=True)
    
    # Show plot if requested
    if show_plot and HAS_PLOTLY:
        fig.show()
    
    return saved_path


# Export only the main unified function
__all__ = [
    'plot_sankey',  # Main unified function
]
