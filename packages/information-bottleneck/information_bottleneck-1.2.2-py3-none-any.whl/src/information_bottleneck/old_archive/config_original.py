"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Configuration Classes - UNIFIED IMPLEMENTATION
==================================================================

This module consolidates all configuration classes and enums for the 
Information Bottleneck method from the scattered structure.

Consolidated from:
- ib_config.py (full configuration classes)
- evaluation_metrics.py (EvaluationConfig class)
- Various enum definitions scattered across modules

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any, Callable
import numpy as np

# ============================================================================
# ENUMS - All Information Bottleneck Method Options
# ============================================================================

class IBMethod(Enum):
    """Available Information Bottleneck methods."""
    DISCRETE = "discrete"  # Classical discrete IB algorithm (Tishby et al.)
    NEURAL = "neural"  # Neural network-based IB (Alemi et al.)
    CONTINUOUS = "continuous"  # Continuous variable approach
    VARIATIONAL = "variational"  # Variational IB (Alemi et al.)
    AGGLOMERATIVE = "agglomerative"  # Agglomerative IB (Slonim et al.)
    SEQUENTIAL = "sequential"  # Sequential IB for large data


class MutualInfoEstimator(Enum):
    """Mutual information estimation methods."""
    KSG = "ksg"  # Kraskov-Stögbauer-Grassberger estimator
    KNN = "knn"  # k-nearest neighbor based
    BINNING = "binning"  # Histogram-based estimation
    KERNEL = "kernel"  # Kernel density estimation
    ENSEMBLE = "ensemble"  # Ensemble of estimators
    ADAPTIVE = "adaptive"  # Adaptive method selection
    COPULA = "copula"  # Copula-based estimation
    MINE = "mine"  # Mutual Information Neural Estimation
    INFONCE = "infonce"  # InfoNCE estimator
    GAUSSIAN = "gaussian"  # Gaussian assumption


class InitializationMethod(Enum):
    """Initialization strategies for IB algorithm."""
    RANDOM = "random"  # Random cluster assignment
    KMEANS = "kmeans"  # K-means clustering initialization
    KMEANS_PLUS_PLUS = "kmeans++"  # K-means++ initialization
    MUTUAL_INFO = "mutual_info"  # Mutual information guided init
    HIERARCHICAL = "hierarchical"  # Hierarchical clustering
    SPECTRAL = "spectral"  # Spectral clustering
    GAUSSIAN_MIXTURE = "gaussian_mixture"  # Gaussian mixture model
    

class OptimizationMethod(Enum):
    """Optimization algorithms for Information Bottleneck."""
    BLAHUT_ARIMOTO = "blahut_arimoto"  # Original iterative algorithm
    NATURAL_GRADIENT = "natural_gradient"  # Natural gradient ascent
    DETERMINISTIC_ANNEALING = "deterministic_annealing"  # Annealing approach
    TEMPERATURE_SCALED = "temperature_scaled"  # Temperature scaling
    ALTERNATE_MINIMIZATION = "alternate_minimization"  # Alternating optimization
    GRADIENT_DESCENT = "gradient_descent"  # Standard gradient descent
    

class EncoderUpdateMethod(Enum):
    """Methods for updating encoder distribution p(t|x)."""
    BLAHUT_ARIMOTO = "blahut_arimoto"  # BA update rule
    NATURAL_GRADIENT = "natural_gradient"  # Natural gradient
    TEMPERATURE_SCALED = "temperature_scaled"  # Temperature scaling
    DETERMINISTIC_ANNEALING = "deterministic_annealing"  # Annealing
    SOFT_ASSIGNMENT = "soft_assignment"  # Soft cluster assignment


class DecoderUpdateMethod(Enum):
    """Methods for updating decoder distribution p(y|t)."""
    BAYES_RULE = "bayes_rule"  # Exact Bayes rule update
    EM = "em"  # Expectation-Maximization
    REGULARIZED = "regularized"  # Regularized estimation
    MAXIMUM_LIKELIHOOD = "maximum_likelihood"  # ML estimation
    MAP = "map"  # Maximum a posteriori


