"""
Change frequency analysis for multi-year land use data.

This module implements specialized analysis for calculating and visualizing
land use change frequency patterns across multiple years.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from ..base import (
    SpatialAnalyzerBase, 
    AnalysisResult, 
    AnalysisError,
    PlotConfig,
    GeospatialDataManager,
    CartographicElements
)


class FrequencyAnalyzer(SpatialAnalyzerBase):
    """
    Specialized analyzer for land use change frequency analysis.
    
    This analyzer calculates how frequently each pixel changes land use
    class across multiple years, providing insights into landscape
    stability and dynamics.
    """
    
    def __init__(self):
        """Initialize frequency analyzer."""
        super().__init__()
        self.analysis_type = "change_frequency"
        
    def analyze(self, config: PlotConfig) -> AnalysisResult:
        """
        Perform change frequency analysis.
        
        Parameters
        ----------
        config : PlotConfig
            Analysis configuration
            
        Returns
        -------
        AnalysisResult
            Analysis results with frequency maps and statistics
        """
        try:
            print(f"🔍 Starting change frequency analysis...")
            
            # Load and validate data
            data_manager = GeospatialDataManager()
            loaded_data = data_manager.load_and_validate(config.images_data)
            
            # Calculate change frequency
            frequency_results = self._calculate_change_frequency(
                loaded_data['image_stack'],
                loaded_data['sorted_years'],
                config
            )
            
            # Calculate statistics
            statistics = self._calculate_frequency_statistics(
                frequency_results,
                loaded_data,
                config
            )
            
            # Prepare result
            result = AnalysisResult(
                analysis_type=self.analysis_type,
                primary_data=frequency_results['frequency_map'],
                secondary_data={
                    'change_years': frequency_results['change_years'],
                    'annual_changes': frequency_results['annual_changes'],
                    'change_matrix': frequency_results['change_matrix'],
                    'valid_mask': frequency_results['valid_mask']
                },
                statistics=statistics,
                metadata={
                    'years': loaded_data['sorted_years'],
                    'n_years': len(loaded_data['sorted_years']),
                    'threshold': config.change_threshold,
                    'max_possible_changes': len(loaded_data['sorted_years']) - 1,
                    'total_changes': statistics['total_changes']
                }
            )
            
            print(f"✅ Change frequency analysis completed")
            return result
            
        except Exception as e:
            raise AnalysisError(f"Change frequency analysis failed: {e}")
            
    def _calculate_change_frequency(self, 
                                  image_stack: np.ndarray,
                                  years: List[str],
                                  config: PlotConfig) -> Dict[str, Any]:
        """
        Calculate change frequency for each pixel.
        
        Parameters
        ----------
        image_stack : np.ndarray
            3D array [time, row, col]
        years : List[str]
            Sorted year labels
        config : PlotConfig
            Analysis configuration
            
        Returns
        -------
        Dict[str, Any]
            Frequency calculation results
        """
        if image_stack.size == 0:
            raise ValueError("Empty image stack provided")
            
        n_years, rows, cols = image_stack.shape
        
        print(f"📊 Calculating change frequency for {n_years} years...")
        
        # Get valid pixels (non-zero in all years)
        valid_mask = np.all(image_stack != 0, axis=0)
        
        # Initialize frequency map
        frequency_map = np.zeros((rows, cols), dtype=np.int32)
        
        # Store years when changes occurred for each pixel
        change_years = {}
        
        # Calculate annual changes
        annual_changes = {}
        
        # Track all changes for matrix calculation
        all_changes = []
        
        # Calculate changes for each pixel
        for i in range(rows):
            for j in range(cols):
                if valid_mask[i, j]:
                    pixel_series = image_stack[:, i, j]
                    
                    # Find change points
                    changes = []
                    change_count = 0
                    
                    for t in range(1, n_years):
                        if pixel_series[t] != pixel_series[t-1]:
                            changes.append(t)
                            change_count += 1
                            all_changes.append({
                                'year_index': t,
                                'year': years[t],
                                'from_class': pixel_series[t-1],
                                'to_class': pixel_series[t],
                                'pixel': (i, j)
                            })
                            
                    # Apply threshold
                    if change_count >= config.change_threshold:
                        frequency_map[i, j] = change_count
                        change_years[(i, j)] = [years[idx] for idx in changes]
                        
        # Calculate annual change statistics
        for year_idx in range(1, n_years):
            year = years[year_idx]
            
            # Count changes in this year
            year_changes = [c for c in all_changes if c['year_index'] == year_idx]
            annual_changes[year] = {
                'total_changes': len(year_changes),
                'change_percentage': len(year_changes) / np.sum(valid_mask) * 100 if np.sum(valid_mask) > 0 else 0,
                'transitions': self._count_transitions(year_changes)
            }
            
        # Create change matrix (from-to transitions)
        change_matrix = self._create_change_matrix(all_changes, image_stack)
        
        print(f"📈 Found {len(change_years)} pixels with {config.change_threshold}+ changes")
        print(f"📊 Total changes recorded: {len(all_changes)}")
        
        return {
            'frequency_map': frequency_map,
            'change_years': change_years,
            'annual_changes': annual_changes,
            'change_matrix': change_matrix,
            'valid_mask': valid_mask,
            'all_changes': all_changes
        }
        
    def _count_transitions(self, year_changes: List[Dict]) -> Dict[str, int]:
        """Count transition types for a specific year."""
        transitions = {}
        for change in year_changes:
            transition = f"{change['from_class']}->{change['to_class']}"
            transitions[transition] = transitions.get(transition, 0) + 1
        return transitions
        
    def _create_change_matrix(self, 
                            all_changes: List[Dict],
                            image_stack: np.ndarray) -> np.ndarray:
        """Create change matrix showing from-to transitions."""
        # Get unique classes
        unique_classes = np.unique(image_stack[image_stack != 0])
        n_classes = len(unique_classes)
        
        # Create class mapping
        class_to_idx = {cls: i for i, cls in enumerate(unique_classes)}
        
        # Initialize change matrix
        change_matrix = np.zeros((n_classes, n_classes), dtype=np.int32)
        
        # Count transitions
        for change in all_changes:
            from_class = change['from_class']
            to_class = change['to_class']
            
            if from_class in class_to_idx and to_class in class_to_idx:
                from_idx = class_to_idx[from_class]
                to_idx = class_to_idx[to_class]
                change_matrix[from_idx, to_idx] += 1
                
        return change_matrix
        
    def _calculate_frequency_statistics(self, 
                                      frequency_results: Dict[str, Any],
                                      loaded_data: Dict[str, Any],
                                      config: PlotConfig) -> Dict[str, Any]:
        """Calculate comprehensive frequency statistics."""
        frequency_map = frequency_results['frequency_map']
        change_years = frequency_results['change_years']
        annual_changes = frequency_results['annual_changes']
        valid_mask = frequency_results['valid_mask']
        all_changes = frequency_results['all_changes']
        
        total_pixels = int(np.sum(valid_mask))
        changing_pixels = int(np.sum(frequency_map > 0))
        total_changes = len(all_changes)
        
        # Basic statistics
        stats = {
            'total_pixels': total_pixels,
            'changing_pixels': changing_pixels,
            'stable_pixels': total_pixels - changing_pixels,
            'change_percentage': changing_pixels / total_pixels * 100 if total_pixels > 0 else 0,
            'total_changes': total_changes,
            'threshold': config.change_threshold
        }
        
        # Frequency distribution
        if changing_pixels > 0:
            change_values = frequency_map[frequency_map > 0]
            stats.update({
                'mean_changes_per_pixel': float(np.mean(change_values)),
                'max_changes_per_pixel': int(np.max(change_values)),
                'min_changes_per_pixel': int(np.min(change_values)),
                'std_changes_per_pixel': float(np.std(change_values))
            })
            
            # Change frequency categories
            low_change = np.sum((change_values >= 1) & (change_values <= 2))
            medium_change = np.sum((change_values >= 3) & (change_values <= 5))
            high_change = np.sum(change_values > 5)
            
            stats['frequency_categories'] = {
                'low_change_pixels': int(low_change),      # 1-2 changes
                'medium_change_pixels': int(medium_change), # 3-5 changes
                'high_change_pixels': int(high_change)      # 6+ changes
            }
        else:
            stats.update({
                'mean_changes_per_pixel': 0.0,
                'max_changes_per_pixel': 0,
                'min_changes_per_pixel': 0,
                'std_changes_per_pixel': 0.0,
                'frequency_categories': {
                    'low_change_pixels': 0,
                    'medium_change_pixels': 0,
                    'high_change_pixels': 0
                }
            })
            
        # Annual change statistics
        stats['annual_statistics'] = {}
        if annual_changes:
            annual_totals = [data['total_changes'] for data in annual_changes.values()]
            annual_percentages = [data['change_percentage'] for data in annual_changes.values()]
            
            stats['annual_statistics'] = {
                'mean_annual_changes': float(np.mean(annual_totals)),
                'max_annual_changes': max(annual_totals),
                'min_annual_changes': min(annual_totals),
                'std_annual_changes': float(np.std(annual_totals)),
                'mean_annual_percentage': float(np.mean(annual_percentages)),
                'years_with_most_changes': max(annual_changes.keys(), 
                                              key=lambda k: annual_changes[k]['total_changes']),
                'years_with_least_changes': min(annual_changes.keys(), 
                                               key=lambda k: annual_changes[k]['total_changes'])
            }
            
        # Most common transitions
        if all_changes:
            transition_counts = {}
            for change in all_changes:
                transition = f"{change['from_class']}->{change['to_class']}"
                transition_counts[transition] = transition_counts.get(transition, 0) + 1
                
            # Sort by frequency
            sorted_transitions = sorted(transition_counts.items(), 
                                      key=lambda x: x[1], reverse=True)
            
            stats['most_common_transitions'] = sorted_transitions[:10]  # Top 10
            
        return stats
        
    def plot(self, result: AnalysisResult, config: PlotConfig) -> Optional[Path]:
        """
        Create frequency visualization.
        
        Parameters
        ----------
        result : AnalysisResult
            Analysis results
        config : PlotConfig
            Plot configuration
            
        Returns
        -------
        Optional[Path]
            Path to saved plot if successful
        """
        try:
            print("🎨 Creating change frequency visualization...")
            
            # Create figure
            fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
            
            # Get frequency map
            frequency_map = result.primary_data
            
            # Setup cartographic elements
            cartographic = CartographicElements()
            
            # Create colormap for frequency
            cmap, norm, labels = cartographic.create_colormap('change_frequency')
            
            # Display frequency map
            im = ax.imshow(frequency_map, 
                          cmap=cmap, 
                          norm=norm,
                          interpolation=config.interpolation,
                          alpha=config.alpha)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Number of Changes', rotation=270, labelpad=20)
            
            # Add legend if requested
            if config.show_legend:
                # Create custom labels based on frequency ranges
                max_changes = result.metadata['max_possible_changes']
                if max_changes <= 10:
                    freq_labels = ['No Change'] + [f'{i} Change{"s" if i>1 else ""}' 
                                                   for i in range(1, max_changes + 1)]
                else:
                    freq_labels = ['No Change', '1-2 Changes', '3-5 Changes', 
                                  '6+ Changes']
                    
                cartographic.add_legend(ax, cmap, freq_labels[:len(cmap.colors)])
                
            # Add title
            title = config.title or f"Land Use Change Frequency ({result.metadata['years'][0]}-{result.metadata['years'][-1]})"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add subtitle with statistics
            change_pct = result.statistics['change_percentage']
            total_changes = result.statistics['total_changes']
            subtitle = (f"Threshold: {config.change_threshold}+ changes | "
                       f"Changing Area: {change_pct:.1f}% | "
                       f"Total Changes: {total_changes:,}")
            ax.text(0.5, -0.1, subtitle, 
                   transform=ax.transAxes, 
                   ha='center', va='top',
                   fontsize=10, style='italic')
            
            # Remove axis ticks
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Add cartographic elements
            if config.show_scale_bar and config.pixel_size:
                cartographic.add_scale_bar(ax, config.pixel_size)
                
            if config.show_north_arrow:
                cartographic.add_north_arrow(ax)
                
            plt.tight_layout()
            
            # Save if requested
            if config.save_path:
                save_path = self._save_plot(fig, config)
                plt.close(fig)
                return save_path
            else:
                plt.show()
                return None
                
        except Exception as e:
            raise AnalysisError(f"Frequency plotting failed: {e}")
            
    def plot_annual_changes(self, 
                           result: AnalysisResult, 
                           config: PlotConfig) -> Optional[Path]:
        """
        Create annual change frequency plot.
        
        Parameters
        ----------
        result : AnalysisResult
            Analysis results
        config : PlotConfig
            Plot configuration
            
        Returns
        -------
        Optional[Path]
            Path to saved plot if successful
        """
        try:
            print("📊 Creating annual change frequency plot...")
            
            annual_changes = result.secondary_data['annual_changes']
            years = list(annual_changes.keys())
            change_counts = [annual_changes[year]['total_changes'] for year in years]
            change_percentages = [annual_changes[year]['change_percentage'] for year in years]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), dpi=config.dpi)
            
            # Plot absolute change counts
            bars1 = ax1.bar(years, change_counts, color='steelblue', alpha=0.7)
            ax1.set_title('Annual Change Frequency (Absolute)', fontweight='bold')
            ax1.set_ylabel('Number of Changes')
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, count in zip(bars1, change_counts):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(change_counts)*0.01,
                        f'{count:,}', ha='center', va='bottom', fontsize=9)
                        
            # Plot percentage changes
            bars2 = ax2.bar(years, change_percentages, color='orange', alpha=0.7)
            ax2.set_title('Annual Change Frequency (Percentage)', fontweight='bold')
            ax2.set_ylabel('Percentage of Landscape (%)')
            ax2.set_xlabel('Year')
            ax2.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, pct in zip(bars2, change_percentages):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(change_percentages)*0.01,
                        f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)
                        
            # Rotate x-axis labels if many years
            if len(years) > 8:
                for ax in [ax1, ax2]:
                    ax.tick_params(axis='x', rotation=45)
                    
            plt.tight_layout()
            
            # Save if requested
            if config.save_path:
                annual_save_path = config.save_path.parent / f"{config.save_path.stem}_annual.{config.save_format}"
                save_path = self._save_plot(fig, config, annual_save_path)
                plt.close(fig)
                return save_path
            else:
                plt.show()
                return None
                
        except Exception as e:
            raise AnalysisError(f"Annual frequency plotting failed: {e}")
            
    def _validate_inputs(self, config: PlotConfig) -> None:
        """Validate inputs specific to frequency analysis."""
        super()._validate_inputs(config)
        
        if config.change_threshold < 0:
            raise AnalysisError("change_threshold must be non-negative")
            
        if len(config.images_data) < 2:
            raise AnalysisError("Need at least 2 years of data for frequency analysis")
            
    def get_analysis_summary(self, result: AnalysisResult) -> str:
        """Get human-readable analysis summary."""
        stats = result.statistics
        metadata = result.metadata
        
        summary_lines = [
            f"Change Frequency Analysis Summary",
            f"="*40,
            f"Period: {metadata['years'][0]} - {metadata['years'][-1]} ({metadata['n_years']} years)",
            f"Change Threshold: {metadata['threshold']}+ changes",
            f"Max Possible Changes: {metadata['max_possible_changes']}",
            f"",
            f"Results:",
            f"  Total Pixels: {stats['total_pixels']:,}",
            f"  Changing Pixels: {stats['changing_pixels']:,} ({stats['change_percentage']:.1f}%)",
            f"  Stable Pixels: {stats['stable_pixels']:,}",
            f"  Total Changes: {stats['total_changes']:,}",
            f"",
        ]
        
        if 'mean_changes_per_pixel' in stats:
            summary_lines.extend([
                f"Change Statistics:",
                f"  Mean Changes/Pixel: {stats['mean_changes_per_pixel']:.1f}",
                f"  Max Changes/Pixel: {stats['max_changes_per_pixel']}",
                f"  Range: {stats['min_changes_per_pixel']} - {stats['max_changes_per_pixel']}",
                f"",
            ])
            
        if 'frequency_categories' in stats:
            categories = stats['frequency_categories']
            summary_lines.extend([
                f"Change Intensity Categories:",
                f"  Low (1-2 changes): {categories['low_change_pixels']:,} pixels",
                f"  Medium (3-5 changes): {categories['medium_change_pixels']:,} pixels",
                f"  High (6+ changes): {categories['high_change_pixels']:,} pixels",
                f"",
            ])
            
        if 'annual_statistics' in stats and stats['annual_statistics']:
            annual = stats['annual_statistics']
            summary_lines.extend([
                f"Annual Change Pattern:",
                f"  Mean Annual Changes: {annual['mean_annual_changes']:.0f}",
                f"  Most Active Year: {annual['years_with_most_changes']} ({annual['max_annual_changes']} changes)",
                f"  Least Active Year: {annual['years_with_least_changes']} ({annual['min_annual_changes']} changes)",
                f"",
            ])
            
        if 'most_common_transitions' in stats:
            transitions = stats['most_common_transitions'][:5]  # Top 5
            summary_lines.extend([
                f"Most Common Transitions:",
            ])
            for transition, count in transitions:
                pct = count / stats['total_changes'] * 100 if stats['total_changes'] > 0 else 0
                summary_lines.append(f"  {transition}: {count:,} ({pct:.1f}%)")
                
        return '\n'.join(summary_lines)
