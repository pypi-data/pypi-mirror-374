"""
📊 Metrics and Evaluation Utilities for Information Bottleneck
=============================================================

Performance metrics and evaluation functions for IB algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    mean_squared_error, r2_score, mean_absolute_error,
    adjusted_rand_score, normalized_mutual_info_score,
    silhouette_score, calinski_harabasz_score
)
from .math_utils import compute_mutual_information_discrete, entropy_discrete


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray] = None,
    average: str = 'weighted'
) -> Dict[str, Any]:
    """
    Compute comprehensive classification metrics
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_proba: Predicted probabilities (optional)
        average: Averaging strategy for multi-class metrics
        
    Returns:
        Dictionary of classification metrics
    """
    
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, average=average, zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, average=average, zero_division=0)
    metrics['f1_score'] = f1_score(y_true, y_pred, average=average, zero_division=0)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics['confusion_matrix'] = cm
    
    # Per-class metrics if multi-class
    n_classes = len(np.unique(y_true))
    if n_classes > 2:
        metrics['precision_per_class'] = precision_score(y_true, y_pred, average=None, zero_division=0)
        metrics['recall_per_class'] = recall_score(y_true, y_pred, average=None, zero_division=0)
        metrics['f1_per_class'] = f1_score(y_true, y_pred, average=None, zero_division=0)
    
    # Additional metrics if probabilities available
    if y_proba is not None:
        try:
            from sklearn.metrics import log_loss, roc_auc_score
            
            metrics['log_loss'] = log_loss(y_true, y_proba)
            
            # ROC AUC for binary or multi-class
            if n_classes == 2:
                metrics['roc_auc'] = roc_auc_score(y_true, y_proba[:, 1])
            elif n_classes > 2:
                metrics['roc_auc_ovr'] = roc_auc_score(y_true, y_proba, multi_class='ovr')
                metrics['roc_auc_ovo'] = roc_auc_score(y_true, y_proba, multi_class='ovo')
        except:
            pass  # Skip if metrics can't be computed
    
    # Summary statistics
    metrics['n_samples'] = len(y_true)
    metrics['n_classes'] = n_classes
    metrics['class_distribution'] = np.bincount(y_true) / len(y_true)
    
    return metrics


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, Any]:
    """
    Compute comprehensive regression metrics
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary of regression metrics
    """
    
    metrics = {}
    
    # Basic metrics
    metrics['mse'] = mean_squared_error(y_true, y_pred)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['mae'] = mean_absolute_error(y_true, y_pred)
    metrics['r2_score'] = r2_score(y_true, y_pred)
    
    # Additional metrics
    residuals = y_true - y_pred
    metrics['mean_residual'] = np.mean(residuals)
    metrics['std_residual'] = np.std(residuals)
    
    # Percentage metrics
    non_zero_mask = y_true != 0
    if np.any(non_zero_mask):
        mape = np.mean(np.abs(residuals[non_zero_mask] / y_true[non_zero_mask])) * 100
        metrics['mape'] = mape
    
    # Explained variance
    metrics['explained_variance'] = 1 - np.var(residuals) / np.var(y_true)
    
    return metrics


def compute_clustering_metrics(
    X: np.ndarray,
    labels_true: Optional[np.ndarray] = None,
    labels_pred: Optional[np.ndarray] = None,
    distance_threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Compute clustering evaluation metrics
    
    Args:
        X: Data points
        labels_true: True cluster labels (if available)
        labels_pred: Predicted cluster labels
        distance_threshold: Threshold for silhouette score computation
        
    Returns:
        Dictionary of clustering metrics
    """
    
    metrics = {}
    
    if labels_pred is not None:
        # Internal metrics (don't require ground truth)
        try:
            metrics['silhouette_score'] = silhouette_score(X, labels_pred)
        except:
            metrics['silhouette_score'] = None
            
        try:
            metrics['calinski_harabasz_score'] = calinski_harabasz_score(X, labels_pred)
        except:
            metrics['calinski_harabasz_score'] = None
        
        # Cluster statistics
        unique_labels = np.unique(labels_pred)
        metrics['n_clusters'] = len(unique_labels)
        metrics['cluster_sizes'] = [np.sum(labels_pred == label) for label in unique_labels]
        metrics['cluster_size_std'] = np.std(metrics['cluster_sizes'])
        
        # External metrics (require ground truth)
        if labels_true is not None:
            metrics['adjusted_rand_score'] = adjusted_rand_score(labels_true, labels_pred)
            metrics['normalized_mutual_info'] = normalized_mutual_info_score(labels_true, labels_pred)
            
            # Purity and inverse purity
            purity, inverse_purity = compute_purity_metrics(labels_true, labels_pred)
            metrics['purity'] = purity
            metrics['inverse_purity'] = inverse_purity
            metrics['f_measure'] = 2 * purity * inverse_purity / (purity + inverse_purity) if (purity + inverse_purity) > 0 else 0
    
    return metrics


def compute_purity_metrics(
    labels_true: np.ndarray,
    labels_pred: np.ndarray
) -> Tuple[float, float]:
    """
    Compute purity and inverse purity for clustering
    
    Args:
        labels_true: True labels
        labels_pred: Predicted labels
        
    Returns:
        Purity and inverse purity scores
    """
    
    # Purity: fraction of correctly clustered points
    n_samples = len(labels_true)
    
    purity_sum = 0
    for cluster in np.unique(labels_pred):
        cluster_mask = labels_pred == cluster
        if np.any(cluster_mask):
            # Most common true label in this cluster
            true_labels_in_cluster = labels_true[cluster_mask]
            most_common = np.bincount(true_labels_in_cluster).max()
            purity_sum += most_common
    
    purity = purity_sum / n_samples
    
    # Inverse purity: average precision of clusters
    inverse_purity_sum = 0
    for true_label in np.unique(labels_true):
        true_mask = labels_true == true_label
        if np.any(true_mask):
            # Most common predicted label for this true class
            pred_labels_for_true = labels_pred[true_mask]
            most_common = np.bincount(pred_labels_for_true).max()
            inverse_purity_sum += most_common
    
    inverse_purity = inverse_purity_sum / n_samples
    
    return purity, inverse_purity