class ConvergenceMetric(Enum):
    """Metrics for checking convergence."""
    OBJECTIVE_CHANGE = "objective_change"  # Change in IB objective
    ASSIGNMENT_CHANGE = "assignment_change"  # Change in cluster assignments
    MUTUAL_INFO_CHANGE = "mutual_info_change"  # Change in MI values
    PARAMETER_CHANGE = "parameter_change"  # Change in parameters
    COMBINED = "combined"  # Multiple criteria


class AnnealingSchedule(Enum):
    """Annealing schedules for β parameter."""
    LINEAR = "linear"  # Linear increase: β(t) = β_start + t*(β_end - β_start)
    EXPONENTIAL = "exponential"  # Exponential: β(t) = β_start * (β_end/β_start)^t
    POWER = "power"  # Power law: β(t) = β_start * (t/T)^α
    COSINE = "cosine"  # Cosine annealing
    SIGMOID = "sigmoid"  # Sigmoid schedule
    STEP = "step"  # Step schedule
    ADAPTIVE = "adaptive"  # Adaptive based on convergence


class NetworkActivation(Enum):
    """Activation functions for neural networks."""
    RELU = "relu"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SWISH = "swish"
    GELU = "gelu"
    TANH = "tanh"
    SIGMOID = "sigmoid"


class LossFunction(Enum):
    """Loss functions for neural IB."""
    MSE = "mse"  # Mean squared error
    CROSS_ENTROPY = "cross_entropy"  # Cross-entropy loss
    KL_DIVERGENCE = "kl_divergence"  # KL divergence
    HUBER = "huber"  # Huber loss
    FOCAL = "focal"  # Focal loss
    

class OptimizerType(Enum):
    """Optimizer types for neural networks."""
    ADAM = "adam"
    ADAMW = "adamw"
    SGD = "sgd"
    RMSPROP = "rmsprop"
    ADAGRAD = "adagrad"
    ADAMAX = "adamax"


class LRSchedulerType(Enum):
    """Learning rate scheduler types."""
    STEP = "step"
    EXPONENTIAL = "exponential"
    COSINE = "cosine"
    PLATEAU = "plateau"
    CYCLIC = "cyclic"


# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

