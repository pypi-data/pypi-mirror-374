"""
📊 Mutual Information Estimation Core
====================================

Core mutual information estimation algorithms for
Information Bottleneck calculations.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, Optional, Tuple, Any, Union, List
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')


class MutualInfoCore:
    """
    Core mutual information estimation algorithms
    
    Provides multiple robust methods for MI estimation including:
    - KSG (Kraskov-Grassberger-Stögbauer) estimator
    - Discrete histogram-based estimation
    - Kernel density-based estimation
    - Binning-based estimation with adaptive bin sizes
    """
    
    def __init__(self, method: str = 'auto', **kwargs):
        """
        Initialize mutual information estimator
        
        Args:
            method: Estimation method ('auto', 'ksg', 'discrete', 'binning', 'kernel')
            **kwargs: Method-specific parameters
        """
        
        self.method = method
        self.params = kwargs
        
        # Method-specific default parameters
        self.ksg_params = {
            'k': kwargs.get('k', 3),
            'metric': kwargs.get('metric', 'chebyshev')
        }
        
        self.binning_params = {
            'n_bins': kwargs.get('n_bins', 'auto'),
            'strategy': kwargs.get('strategy', 'equal_width')
        }
        
        self.kernel_params = {
            'bandwidth': kwargs.get('bandwidth', 'scott'),
            'kernel': kwargs.get('kernel', 'gaussian')
        }
    
    def estimate(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        method: Optional[str] = None
    ) -> float:
        """
        Estimate mutual information I(X;Y)
        
        Args:
            X: First variable
            Y: Second variable
            method: Override default method
            
        Returns:
            Mutual information estimate in bits
        """
        
        method = method or self.method
        
        if method == 'auto':
            method = self._select_method(X, Y)
        
        if method == 'ksg':
            return self._ksg_estimator(X, Y)
        elif method == 'discrete':
            return self._discrete_estimator(X, Y)
        elif method == 'binning':
            return self._binning_estimator(X, Y)
        elif method == 'kernel':
            return self._kernel_estimator(X, Y)
        elif method == 'sklearn':
            return self._sklearn_estimator(X, Y)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _select_method(self, X: np.ndarray, Y: np.ndarray) -> str:
        """Automatically select best MI estimation method"""
        
        n_samples = len(X)
        
        # Check if data is discrete
        x_unique = len(np.unique(X))
        y_unique = len(np.unique(Y))
        
        x_discrete = x_unique < n_samples * 0.1
        y_discrete = y_unique < n_samples * 0.1
        
        if x_discrete and y_discrete and n_samples < 10000:
            return 'discrete'
        elif n_samples < 500:
            return 'binning'
        elif n_samples > 5000:
            return 'ksg'
        else:
            return 'sklearn'
    
    def _ksg_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Kraskov-Grassberger-Stögbauer estimator"""
        
        # Ensure 2D arrays
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        if len(Y.shape) == 1:
            Y = Y.reshape(-1, 1)
        
        n_samples = X.shape[0]
        k = self.ksg_params['k']
        
        # Normalize to [0,1]
        X_norm = (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0) + 1e-12)
        Y_norm = (Y - np.min(Y, axis=0)) / (np.max(Y, axis=0) - np.min(Y, axis=0) + 1e-12)
        
        # Combined space
        XY = np.hstack([X_norm, Y_norm])
        
        # Build nearest neighbor structures
        nbrs_xy = NearestNeighbors(n_neighbors=k+1, metric=self.ksg_params['metric']).fit(XY)
        nbrs_x = NearestNeighbors(metric=self.ksg_params['metric']).fit(X_norm)
        nbrs_y = NearestNeighbors(metric=self.ksg_params['metric']).fit(Y_norm)
        
        # Find k-th nearest neighbors in joint space
        distances, _ = nbrs_xy.kneighbors(XY)
        epsilon = distances[:, -1]  # Distance to k-th neighbor
        
        # KSG estimator computation
        mi_sum = 0.0
        
        for i in range(n_samples):
            # Count neighbors within epsilon distance in marginal spaces
            n_x = len(nbrs_x.radius_neighbors([X_norm[i]], epsilon[i])[1][0]) - 1
            n_y = len(nbrs_y.radius_neighbors([Y_norm[i]], epsilon[i])[1][0]) - 1
            
            # Digamma function approximation
            def digamma_approx(x):
                if x <= 0:
                    return 0.0
                return np.log(max(1, x)) - 1.0/(2*max(1, x))
            
            mi_sum += (digamma_approx(k) - digamma_approx(max(1, n_x + 1)) - 
                      digamma_approx(max(1, n_y + 1)) + digamma_approx(n_samples))
        
        return max(0.0, mi_sum / n_samples / np.log(2))  # Convert to bits
    
    def _discrete_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Discrete histogram-based MI estimation"""
        
        # Create joint histogram
        x_vals = np.unique(X)
        y_vals = np.unique(Y)
        
        joint_hist = np.zeros((len(x_vals), len(y_vals)))
        
        for i, x_val in enumerate(x_vals):
            for j, y_val in enumerate(y_vals):
                joint_hist[i, j] = np.sum((X == x_val) & (Y == y_val))
        
        # Normalize to probabilities
        joint_prob = joint_hist / np.sum(joint_hist)
        
        # Add small epsilon to avoid log(0)
        epsilon = 1e-12
        joint_prob = joint_prob + epsilon
        joint_prob = joint_prob / np.sum(joint_prob)
        
        # Marginal probabilities
        p_x = np.sum(joint_prob, axis=1)
        p_y = np.sum(joint_prob, axis=0)
        
        # Compute mutual information
        mi = 0.0
        for i in range(len(x_vals)):
            for j in range(len(y_vals)):
                if joint_prob[i, j] > epsilon:
                    mi += joint_prob[i, j] * np.log2(joint_prob[i, j] / (p_x[i] * p_y[j]))
        
        return max(0.0, mi)
    
    def _binning_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Binning-based MI estimation for continuous variables"""
        
        n_bins = self._determine_n_bins(X, Y) if self.binning_params['n_bins'] == 'auto' else self.binning_params['n_bins']
        
        # Create bins
        x_bins = np.linspace(np.min(X), np.max(X), n_bins + 1)
        y_bins = np.linspace(np.min(Y), np.max(Y), n_bins + 1)
        
        # Digitize data
        x_binned = np.digitize(X, x_bins) - 1
        y_binned = np.digitize(Y, y_bins) - 1
        
        # Clamp to valid range
        x_binned = np.clip(x_binned, 0, n_bins - 1)
        y_binned = np.clip(y_binned, 0, n_bins - 1)
        
        # Use discrete estimator on binned data
        return self._discrete_estimator(x_binned, y_binned)
    
    def _determine_n_bins(self, X: np.ndarray, Y: np.ndarray) -> int:
        """Determine optimal number of bins using various rules"""
        
        n_samples = len(X)
        
        # Freedman-Diaconis rule
        def fd_bins(data):
            q75, q25 = np.percentile(data, [75, 25])
            iqr = q75 - q25
            if iqr == 0:
                return int(np.sqrt(n_samples))
            h = 2 * iqr / (n_samples ** (1/3))
            return max(1, int((np.max(data) - np.min(data)) / h))
        
        # Sturges' rule
        sturges_bins = max(1, int(np.log2(n_samples) + 1))
        
        # Scott's rule
        def scott_bins(data):
            std = np.std(data)
            if std == 0:
                return int(np.sqrt(n_samples))
            h = 3.5 * std / (n_samples ** (1/3))
            return max(1, int((np.max(data) - np.min(data)) / h))
        
        # Use maximum of different rules (more conservative)
        x_bins_fd = fd_bins(X)
        x_bins_scott = scott_bins(X)
        y_bins_fd = fd_bins(Y)
        y_bins_scott = scott_bins(Y)
        
        optimal_bins = max(
            min(x_bins_fd, y_bins_fd),
            min(x_bins_scott, y_bins_scott),
            sturges_bins,
            5  # Minimum bins
        )
        
        # Cap at reasonable maximum
        return min(optimal_bins, int(np.sqrt(n_samples)), 50)
    
    def _kernel_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Kernel density-based MI estimation"""
        
        try:
            from scipy.stats import gaussian_kde
        except ImportError:
            # Fallback to binning method
            return self._binning_estimator(X, Y)
        
        # Estimate marginal and joint densities using KDE
        joint_data = np.vstack([X.ravel(), Y.ravel()])
        joint_kde = gaussian_kde(joint_data)
        
        x_kde = gaussian_kde(X.ravel())
        y_kde = gaussian_kde(Y.ravel())
        
        # Sample points for integration
        n_samples_integration = min(1000, len(X))
        indices = np.random.choice(len(X), n_samples_integration, replace=False)
        
        x_samples = X[indices]
        y_samples = Y[indices]
        
        # Estimate MI using samples
        mi_sum = 0.0
        for x_val, y_val in zip(x_samples, y_samples):
            joint_density = joint_kde([x_val, y_val])[0]
            x_density = x_kde([x_val])[0]
            y_density = y_kde([y_val])[0]
            
            if joint_density > 1e-12 and x_density > 1e-12 and y_density > 1e-12:
                mi_sum += np.log2(joint_density / (x_density * y_density))
        
        return max(0.0, mi_sum / n_samples_integration)
    
    def _sklearn_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Use sklearn's mutual information estimators"""
        
        # Determine if Y is categorical or continuous
        y_unique = len(np.unique(Y))
        is_classification = y_unique < len(Y) * 0.1 and y_unique < 50
        
        try:
            if is_classification:
                mi = mutual_info_classif(X.reshape(-1, 1), Y, random_state=0)[0]
            else:
                mi = mutual_info_regression(X.reshape(-1, 1), Y, random_state=0)[0]
            
            # Convert to bits (sklearn uses natural log)
            return mi / np.log(2)
            
        except Exception:
            # Fallback to binning method
            return self._binning_estimator(X, Y)


