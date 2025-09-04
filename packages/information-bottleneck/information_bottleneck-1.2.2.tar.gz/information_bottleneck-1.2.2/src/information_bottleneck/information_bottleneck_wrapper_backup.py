"""
Backward compatibility module for Information Bottleneck
Imports from refactored modules to maintain existing API
"""

# Import the main classes from the consolidated core module
from .core import InformationBottleneck, NeuralInformationBottleneck

# Maintain backward compatibility
__all__ = ["InformationBottleneck", "NeuralInformationBottleneck"]