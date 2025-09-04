"""
🛠️ Utilities for Information Bottleneck
=======================================

Utility functions for data processing, validation, and metrics
for Information Bottleneck algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .data_utils import (
    normalize_data,
    discretize_data,
    create_synthetic_ib_data,
    validate_ib_inputs
)

from .math_utils import (
    safe_log,
    safe_divide,
    entropy_discrete,
    kl_divergence_discrete,
    compute_mutual_information_discrete,
    compute_mutual_information_ksg
)

from .metrics import (
    compute_classification_metrics,
    compute_clustering_metrics,
    compute_information_theoretic_metrics
)

__all__ = [
    # Data utilities
    'normalize_data',
    'discretize_data', 
    'create_synthetic_ib_data',
    'validate_ib_inputs',
    
    # Math utilities
    'safe_log',
    'safe_divide',
    'entropy_discrete',
    'kl_divergence_discrete',
    'compute_mutual_information_discrete',
    'compute_mutual_information_ksg',
    
    # Metrics
    'compute_classification_metrics',
    'compute_clustering_metrics',
    'compute_information_theoretic_metrics'
]