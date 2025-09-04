"""
Factory pattern for creating spatial analyzers.

This module implements the Factory pattern for creating appropriate
analyzer instances based on configuration and requirements.
"""

from typing import Dict, Type, Optional, List, Any
from enum import Enum

from ..base import SpatialAnalyzerBase, PlotConfig, AnalysisError
from ..analyzers import (
    PersistenceAnalyzer,
    TrajectoryAnalyzer,
    FrequencyAnalyzer,
    PontiusAnalyzer
)


class AnalyzerType(Enum):
    """Enumeration of available analyzer types."""
    PERSISTENCE = "persistence"
    TRAJECTORY = "trajectory"
    FREQUENCY = "change_frequency"
    PONTIUS = "pontius"
    

class SpatialAnalyzerFactory:
    """
    Factory for creating spatial analyzer instances.
    
    This factory provides a centralized way to create analyzer instances
    with automatic registration and validation capabilities.
    """
    
    def __init__(self):
        """Initialize the factory with registered analyzers."""
        self._analyzers: Dict[str, Type[SpatialAnalyzerBase]] = {}
        self._register_default_analyzers()
        
    def _register_default_analyzers(self) -> None:
        """Register default analyzer implementations."""
        self.register_analyzer(AnalyzerType.PERSISTENCE.value, PersistenceAnalyzer)
        self.register_analyzer(AnalyzerType.TRAJECTORY.value, TrajectoryAnalyzer)
        self.register_analyzer(AnalyzerType.FREQUENCY.value, FrequencyAnalyzer)
        self.register_analyzer(AnalyzerType.PONTIUS.value, PontiusAnalyzer)
        
    def register_analyzer(self, 
                         analyzer_type: str, 
                         analyzer_class: Type[SpatialAnalyzerBase]) -> None:
        """
        Register a new analyzer type.
        
        Parameters
        ----------
        analyzer_type : str
            Unique identifier for the analyzer type
        analyzer_class : Type[SpatialAnalyzerBase]
            Analyzer class that inherits from SpatialAnalyzerBase
        """
        if not issubclass(analyzer_class, SpatialAnalyzerBase):
            raise ValueError(f"Analyzer class must inherit from SpatialAnalyzerBase")
            
        self._analyzers[analyzer_type] = analyzer_class
        print(f"📝 Registered analyzer: {analyzer_type}")
        
    def create_analyzer(self, analyzer_type: str) -> SpatialAnalyzerBase:
        """
        Create an analyzer instance.
        
        Parameters
        ----------
        analyzer_type : str
            Type of analyzer to create
            
        Returns
        -------
        SpatialAnalyzerBase
            Analyzer instance
            
        Raises
        ------
        AnalysisError
            If analyzer type is not registered
        """
        if analyzer_type not in self._analyzers:
            available_types = list(self._analyzers.keys())
            raise AnalysisError(
                f"Unknown analyzer type: {analyzer_type}. "
                f"Available types: {available_types}"
            )
            
        analyzer_class = self._analyzers[analyzer_type]
        return analyzer_class()
        
    def create_from_config(self, config: PlotConfig) -> SpatialAnalyzerBase:
        """
        Create analyzer from configuration.
        
        Parameters
        ----------
        config : PlotConfig
            Configuration containing plot_type
            
        Returns
        -------
        SpatialAnalyzerBase
            Appropriate analyzer instance
        """
        return self.create_analyzer(config.plot_type)
        
    def get_available_types(self) -> List[str]:
        """Get list of available analyzer types."""
        return list(self._analyzers.keys())
        
    def is_registered(self, analyzer_type: str) -> bool:
        """Check if analyzer type is registered."""
        return analyzer_type in self._analyzers
        
    def unregister_analyzer(self, analyzer_type: str) -> bool:
        """
        Unregister an analyzer type.
        
        Parameters
        ----------
        analyzer_type : str
            Type to unregister
            
        Returns
        -------
        bool
            True if successfully unregistered, False if not found
        """
        if analyzer_type in self._analyzers:
            del self._analyzers[analyzer_type]
            print(f"🗑️ Unregistered analyzer: {analyzer_type}")
            return True
        return False
        
    def get_analyzer_info(self, analyzer_type: str) -> Dict[str, str]:
        """
        Get information about a registered analyzer.
        
        Parameters
        ----------
        analyzer_type : str
            Analyzer type
            
        Returns
        -------
        Dict[str, str]
            Analyzer information
        """
        if analyzer_type not in self._analyzers:
            raise AnalysisError(f"Analyzer type not registered: {analyzer_type}")
            
        analyzer_class = self._analyzers[analyzer_type]
        
        return {
            'type': analyzer_type,
            'class_name': analyzer_class.__name__,
            'module': analyzer_class.__module__,
            'docstring': analyzer_class.__doc__ or "No description available"
        }
        
    def validate_config_for_type(self, 
                                config: PlotConfig, 
                                analyzer_type: Optional[str] = None) -> bool:
        """
        Validate configuration for specific analyzer type.
        
        Parameters
        ----------
        config : PlotConfig
            Configuration to validate
        analyzer_type : Optional[str]
            Analyzer type to validate against (uses config.plot_type if None)
            
        Returns
        -------
        bool
            True if valid, raises AnalysisError if invalid
        """
        target_type = analyzer_type or config.plot_type
        
        if not self.is_registered(target_type):
            raise AnalysisError(f"Unknown analyzer type: {target_type}")
            
        # Create temporary analyzer for validation
        analyzer = self.create_analyzer(target_type)
        
        # Use analyzer's validation method
        try:
            analyzer._validate_inputs(config)
            return True
        except Exception as e:
            raise AnalysisError(f"Configuration validation failed: {e}")
            

