"""
🧠 KSG MI Estimator - Modular Implementation  
============================================

🎯 ELI5 EXPLANATION:
==================
Think of mutual information estimation like measuring how much two friends know about each other!

When you want to know how connected two pieces of information are, you need different 
tools for different situations:

1. 🏃 **Fast Estimator**: Like speed-reading - quick but might miss details
2. 🎯 **Accurate Estimator**: Like careful study - slow but very precise  
3. 🤖 **Smart Estimator**: Automatically picks the best method
4. 📊 **Binning Estimator**: Groups data into buckets for easy counting
5. 🔬 **Research Estimator**: Maximum scientific accuracy

This modular approach makes it easy to pick the right tool for your data!

🔬 RESEARCH FOUNDATION:
======================
Cutting-edge mutual information estimation research:
- Kraskov, Stögbauer & Grassberger (2004): "Estimating mutual information" - KSG algorithm
- Darbellay & Vajda (1999): "Estimation of the information by adaptive partitioning"  
- Belghazi et al. (2018): "Mutual Information Neural Estimation" - MINE approach
- Tishby, Pereira & Bialek (1999): "The Information Bottleneck Method"

🧮 MATHEMATICAL PRINCIPLES:
==========================
**KSG Estimation:**
I(X;Y) = ψ(k) + ψ(N) - ⟨ψ(nₓ+1) + ψ(nᵧ+1)⟩

**Binning Approach:**
I(X;Y) = ΣΣ p(x,y) log[p(x,y) / (p(x)p(y))]

📊 MODULAR ARCHITECTURE:
========================
```
🧠 KSG MI ESTIMATOR (MODULAR) 🧠

┌─────────────────────────────────────────────────────────────────┐
│                    📋 FACTORY FUNCTIONS                         │
│  • create_efficient_mi_estimator • create_research_mi_estimator │
└─────────────────────────────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼─────────┐  ┌──────────▼──────────┐  ┌─────────▼─────────┐
│ 🎯 KSG ESTIMATORS │  │ 📊 BINNING METHODS  │  │ 🔧 BASE CLASSES   │  
│ • Main KSG Class  │  │ • Adaptive Binning  │  │ • BaseMIEstimator │
│ • Efficient KSG   │  │ • Histogram Simple  │  │ • MIEstimationRes │
│ • Legacy KSG      │  │ • Smart Bin Select  │  │ • Input Validation│
└────────────────────┘  └─────────────────────┘  └───────────────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │ 🚀 UNIFIED API  │
                          │ • Auto Selection │
                          │ • Error Handling │  
                          │ • Performance    │
                          │ • Research Acc.  │
                          └─────────────────┘
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
Based on: KSG algorithm and modern MI estimation methods

📁 MODULAR STRUCTURE:
===================
This file now serves as the main interface to the modularized components:

mi_estimator_modules/
├── __init__.py                    # Module exports
├── base_estimator.py             # Base classes and validation  
├── ksg_estimator.py              # KSG algorithm implementations
├── binning_estimator.py          # Binning-based methods
└── estimator_factory.py         # Factory functions for easy creation

🚀 BENEFITS OF MODULARIZATION:
==============================
✅ Improved Maintainability: Each estimator type in its own file
✅ Better Testing: Individual modules can be tested independently  
✅ Enhanced Readability: Focused, single-responsibility components
✅ Easier Extension: Add new estimators without touching existing code
✅ Reduced Complexity: 1,385 lines → 4 focused modules (~300-400 lines each)
✅ Better Documentation: Each module has targeted research context
"""

# Import all components from the modular structure
from .mi_estimator_modules import (
    # Base classes
    BaseMIEstimator,
    MIEstimationResult,
    
    # KSG estimators
    KSGMutualInformationEstimator,
    EfficientKSGEstimator, 
    LegacyKSGEstimator,
    
    # Compatibility alias
    KSGMutualInformationEstimator as KSGMutualInformationEstimatorComplete,
    
    # Neural estimators (placeholder)
    KSGMutualInformationEstimator as MINEEstimator,  # Placeholder for compatibility
    KSGMutualInformationEstimator as SklearnMIEstimator,  # Placeholder for compatibility
    
    # Binning estimators
    AdaptiveBinningEstimator,
    HistogramEstimator,
    
    # Factory functions
    create_efficient_mi_estimator,
    create_research_mi_estimator,
    create_legacy_mi_estimator,
    create_fast_mi_estimator,
    create_binning_mi_estimator,
    create_discrete_mi_estimator,
    create_continuous_mi_estimator,
    create_default_mi_estimator,
    create_accurate_mi_estimator
)

# Backward compatibility exports
__all__ = [
    # Base classes
    'BaseMIEstimator',
    'MIEstimationResult',
    
    # Main estimator classes (for advanced users)
    'KSGMutualInformationEstimator',
    'EfficientKSGEstimator', 
    'LegacyKSGEstimator',
    'AdaptiveBinningEstimator',
    'HistogramEstimator',
    
    # Factory functions (recommended for most users)
    'create_efficient_mi_estimator',
    'create_research_mi_estimator',
    'create_legacy_mi_estimator',
    'create_fast_mi_estimator',
    'create_binning_mi_estimator',
    'create_discrete_mi_estimator',
    'create_continuous_mi_estimator',
    'create_default_mi_estimator',
    'create_accurate_mi_estimator'
]

def print_modular_info():
    """Print information about the modular structure."""
    print("🧠 KSG MI Estimator - Modular Implementation")
    print("=" * 45)
    print()
    print("📁 MODULAR STRUCTURE:")
    print("   📋 base_estimator.py      - Base classes and validation")
    # Removed print spam: "   ...
    # Removed print spam: "   ...  
    # Removed print spam: "   ...
    print()
    # # Removed print spam: "...
    print("   • Reduced from 1,385 lines to 4 focused modules")
    print("   • Each module ~300-400 lines with single responsibility")
    print("   • Better maintainability and testing")
    print("   • Easier to extend with new estimation methods")
    print("   • Improved documentation and research context")
    print()
    # # Removed print spam: "...
    print("   from ksg_mi_estimator_modular import create_efficient_mi_estimator")
    print("   estimator = create_efficient_mi_estimator(data_size='large')")
    print("   result = estimator.estimate(X, Y)")


if __name__ == "__main__":
    print_modular_info()