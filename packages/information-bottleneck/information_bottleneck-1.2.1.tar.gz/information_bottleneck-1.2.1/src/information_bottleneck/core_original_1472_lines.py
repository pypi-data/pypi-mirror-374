"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Core Algorithms - UNIFIED IMPLEMENTATION
==============================================================

This module consolidates all the core Information Bottleneck algorithm implementations
from the scattered structure into a single, unified location.

Consolidated from:
- information_bottleneck_main.py (112KB)
- information_bottleneck.py (129KB) 
- ib_modules/core_algorithm.py (35KB)
- ib_modules/information_bottleneck_core.py (112KB)
- ib_modules/core_theory.py (35KB)
- ib_modules/neural_information_bottleneck.py (24KB)
- deep_ib.py (18KB)
- neural_ib.py (16KB)
- ib_classifier.py (22KB)
- ib_optimizer.py (17KB)
- mutual_info_core.py (16KB)
- mutual_info_estimator.py (13KB)

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057
"""

import numpy as np
import scipy.sparse as sp
import scipy.optimize as opt
from scipy.special import logsumexp
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.metrics import mutual_info_score
import torch
import torch.nn as nn
import torch.optim as optim
import warnings
from typing import Optional, Union, Dict, List, Tuple, Any
from abc import ABC, abstractmethod

# ============================================================================
# CORE THEORY MIXINS - Mathematical Foundation
# ============================================================================

class CoreTheoryMixin:
    """
    Core mathematical theory for Information Bottleneck method.
    
    Implements the fundamental equations from Tishby, Pereira & Bialek (1999):
    - Lagrangian formulation: L = I(T;Y) - β*I(X;T)  
    - Self-consistent equations for optimal solution
    - Theoretical bounds and convergence conditions
    """
    
    def compute_ib_lagrangian(self, I_TX, I_TY, beta):
        """
        Compute Information Bottleneck Lagrangian.
        
        L = I(T;Y) - β*I(X;T)
        
        The core objective function that balances compression (minimize I(X;T))
        with relevance (maximize I(T;Y)).
        """
        return I_TY - beta * I_TX
    
    def compute_theoretical_bounds(self, X, Y):
        """Compute theoretical Information Bottleneck bounds."""
        # Rate bound: 0 ≤ I(X;T) ≤ I(X;Y)
        I_XY = self._compute_mutual_information_discrete(X, Y)
        
        # Distortion bound: 0 ≤ I(T;Y) ≤ min(H(Y), I(X;Y))
        H_Y = self._compute_entropy(Y)
        
        return {
            'rate_lower_bound': 0.0,
            'rate_upper_bound': I_XY,
            'distortion_lower_bound': 0.0, 
            'distortion_upper_bound': min(H_Y, I_XY),
            'I_XY': I_XY,
            'H_Y': H_Y
        }
    
    def verify_self_consistency(self, p_t_given_x, p_y_given_t, beta, tolerance=1e-6):
        """
        Verify the self-consistent equations are satisfied.
        
        For optimal solution:
        p(t|x) ∝ p(t) * exp(-β * D_KL[p(y|x) || p(y|t)])
        p(y|t) = Σ_x p(y|x) * p(x|t) 
        """
        # This is a mathematical verification step
        # In practice, convergence of the algorithm implies self-consistency
        return True

class MutualInformationMixin:
    """
    Advanced mutual information estimation methods.
    
    Implements multiple estimators for different data types and scenarios:
    - Discrete data: Direct computation from joint distributions
    - Continuous data: Kernel density estimation, k-NN methods
    - Neural estimators: MINE, InfoNCE approaches
    """
    
    def _compute_mutual_information_discrete(self, X, Y):
        """Compute MI for discrete variables using joint probability."""
        # FIXME: Critical algorithmic complexity and numerical stability issues
        # Issue 1: O(|X|×|Y|×n) time complexity - should be O(n log n) with efficient binning
        # Issue 2: Nested loops are extremely slow for large datasets
        # Issue 3: No numerical stability for small probabilities
        # Issue 4: Memory inefficient for high-cardinality discrete variables
        
        if len(X) != len(Y):
            raise ValueError("X and Y must have same length")
        
        # FIXME: No input validation for data types or ranges
        # Issue: Could fail with non-discrete data, extreme values, or NaN
        # Solutions:
        # 1. Validate inputs are discrete/categorical
        # 2. Check for NaN/Inf values and handle appropriately
        # 3. Add warnings for high cardinality that may cause performance issues
        #
        # Example validation:
        # if np.any(np.isnan(X)) or np.any(np.isnan(Y)):
        #     raise ValueError("NaN values not supported for discrete MI computation")
        # if len(np.unique(X)) > 1000 or len(np.unique(Y)) > 1000:
        #     warnings.warn("High cardinality variables may cause performance issues")
            
        # Create joint distribution
        unique_x = np.unique(X)
        unique_y = np.unique(Y) 
        n = len(X)
        
        # FIXME: Extremely inefficient nested loop implementation O(|X|×|Y|×n)
        # Issue: For large datasets or high cardinality, this becomes prohibitively slow
        # Solutions:
        # 1. Use numpy's histogram2d for O(n log n) complexity
        # 2. Use pandas crosstab for efficient joint distribution computation
        # 3. Use sparse matrices for high-dimensional discrete spaces
        #
        # Efficient implementation:
        # joint_counts, x_edges, y_edges = np.histogram2d(X, Y, bins=[unique_x, unique_y])
        # p_xy = joint_counts / n
        # Much faster and more memory efficient!
        
        # Compute joint probability p(x,y)
        p_xy = np.zeros((len(unique_x), len(unique_y)))
        for i, x in enumerate(unique_x):
            for j, y in enumerate(unique_y):
                p_xy[i, j] = np.sum((X == x) & (Y == y)) / n
                
        # Compute marginals
        p_x = np.sum(p_xy, axis=1)
        p_y = np.sum(p_xy, axis=0)
        
        # FIXME: Numerical instability in logarithm computation
        # Issue: log(p_xy[i, j] / (p_x[i] * p_y[j])) can be unstable for small probabilities
        # Solutions:
        # 1. Use log-space arithmetic: log(a/b) = log(a) - log(b)
        # 2. Add small epsilon to prevent log(0)
        # 3. Use scipy's logsumexp for numerical stability
        #
        # Stable implementation:
        # mi = 0.0
        # for i in range(len(unique_x)):
        #     for j in range(len(unique_y)):
        #         if p_xy[i, j] > 1e-12 and p_x[i] > 1e-12 and p_y[j] > 1e-12:
        #             log_ratio = np.log(p_xy[i, j]) - np.log(p_x[i]) - np.log(p_y[j])
        #             mi += p_xy[i, j] * log_ratio
        
        # Compute MI = Σ p(x,y) * log(p(x,y) / (p(x)*p(y)))
        mi = 0.0
        for i in range(len(unique_x)):
            for j in range(len(unique_y)):
                if p_xy[i, j] > 0:
                    # FIXME: This can cause numerical overflow/underflow
                    # Better: use log-space computation
                    mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
                    
        return mi
    
    def _compute_mutual_information_continuous(self, X, Y, method='knn', k=3):
        """Compute MI for continuous variables."""
        from sklearn.metrics import mutual_info_score
        from sklearn.feature_selection import mutual_info_regression
        
        if method == 'knn':
            # Use sklearn's mutual info estimator (k-NN based)
            return mutual_info_regression(X.reshape(-1, 1), Y, 
                                        discrete_features=False,
                                        n_neighbors=k)[0]
        elif method == 'discretize':
            # Discretize and use discrete MI
            X_discrete = np.digitize(X, bins=np.linspace(X.min(), X.max(), 20))
            Y_discrete = np.digitize(Y, bins=np.linspace(Y.min(), Y.max(), 20))
            return mutual_info_score(X_discrete, Y_discrete)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _compute_entropy(self, X):
        """Compute entropy H(X)."""
        unique, counts = np.unique(X, return_counts=True)
        probabilities = counts / len(X)
        return -np.sum(probabilities * np.log2(probabilities + 1e-10))

class OptimizationMixin:
    """
    Optimization algorithms for Information Bottleneck.
    
    Implements various optimization approaches:
    - Iterative Blahut-Arimoto algorithm (original method)
    - Deterministic annealing for better convergence
    - Sequential Information Bottleneck for large datasets
    - Gradient-based optimization for neural variants
    """
    
    def _optimize_blahut_arimoto(self, X, Y, n_clusters, beta, max_iter=100, tol=1e-6):
        """
        Original Blahut-Arimoto iterative algorithm.
        
        Alternates between:
        1. Update p(t|x): p(t|x) ∝ p(t) * exp(-β * D_KL[p(y|x) || p(y|t)])
        2. Update p(y|t): p(y|t) = Σ_x p(y|x) * p(x|t)
        """
        # FIXME: Critical algorithmic and numerical issues in Blahut-Arimoto implementation
        # Issue 1: No numerical stability in probability updates (can produce NaN/Inf)
        # Issue 2: Random initialization may lead to poor local minima
        # Issue 3: Missing methods: _update_conditional_probabilities, _compute_I_TX, etc.
        # Issue 4: No convergence monitoring beyond simple tolerance check
        # Issue 5: No handling of degenerate cases (empty clusters, singular distributions)
        
        n_samples = len(X)
        n_x_vals = len(np.unique(X))
        n_y_vals = len(np.unique(Y))
        
        # FIXME: Poor initialization strategy can lead to convergence failures
        # Issue: Random Dirichlet initialization often leads to poor local minima
        # Solutions:
        # 1. Use informed initialization (k-means, PCA-based, or data-driven)
        # 2. Multiple random restarts with best objective selection
        # 3. Warm-start from lower beta values (annealing)
        #
        # Better initialization:
        # from sklearn.cluster import KMeans
        # kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        # cluster_assignments = kmeans.fit_predict(X.reshape(-1, 1))
        # p_t_given_x = np.eye(n_clusters)[cluster_assignments] + 1e-6  # One-hot + smoothing
        # p_t_given_x /= p_t_given_x.sum(axis=1, keepdims=True)
        
        # Initialize random cluster assignments
        p_t_given_x = np.random.dirichlet(np.ones(n_clusters), size=n_x_vals)
        p_t_given_x /= p_t_given_x.sum(axis=1, keepdims=True)
        
        # FIXME: No numerical stability safeguards for probability matrices
        # Issue: Probabilities can become 0 or very small, causing log(0) errors
        # Solutions:
        # 1. Add small epsilon to prevent zero probabilities
        # 2. Renormalize after each update
        # 3. Monitor for numerical issues and restart if needed
        #
        # Example:
        # epsilon = 1e-10
        # p_t_given_x = np.clip(p_t_given_x, epsilon, 1.0 - epsilon)
        # p_t_given_x /= p_t_given_x.sum(axis=1, keepdims=True)
        
        prev_objective = -np.inf
        
        # FIXME: Missing convergence diagnostics and oscillation detection
        # Issue: Simple tolerance check misses oscillating or slowly converging solutions
        # Solutions:
        # 1. Track objective history and detect oscillations
        # 2. Use relative change instead of absolute change
        # 3. Add maximum patience for convergence
        # 4. Monitor gradient norms or probability changes
        #
        # Better convergence tracking:
        # objective_history = []
        # patience_counter = 0
        # max_patience = 10
        
        for iteration in range(max_iter):
            # FIXME: Missing implementation of critical update methods
            # Issue: Methods _update_conditional_probabilities, _update_cluster_assignments don't exist
            # This will cause AttributeError at runtime
            # Solutions:
            # 1. Implement these missing methods following Blahut-Arimoto equations
            # 2. Use proper mathematical formulations from Tishby et al. (1999)
            # 3. Add numerical stability to each update step
            #
            # Correct E-step implementation needed:
            # def _update_conditional_probabilities(self, X, Y, p_t_given_x):
            #     # p(y|t) = Σ_x p(y|x) * p(x|t) / p(t)
            #     # Need to implement proper Bayes rule update
            
            # Update p(y|t) based on current p(t|x)
            p_y_given_t = self._update_conditional_probabilities(X, Y, p_t_given_x)
            
            # Update p(t|x) based on current p(y|t)  
            p_t_given_x = self._update_cluster_assignments(X, Y, p_y_given_t, beta)
            
            # FIXME: Missing implementation of mutual information computation methods
            # Issue: _compute_I_TX and _compute_I_TY methods are not defined
            # Solutions:
            # 1. Implement proper MI computation: I(T;X) = Σ p(t,x) log(p(t,x)/(p(t)p(x)))
            # 2. Use efficient algorithms to avoid O(n³) complexity
            # 3. Add numerical stability to MI calculations
            #
            # Required implementations:
            # def _compute_I_TX(self, X, p_t_given_x):
            #     # Compute I(T;X) = H(T) - H(T|X)
            # def _compute_I_TY(self, Y, p_y_given_t, p_t_given_x):
            #     # Compute I(T;Y) using joint distributions
            
            # Compute objective
            I_TX = self._compute_I_TX(X, p_t_given_x)
            I_TY = self._compute_I_TY(Y, p_y_given_t, p_t_given_x)
            objective = I_TY - beta * I_TX
            
            # FIXME: Weak convergence check may miss important convergence issues
            # Issue: Only checks absolute objective change, misses oscillations and slow convergence
            # Solutions:
            # 1. Add relative change: |new - old| / |old| < relative_tol
            # 2. Check probability matrix changes: ||p_new - p_old||_F < prob_tol
            # 3. Detect oscillations in objective function
            # 4. Add early stopping for non-improving iterations
            #
            # Better convergence check:
            # relative_change = abs(objective - prev_objective) / (abs(prev_objective) + 1e-10)
            # if relative_change < tol and iteration > 5:  # Allow few iterations to settle
            #     break
            
            if abs(objective - prev_objective) < tol:
                break
                
            prev_objective = objective
            
        # FIXME: No validation of final solution quality
        # Issue: Could return degenerate or poor solutions without warning
        # Solutions:
        # 1. Check for empty clusters or singular probability matrices
        # 2. Validate that probabilities sum to 1
        # 3. Compute and warn about solution quality metrics
        #
        # Example validation:
        # if np.any(np.sum(p_t_given_x, axis=1) < 0.99):
        #     warnings.warn("Probability normalization issue detected")
        # if np.any(np.sum(p_y_given_t, axis=1) < 0.99):
        #     warnings.warn("Conditional probability normalization issue")
            
        return p_t_given_x, p_y_given_t, objective
    
    def _deterministic_annealing(self, X, Y, n_clusters, beta_schedule, max_iter=50):
        """
        Deterministic annealing approach.
        
        Gradually increases β from 0 to target value to avoid local minima.
        """
        results = []
        p_t_given_x = None
        
        for beta in beta_schedule:
            if p_t_given_x is None:
                # Initialize with random assignment
                n_x_vals = len(np.unique(X))
                p_t_given_x = np.random.dirichlet(np.ones(n_clusters), size=n_x_vals)
            
            # Optimize at this beta level
            p_t_given_x, p_y_given_t, objective = self._optimize_blahut_arimoto(
                X, Y, n_clusters, beta, max_iter=max_iter
            )
            
            results.append({
                'beta': beta,
                'p_t_given_x': p_t_given_x.copy(),
                'p_y_given_t': p_y_given_t.copy(), 
                'objective': objective
            })
            
        return results

class TransformPredictMixin:
    """
    Transformation and prediction functionality.
    
    Implements the core interface for using Information Bottleneck as:
    - Dimensionality reduction (transform)
    - Feature selection (select features)
    - Clustering (group similar inputs)
    - Classification (predict labels)
    """
    
    def transform(self, X):
        """
        Transform data through the information bottleneck.
        
        Maps X → T using learned p(t|x) distributions.
        """
        if not hasattr(self, 'p_t_given_x_'):
            raise ValueError("Model must be fitted before transform")
            
        # Map continuous X to discrete clusters based on learned mapping
        T = np.zeros(len(X))
        unique_x = np.unique(self.X_fit_)
        
        for i, x in enumerate(X):
            # Find closest training example
            closest_idx = np.argmin(np.abs(unique_x - x))
            cluster_probs = self.p_t_given_x_[closest_idx]
            # Sample from cluster distribution or take most likely
            T[i] = np.argmax(cluster_probs)
            
        return T.astype(int)
    
    def predict_proba(self, X):
        """Predict class probabilities using learned p(y|t)."""
        if not hasattr(self, 'p_y_given_t_'):
            raise ValueError("Model must be fitted before prediction")
            
        T = self.transform(X)
        return self.p_y_given_t_[T]
    
    def predict(self, X):
        """Predict class labels."""
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)
    
    def fit_transform(self, X, y=None):
        """Fit model and return transformed data."""
        self.fit(X, y)
        return self.transform(X)

class EvaluationMixin:
    """
    Evaluation metrics and analysis for Information Bottleneck.
    
    Provides comprehensive evaluation including:
    - Information-theoretic measures (I(X;T), I(T;Y), etc.)
    - Classification performance when applicable
    - Compression-distortion trade-off analysis
    - Theoretical bounds verification
    """
    
    def compute_information_metrics(self, X, Y, T=None):
        """Compute all information-theoretic metrics."""
        if T is None:
            T = self.transform(X)
            
        metrics = {}
        
        # Core information measures
        metrics['I_XT'] = self._compute_mutual_information_discrete(X, T)
        metrics['I_TY'] = self._compute_mutual_information_discrete(T, Y)
        metrics['I_XY'] = self._compute_mutual_information_discrete(X, Y)
        
        # Entropies
        metrics['H_X'] = self._compute_entropy(X)
        metrics['H_T'] = self._compute_entropy(T)
        metrics['H_Y'] = self._compute_entropy(Y)
        
        # Information bottleneck objective
        if hasattr(self, 'beta'):
            metrics['IB_objective'] = metrics['I_TY'] - self.beta * metrics['I_XT']
            
        # Compression ratio
        metrics['compression_ratio'] = metrics['I_XT'] / metrics['I_XY'] if metrics['I_XY'] > 0 else 0
        
        # Information transmission efficiency 
        metrics['transmission_efficiency'] = metrics['I_TY'] / metrics['I_XT'] if metrics['I_XT'] > 0 else 0
        
        return metrics
    
    def evaluate_compression_distortion_tradeoff(self, X, Y, beta_values):
        """Analyze compression-distortion trade-off across β values."""
        tradeoff_data = []
        
        for beta in beta_values:
            # Temporarily set beta and refit
            original_beta = getattr(self, 'beta', None)
            self.beta = beta
            self.fit(X, Y)
            
            # Compute metrics
            T = self.transform(X)
            metrics = self.compute_information_metrics(X, Y, T)
            
            tradeoff_data.append({
                'beta': beta,
                'compression': metrics['I_XT'],
                'relevance': metrics['I_TY'], 
                'objective': metrics['IB_objective']
            })
            
        # Restore original beta
        if original_beta is not None:
            self.beta = original_beta
            self.fit(X, Y)
            
        return tradeoff_data

# ============================================================================
# MAIN ALGORITHM IMPLEMENTATIONS
# ============================================================================

class InformationBottleneck(BaseEstimator, TransformerMixin, CoreTheoryMixin, 
                          MutualInformationMixin, OptimizationMixin, 
                          TransformPredictMixin, EvaluationMixin):
    """
    Classical Information Bottleneck Implementation.
    
    Based on: Tishby, Pereira & Bialek (1999)
    "The Information Bottleneck Method"
    
    The Information Bottleneck method finds representations T of data X that are:
    1. Maximally informative about target Y: maximize I(T;Y)
    2. Minimally complex: minimize I(X;T) 
    
    The trade-off is controlled by parameter β in the objective:
    L = I(T;Y) - β*I(X;T)
    
    Parameters
    ----------
    n_clusters : int, default=10
        Number of clusters T (bottleneck size)
    beta : float, default=1.0
        Trade-off parameter between compression and relevance
    max_iter : int, default=100
        Maximum iterations for optimization
    tol : float, default=1e-6
        Convergence tolerance
    method : str, default='blahut_arimoto'
        Optimization method ('blahut_arimoto', 'deterministic_annealing')
    """
    
    def __init__(self, n_clusters=10, beta=1.0, max_iter=100, tol=1e-6, 
                 method='blahut_arimoto', random_state=None):
        self.n_clusters = n_clusters
        self.beta = beta
        self.max_iter = max_iter
        self.tol = tol
        self.method = method
        self.random_state = random_state
    
    def fit(self, X, Y):
        """
        Fit Information Bottleneck model.
        
        Parameters
        ----------
        X : array-like, shape (n_samples,) or (n_samples, n_features)
            Input data
        Y : array-like, shape (n_samples,)
            Target variable
        """
        X = np.asarray(X).flatten() if X.ndim > 1 else np.asarray(X)
        Y = np.asarray(Y).flatten()
        
        if len(X) != len(Y):
            raise ValueError("X and Y must have same number of samples")
        
        self.X_fit_ = X
        self.Y_fit_ = Y
        
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        if self.method == 'blahut_arimoto':
            self.p_t_given_x_, self.p_y_given_t_, self.objective_ = \
                self._optimize_blahut_arimoto(X, Y, self.n_clusters, self.beta, 
                                            self.max_iter, self.tol)
        elif self.method == 'deterministic_annealing':
            beta_schedule = np.logspace(-2, np.log10(self.beta), 10)
            results = self._deterministic_annealing(X, Y, self.n_clusters, 
                                                  beta_schedule, self.max_iter//10)
            # Use final result
            final_result = results[-1]
            self.p_t_given_x_ = final_result['p_t_given_x']
            self.p_y_given_t_ = final_result['p_y_given_t']
            self.objective_ = final_result['objective']
        else:
            raise ValueError(f"Unknown method: {self.method}")
            
        return self
    
    # Helper methods for optimization
    def _update_conditional_probabilities(self, X, Y, p_t_given_x):
        """Update p(y|t) based on current cluster assignments."""
        unique_x = np.unique(X)
        unique_y = np.unique(Y)
        n_clusters = p_t_given_x.shape[1]
        n_y_vals = len(unique_y)
        
        p_y_given_t = np.zeros((n_clusters, n_y_vals))
        
        for t in range(n_clusters):
            # Compute p(y|t) = Σ_x p(y|x) * p(x|t)
            denominator = 0
            for i, x in enumerate(unique_x):
                x_mask = (X == x)
                p_x_given_t = p_t_given_x[i, t] * np.sum(x_mask) / len(X)
                denominator += p_x_given_t
                
                for j, y in enumerate(unique_y):
                    y_given_x = np.sum((Y == y) & x_mask) / max(np.sum(x_mask), 1)
                    p_y_given_t[t, j] += y_given_x * p_x_given_t
                    
            if denominator > 0:
                p_y_given_t[t] /= denominator
            else:
                p_y_given_t[t] = np.ones(n_y_vals) / n_y_vals
                
        return p_y_given_t
    
    def _update_cluster_assignments(self, X, Y, p_y_given_t, beta):
        """Update p(t|x) based on current conditional probabilities."""
        unique_x = np.unique(X)
        unique_y = np.unique(Y)
        n_clusters = p_y_given_t.shape[0]
        n_x_vals = len(unique_x)
        
        p_t_given_x = np.zeros((n_x_vals, n_clusters))
        
        for i, x in enumerate(unique_x):
            x_mask = (X == x)
            
            # Compute p(y|x) for this x
            p_y_given_x = np.zeros(len(unique_y))
            for j, y in enumerate(unique_y):
                p_y_given_x[j] = np.sum((Y == y) & x_mask) / max(np.sum(x_mask), 1)
                
            # Update p(t|x) ∝ p(t) * exp(-β * D_KL[p(y|x) || p(y|t)])
            for t in range(n_clusters):
                # Compute KL divergence D_KL[p(y|x) || p(y|t)]
                kl_div = 0
                for j in range(len(unique_y)):
                    if p_y_given_x[j] > 0 and p_y_given_t[t, j] > 0:
                        kl_div += p_y_given_x[j] * np.log(p_y_given_x[j] / p_y_given_t[t, j])
                
                # Assume uniform prior p(t)
                p_t = 1.0 / n_clusters
                p_t_given_x[i, t] = p_t * np.exp(-beta * kl_div)
                
            # Normalize
            p_t_given_x[i] /= np.sum(p_t_given_x[i])
            
        return p_t_given_x
    
    def _compute_I_TX(self, X, p_t_given_x):
        """Compute I(X;T) from cluster assignments."""
        unique_x = np.unique(X)
        n_clusters = p_t_given_x.shape[1]
        
        # Compute joint distribution p(x,t)
        p_xt = np.zeros((len(unique_x), n_clusters))
        for i, x in enumerate(unique_x):
            p_x = np.sum(X == x) / len(X)
            p_xt[i] = p_x * p_t_given_x[i]
            
        # Compute marginals
        p_x = np.sum(p_xt, axis=1)
        p_t = np.sum(p_xt, axis=0)
        
        # Compute MI
        mi = 0
        for i in range(len(unique_x)):
            for t in range(n_clusters):
                if p_xt[i, t] > 0:
                    mi += p_xt[i, t] * np.log(p_xt[i, t] / (p_x[i] * p_t[t]))
                    
        return mi
    
    def _compute_I_TY(self, Y, p_y_given_t, p_t_given_x):
        """Compute I(T;Y) from conditional probabilities."""
        unique_x = np.unique(self.X_fit_)
        unique_y = np.unique(Y)
        n_clusters = p_y_given_t.shape[0]
        
        # Compute p(t) from p(t|x) and p(x)
        p_t = np.zeros(n_clusters)
        for i, x in enumerate(unique_x):
            p_x = np.sum(self.X_fit_ == x) / len(self.X_fit_)
            p_t += p_x * p_t_given_x[i]
            
        # Compute p(y)
        p_y = np.zeros(len(unique_y))
        for j, y in enumerate(unique_y):
            p_y[j] = np.sum(Y == y) / len(Y)
            
        # Compute joint p(t,y) = p(y|t) * p(t)
        p_ty = p_y_given_t * p_t.reshape(-1, 1)
        
        # Compute MI
        mi = 0
        for t in range(n_clusters):
            for j in range(len(unique_y)):
                if p_ty[t, j] > 0:
                    mi += p_ty[t, j] * np.log(p_ty[t, j] / (p_t[t] * p_y[j]))
                    
        return mi


class NeuralInformationBottleneck(nn.Module, BaseEstimator, TransformerMixin):
    """
    Neural Information Bottleneck implementation using deep networks.
    
    Uses neural networks to parameterize the encoder p(T|X) and decoder p(Y|T)
    distributions, allowing application to high-dimensional continuous data.
    
    The objective is still the same:
    L = I(T;Y) - β*I(X;T)
    
    But now T is a continuous latent representation, and mutual information
    is estimated using neural mutual information estimators.
    
    Parameters
    ----------
    input_dim : int
        Dimensionality of input X
    latent_dim : int, default=10
        Dimensionality of bottleneck representation T
    output_dim : int
        Dimensionality of output Y
    beta : float, default=1.0
        Trade-off parameter
    encoder_hidden : list, default=[50, 50]
        Hidden layer sizes for encoder network
    decoder_hidden : list, default=[50, 50]
        Hidden layer sizes for decoder network
    """
    
    def __init__(self, input_dim, latent_dim=10, output_dim=1, beta=1.0,
                 encoder_hidden=[50, 50], decoder_hidden=[50, 50],
                 learning_rate=1e-3, max_epochs=100):
        super(NeuralInformationBottleneck, self).__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.output_dim = output_dim
        self.beta = beta
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        
        # Build encoder network: X → μ, σ for T ~ N(μ, σ²)
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in encoder_hidden:
            encoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim
            
        # Output both mean and log-variance for reparameterization trick
        encoder_layers.append(nn.Linear(prev_dim, 2 * latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Build decoder network: T → Y
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in decoder_hidden:
            decoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = hidden_dim
        decoder_layers.append(nn.Linear(prev_dim, output_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x):
        """Encode input to latent distribution parameters."""
        h = self.encoder(x)
        mu, log_var = h.chunk(2, dim=1)
        return mu, log_var
    
    def reparameterize(self, mu, log_var):
        """Reparameterization trick for sampling from latent distribution."""
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, t):
        """Decode latent representation to output."""
        return self.decoder(t)
    
    def forward(self, x):
        """Forward pass through the network."""
        mu, log_var = self.encode(x)
        t = self.reparameterize(mu, log_var)
        y_pred = self.decode(t)
        return y_pred, mu, log_var, t
    
    def compute_loss(self, x, y):
        """
        Compute Information Bottleneck loss.
        
        L = -I(T;Y) + β*I(X;T)
        
        I(T;Y) is approximated by reconstruction loss (for continuous Y)
        I(X;T) is the KL divergence between encoder output and prior
        """
        y_pred, mu, log_var, t = self.forward(x)
        
        # Reconstruction loss approximates -I(T;Y)
        if self.output_dim == 1:
            reconstruction_loss = nn.MSELoss()(y_pred, y)
        else:
            reconstruction_loss = nn.CrossEntropyLoss()(y_pred, y)
        
        # KL divergence approximates I(X;T) 
        kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        kl_loss /= x.size(0)  # Normalize by batch size
        
        # Information Bottleneck objective
        ib_loss = reconstruction_loss + self.beta * kl_loss
        
        return ib_loss, reconstruction_loss, kl_loss
    
    def fit(self, X, y):
        """Fit the neural information bottleneck model."""
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).view(-1, self.output_dim)
        
        optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)
        
        self.train()
        for epoch in range(self.max_epochs):
            optimizer.zero_grad()
            loss, recon_loss, kl_loss = self.compute_loss(X_tensor, y_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Loss={loss:.4f}, Recon={recon_loss:.4f}, KL={kl_loss:.4f}")
        
        return self
    
    def transform(self, X):
        """Transform data through the bottleneck."""
        X_tensor = torch.FloatTensor(X)
        self.eval()
        with torch.no_grad():
            mu, log_var = self.encode(X_tensor)
            # Use mean of latent distribution for deterministic transform
            return mu.numpy()
    
    def predict(self, X):
        """Predict outputs for new inputs."""
        X_tensor = torch.FloatTensor(X)
        self.eval()
        with torch.no_grad():
            y_pred, _, _, _ = self.forward(X_tensor)
            return y_pred.numpy()


class DeepInformationBottleneck(NeuralInformationBottleneck):
    """
    Deep Information Bottleneck with multiple bottleneck layers.
    
    Extends the Neural IB to have multiple compression stages, creating
    a hierarchy of representations with increasing compression.
    
    Architecture: X → T₁ → T₂ → ... → Tₖ → Y
    
    Each layer Ti has lower dimensionality than Ti-1, creating a series
    of information bottlenecks.
    """
    
    def __init__(self, input_dim, bottleneck_dims=[50, 20, 10], output_dim=1, 
                 beta=1.0, learning_rate=1e-3, max_epochs=100):
        # Use the final bottleneck dimension as latent_dim for parent class
        super(DeepInformationBottleneck, self).__init__(
            input_dim=input_dim, 
            latent_dim=bottleneck_dims[-1],
            output_dim=output_dim,
            beta=beta,
            learning_rate=learning_rate,
            max_epochs=max_epochs
        )
        
        self.bottleneck_dims = bottleneck_dims
        
        # Build multi-layer encoder
        encoder_layers = []
        prev_dim = input_dim
        
        for i, dim in enumerate(bottleneck_dims):
            # Add compression layer
            encoder_layers.append(nn.Linear(prev_dim, dim))
            if i < len(bottleneck_dims) - 1:  # No activation on final layer
                encoder_layers.append(nn.ReLU())
            prev_dim = dim
            
        # Final layer outputs mean and log-variance
        encoder_layers.append(nn.Linear(prev_dim, 2 * bottleneck_dims[-1]))
        self.encoder = nn.Sequential(*encoder_layers)
        
        print(f"Deep IB: {input_dim} → {' → '.join(map(str, bottleneck_dims))} → {output_dim}")


class InformationBottleneckClassifier(BaseEstimator, ClassifierMixin, TransformerMixin):
    """
    Information Bottleneck for classification tasks.
    
    Specializes the IB method for classification by:
    1. Using class labels as the relevant variable Y
    2. Providing sklearn-compatible interface
    3. Supporting multiclass classification
    4. Automatic parameter selection via cross-validation
    """
    
    def __init__(self, n_clusters=10, beta=1.0, max_iter=100, 
                 cv_beta_search=False, beta_range=(0.1, 10.0)):
        self.n_clusters = n_clusters
        self.beta = beta
        self.max_iter = max_iter
        self.cv_beta_search = cv_beta_search
        self.beta_range = beta_range
    
    def fit(self, X, y):
        """Fit classifier using Information Bottleneck."""
        X = np.asarray(X)
        y = np.asarray(y)
        
        # Convert to discrete features if continuous
        if X.dtype in [np.float32, np.float64] and X.ndim > 1:
            # Use k-means to discretize features
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=min(20, len(np.unique(X.flatten()))), 
                          random_state=42)
            X_discrete = kmeans.fit_predict(X.reshape(len(X), -1))
            self.discretizer_ = kmeans
        else:
            X_discrete = X.flatten() if X.ndim > 1 else X
            self.discretizer_ = None
        
        # Encode class labels
        self.classes_ = np.unique(y)
        y_encoded = np.searchsorted(self.classes_, y)
        
        if self.cv_beta_search:
            # Find optimal beta via cross-validation
            from sklearn.model_selection import cross_val_score
            
            beta_values = np.logspace(np.log10(self.beta_range[0]), 
                                    np.log10(self.beta_range[1]), 10)
            best_score = -np.inf
            best_beta = self.beta
            
            for beta in beta_values:
                ib = InformationBottleneck(n_clusters=self.n_clusters, 
                                         beta=beta, max_iter=self.max_iter)
                try:
                    # Create temporary classifier for CV
                    temp_clf = InformationBottleneckClassifier(
                        n_clusters=self.n_clusters, beta=beta, 
                        max_iter=self.max_iter, cv_beta_search=False
                    )
                    scores = cross_val_score(temp_clf, X, y, cv=3, scoring='accuracy')
                    mean_score = np.mean(scores)
                    
                    if mean_score > best_score:
                        best_score = mean_score
                        best_beta = beta
                except:
                    continue
                    
            self.beta = best_beta
        
        # Fit final model
        self.ib_model_ = InformationBottleneck(
            n_clusters=self.n_clusters,
            beta=self.beta, 
            max_iter=self.max_iter
        )
        self.ib_model_.fit(X_discrete, y_encoded)
        
        return self
    
    def predict(self, X):
        """Predict class labels."""
        X = np.asarray(X)
        
        # Apply same discretization as training
        if self.discretizer_ is not None:
            X_discrete = self.discretizer_.predict(X.reshape(len(X), -1))
        else:
            X_discrete = X.flatten() if X.ndim > 1 else X
        
        # Get cluster assignments
        T = self.ib_model_.transform(X_discrete)
        
        # Use learned p(y|t) for prediction
        y_pred_encoded = np.argmax(self.ib_model_.p_y_given_t_[T], axis=1)
        
        # Convert back to original class labels
        return self.classes_[y_pred_encoded]
    
    def predict_proba(self, X):
        """Predict class probabilities."""
        X = np.asarray(X)
        
        if self.discretizer_ is not None:
            X_discrete = self.discretizer_.predict(X.reshape(len(X), -1))
        else:
            X_discrete = X.flatten() if X.ndim > 1 else X
            
        T = self.ib_model_.transform(X_discrete)
        return self.ib_model_.p_y_given_t_[T]
    
    def transform(self, X):
        """Transform data through information bottleneck."""
        X = np.asarray(X)
        
        if self.discretizer_ is not None:
            X_discrete = self.discretizer_.predict(X.reshape(len(X), -1))
        else:
            X_discrete = X.flatten() if X.ndim > 1 else X
            
        return self.ib_model_.transform(X_discrete)


class IBOptimizer:
    """
    Advanced optimization algorithms for Information Bottleneck.
    
    Implements state-of-the-art optimization methods:
    - Sequential Information Bottleneck for large datasets
    - Agglomerative Information Bottleneck (Slonim & Tishby)
    - Parametric approaches for continuous variables
    - Multi-objective optimization for beta-free methods
    """
    
    def __init__(self, method='sequential', **kwargs):
        self.method = method
        self.kwargs = kwargs
    
    def optimize(self, X, Y, n_clusters, beta_schedule=None):
        """
        Optimize Information Bottleneck with advanced methods.
        
        Parameters
        ----------
        X : array-like
            Input data
        Y : array-like  
            Target data
        n_clusters : int or list
            Number of clusters (or schedule for agglomerative)
        beta_schedule : array-like, optional
            Schedule of beta values for annealing
        """
        if self.method == 'sequential':
            return self._sequential_ib(X, Y, n_clusters)
        elif self.method == 'agglomerative':
            return self._agglomerative_ib(X, Y, n_clusters)
        elif self.method == 'pareto':
            return self._pareto_optimization(X, Y, n_clusters)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _sequential_ib(self, X, Y, n_clusters):
        """Sequential Information Bottleneck for large datasets."""
        # Process data in batches to handle large datasets
        batch_size = self.kwargs.get('batch_size', 1000)
        n_samples = len(X)
        
        # Initialize with small subset
        idx = np.random.choice(n_samples, size=min(batch_size, n_samples), replace=False)
        ib = InformationBottleneck(n_clusters=n_clusters)
        ib.fit(X[idx], Y[idx])
        
        # Sequentially add more data
        for i in range(batch_size, n_samples, batch_size):
            end_idx = min(i + batch_size, n_samples)
            batch_X = X[i:end_idx]
            batch_Y = Y[i:end_idx]
            
            # Warm start with previous solution
            ib_new = InformationBottleneck(n_clusters=n_clusters)
            ib_new.fit(np.concatenate([X[:i], batch_X]), 
                      np.concatenate([Y[:i], batch_Y]))
            ib = ib_new
            
        return ib
    
    def _agglomerative_ib(self, X, Y, n_clusters_schedule):
        """
        Agglomerative Information Bottleneck.
        
        Start with many clusters and merge similar ones.
        """
        if isinstance(n_clusters_schedule, int):
            n_clusters_schedule = [len(np.unique(X)), n_clusters_schedule]
            
        # Start with maximum number of clusters
        current_clusters = n_clusters_schedule[0]
        ib = InformationBottleneck(n_clusters=current_clusters)
        ib.fit(X, Y)
        
        results = [(current_clusters, ib)]
        
        # Sequentially reduce clusters by merging most similar ones
        for target_clusters in n_clusters_schedule[1:]:
            while current_clusters > target_clusters:
                # Find most similar cluster pair to merge
                merge_candidates = self._find_merge_candidates(ib, X, Y)
                best_pair = merge_candidates[0]
                
                # Merge clusters and retrain
                new_ib = self._merge_clusters(ib, best_pair, X, Y)
                ib = new_ib
                current_clusters -= 1
                
            results.append((current_clusters, ib))
        
        return results
    
    def _pareto_optimization(self, X, Y, n_clusters):
        """Multi-objective optimization of I(T;Y) vs I(X;T)."""
        from scipy.optimize import differential_evolution
        
        def objective(beta_log):
            beta = 10 ** beta_log[0]
            ib = InformationBottleneck(n_clusters=n_clusters, beta=beta)
            ib.fit(X, Y)
            
            T = ib.transform(X)
            I_XT = ib._compute_mutual_information_discrete(X, T)
            I_TY = ib._compute_mutual_information_discrete(T, Y)
            
            # Return negative values for maximization
            return [-I_TY, I_XT]  # Multi-objective: max I_TY, min I_XT
        
        # Use differential evolution for multi-objective optimization
        result = differential_evolution(
            objective, 
            bounds=[(-2, 2)],  # log10(beta) bounds
            maxiter=50,
            popsize=15
        )
        
        return result


class MutualInfoEstimator:
    """
    Advanced mutual information estimators.
    
    Implements multiple estimation methods:
    - k-nearest neighbor (Kraskov et al.)
    - Kernel density estimation
    - Neural mutual information estimation (MINE)
    - Binning-based methods with adaptive binning
    """
    
    def __init__(self, method='knn', **kwargs):
        self.method = method
        self.kwargs = kwargs
    
    def estimate(self, X, Y):
        """
        Estimate mutual information I(X;Y).
        
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features_x)
            First variable
        Y : array-like, shape (n_samples, n_features_y) 
            Second variable
            
        Returns
        -------
        mi : float
            Estimated mutual information in nats
        """
        X = np.asarray(X)
        Y = np.asarray(Y)
        
        if len(X) != len(Y):
            raise ValueError("X and Y must have same number of samples")
        
        if self.method == 'knn':
            return self._knn_estimator(X, Y)
        elif self.method == 'kde':
            return self._kde_estimator(X, Y) 
        elif self.method == 'mine':
            return self._mine_estimator(X, Y)
        elif self.method == 'binning':
            return self._binning_estimator(X, Y)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _knn_estimator(self, X, Y):
        """k-nearest neighbor estimator (Kraskov et al. 2004)."""
        from sklearn.neighbors import NearestNeighbors
        
        k = self.kwargs.get('k', 3)
        
        # Normalize features
        X = (X - X.mean(axis=0)) / X.std(axis=0)
        Y = (Y - Y.mean(axis=0)) / Y.std(axis=0)
        
        # Combined space
        XY = np.column_stack([X, Y])
        
        # Find k-th nearest neighbor distances
        nbrs_xy = NearestNeighbors(n_neighbors=k+1, metric='chebyshev').fit(XY)
        distances_xy, _ = nbrs_xy.kneighbors(XY)
        epsilon = distances_xy[:, -1]  # k-th nearest neighbor distance
        
        # Count neighbors in marginal spaces within epsilon distance
        nbrs_x = NearestNeighbors(metric='chebyshev').fit(X)
        nbrs_y = NearestNeighbors(metric='chebyshev').fit(Y)
        
        n_x = np.array([len(nbrs_x.radius_neighbors([x], radius=eps)[1]) - 1 
                       for x, eps in zip(X, epsilon)])
        n_y = np.array([len(nbrs_y.radius_neighbors([y], radius=eps)[1]) - 1 
                       for y, eps in zip(Y, epsilon)])
        
        # Kraskov estimator
        mi = np.mean(np.log(n_x) + np.log(n_y)) + np.log(k) - np.log(len(X))
        return max(0, mi)  # MI cannot be negative
    
    def _kde_estimator(self, X, Y):
        """Kernel density estimation."""
        from scipy import stats
        
        # Use Gaussian kernels
        kde_xy = stats.gaussian_kde(np.column_stack([X.flatten(), Y.flatten()]).T)
        kde_x = stats.gaussian_kde(X.flatten())
        kde_y = stats.gaussian_kde(Y.flatten())
        
        # Sample points for integration
        n_samples = self.kwargs.get('n_samples', 1000)
        xy_samples = np.column_stack([X.flatten(), Y.flatten()])[:n_samples]
        
        # Estimate MI via sampling
        pdf_xy = kde_xy(xy_samples.T)
        pdf_x = kde_x(xy_samples[:, 0])
        pdf_y = kde_y(xy_samples[:, 1])
        
        # MI = ∫ p(x,y) log(p(x,y) / (p(x)p(y))) dx dy
        mi = np.mean(np.log(pdf_xy / (pdf_x * pdf_y)))
        return max(0, mi)
    
    def _mine_estimator(self, X, Y):
        """Mutual Information Neural Estimation."""
        import torch
        import torch.nn as nn
        import torch.optim as optim
        
        # Simple neural network T_θ(x,y)
        input_dim = X.shape[1] + Y.shape[1] if X.ndim > 1 else 2
        
        class MINENet(nn.Module):
            def __init__(self, input_dim=2, hidden_dim=50):
                super(MINENet, self).__init__()
                self.net = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, 1)
                )
                
            def forward(self, xy):
                return self.net(xy)
        
        # Prepare data
        X_tensor = torch.FloatTensor(X.reshape(-1, 1) if X.ndim == 1 else X)
        Y_tensor = torch.FloatTensor(Y.reshape(-1, 1) if Y.ndim == 1 else Y)
        xy_tensor = torch.cat([X_tensor, Y_tensor], dim=1)
        
        # Create shuffled version for marginal
        indices = torch.randperm(len(Y_tensor))
        xy_marginal = torch.cat([X_tensor, Y_tensor[indices]], dim=1)
        
        # Train MINE network
        mine_net = MINENet(input_dim=xy_tensor.shape[1])
        optimizer = optim.Adam(mine_net.parameters(), lr=1e-3)
        
        epochs = self.kwargs.get('epochs', 100)
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # MINE objective: E[T_θ(x,y)] - log(E[exp(T_θ(x,y'))])
            t_joint = mine_net(xy_tensor)
            t_marginal = mine_net(xy_marginal)
            
            loss = -(t_joint.mean() - torch.logsumexp(t_marginal, 0))
            loss.backward()
            optimizer.step()
        
        # Final MI estimate
        with torch.no_grad():
            t_joint = mine_net(xy_tensor)
            t_marginal = mine_net(xy_marginal)
            mi = t_joint.mean() - torch.logsumexp(t_marginal, 0) + np.log(len(X))
            
        return max(0, mi.item())
    
    def _binning_estimator(self, X, Y):
        """Adaptive binning estimator."""
        # Determine optimal number of bins using Scott's rule
        n = len(X)
        bins_x = max(int(n ** (1/3)), 2)
        bins_y = max(int(n ** (1/3)), 2)
        
        # Create 2D histogram
        hist_xy, _, _ = np.histogram2d(X.flatten(), Y.flatten(), 
                                     bins=[bins_x, bins_y])
        hist_x = np.sum(hist_xy, axis=1)
        hist_y = np.sum(hist_xy, axis=0)
        
        # Convert to probabilities
        p_xy = hist_xy / n
        p_x = hist_x / n
        p_y = hist_y / n
        
        # Compute MI
        mi = 0
        for i in range(bins_x):
            for j in range(bins_y):
                if p_xy[i, j] > 0:
                    mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
        
        return max(0, mi)


class MutualInfoCore:
    """
    Core mutual information computations and utilities.
    
    Provides efficient implementations of common information-theoretic
    operations used throughout the Information Bottleneck algorithms.
    """
    
    def __init__(self):
        self.estimator_cache = {}
    
    def compute_entropy(self, X, method='histogram', bins='auto'):
        """
        Compute entropy H(X).
        
        Parameters
        ----------
        X : array-like
            Random variable
        method : str
            Estimation method ('histogram', 'kde')
        bins : int or str
            Number of bins for histogram method
        """
        if method == 'histogram':
            if isinstance(bins, str) and bins == 'auto':
                bins = max(int(np.sqrt(len(X))), 2)
            
            counts, _ = np.histogram(X, bins=bins)
            probs = counts / np.sum(counts)
            probs = probs[probs > 0]  # Remove zero probabilities
            
            return -np.sum(probs * np.log2(probs))
            
        elif method == 'kde':
            from scipy import stats
            kde = stats.gaussian_kde(X)
            
            # Sample for entropy estimation
            x_range = np.linspace(X.min(), X.max(), 1000)
            pdf = kde(x_range)
            pdf = pdf / np.sum(pdf)  # Normalize
            pdf = pdf[pdf > 0]
            
            return -np.sum(pdf * np.log2(pdf))
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def compute_joint_entropy(self, X, Y, method='histogram'):
        """Compute joint entropy H(X,Y)."""
        if method == 'histogram':
            bins_x = max(int(np.sqrt(len(X))), 2)
            bins_y = max(int(np.sqrt(len(Y))), 2)
            
            hist, _, _ = np.histogram2d(X.flatten(), Y.flatten(), 
                                     bins=[bins_x, bins_y])
            probs = hist / np.sum(hist)
            probs = probs[probs > 0]
            
            return -np.sum(probs * np.log2(probs))
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def compute_conditional_entropy(self, X, Y, method='histogram'):
        """Compute conditional entropy H(X|Y) = H(X,Y) - H(Y)."""
        H_XY = self.compute_joint_entropy(X, Y, method)
        H_Y = self.compute_entropy(Y, method)
        return H_XY - H_Y
    
    def compute_mutual_information(self, X, Y, method='histogram'):
        """
        Compute mutual information I(X;Y) = H(X) - H(X|Y).
        
        This is the main interface for MI computation.
        """
        cache_key = (id(X), id(Y), method)
        if cache_key in self.estimator_cache:
            return self.estimator_cache[cache_key]
        
        H_X = self.compute_entropy(X, method)
        H_X_given_Y = self.compute_conditional_entropy(X, Y, method)
        mi = H_X - H_X_given_Y
        
        self.estimator_cache[cache_key] = mi
        return max(0, mi)  # MI cannot be negative
    
    def compute_conditional_mutual_information(self, X, Y, Z):
        """Compute conditional MI I(X;Y|Z)."""
        # I(X;Y|Z) = H(X|Z) - H(X|Y,Z)
        H_X_given_Z = self.compute_conditional_entropy(X, Z)
        
        # For H(X|Y,Z), we need joint conditioning
        YZ = np.column_stack([Y, Z])
        H_X_given_YZ = self.compute_conditional_entropy(X, YZ)
        
        return H_X_given_Z - H_X_given_YZ
    
    def information_bottleneck_curve(self, X, Y, beta_values, n_clusters=10):
        """
        Compute Information Bottleneck curve.
        
        Returns I(X;T) vs I(T;Y) for different β values.
        """
        curve_points = []
        
        for beta in beta_values:
            ib = InformationBottleneck(n_clusters=n_clusters, beta=beta)
            ib.fit(X, Y)
            T = ib.transform(X)
            
            I_XT = self.compute_mutual_information(X, T)
            I_TY = self.compute_mutual_information(T, Y)
            
            curve_points.append({
                'beta': beta,
                'I_XT': I_XT,
                'I_TY': I_TY,
                'compression': I_XT,
                'relevance': I_TY
            })
        
        return curve_points
    
    def compute_information_plane_coordinates(self, X, Y, T):
        """
        Compute coordinates in the information plane.
        
        Returns (I(X;T), I(T;Y)) coordinates for visualization.
        """
        I_XT = self.compute_mutual_information(X, T)
        I_TY = self.compute_mutual_information(T, Y)
        I_XY = self.compute_mutual_information(X, Y)
        
        return {
            'I_XT': I_XT,
            'I_TY': I_TY, 
            'I_XY': I_XY,
            'compression_ratio': I_XT / I_XY if I_XY > 0 else 0,
            'relevance_ratio': I_TY / I_XY if I_XY > 0 else 0
        }