"""
Bar chart plotting functions for land use area analysis.

This module provides functions for creating bar charts showing land use
areas, changes over time, and comparative analysis.
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
import pandas as pd
import numpy as np

from .plot_utils import (
    ensure_output_dir, create_category_labels, save_plot_files,
    validate_contingency_data, extract_data_for_plot, get_category_colors,
    HAS_PLOTLY, plt, sns
)

if HAS_PLOTLY:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots


def plot_barplot_lulc(
    contingency_data: Dict,
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    plot_type: str = 'grouped',
    save_png: bool = True,
    save_html: bool = True,
    figsize: tuple = (12, 8)
) -> Optional[str]:
    """
    Create bar plots showing land use areas across time periods.
    
    Parameters
    ----------
    contingency_data : dict
        Dictionary containing contingency table data
    output_dir : str
        Directory to save the output files
    period : str
        Period description for the plot title
    title : str, optional
        Custom title for the plot
    custom_labels : dict, optional
        Custom labels for land use categories
    plot_type : str
        Type of bar plot: 'grouped', 'stacked', or 'individual'
    save_png : bool
        Whether to save PNG version
    save_html : bool
        Whether to save HTML version (if plotly available)
    figsize : tuple
        Figure size (width, height)
        
    Returns
    -------
    str or None
        Path to saved file if successful, None otherwise
    """
    if not validate_contingency_data(contingency_data):
        print("❌ Invalid contingency data format")
        return None
    
    try:
        # Extract data - prefer multi-step for time series
        data, legend = extract_data_for_plot(contingency_data, prefer_singlestep=False)
        
        if data.empty:
            print("❌ No data available for area analysis")
            return None
        
        # Create category labels
        label_map = create_category_labels(data, legend, custom_labels)
        
        # Check if we have multi-step data with time periods
        time_columns = [col for col in data.columns if col.startswith('Year_') or col.isdigit()]
        
        if time_columns:
            # Multi-step data: aggregate areas by time period and category
            time_columns = sorted(time_columns)
            area_data = []
            
            for time_col in time_columns:
                period_name = time_col.replace('Year_', '')
                category_areas = data.groupby(time_col)['km2'].sum().reset_index()
                category_areas['Time_Period'] = period_name
                category_areas['Category'] = category_areas[time_col].map(label_map)
                area_data.append(category_areas[['Time_Period', 'Category', 'km2']])
            
            plot_data = pd.concat(area_data, ignore_index=True)
            
        else:
            # Single-step data: aggregate by From and To categories
            from_areas = data.groupby('From')['km2'].sum().reset_index()
            from_areas['Time_Period'] = 'Initial'
            from_areas['Category'] = from_areas['From'].map(label_map)
            from_areas = from_areas[['Time_Period', 'Category', 'km2']]
            
            to_areas = data.groupby('To')['km2'].sum().reset_index()
            to_areas['Time_Period'] = 'Final'
            to_areas['Category'] = to_areas['To'].map(label_map)
            to_areas = to_areas[['Time_Period', 'Category', 'km2']]
            
            plot_data = pd.concat([from_areas, to_areas], ignore_index=True)
        
        if plot_data.empty:
            print("❌ Could not prepare data for area plotting")
            return None
        
        # Create plots based on type and availability
        saved_files = {}
        
        if HAS_PLOTLY and save_html:
            # Create interactive Plotly plot
            saved_files.update(_create_plotly_barplot(
                plot_data, output_dir, period, title, plot_type
            ))
        
        if save_png:
            # Create matplotlib plot
            saved_files.update(_create_matplotlib_barplot(
                plot_data, output_dir, period, title, plot_type, figsize
            ))
        
        # Print summary
        total_area = plot_data['km2'].sum()
        n_categories = plot_data['Category'].nunique()
        n_periods = plot_data['Time_Period'].nunique()
        
        print(f"✅ Land use area bar plot created successfully")
        print(f"   Categories: {n_categories}")
        print(f"   Time periods: {n_periods}")
        print(f"   Total area: {total_area:.1f} km²")
        print(f"   Plot type: {plot_type}")
        
        return saved_files.get('html') or saved_files.get('png')
        
    except Exception as e:
        print(f"❌ Error creating land use area bar plot: {e}")
        import traceback
        traceback.print_exc()
        return None


def _create_plotly_barplot(
    plot_data: pd.DataFrame,
    output_dir: str,
    period: str,
    title: Optional[str],
    plot_type: str
) -> Dict[str, str]:
    """Create interactive Plotly bar plot."""
    saved_files = {}
    
    try:
        if plot_type == 'grouped':
            fig = px.bar(
                plot_data,
                x='Time_Period',
                y='km2',
                color='Category',
                title=title or f"Land Use Areas by Time Period{' - ' + period if period else ''}",
                labels={'km2': 'Area (km²)', 'Time_Period': 'Time Period'},
                barmode='group'
            )
        elif plot_type == 'stacked':
            fig = px.bar(
                plot_data,
                x='Time_Period',
                y='km2',
                color='Category',
                title=title or f"Land Use Areas (Stacked){' - ' + period if period else ''}",
                labels={'km2': 'Area (km²)', 'Time_Period': 'Time Period'},
                barmode='stack'
            )
        else:  # individual
            fig = px.bar(
                plot_data,
                x='Category',
                y='km2',
                color='Time_Period',
                title=title or f"Land Use Areas by Category{' - ' + period if period else ''}",
                labels={'km2': 'Area (km²)', 'Category': 'Land Use Category'},
                barmode='group'
            )
        
        # Update layout
        fig.update_layout(
            width=1200,
            height=600,
            font=dict(size=12),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            margin=dict(t=80, b=80, l=80, r=150)
        )
        
        # Add total area annotation
        total_area = plot_data['km2'].sum()
        fig.add_annotation(
            text=f"Total Area: {total_area:.1f} km²",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        )
        
        # Save HTML
        output_path = ensure_output_dir(output_dir) / "barras_area"
        output_path.mkdir(exist_ok=True)
        
        filename = f"area_por_classe_{plot_type}{('_' + period.replace(' ', '_')) if period else ''}"
        html_path = output_path / f"{filename}.html"
        fig.write_html(html_path)
        saved_files['html'] = str(html_path)
        print(f"✅ HTML saved: {html_path}")
        
        # Save PNG if possible
        try:
            png_path = output_path / f"{filename}.png"
            fig.write_image(png_path, width=1200, height=600, scale=2)
            saved_files['png'] = str(png_path)
            print(f"✅ PNG saved: {png_path}")
        except Exception as e:
            print(f"⚠️ Could not save PNG from Plotly: {e}")
        
    except Exception as e:
        print(f"⚠️ Error creating Plotly bar plot: {e}")
    
    return saved_files


def _create_matplotlib_barplot(
    plot_data: pd.DataFrame,
    output_dir: str,
    period: str,
    title: Optional[str],
    plot_type: str,
    figsize: tuple
) -> Dict[str, str]:
    """Create matplotlib bar plot."""
    saved_files = {}
    
    try:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get unique categories and colors
        categories = sorted(plot_data['Category'].unique())
        time_periods = sorted(plot_data['Time_Period'].unique())
        colors = get_category_colors(len(categories))
        
        if plot_type == 'grouped':
            # Grouped bar plot
            pivot_data = plot_data.pivot(index='Time_Period', columns='Category', values='km2').fillna(0)
            pivot_data.plot(kind='bar', ax=ax, color=colors[:len(categories)], width=0.8)
            ax.set_xlabel('Time Period', fontweight='bold')
            ax.set_title(title or f"Land Use Areas by Time Period{' - ' + period if period else ''}", 
                        fontweight='bold', pad=20)
            
        elif plot_type == 'stacked':
            # Stacked bar plot
            pivot_data = plot_data.pivot(index='Time_Period', columns='Category', values='km2').fillna(0)
            pivot_data.plot(kind='bar', ax=ax, stacked=True, color=colors[:len(categories)], width=0.8)
            ax.set_xlabel('Time Period', fontweight='bold')
            ax.set_title(title or f"Land Use Areas (Stacked){' - ' + period if period else ''}", 
                        fontweight='bold', pad=20)
            
        else:  # individual
            # Individual category plot
            pivot_data = plot_data.pivot(index='Category', columns='Time_Period', values='km2').fillna(0)
            pivot_data.plot(kind='bar', ax=ax, color=colors[:len(time_periods)], width=0.8)
            ax.set_xlabel('Land Use Category', fontweight='bold')
            ax.set_title(title or f"Land Use Areas by Category{' - ' + period if period else ''}", 
                        fontweight='bold', pad=20)
        
        ax.set_ylabel('Area (km²)', fontweight='bold')
        ax.legend(title='', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=45)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3)
        
        # Add total area annotation
        total_area = plot_data['km2'].sum()
        ax.text(
            0.02, 0.98, f"Total Area: {total_area:.1f} km²",
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            fontsize=10
        )
        
        plt.tight_layout()
        
        # Save PNG
        output_path = ensure_output_dir(output_dir) / "barras_area"
        output_path.mkdir(exist_ok=True)
        
        filename = f"area_por_classe_{plot_type}{('_' + period.replace(' ', '_')) if period else ''}"
        png_path = output_path / f"{filename}.png"
        plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
        saved_files['png'] = str(png_path)
        print(f"✅ PNG saved: {png_path}")
        
        plt.close(fig)
        
    except Exception as e:
        print(f"⚠️ Error creating matplotlib bar plot: {e}")
    
    return saved_files


def plot_change_frequency(
    contingency_data: Dict,
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    save_png: bool = True,
    figsize: tuple = (10, 6)
) -> Optional[str]:
    """
    Create bar plot showing frequency of changes by category.
    
    Parameters
    ----------
    contingency_data : dict
        Dictionary containing contingency table data
    output_dir : str
        Directory to save the output files
    period : str
        Period description for the plot title
    title : str, optional
        Custom title for the plot
    custom_labels : dict, optional
        Custom labels for land use categories
    save_png : bool
        Whether to save PNG version
    figsize : tuple
        Figure size (width, height)
        
    Returns
    -------
    str or None
        Path to saved PNG file if successful, None otherwise
    """
    if not validate_contingency_data(contingency_data):
        print("❌ Invalid contingency data format")
        return None
    
    try:
        # Extract data
        data, legend = extract_data_for_plot(contingency_data, prefer_singlestep=True)
        
        if data.empty:
            print("❌ No data available for change frequency analysis")
            return None
        
        # Create category labels
        label_map = create_category_labels(data, legend, custom_labels)
        
        # Count changes (transitions where From != To)
        changes = data[data['From'] != data['To']].copy()
        
        if changes.empty:
            print("❌ No land use changes found in data")
            return None
        
        # Count frequency of changes by category (both From and To)
        from_changes = changes.groupby('From').size()
        to_changes = changes.groupby('To').size()
        
        # Combine and create comprehensive frequency data
        all_categories = sorted(set(changes['From'].unique()) | set(changes['To'].unique()))
        
        change_data = []
        for cat in all_categories:
            cat_label = label_map.get(cat, f"Class_{cat}")
            from_count = from_changes.get(cat, 0)
            to_count = to_changes.get(cat, 0)
            total_count = from_count + to_count
            
            change_data.append({
                'Category': cat_label,
                'From_Changes': from_count,
                'To_Changes': to_count,
                'Total_Changes': total_count
            })
        
        freq_df = pd.DataFrame(change_data)
        
        if freq_df.empty:
            print("❌ Could not create change frequency data")
            return None
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Plot 1: Changes FROM each category (losses)
        bars1 = ax1.bar(range(len(freq_df)), freq_df['From_Changes'], 
                       color='red', alpha=0.7, label='Changes From')
        ax1.set_title('Changes FROM Each Category\n(Category Losses)', fontweight='bold')
        ax1.set_ylabel('Number of Transition Types')
        ax1.set_xticks(range(len(freq_df)))
        ax1.set_xticklabels(freq_df['Category'], rotation=45, ha='right')
        
        # Add value labels
        for bar, val in zip(bars1, freq_df['From_Changes']):
            if val > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{int(val)}', ha='center', va='bottom', fontsize=9)
        
        # Plot 2: Changes TO each category (gains)
        bars2 = ax2.bar(range(len(freq_df)), freq_df['To_Changes'], 
                       color='blue', alpha=0.7, label='Changes To')
        ax2.set_title('Changes TO Each Category\n(Category Gains)', fontweight='bold')
        ax2.set_ylabel('Number of Transition Types')
        ax2.set_xticks(range(len(freq_df)))
        ax2.set_xticklabels(freq_df['Category'], rotation=45, ha='right')
        
        # Add value labels
        for bar, val in zip(bars2, freq_df['To_Changes']):
            if val > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{int(val)}', ha='center', va='bottom', fontsize=9)
        
        # Set main title
        if title is None:
            title = f"Land Use Change Frequency{' - ' + period if period else ''}"
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)
        
        # Save outputs
        output_path = ensure_output_dir(output_dir) / "frequencia_mudancas"
        output_path.mkdir(exist_ok=True)
        
        filename = f"frequencia_mudancas{('_' + period.replace(' ', '_')) if period else ''}"
        saved_files = save_plot_files(
            fig, output_path, filename, save_png, False, is_plotly=False
        )
        
        # Print summary
        total_transitions = len(changes)
        most_active_from = freq_df.loc[freq_df['From_Changes'].idxmax(), 'Category']
        most_active_to = freq_df.loc[freq_df['To_Changes'].idxmax(), 'Category']
        
        print(f"✅ Change frequency analysis created successfully")
        print(f"   Total transitions: {total_transitions}")
        print(f"   Categories analyzed: {len(freq_df)}")
        print(f"   Most losses from: {most_active_from}")
        print(f"   Most gains to: {most_active_to}")
        
        return saved_files.get('png')
        
    except Exception as e:
        print(f"❌ Error creating change frequency plot: {e}")
        import traceback
        traceback.print_exc()
        return None


# Export functions
__all__ = [
    'plot_barplot_lulc',
    'plot_change_frequency'
]