@dataclass
class IBConfig:
    """
    Comprehensive configuration for Information Bottleneck algorithm.
    
    Controls all aspects of the IB optimization process including:
    - Core algorithm parameters (β, clusters, iterations)
    - Method selection (discrete/neural/continuous)
    - Optimization settings (convergence, annealing)
    - Mutual information estimation parameters
    - Advanced options (regularization, debugging)
    
    Based on: Tishby, Pereira & Bialek (1999)
    """
    
    # ========================================================================
    # Core Algorithm Parameters
    # ========================================================================
    n_clusters: int = 10
    """Number of clusters T (bottleneck size)"""
    
    beta: float = 1.0
    """Trade-off parameter between compression I(X;T) and relevance I(T;Y)"""
    
    max_iterations: int = 100
    """Maximum number of optimization iterations"""
    
    tolerance: float = 1e-6
    """Convergence tolerance for optimization"""
    
    # ========================================================================
    # Method Selection
    # ========================================================================
    method: IBMethod = IBMethod.DISCRETE
    """Information Bottleneck method to use"""
    
    optimization_method: OptimizationMethod = OptimizationMethod.BLAHUT_ARIMOTO
    """Optimization algorithm"""
    
    mi_estimator: MutualInfoEstimator = MutualInfoEstimator.KSG
    """Mutual information estimation method"""
    
    # ========================================================================
    # Initialization
    # ========================================================================
    initialization: InitializationMethod = InitializationMethod.KMEANS_PLUS_PLUS
    """Initialization strategy for cluster assignments"""
    
    n_init: int = 10
    """Number of random initializations to try"""
    
    random_state: Optional[int] = None
    """Random seed for reproducibility"""
    
    # ========================================================================
    # Algorithm Update Methods
    # ========================================================================
    encoder_update_method: EncoderUpdateMethod = EncoderUpdateMethod.BLAHUT_ARIMOTO
    """Method for updating encoder distribution p(t|x)"""
    
    decoder_update_method: DecoderUpdateMethod = DecoderUpdateMethod.BAYES_RULE
    """Method for updating decoder distribution p(y|t)"""
    
    # ========================================================================
    # Annealing Schedule
    # ========================================================================
    use_annealing: bool = True
    """Whether to use deterministic annealing"""
    
    annealing_schedule: AnnealingSchedule = AnnealingSchedule.EXPONENTIAL
    """Type of annealing schedule"""
    
    beta_start: float = 0.001
    """Starting β value for annealing"""
    
    beta_end: float = 10.0
    """Final β value for annealing"""
    
    annealing_steps: int = 20
    """Number of annealing steps"""
    
    annealing_power: float = 2.0
    """Power for power-law annealing"""
    
    # ========================================================================
    # Convergence Criteria
    # ========================================================================
    convergence_metric: ConvergenceMetric = ConvergenceMetric.OBJECTIVE_CHANGE
    """Metric to use for convergence checking"""
    
    check_convergence_every: int = 10
    """Check convergence every N iterations"""
    
    patience: int = 10
    """Early stopping patience"""
    
    min_improvement: float = 1e-6
    """Minimum improvement required to continue"""
    
    # ========================================================================
    # Mutual Information Estimation Parameters
    # ========================================================================
    mi_k_neighbors: int = 3
    """Number of neighbors for k-NN MI estimators"""
    
    mi_bins: Union[int, str] = "auto"
    """Number of bins for histogram-based MI estimation"""
    
    mi_kernel: str = "rbf"
    """Kernel type for kernel-based MI estimation"""
    
    mi_kernel_bandwidth: Optional[float] = None
    """Kernel bandwidth (None for automatic selection)"""
    
    mi_ensemble_weights: Optional[List[float]] = None
    """Weights for ensemble MI estimators"""
    
    mi_noise_level: float = 1e-10
    """Noise level for numerical stability"""
    
    # ========================================================================
    # Regularization
    # ========================================================================
    encoder_regularization: float = 0.0
    """L2 regularization for encoder parameters"""
    
    decoder_regularization: float = 0.1
    """L2 regularization for decoder parameters"""
    
    entropy_regularization: float = 0.0
    """Entropy regularization coefficient"""
    
    sparsity_regularization: float = 0.0
    """Sparsity regularization for cluster assignments"""
    
    # ========================================================================
    # Data Processing
    # ========================================================================
    normalize_data: bool = True
    """Whether to normalize input data"""
    
    standardize_data: bool = False
    """Whether to standardize input data (z-score)"""
    
    handle_missing_values: str = "remove"
    """How to handle missing values ('remove', 'impute', 'ignore')"""
    
    discretization_method: str = "quantile"
    """Method for discretizing continuous data ('quantile', 'uniform', 'kmeans')"""
    
    discretization_bins: int = 20
    """Number of bins for data discretization"""
    
    # ========================================================================
    # Advanced Options
    # ========================================================================
    verbose: bool = True
    """Whether to print optimization progress"""
    
    debug: bool = False
    """Whether to enable debug mode with detailed logging"""
    
    save_history: bool = True
    """Whether to save optimization history"""
    
    compute_bounds: bool = True
    """Whether to compute theoretical bounds"""
    
    track_information_metrics: bool = True
    """Whether to track I(X;T), I(T;Y) during optimization"""
    
    # ========================================================================
    # Parallelization
    # ========================================================================
    n_jobs: int = 1
    """Number of parallel jobs (-1 for all cores)"""
    
    parallel_backend: str = "threading"
    """Parallel backend ('threading', 'multiprocessing')"""
    
    # ========================================================================
    # Memory Management
    # ========================================================================
    batch_size: Optional[int] = None
    """Batch size for large datasets (None for full batch)"""
    
    memory_efficient: bool = False
    """Whether to use memory-efficient algorithms"""
    
    cache_computations: bool = True
    """Whether to cache MI computations"""
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.n_clusters <= 0:
            raise ValueError(f"n_clusters must be positive, got {self.n_clusters}")
        if self.beta < 0:
            raise ValueError(f"beta must be non-negative, got {self.beta}")
        if self.max_iterations <= 0:
            raise ValueError(f"max_iterations must be positive, got {self.max_iterations}")
        if self.tolerance <= 0:
            raise ValueError(f"tolerance must be positive, got {self.tolerance}")
        if self.annealing_steps <= 0:
            raise ValueError(f"annealing_steps must be positive, got {self.annealing_steps}")
        if self.beta_start <= 0 or self.beta_end <= 0:
            raise ValueError("beta_start and beta_end must be positive")
        if self.beta_start >= self.beta_end:
            raise ValueError("beta_start must be less than beta_end")
            
    def get_annealing_schedule(self) -> np.ndarray:
        """Generate β annealing schedule."""
        if not self.use_annealing:
            return np.array([self.beta])
            
        steps = np.linspace(0, 1, self.annealing_steps)
        
        if self.annealing_schedule == AnnealingSchedule.LINEAR:
            return self.beta_start + steps * (self.beta_end - self.beta_start)
        elif self.annealing_schedule == AnnealingSchedule.EXPONENTIAL:
            ratio = self.beta_end / self.beta_start
            return self.beta_start * (ratio ** steps)
        elif self.annealing_schedule == AnnealingSchedule.POWER:
            return self.beta_start + (self.beta_end - self.beta_start) * (steps ** self.annealing_power)
        elif self.annealing_schedule == AnnealingSchedule.COSINE:
            return self.beta_start + 0.5 * (self.beta_end - self.beta_start) * (1 + np.cos(np.pi * (1 - steps)))
        elif self.annealing_schedule == AnnealingSchedule.SIGMOID:
            # Sigmoid from -6 to 6 mapped to beta range
            x = -6 + 12 * steps
            sigmoid = 1 / (1 + np.exp(-x))
            return self.beta_start + sigmoid * (self.beta_end - self.beta_start)
        else:
            raise ValueError(f"Unknown annealing schedule: {self.annealing_schedule}")


