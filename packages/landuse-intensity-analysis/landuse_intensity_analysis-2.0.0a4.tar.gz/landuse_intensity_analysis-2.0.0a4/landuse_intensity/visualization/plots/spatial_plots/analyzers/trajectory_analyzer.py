"""
Trajectory analysis for multi-year land use change patterns.

This module implements specialized analysis for tracking and visualizing
land use change trajectories across multiple years.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

from ..base import (
    SpatialAnalyzerBase, 
    AnalysisResult, 
    AnalysisError,
    PlotConfig,
    GeospatialDataManager,
    CartographicElements
)


class TrajectoryAnalyzer(SpatialAnalyzerBase):
    """
    Specialized analyzer for land use change trajectory analysis.
    
    This analyzer tracks and analyzes the sequence of land use changes
    for each pixel across multiple years, identifying common patterns
    and transitions.
    """
    
    def __init__(self):
        """Initialize trajectory analyzer."""
        super().__init__()
        self.analysis_type = "trajectory"
        
    def analyze(self, config: PlotConfig) -> AnalysisResult:
        """
        Perform trajectory analysis.
        
        Parameters
        ----------
        config : PlotConfig
            Analysis configuration
            
        Returns
        -------
        AnalysisResult
            Analysis results with trajectory maps and statistics
        """
        try:
            print(f"🔍 Starting trajectory analysis...")
            
            # Load and validate data
            data_manager = GeospatialDataManager()
            loaded_data = data_manager.load_and_validate(config.images_data)
            
            # Calculate trajectories
            trajectory_results = self._calculate_trajectories(
                loaded_data['image_stack'],
                loaded_data['sorted_years'],
                config
            )
            
            # Calculate statistics
            statistics = self._calculate_trajectory_statistics(
                trajectory_results,
                loaded_data,
                config
            )
            
            # Prepare result
            result = AnalysisResult(
                analysis_type=self.analysis_type,
                primary_data=trajectory_results['trajectory_map'],
                secondary_data={
                    'trajectory_sequences': trajectory_results['trajectory_sequences'],
                    'pattern_frequency': trajectory_results['pattern_frequency'],
                    'transition_matrix': trajectory_results['transition_matrix'],
                    'valid_mask': trajectory_results['valid_mask']
                },
                statistics=statistics,
                metadata={
                    'years': loaded_data['sorted_years'],
                    'n_years': len(loaded_data['sorted_years']),
                    'method': config.trajectory_method,
                    'n_patterns': len(trajectory_results['pattern_frequency']),
                    'total_trajectories': statistics['total_trajectories']
                }
            )
            
            print(f"✅ Trajectory analysis completed")
            return result
            
        except Exception as e:
            raise AnalysisError(f"Trajectory analysis failed: {e}")
            
    def _calculate_trajectories(self, 
                              image_stack: np.ndarray,
                              years: List[str],
                              config: PlotConfig) -> Dict[str, Any]:
        """
        Calculate trajectory patterns for each pixel.
        
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
            Trajectory calculation results
        """
        if image_stack.size == 0:
            raise ValueError("Empty image stack provided")
            
        n_years, rows, cols = image_stack.shape
        
        print(f"📊 Calculating trajectories for {n_years} years using '{config.trajectory_method}' method...")
        
        # Get valid pixels (non-zero in all years)
        valid_mask = np.all(image_stack != 0, axis=0)
        
        # Initialize trajectory map
        trajectory_map = np.zeros((rows, cols), dtype=np.int32)
        
        # Store trajectory sequences for analysis
        trajectory_sequences = {}
        
        if config.trajectory_method == 'sequence':
            results = self._calculate_sequence_trajectories(
                image_stack, valid_mask, trajectory_sequences
            )
        elif config.trajectory_method == 'pattern':
            results = self._calculate_pattern_trajectories(
                image_stack, valid_mask, trajectory_sequences
            )
        elif config.trajectory_method == 'frequency':
            results = self._calculate_frequency_trajectories(
                image_stack, valid_mask, trajectory_sequences
            )
        else:
            raise ValueError(f"Unknown trajectory method: {config.trajectory_method}")
            
        trajectory_map = results['trajectory_map']
        trajectory_sequences = results['trajectory_sequences']
        
        # Calculate pattern frequency
        pattern_frequency = self._calculate_pattern_frequency(trajectory_sequences)
        
        # Calculate transition matrix
        transition_matrix = self._calculate_transition_matrix(image_stack, valid_mask)
        
        print(f"📈 Found {len(pattern_frequency)} unique trajectory patterns")
        
        return {
            'trajectory_map': trajectory_map,
            'trajectory_sequences': trajectory_sequences,
            'pattern_frequency': pattern_frequency,
            'transition_matrix': transition_matrix,
            'valid_mask': valid_mask
        }
        
    def _calculate_sequence_trajectories(self, 
                                       image_stack: np.ndarray,
                                       valid_mask: np.ndarray,
                                       trajectory_sequences: Dict) -> Dict[str, Any]:
        """Calculate trajectories based on full temporal sequences."""
        n_years, rows, cols = image_stack.shape
        trajectory_map = np.zeros((rows, cols), dtype=np.int32)
        
        # Convert each pixel's time series to a unique sequence identifier
        sequence_to_id = {}
        current_id = 1
        
        for i in range(rows):
            for j in range(cols):
                if valid_mask[i, j]:
                    # Get time series for this pixel
                    sequence = tuple(image_stack[:, i, j])
                    
                    # Check if sequence already exists
                    if sequence not in sequence_to_id:
                        sequence_to_id[sequence] = current_id
                        trajectory_sequences[current_id] = {
                            'sequence': sequence,
                            'pixels': [(i, j)],
                            'count': 1
                        }
                        current_id += 1
                    else:
                        seq_id = sequence_to_id[sequence]
                        trajectory_sequences[seq_id]['pixels'].append((i, j))
                        trajectory_sequences[seq_id]['count'] += 1
                        
                    # Assign ID to pixel
                    trajectory_map[i, j] = sequence_to_id[sequence]
                    
        return {
            'trajectory_map': trajectory_map,
            'trajectory_sequences': trajectory_sequences
        }
        
    def _calculate_pattern_trajectories(self, 
                                      image_stack: np.ndarray,
                                      valid_mask: np.ndarray,
                                      trajectory_sequences: Dict) -> Dict[str, Any]:
        """Calculate trajectories based on change patterns."""
        n_years, rows, cols = image_stack.shape
        trajectory_map = np.zeros((rows, cols), dtype=np.int32)
        
        # Define pattern types
        patterns = {
            1: 'stable',        # No change
            2: 'single_change', # One change event
            3: 'multiple_change', # Multiple changes
            4: 'cyclic',        # Returns to original
            5: 'degradation',   # Systematic decrease
            6: 'improvement'    # Systematic increase
        }
        
        for i in range(rows):
            for j in range(cols):
                if valid_mask[i, j]:
                    sequence = image_stack[:, i, j]
                    pattern_id = self._classify_pattern(sequence)
                    trajectory_map[i, j] = pattern_id
                    
                    # Store sequence info
                    if pattern_id not in trajectory_sequences:
                        trajectory_sequences[pattern_id] = {
                            'pattern_type': patterns.get(pattern_id, 'unknown'),
                            'pixels': [],
                            'count': 0,
                            'examples': []
                        }
                        
                    trajectory_sequences[pattern_id]['pixels'].append((i, j))
                    trajectory_sequences[pattern_id]['count'] += 1
                    
                    # Store example sequences (up to 10)
                    if len(trajectory_sequences[pattern_id]['examples']) < 10:
                        trajectory_sequences[pattern_id]['examples'].append(tuple(sequence))
                        
        return {
            'trajectory_map': trajectory_map,
            'trajectory_sequences': trajectory_sequences
        }
        
    def _calculate_frequency_trajectories(self, 
                                        image_stack: np.ndarray,
                                        valid_mask: np.ndarray,
                                        trajectory_sequences: Dict) -> Dict[str, Any]:
        """Calculate trajectories based on change frequency."""
        n_years, rows, cols = image_stack.shape
        trajectory_map = np.zeros((rows, cols), dtype=np.int32)
        
        for i in range(rows):
            for j in range(cols):
                if valid_mask[i, j]:
                    sequence = image_stack[:, i, j]
                    
                    # Count number of changes
                    changes = np.sum(sequence[1:] != sequence[:-1])
                    
                    # Assign frequency class (0-5+ changes)
                    freq_class = min(changes, 5) + 1  # 1-6 range
                    trajectory_map[i, j] = freq_class
                    
                    # Store in sequences
                    if freq_class not in trajectory_sequences:
                        trajectory_sequences[freq_class] = {
                            'change_count': changes if changes < 5 else '5+',
                            'pixels': [],
                            'count': 0,
                            'examples': []
                        }
                        
                    trajectory_sequences[freq_class]['pixels'].append((i, j))
                    trajectory_sequences[freq_class]['count'] += 1
                    
                    # Store example sequences
                    if len(trajectory_sequences[freq_class]['examples']) < 10:
                        trajectory_sequences[freq_class]['examples'].append(tuple(sequence))
                        
        return {
            'trajectory_map': trajectory_map,
            'trajectory_sequences': trajectory_sequences
        }
        
    def _classify_pattern(self, sequence: np.ndarray) -> int:
        """Classify a sequence into a pattern type."""
        # Check for stability (no change)
        if np.all(sequence == sequence[0]):
            return 1  # stable
            
        # Count changes
        changes = np.sum(sequence[1:] != sequence[:-1])
        
        # Single change
        if changes == 1:
            return 2  # single_change
            
        # Check for cyclic (returns to original)
        if sequence[0] == sequence[-1] and changes > 1:
            return 4  # cyclic
            
        # Check for systematic change (monotonic)
        if self._is_monotonic(sequence):
            if sequence[-1] > sequence[0]:
                return 6  # improvement
            else:
                return 5  # degradation
                
        # Multiple changes (complex)
        return 3  # multiple_change
        
    def _is_monotonic(self, sequence: np.ndarray) -> bool:
        """Check if sequence is monotonic (always increasing or decreasing)."""
        diff = np.diff(sequence)
        return np.all(diff >= 0) or np.all(diff <= 0)
        
    def _calculate_pattern_frequency(self, 
                                   trajectory_sequences: Dict) -> Dict[int, int]:
        """Calculate frequency of each trajectory pattern."""
        pattern_frequency = {}
        for pattern_id, data in trajectory_sequences.items():
            pattern_frequency[pattern_id] = data['count']
        return pattern_frequency
        
    def _calculate_transition_matrix(self, 
                                   image_stack: np.ndarray,
                                   valid_mask: np.ndarray) -> np.ndarray:
        """Calculate transition matrix between consecutive years."""
        n_years, rows, cols = image_stack.shape
        
        # Get unique classes
        unique_classes = np.unique(image_stack[image_stack != 0])
        n_classes = len(unique_classes)
        
        # Create class mapping
        class_to_idx = {cls: i for i, cls in enumerate(unique_classes)}
        
        # Initialize transition matrix
        transition_matrix = np.zeros((n_classes, n_classes), dtype=np.int32)
        
        # Count transitions
        for t in range(n_years - 1):
            from_year = image_stack[t]
            to_year = image_stack[t + 1]
            
            for i in range(rows):
                for j in range(cols):
                    if valid_mask[i, j]:
                        from_class = from_year[i, j]
                        to_class = to_year[i, j]
                        
                        if from_class != 0 and to_class != 0:
                            from_idx = class_to_idx[from_class]
                            to_idx = class_to_idx[to_class]
                            transition_matrix[from_idx, to_idx] += 1
                            
        return transition_matrix
        
    def _calculate_trajectory_statistics(self, 
                                       trajectory_results: Dict[str, Any],
                                       loaded_data: Dict[str, Any],
                                       config: PlotConfig) -> Dict[str, Any]:
        """Calculate comprehensive trajectory statistics."""
        trajectory_sequences = trajectory_results['trajectory_sequences']
        pattern_frequency = trajectory_results['pattern_frequency']
        valid_mask = trajectory_results['valid_mask']
        
        total_pixels = int(np.sum(valid_mask))
        total_trajectories = len(trajectory_sequences)
        
        # Basic statistics
        stats = {
            'total_pixels': total_pixels,
            'total_trajectories': total_trajectories,
            'pattern_frequency': pattern_frequency,
            'method': config.trajectory_method
        }
        
        # Pattern distribution
        if pattern_frequency:
            sorted_patterns = sorted(pattern_frequency.items(), 
                                   key=lambda x: x[1], reverse=True)
            
            stats['most_common_pattern'] = {
                'pattern_id': sorted_patterns[0][0],
                'frequency': sorted_patterns[0][1],
                'percentage': sorted_patterns[0][1] / total_pixels * 100
            }
            
            stats['pattern_diversity'] = {
                'unique_patterns': total_trajectories,
                'diversity_index': self._calculate_diversity_index(pattern_frequency)
            }
            
        # Trajectory complexity
        if config.trajectory_method == 'frequency':
            complexity_stats = self._calculate_complexity_statistics(trajectory_sequences)
            stats['complexity'] = complexity_stats
            
        return stats
        
    def _calculate_diversity_index(self, pattern_frequency: Dict[int, int]) -> float:
        """Calculate Shannon diversity index for trajectory patterns."""
        total = sum(pattern_frequency.values())
        if total == 0:
            return 0.0
            
        diversity = 0.0
        for count in pattern_frequency.values():
            if count > 0:
                p = count / total
                diversity -= p * np.log(p)
                
        return diversity
        
    def _calculate_complexity_statistics(self, 
                                       trajectory_sequences: Dict) -> Dict[str, Any]:
        """Calculate statistics about trajectory complexity."""
        complexity_stats = {
            'stable_pixels': 0,
            'low_change_pixels': 0,  # 1-2 changes
            'high_change_pixels': 0,  # 3+ changes
            'mean_changes': 0.0
        }
        
        total_pixels = 0
        total_changes = 0
        
        for pattern_id, data in trajectory_sequences.items():
            count = data['count']
            total_pixels += count
            
            if pattern_id == 1:  # No changes
                complexity_stats['stable_pixels'] += count
            elif pattern_id <= 3:  # 1-2 changes
                complexity_stats['low_change_pixels'] += count
                total_changes += count * (pattern_id - 1)
            else:  # 3+ changes
                complexity_stats['high_change_pixels'] += count
                total_changes += count * 3  # Approximate
                
        if total_pixels > 0:
            complexity_stats['mean_changes'] = total_changes / total_pixels
            
        return complexity_stats
        
    def plot(self, result: AnalysisResult, config: PlotConfig) -> Optional[Path]:
        """
        Create trajectory visualization.
        
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
            print("🎨 Creating trajectory visualization...")
            
            # Create figure
            fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
            
            # Get trajectory map
            trajectory_map = result.primary_data
            
            # Setup cartographic elements
            cartographic = CartographicElements()
            
            # Create colormap for trajectories
            n_patterns = result.metadata['n_patterns']
            cmap, norm, labels = cartographic.create_colormap('trajectory')
            
            # Display trajectory map
            im = ax.imshow(trajectory_map, 
                          cmap=cmap, 
                          norm=norm,
                          interpolation=config.interpolation,
                          alpha=config.alpha)
            
            # Add legend if requested
            if config.show_legend and n_patterns <= 10:
                # Create custom labels based on method
                if config.trajectory_method == 'pattern':
                    pattern_labels = ['Stable', 'Single Change', 'Multiple Change', 
                                    'Cyclic', 'Degradation', 'Improvement']
                    labels = pattern_labels[:n_patterns]
                elif config.trajectory_method == 'frequency':
                    labels = [f'{i} Changes' if i < 5 else '5+ Changes' 
                             for i in range(n_patterns)]
                else:
                    labels = [f'Pattern {i}' for i in range(1, n_patterns + 1)]
                    
                cartographic.add_legend(ax, cmap, labels[:n_patterns])
                
            # Add title
            title = config.title or f"Land Use Change Trajectories ({result.metadata['years'][0]}-{result.metadata['years'][-1]})"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add subtitle with statistics
            subtitle = (f"Method: {config.trajectory_method.title()} | "
                       f"Patterns: {n_patterns} | "
                       f"Pixels: {result.statistics['total_pixels']:,}")
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
            raise AnalysisError(f"Trajectory plotting failed: {e}")
            
    def _validate_inputs(self, config: PlotConfig) -> None:
        """Validate inputs specific to trajectory analysis."""
        super()._validate_inputs(config)
        
        valid_methods = ['sequence', 'pattern', 'frequency']
        if config.trajectory_method not in valid_methods:
            raise AnalysisError(f"trajectory_method must be one of {valid_methods}")
            
        if len(config.images_data) < 2:
            raise AnalysisError("Need at least 2 years of data for trajectory analysis")
            
    def get_analysis_summary(self, result: AnalysisResult) -> str:
        """Get human-readable analysis summary."""
        stats = result.statistics
        metadata = result.metadata
        
        summary_lines = [
            f"Trajectory Analysis Summary",
            f"="*40,
            f"Period: {metadata['years'][0]} - {metadata['years'][-1]} ({metadata['n_years']} years)",
            f"Method: {metadata['method'].title()}",
            f"",
            f"Results:",
            f"  Total Pixels: {stats['total_pixels']:,}",
            f"  Unique Patterns: {stats['total_trajectories']}",
            f"",
        ]
        
        if 'most_common_pattern' in stats:
            most_common = stats['most_common_pattern']
            summary_lines.extend([
                f"Most Common Pattern:",
                f"  Pattern ID: {most_common['pattern_id']}",
                f"  Frequency: {most_common['frequency']:,} pixels ({most_common['percentage']:.1f}%)",
                f"",
            ])
            
        if 'pattern_diversity' in stats:
            diversity = stats['pattern_diversity']
            summary_lines.extend([
                f"Pattern Diversity:",
                f"  Unique Patterns: {diversity['unique_patterns']}",
                f"  Diversity Index: {diversity['diversity_index']:.3f}",
                f"",
            ])
            
        if 'complexity' in stats:
            complexity = stats['complexity']
            summary_lines.extend([
                f"Change Complexity:",
                f"  Stable Pixels: {complexity['stable_pixels']:,}",
                f"  Low Change: {complexity['low_change_pixels']:,}",
                f"  High Change: {complexity['high_change_pixels']:,}",
                f"  Mean Changes: {complexity['mean_changes']:.2f}",
            ])
            
        return '\n'.join(summary_lines)
