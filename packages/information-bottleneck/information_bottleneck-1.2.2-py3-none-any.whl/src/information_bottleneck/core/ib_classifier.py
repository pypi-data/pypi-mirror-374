"""
📊 Information Bottleneck Classifier
===================================

Classification wrapper using Information Bottleneck for
optimal feature extraction and prediction.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, Optional, Any, Union
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from .classical_ib import InformationBottleneck
from .neural_ib import NeuralInformationBottleneck


class InformationBottleneckClassifier(BaseEstimator, ClassifierMixin):
    """
    Information Bottleneck-based classifier
    
    Combines optimal representation learning with classification
    using the Information Bottleneck principle.
    """
    
    def __init__(
        self,
        n_clusters: int = 20,
        beta: float = 1.0,
        max_iter: int = 100,
        tolerance: float = 1e-6,
        ib_type: str = 'classical',
        random_seed: Optional[int] = None
    ):
        """
        Initialize IB Classifier
        
        Args:
            n_clusters: Number of clusters for classical IB
            beta: Information trade-off parameter
            max_iter: Maximum optimization iterations
            tolerance: Convergence tolerance
            ib_type: 'classical' or 'neural' IB implementation
            random_seed: Random seed for reproducibility
        """
        
        self.n_clusters = n_clusters
        self.beta = beta
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.ib_type = ib_type
        self.random_seed = random_seed
        
        # Will be initialized in fit
        self.ib_model_ = None
        self.label_encoder_ = None
        self.classes_ = None
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'InformationBottleneckClassifier':
        """
        Fit Information Bottleneck classifier
        
        Args:
            X: Training features
            y: Training labels
            
        Returns:
            self: Fitted classifier
        """
        
        # Encode labels
        self.label_encoder_ = LabelEncoder()
        y_encoded = self.label_encoder_.fit_transform(y)
        self.classes_ = self.label_encoder_.classes_
        
        # Initialize appropriate IB model
        if self.ib_type == 'classical':
            self.ib_model_ = InformationBottleneck(
                n_clusters=self.n_clusters,
                beta=self.beta,
                max_iter=self.max_iter,
                tolerance=self.tolerance,
                random_seed=self.random_seed
            )
        elif self.ib_type == 'neural':
            # Default neural architecture
            input_dim = X.shape[1] if len(X.shape) > 1 else 1
            output_dim = len(self.classes_)
            
            encoder_dims = [input_dim, 64, 32]
            decoder_dims = [self.n_clusters, 32, output_dim]
            
            self.ib_model_ = NeuralInformationBottleneck(
                encoder_dims=encoder_dims,
                decoder_dims=decoder_dims,
                latent_dim=self.n_clusters,
                beta=self.beta
            )
        else:
            raise ValueError(f"Unknown ib_type: {self.ib_type}")
        
        # Fit IB model
        self.ib_model_.fit(X, y_encoded)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using IB classifier"""
        if self.ib_model_ is None:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        if self.ib_type == 'classical':
            y_pred_encoded = self.ib_model_.predict(X)
        else:  # neural
            y_pred_proba = self.ib_model_.predict(X)
            y_pred_encoded = np.argmax(y_pred_proba, axis=1)
        
        return self.label_encoder_.inverse_transform(y_pred_encoded)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities using IB classifier"""
        if self.ib_model_ is None:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        if self.ib_type == 'classical':
            return self.ib_model_.predict_proba(X)
        else:  # neural
            return self.ib_model_.predict(X)
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data to IB representation"""
        if self.ib_model_ is None:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        return self.ib_model_.transform(X)
    
    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Fit classifier and transform data"""
        return self.fit(X, y).transform(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute accuracy score"""
        y_pred = self.predict(X)
        return np.mean(y == y_pred)
    
    def get_information_statistics(self) -> Dict[str, Any]:
        """Get information-theoretic statistics"""
        if self.ib_model_ is None:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        base_stats = {
            'n_clusters': self.n_clusters,
            'beta': self.beta,
            'ib_type': self.ib_type,
            'n_classes': len(self.classes_),
            'classes': self.classes_
        }
        
        if hasattr(self.ib_model_, 'get_information_statistics'):
            model_stats = self.ib_model_.get_information_statistics()
            base_stats.update(model_stats)
        
        if hasattr(self.ib_model_, 'training_history'):
            base_stats['training_history'] = self.ib_model_.training_history
        
        return base_stats