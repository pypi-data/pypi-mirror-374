"""
Persistence analysis for multi-year land use data.

This module implements specialized analysis for calculating and visualizing
land use persistence patterns across multiple years.
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


class PersistenceAnalyzer(SpatialAnalyzerBase):
    """
    Specialized analyzer for land use persistence analysis.
    
    This analyzer calculates persistence patterns by identifying pixels
    that maintain the same land use class across multiple years.
    """
    
    def __init__(self):
        """Initialize persistence analyzer."""
        super().__init__()
        self.analysis_type = "persistence"
        
    def analyze(self, config: PlotConfig) -> AnalysisResult:
        """
        Perform persistence analysis.
        
        Parameters
        ----------
        config : PlotConfig
            Analysis configuration
            
        Returns
        -------
        AnalysisResult
            Analysis results with persistence maps and statistics
        """
        try:
            print(f"🔍 Starting persistence analysis...")
            
            # Load and validate data
            data_manager = GeospatialDataManager()
            loaded_data = data_manager.load_and_validate(config.images_data)
            
            # Calculate persistence
            persistence_results = self._calculate_persistence(
                loaded_data['image_stack'],
                loaded_data['sorted_years'],
                config
            )
            
            # Calculate statistics
            statistics = self._calculate_persistence_statistics(
                persistence_results,
                loaded_data,
                config
            )
            
            # Prepare result
            result = AnalysisResult(
                analysis_type=self.analysis_type,
                primary_data=persistence_results['persistence_map'],
                secondary_data={
                    'class_persistence': persistence_results['class_persistence'],
                    'persistence_percentage': persistence_results['persistence_percentage'],
                    'valid_mask': persistence_results['valid_mask']
                },
                statistics=statistics,
                metadata={
                    'years': loaded_data['sorted_years'],
                    'n_years': len(loaded_data['sorted_years']),
                    'threshold': config.persistence_threshold,
                    'min_years': config.min_persistence_years,
                    'total_classes': len(statistics['class_persistence'])
                }
            )
            
            print(f"✅ Persistence analysis completed")
            return result
            
        except Exception as e:
            raise AnalysisError(f"Persistence analysis failed: {e}")
            
    def _calculate_persistence(self, 
                             image_stack: np.ndarray,
                             years: List[str],
                             config: PlotConfig) -> Dict[str, Any]:
        """
        Calculate persistence maps and statistics.
        
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
            Persistence calculation results
        """
        if image_stack.size == 0:
            raise ValueError("Empty image stack provided")
            
        n_years, rows, cols = image_stack.shape
        min_years = config.min_persistence_years
        
        print(f"📊 Calculating persistence for {n_years} years...")
        
        # Get valid pixels (non-zero in all years)
        valid_mask = np.all(image_stack != 0, axis=0)
        
        # Initialize persistence map
        persistence_map = np.zeros((rows, cols), dtype=np.float32)
        
        # Get unique classes (excluding 0)
        unique_classes = np.unique(image_stack[image_stack != 0])
        class_persistence = {}
        
        # Calculate persistence for each class
        for class_val in unique_classes:
            print(f"  Processing class {class_val}...")
            
            # Create mask for pixels of this class in each year
            class_masks = image_stack == class_val
            
            # Count consecutive years for each pixel
            persistence_count = np.sum(class_masks, axis=0)
            
            # Apply minimum years threshold
            persistent_pixels = (persistence_count >= min_years) & valid_mask
            
            # Calculate persistence percentage for this class
            persistence_percentage = persistence_count / n_years
            
            # Update persistence map where this class is persistent
            persistence_map[persistent_pixels] = persistence_percentage[persistent_pixels]
            
            # Store class-specific statistics
            class_persistence[int(class_val)] = {
                'total_pixels': int(np.sum(class_masks[0])),  # Pixels in first year
                'persistent_pixels': int(np.sum(persistent_pixels)),
                'max_persistence': float(np.max(persistence_percentage[persistent_pixels]) 
                                      if np.any(persistent_pixels) else 0),
                'mean_persistence': float(np.mean(persistence_percentage[persistent_pixels]) 
                                       if np.any(persistent_pixels) else 0)
            }
            
        # Apply threshold to persistence map
        threshold_mask = persistence_map >= config.persistence_threshold
        persistence_map_thresholded = np.where(threshold_mask, persistence_map, 0)
        
        # Calculate overall persistence percentage
        total_valid_pixels = np.sum(valid_mask)
        persistent_pixels = np.sum(threshold_mask & valid_mask)
        overall_persistence_pct = (persistent_pixels / total_valid_pixels * 100 
                                 if total_valid_pixels > 0 else 0)
        
        print(f"📈 Overall persistence: {overall_persistence_pct:.1f}% of valid pixels")
        
        return {
            'persistence_map': persistence_map_thresholded,
            'persistence_percentage': persistence_map,
            'class_persistence': class_persistence,
            'valid_mask': valid_mask,
            'overall_persistence_pct': overall_persistence_pct
        }
        
    def _calculate_persistence_statistics(self, 
                                        persistence_results: Dict[str, Any],
                                        loaded_data: Dict[str, Any],
                                        config: PlotConfig) -> Dict[str, Any]:
        """Calculate comprehensive persistence statistics."""
        persistence_map = persistence_results['persistence_map']
        class_persistence = persistence_results['class_persistence']
        valid_mask = persistence_results['valid_mask']
        
        # Basic statistics
        stats = {
            'total_area_pixels': int(np.sum(valid_mask)),
            'persistent_area_pixels': int(np.sum(persistence_map > 0)),
            'persistence_threshold': config.persistence_threshold,
            'min_persistence_years': config.min_persistence_years,
            'class_persistence': class_persistence
        }
        
        # Calculate persistence distribution
        if np.any(persistence_map > 0):
            persistence_values = persistence_map[persistence_map > 0]
            stats.update({
                'mean_persistence': float(np.mean(persistence_values)),
                'std_persistence': float(np.std(persistence_values)),
                'min_persistence': float(np.min(persistence_values)),
                'max_persistence': float(np.max(persistence_values)),
                'median_persistence': float(np.median(persistence_values))
            })
            
            # Persistence categories
            high_persistence = np.sum(persistence_values >= 0.8)
            medium_persistence = np.sum((persistence_values >= 0.6) & (persistence_values < 0.8))
            low_persistence = np.sum(persistence_values < 0.6)
            
            stats['persistence_categories'] = {
                'high_persistence_pixels': int(high_persistence),
                'medium_persistence_pixels': int(medium_persistence), 
                'low_persistence_pixels': int(low_persistence)
            }
        else:
            stats.update({
                'mean_persistence': 0.0,
                'std_persistence': 0.0,
                'min_persistence': 0.0,
                'max_persistence': 0.0,
                'median_persistence': 0.0,
                'persistence_categories': {
                    'high_persistence_pixels': 0,
                    'medium_persistence_pixels': 0,
                    'low_persistence_pixels': 0
                }
            })
            
        return stats
        
    def plot(self, result: AnalysisResult, config: PlotConfig) -> Optional[Path]:
        """
        Create persistence visualization.
        
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
            print("🎨 Creating persistence visualization...")
            
            # Create figure
            fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
            
            # Get persistence map
            persistence_map = result.primary_data
            
            # Setup cartographic elements
            cartographic = CartographicElements()
            
            # Create colormap for persistence
            cmap, norm, labels = cartographic.create_colormap('persistence')
            
            # Display persistence map
            im = ax.imshow(persistence_map, 
                          cmap=cmap, 
                          norm=norm,
                          interpolation=config.interpolation,
                          alpha=config.alpha)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Persistence (%)', rotation=270, labelpad=20)
            
            # Add title
            title = config.title or f"Land Use Persistence ({result.metadata['years'][0]}-{result.metadata['years'][-1]})"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add subtitle with statistics
            subtitle = (f"Threshold: {config.persistence_threshold*100:.0f}% | "
                       f"Persistent Area: {result.statistics['persistent_area_pixels']:,} pixels "
                       f"({result.statistics['persistent_area_pixels']/result.statistics['total_area_pixels']*100:.1f}%)")
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
                
            # Add metadata
            if config.metadata:
                cartographic.add_title_block(fig, title, subtitle, config.metadata)
                
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
            raise AnalysisError(f"Persistence plotting failed: {e}")
            
    def _validate_inputs(self, config: PlotConfig) -> None:
        """Validate inputs specific to persistence analysis."""
        super()._validate_inputs(config)
        
        if config.persistence_threshold <= 0 or config.persistence_threshold > 1:
            raise AnalysisError("persistence_threshold must be between 0 and 1")
            
        if config.min_persistence_years < 1:
            raise AnalysisError("min_persistence_years must be at least 1")
            
        if len(config.images_data) < config.min_persistence_years:
            raise AnalysisError(
                f"Need at least {config.min_persistence_years} years of data "
                f"(got {len(config.images_data)})"
            )
            
    def get_analysis_summary(self, result: AnalysisResult) -> str:
        """Get human-readable analysis summary."""
        stats = result.statistics
        metadata = result.metadata
        
        summary_lines = [
            f"Persistence Analysis Summary",
            f"="*40,
            f"Period: {metadata['years'][0]} - {metadata['years'][-1]} ({metadata['n_years']} years)",
            f"Persistence Threshold: {metadata['threshold']*100:.0f}%",
            f"Minimum Years Required: {metadata['min_years']}",
            f"",
            f"Results:",
            f"  Total Valid Area: {stats['total_area_pixels']:,} pixels",
            f"  Persistent Area: {stats['persistent_area_pixels']:,} pixels",
            f"  Persistence Rate: {stats['persistent_area_pixels']/stats['total_area_pixels']*100:.1f}%",
            f"",
        ]
        
        if 'mean_persistence' in stats:
            summary_lines.extend([
                f"Persistence Statistics:",
                f"  Mean: {stats['mean_persistence']*100:.1f}%",
                f"  Median: {stats['median_persistence']*100:.1f}%", 
                f"  Range: {stats['min_persistence']*100:.1f}% - {stats['max_persistence']*100:.1f}%",
                f"",
            ])
            
        if 'persistence_categories' in stats:
            categories = stats['persistence_categories']
            summary_lines.extend([
                f"Persistence Categories:",
                f"  High (≥80%): {categories['high_persistence_pixels']:,} pixels",
                f"  Medium (60-80%): {categories['medium_persistence_pixels']:,} pixels",
                f"  Low (<60%): {categories['low_persistence_pixels']:,} pixels",
                f"",
            ])
            
        if 'class_persistence' in stats:
            summary_lines.extend([
                f"Class-Specific Persistence:",
            ])
            for class_val, class_stats in stats['class_persistence'].items():
                pct = (class_stats['persistent_pixels'] / class_stats['total_pixels'] * 100 
                      if class_stats['total_pixels'] > 0 else 0)
                summary_lines.append(
                    f"  Class {class_val}: {class_stats['persistent_pixels']:,}/{class_stats['total_pixels']:,} "
                    f"pixels ({pct:.1f}%)"
                )
                
        return '\n'.join(summary_lines)
