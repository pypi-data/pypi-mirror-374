"""
📋 Enumerations for Information Bottleneck Configuration
======================================================

Enum types for consistent configuration across IB implementations.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from enum import Enum


class IBMethod(Enum):
    """Information Bottleneck method types"""
    CLASSICAL = "classical"
    NEURAL = "neural" 
    DEEP = "deep"
    VARIATIONAL = "variational"


class InitializationMethod(Enum):
    """Initialization methods for IB algorithms"""
    RANDOM = "random"
    KMEANS = "kmeans"
    KMEANS_PLUS_PLUS = "kmeans++"
    DETERMINISTIC_ANNEALING = "deterministic_annealing"


class MutualInfoEstimator(Enum):
    """Mutual information estimation methods"""
    KSG = "ksg"  # Kraskov-Grassberger-Stögbauer
    DISCRETE = "discrete"
    BINNING = "binning"
    KERNEL = "kernel"
    SKLEARN = "sklearn"
    AUTO = "auto"


class OptimizationMethod(Enum):
    """Optimization methods for IB"""
    ALTERNATING = "alternating"
    DETERMINISTIC_ANNEALING = "deterministic_annealing"
    GRADIENT_DESCENT = "gradient_descent"
    EVOLUTIONARY = "evolutionary"
    MULTI_RESTART = "multi_restart"