def compute_information_theoretic_metrics(
    X: np.ndarray,
    Y: np.ndarray,
    Z: Optional[np.ndarray] = None,
    method: str = 'discrete'
) -> Dict[str, float]:
    """
    Compute information-theoretic metrics for IB evaluation
    
    Args:
        X: Input features
        Y: Target values
        Z: Compressed representation (optional)
        method: MI estimation method
        
    Returns:
        Dictionary of information metrics
    """
    
    metrics = {}
    
    # Convert to discrete if needed
    if method == 'discrete':
        from .data_utils import discretize_data
        
        if not _is_discrete(X):
            X_discrete = discretize_data(X.ravel(), n_bins='auto')
        else:
            X_discrete = X.ravel()
            
        if not _is_discrete(Y):
            Y_discrete = discretize_data(Y.ravel(), n_bins='auto')
        else:
            Y_discrete = Y.ravel()
        
        # Compute I(X;Y)
        joint_xy = _compute_joint_histogram(X_discrete, Y_discrete)
        metrics['mutual_info_XY'] = compute_mutual_information_discrete(joint_xy)
        
        # Compute individual entropies
        metrics['entropy_X'] = entropy_discrete(np.bincount(X_discrete))
        metrics['entropy_Y'] = entropy_discrete(np.bincount(Y_discrete))
        
        # If compressed representation available
        if Z is not None:
            if not _is_discrete(Z):
                Z_discrete = discretize_data(Z.ravel(), n_bins='auto')
            else:
                Z_discrete = Z.ravel()
            
            # Compute I(X;Z) and I(Z;Y)
            joint_xz = _compute_joint_histogram(X_discrete, Z_discrete)
            joint_zy = _compute_joint_histogram(Z_discrete, Y_discrete)
            
            metrics['mutual_info_XZ'] = compute_mutual_information_discrete(joint_xz)
            metrics['mutual_info_ZY'] = compute_mutual_information_discrete(joint_zy)
            metrics['entropy_Z'] = entropy_discrete(np.bincount(Z_discrete))
            
            # Information bottleneck metrics
            compression_ratio = metrics['mutual_info_XZ'] / metrics['entropy_X'] if metrics['entropy_X'] > 0 else 0
            prediction_ratio = metrics['mutual_info_ZY'] / metrics['entropy_Y'] if metrics['entropy_Y'] > 0 else 0
            
            metrics['compression_ratio'] = compression_ratio
            metrics['prediction_ratio'] = prediction_ratio
            metrics['ib_objective'] = metrics['mutual_info_XZ'] - metrics['mutual_info_ZY']  # Simplified, without beta
    
    return metrics


def _is_discrete(data: np.ndarray, threshold: float = 0.1) -> bool:
    """Check if data appears to be discrete"""
    n_unique = len(np.unique(data))
    n_samples = len(data)
    return n_unique < n_samples * threshold and n_unique < 50


def _compute_joint_histogram(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Compute joint histogram for discrete data"""
    x_vals = np.unique(X)
    y_vals = np.unique(Y)
    
    joint_hist = np.zeros((len(x_vals), len(y_vals)))
    
    for i, x_val in enumerate(x_vals):
        for j, y_val in enumerate(y_vals):
            joint_hist[i, j] = np.sum((X == x_val) & (Y == y_val))
    
    return joint_hist


def evaluate_ib_performance(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    Y_pred: Optional[np.ndarray] = None,
    Y_proba: Optional[np.ndarray] = None,
    task_type: str = 'classification'
) -> Dict[str, Any]:
    """
    Comprehensive evaluation of Information Bottleneck performance
    
    Args:
        X: Original features
        Y: True targets
        Z: IB representation
        Y_pred: Predicted targets
        Y_proba: Predicted probabilities
        task_type: 'classification' or 'regression'
        
    Returns:
        Complete evaluation results
    """
    
    results = {
        'information_metrics': compute_information_theoretic_metrics(X, Y, Z),
        'representation_metrics': {
            'compression_dim': Z.shape[1] if len(Z.shape) > 1 else 1,
            'original_dim': X.shape[1] if len(X.shape) > 1 else 1,
            'dimensionality_reduction': (X.shape[1] if len(X.shape) > 1 else 1) / (Z.shape[1] if len(Z.shape) > 1 else 1)
        }
    }
    
    # Task-specific metrics
    if Y_pred is not None:
        if task_type == 'classification':
            results['task_metrics'] = compute_classification_metrics(Y, Y_pred, Y_proba)
        elif task_type == 'regression':
            results['task_metrics'] = compute_regression_metrics(Y, Y_pred)
    
    # Clustering metrics for representation
    if len(Z.shape) > 1 and Z.shape[1] > 1:
        # Use k-means on representation
        try:
            from sklearn.cluster import KMeans
            n_clusters = min(10, len(np.unique(Y)))
            kmeans = KMeans(n_clusters=n_clusters, random_state=0)
            Z_clusters = kmeans.fit_predict(Z)
            
            results['clustering_metrics'] = compute_clustering_metrics(
                Z, labels_true=Y if task_type == 'classification' else None,
                labels_pred=Z_clusters
            )
        except:
            pass
    
    return results