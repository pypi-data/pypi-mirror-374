"""
⚙️ Information Bottleneck Configuration Classes
==============================================

Dataclass-based configuration system for IB algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .enums import IBMethod, InitializationMethod, MutualInfoEstimator, OptimizationMethod


@dataclass
class IBConfig:
    """Base configuration for Information Bottleneck"""
    
    # Algorithm settings
    method: IBMethod = IBMethod.CLASSICAL
    n_clusters: int = 20
    beta: float = 1.0
    
    # Optimization settings
    max_iter: int = 100
    tolerance: float = 1e-6
    optimization_method: OptimizationMethod = OptimizationMethod.ALTERNATING
    
    # Initialization
    initialization: InitializationMethod = InitializationMethod.RANDOM
    random_seed: Optional[int] = None
    
    # Mutual information estimation
    mi_estimator: MutualInfoEstimator = MutualInfoEstimator.AUTO
    
    # Annealing settings
    use_annealing: bool = False
    beta_min: float = 0.01
    beta_max: float = 10.0
    annealing_steps: int = 50
    
    def validate(self) -> bool:
        """Validate configuration parameters"""
        if self.n_clusters <= 0:
            raise ValueError("n_clusters must be positive")
        if self.beta <= 0:
            raise ValueError("beta must be positive")
        if self.max_iter <= 0:
            raise ValueError("max_iter must be positive")
        if not 0 < self.tolerance <= 1:
            raise ValueError("tolerance must be in (0, 1]")
        return True


@dataclass
class NeuralIBConfig:
    """Configuration for Neural Information Bottleneck"""
    
    # Network architecture
    encoder_dims: List[int] = field(default_factory=lambda: [64, 32])
    decoder_dims: List[int] = field(default_factory=lambda: [32, 64])
    latent_dim: int = 16
    
    # IB parameters
    beta: float = 1.0
    kl_weight: float = 1.0
    
    # Training settings
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    
    # Regularization
    dropout_rate: float = 0.1
    use_batch_norm: bool = True
    
    # Backend
    use_pytorch: bool = True
    device: str = "auto"  # "auto", "cpu", "cuda"
    
    def validate(self) -> bool:
        """Validate neural IB configuration"""
        if self.latent_dim <= 0:
            raise ValueError("latent_dim must be positive")
        if len(self.encoder_dims) == 0:
            raise ValueError("encoder_dims cannot be empty")
        if len(self.decoder_dims) == 0:
            raise ValueError("decoder_dims cannot be empty")
        if not 0 <= self.dropout_rate < 1:
            raise ValueError("dropout_rate must be in [0, 1)")
        return True


@dataclass
class DeepIBConfig:
    """Configuration for Deep Information Bottleneck"""
    
    # Network architecture
    encoder_layers: List[int] = field(default_factory=lambda: [128, 64, 32])
    decoder_layers: List[int] = field(default_factory=lambda: [32, 64, 128])
    latent_dim: int = 16
    
    # IB parameters
    beta: float = 1.0
    kl_weight: float = 1.0
    
    # Training settings
    epochs: int = 200
    batch_size: int = 64
    learning_rate: float = 0.001
    validation_split: float = 0.2
    
    # Network settings
    activation: str = "relu"
    dropout_rate: float = 0.2
    use_batch_norm: bool = True
    
    # Loss settings
    reconstruction_loss: str = "mse"  # "mse", "cross_entropy"
    
    def validate(self) -> bool:
        """Validate deep IB configuration"""
        if self.latent_dim <= 0:
            raise ValueError("latent_dim must be positive")
        if not 0 < self.validation_split < 1:
            raise ValueError("validation_split must be in (0, 1)")
        if not 0 <= self.dropout_rate < 1:
            raise ValueError("dropout_rate must be in [0, 1)")
        return True


@dataclass
class EvaluationConfig:
    """Configuration for IB evaluation and metrics"""
    
    # Information metrics
    compute_mutual_info: bool = True
    mi_estimation_method: MutualInfoEstimator = MutualInfoEstimator.KSG
    
    # Visualization
    create_info_plots: bool = False
    plot_convergence: bool = True
    save_plots: bool = False
    
    # Performance metrics
    compute_classification_metrics: bool = True
    compute_clustering_metrics: bool = False
    
    # Cross-validation
    use_cross_validation: bool = False
    cv_folds: int = 5
    
    # Output settings
    verbose: bool = True
    save_results: bool = True
    results_dir: str = "./ib_results"


# Factory functions for common configurations

def create_discrete_ib_config(
    n_clusters: int = 20,
    beta: float = 1.0,
    use_annealing: bool = True,
    **kwargs
) -> IBConfig:
    """Create configuration for discrete/classical IB"""
    
    return IBConfig(
        method=IBMethod.CLASSICAL,
        n_clusters=n_clusters,
        beta=beta,
        use_annealing=use_annealing,
        mi_estimator=MutualInfoEstimator.DISCRETE,
        **kwargs
    )


def create_neural_ib_config(
    latent_dim: int = 16,
    beta: float = 1.0,
    encoder_dims: Optional[List[int]] = None,
    **kwargs
) -> NeuralIBConfig:
    """Create configuration for neural IB"""
    
    if encoder_dims is None:
        encoder_dims = [64, 32]
    
    decoder_dims = encoder_dims[::-1]  # Symmetric architecture
    
    return NeuralIBConfig(
        encoder_dims=encoder_dims,
        decoder_dims=decoder_dims,
        latent_dim=latent_dim,
        beta=beta,
        **kwargs
    )


def create_deep_ib_config(
    latent_dim: int = 32,
    beta: float = 1.0,
    epochs: int = 200,
    **kwargs
) -> DeepIBConfig:
    """Create configuration for deep IB"""
    
    return DeepIBConfig(
        latent_dim=latent_dim,
        beta=beta,
        epochs=epochs,
        **kwargs
    )