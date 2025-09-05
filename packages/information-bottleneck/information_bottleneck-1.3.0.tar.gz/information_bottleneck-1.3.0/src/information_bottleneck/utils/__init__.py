"""
📋   Init  
============

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
🛠️ Utilities for Information Bottleneck
=======================================

Utility functions for data processing, validation, and metrics
for Information Bottleneck algorithms.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .data_utils import (
    normalize_data,
    discretize_data,
    create_synthetic_ib_data,
    validate_ib_inputs
)

from .math_utils import (
    safe_log,
    safe_divide,
    entropy_discrete,
    kl_divergence_discrete,
    compute_mutual_information_discrete,
    compute_mutual_information_ksg
)

from .metrics import (
    compute_classification_metrics,
    compute_clustering_metrics,
    compute_information_theoretic_metrics
)

__all__ = [
    # Data utilities
    'normalize_data',
    'discretize_data', 
    'create_synthetic_ib_data',
    'validate_ib_inputs',
    
    # Math utilities
    'safe_log',
    'safe_divide',
    'entropy_discrete',
    'kl_divergence_discrete',
    'compute_mutual_information_discrete',
    'compute_mutual_information_ksg',
    
    # Metrics
    'compute_classification_metrics',
    'compute_clustering_metrics',
    'compute_information_theoretic_metrics'
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