@dataclass
class NeuralIBConfig:
    """
    Configuration for Neural Information Bottleneck.
    
    Extends IB to neural network implementations using deep networks
    to parameterize encoder p(T|X) and decoder p(Y|T) distributions.
    
    Based on: Alemi et al. (2017) "Deep Variational Information Bottleneck"
    """
    
    # ========================================================================
    # Network Architecture
    # ========================================================================
    input_dim: int = 784
    """Dimensionality of input data X"""
    
    output_dim: int = 10
    """Dimensionality of output data Y"""
    
    latent_dim: int = 20
    """Dimensionality of bottleneck representation T"""
    
    encoder_dims: List[int] = field(default_factory=lambda: [512, 256])
    """Hidden layer dimensions for encoder network"""
    
    decoder_dims: List[int] = field(default_factory=lambda: [256, 512])
    """Hidden layer dimensions for decoder network"""
    
    activation: NetworkActivation = NetworkActivation.RELU
    """Activation function for hidden layers"""
    
    output_activation: Optional[NetworkActivation] = None
    """Output layer activation (None for linear)"""
    
    # ========================================================================
    # Training Parameters
    # ========================================================================
    beta: float = 1.0
    """Information bottleneck trade-off parameter"""
    
    learning_rate: float = 0.001
    """Learning rate for optimizer"""
    
    batch_size: int = 128
    """Mini-batch size for training"""
    
    epochs: int = 100
    """Number of training epochs"""
    
    # ========================================================================
    # Network Configuration
    # ========================================================================
    use_batch_norm: bool = True
    """Whether to use batch normalization"""
    
    dropout_rate: float = 0.1
    """Dropout rate for regularization"""
    
    use_layer_norm: bool = False
    """Whether to use layer normalization"""
    
    use_spectral_norm: bool = False
    """Whether to use spectral normalization"""
    
    # ========================================================================
    # Optimizer Settings
    # ========================================================================
    optimizer: OptimizerType = OptimizerType.ADAM
    """Optimizer type"""
    
    weight_decay: float = 1e-4
    """L2 regularization coefficient"""
    
    momentum: float = 0.9
    """Momentum for SGD optimizer"""
    
    adam_betas: tuple = (0.9, 0.999)
    """Beta parameters for Adam optimizer"""
    
    adam_eps: float = 1e-8
    """Epsilon parameter for Adam optimizer"""
    
    # ========================================================================
    # Learning Rate Scheduling
    # ========================================================================
    lr_scheduler: Optional[LRSchedulerType] = LRSchedulerType.STEP
    """Learning rate scheduler type"""
    
    lr_step_size: int = 30
    """Step size for StepLR scheduler"""
    
    lr_gamma: float = 0.1
    """Decay factor for learning rate"""
    
    lr_patience: int = 10
    """Patience for ReduceLROnPlateau"""
    
    # ========================================================================
    # Variational Parameters
    # ========================================================================
    use_variational: bool = True
    """Whether to use variational (stochastic) encoder"""
    
    kl_weight: float = 1.0
    """Weight for KL divergence term"""
    
    kl_annealing: bool = True
    """Whether to anneal KL weight during training"""
    
    kl_annealing_epochs: int = 50
    """Number of epochs for KL annealing"""
    
    posterior_type: str = "gaussian"
    """Type of posterior distribution ('gaussian', 'mixture')"""
    
    prior_type: str = "standard_normal"
    """Type of prior distribution ('standard_normal', 'mixture')"""
    
    # ========================================================================
    # Loss Configuration
    # ========================================================================
    reconstruction_loss: LossFunction = LossFunction.MSE
    """Reconstruction loss function"""
    
    classification_loss: LossFunction = LossFunction.CROSS_ENTROPY
    """Classification loss function"""
    
    use_mutual_info_loss: bool = True
    """Whether to use neural MI estimation in loss"""
    
    mi_estimator_type: str = "mine"
    """Type of neural MI estimator ('mine', 'infonce', 'js')"""
    
    # ========================================================================
    # Device and Precision
    # ========================================================================
    device: str = "auto"
    """Device to use ('auto', 'cpu', 'cuda', 'mps')"""
    
    mixed_precision: bool = False
    """Whether to use mixed precision training"""
    
    compile_model: bool = False
    """Whether to compile model with torch.compile"""
    
    # ========================================================================
    # Data Loading
    # ========================================================================
    num_workers: int = 4
    """Number of workers for data loading"""
    
    pin_memory: bool = True
    """Whether to pin memory in data loader"""
    
    persistent_workers: bool = True
    """Whether to use persistent workers"""
    
    # ========================================================================
    # Monitoring and Checkpointing
    # ========================================================================
    log_interval: int = 10
    """Interval for logging training progress"""
    
    eval_interval: int = 1
    """Interval for evaluation"""
    
    save_checkpoints: bool = False
    """Whether to save model checkpoints"""
    
    checkpoint_dir: Optional[str] = None
    """Directory for saving checkpoints"""
    
    save_best_only: bool = True
    """Whether to save only the best model"""
    
    monitor_metric: str = "loss"
    """Metric to monitor for best model selection"""
    
    # ========================================================================
    # Regularization
    # ========================================================================
    information_penalty: float = 0.0
    """Additional penalty on mutual information"""
    
    capacity_regularization: float = 0.0
    """Regularization on representation capacity"""
    
    diversity_regularization: float = 0.0
    """Regularization to encourage diverse representations"""
    
    # ========================================================================
    # Advanced Neural Options
    # ========================================================================
    use_skip_connections: bool = False
    """Whether to use skip connections in networks"""
    
    use_attention: bool = False
    """Whether to use attention mechanisms"""
    
    gradient_clip_norm: Optional[float] = 1.0
    """Gradient clipping norm (None to disable)"""
    
    ema_decay: Optional[float] = None
    """Exponential moving average decay for model parameters"""
    
    def __post_init__(self):
        """Validate neural IB configuration."""
        if self.input_dim <= 0:
            raise ValueError(f"input_dim must be positive, got {self.input_dim}")
        if self.output_dim <= 0:
            raise ValueError(f"output_dim must be positive, got {self.output_dim}")
        if self.latent_dim <= 0:
            raise ValueError(f"latent_dim must be positive, got {self.latent_dim}")
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be positive, got {self.learning_rate}")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        if self.epochs <= 0:
            raise ValueError(f"epochs must be positive, got {self.epochs}")
        if not 0 <= self.dropout_rate <= 1:
            raise ValueError(f"dropout_rate must be in [0, 1], got {self.dropout_rate}")
            
    def get_device(self):
        """Get the appropriate device for training."""
        if self.device == "auto":
            if hasattr(torch, 'mps') and torch.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return self.device


