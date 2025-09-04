# Classe principal modernizada
from .core import ContingencyTable, AnalysisConfiguration, AnalysisResults

# Aliases para compatibilidade  
from .core import MultiStepAnalyzer, IntensityAnalyzer

# Módulos organizados
from . import core
from . import visualization
from . import processing
from . import utils
from . import statistics
from . import io

# Importar funções principais de plotting para facilitar o acesso
from .visualization.plots import plot_sankey
from .visualization.plots import plot_transition_matrix_heatmap, plot_contingency_table
from .visualization.plots import plot_barplot_lulc

# Novos módulos de arquitetura limpa
from .core.base import AnalyzerBase, PlotBase, DataValidator, AreaCalculator
from .visualization.plot_manager import PlotManager, get_plot_manager
from .core.analyzer_factory import AnalyzerFactory, get_analyzer_factory
from .core.analyzer_manager import AnalyzerManager, get_analyzer_manager

# Statistics module
from . import statistics
from .statistics import (
    LandUseStatistics,
    calculate_change_intensity,
    calculate_persistence_rate,
    calculate_net_change,
    get_summary_statistics
)

# Funções de conveniência para análise
from .core.analyzer_manager import analyze_frequency, analyze_persistence, analyze_trajectory, batch_analyze

__version__ = "2.0.0a2"

__all__ = [
    "ContingencyTable",
    "AnalysisConfiguration", 
    "AnalysisResults",
    "MultiStepAnalyzer",
    "IntensityAnalyzer",
    "core",
    "visualization",
    "processing",
    "utils",
    "statistics", 
    "io",
    "__version__",
    # Principais funções de plotting
    "plot_sankey",
    "plot_transition_matrix_heatmap",
    "plot_contingency_table",
    "plot_barplot_lulc",
    # Novos componentes de arquitetura limpa
    "AnalyzerBase",
    "PlotBase", 
    "DataValidator",
    "AreaCalculator",
    "PlotManager",
    "get_plot_manager",
    "AnalyzerFactory",
    "get_analyzer_factory",
    "AnalyzerManager",
    "get_analyzer_manager",
    # Statistics
    "LandUseStatistics",
    "calculate_change_intensity",
    "calculate_persistence_rate",
    "calculate_net_change",
    "get_summary_statistics",
    # Funções de conveniência
    "analyze_frequency",
    "analyze_persistence", 
    "analyze_trajectory",
    "batch_analyze"
]
