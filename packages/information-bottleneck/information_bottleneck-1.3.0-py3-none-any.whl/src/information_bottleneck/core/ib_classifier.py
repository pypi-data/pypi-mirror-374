"""
🔍 Information Bottleneck Classifier - Smart Feature Learning System
===================================================================

🎯 ELI5 EXPLANATION:
==================
Think of the Information Bottleneck Classifier like a brilliant detective who solves cases by focusing only on the most important clues!

Imagine you're a detective with thousands of pieces of evidence for a case. Most evidence is noise, but some clues are golden - they tell you everything you need to know to solve the case perfectly. The Information Bottleneck Classifier is like having the world's best detective who:

1. 🔍 **Evidence Filtering**: Looks at all available information about your data
2. 🎯 **Clue Selection**: Finds the absolute minimum information needed for perfect classification
3. 🧠 **Smart Compression**: Throws away irrelevant noise, keeps only what matters
4. ⚖️  **Perfect Balance**: Maximum accuracy with minimal information complexity!

Just like a detective who can solve any case with just the right clues, this classifier finds the perfect "information bottleneck" - the smallest set of features that still gives perfect predictions!

🔬 RESEARCH FOUNDATION:
======================
Core information theory from computational learning pioneers:
- **Tishby et al. (2000)**: "The information bottleneck method" - Original breakthrough theory
- **Alemi et al. (2016)**: "Deep variational information bottleneck" - Neural network extensions
- **Shwartz-Ziv & Tishby (2017)**: "Opening the black box of deep neural networks" - DNN analysis
- **Kolchinsky et al. (2019)**: "Nonlinear information bottleneck" - Advanced formulations

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Core Information Bottleneck Principle:**
min I(X,T) - βI(T,Y)

**Classification Objective:**
Find representation T that minimizes input complexity I(X,T) 
while maximizing predictive power I(T,Y)

**Optimal Trade-off:**
β parameter controls compression-prediction balance
β → 0: Maximum compression (lose all information)
β → ∞: No compression (keep everything)

📊 IB CLASSIFIER ARCHITECTURE VISUALIZATION:
==========================================
```
🔍 INFORMATION BOTTLENECK CLASSIFIER 🔍

Raw Features               Information Bottleneck            Perfect Classification
┌─────────────────┐       ┌──────────────────────────────┐   ┌─────────────────┐
│ 📊 Input X      │       │                              │   │ 🎯 PREDICTIONS  │
│ [1000 features] │ ───→  │  🔍 BOTTLENECK T:            │ → │ Class A: 95%    │
│ Noisy, complex  │       │  • Compress: min I(X,T)     │   │ Class B: 5%     │
└─────────────────┘       │  • Preserve: max I(T,Y)     │   │                 │
                          │                              │   │ 🎲 CERTAINTY    │
┌─────────────────┐       │  ⚖️  TRADE-OFF PARAMETER β:  │   │ High confidence │
│ 🏷️ Labels Y      │ ───→  │  Controls compression level  │   │ Low entropy     │
│ [Class labels]  │       │                              │   │                 │
└─────────────────┘       │  🧠 LEARNING METHODS:        │   │ 🔬 EFFICIENCY   │
                          │  • Classical IB clustering   │   │ Minimal info    │
┌─────────────────┐       │  • Neural network variational│   │ Maximum accuracy│
│ 🎛️ Hyperparams   │ ───→  │  • Optimal representation   │   │                 │
│ β, clusters, etc│       │                              │   │ ✨ GENERALIZE   │
└─────────────────┘       └──────────────────────────────┘   │ Robust to noise │
                                         │                    │ Finds true      │
                                         ▼                    │ patterns        │
                              RESULT: Optimal information     └─────────────────┘
                                     compression for ML! 🚀
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Naftali Tishby's foundational information bottleneck theory
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