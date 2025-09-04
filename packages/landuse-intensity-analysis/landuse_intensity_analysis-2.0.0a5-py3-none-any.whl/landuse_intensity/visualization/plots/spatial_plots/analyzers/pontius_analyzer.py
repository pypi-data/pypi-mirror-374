"""
Pontius analysis for LULC change assessment.

This module implements the Pontius framework for comprehensive land use
change analysis including quantity vs allocation disagreement analysis.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

from ..base import (
    SpatialAnalyzerBase,
    AnalysisResult,
    AnalysisError,
    PlotConfig,
    GeospatialDataManager,
    CartographicElements
)


class PontiusAnalyzer(SpatialAnalyzerBase):
    """
    Specialized analyzer for Pontius et al. change analysis framework.

    This analyzer implements the Pontius methodology for comprehensive
    LULC change assessment, including quantity vs allocation disagreement
    analysis and error matrix visualization.
    """

    def __init__(self):
        """Initialize Pontius analyzer."""
        super().__init__()
        self.analysis_type = "pontius"

    def analyze(self, loaded_data: Dict[str, Any], **kwargs) -> np.ndarray:
        """
        Perform Pontius analysis on contingency data.

        Parameters
        ----------
        loaded_data : Dict[str, Any]
            Loaded and validated data from data manager
        **kwargs
            Additional analysis parameters

        Returns
        -------
        np.ndarray
            Pontius analysis results
        """
        try:
            print("🔬 Starting Pontius analysis...")

            # Extract contingency matrix from loaded data
            contingency_matrix = loaded_data.get('contingency_matrix')
            if contingency_matrix is None:
                raise AnalysisError("Contingency matrix required for Pontius analysis")

            # Perform Pontius calculations
            pontius_results = self._calculate_pontius_metrics(contingency_matrix)

            # Create analysis result array
            # This could be a multi-dimensional array with different metrics
            result_shape = (contingency_matrix.shape[0], contingency_matrix.shape[1], 3)  # quantity, allocation, total
            pontius_array = np.zeros(result_shape, dtype=np.float32)

            # Fill with calculated metrics
            for i in range(contingency_matrix.shape[0]):
                for j in range(contingency_matrix.shape[1]):
                    if i != j:  # Off-diagonal elements (changes)
                        quantity = pontius_results['quantity_disagreement'].get((i, j), 0)
                        allocation = pontius_results['allocation_disagreement'].get((i, j), 0)
                        pontius_array[i, j] = [quantity, allocation, quantity + allocation]

            print("✅ Pontius analysis completed")
            return pontius_array

        except Exception as e:
            raise AnalysisError(f"Pontius analysis failed: {e}")

    def plot(self, analysis_result: np.ndarray, **kwargs) -> Any:
        """
        Create visualization of Pontius analysis results.

        Parameters
        ----------
        analysis_result : np.ndarray
            Result from the analyze method
        **kwargs
            Additional plotting parameters

        Returns
        -------
        Any
            Plot object (matplotlib figure)
        """
        try:
            print("📊 Creating Pontius visualization...")

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

            # Plot 1: Quantity Disagreement
            quantity_data = analysis_result[:, :, 0]
            im1 = ax1.imshow(quantity_data, cmap='Reds', aspect='auto')
            ax1.set_title('Quantity Disagreement', fontweight='bold')
            ax1.set_xlabel('To Class')
            ax1.set_ylabel('From Class')
            plt.colorbar(im1, ax=ax1, shrink=0.8)

            # Plot 2: Allocation Disagreement
            allocation_data = analysis_result[:, :, 1]
            im2 = ax2.imshow(allocation_data, cmap='Blues', aspect='auto')
            ax2.set_title('Allocation Disagreement', fontweight='bold')
            ax2.set_xlabel('To Class')
            ax2.set_ylabel('From Class')
            plt.colorbar(im2, ax=ax2, shrink=0.8)

            # Plot 3: Total Disagreement
            total_data = analysis_result[:, :, 2]
            im3 = ax3.imshow(total_data, cmap='viridis', aspect='auto')
            ax3.set_title('Total Disagreement', fontweight='bold')
            ax3.set_xlabel('To Class')
            ax3.set_ylabel('From Class')
            plt.colorbar(im3, ax=ax3, shrink=0.8)

            # Plot 4: Summary Statistics
            ax4.axis('off')

            # Calculate summary stats
            total_quantity = np.sum(quantity_data)
            total_allocation = np.sum(allocation_data)
            total_disagreement = np.sum(total_data)

            quantity_pct = (total_quantity / total_disagreement * 100) if total_disagreement > 0 else 0
            allocation_pct = (total_allocation / total_disagreement * 100) if total_disagreement > 0 else 0

            stats_text = f"""
Pontius Analysis Summary:

• Quantity Disagreement: {total_quantity:.2f}
• Allocation Disagreement: {total_allocation:.2f}
• Total Disagreement: {total_disagreement:.2f}

• Quantity %: {quantity_pct:.1f}%
• Allocation %: {allocation_pct:.1f}%
"""

            ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
                    fontsize=10, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray"))

            # Overall title
            fig.suptitle('Pontius et al. Change Analysis Framework',
                        fontsize=14, fontweight='bold', y=0.98)

            plt.tight_layout()
            print("✅ Pontius visualization created")
            return fig

        except Exception as e:
            print(f"❌ Error creating Pontius visualization: {e}")
            return None

    def _calculate_pontius_metrics(self, contingency_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Calculate Pontius quantity and allocation disagreement metrics.

        Parameters
        ----------
        contingency_matrix : np.ndarray
            Contingency table with rows as 'from' classes, columns as 'to' classes

        Returns
        -------
        Dict[str, Any]
            Dictionary containing Pontius metrics
        """
        n_classes = contingency_matrix.shape[0]

        # Calculate row and column totals
        row_totals = np.sum(contingency_matrix, axis=1)
        col_totals = np.sum(contingency_matrix, axis=0)
        total_pixels = np.sum(contingency_matrix)

        # Initialize disagreement dictionaries
        quantity_disagreement = {}
        allocation_disagreement = {}

        # Calculate for each class pair
        for i in range(n_classes):
            for j in range(n_classes):
                if i != j:  # Only for changes
                    # Quantity disagreement for this transition
                    quantity = abs(row_totals[i] - col_totals[j]) / 2
                    quantity_disagreement[(i, j)] = quantity

                    # Allocation disagreement (simplified)
                    # In full Pontius method, this involves more complex calculations
                    allocation = contingency_matrix[i, j] - quantity
                    allocation_disagreement[(i, j)] = max(0, allocation)

        return {
            'quantity_disagreement': quantity_disagreement,
            'allocation_disagreement': allocation_disagreement,
            'row_totals': row_totals,
            'col_totals': col_totals,
            'total_pixels': total_pixels
        }
