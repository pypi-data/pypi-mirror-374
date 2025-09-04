"""
📊 Data Utilities for Information Bottleneck
===========================================

Data preprocessing and validation utilities for IB algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.datasets import make_classification, make_regression, make_blobs
import warnings
warnings.filterwarnings('ignore')


def normalize_data(
    X: np.ndarray,
    method: str = 'standard',
    return_scaler: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, Any]]:
    """
    Normalize data using various methods
    
    Args:
        X: Input data
        method: Normalization method ('standard', 'minmax', 'robust')
        return_scaler: Whether to return the fitted scaler
        
    Returns:
        Normalized data, optionally with fitted scaler
    """
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'robust':
        from sklearn.preprocessing import RobustScaler
        scaler = RobustScaler()
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    X_normalized = scaler.fit_transform(X)
    
    if return_scaler:
        return X_normalized, scaler
    else:
        return X_normalized


def discretize_data(
    X: np.ndarray,
    n_bins: Union[int, str] = 'auto',
    strategy: str = 'uniform',
    return_bin_edges: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Discretize continuous data into bins
    
    Args:
        X: Input data
        n_bins: Number of bins or 'auto' for automatic selection
        strategy: Binning strategy ('uniform', 'quantile', 'kmeans')
        return_bin_edges: Whether to return bin edges
        
    Returns:
        Discretized data, optionally with bin edges
    """
    
    if n_bins == 'auto':
        # Use Freedman-Diaconis rule
        q75, q25 = np.percentile(X, [75, 25])
        iqr = q75 - q25
        if iqr == 0:
            n_bins = int(np.sqrt(len(X)))
        else:
            h = 2 * iqr / (len(X) ** (1/3))
            n_bins = max(5, min(50, int((np.max(X) - np.min(X)) / h)))
    
    if strategy == 'uniform':
        bin_edges = np.linspace(np.min(X), np.max(X), n_bins + 1)
        X_discretized = np.digitize(X, bin_edges[1:-1])
        
    elif strategy == 'quantile':
        quantiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.percentile(X, quantiles)
        X_discretized = np.digitize(X, bin_edges[1:-1])
        
    elif strategy == 'kmeans':
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_bins, random_state=0)
        X_discretized = kmeans.fit_predict(X.reshape(-1, 1))
        bin_edges = np.sort(kmeans.cluster_centers_.flatten())
        
    else:
        raise ValueError(f"Unknown discretization strategy: {strategy}")
    
    # Ensure valid range
    X_discretized = np.clip(X_discretized, 0, n_bins - 1)
    
    if return_bin_edges:
        return X_discretized, bin_edges
    else:
        return X_discretized


