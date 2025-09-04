"""
⚙️ Configuration Module for Information Bottleneck
=================================================

Configuration classes and presets for Information Bottleneck algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .ib_config import (
    IBConfig,
    NeuralIBConfig,
    DeepIBConfig,
    EvaluationConfig,
    create_discrete_ib_config,
    create_neural_ib_config,
    create_deep_ib_config
)

from .enums import (
    IBMethod,
    InitializationMethod,
    MutualInfoEstimator,
    OptimizationMethod
)

__all__ = [
    'IBConfig',
    'NeuralIBConfig',
    'DeepIBConfig',
    'EvaluationConfig',
    'IBMethod',
    'InitializationMethod',
    'MutualInfoEstimator',
    'OptimizationMethod',
    'create_discrete_ib_config',
    'create_neural_ib_config',
    'create_deep_ib_config'
]