"""
XDT (Exact Decision Tree) - High-performance decision tree classifier

A high-performance decision tree implementation with exact split optimization,
histogram-based candidate selection, and multi-class support.

Key Features:
- Exact split computation with O(n) bucket optimization for integer-like features
- Histogram-based candidate selection for fast training
- Multi-class classification support with Gini impurity
- Numba-accelerated prediction with parallel processing
- Memory-efficient BFS tree layout
- Quantile-based binning for optimal feature discretization

Classes:
    XDTClassifier: Main decision tree classifier

Example:
    >>> from xdt import XDTClassifier
    >>> clf = XDTClassifier(max_depth=10, n_bins=192)
    >>> clf.fit(X_train, y_train)
    >>> predictions = clf.predict(X_test)
    >>> probabilities = clf.predict_proba(X_test)
"""

from .xdt import XDTClassifier

__version__ = "1.0.1"
__author__ = "mohdadil"
__email__ = "mohdadil@live.com"

__all__ = [
    "XDTClassifier",
]

# Algorithm information
ALGORITHM_INFO = {
    "name": "XDT",
    "full_name": "Exact Decision Tree",
    "version": __version__,
    "features": [
        "Exact split computation",
        "Histogram-based candidate selection", 
        "Multi-class classification",
        "Numba acceleration",
        "Parallel prediction",
        "Memory-efficient BFS layout",
        "Quantile-based binning",
        "O(n) bucket optimization"
    ]
}