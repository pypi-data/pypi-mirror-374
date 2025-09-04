"""
Matrix heatmap plotting functions for land use transition analysis.

This module provides functions for creating transition matrix heatmaps
and contingency tables to visualize land use change patterns.
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
import pandas as pd
import numpy as np

from .plot_utils import (
    ensure_output_dir, create_category_labels, prepare_transition_matrix,
    save_plot_files, validate_contingency_data, extract_data_for_plot,
    get_category_colors, plt, sns
)


def plot_transition_matrix_heatmap(
    contingency_data: Dict,
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    normalize: str = 'none',
    show_values: bool = True,
    cmap: str = 'YlOrRd',
    save_png: bool = True,
    figsize: tuple = (12, 10)
) -> Optional[str]:
    """
    Create a transition matrix heatmap showing land use changes.
    
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
    normalize : str
        Normalization method: 'none', 'index' (rows), 'columns', or 'all'
    show_values : bool
        Whether to show values in heatmap cells
    cmap : str
        Colormap for the heatmap
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
            print("❌ No data available for transition matrix")
            return None
        
        # Create category labels
        label_map = create_category_labels(data, legend, custom_labels)
        
        # Create transition matrix
        matrix = prepare_transition_matrix(data, 'km2', 'From', 'To')
        
        if matrix.empty:
            print("❌ Could not create transition matrix")
            return None
        
        # Apply labels to matrix
        matrix.index = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
        matrix.columns = [label_map.get(col, f"Class_{col}") for col in matrix.columns]
        
        # Normalize matrix if requested
        if normalize == 'index':
            matrix_norm = matrix.div(matrix.sum(axis=1), axis=0) * 100
            value_format = '.1f'
            unit = '%'
        elif normalize == 'columns':
            matrix_norm = matrix.div(matrix.sum(axis=0), axis=1) * 100
            value_format = '.1f'
            unit = '%'
        elif normalize == 'all':
            matrix_norm = matrix / matrix.sum().sum() * 100
            value_format = '.2f'
            unit = '%'
        else:
            matrix_norm = matrix
            value_format = '.1f'
            unit = 'km²'
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create annotation format
        if show_values:
            annot = matrix_norm.round(2 if normalize == 'all' else 1)
            fmt = value_format
        else:
            annot = False
            fmt = ''
        
        # Plot heatmap
        im = sns.heatmap(
            matrix_norm,
            annot=annot,
            fmt=fmt,
            cmap=cmap,
            cbar_kws={'label': f'Area ({unit})'},
            square=True,
            linewidths=0.5,
            ax=ax
        )
        
        # Set title
        if title is None:
            norm_text = {
                'index': ' (Row Normalized)',
                'columns': ' (Column Normalized)', 
                'all': ' (Total Normalized)',
                'none': ''
            }.get(normalize, '')
            title = f"Land Use Transition Matrix{norm_text}{' - ' + period if period else ''}"
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('To (Final Period)', fontsize=12, fontweight='bold')
        ax.set_ylabel('From (Initial Period)', fontsize=12, fontweight='bold')
        
        # Rotate labels for better readability
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        # Add statistics annotation
        total_area = matrix.sum().sum()
        n_categories = len(matrix.index)
        persistent_area = np.diag(matrix).sum()
        change_area = total_area - persistent_area
        
        stats_text = (
            f"Total Area: {total_area:.1f} km²\n"
            f"Categories: {n_categories}\n"
            f"Persistent: {persistent_area:.1f} km² ({persistent_area/total_area*100:.1f}%)\n"
            f"Changed: {change_area:.1f} km² ({change_area/total_area*100:.1f}%)"
        )
        
        ax.text(
            0.02, 0.98, stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            fontsize=10
        )
        
        plt.tight_layout()
        
        # Save outputs
        output_path = ensure_output_dir(output_dir) / "matriz_contingencia"
        output_path.mkdir(exist_ok=True)
        
        norm_suffix = {
            'index': '_row_norm',
            'columns': '_col_norm',
            'all': '_total_norm',
            'none': ''
        }.get(normalize, '')
        
        filename = f"transition_matrix{norm_suffix}{('_' + period.replace(' ', '_')) if period else ''}"
        saved_files = save_plot_files(
            fig, output_path, filename, save_png, False, is_plotly=False
        )
        
        print(f"✅ Transition matrix heatmap created successfully")
        print(f"   Matrix size: {matrix.shape[0]}×{matrix.shape[1]}")
        print(f"   Total area: {total_area:.1f} km²")
        print(f"   Normalization: {normalize}")
        
        return saved_files.get('png')
        
    except Exception as e:
        print(f"❌ Error creating transition matrix heatmap: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_contingency_table(
    contingency_data: Dict,
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    show_percentages: bool = True,
    save_png: bool = True,
    figsize: tuple = (14, 10)
) -> Optional[str]:
    """
    Create a detailed contingency table visualization.
    
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
    show_percentages : bool
        Whether to show percentages alongside areas
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
            print("❌ No data available for contingency table")
            return None
        
        # Create category labels
        label_map = create_category_labels(data, legend, custom_labels)
        
        # Create transition matrix
        matrix = prepare_transition_matrix(data, 'km2', 'From', 'To')
        
        if matrix.empty:
            print("❌ Could not create transition matrix")
            return None
        
        # Apply labels to matrix
        matrix.index = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
        matrix.columns = [label_map.get(col, f"Class_{col}") for col in matrix.columns]
        
        # Calculate percentages
        total_area = matrix.sum().sum()
        percent_matrix = (matrix / total_area * 100)
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. Raw values heatmap
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.1f',
            cmap='Blues',
            cbar_kws={'label': 'Area (km²)'},
            ax=ax1
        )
        ax1.set_title('Transition Areas (km²)', fontweight='bold')
        ax1.set_xlabel('To')
        ax1.set_ylabel('From')
        
        # 2. Percentage heatmap
        sns.heatmap(
            percent_matrix,
            annot=True,
            fmt='.2f',
            cmap='Oranges',
            cbar_kws={'label': 'Percentage (%)'},
            ax=ax2
        )
        ax2.set_title('Transition Percentages (%)', fontweight='bold')
        ax2.set_xlabel('To')
        ax2.set_ylabel('From')
        
        # 3. Row-normalized (gains/losses by initial class)
        row_norm = matrix.div(matrix.sum(axis=1), axis=0) * 100
        sns.heatmap(
            row_norm,
            annot=True,
            fmt='.1f',
            cmap='Greens',
            cbar_kws={'label': 'Row Percentage (%)'},
            ax=ax3
        )
        ax3.set_title('Transitions by Initial Class (%)', fontweight='bold')
        ax3.set_xlabel('To')
        ax3.set_ylabel('From')
        
        # 4. Column-normalized (gains/losses by final class)
        col_norm = matrix.div(matrix.sum(axis=0), axis=1) * 100
        sns.heatmap(
            col_norm,
            annot=True,
            fmt='.1f',
            cmap='Purples',
            cbar_kws={'label': 'Column Percentage (%)'},
            ax=ax4
        )
        ax4.set_title('Transitions by Final Class (%)', fontweight='bold')
        ax4.set_xlabel('To')
        ax4.set_ylabel('From')
        
        # Set main title
        if title is None:
            title = f"Land Use Contingency Analysis{' - ' + period if period else ''}"
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        # Rotate labels for all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.94)
        
        # Save outputs
        output_path = ensure_output_dir(output_dir) / "matriz_contingencia"
        output_path.mkdir(exist_ok=True)
        
        filename = f"contingency_analysis{('_' + period.replace(' ', '_')) if period else ''}"
        saved_files = save_plot_files(
            fig, output_path, filename, save_png, False, is_plotly=False
        )
        
        # Calculate summary statistics
        persistent_area = np.diag(matrix).sum()
        change_area = total_area - persistent_area
        n_categories = len(matrix.index)
        
        print(f"✅ Contingency table visualization created successfully")
        print(f"   Matrix size: {matrix.shape[0]}×{matrix.shape[1]}")
        print(f"   Total area: {total_area:.1f} km²")
        print(f"   Persistent area: {persistent_area:.1f} km² ({persistent_area/total_area*100:.1f}%)")
        print(f"   Changed area: {change_area:.1f} km² ({change_area/total_area*100:.1f}%)")
        
        return saved_files.get('png')
        
    except Exception as e:
        print(f"❌ Error creating contingency table: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_diagonal_analysis(
    contingency_data: Dict,
    output_dir: str = "outputs/",
    period: str = "",
    title: Optional[str] = None,
    custom_labels: Optional[Dict[str, str]] = None,
    save_png: bool = True,
    figsize: tuple = (12, 8)
) -> Optional[str]:
    """
    Create a diagonal analysis showing persistence vs change.
    
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
            print("❌ No data available for diagonal analysis")
            return None
        
        # Create category labels
        label_map = create_category_labels(data, legend, custom_labels)
        
        # Create transition matrix
        matrix = prepare_transition_matrix(data, 'km2', 'From', 'To')
        
        if matrix.empty:
            print("❌ Could not create transition matrix")
            return None
        
        # Apply labels to matrix
        matrix.index = [label_map.get(idx, f"Class_{idx}") for idx in matrix.index]
        matrix.columns = [label_map.get(col, f"Class_{col}") for col in matrix.columns]
        
        # Calculate persistence and change for each category
        categories = matrix.index
        persistence = []
        losses = []
        gains = []
        net_change = []
        
        for cat in categories:
            if cat in matrix.index and cat in matrix.columns:
                persist = matrix.loc[cat, cat]
                total_from = matrix.loc[cat, :].sum()
                total_to = matrix.loc[:, cat].sum()
                loss = total_from - persist
                gain = total_to - persist
                net = gain - loss
                
                persistence.append(persist)
                losses.append(loss)
                gains.append(gain)
                net_change.append(net)
            else:
                persistence.append(0)
                losses.append(0)
                gains.append(0)
                net_change.append(0)
        
        # Create DataFrame for plotting
        analysis_df = pd.DataFrame({
            'Category': categories,
            'Persistence': persistence,
            'Losses': losses,
            'Gains': gains,
            'Net_Change': net_change
        })
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. Persistence bar plot
        bars1 = ax1.bar(range(len(categories)), persistence, color='green', alpha=0.7)
        ax1.set_title('Class Persistence', fontweight='bold')
        ax1.set_ylabel('Area (km²)')
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, val in zip(bars1, persistence):
            if val > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(persistence)*0.01,
                        f'{val:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Gains and Losses
        x = range(len(categories))
        width = 0.35
        ax2.bar([i - width/2 for i in x], losses, width, label='Losses', color='red', alpha=0.7)
        ax2.bar([i + width/2 for i in x], gains, width, label='Gains', color='blue', alpha=0.7)
        ax2.set_title('Gains and Losses by Class', fontweight='bold')
        ax2.set_ylabel('Area (km²)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right')
        ax2.legend()
        
        # 3. Net change
        colors = ['red' if x < 0 else 'blue' for x in net_change]
        bars3 = ax3.bar(range(len(categories)), net_change, color=colors, alpha=0.7)
        ax3.set_title('Net Change by Class', fontweight='bold')
        ax3.set_ylabel('Net Change (km²)')
        ax3.set_xticks(range(len(categories)))
        ax3.set_xticklabels(categories, rotation=45, ha='right')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars3, net_change):
            if abs(val) > max(abs(min(net_change)), max(net_change)) * 0.05:
                ax3.text(bar.get_x() + bar.get_width()/2, 
                        bar.get_height() + (max(net_change)*0.02 if val >= 0 else -max(net_change)*0.05),
                        f'{val:.1f}', ha='center', va='bottom' if val >= 0 else 'top', fontsize=9)
        
        # 4. Percentage breakdown
        total_areas = [p + l for p, l in zip(persistence, losses)]
        persist_pct = [p/t*100 if t > 0 else 0 for p, t in zip(persistence, total_areas)]
        change_pct = [100 - p for p in persist_pct]
        
        ax4.bar(range(len(categories)), persist_pct, label='Persistence %', color='green', alpha=0.7)
        ax4.bar(range(len(categories)), change_pct, bottom=persist_pct, label='Change %', color='orange', alpha=0.7)
        ax4.set_title('Persistence vs Change (%)', fontweight='bold')
        ax4.set_ylabel('Percentage (%)')
        ax4.set_xticks(range(len(categories)))
        ax4.set_xticklabels(categories, rotation=45, ha='right')
        ax4.legend()
        ax4.set_ylim(0, 100)
        
        # Set main title
        if title is None:
            title = f"Diagonal Analysis - Persistence vs Change{' - ' + period if period else ''}"
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.94)
        
        # Save outputs
        output_path = ensure_output_dir(output_dir) / "matriz_contingencia"
        output_path.mkdir(exist_ok=True)
        
        filename = f"diagonal_analysis{('_' + period.replace(' ', '_')) if period else ''}"
        saved_files = save_plot_files(
            fig, output_path, filename, save_png, False, is_plotly=False
        )
        
        # Calculate summary statistics
        total_persistence = sum(persistence)
        total_change = sum(losses)
        total_area = total_persistence + total_change
        
        print(f"✅ Diagonal analysis created successfully")
        print(f"   Categories analyzed: {len(categories)}")
        print(f"   Total persistence: {total_persistence:.1f} km² ({total_persistence/total_area*100:.1f}%)")
        print(f"   Total change: {total_change:.1f} km² ({total_change/total_area*100:.1f}%)")
        
        return saved_files.get('png')
        
    except Exception as e:
        print(f"❌ Error creating diagonal analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


# Export functions
__all__ = [
    'plot_transition_matrix_heatmap',
    'plot_contingency_table',
    'plot_diagonal_analysis'
]
