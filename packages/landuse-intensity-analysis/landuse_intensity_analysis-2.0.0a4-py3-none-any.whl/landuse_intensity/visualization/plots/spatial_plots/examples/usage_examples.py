"""
Example usage of the modular spatial analysis framework.

This script demonstrates how to use the new object-oriented architecture
for spatial analysis of land use change data.
"""

import numpy as np
from pathlib import Path

# Import the new modular framework
from landuse_intensity.plots.spatial_plots import (
    # Main functions
    create_spatial_plot,
    analyze_persistence,
    analyze_trajectory,
    analyze_change_frequency,
    
    # Configuration
    PlotConfigBuilder,
    ConfigPresets,
    
    # Factory pattern
    create_analyzer,
    AnalyzerType,
    
    # Legacy compatibility
    create_persistence_plot,
    create_trajectory_plot,
    create_frequency_plot
)


def generate_sample_data(n_years: int = 5, height: int = 100, width: int = 100) -> np.ndarray:
    """Generate sample land use data for testing."""
    np.random.seed(42)
    
    # Create base land use classes
    data = np.zeros((n_years, height, width), dtype=np.uint8)
    
    # Initialize with random land use classes (1-5)
    data[0] = np.random.randint(1, 6, size=(height, width))
    
    # Simulate land use changes over time
    for year in range(1, n_years):
        # Copy previous year
        data[year] = data[year-1].copy()
        
        # Add some random changes (simulate 5% change per year)
        n_changes = int(0.05 * height * width)
        change_indices = np.random.choice(height * width, n_changes, replace=False)
        
        for idx in change_indices:
            i, j = divmod(idx, width)
            # Change to a different random class
            current_class = data[year, i, j]
            new_class = np.random.choice([x for x in range(1, 6) if x != current_class])
            data[year, i, j] = new_class
    
    return data


