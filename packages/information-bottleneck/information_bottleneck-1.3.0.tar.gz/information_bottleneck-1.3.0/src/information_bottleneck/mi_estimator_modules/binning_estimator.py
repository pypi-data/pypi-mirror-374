"""
🧠 Binning-Based MI Estimators  
==============================

Implementation of binning-based mutual information estimators.
Includes adaptive and histogram-based methods for different data types.

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Darbellay & Vajda (1999) "Estimation of the information by adaptive partitioning"
"""

import numpy as np
from typing import Union, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from .base_estimator import BaseMIEstimator, MIEstimationResult


class AdaptiveBinningEstimator(BaseMIEstimator):
    """
    Adaptive binning MI estimator with optimal bin selection.
    
    Implements Freedman-Diaconis rule and other adaptive strategies
    for optimal bin width selection in mutual information estimation.
    """
    
    def __init__(self, binning_strategy: str = 'freedman_diaconis', 
                 max_bins: int = 100, normalize_data: bool = True):
        """
        Initialize adaptive binning estimator.
        
        Args:
            binning_strategy: Method for bin selection ('freedman_diaconis', 'scott', 'sturges')
            max_bins: Maximum number of bins per dimension
            normalize_data: Whether to standardize data before binning
        """
        self.binning_strategy = binning_strategy
        self.max_bins = max_bins
        self.normalize_data = normalize_data
        
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """Estimate MI using adaptive binning method."""
        self._validate_input(X, Y)
        X, Y = self._preprocess_data(X, Y)
        
        # Normalize data if requested
        if self.normalize_data:
            X = self._standardize_data(X)
            Y = self._standardize_data(Y)
        
        # Determine optimal bin counts
        n_bins_x = self._compute_optimal_bins(X)
        n_bins_y = self._compute_optimal_bins(Y) 
        
        # Create bins and compute joint/marginal histograms
        joint_hist, x_edges, y_edges = self._compute_joint_histogram(X, Y, n_bins_x, n_bins_y)
        
        # Compute marginal histograms
        x_hist = np.sum(joint_hist, axis=1)
        y_hist = np.sum(joint_hist, axis=0)
        
        # Calculate MI from histograms
        mi_estimate = self._compute_mi_from_histograms(joint_hist, x_hist, y_hist)
        
        return MIEstimationResult(
            mi_value=mi_estimate,
            method="adaptive_binning",
            n_samples=X.shape[0],
            computation_time=0.0,
            metadata={
                'n_bins_x': n_bins_x,
                'n_bins_y': n_bins_y,
                'binning_strategy': self.binning_strategy,
                'data_normalized': self.normalize_data
            }
        )
    
    def _compute_optimal_bins(self, data: np.ndarray) -> int:
        """Compute optimal number of bins using selected strategy."""
        n_samples = data.shape[0]
        
        if self.binning_strategy == 'freedman_diaconis':
            # Freedman-Diaconis rule: bin_width = 2 * IQR * n^(-1/3)
            q75, q25 = np.percentile(data, [75, 25], axis=0)
            iqr = np.mean(q75 - q25)
            if iqr > 0:
                bin_width = 2 * iqr * (n_samples ** (-1/3))
                data_range = np.max(data) - np.min(data)
                n_bins = max(1, min(int(data_range / bin_width), self.max_bins))
            else:
                n_bins = 10  # Default for constant data
                
        elif self.binning_strategy == 'scott':
            # Scott's rule: bin_width = 3.5 * σ * n^(-1/3)
            std_dev = np.std(data)
            if std_dev > 0:
                bin_width = 3.5 * std_dev * (n_samples ** (-1/3))
                data_range = np.max(data) - np.min(data)
                n_bins = max(1, min(int(data_range / bin_width), self.max_bins))
            else:
                n_bins = 10
                
        elif self.binning_strategy == 'sturges':
            # Sturges' rule: n_bins = log2(n) + 1
            n_bins = min(int(np.log2(n_samples)) + 1, self.max_bins)
            
        else:
            raise ValueError(f"Unknown binning strategy: {self.binning_strategy}")
        
        return max(2, n_bins)  # Ensure at least 2 bins
    
    def _standardize_data(self, data: np.ndarray) -> np.ndarray:
        """Standardize data to zero mean and unit variance."""
        scaler = StandardScaler()
        return scaler.fit_transform(data)
    
    def _compute_joint_histogram(self, X: np.ndarray, Y: np.ndarray, 
                                n_bins_x: int, n_bins_y: int) -> tuple:
        """Compute joint histogram of X and Y."""
        # For multivariate data, use first principal component
        if X.shape[1] > 1:
            pca_x = PCA(n_components=1)
            X_reduced = pca_x.fit_transform(X).ravel()
        else:
            X_reduced = X.ravel()
            
        if Y.shape[1] > 1:
            pca_y = PCA(n_components=1)
            Y_reduced = pca_y.fit_transform(Y).ravel()
        else:
            Y_reduced = Y.ravel()
        
        # Compute 2D histogram
        joint_hist, x_edges, y_edges = np.histogram2d(
            X_reduced, Y_reduced, bins=[n_bins_x, n_bins_y]
        )
        
        return joint_hist, x_edges, y_edges
    
    def _compute_mi_from_histograms(self, joint_hist: np.ndarray, 
                                   x_hist: np.ndarray, y_hist: np.ndarray) -> float:
        """Compute MI from joint and marginal histograms."""
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        n_samples = np.sum(joint_hist)
        
        # Convert counts to probabilities  
        p_joint = (joint_hist + epsilon) / (n_samples + epsilon * joint_hist.size)
        p_x = (x_hist + epsilon) / (n_samples + epsilon * len(x_hist))
        p_y = (y_hist + epsilon) / (n_samples + epsilon * len(y_hist))
        
        # Compute MI: I(X;Y) = ΣΣ p(x,y) log[p(x,y) / (p(x)p(y))]
        mi = 0.0
        for i in range(len(p_x)):
            for j in range(len(p_y)):
                if p_joint[i, j] > epsilon:
                    mi += p_joint[i, j] * np.log(p_joint[i, j] / (p_x[i] * p_y[j]))
        
        return max(0.0, mi)  # Ensure non-negative


