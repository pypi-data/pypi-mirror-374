"""
Test module for spatial analysis framework.

This module contains comprehensive tests for the object-oriented
spatial analysis framework including unit tests and integration tests.
"""

from .integration_tests import (
    TestDataGeneration,
    TestConfigurationSystem,
    TestBaseClasses,
    TestAnalyzers,
    TestFactoryPattern,
    TestMainAPI,
    TestErrorHandling,
    TestIntegration,
    run_integration_tests
)

__all__ = [
    'TestDataGeneration',
    'TestConfigurationSystem',
    'TestBaseClasses', 
    'TestAnalyzers',
    'TestFactoryPattern',
    'TestMainAPI',
    'TestErrorHandling',
    'TestIntegration',
    'run_integration_tests'
]