def example_basic_usage():
    """Demonstrate basic usage of the modular framework."""
    print("🚀 Basic Usage Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=6, height=50, width=50)
    print(f"📊 Generated sample data: {data.shape}")
    
    # Example 1: Simple persistence analysis
    print("\n1️⃣ Persistence Analysis")
    result = create_spatial_plot(
        data=data,
        plot_type='persistence',
        output_path='example_persistence.png',
        title='Land Use Persistence Example'
    )
    print(f"✅ Persistence analysis completed")
    print(f"📈 Persistence statistics: {result.statistics['overall_persistence']:.3f}")
    
    # Example 2: Trajectory analysis
    print("\n2️⃣ Trajectory Analysis")
    result = create_spatial_plot(
        data=data,
        plot_type='trajectory',
        output_path='example_trajectory.png',
        title='Land Use Trajectory Example'
    )
    print(f"✅ Trajectory analysis completed")
    print(f"📈 Unique trajectories: {result.statistics['n_unique_trajectories']}")
    
    # Example 3: Change frequency analysis
    print("\n3️⃣ Change Frequency Analysis")
    result = create_spatial_plot(
        data=data,
        plot_type='change_frequency',
        output_path='example_frequency.png',
        title='Land Use Change Frequency Example'
    )
    print(f"✅ Frequency analysis completed")
    print(f"📈 Mean change frequency: {result.statistics['mean_frequency']:.3f}")


def example_advanced_configuration():
    """Demonstrate advanced configuration using PlotConfigBuilder."""
    print("\n🔧 Advanced Configuration Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=4, height=30, width=30)
    
    # Create custom configuration using builder pattern
    config = (PlotConfigBuilder()
              .plot_type('persistence')
              .title('Custom Persistence Analysis')
              .colormap('viridis')
              .figsize((10, 6))
              .dpi(150)
              .output_path('custom_persistence.png')
              .add_parameter('persistence_threshold', 0.8)
              .add_parameter('show_statistics', True)
              .build())
    
    print(f"📋 Created custom configuration:")
    print(f"   - Plot type: {config.plot_type}")
    print(f"   - Title: {config.title}")
    print(f"   - Colormap: {config.colormap}")
    print(f"   - Threshold: {config.parameters['persistence_threshold']}")
    
    # Run analysis with custom configuration
    result = create_spatial_plot(data, config.plot_type, config=config)
    print(f"✅ Custom analysis completed")


def example_factory_pattern():
    """Demonstrate using the factory pattern directly."""
    print("\n🏭 Factory Pattern Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=5, height=40, width=40)
    
    # Create analyzer using factory
    analyzer = create_analyzer(AnalyzerType.TRAJECTORY.value)
    print(f"🔧 Created analyzer: {analyzer.__class__.__name__}")
    
    # Create configuration
    config = (PlotConfigBuilder()
              .plot_type('trajectory')
              .title('Factory Pattern Example')
              .output_path('factory_trajectory.png')
              .add_parameter('trajectory_method', 'pattern')
              .build())
    
    # Run analysis
    result = analyzer.run_analysis(data, config)
    print(f"✅ Factory analysis completed")
    print(f"📈 Result type: {type(result).__name__}")


def example_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n⚡ Convenience Functions Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=4, height=35, width=35)
    
    # Using convenience functions
    print("1️⃣ Using analyze_persistence()")
    result1 = analyze_persistence(
        data=data,
        output_path='convenience_persistence.png',
        threshold=0.75
    )
    print(f"✅ Persistence: {result1.statistics['overall_persistence']:.3f}")
    
    print("\n2️⃣ Using analyze_trajectory()")
    result2 = analyze_trajectory(
        data=data,
        output_path='convenience_trajectory.png',
        method='frequency'
    )
    print(f"✅ Trajectories: {result2.statistics['n_unique_trajectories']}")
    
    print("\n3️⃣ Using analyze_change_frequency()")
    result3 = analyze_change_frequency(
        data=data,
        output_path='convenience_frequency.png'
    )
    print(f"✅ Mean frequency: {result3.statistics['mean_frequency']:.3f}")


def example_legacy_compatibility():
    """Demonstrate legacy compatibility functions."""
    print("\n🔄 Legacy Compatibility Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=5, height=25, width=25)
    
    # Using legacy functions (same API as before)
    print("1️⃣ Legacy persistence plot")
    result1 = create_persistence_plot(
        data=data,
        output_path="legacy_persistence.png",
        threshold=0.7,
        colormap="RdYlGn"
    )
    print(f"✅ Status: {result1['status']}")
    
    print("\n2️⃣ Legacy trajectory plot")
    result2 = create_trajectory_plot(
        data=data,
        output_path="legacy_trajectory.png",
        method="sequence",
        colormap="tab20"
    )
    print(f"✅ Status: {result2['status']}")
    
    print("\n3️⃣ Legacy frequency plot")
    result3 = create_frequency_plot(
        data=data,
        output_path="legacy_frequency.png",
        colormap="RdYlBu"
    )
    print(f"✅ Status: {result3['status']}")


def example_preset_configurations():
    """Demonstrate preset configurations."""
    print("\n🎨 Preset Configurations Example")
    print("=" * 50)
    
    # Generate sample data
    data = generate_sample_data(n_years=6, height=45, width=45)
    
    # Use preset configurations
    presets = ['default', 'high_quality', 'quick_analysis']
    
    for preset_name in presets:
        print(f"\n🎯 Using {preset_name} preset")
        
        try:
            # Get preset configuration
            preset_config = getattr(ConfigPresets, preset_name)()
            preset_config.plot_type = 'persistence'
            preset_config.output_path = f'preset_{preset_name}_persistence.png'
            preset_config.title = f'Persistence - {preset_name} preset'
            
            result = create_spatial_plot(data, 'persistence', config=preset_config)
            print(f"✅ {preset_name} preset completed")
            
        except AttributeError:
            print(f"❌ Preset {preset_name} not available")


def main():
    """Run all examples."""
    print("🌍 Spatial Analysis Framework - Usage Examples")
    print("=" * 60)
    
    try:
        # Run all examples
        example_basic_usage()
        example_advanced_configuration()
        example_factory_pattern()
        example_convenience_functions()
        example_legacy_compatibility()
        example_preset_configurations()
        
        print("\n🎉 All examples completed successfully!")
        print("📁 Check the generated files in the current directory")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