class HistogramEstimator(BaseMIEstimator):
    """
    Simple histogram-based MI estimator.
    
    Basic implementation using fixed bin counts for quick estimation.
    Suitable for discrete data or when simple binning is sufficient.
    """
    
    def __init__(self, n_bins: Union[int, str] = 'auto'):
        """
        Initialize histogram estimator.
        
        Args:
            n_bins: Number of bins or 'auto' for automatic selection
        """
        self.n_bins = n_bins
        
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """Estimate MI using simple histogram method."""
        self._validate_input(X, Y)
        X, Y = self._preprocess_data(X, Y)
        
        # Determine bin count
        if self.n_bins == 'auto':
            n_bins = min(int(np.sqrt(X.shape[0])), 50)
        else:
            n_bins = self.n_bins
            
        # Reduce to 1D if multivariate
        if X.shape[1] > 1:
            X_use = X[:, 0]  # Use first dimension
        else:
            X_use = X.ravel()
            
        if Y.shape[1] > 1:
            Y_use = Y[:, 0]  # Use first dimension  
        else:
            Y_use = Y.ravel()
        
        # Compute histograms
        joint_hist, _, _ = np.histogram2d(X_use, Y_use, bins=n_bins)
        x_hist, _ = np.histogram(X_use, bins=n_bins)
        y_hist, _ = np.histogram(Y_use, bins=n_bins)
        
        # Calculate MI
        mi_estimate = self._compute_mi_from_counts(joint_hist, x_hist, y_hist)
        
        return MIEstimationResult(
            mi_value=mi_estimate,
            method="histogram_basic",
            n_samples=X.shape[0],
            computation_time=0.0,
            metadata={
                'n_bins': n_bins,
                'dimensions_used': (1, 1)  # Always use first dimension
            }
        )
    
    def _compute_mi_from_counts(self, joint_counts: np.ndarray,
                               x_counts: np.ndarray, y_counts: np.ndarray) -> float:
        """Compute MI from count histograms."""
        n_total = np.sum(joint_counts)
        if n_total == 0:
            return 0.0
            
        # Convert to probabilities with smoothing
        epsilon = 1e-10
        p_joint = (joint_counts + epsilon) / (n_total + epsilon * joint_counts.size)
        p_x = (x_counts + epsilon) / (n_total + epsilon * len(x_counts))
        p_y = (y_counts + epsilon) / (n_total + epsilon * len(y_counts))
        
        # Compute MI
        mi = 0.0
        for i in range(len(p_x)):
            for j in range(len(p_y)):
                if p_joint[i, j] > epsilon:
                    mi += p_joint[i, j] * np.log(p_joint[i, j] / (p_x[i] * p_y[j]))
        
        return max(0.0, mi)