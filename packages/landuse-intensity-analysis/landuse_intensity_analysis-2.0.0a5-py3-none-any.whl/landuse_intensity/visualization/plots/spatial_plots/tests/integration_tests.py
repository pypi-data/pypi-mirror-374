"""
Integration tests for the modular spatial analysis framework.

This module contains comprehensive tests to validate the complete
object-oriented architecture and ensure all components work together.
"""

import numpy as np
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the framework components
from landuse_intensity.plots.spatial_plots import (
    # Main functions
    create_spatial_plot,
    analyze_persistence,
    analyze_trajectory,
    analyze_change_frequency,
    
    # Configuration classes
    PlotConfig,
    PlotConfigBuilder,
    ConfigPresets,
    AnalysisResult,
    AnalysisError,
    
    # Base classes
    SpatialAnalyzerBase,
    GeospatialDataManager,
    CartographicElements,
    
    # Analyzer classes
    PersistenceAnalyzer,
    TrajectoryAnalyzer,
    FrequencyAnalyzer,
    
    # Factory classes
    SpatialAnalyzerFactory,
    AnalyzerType,
    create_analyzer,
    get_available_analyzer_types,
    
    # Legacy functions
    create_persistence_plot,
    create_trajectory_plot,
    create_frequency_plot
)


class TestDataGeneration:
    """Test data generation utilities."""
    
    @staticmethod
    def create_test_data(n_years: int = 5, height: int = 20, width: int = 20) -> np.ndarray:
        """Create test data with predictable patterns."""
        np.random.seed(42)  # Ensure reproducibility
        
        data = np.zeros((n_years, height, width), dtype=np.uint8)
        
        # Create zones with different land use patterns
        # Zone 1: Stable forest (class 1)
        data[:, :height//2, :width//2] = 1
        
        # Zone 2: Agricultural area with some changes (class 2 -> 3)
        data[:, :height//2, width//2:] = 2
        data[2:, :height//2, width//2:] = 3  # Change after year 2
        
        # Zone 3: Urban expansion (class 4 -> 5)
        data[:, height//2:, :width//2] = 4
        data[3:, height//2:, :width//2] = 5  # Urban expansion after year 3
        
        # Zone 4: Dynamic area with frequent changes
        for year in range(n_years):
            data[year, height//2:, width//2:] = (year % 3) + 2
        
        return data


class TestConfigurationSystem:
    """Test the configuration system."""
    
    def test_plot_config_builder(self):
        """Test PlotConfigBuilder functionality."""
        config = (PlotConfigBuilder()
                  .plot_type('persistence')
                  .title('Test Plot')
                  .colormap('viridis')
                  .figsize((10, 8))
                  .dpi(150)
                  .output_path('test.png')
                  .add_parameter('threshold', 0.8)
                  .build())
        
        assert config.plot_type == 'persistence'
        assert config.title == 'Test Plot'
        assert config.colormap == 'viridis'
        assert config.figsize == (10, 8)
        assert config.dpi == 150
        assert config.output_path == 'test.png'
        assert config.parameters['threshold'] == 0.8
    
    def test_config_presets(self):
        """Test configuration presets."""
        default_config = ConfigPresets.default()
        assert isinstance(default_config, PlotConfig)
        assert default_config.dpi == 300
        
        hq_config = ConfigPresets.high_quality()
        assert hq_config.dpi == 600
        
        quick_config = ConfigPresets.quick_analysis()
        assert quick_config.dpi == 150


class TestBaseClasses:
    """Test base classes functionality."""
    
    def test_data_manager(self):
        """Test GeospatialDataManager."""
        data = TestDataGeneration.create_test_data()
        manager = GeospatialDataManager()
        
        # Test validation
        validated_data = manager._validate_input_data(data)
        assert validated_data.shape == data.shape
        assert validated_data.dtype in [np.uint8, np.int32, np.float32, np.float64]
        
        # Test statistics
        stats = manager._calculate_basic_statistics(data)
        assert 'n_years' in stats
        assert 'n_classes' in stats
        assert 'spatial_dimensions' in stats
        assert stats['n_years'] == data.shape[0]
    
    def test_cartographic_elements(self):
        """Test CartographicElements."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 6))
        cartographic = CartographicElements()
        
        # Test colormap creation
        cmap = cartographic.create_colormap(['red', 'green', 'blue'])
        assert cmap is not None
        
        # Test theme application
        cartographic.apply_theme(fig, ax, 'publication')
        
        plt.close(fig)


class TestAnalyzers:
    """Test individual analyzer classes."""
    
    def test_persistence_analyzer(self):
        """Test PersistenceAnalyzer."""
        data = TestDataGeneration.create_test_data()
        analyzer = PersistenceAnalyzer()
        
        config = (PlotConfigBuilder()
                  .plot_type('persistence')
                  .add_parameter('persistence_threshold', 0.7)
                  .build())
        
        # Mock plotting to avoid file creation
        with patch('matplotlib.pyplot.savefig'):
            result = analyzer.run_analysis(data, config)
        
        assert isinstance(result, AnalysisResult)
        assert 'overall_persistence' in result.statistics
        assert 'class_persistence' in result.statistics
        assert result.analysis_type == 'persistence'
    
    def test_trajectory_analyzer(self):
        """Test TrajectoryAnalyzer."""
        data = TestDataGeneration.create_test_data()
        analyzer = TrajectoryAnalyzer()
        
        config = (PlotConfigBuilder()
                  .plot_type('trajectory')
                  .add_parameter('trajectory_method', 'sequence')
                  .build())
        
        with patch('matplotlib.pyplot.savefig'):
            result = analyzer.run_analysis(data, config)
        
        assert isinstance(result, AnalysisResult)
        assert 'n_unique_trajectories' in result.statistics
        assert 'trajectory_distribution' in result.statistics
        assert result.analysis_type == 'trajectory'
    
    def test_frequency_analyzer(self):
        """Test FrequencyAnalyzer."""
        data = TestDataGeneration.create_test_data()
        analyzer = FrequencyAnalyzer()
        
        config = PlotConfigBuilder().plot_type('change_frequency').build()
        
        with patch('matplotlib.pyplot.savefig'):
            result = analyzer.run_analysis(data, config)
        
        assert isinstance(result, AnalysisResult)
        assert 'mean_frequency' in result.statistics
        assert 'frequency_distribution' in result.statistics
        assert result.analysis_type == 'change_frequency'


class TestFactoryPattern:
    """Test factory pattern implementation."""
    
    def test_analyzer_factory(self):
        """Test SpatialAnalyzerFactory."""
        factory = SpatialAnalyzerFactory()
        
        # Test available types
        types = factory.get_available_types()
        assert 'persistence' in types
        assert 'trajectory' in types
        assert 'change_frequency' in types
        
        # Test analyzer creation
        persistence_analyzer = factory.create_analyzer('persistence')
        assert isinstance(persistence_analyzer, PersistenceAnalyzer)
        
        trajectory_analyzer = factory.create_analyzer('trajectory')
        assert isinstance(trajectory_analyzer, TrajectoryAnalyzer)
        
        frequency_analyzer = factory.create_analyzer('change_frequency')
        assert isinstance(frequency_analyzer, FrequencyAnalyzer)
        
        # Test invalid type
        with pytest.raises(AnalysisError):
            factory.create_analyzer('invalid_type')
    
    def test_global_factory_functions(self):
        """Test global factory convenience functions."""
        # Test available types
        types = get_available_analyzer_types()
        assert len(types) >= 3
        
        # Test analyzer creation
        analyzer = create_analyzer('persistence')
        assert isinstance(analyzer, PersistenceAnalyzer)


class TestMainAPI:
    """Test main API functions."""
    
    def test_create_spatial_plot(self):
        """Test main create_spatial_plot function."""
        data = TestDataGeneration.create_test_data()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_plot.png')
            
            with patch('matplotlib.pyplot.savefig'):
                result = create_spatial_plot(
                    data=data,
                    plot_type='persistence',
                    output_path=output_path,
                    title='Test Plot'
                )
            
            assert isinstance(result, AnalysisResult)
            assert result.analysis_type == 'persistence'
    
    def test_convenience_functions(self):
        """Test convenience analysis functions."""
        data = TestDataGeneration.create_test_data()
        
        with patch('matplotlib.pyplot.savefig'):
            # Test persistence analysis
            result1 = analyze_persistence(data, threshold=0.8)
            assert result1.analysis_type == 'persistence'
            
            # Test trajectory analysis  
            result2 = analyze_trajectory(data, method='pattern')
            assert result2.analysis_type == 'trajectory'
            
            # Test frequency analysis
            result3 = analyze_change_frequency(data)
            assert result3.analysis_type == 'change_frequency'
    
    def test_legacy_compatibility(self):
        """Test legacy compatibility functions."""
        data = TestDataGeneration.create_test_data()
        
        with patch('matplotlib.pyplot.savefig'):
            # Test legacy functions
            result1 = create_persistence_plot(data, output_path='test1.png')
            assert result1['status'] == 'success'
            assert result1['analysis_type'] == 'persistence'
            
            result2 = create_trajectory_plot(data, output_path='test2.png')
            assert result2['status'] == 'success'
            assert result2['analysis_type'] == 'trajectory'
            
            result3 = create_frequency_plot(data, output_path='test3.png')
            assert result3['status'] == 'success'
            assert result3['analysis_type'] == 'frequency'


class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_invalid_data(self):
        """Test handling of invalid input data."""
        # Test with wrong shape
        invalid_data = np.random.rand(10, 10)  # Missing time dimension
        
        with pytest.raises(AnalysisError):
            create_spatial_plot(invalid_data, 'persistence')
    
    def test_invalid_plot_type(self):
        """Test handling of invalid plot types."""
        data = TestDataGeneration.create_test_data()
        
        with pytest.raises(AnalysisError):
            create_spatial_plot(data, 'invalid_type')
    
    def test_invalid_configuration(self):
        """Test handling of invalid configurations."""
        data = TestDataGeneration.create_test_data()
        
        # Test invalid threshold
        with pytest.raises(AnalysisError):
            analyze_persistence(data, threshold=1.5)  # Threshold > 1.0


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Generate test data
        data = TestDataGeneration.create_test_data(n_years=6, height=30, width=30)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test each analysis type
            analysis_types = ['persistence', 'trajectory', 'change_frequency']
            
            for analysis_type in analysis_types:
                output_path = os.path.join(tmpdir, f'{analysis_type}_test.png')
                
                with patch('matplotlib.pyplot.savefig'):
                    result = create_spatial_plot(
                        data=data,
                        plot_type=analysis_type,
                        output_path=output_path,
                        title=f'Test {analysis_type.title()} Analysis'
                    )
                
                # Validate result
                assert isinstance(result, AnalysisResult)
                assert result.analysis_type == analysis_type
                assert len(result.statistics) > 0
                assert result.metadata['success'] is True
    
    def test_performance_benchmark(self):
        """Test performance with larger dataset."""
        import time
        
        # Create larger dataset
        data = TestDataGeneration.create_test_data(n_years=10, height=100, width=100)
        
        start_time = time.time()
        
        with patch('matplotlib.pyplot.savefig'):
            result = create_spatial_plot(data, 'persistence')
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 10.0, f"Processing took too long: {processing_time:.2f}s"
        assert isinstance(result, AnalysisResult)


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    test_classes = [
        TestDataGeneration,
        TestConfigurationSystem,
        TestBaseClasses,
        TestAnalyzers,
        TestFactoryPattern,
        TestMainAPI,
        TestErrorHandling,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        
        # Get test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                # Create instance and run test
                test_instance = test_class()
                test_method = getattr(test_instance, method_name)
                test_method()
                
                passed_tests += 1
                print(f"  ✅ {method_name}")
                
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
