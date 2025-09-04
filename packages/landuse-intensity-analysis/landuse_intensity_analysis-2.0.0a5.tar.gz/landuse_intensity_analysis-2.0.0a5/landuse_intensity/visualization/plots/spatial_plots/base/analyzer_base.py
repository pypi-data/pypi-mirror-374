"""
Abstract base class for spatial analysis components.

This module implements the Template Method pattern providing a common structure
for all spatial analysis operations while allowing concrete implementations
to customize specific behaviors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import pandas as pd


class AnalysisError(Exception):
    """
    Custom exception for analysis errors.
    
    This exception is raised when errors occur during spatial analysis
    operations that need specific handling.
    """
    pass



@dataclass
class AnalysisResult:
    """Data class to encapsulate analysis results."""
    
    data: np.ndarray
    metadata: Dict[str, Any]
    statistics: Dict[str, Any]
    output_paths: List[str]
    analysis_type: str = "unknown"
    success: bool = True
    error_message: Optional[str] = None


class SpatialAnalyzerBase(ABC):
    """
    Abstract base class for all spatial analysis components.
    
    This class implements the Template Method pattern, defining the skeleton
    of the analysis algorithm while allowing subclasses to override specific
    steps. It provides common functionality for data loading, validation,
    plotting configuration, and output generation.
    
    Attributes
    ----------
    output_dir : Path
        Directory for output files
    title : str
        Title for the analysis
    config : Dict[str, Any]
        Configuration parameters
    data_manager : GeospatialDataManager
        Data management component
    cartographic : CartographicElements
        Cartographic elements component
    """
    
    def __init__(self, 
                 output_dir: str = "outputs/",
                 title: str = "Spatial Analysis",
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the spatial analyzer.
        
        Parameters
        ----------
        output_dir : str
            Directory for output files
        title : str
            Title for the analysis
        config : Dict[str, Any], optional
            Configuration parameters
        """
        self.output_dir = Path(output_dir)
        self.title = title
        self.config = config or {}
        self._data_manager = None
        self._cartographic = None
        self._initialized = False
        
    def set_data_manager(self, data_manager):
        """Set the data manager component (dependency injection)."""
        self._data_manager = data_manager
        
    def set_cartographic(self, cartographic):
        """Set the cartographic elements component (dependency injection)."""
        self._cartographic = cartographic
        
    @property
    def data_manager(self):
        """Get data manager, creating if needed."""
        if self._data_manager is None:
            from .data_manager import GeospatialDataManager
            self._data_manager = GeospatialDataManager()
        return self._data_manager
        
    @property
    def cartographic(self):
        """Get cartographic elements, creating if needed."""
        if self._cartographic is None:
            from .cartographic import CartographicElements
            self._cartographic = CartographicElements()
        return self._cartographic
    
    def run_analysis(self, 
                    images_data: Dict[str, Union[str, np.ndarray]], 
                    **kwargs) -> AnalysisResult:
        """
        Template method that defines the analysis workflow.
        
        This method implements the Template Method pattern, defining the
        overall algorithm structure while delegating specific steps to
        abstract methods that subclasses must implement.
        
        Parameters
        ----------
        images_data : Dict[str, Union[str, np.ndarray]]
            Dictionary with year keys and file paths or arrays as values
        **kwargs
            Additional parameters passed to analysis methods
            
        Returns
        -------
        AnalysisResult
            Complete analysis results including data, metadata, and outputs
        """
        try:
            # Step 1: Initialize (Template Method pattern)
            self._initialize(**kwargs)
            
            # Step 2: Load and validate data (common behavior)
            loaded_data = self._load_and_validate_data(images_data)
            
            # Step 3: Perform analysis (abstract - subclass implementation)
            analysis_result = self.analyze(loaded_data, **kwargs)
            
            # Step 4: Create visualizations (abstract - subclass implementation)
            plot_result = self.plot(analysis_result, **kwargs)
            
            # Step 5: Save outputs (common behavior with customization hooks)
            output_paths = self._save_outputs(analysis_result, plot_result, **kwargs)
            
            # Step 6: Generate final result
            return AnalysisResult(
                data=analysis_result,
                metadata=loaded_data.get('metadata', {}),
                statistics=self._calculate_statistics(analysis_result),
                output_paths=output_paths,
                success=True
            )
            
        except Exception as e:
            return AnalysisResult(
                data=np.array([]),
                metadata={},
                statistics={},
                output_paths=[],
                success=False,
                error_message=str(e)
            )
    
    def _initialize(self, **kwargs):
        """Initialize the analyzer with configuration."""
        if not self._initialized:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.config.update(kwargs)
            self._initialized = True
            
    def _load_and_validate_data(self, 
                               images_data: Dict[str, Union[str, np.ndarray]]) -> Dict[str, Any]:
        """Load and validate input data using data manager."""
        return self.data_manager.load_and_validate(images_data)
        
    def _save_outputs(self, 
                     analysis_result: np.ndarray, 
                     plot_result: Any,
                     **kwargs) -> List[str]:
        """Save analysis outputs with customization hooks."""
        output_paths = []
        
        # Save data outputs
        data_paths = self._save_data_outputs(analysis_result, **kwargs)
        output_paths.extend(data_paths)
        
        # Save plot outputs  
        plot_paths = self._save_plot_outputs(plot_result, **kwargs)
        output_paths.extend(plot_paths)
        
        return output_paths
        
    def _save_data_outputs(self, data: np.ndarray, **kwargs) -> List[str]:
        """Save data outputs (can be overridden by subclasses)."""
        output_paths = []
        
        # Save as GeoTIFF if geospatial metadata available
        if self.config.get('save_geotiff', True):
            geotiff_path = self._save_geotiff(data, **kwargs)
            if geotiff_path:
                output_paths.append(str(geotiff_path))
                
        return output_paths
        
    def _save_plot_outputs(self, plot_result: Any, **kwargs) -> List[str]:
        """Save plot outputs (can be overridden by subclasses)."""
        output_paths = []
        
        if plot_result and self.config.get('save_png', True):
            png_path = self._save_png(plot_result, **kwargs)
            if png_path:
                output_paths.append(str(png_path))
                
        return output_paths
        
    def _save_geotiff(self, data: np.ndarray, **kwargs) -> Optional[Path]:
        """Save data as GeoTIFF using data manager."""
        return self.data_manager.save_geotiff(
            data, 
            self.output_dir / f"{self._get_output_prefix()}.tif",
            **kwargs
        )
        
    def _save_png(self, plot_result: Any, **kwargs) -> Optional[Path]:
        """Save plot as PNG using cartographic elements."""
        return self.cartographic.save_plot(
            plot_result,
            self.output_dir / f"{self._get_output_prefix()}.png",
            **kwargs
        )
        
    def _get_output_prefix(self) -> str:
        """Get output filename prefix (can be overridden)."""
        return self.__class__.__name__.lower().replace('analyzer', '')
        
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, Any]:
        """Calculate basic statistics (can be overridden)."""
        if data.size == 0:
            return {}
            
        return {
            'shape': data.shape,
            'dtype': str(data.dtype),
            'min': float(np.min(data)) if data.size > 0 else None,
            'max': float(np.max(data)) if data.size > 0 else None,
            'mean': float(np.mean(data)) if data.size > 0 else None,
            'std': float(np.std(data)) if data.size > 0 else None,
            'unique_values': len(np.unique(data)) if data.size > 0 else 0
        }
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    def analyze(self, loaded_data: Dict[str, Any], **kwargs) -> np.ndarray:
        """
        Perform the core analysis operation.
        
        This method must be implemented by concrete subclasses to define
        the specific analysis algorithm.
        
        Parameters
        ----------
        loaded_data : Dict[str, Any]
            Loaded and validated data from data manager
        **kwargs
            Additional analysis parameters
            
        Returns
        -------
        np.ndarray
            Analysis result data
        """
        pass
        
    @abstractmethod 
    def plot(self, analysis_result: np.ndarray, **kwargs) -> Any:
        """
        Create visualization of analysis results.
        
        This method must be implemented by concrete subclasses to define
        the specific visualization approach.
        
        Parameters
        ----------
        analysis_result : np.ndarray
            Result from the analyze method
        **kwargs
            Additional plotting parameters
            
        Returns
        -------
        Any
            Plot object (matplotlib figure, etc.)
        """
        pass
        
    # Hook methods that subclasses can optionally override
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate analysis parameters (hook method).
        
        Subclasses can override this to implement custom validation.
        
        Returns
        -------
        bool
            True if parameters are valid, False otherwise
        """
        return True
        
    def pre_analysis_hook(self, loaded_data: Dict[str, Any], **kwargs):
        """
        Hook called before analysis (optional override).
        
        Subclasses can use this for custom pre-processing.
        """
        pass
        
    def post_analysis_hook(self, analysis_result: np.ndarray, **kwargs):
        """
        Hook called after analysis (optional override).
        
        Subclasses can use this for custom post-processing.
        """
        pass
        
    def __str__(self) -> str:
        """String representation of the analyzer."""
        return f"{self.__class__.__name__}(output_dir={self.output_dir}, title='{self.title}')"
        
    def __repr__(self) -> str:
        """Detailed representation of the analyzer."""
        return f"{self.__class__.__name__}(output_dir='{self.output_dir}', title='{self.title}', config={self.config})"
