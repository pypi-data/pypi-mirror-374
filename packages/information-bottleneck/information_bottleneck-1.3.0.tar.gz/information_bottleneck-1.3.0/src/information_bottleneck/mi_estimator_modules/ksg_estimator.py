"""
🧠 KSG Mutual Information Estimators
====================================

Implementation of KSG (Kraskov-Stögbauer-Grassberger) MI estimators.
Includes efficient and legacy versions for different use cases.

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Kraskov, Stögbauer & Grassberger (2004) "Estimating mutual information"
"""

import numpy as np
import time
import logging
import warnings
from typing import Optional
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import cKDTree
from sklearn.neighbors import NearestNeighbors

from .base_estimator import BaseMIEstimator, MIEstimationResult


class KSGMutualInformationEstimator:
    """
    Main KSG Mutual Information estimator with multiple method support.
    
    Implements the KSG algorithm with automatic method selection and
    performance optimization for different dataset characteristics.
    """
    
    def __init__(self, method='auto', k=3, random_state=None):
        """
        Initialize KSG MI estimator.
        
        Args:
            method: Estimation method ('efficient', 'legacy', 'auto')
            k: Number of nearest neighbors for KSG algorithm  
            random_state: Random seed for reproducibility
        """
        self.method = method
        self.k = k
        self.random_state = random_state
        
        # Initialize estimator components
        self.efficient_estimator = EfficientKSGEstimator(k=k)
        self.legacy_estimator = LegacyKSGEstimator(k=k)
        
        # Performance tracking
        self.estimation_history = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """
        Estimate mutual information using KSG method.
        
        Args:
            X: Input data array of shape (n_samples, n_features_x)
            Y: Target data array of shape (n_samples, n_features_y)
            
        Returns:
            MIEstimationResult with MI value and metadata
        """
        start_time = time.time()
        
        # Automatic method selection
        if self.method == 'auto':
            n_samples = X.shape[0]
            if n_samples > 10000:
                selected_method = 'efficient'
                estimator = self.efficient_estimator
            else:
                selected_method = 'legacy'  
                estimator = self.legacy_estimator
        else:
            selected_method = self.method
            estimator = (self.efficient_estimator if self.method == 'efficient' 
                        else self.legacy_estimator)
        
        # Perform estimation
        result = estimator.estimate(X, Y)
        result.method = f"ksg_{selected_method}"
        result.computation_time = time.time() - start_time
        
        # Track performance
        self.estimation_history.append(result)
        
        return result


