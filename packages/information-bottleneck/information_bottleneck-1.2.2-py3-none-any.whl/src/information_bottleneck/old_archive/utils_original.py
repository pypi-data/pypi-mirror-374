"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Utility Functions - UNIFIED IMPLEMENTATION
===============================================================

This module consolidates all utility functions for the Information Bottleneck
method from the scattered structure into a single, unified location.

Consolidated from:
- ib_modules/utilities.py (18KB - mathematical utilities)
- evaluation_metrics.py (26KB - evaluation functions)
- Various helper functions from other modules

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057
"""

import numpy as np
import scipy.sparse as sp
from scipy.special import digamma, gamma, logsumexp
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy, pearsonr, spearmanr
from scipy.optimize import minimize_scalar
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    adjusted_rand_score, adjusted_mutual_info_score,
    silhouette_score, calinski_harabasz_score
)
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import NearestNeighbors
import warnings
import time
from typing import List, Optional, Dict, Any, Tuple, Union, Callable
from abc import ABC, abstractmethod

# ============================================================================
# MATHEMATICAL UTILITIES - Core Numerical Functions
# ============================================================================

def safe_log(x: np.ndarray, min_val: float = 1e-12) -> np.ndarray:
    """
    Compute logarithm with numerical stability.
    
    Prevents log(0) by clipping values to minimum threshold.
    Essential for information-theoretic computations.
    
    Parameters
    ----------
    x : np.ndarray
        Input values
    min_val : float
        Minimum value to prevent log(0)
        
    Returns
    -------
    np.ndarray
        log(max(x, min_val))
    """
    return np.log(np.maximum(x, min_val))


def safe_divide(numerator: np.ndarray, denominator: np.ndarray, 
                default_val: float = 0.0) -> np.ndarray:
    """
    Safe division with handling of division by zero.
    
    Parameters
    ----------
    numerator : np.ndarray
        Numerator values
    denominator : np.ndarray  
        Denominator values
    default_val : float
        Value to return when denominator is zero
        
    Returns
    -------
    np.ndarray
        Safe division result
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.divide(numerator, denominator)
        result[~np.isfinite(result)] = default_val
    return result