@dataclass
class DeepIBConfig(NeuralIBConfig):
    """
    Configuration for Deep Information Bottleneck.
    
    Extends Neural IB to multiple bottleneck layers creating
    a hierarchy of compressed representations.
    
    Architecture: X → T₁ → T₂ → ... → Tₖ → Y
    """
    
    bottleneck_dims: List[int] = field(default_factory=lambda: [50, 20, 10])
    """Dimensions of successive bottleneck layers"""
    
    bottleneck_betas: Optional[List[float]] = None
    """Different β values for each bottleneck layer"""
    
    layer_wise_training: bool = False
    """Whether to train layers progressively"""
    
    freeze_lower_layers: bool = False
    """Whether to freeze lower layers during training"""
    
    def __post_init__(self):
        """Validate deep IB configuration."""
        super().__post_init__()
        if not self.bottleneck_dims:
            raise ValueError("bottleneck_dims cannot be empty")
        if len(self.bottleneck_dims) < 2:
            raise ValueError("Deep IB requires at least 2 bottleneck layers")
        
        # Set latent_dim to final bottleneck dimension
        self.latent_dim = self.bottleneck_dims[-1]
        
        # Set default β values for each layer if not provided
        if self.bottleneck_betas is None:
            # Use exponentially increasing β values
            self.bottleneck_betas = [self.beta * (2 ** i) for i in range(len(self.bottleneck_dims))]


