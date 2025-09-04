# 🌍 LandUse Intensity Analysis

[![PyPI version](https://badge.fury.io/py/landuse-intensity-analysis.svg)](https://pypi.org/project/landuse-intensity-analysis/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-73.7%25-green.svg)](https://github.com/ils15/LandUse-Intensity-Analysis)

> **Modern Python library for comprehensive land use change analysis using clean architecture principles and the Pontius-Aldwaik intensity analysis methodology**

---

## 🚀 Quick Start

### Installation

```bash
pip install landuse-intensity-analysis
```

### Basic Usage

```python
import landuse_intensity as lui

# Load your raster data
from landuse_intensity.processing import read_raster
data_2000, _ = read_raster("landuse_2000.tiff")
data_2010, _ = read_raster("landuse_2010.tiff")

# Create analyzer
analyzer = lui.AnalyzerFactory.create_analyzer("intensity")

# Perform analysis
results = analyzer.analyze(data_2000, data_2010)

# Generate visualizations
lui.plot_sankey(data_2000, data_2010, save_path="transition_flow.png")
lui.plot_transition_matrix_heatmap(data_2000, data_2010, save_path="matrix.png")
```

---

## 🧩 Package Architecture

The library follows clean architecture principles with modular structure:

### Core Modules

```python
from landuse_intensity import (
    AnalyzerFactory,      # Factory pattern for creating analyzers
    AnalyzerManager,      # Central management of analysis workflows
    # Core analysis functions
    transition_matrix_calculation,
    loss_gain_table,
    interval_level_analysis,
    category_level_analysis,
    transition_level_analysis,
    # Visualization functions
    plot_sankey,
    plot_transition_matrix_heatmap,
    plot_loss_gain_bar,
    plot_comprehensive_analysis,
    # Statistics and utilities
    calculate_statistics,
    export_results
)
```

### Main Components

#### AnalyzerFactory

Creates different types of analyzers based on your needs:

```python
# Create an intensity analyzer
analyzer = AnalyzerFactory.create_analyzer("intensity")

# Create a multi-step analyzer
multi_analyzer = AnalyzerFactory.create_analyzer("multi_step")

# Create a change analyzer
change_analyzer = AnalyzerFactory.create_analyzer("change")
```

#### AnalyzerManager

Manages the complete analysis workflow:

```python
# Initialize manager
manager = AnalyzerManager()

# Add multiple datasets
manager.add_dataset("2000", data_2000)
manager.add_dataset("2010", data_2010)
manager.add_dataset("2020", data_2020)

# Run comprehensive analysis
results = manager.run_analysis(output_dir="./results/")
```

---

## 🔬 Analysis Methods

### Standard Intensity Analysis

```python
# Load your raster data
from landuse_intensity.processing import read_raster

data_2000, profile_2000 = read_raster("landuse_2000.tiff")
data_2010, profile_2010 = read_raster("landuse_2010.tiff")

# Calculate transition matrix
transition_matrix = transition_matrix_calculation(data_2000, data_2010)

# Perform interval-level analysis
interval_results = interval_level_analysis(transition_matrix)

# Perform category-level analysis  
category_results = category_level_analysis(transition_matrix)

# Perform transition-level analysis
transition_results = transition_level_analysis(transition_matrix)
```

### Multi-Period Analysis

```python
# Analyze multiple time periods
datasets = {
    "2000": data_2000,
    "2005": data_2005, 
    "2010": data_2010,
    "2015": data_2015,
    "2020": data_2020
}

manager = AnalyzerManager()
for year, data in datasets.items():
    manager.add_dataset(year, data)

# Run analysis for all periods
results = manager.run_analysis(
    output_dir="./multi_period_results/",
    generate_plots=True,
    export_excel=True
)
```

### Advanced Spatial Analysis

```python
from landuse_intensity.plots.spatial_plots import (
    plot_change_map,
    plot_persistence_map,
    plot_transition_hotspots
)

# Generate spatial change maps
plot_change_map(data_2000, data_2010, save_path="change_map.png")

# Show areas of persistence vs change
plot_persistence_map(data_2000, data_2010, save_path="persistence.png")

# Identify transition hotspots
plot_transition_hotspots(data_2000, data_2010, save_path="hotspots.png")
```

---

## 🎨 Visualization Gallery

### Graph Visualizations

```python
# Sankey diagram for transition flows
plot_sankey(data_t1, data_t2, save_path="flows.png")

# Transition matrix heatmap
plot_transition_matrix_heatmap(data_t1, data_t2, save_path="matrix.png")

# Loss and gain bar chart
plot_loss_gain_bar(loss_gain_data, save_path="losses_gains.png")

# Comprehensive analysis with multiple plots
plot_comprehensive_analysis(data_t1, data_t2, save_directory="./output/")
```

---

## 📦 Output Organization

All analysis outputs are automatically organized into structured directories:

```
analysis_results/
├── plots/
│   ├── sankey_diagrams/
│   ├── heatmaps/
│   ├── bar_charts/
│   └── spatial_maps/
├── tables/
│   ├── transition_matrices/
│   ├── loss_gain_tables/
│   └── intensity_analysis/
├── reports/
│   ├── analysis_summary.html
│   ├── data_validation.pdf
│   └── methodology_notes.txt
└── validation/
    ├── data_quality_checks.json
    └── processing_log.txt
```

---

## 🛠️ Development and PyPI Release

### PyPI Publishing Guide

This package is designed for professional PyPI distribution. See detailed guides:

- **📦 PyPI Deployment**: [docs/deployment/pypi-guide.md](docs/deployment/pypi-guide.md)
- **🔧 Development Setup**: [docs/development/development-guide.md](docs/development/development-guide.md)
- **📊 Data Processing**: [docs/GUIA_PROCESSAMENTO_DADOS.md](docs/GUIA_PROCESSAMENTO_DADOS.md)

### Quick PyPI Release

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install landuse-intensity-analysis
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ils15/LandUse-Intensity-Analysis.git
cd LandUse-Intensity-Analysis

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run code quality checks
black landuse_intensity/
flake8 landuse_intensity/
mypy landuse_intensity/
```

---

## 🧪 Testing and Validation

### Built-in Data Validation

```python
from landuse_intensity.utils import validate_raster_data

# Comprehensive data validation
validation = validate_raster_data([data_2000, data_2010])
print(f"Validation passed: {validation['status']}")
print(f"Issues found: {validation['issues']}")
```

### Example Data for Testing

```python
from landuse_intensity import load_example_data

# Load Rio de Janeiro example data (5 years)
rio_data = load_example_data("rio_de_janeiro")
print(f"Years available: {list(rio_data.keys())}")

# Quick analysis with example data
results = run_comprehensive_analysis(
    data_t1=rio_data["2000"],
    data_t2=rio_data["2004"],
    output_dir="./rio_analysis/"
)
```

---

## 🌍 Real-World Example: Brazilian Cerrado

```python
import landuse_intensity as lui
import numpy as np

# Simulate Brazilian Cerrado data
print("🌍 Cerrado Biome Analysis")

# Simulated data (replace with real data)
cerrado_classes = ['Cerrado', 'Cerradão', 'Campo', 'Agriculture', 'Pasture', 'Silviculture']

# Create simulated rasters
np.random.seed(42)
raster_2000 = np.random.choice([0,1,2,3,4,5], size=(500, 500), p=[0.4, 0.2, 0.2, 0.1, 0.05, 0.05])
raster_2020 = np.random.choice([0,1,2,3,4,5], size=(500, 500), p=[0.3, 0.15, 0.15, 0.2, 0.15, 0.05])

# Analysis
ct_cerrado = lui.ContingencyTable.from_rasters(
    raster_2000, raster_2020,
    labels1=cerrado_classes,
    labels2=cerrado_classes
)

analyzer_cerrado = lui.IntensityAnalyzer(ct_cerrado)
results_cerrado = analyzer_cerrado.full_analysis()

# Report
print("\n📊 REPORT - CERRADO CHANGES (2000-2020)")
print("=" * 50)
print(f"Total analyzed area: {ct_cerrado.total_area:,} hectares")
print(f"Changed area: {ct_cerrado.total_change:,} hectares ({ct_cerrado.total_change/ct_cerrado.total_area*100:.1f}%)")
print(f"Annual change rate: {results_cerrado.interval.annual_change_rate:.2f}%")

print("\n🔄 Main Transitions:")
transitions = ct_cerrado.table.stack()
top_transitions = transitions[transitions > 0].sort_values(ascending=False).head(5)

for (from_class, to_class), area in top_transitions.items():
    if from_class != to_class:
        print(f"  {from_class} → {to_class}: {area:,} hectares")

# Generate visualizations
from landuse_intensity.sankey_visualization import plot_single_step_sankey

plot_single_step_sankey(
    ct_cerrado.table,
    output_dir="cerrado_results",
    filename="cerrado_transitions",
    title="Cerrado Biome Transitions (2000-2020)",
    export_formats=['html', 'png', 'pdf']
)

print("\n✅ Report and visualizations saved in: cerrado_results/")
print("🌐 Interactive file: cerrado_results/cerrado_transitions.html")
```

---

## 🔧 Troubleshooting

### Common Issues

#### Error: "Module not found"

```python
# Verify installation
import landuse_intensity as lui
print("Version:", lui.__version__)

# If not working, reinstall
pip uninstall landuse-intensity-analysis
pip install landuse-intensity-analysis
```

#### Error: "Invalid data"

```python
# Validate data before analysis
from landuse_intensity.utils import validate_raster_data

is_valid, message = validate_raster_data(raster_t1, raster_t2)
if not is_valid:
    print(f"Data error: {message}")
```

#### Performance with Large Rasters

```python
# For very large rasters, process in chunks
from landuse_intensity.utils import process_raster_in_chunks

results = process_raster_in_chunks(
    raster_t1, raster_t2,
    chunk_size=(1000, 1000),
    overlap=50
)
```

---

## 📚 Scientific Background

This library implements the **Pontius-Aldwaik Intensity Analysis** methodology, a rigorous approach for analyzing land use change patterns. The methodology provides three levels of analysis:

1. **Interval Level**: Overall rate of change
2. **Category Level**: Category-specific gain/loss patterns  
3. **Transition Level**: Systematic vs random transitions

### Key Publications

- **Pontius Jr., R.G. & Aldwaik, S.Z. (2012).** "Intensity analysis to unify measurements of size and stationarity of land changes." *Landscape and Urban Planning*, 106(1), 103-114.

- **Aldwaik, S.Z. & Pontius Jr., R.G. (2012).** "Map errors that could account for deviations from a uniform intensity of land change." *Environmental Modelling & Software*, 31, 36-49.

---

## 📚 References

### Methodology

- **Aldwaik, S. Z., & Pontius Jr, R. G. (2012).** Intensity analysis to unify measurements of size and stationarity of land changes by interval, category, and transition. *Landscape and Urban Planning*, 106(1), 103-114.

- **Pontius Jr, R. G., & Millones, M. (2011).** Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing*, 32(15), 4407-4429.

### Implementation

- **Official Documentation**: [Read the Docs](https://landuse-intensity-analysis.readthedocs.io/)
- **GitHub Repository**: [Source Code](https://github.com/ils15/LandUse-Intensity-Analysis)
- **Examples**: `examples/` folder in repository

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎯 Citation

If you use this library in your research, please cite:

```bibtex
@software{landuse_intensity_analysis,
  title = {LandUse Intensity Analysis},
  author = {LandUse Intensity Analysis Contributors},
  url = {https://github.com/ils15/LandUse-Intensity-Analysis},
  version = {2.0.0a3},
  year = {2025}
}
```

---

## 📞 Support

- **Documentation**: [https://landuse-intensity-analysis.readthedocs.io/](https://landuse-intensity-analysis.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/ils15/LandUse-Intensity-Analysis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ils15/LandUse-Intensity-Analysis/discussions)
- **PyPI**: [https://pypi.org/project/landuse-intensity-analysis/](https://pypi.org/project/landuse-intensity-analysis/)

---

## Ready to analyze land use changes? Get started today! 🚀
