"""
🧮 Mathematical Utilities for Information Bottleneck
===================================================

Core mathematical functions for information theory and IB calculations.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Union, Optional, Tuple
from scipy.stats import entropy


def safe_log(x: Union[float, np.ndarray], base: float = 2.0, epsilon: float = 1e-12) -> Union[float, np.ndarray]:
    """
    Compute logarithm safely, avoiding log(0)
    
    Args:
        x: Input value(s)
        base: Logarithm base
        epsilon: Small value to add to avoid log(0)
        
    Returns:
        Safe logarithm values
    """
    x_safe = np.maximum(x, epsilon)
    return np.log(x_safe) / np.log(base)


def safe_divide(
    numerator: Union[float, np.ndarray], 
    denominator: Union[float, np.ndarray],
    epsilon: float = 1e-12,
    default: float = 0.0
) -> Union[float, np.ndarray]:
    """
    Perform safe division, avoiding division by zero
    
    Args:
        numerator: Numerator values
        denominator: Denominator values  
        epsilon: Small value to add to denominator
        default: Default value when denominator is zero
        
    Returns:
        Safe division results
    """
    denom_safe = np.where(np.abs(denominator) < epsilon, epsilon, denominator)
    return np.divide(numerator, denom_safe)


def entropy_discrete(
    probabilities: np.ndarray,
    base: float = 2.0,
    normalize: bool = True
) -> float:
    """
    Compute entropy of discrete probability distribution
    
    Args:
        probabilities: Probability values
        base: Logarithm base (2 for bits, e for nats)
        normalize: Whether to normalize probabilities
        
    Returns:
        Entropy value
    """
    if normalize:
        p = probabilities / np.sum(probabilities)
    else:
        p = probabilities
    
    # Use scipy's entropy function which handles edge cases
    return entropy(p, base=base)


def kl_divergence_discrete(
    p: np.ndarray,
    q: np.ndarray,
    base: float = 2.0,
    normalize: bool = True,
    epsilon: float = 1e-12
) -> float:
    """
    Compute Kullback-Leibler divergence between two discrete distributions
    
    Args:
        p: First probability distribution
        q: Second probability distribution
        base: Logarithm base
        normalize: Whether to normalize distributions
        epsilon: Small value to avoid log(0)
        
    Returns:
        KL divergence D_KL(p || q)
    """
    if normalize:
        p = p / np.sum(p)
        q = q / np.sum(q)
    
    # Add epsilon to avoid log(0)
    q_safe = np.maximum(q, epsilon)
    p_safe = np.maximum(p, epsilon)
    
    # Only compute where p > 0
    mask = p_safe > epsilon
    kl = np.sum(p_safe[mask] * safe_log(p_safe[mask] / q_safe[mask], base))
    
    return kl


def compute_mutual_information_discrete(
    joint_distribution: np.ndarray,
    base: float = 2.0
) -> float:
    """
    Compute mutual information from joint probability distribution
    
    Args:
        joint_distribution: Joint probability matrix P(X,Y)
        base: Logarithm base
        
    Returns:
        Mutual information I(X;Y)
    """
    # Normalize to probabilities
    joint_prob = joint_distribution / np.sum(joint_distribution)
    
    # Marginal distributions
    marginal_x = np.sum(joint_prob, axis=1)
    marginal_y = np.sum(joint_prob, axis=0)
    
    # Compute MI using entropy formula: I(X;Y) = H(X) + H(Y) - H(X,Y)
    H_X = entropy_discrete(marginal_x, base=base, normalize=False)
    H_Y = entropy_discrete(marginal_y, base=base, normalize=False)
    H_XY = entropy_discrete(joint_prob.flatten(), base=base, normalize=False)
    
    mi = H_X + H_Y - H_XY
    return max(0.0, mi)  # Ensure non-negative


def compute_mutual_information_ksg(
    X: np.ndarray,
    Y: np.ndarray,
    k: int = 3,
    base: float = 2.0
) -> float:
    """
    Compute mutual information using KSG estimator
    
    Args:
        X: First variable
        Y: Second variable
        k: Number of nearest neighbors
        base: Logarithm base
        
    Returns:
        MI estimate in specified base
    """
    from sklearn.neighbors import NearestNeighbors
    
    # Ensure proper shape
    if len(X.shape) == 1:
        X = X.reshape(-1, 1)
    if len(Y.shape) == 1:
        Y = Y.reshape(-1, 1)
    
    n_samples = X.shape[0]
    
    # Normalize to [0,1]
    X_norm = (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0) + 1e-12)
    Y_norm = (Y - np.min(Y, axis=0)) / (np.max(Y, axis=0) - np.min(Y, axis=0) + 1e-12)
    
    # Joint space
    XY = np.hstack([X_norm, Y_norm])
    
    # Nearest neighbor structures
    nbrs_xy = NearestNeighbors(n_neighbors=k+1, metric='chebyshev').fit(XY)
    nbrs_x = NearestNeighbors(metric='chebyshev').fit(X_norm)
    nbrs_y = NearestNeighbors(metric='chebyshev').fit(Y_norm)
    
    # KSG estimator
    distances, _ = nbrs_xy.kneighbors(XY)
    epsilon = distances[:, -1]
    
    mi_sum = 0.0
    for i in range(n_samples):
        # Count neighbors in marginal spaces
        n_x = len(nbrs_x.radius_neighbors([X_norm[i]], epsilon[i])[1][0]) - 1
        n_y = len(nbrs_y.radius_neighbors([Y_norm[i]], epsilon[i])[1][0]) - 1
        
        # Digamma approximation
        def digamma_approx(x):
            return np.log(max(1, x)) - 1.0/(2*max(1, x)) if x > 0 else 0.0
        
        mi_sum += (digamma_approx(k) - digamma_approx(n_x + 1) - 
                  digamma_approx(n_y + 1) + digamma_approx(n_samples))
    
    mi = mi_sum / n_samples
    
    # Convert to specified base
    if base == 2:
        return max(0.0, mi / np.log(2))
    elif base == np.e:
        return max(0.0, mi)
    else:
        return max(0.0, mi / np.log(base))


def compute_joint_distribution(
    X: np.ndarray,
    Y: np.ndarray,
    x_bins: Optional[np.ndarray] = None,
    y_bins: Optional[np.ndarray] = None,
    n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute joint probability distribution from data
    
    Args:
        X: First variable
        Y: Second variable
        x_bins: Bin edges for X (if None, computed automatically)
        y_bins: Bin edges for Y (if None, computed automatically)
        n_bins: Number of bins if edges not provided
        
    Returns:
        Joint distribution, X bin edges, Y bin edges
    """
    if x_bins is None:
        x_bins = np.linspace(np.min(X), np.max(X), n_bins + 1)
    if y_bins is None:
        y_bins = np.linspace(np.min(Y), np.max(Y), n_bins + 1)
    
    # Create joint histogram
    joint_hist, _, _ = np.histogram2d(X, Y, bins=[x_bins, y_bins])
    
    # Normalize to probabilities
    joint_dist = joint_hist / np.sum(joint_hist)
    
    return joint_dist, x_bins, y_bins