@dataclass
class EvaluationConfig:
    """
    Configuration for Information Bottleneck evaluation and analysis.
    
    Controls comprehensive evaluation including:
    - Information-theoretic metrics
    - Classification performance
    - Visualization settings
    - Statistical significance testing
    """
    
    # ========================================================================
    # Information Metrics
    # ========================================================================
    compute_mutual_information: bool = True
    """Whether to compute I(X;T), I(T;Y), I(X;Y)"""
    
    compute_conditional_entropy: bool = True
    """Whether to compute conditional entropies"""
    
    compute_information_curves: bool = True
    """Whether to compute information bottleneck curves"""
    
    mi_estimation_samples: int = 1000
    """Number of samples for MI estimation"""
    
    # ========================================================================
    # Performance Metrics
    # ========================================================================
    compute_classification_metrics: bool = True
    """Whether to compute classification performance"""
    
    compute_clustering_metrics: bool = True
    """Whether to compute clustering performance"""
    
    compute_reconstruction_error: bool = True
    """Whether to compute reconstruction error"""
    
    cross_validation_folds: int = 5
    """Number of CV folds for evaluation"""
    
    # ========================================================================
    # Statistical Testing
    # ========================================================================
    significance_testing: bool = True
    """Whether to perform statistical significance tests"""
    
    bootstrap_samples: int = 1000
    """Number of bootstrap samples for confidence intervals"""
    
    confidence_level: float = 0.95
    """Confidence level for statistical tests"""
    
    # ========================================================================
    # Visualization
    # ========================================================================
    generate_plots: bool = True
    """Whether to generate evaluation plots"""
    
    plot_information_plane: bool = True
    """Whether to plot information plane visualization"""
    
    plot_training_history: bool = True
    """Whether to plot training history"""
    
    save_plots: bool = True
    """Whether to save generated plots"""
    
    plot_format: str = "png"
    """Format for saved plots ('png', 'pdf', 'svg')"""
    
    plot_dpi: int = 300
    """DPI for saved plots"""


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_discrete_ib_config(
    n_clusters: int = 10,
    beta: float = 1.0,
    method: str = "blahut_arimoto",
    **kwargs
) -> IBConfig:
    """
    Create configuration for discrete Information Bottleneck.
    
    Parameters
    ----------
    n_clusters : int
        Number of clusters
    beta : float
        Trade-off parameter  
    method : str
        Optimization method
    **kwargs
        Additional configuration options
    """
    config = IBConfig(
        n_clusters=n_clusters,
        beta=beta,
        method=IBMethod.DISCRETE,
        optimization_method=OptimizationMethod[method.upper()],
        **kwargs
    )
    return config


