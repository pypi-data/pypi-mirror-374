"""
MedDevStats: Statistical analysis tools for medical device FDA 510(k) submissions.

This package provides comprehensive statistical methods for analyzing medical device data
in accordance with FDA CDRH requirements for 510(k) submissions.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.equivalence import (
    equivalence_test,
    equivalence_margin_calculation,
    confidence_interval
)
from .core.agreement import (
    bland_altman_analysis,
    passing_bablok_regression,
    deming_regression,
    lin_concordance_correlation
)
from .core.performance import (
    sensitivity_specificity,
    roc_analysis,
    confusion_matrix_metrics,
    diagnostic_accuracy
)
from .core.validation import (
    method_comparison,
    precision_study,
    linearity_study,
    stability_analysis
)

__all__ = [
    'equivalence_test',
    'equivalence_margin_calculation',
    'confidence_interval',
    'bland_altman_analysis',
    'passing_bablok_regression',
    'deming_regression',
    'lin_concordance_correlation',
    'sensitivity_specificity',
    'roc_analysis',
    'confusion_matrix_metrics',
    'diagnostic_accuracy',
    'method_comparison',
    'precision_study',
    'linearity_study',
    'stability_analysis'
]