def conditional_entropy(
    X: np.ndarray,
    Y: np.ndarray,
    method: str = 'discrete',
    base: float = 2.0,
    **kwargs
) -> float:
    """
    Compute conditional entropy H(Y|X)
    
    Args:
        X: Conditioning variable
        Y: Target variable
        method: Estimation method
        base: Logarithm base
        **kwargs: Method-specific parameters
        
    Returns:
        Conditional entropy H(Y|X)
    """
    if method == 'discrete':
        # H(Y|X) = H(X,Y) - H(X)
        joint_dist, _, _ = compute_joint_distribution(X, Y, **kwargs)
        
        # Marginal distribution of X
        marginal_x = np.sum(joint_dist, axis=1)
        
        H_XY = entropy_discrete(joint_dist.flatten(), base=base, normalize=False)
        H_X = entropy_discrete(marginal_x, base=base, normalize=False)
        
        return H_XY - H_X
    
    else:
        raise ValueError(f"Unknown method: {method}")


def information_radius(
    distributions: list,
    base: float = 2.0,
    weights: Optional[np.ndarray] = None
) -> float:
    """
    Compute information radius (average divergence from mixture)
    
    Args:
        distributions: List of probability distributions
        base: Logarithm base
        weights: Mixture weights (uniform if None)
        
    Returns:
        Information radius
    """
    n_dists = len(distributions)
    
    if weights is None:
        weights = np.ones(n_dists) / n_dists
    
    # Compute mixture distribution
    mixture = np.zeros_like(distributions[0])
    for i, dist in enumerate(distributions):
        mixture += weights[i] * dist
    
    # Compute average KL divergence to mixture
    info_radius = 0.0
    for i, dist in enumerate(distributions):
        kl_div = kl_divergence_discrete(dist, mixture, base=base, normalize=False)
        info_radius += weights[i] * kl_div
    
    return info_radius


def jensen_shannon_divergence(
    p: np.ndarray,
    q: np.ndarray,
    base: float = 2.0,
    weights: Optional[Tuple[float, float]] = None
) -> float:
    """
    Compute Jensen-Shannon divergence
    
    Args:
        p: First distribution
        q: Second distribution
        base: Logarithm base
        weights: Mixture weights (0.5, 0.5) if None
        
    Returns:
        JS divergence
    """
    if weights is None:
        weights = (0.5, 0.5)
    
    w1, w2 = weights
    
    # Mixture distribution
    m = w1 * p + w2 * q
    
    # JS divergence
    js = w1 * kl_divergence_discrete(p, m, base=base, normalize=False)
    js += w2 * kl_divergence_discrete(q, m, base=base, normalize=False)
    
    return js