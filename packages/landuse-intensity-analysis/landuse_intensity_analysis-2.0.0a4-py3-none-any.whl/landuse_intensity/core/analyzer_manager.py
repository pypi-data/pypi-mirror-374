"""
Analyzer Manager for centralized analyzer operations.

This module implements the Manager pattern to centralize analyzer operations,
providing a unified interface for all analysis types and eliminating duplication.
"""

from typing import Any, Dict, List, Optional, Union, Type
import numpy as np
import pandas as pd
from .base import AnalyzerBase, DataValidator
from .analyzer_factory import AnalyzerFactory


class AnalyzerManager:
    """
    Manager for centralized analyzer operations following the Manager pattern.

    This class provides a unified interface for all analyzer operations,
    eliminating duplication and providing consistent behavior across analysis types.
    """

    def __init__(self):
        self.factory = AnalyzerFactory()
        self.validator = DataValidator()
        self._analysis_history: List[Dict[str, Any]] = []

    def analyze(self, analyzer_type: str, data: Union[np.ndarray, pd.DataFrame],
               config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis using specified analyzer type.

        Args:
            analyzer_type: Type of analyzer to use
            data: Data to analyze
            config: Analysis configuration
            **kwargs: Additional analysis parameters

        Returns:
            Analysis results dictionary

        Raises:
            ValueError: If analysis fails or data is invalid
        """
        try:
            # Validate input data
            if not self.validator.validate_contingency_data(data):
                raise ValueError("Invalid input data")

            # Perform analysis
            results = self.factory.analyze_data(analyzer_type, data, config, **kwargs)

            # Record analysis in history
            self._record_analysis(analyzer_type, config, results)

            return results

        except Exception as e:
            raise ValueError(f"Analysis failed: {str(e)}")

    def batch_analyze(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform multiple analyses in batch.

        Args:
            analyses: List of analysis configurations
                Each config should have 'analyzer_type', 'data', and optional 'config'

        Returns:
            List of analysis results
        """
        results = []
        for analysis_config in analyses:
            try:
                analyzer_type = analysis_config['analyzer_type']
                data = analysis_config['data']
                config = analysis_config.get('config')
                kwargs = analysis_config.get('kwargs', {})

                result = self.analyze(analyzer_type, data, config, **kwargs)
                results.append({
                    'success': True,
                    'analyzer_type': analyzer_type,
                    'result': result
                })

            except Exception as e:
                results.append({
                    'success': False,
                    'analyzer_type': analysis_config.get('analyzer_type'),
                    'error': str(e)
                })

        return results

    def get_available_analyzers(self) -> List[str]:
        """Get list of available analyzer types."""
        return self.factory.get_available_analyzer_types()

    def get_analyzer_info(self, analyzer_type: str) -> Dict[str, Any]:
        """
        Get information about a specific analyzer type.

        Args:
            analyzer_type: Type of analyzer

        Returns:
            Analyzer information dictionary
        """
        try:
            config_template = self.factory.get_analyzer_config_template(analyzer_type)
            return {
                'type': analyzer_type,
                'available': True,
                'config_template': config_template
            }
        except Exception:
            return {
                'type': analyzer_type,
                'available': False,
                'error': 'Analyzer not available'
            }

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of performed analyses."""
        return self._analysis_history.copy()

    def clear_analysis_history(self):
        """Clear the analysis history."""
        self._analysis_history.clear()

    def _record_analysis(self, analyzer_type: str, config: Optional[Dict[str, Any]],
                        results: Dict[str, Any]):
        """Record analysis in history."""
        record = {
            'analyzer_type': analyzer_type,
            'config': config or {},
            'timestamp': pd.Timestamp.now(),
            'results_summary': self._summarize_results(results)
        }
        self._analysis_history.append(record)

        # Keep only last 100 analyses
        if len(self._analysis_history) > 100:
            self._analysis_history.pop(0)

    def _summarize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis results."""
        summary = {}
        for key, value in results.items():
            if isinstance(value, (np.ndarray, pd.DataFrame)):
                summary[key] = f"{type(value).__name__} with shape {value.shape}"
            elif isinstance(value, dict):
                summary[key] = f"Dict with {len(value)} keys"
            else:
                summary[key] = str(type(value).__name__)
        return summary

    def validate_analysis_config(self, analyzer_type: str, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for an analysis.

        Args:
            analyzer_type: Type of analyzer
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        return self.factory.validate_analyzer_config(analyzer_type, config)

    def get_supported_data_types(self, analyzer_type: str) -> List[str]:
        """
        Get supported data types for an analyzer.

        Args:
            analyzer_type: Type of analyzer

        Returns:
            List of supported data type names
        """
        try:
            analyzer = self.factory.create_analyzer(analyzer_type)
            return analyzer.get_supported_data_types()
        except Exception:
            return []


# Global instance for convenience
_analyzer_manager = None

def get_analyzer_manager() -> AnalyzerManager:
    """Get the global analyzer manager instance."""
    global _analyzer_manager
    if _analyzer_manager is None:
        _analyzer_manager = AnalyzerManager()
    return _analyzer_manager


# Convenience functions for backward compatibility
def analyze_frequency(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Dict[str, Any]:
    """Convenience function for frequency analysis."""
    return get_analyzer_manager().analyze('frequency', data, **kwargs)

def analyze_persistence(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Dict[str, Any]:
    """Convenience function for persistence analysis."""
    return get_analyzer_manager().analyze('persistence', data, **kwargs)

def analyze_trajectory(data: Union[np.ndarray, pd.DataFrame], **kwargs) -> Dict[str, Any]:
    """Convenience function for trajectory analysis."""
    return get_analyzer_manager().analyze('trajectory', data, **kwargs)

def batch_analyze(analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function for batch analysis."""
    return get_analyzer_manager().batch_analyze(analyses)