def create_synthetic_ib_data(
    data_type: str = 'classification',
    n_samples: int = 1000,
    n_features: int = 10,
    n_informative: int = 5,
    n_clusters: int = 3,
    noise: float = 0.1,
    random_state: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic data for IB testing
    
    Args:
        data_type: Type of data ('classification', 'regression', 'clustering')
        n_samples: Number of samples
        n_features: Number of features
        n_informative: Number of informative features
        n_clusters: Number of clusters (for classification/clustering)
        noise: Noise level
        random_state: Random seed
        
    Returns:
        Features (X) and targets (y)
    """
    
    if data_type == 'classification':
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            n_classes=n_clusters,
            n_redundant=0,
            n_clusters_per_class=1,
            class_sep=1.0,
            random_state=random_state
        )
        
    elif data_type == 'regression':
        X, y = make_regression(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            noise=noise * 10,
            random_state=random_state
        )
        
    elif data_type == 'clustering':
        X, y = make_blobs(
            n_samples=n_samples,
            centers=n_clusters,
            n_features=n_features,
            cluster_std=noise * 10,
            random_state=random_state
        )
        
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    # Add some noise to features if specified
    if noise > 0 and data_type != 'regression':
        X += np.random.normal(0, noise, X.shape)
    
    return X, y


def validate_ib_inputs(
    X: np.ndarray,
    Y: np.ndarray,
    check_shapes: bool = True,
    check_types: bool = True,
    min_samples: int = 10
) -> Dict[str, Any]:
    """
    Validate inputs for Information Bottleneck algorithms
    
    Args:
        X: Input features
        Y: Target values
        check_shapes: Whether to validate shapes
        check_types: Whether to validate data types
        min_samples: Minimum number of samples required
        
    Returns:
        Validation results dictionary
    """
    
    results = {
        'is_valid': True,
        'warnings': [],
        'errors': [],
        'info': {}
    }
    
    # Basic existence check
    if X is None or Y is None:
        results['errors'].append("X and Y cannot be None")
        results['is_valid'] = False
        return results
    
    # Convert to numpy arrays
    X = np.asarray(X)
    Y = np.asarray(Y)
    
    # Shape validation
    if check_shapes:
        if len(X) != len(Y):
            results['errors'].append(f"X and Y must have same length: {len(X)} vs {len(Y)}")
            results['is_valid'] = False
        
        if len(X) < min_samples:
            results['errors'].append(f"Need at least {min_samples} samples, got {len(X)}")
            results['is_valid'] = False
        
        if len(X.shape) > 2:
            results['warnings'].append("X has more than 2 dimensions, may need reshaping")
    
    # Data type validation
    if check_types:
        # Check for NaN values
        if np.any(np.isnan(X)):
            results['errors'].append("X contains NaN values")
            results['is_valid'] = False
            
        if np.any(np.isnan(Y)):
            results['errors'].append("Y contains NaN values")
            results['is_valid'] = False
        
        # Check for infinite values
        if np.any(np.isinf(X)):
            results['errors'].append("X contains infinite values")
            results['is_valid'] = False
            
        if np.any(np.isinf(Y)):
            results['errors'].append("Y contains infinite values")
            results['is_valid'] = False
    
    # Information about data
    results['info'] = {
        'n_samples': len(X),
        'n_features': X.shape[1] if len(X.shape) > 1 else 1,
        'X_dtype': X.dtype,
        'Y_dtype': Y.dtype,
        'X_range': (np.min(X), np.max(X)) if results['is_valid'] else None,
        'Y_unique_values': len(np.unique(Y)) if results['is_valid'] else None,
        'Y_is_categorical': len(np.unique(Y)) < len(Y) * 0.1 if results['is_valid'] else None
    }
    
    # Additional warnings
    if results['is_valid']:
        if results['info']['Y_unique_values'] == 1:
            results['warnings'].append("Y has only one unique value")
            
        if results['info']['n_features'] > results['info']['n_samples']:
            results['warnings'].append("More features than samples (n_features > n_samples)")
        
        if results['info']['X_range'][1] - results['info']['X_range'][0] > 1000:
            results['warnings'].append("X has very large range, consider normalization")
    
    return results


def encode_categorical_data(
    data: np.ndarray,
    return_encoder: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, LabelEncoder]]:
    """
    Encode categorical data to numeric labels
    
    Args:
        data: Categorical data
        return_encoder: Whether to return the fitted encoder
        
    Returns:
        Encoded data, optionally with fitted encoder
    """
    
    encoder = LabelEncoder()
    
    # Handle different input types
    if isinstance(data[0], str):
        encoded_data = encoder.fit_transform(data)
    elif isinstance(data[0], (list, tuple)):
        # Convert complex objects to strings first
        str_data = [str(item) for item in data]
        encoded_data = encoder.fit_transform(str_data)
    else:
        # Assume already numeric
        encoded_data = np.asarray(data, dtype=int)
        encoder = None
    
    if return_encoder:
        return encoded_data, encoder
    else:
        return encoded_data


def split_data_for_ib(
    X: np.ndarray,
    Y: np.ndarray,
    test_size: float = 0.2,
    random_state: Optional[int] = None,
    stratify: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data for IB training and evaluation
    
    Args:
        X: Features
        Y: Targets
        test_size: Fraction of data for testing
        random_state: Random seed
        stratify: Whether to stratify split (for classification)
        
    Returns:
        X_train, X_test, Y_train, Y_test
    """
    
    from sklearn.model_selection import train_test_split
    
    # Determine if we should stratify
    y_unique = len(np.unique(Y))
    is_classification = y_unique < len(Y) * 0.1 and y_unique < 50
    
    if stratify and is_classification:
        return train_test_split(
            X, Y, test_size=test_size, 
            random_state=random_state, 
            stratify=Y
        )
    else:
        return train_test_split(
            X, Y, test_size=test_size,
            random_state=random_state
        )