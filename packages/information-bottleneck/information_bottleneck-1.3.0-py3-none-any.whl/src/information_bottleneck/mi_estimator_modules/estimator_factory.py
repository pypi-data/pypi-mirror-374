"""
🧠 MI Estimator Factory Functions
=================================

Factory functions for easy creation of MI estimator instances.
Provides convenient interfaces for different use cases and data types.

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Multiple MI estimation methods from research literature
"""

from typing import Optional, Union

from .ksg_estimator import KSGMutualInformationEstimator, EfficientKSGEstimator, LegacyKSGEstimator
from .binning_estimator import AdaptiveBinningEstimator, HistogramEstimator


def create_efficient_mi_estimator(data_size: str = 'auto', k: int = 3) -> KSGMutualInformationEstimator:
    """
    Create efficient MI estimator optimized for different data sizes.
    
    Args:
        data_size: 'small' (<1000 samples), 'medium' (1K-10K), 'large' (>10K), or 'auto'
        k: Number of nearest neighbors for KSG algorithm
        
    Returns:
        KSGMutualInformationEstimator configured for optimal performance
    """
    if data_size == 'auto':
        method = 'auto'  # Will auto-select based on sample size
    elif data_size == 'small':
        method = 'legacy'  # More accurate for small datasets
    elif data_size in ['medium', 'large']:
        method = 'efficient'  # Faster for larger datasets
    else:
        raise ValueError(f"Unknown data_size: {data_size}. Use 'small', 'medium', 'large', or 'auto'")
    
    return KSGMutualInformationEstimator(method=method, k=k)


def create_research_mi_estimator(k: int = 3) -> KSGMutualInformationEstimator:
    """
    Create MI estimator configured for research accuracy.
    
    Uses legacy KSG implementation for maximum research fidelity,
    even at the cost of computational efficiency.
    
    Args:
        k: Number of nearest neighbors
        
    Returns:
        KSGMutualInformationEstimator with legacy method
    """
    return KSGMutualInformationEstimator(method='legacy', k=k)


def create_legacy_mi_estimator(k: int = 3) -> LegacyKSGEstimator:
    """
    Create legacy KSG MI estimator for backward compatibility.
    
    Args:
        k: Number of nearest neighbors
        
    Returns:
        LegacyKSGEstimator instance
    """
    return LegacyKSGEstimator(k=k)


def create_fast_mi_estimator(k: int = 3, tree_method: str = 'kd_tree') -> EfficientKSGEstimator:
    """
    Create fast MI estimator optimized for large datasets.
    
    Args:
        k: Number of nearest neighbors
        tree_method: Tree algorithm for neighbor search
        
    Returns:
        EfficientKSGEstimator instance
    """
    return EfficientKSGEstimator(k=k, tree_method=tree_method)


def create_binning_mi_estimator(strategy: str = 'adaptive', 
                               n_bins: Union[int, str] = 'auto') -> Union[AdaptiveBinningEstimator, HistogramEstimator]:
    """
    Create binning-based MI estimator.
    
    Args:
        strategy: 'adaptive' for smart binning or 'simple' for fixed bins
        n_bins: Number of bins (for simple) or binning strategy (for adaptive)
        
    Returns:
        Appropriate binning estimator
    """
    if strategy == 'adaptive':
        binning_strategy = n_bins if isinstance(n_bins, str) else 'freedman_diaconis'
        return AdaptiveBinningEstimator(binning_strategy=binning_strategy)
    elif strategy == 'simple':
        return HistogramEstimator(n_bins=n_bins)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'adaptive' or 'simple'")


def create_discrete_mi_estimator(n_bins: Union[int, str] = 'auto') -> HistogramEstimator:
    """
    Create MI estimator optimized for discrete data.
    
    Args:
        n_bins: Number of bins or 'auto' for automatic selection
        
    Returns:
        HistogramEstimator configured for discrete data
    """
    return HistogramEstimator(n_bins=n_bins)


def create_continuous_mi_estimator(method: str = 'ksg', k: int = 3) -> Union[KSGMutualInformationEstimator, AdaptiveBinningEstimator]:
    """
    Create MI estimator optimized for continuous data.
    
    Args:
        method: 'ksg' for KSG algorithm or 'binning' for adaptive binning
        k: Number of neighbors (for KSG only)
        
    Returns:
        Appropriate continuous data estimator
    """
    if method == 'ksg':
        return KSGMutualInformationEstimator(method='auto', k=k)
    elif method == 'binning':
        return AdaptiveBinningEstimator(binning_strategy='freedman_diaconis')
    else:
        raise ValueError(f"Unknown method: {method}. Use 'ksg' or 'binning'")


def create_robust_mi_estimator(primary_method: str = 'ksg', 
                             fallback_method: str = 'binning') -> KSGMutualInformationEstimator:
    """
    Create robust MI estimator with fallback capability.
    
    Args:
        primary_method: Primary estimation method
        fallback_method: Fallback if primary fails
        
    Returns:
        Robust estimator with error handling
    """
    # For now, return the primary estimator
    # Future enhancement: implement ensemble estimation
    if primary_method == 'ksg':
        return KSGMutualInformationEstimator(method='auto')
    else:
        raise NotImplementedError("Ensemble estimation not yet implemented")


# Convenience aliases for common use cases
def create_default_mi_estimator() -> KSGMutualInformationEstimator:
    """Create default MI estimator with balanced performance/accuracy."""
    return create_efficient_mi_estimator(data_size='auto', k=3)


def create_accurate_mi_estimator() -> KSGMutualInformationEstimator:
    """Create MI estimator optimized for accuracy over speed."""
    return create_research_mi_estimator(k=5)


def create_fast_mi_estimator_alias() -> EfficientKSGEstimator:
    """Create MI estimator optimized for speed over accuracy."""
    return create_fast_mi_estimator(k=3, tree_method='kd_tree')