class AnalyzerRegistry:
    """
    Registry for managing analyzer instances and metadata.
    
    This class provides a global registry for analyzer types with
    additional metadata and discovery capabilities.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._registry: Dict[str, Dict] = {}
        self._factory = SpatialAnalyzerFactory()
        
    def register_analyzer_with_metadata(self, 
                                       analyzer_type: str,
                                       analyzer_class: Type[SpatialAnalyzerBase],
                                       metadata: Optional[Dict] = None) -> None:
        """
        Register analyzer with additional metadata.
        
        Parameters
        ----------
        analyzer_type : str
            Analyzer type identifier
        analyzer_class : Type[SpatialAnalyzerBase]
            Analyzer class
        metadata : Optional[Dict]
            Additional metadata about the analyzer
        """
        # Register with factory
        self._factory.register_analyzer(analyzer_type, analyzer_class)
        
        # Store metadata
        self._registry[analyzer_type] = {
            'class': analyzer_class,
            'metadata': metadata or {},
            'created_instances': 0,
            'last_used': None
        }
        
    def get_analyzer_recommendations(self, 
                                   data_characteristics: Dict[str, Any]) -> List[str]:
        """
        Get analyzer recommendations based on data characteristics.
        
        Parameters
        ----------
        data_characteristics : Dict[str, Any]
            Characteristics of the data (e.g., n_years, data_type, etc.)
            
        Returns
        -------
        List[str]
            Recommended analyzer types in order of preference
        """
        recommendations = []
        n_years = data_characteristics.get('n_years', 0)
        
        # Persistence analysis - good for stability assessment
        if n_years >= 3:
            recommendations.append(AnalyzerType.PERSISTENCE.value)
            
        # Trajectory analysis - good for pattern identification
        if n_years >= 2:
            recommendations.append(AnalyzerType.TRAJECTORY.value)
            
        # Frequency analysis - good for change intensity
        if n_years >= 2:
            recommendations.append(AnalyzerType.FREQUENCY.value)
            
        return recommendations
        
    def create_analyzer(self, analyzer_type: str) -> SpatialAnalyzerBase:
        """Create analyzer and update usage statistics."""
        analyzer = self._factory.create_analyzer(analyzer_type)
        
        # Update statistics
        if analyzer_type in self._registry:
            self._registry[analyzer_type]['created_instances'] += 1
            from datetime import datetime
            self._registry[analyzer_type]['last_used'] = datetime.now()
            
        return analyzer
        
    def get_usage_statistics(self) -> Dict[str, Dict]:
        """Get usage statistics for all registered analyzers."""
        stats = {}
        for analyzer_type, info in self._registry.items():
            stats[analyzer_type] = {
                'instances_created': info['created_instances'],
                'last_used': info['last_used'],
                'class_name': info['class'].__name__
            }
        return stats
        

# Global factory instance
_global_factory = SpatialAnalyzerFactory()

def create_analyzer(analyzer_type: str) -> SpatialAnalyzerBase:
    """
    Convenience function to create analyzer using global factory.
    
    Parameters
    ----------
    analyzer_type : str
        Type of analyzer to create
        
    Returns
    -------
    SpatialAnalyzerBase
        Analyzer instance
    """
    return _global_factory.create_analyzer(analyzer_type)

def create_analyzer_from_config(config: PlotConfig) -> SpatialAnalyzerBase:
    """
    Convenience function to create analyzer from configuration.
    
    Parameters
    ----------
    config : PlotConfig
        Configuration object
        
    Returns
    -------
    SpatialAnalyzerBase
        Analyzer instance
    """
    return _global_factory.create_from_config(config)

def get_available_analyzer_types() -> List[str]:
    """Get list of available analyzer types from global factory."""
    return _global_factory.get_available_types()

def register_custom_analyzer(analyzer_type: str, 
                           analyzer_class: Type[SpatialAnalyzerBase]) -> None:
    """
    Register custom analyzer with global factory.
    
    Parameters
    ----------
    analyzer_type : str
        Unique identifier for the analyzer
    analyzer_class : Type[SpatialAnalyzerBase]
        Analyzer class
    """
    _global_factory.register_analyzer(analyzer_type, analyzer_class)
