"""
🔍 Core Information Bottleneck Module
====================================

Core implementations of Information Bottleneck methods including
classical IB, neural IB, and deep IB algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .neural_ib import NeuralInformationBottleneck
from .classical_ib import InformationBottleneck
from .deep_ib import DeepInformationBottleneck
from .ib_classifier import InformationBottleneckClassifier
from .optimizer import IBOptimizer
from .mutual_info import MutualInfoEstimator, MutualInfoCore

__all__ = [
    'NeuralInformationBottleneck',
    'InformationBottleneck', 
    'DeepInformationBottleneck',
    'InformationBottleneckClassifier',
    'IBOptimizer',
    'MutualInfoEstimator',
    'MutualInfoCore'
]