def project_to_simplex(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Project vector onto probability simplex using fast algorithm.
    
    Projects x onto the probability simplex: {p : p ≥ 0, Σp = 1}
    Uses efficient O(n log n) algorithm.
    
    Parameters
    ----------
    x : np.ndarray
        Input vector or matrix
    axis : int
        Axis along which to project
        
    Returns
    -------
    np.ndarray
        Projected vector(s) on probability simplex
        
    References
    ----------
    Duchi et al. (2008). "Efficient Projections onto the l1-Ball 
    for Learning in High Dimensions"
    """
    # Handle different array shapes
    if x.ndim == 1:
        n = len(x)
        if n == 1:
            return np.ones(1)
            
        # Sort in descending order
        u = np.sort(x)[::-1]
        
        # Find threshold
        cumsum = np.cumsum(u)
        rho = np.max(np.where(u > (cumsum - 1) / np.arange(1, n + 1))[0])
        theta = (cumsum[rho] - 1) / (rho + 1)
        
        return np.maximum(x - theta, 0)
    else:
        # Apply along specified axis
        return np.apply_along_axis(
            lambda vec: project_to_simplex(vec), axis, x
        )


def entropy_discrete(p: np.ndarray, base: float = np.e, 
                    axis: int = -1) -> np.ndarray:
    """
    Compute entropy of discrete probability distribution.
    
    H(p) = -Σ p_i log(p_i)
    
    Parameters
    ----------
    p : np.ndarray
        Probability distribution(s)
    base : float
        Logarithm base (e for nats, 2 for bits)
    axis : int
        Axis along which to compute entropy
        
    Returns
    -------
    np.ndarray
        Entropy values
    """
    p_safe = np.maximum(p, 1e-12)  # Avoid log(0)
    log_base = np.log(base)
    return -np.sum(p_safe * np.log(p_safe), axis=axis) / log_base


def kl_divergence_discrete(p: np.ndarray, q: np.ndarray, 
                          base: float = np.e, axis: int = -1) -> np.ndarray:
    """
    Compute KL divergence between discrete distributions.
    
    D_KL(p || q) = Σ p_i log(p_i / q_i)
    
    Parameters
    ----------
    p : np.ndarray
        First distribution
    q : np.ndarray
        Second distribution
    base : float
        Logarithm base
    axis : int
        Axis along which to compute divergence
        
    Returns
    -------
    np.ndarray
        KL divergence values
    """
    p_safe = np.maximum(p, 1e-12)
    q_safe = np.maximum(q, 1e-12)
    log_base = np.log(base)
    
    return np.sum(p_safe * np.log(p_safe / q_safe), axis=axis) / log_base


def js_divergence(p: np.ndarray, q: np.ndarray, 
                  base: float = np.e, axis: int = -1) -> np.ndarray:
    """
    Compute Jensen-Shannon divergence between distributions.
    
    JS(p, q) = 0.5 * D_KL(p || m) + 0.5 * D_KL(q || m)
    where m = 0.5 * (p + q)
    
    Parameters
    ----------
    p, q : np.ndarray
        Probability distributions
    base : float
        Logarithm base
    axis : int
        Axis along which to compute
        
    Returns
    -------
    np.ndarray
        JS divergence values
    """
    m = 0.5 * (p + q)
    return (0.5 * kl_divergence_discrete(p, m, base, axis) + 
            0.5 * kl_divergence_discrete(q, m, base, axis))


# ============================================================================
# DIGAMMA FUNCTION UTILITIES - For Continuous MI Estimation
# ============================================================================

def compute_digamma_approximation(k: int, n_x: int, n_y: int, n_samples: int) -> float:
    """
    Improved digamma approximation for KGS mutual information estimator.
    
    Computes: ψ(k) - ψ(n_x + 1) - ψ(n_y + 1) + ψ(n_samples)
    Uses second-order asymptotic expansion for better accuracy.
    
    Parameters
    ----------
    k : int
        Number of k-th nearest neighbors
    n_x : int  
        Number of neighbors in X-marginal space
    n_y : int
        Number of neighbors in Y-marginal space
    n_samples : int
        Total number of samples
        
    Returns
    -------
    float
        Digamma difference for MI estimation
    """
    def digamma_approx(x: float) -> float:
        """Second-order digamma approximation with recurrence relation."""
        if x <= 0:
            return -np.inf
        elif x < 1:
            # Use recurrence relation: ψ(x+1) = ψ(x) + 1/x
            return digamma_approx(x + 1) - 1.0/x
        else:
            # Second-order approximation for x >= 1
            return np.log(x) - 1.0/(2*x) - 1.0/(12*x*x)
    
    return (digamma_approx(k) - digamma_approx(n_x + 1) - 
            digamma_approx(n_y + 1) + digamma_approx(n_samples))


def compute_digamma_asymptotic(k: int, n_x: int, n_y: int, n_samples: int) -> float:
    """
    High-precision digamma approximation using higher-order terms.
    
    Uses expansion: ψ(x) ≈ log(x) - 1/(2x) - 1/(12x²) + 1/(120x⁴) - 1/(252x⁶)
    
    Parameters
    ----------
    k, n_x, n_y, n_samples : int
        Parameters for digamma computation
        
    Returns
    -------
    float
        High-precision digamma difference
    """
    def digamma_asymptotic(x: float) -> float:
        """Higher-order digamma approximation."""
        if x <= 0:
            return -np.inf
        elif x < 2:
            # Use recurrence relation for small values
            return digamma_asymptotic(x + 1) - 1.0/x
        else:
            # Higher-order approximation
            x2 = x * x
            x4 = x2 * x2
            x6 = x4 * x2
            return (np.log(x) - 1.0/(2*x) - 1.0/(12*x2) + 
                   1.0/(120*x4) - 1.0/(252*x6))
    
    return (digamma_asymptotic(k) - digamma_asymptotic(n_x + 1) - 
            digamma_asymptotic(n_y + 1) + digamma_asymptotic(n_samples))


def benchmark_digamma_methods(test_values: Optional[List[float]] = None) -> Dict[str, Dict[str, float]]:
    """
    Benchmark different digamma approximation methods.
    
    Compares accuracy and speed of various digamma implementations
    against scipy.special.digamma reference.
    
    Parameters
    ----------
    test_values : List[float], optional
        Values to test (default generates test range)
        
    Returns
    -------
    Dict
        Benchmark results with timing and accuracy metrics
    """
    if test_values is None:
        test_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0, 1000.0]
    
    methods = {
        'scipy': digamma,
        'second_order': lambda x: np.log(x) - 1/(2*x) - 1/(12*x*x),
        'higher_order': lambda x: (np.log(x) - 1/(2*x) - 1/(12*x*x) + 
                                  1/(120*x**4) - 1/(252*x**6))
    }
    
    results = {}
    reference = digamma(np.array(test_values))
    
    for name, method in methods.items():
        # Time the method
        start_time = time.time()
        for _ in range(1000):  # Multiple runs for timing
            computed = method(np.array(test_values))
        elapsed = time.time() - start_time
        
        # Compute accuracy
        if name != 'scipy':
            error = np.abs(computed - reference)
            max_error = np.max(error)
            mean_error = np.mean(error)
            rmse = np.sqrt(np.mean(error**2))
        else:
            max_error = mean_error = rmse = 0.0
        
        results[name] = {
            'time_ms': elapsed * 1000,
            'max_error': max_error,
            'mean_error': mean_error,
            'rmse': rmse
        }
    
    return results


# ============================================================================
# MUTUAL INFORMATION UTILITIES
# ============================================================================

def compute_mutual_information_discrete(X: np.ndarray, Y: np.ndarray, 
                                      bins: Union[int, str] = 'auto') -> float:
    """
    Compute mutual information for discrete or discretized variables.
    
    I(X;Y) = Σ p(x,y) log(p(x,y) / (p(x)p(y)))
    
    Parameters
    ----------
    X, Y : np.ndarray
        Input variables
    bins : int or str
        Number of bins for discretization
        
    Returns
    -------
    float
        Mutual information in nats
    """
    if isinstance(bins, str) and bins == 'auto':
        bins = max(int(np.sqrt(len(X))), 2)
    
    # Discretize if continuous
    if X.dtype in [np.float32, np.float64]:
        X_discrete = np.digitize(X, bins=np.linspace(X.min(), X.max(), bins))
    else:
        X_discrete = X
        
    if Y.dtype in [np.float32, np.float64]:
        Y_discrete = np.digitize(Y, bins=np.linspace(Y.min(), Y.max(), bins))
    else:
        Y_discrete = Y
    
    # Compute joint and marginal distributions
    xy_hist, _, _ = np.histogram2d(X_discrete, Y_discrete, bins=bins)
    xy_prob = xy_hist / np.sum(xy_hist)
    
    x_prob = np.sum(xy_prob, axis=1)
    y_prob = np.sum(xy_prob, axis=0)
    
    # Compute MI
    mi = 0.0
    for i in range(len(x_prob)):
        for j in range(len(y_prob)):
            if xy_prob[i, j] > 0:
                mi += xy_prob[i, j] * np.log(xy_prob[i, j] / (x_prob[i] * y_prob[j]))
    
    return max(0.0, mi)


def compute_mutual_information_ksg(X: np.ndarray, Y: np.ndarray, 
                                  k: int = 3) -> float:
    """
    Compute mutual information using Kraskov-Stögbauer-Grassberger estimator.
    
    The KSG estimator is the state-of-the-art method for continuous MI estimation.
    
    Parameters
    ----------
    X : np.ndarray, shape (n_samples, n_features_x)
        First variable
    Y : np.ndarray, shape (n_samples, n_features_y)  
        Second variable
    k : int
        Number of nearest neighbors
        
    Returns
    -------
    float
        Mutual information estimate in nats
    """
    X = np.asarray(X).reshape(len(X), -1)
    Y = np.asarray(Y).reshape(len(Y), -1)
    n_samples = len(X)
    
    if len(X) != len(Y):
        raise ValueError("X and Y must have same number of samples")
    
    # Normalize to unit variance
    X_norm = (X - X.mean(axis=0)) / X.std(axis=0)
    Y_norm = (Y - Y.mean(axis=0)) / Y.std(axis=0)
    
    # Combined space
    XY = np.column_stack([X_norm, Y_norm])
    
    # Find k-th nearest neighbor distances in joint space
    nbrs_xy = NearestNeighbors(n_neighbors=k+1, metric='chebyshev').fit(XY)
    distances_xy, _ = nbrs_xy.kneighbors(XY)
    epsilon = distances_xy[:, -1]  # k-th nearest neighbor distance
    
    # Count neighbors in marginal spaces within epsilon
    nbrs_x = NearestNeighbors(metric='chebyshev').fit(X_norm)
    nbrs_y = NearestNeighbors(metric='chebyshev').fit(Y_norm)
    
    n_x = np.array([len(nbrs_x.radius_neighbors([x], radius=eps)[1]) - 1 
                   for x, eps in zip(X_norm, epsilon)])
    n_y = np.array([len(nbrs_y.radius_neighbors([y], radius=eps)[1]) - 1 
                   for y, eps in zip(Y_norm, epsilon)])
    
    # KSG estimator
    mi = digamma(k) - np.mean(digamma(n_x + 1) + digamma(n_y + 1)) + digamma(n_samples)
    return max(0.0, mi)


def compute_conditional_mutual_information(X: np.ndarray, Y: np.ndarray, 
                                         Z: np.ndarray, method: str = 'discrete') -> float:
    """
    Compute conditional mutual information I(X;Y|Z).
    
    I(X;Y|Z) = H(X|Z) - H(X|Y,Z)
    
    Parameters
    ----------
    X, Y, Z : np.ndarray
        Input variables
    method : str
        Estimation method ('discrete', 'ksg')
        
    Returns
    -------
    float
        Conditional mutual information
    """
    if method == 'discrete':
        # Use discretization
        H_X_Z = compute_conditional_entropy_discrete(X, Z)
        H_X_YZ = compute_conditional_entropy_discrete(X, np.column_stack([Y, Z]))
        return H_X_Z - H_X_YZ
    elif method == 'ksg':
        # Use KSG estimator with conditioning
        I_XYZ = compute_mutual_information_ksg(np.column_stack([X, Y]), Z)
        I_XZ = compute_mutual_information_ksg(X, Z)
        I_YZ = compute_mutual_information_ksg(Y, Z)
        I_Z = entropy_discrete(discretize_data(Z))
        
        # I(X;Y|Z) = I(X;Y;Z) - I(X;Z) - I(Y;Z) + I(Z)
        return I_XYZ - I_XZ - I_YZ + I_Z
    else:
        raise ValueError(f"Unknown method: {method}")


def compute_conditional_entropy_discrete(X: np.ndarray, Y: np.ndarray, 
                                       bins: int = 20) -> float:
    """
    Compute conditional entropy H(X|Y) using discretization.
    
    H(X|Y) = -Σ p(x,y) log p(x|y)
    
    Parameters
    ----------
    X, Y : np.ndarray
        Input variables
    bins : int
        Number of bins for discretization
        
    Returns
    -------
    float
        Conditional entropy in nats
    """
    # Discretize variables
    X_discrete = discretize_data(X, bins=bins)
    Y_discrete = discretize_data(Y, bins=bins)
    
    # Compute joint and marginal distributions
    xy_hist, _, _ = np.histogram2d(X_discrete, Y_discrete, bins=bins)
    xy_prob = xy_hist / np.sum(xy_hist)
    y_prob = np.sum(xy_prob, axis=0)
    
    # Compute conditional entropy
    h_x_given_y = 0.0
    for j in range(len(y_prob)):
        if y_prob[j] > 0:
            # p(x|y_j) for all x
            p_x_given_y = xy_prob[:, j] / y_prob[j]
            p_x_given_y = p_x_given_y[p_x_given_y > 0]  # Remove zeros
            
            # H(X|Y=y_j)
            h_x_given_y_j = -np.sum(p_x_given_y * np.log(p_x_given_y))
            h_x_given_y += y_prob[j] * h_x_given_y_j
    
    return h_x_given_y


def discretize_data(X: np.ndarray, bins: Union[int, str] = 'auto', 
                   method: str = 'uniform') -> np.ndarray:
    """
    Discretize continuous data for information-theoretic computations.
    
    Parameters
    ----------
    X : np.ndarray
        Continuous data to discretize
    bins : int or str
        Number of bins or 'auto'
    method : str
        Discretization method ('uniform', 'quantile', 'kmeans')
        
    Returns
    -------
    np.ndarray
        Discretized data
    """
    if isinstance(bins, str) and bins == 'auto':
        bins = max(int(np.sqrt(len(X))), 2)
    
    X_flat = X.flatten()
    
    if method == 'uniform':
        # Uniform width bins
        return np.digitize(X_flat, bins=np.linspace(X_flat.min(), X_flat.max(), bins))
    elif method == 'quantile':
        # Equal frequency bins
        quantiles = np.linspace(0, 1, bins + 1)
        bin_edges = np.quantile(X_flat, quantiles)
        return np.digitize(X_flat, bins=bin_edges)
    elif method == 'kmeans':
        # K-means based discretization
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=bins, random_state=42, n_init=10)
        return kmeans.fit_predict(X_flat.reshape(-1, 1))
    else:
        raise ValueError(f"Unknown discretization method: {method}")


# ============================================================================
# DATA PREPROCESSING UTILITIES
# ============================================================================

def normalize_data(X: np.ndarray, method: str = 'minmax', 
                  axis: int = 0) -> np.ndarray:
    """
    Normalize data using various methods.
    
    Parameters
    ----------
    X : np.ndarray
        Input data
    method : str
        Normalization method ('minmax', 'zscore', 'robust', 'unit')
    axis : int
        Axis along which to normalize
        
    Returns
    -------
    np.ndarray
        Normalized data
    """
    if method == 'minmax':
        # Min-max normalization to [0, 1]
        X_min = np.min(X, axis=axis, keepdims=True)
        X_max = np.max(X, axis=axis, keepdims=True)
        return (X - X_min) / (X_max - X_min + 1e-8)
    
    elif method == 'zscore':
        # Z-score normalization (standardization)
        X_mean = np.mean(X, axis=axis, keepdims=True)
        X_std = np.std(X, axis=axis, keepdims=True)
        return (X - X_mean) / (X_std + 1e-8)
    
    elif method == 'robust':
        # Robust normalization using median and MAD
        X_median = np.median(X, axis=axis, keepdims=True)
        X_mad = np.median(np.abs(X - X_median), axis=axis, keepdims=True)
        return (X - X_median) / (X_mad + 1e-8)
    
    elif method == 'unit':
        # Unit vector normalization
        X_norm = np.linalg.norm(X, axis=axis, keepdims=True)
        return X / (X_norm + 1e-8)
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def handle_missing_values(X: np.ndarray, method: str = 'remove', 
                         fill_value: Optional[float] = None) -> np.ndarray:
    """
    Handle missing values in data.
    
    Parameters
    ----------
    X : np.ndarray
        Input data with potential NaN values
    method : str
        Handling method ('remove', 'mean', 'median', 'mode', 'constant')
    fill_value : float, optional
        Constant value for 'constant' method
        
    Returns
    -------
    np.ndarray
        Data with handled missing values
    """
    if not np.any(np.isnan(X)):
        return X  # No missing values
    
    if method == 'remove':
        # Remove rows with any NaN
        return X[~np.any(np.isnan(X), axis=1)]
    
    elif method == 'mean':
        # Fill with column means
        col_means = np.nanmean(X, axis=0)
        X_filled = X.copy()
        for j in range(X.shape[1]):
            X_filled[np.isnan(X[:, j]), j] = col_means[j]
        return X_filled
    
    elif method == 'median':
        # Fill with column medians
        col_medians = np.nanmedian(X, axis=0)
        X_filled = X.copy()
        for j in range(X.shape[1]):
            X_filled[np.isnan(X[:, j]), j] = col_medians[j]
        return X_filled
    
    elif method == 'constant':
        # Fill with constant value
        if fill_value is None:
            fill_value = 0.0
        return np.nan_to_num(X, nan=fill_value)
    
    else:
        raise ValueError(f"Unknown missing value method: {method}")


# ============================================================================
# EVALUATION UTILITIES
# ============================================================================

def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                                 average: str = 'weighted') -> Dict[str, float]:
    """
    Compute comprehensive classification metrics.
    
    Parameters
    ----------
    y_true : np.ndarray
        True labels
    y_pred : np.ndarray
        Predicted labels
    average : str
        Averaging method for multi-class metrics
        
    Returns
    -------
    Dict[str, float]
        Classification metrics
    """
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
        'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
        'f1': f1_score(y_true, y_pred, average=average, zero_division=0)
    }


def compute_clustering_metrics(X: np.ndarray, labels_true: np.ndarray, 
                             labels_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute clustering evaluation metrics.
    
    Parameters
    ----------
    X : np.ndarray
        Data points
    labels_true : np.ndarray
        Ground truth cluster labels
    labels_pred : np.ndarray
        Predicted cluster labels
        
    Returns
    -------
    Dict[str, float]
        Clustering metrics
    """
    metrics = {
        'adjusted_rand_index': adjusted_rand_score(labels_true, labels_pred),
        'adjusted_mutual_info': adjusted_mutual_info_score(labels_true, labels_pred)
    }
    
    # Add internal metrics if we have enough clusters
    n_clusters = len(np.unique(labels_pred))
    if n_clusters > 1 and n_clusters < len(labels_pred) - 1:
        try:
            metrics['silhouette_score'] = silhouette_score(X, labels_pred)
            metrics['calinski_harabasz'] = calinski_harabasz_score(X, labels_pred)
        except ValueError:
            # Handle cases where metrics can't be computed
            pass
    
    return metrics


def compute_information_theoretic_metrics(X: np.ndarray, Y: np.ndarray, 
                                        T: np.ndarray) -> Dict[str, float]:
    """
    Compute comprehensive information-theoretic metrics.
    
    Parameters
    ----------
    X : np.ndarray
        Input variable
    Y : np.ndarray
        Target variable
    T : np.ndarray
        Bottleneck representation
        
    Returns
    -------
    Dict[str, float]
        Information-theoretic metrics
    """
    metrics = {}
    
    # Core mutual information measures
    metrics['I_XT'] = compute_mutual_information_discrete(X, T)
    metrics['I_TY'] = compute_mutual_information_discrete(T, Y)
    metrics['I_XY'] = compute_mutual_information_discrete(X, Y)
    
    # Entropies
    metrics['H_X'] = entropy_discrete(discretize_data(X))
    metrics['H_T'] = entropy_discrete(discretize_data(T))
    metrics['H_Y'] = entropy_discrete(discretize_data(Y))
    
    # Derived measures
    metrics['compression_ratio'] = metrics['I_XT'] / metrics['I_XY'] if metrics['I_XY'] > 0 else 0
    metrics['relevance_ratio'] = metrics['I_TY'] / metrics['I_XY'] if metrics['I_XY'] > 0 else 0
    metrics['efficiency'] = metrics['I_TY'] / metrics['I_XT'] if metrics['I_XT'] > 0 else 0
    
    return metrics


def bootstrap_confidence_interval(data: np.ndarray, statistic: Callable,
                                confidence: float = 0.95, 
                                n_bootstrap: int = 1000) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a statistic.
    
    Parameters
    ----------
    data : np.ndarray
        Input data
    statistic : callable
        Function to compute statistic
    confidence : float
        Confidence level
    n_bootstrap : int
        Number of bootstrap samples
        
    Returns
    -------
    Tuple[float, float, float]
        (mean, lower_bound, upper_bound)
    """
    bootstrap_stats = []
    n_samples = len(data)
    
    np.random.seed(42)  # For reproducibility
    
    for _ in range(n_bootstrap):
        # Bootstrap sample
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        bootstrap_sample = data[indices]
        
        # Compute statistic
        stat = statistic(bootstrap_sample)
        bootstrap_stats.append(stat)
    
    bootstrap_stats = np.array(bootstrap_stats)
    
    # Compute confidence interval
    alpha = 1 - confidence
    lower_percentile = 100 * (alpha / 2)
    upper_percentile = 100 * (1 - alpha / 2)
    
    mean_stat = np.mean(bootstrap_stats)
    lower_bound = np.percentile(bootstrap_stats, lower_percentile)
    upper_bound = np.percentile(bootstrap_stats, upper_percentile)
    
    return mean_stat, lower_bound, upper_bound


# ============================================================================
# OPTIMIZATION UTILITIES
# ============================================================================

def check_convergence(history: List[float], tolerance: float = 1e-6, 
                     patience: int = 10, min_improvement: float = 1e-6) -> bool:
    """
    Check convergence based on optimization history.
    
    Parameters
    ----------
    history : List[float]
        Optimization objective history
    tolerance : float
        Convergence tolerance
    patience : int
        Number of iterations without improvement
    min_improvement : float
        Minimum required improvement
        
    Returns
    -------
    bool
        Whether convergence criteria are met
    """
    if len(history) < patience + 1:
        return False
    
    # Check recent changes
    recent_values = history[-patience-1:]
    
    # Check if change is below tolerance
    max_change = max(abs(recent_values[i+1] - recent_values[i]) 
                    for i in range(len(recent_values)-1))
    
    if max_change < tolerance:
        return True
    
    # Check if no improvement for patience iterations
    current_best = max(history)
    recent_best = max(recent_values[:-1])
    
    if current_best - recent_best < min_improvement:
        return True
    
    return False


def adaptive_learning_rate(iteration: int, initial_lr: float = 1e-3,
                          decay_type: str = 'exponential', 
                          decay_rate: float = 0.95, 
                          decay_steps: int = 100) -> float:
    """
    Compute adaptive learning rate schedule.
    
    Parameters
    ----------
    iteration : int
        Current iteration
    initial_lr : float
        Initial learning rate
    decay_type : str
        Decay schedule type
    decay_rate : float
        Decay rate parameter
    decay_steps : int
        Steps between decay
        
    Returns
    -------
    float
        Current learning rate
    """
    if decay_type == 'exponential':
        return initial_lr * (decay_rate ** (iteration // decay_steps))
    elif decay_type == 'polynomial':
        return initial_lr * (1 + iteration / decay_steps) ** (-decay_rate)
    elif decay_type == 'cosine':
        return initial_lr * 0.5 * (1 + np.cos(np.pi * iteration / decay_steps))
    elif decay_type == 'step':
        return initial_lr * (decay_rate ** (iteration // decay_steps))
    else:
        return initial_lr


# ============================================================================
# VALIDATION AND TESTING UTILITIES
# ============================================================================

def validate_ib_inputs(X: np.ndarray, Y: np.ndarray, 
                      n_clusters: int, beta: float) -> None:
    """
    Validate inputs for Information Bottleneck algorithm.
    
    Parameters
    ----------
    X : np.ndarray
        Input data
    Y : np.ndarray
        Target data
    n_clusters : int
        Number of clusters
    beta : float
        Trade-off parameter
        
    Raises
    ------
    ValueError
        If inputs are invalid
    """
    if len(X) != len(Y):
        raise ValueError(f"X and Y must have same length, got {len(X)} and {len(Y)}")
    
    if len(X) == 0:
        raise ValueError("Input arrays cannot be empty")
    
    if n_clusters <= 0:
        raise ValueError(f"n_clusters must be positive, got {n_clusters}")
    
    if n_clusters >= len(X):
        raise ValueError(f"n_clusters ({n_clusters}) must be less than n_samples ({len(X)})")
    
    if beta < 0:
        raise ValueError(f"beta must be non-negative, got {beta}")
    
    if np.any(np.isnan(X)) or np.any(np.isnan(Y)):
        warnings.warn("Input data contains NaN values")
    
    if np.any(np.isinf(X)) or np.any(np.isinf(Y)):
        raise ValueError("Input data contains infinite values")


def create_synthetic_ib_data(n_samples: int = 1000, n_clusters: int = 5,
                            noise_level: float = 0.1, 
                            random_state: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic data for Information Bottleneck testing.
    
    Generates data with known ground-truth clustering structure
    that can be used to validate IB implementations.
    
    Parameters
    ----------
    n_samples : int
        Number of samples to generate
    n_clusters : int
        Number of ground-truth clusters
    noise_level : float
        Amount of noise to add
    random_state : int, optional
        Random seed
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (X, Y) synthetic data
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate cluster centers
    cluster_centers = np.random.randn(n_clusters, 2) * 3
    
    # Assign samples to clusters
    cluster_assignments = np.random.choice(n_clusters, size=n_samples)
    
    # Generate X data around cluster centers
    X = np.zeros(n_samples)
    Y = np.zeros(n_samples, dtype=int)
    
    for i in range(n_samples):
        cluster = cluster_assignments[i]
        # X is distance from cluster center with noise
        X[i] = np.linalg.norm(cluster_centers[cluster]) + np.random.randn() * noise_level
        # Y is related to cluster with some randomness
        Y[i] = cluster if np.random.rand() > noise_level else np.random.choice(n_clusters)
    
    return X, Y


# Global configuration for digamma method selection
_DIGAMMA_METHOD = 'scipy'  # Default to scipy if available

def get_digamma_method() -> str:
    """Get current digamma computation method."""
    return _DIGAMMA_METHOD

def set_global_digamma_method(method: str) -> None:
    """Set global digamma computation method."""
    global _DIGAMMA_METHOD
    valid_methods = ['scipy', 'approximation', 'asymptotic']
    if method not in valid_methods:
        raise ValueError(f"Method must be one of {valid_methods}, got {method}")
    _DIGAMMA_METHOD = method