class MutualInfoEstimator:
    """
    High-level mutual information estimator with multiple algorithms
    
    Provides a unified interface for various MI estimation methods
    with automatic method selection and robust error handling.
    """
    
    def __init__(self, **kwargs):
        """Initialize MI estimator"""
        self.core = MutualInfoCore(**kwargs)
        self.estimation_history = []
    
    def estimate(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        method: str = 'auto',
        return_confidence: bool = False
    ) -> Union[float, Tuple[float, Dict[str, Any]]]:
        """
        Estimate mutual information with confidence measures
        
        Args:
            X: First variable
            Y: Second variable
            method: Estimation method
            return_confidence: Return confidence information
            
        Returns:
            MI estimate, optionally with confidence dictionary
        """
        
        # Basic estimation
        mi_estimate = self.core.estimate(X, Y, method)
        
        if return_confidence:
            confidence_info = self._compute_confidence(X, Y, mi_estimate, method)
            return mi_estimate, confidence_info
        else:
            return mi_estimate
    
    def _compute_confidence(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        mi_estimate: float,
        method: str
    ) -> Dict[str, Any]:
        """Compute confidence measures for MI estimate"""
        
        n_samples = len(X)
        
        # Bootstrap confidence interval
        bootstrap_estimates = []
        n_bootstrap = min(50, n_samples // 10)
        
        for _ in range(n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot = X[indices]
            Y_boot = Y[indices]
            
            try:
                mi_boot = self.core.estimate(X_boot, Y_boot, method)
                bootstrap_estimates.append(mi_boot)
            except:
                continue
        
        if bootstrap_estimates:
            bootstrap_estimates = np.array(bootstrap_estimates)
            confidence_interval = np.percentile(bootstrap_estimates, [5, 95])
            bootstrap_std = np.std(bootstrap_estimates)
        else:
            confidence_interval = [mi_estimate, mi_estimate]
            bootstrap_std = 0.0
        
        return {
            'method': method,
            'n_samples': n_samples,
            'confidence_interval_90': confidence_interval,
            'bootstrap_std': bootstrap_std,
            'bootstrap_estimates': len(bootstrap_estimates)
        }
    
    def compare_methods(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        methods: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Compare different MI estimation methods"""
        
        if methods is None:
            methods = ['ksg', 'discrete', 'binning', 'sklearn']
        
        results = {}
        
        for method in methods:
            try:
                mi = self.core.estimate(X, Y, method)
                results[method] = mi
            except Exception as e:
                results[method] = None
                print(f"Warning: {method} failed: {e}")
        
        return results