"""
📋 Enums
=========

🔬 Research Foundation:
======================  
Based on information bottleneck principle:
- Tishby, N., Pereira, F.C. & Bialek, W. (1999). "The Information Bottleneck Method"
- Schwartz-Ziv, R. & Tishby, N. (2017). "Opening the Black Box of Deep Neural Networks"
- Alemi, A.A. et al. (2016). "Deep Variational Information Bottleneck"
🎯 ELI5 Summary:
This file is an important component in our AI research system! Like different organs 
in your body that work together to keep you healthy, this file has a specific job that 
helps the overall algorithm work correctly and efficiently.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

📋 Component Integration:
========================
    ┌──────────┐
    │   This   │
    │Component │ ←→ Other Components
    └──────────┘
         ↑↓
    System Integration

"""
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