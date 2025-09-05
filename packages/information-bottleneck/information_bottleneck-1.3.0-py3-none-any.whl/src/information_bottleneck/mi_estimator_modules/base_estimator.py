"""
🧠 Base MI Estimator Classes
============================

Base classes and data structures for mutual information estimation.

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Multiple MI estimation methods from research literature
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MIEstimationResult:
    """
    Result container for mutual information estimation.
    
    Contains the MI value along with metadata about the estimation process.
    """
    mi_value: float
    method: str
    n_samples: int
    computation_time: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMIEstimator(ABC):
    """
    Abstract base class for mutual information estimators.
    
    Provides common interface and validation for all MI estimation methods.
    """
    
    @abstractmethod
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> MIEstimationResult:
        """
        Estimate mutual information between X and Y.
        
        Args:
            X: Input data array of shape (n_samples, n_features_x)
            Y: Target data array of shape (n_samples, n_features_y) 
            
        Returns:
            MIEstimationResult with MI value and metadata
        """
        pass
    
    def _validate_input(self, X: np.ndarray, Y: np.ndarray) -> None:
        """Validate input arrays for MI estimation."""
        if not isinstance(X, np.ndarray) or not isinstance(Y, np.ndarray):
            raise TypeError("X and Y must be numpy arrays")
            
        if X.shape[0] != Y.shape[0]:
            raise ValueError(f"X and Y must have same number of samples: {X.shape[0]} vs {Y.shape[0]}")
            
        if X.shape[0] < 2:
            raise ValueError("Need at least 2 samples for MI estimation")
            
        if np.any(np.isnan(X)) or np.any(np.isnan(Y)):
            raise ValueError("X and Y cannot contain NaN values")
            
        if np.any(np.isinf(X)) or np.any(np.isinf(Y)):
            raise ValueError("X and Y cannot contain infinite values")
    
    def _preprocess_data(self, X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Preprocess data for MI estimation."""
        # Ensure 2D arrays
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
            
        return X, Y