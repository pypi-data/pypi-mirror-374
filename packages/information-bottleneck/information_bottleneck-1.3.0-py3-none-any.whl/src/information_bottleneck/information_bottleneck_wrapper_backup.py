"""
📋 Information Bottleneck Wrapper Backup
=========================================

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
Backward compatibility module for Information Bottleneck
Imports from refactored modules to maintain existing API
"""

# Import the main classes from the consolidated core module
from .core import InformationBottleneck, NeuralInformationBottleneck

# Maintain backward compatibility
__all__ = ["InformationBottleneck", "NeuralInformationBottleneck"]