def create_neural_ib_config(
    input_dim: int,
    output_dim: int,
    latent_dim: int = 20,
    beta: float = 1.0,
    **kwargs
) -> NeuralIBConfig:
    """
    Create configuration for Neural Information Bottleneck.
    
    Parameters
    ----------
    input_dim : int
        Input dimensionality
    output_dim : int
        Output dimensionality
    latent_dim : int
        Latent dimensionality
    beta : float
        Trade-off parameter
    **kwargs
        Additional configuration options
    """
    config = NeuralIBConfig(
        input_dim=input_dim,
        output_dim=output_dim,
        latent_dim=latent_dim,
        beta=beta,
        **kwargs
    )
    return config


def create_deep_ib_config(
    input_dim: int,
    output_dim: int,
    bottleneck_dims: List[int],
    beta: float = 1.0,
    **kwargs
) -> DeepIBConfig:
    """
    Create configuration for Deep Information Bottleneck.
    
    Parameters
    ----------
    input_dim : int
        Input dimensionality
    output_dim : int
        Output dimensionality
    bottleneck_dims : List[int]
        Dimensions of bottleneck layers
    beta : float
        Trade-off parameter
    **kwargs
        Additional configuration options
    """
    config = DeepIBConfig(
        input_dim=input_dim,
        output_dim=output_dim,
        bottleneck_dims=bottleneck_dims,
        beta=beta,
        **kwargs
    )
    return config


def create_evaluation_config(
    detailed: bool = True,
    **kwargs
) -> EvaluationConfig:
    """
    Create configuration for Information Bottleneck evaluation.
    
    Parameters
    ----------
    detailed : bool
        Whether to enable detailed evaluation
    **kwargs
        Additional configuration options
    """
    if detailed:
        config = EvaluationConfig(
            compute_mutual_information=True,
            compute_conditional_entropy=True,
            compute_information_curves=True,
            compute_classification_metrics=True,
            generate_plots=True,
            significance_testing=True,
            **kwargs
        )
    else:
        config = EvaluationConfig(
            compute_mutual_information=True,
            compute_classification_metrics=True,
            generate_plots=False,
            significance_testing=False,
            **kwargs
        )
    
    return config


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

# Preset configurations for common use cases
IB_PRESETS = {
    "fast": IBConfig(
        n_clusters=5,
        beta=1.0,
        max_iterations=50,
        use_annealing=False,
        verbose=False
    ),
    
    "accurate": IBConfig(
        n_clusters=20,
        beta=1.0,
        max_iterations=500,
        tolerance=1e-8,
        use_annealing=True,
        annealing_steps=50,
        n_init=20
    ),
    
    "large_scale": IBConfig(
        n_clusters=10,
        beta=1.0,
        batch_size=1000,
        memory_efficient=True,
        n_jobs=-1,
        cache_computations=False
    )
}

NEURAL_IB_PRESETS = {
    "mnist": NeuralIBConfig(
        input_dim=784,
        output_dim=10,
        latent_dim=20,
        encoder_dims=[512, 256],
        decoder_dims=[256, 512],
        epochs=100
    ),
    
    "cifar10": NeuralIBConfig(
        input_dim=3072,
        output_dim=10,
        latent_dim=50,
        encoder_dims=[1024, 512, 256],
        decoder_dims=[256, 512, 1024],
        epochs=200,
        batch_size=256
    )
}


def get_preset_config(preset_name: str, config_type: str = "ib") -> Union[IBConfig, NeuralIBConfig]:
    """
    Get a preset configuration.
    
    Parameters
    ----------
    preset_name : str
        Name of the preset
    config_type : str
        Type of configuration ('ib', 'neural_ib')
    
    Returns
    -------
    config : IBConfig or NeuralIBConfig
        Preset configuration
    """
    if config_type == "ib":
        if preset_name not in IB_PRESETS:
            raise ValueError(f"Unknown IB preset: {preset_name}")
        return IB_PRESETS[preset_name]
    elif config_type == "neural_ib":
        if preset_name not in NEURAL_IB_PRESETS:
            raise ValueError(f"Unknown Neural IB preset: {preset_name}")
        return NEURAL_IB_PRESETS[preset_name]
    else:
        raise ValueError(f"Unknown config type: {config_type}")