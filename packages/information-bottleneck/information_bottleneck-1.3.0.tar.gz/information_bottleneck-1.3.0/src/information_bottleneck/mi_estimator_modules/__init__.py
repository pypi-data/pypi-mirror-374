"""
🧠 MI Estimator Modules
=======================

Modularized implementation of mutual information estimators.
Broken down from the original ksg_mi_estimator.py for better maintainability.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Multiple MI estimation methods from research literature
"""

# Base classes and results
from .base_estimator import BaseMIEstimator, MIEstimationResult

# Individual estimator implementations
from .ksg_estimator import KSGMutualInformationEstimator, EfficientKSGEstimator, LegacyKSGEstimator
from .binning_estimator import AdaptiveBinningEstimator, HistogramEstimator

# Factory functions  
from .estimator_factory import (
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

__all__ = [
    # Base classes
    'BaseMIEstimator',
    'MIEstimationResult',
    
    # KSG estimators
    'KSGMutualInformationEstimator',
    'EfficientKSGEstimator', 
    'LegacyKSGEstimator',
    
    # Binning estimators
    'AdaptiveBinningEstimator',
    'HistogramEstimator',
    
    # Factory functions
    'create_efficient_mi_estimator',
    'create_research_mi_estimator', 
    'create_legacy_mi_estimator'
]

print("""
💰 MODULE SUPPORT - Made possible by Benedict Chen
   ]8;;mailto:benedict@benedictchen.com\benedict@benedictchen.com]8;;\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 ]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\💳 CLICK HERE TO DONATE VIA PAYPAL]8;;\
   ❤️ ]8;;https://github.com/sponsors/benedictchen\💖 SPONSOR ON GITHUB]8;;\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")