class EfficientKSGEstimator(BaseMIEstimator):
    """
    Efficient O(n log n) KSG estimator using vectorized operations.
    
    Implements optimizations for large datasets:
    - Tree-based nearest neighbor search
    - Vectorized distance computations  
    - Memory-efficient implementations
    """
    
    def __init__(self, k: int = 3, tree_method: str = 'kd_tree'):
        """
        Initialize efficient KSG estimator.
        
        Args:
            k: Number of nearest neighbors
            tree_method: Tree algorithm ('kd_tree', 'ball_tree')
        """
        self.k = k
        self.tree_method = tree_method
        
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """Estimate MI using efficient KSG algorithm."""
        self._validate_input(X, Y)
        X, Y = self._preprocess_data(X, Y)
        
        n_samples = X.shape[0]
        
        # Combine X and Y for joint space
        XY = np.hstack([X, Y])
        
        # Build efficient nearest neighbor trees
        xy_tree = NearestNeighbors(n_neighbors=self.k + 1, algorithm=self.tree_method)
        xy_tree.fit(XY)
        
        x_tree = NearestNeighbors(algorithm=self.tree_method)
        x_tree.fit(X)
        
        y_tree = NearestNeighbors(algorithm=self.tree_method) 
        y_tree.fit(Y)
        
        # Vectorized KSG computation
        distances, _ = xy_tree.kneighbors(XY)
        epsilon = distances[:, self.k]  # k-th nearest neighbor distance
        
        # Count neighbors within epsilon in marginal spaces
        nx = self._count_neighbors_vectorized(x_tree, X, epsilon)
        ny = self._count_neighbors_vectorized(y_tree, Y, epsilon)
        
        # KSG MI formula: ψ(k) + log(N) - <ψ(nx+1) + ψ(ny+1)>
        mi_estimate = (self._digamma(self.k) + 
                      self._digamma(n_samples) - 
                      np.mean(self._digamma(nx + 1) + self._digamma(ny + 1)))
        
        return MIEstimationResult(
            mi_value=max(0.0, mi_estimate),  # Ensure non-negative
            method="ksg_efficient",
            n_samples=n_samples,
            computation_time=0.0,  # Will be set by parent
            metadata={
                'k': self.k,
                'tree_method': self.tree_method,
                'mean_nx': np.mean(nx),
                'mean_ny': np.mean(ny)
            }
        )
    
    def _count_neighbors_vectorized(self, tree, points, epsilon):
        """Vectorized neighbor counting for efficiency."""
        neighbor_counts = []
        for i, point in enumerate(points):
            # Use radius_neighbors for epsilon-ball queries
            neighbors = tree.radius_neighbors([point], radius=epsilon[i], 
                                            return_distance=False)[0]
            neighbor_counts.append(len(neighbors) - 1)  # Exclude self
        return np.array(neighbor_counts)
    
    def _digamma(self, x):
        """Digamma function approximation for KSG formula."""
        from scipy.special import digamma
        return digamma(x)


class LegacyKSGEstimator(BaseMIEstimator):
    """
    Legacy KSG estimator preserved for backward compatibility.
    
    Uses original O(n²) implementation for research accuracy verification.
    Recommended only for small datasets or validation purposes.
    """
    
    def __init__(self, k: int = 3):
        """Initialize legacy KSG estimator."""
        self.k = k
        
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """Estimate MI using legacy KSG algorithm."""
        self._validate_input(X, Y)
        X, Y = self._preprocess_data(X, Y)
        
        if X.shape[0] > 5000:
            warnings.warn("Legacy KSG estimator is slow for large datasets. "
                         "Consider using EfficientKSGEstimator.")
        
        n_samples = X.shape[0]
        
        # Legacy O(n²) implementation
        mi_sum = 0.0
        
        for i in range(n_samples):
            # Find k-th nearest neighbor in joint space
            joint_distances = self._compute_distances_to_point(
                np.hstack([X, Y]), np.hstack([X[i], Y[i]]))
            joint_distances = np.sort(joint_distances)[1:]  # Exclude self (distance 0)
            epsilon = joint_distances[self.k - 1]
            
            # Count neighbors in marginal spaces
            x_distances = self._compute_distances_to_point(X, X[i])
            y_distances = self._compute_distances_to_point(Y, Y[i])
            
            nx = np.sum(x_distances < epsilon)
            ny = np.sum(y_distances < epsilon)
            
            # Accumulate KSG formula terms
            mi_sum += (self._digamma(nx + 1) + self._digamma(ny + 1))
        
        mi_estimate = (self._digamma(self.k) + 
                      self._digamma(n_samples) - 
                      mi_sum / n_samples)
        
        return MIEstimationResult(
            mi_value=max(0.0, mi_estimate),
            method="ksg_legacy", 
            n_samples=n_samples,
            computation_time=0.0,
            metadata={
                'k': self.k,
                'algorithm': 'legacy_o_n_squared'
            }
        )
    
    def _compute_distances_to_point(self, data, point):
        """Compute distances from all points in data to given point."""
        return np.linalg.norm(data - point.reshape(1, -1), axis=1)
    
    def _digamma(self, x):
        """Digamma function for KSG formula."""
        if x <= 0:
            return float('-inf')
        from scipy.special import digamma
        return digamma(x)