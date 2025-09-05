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

print("""
💰 MODULE SUPPORT - Made possible by Benedict Chen
   ]8;;mailto:benedict@benedictchen.com\benedict@benedictchen.com]8;;\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 ]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\💳 CLICK HERE TO DONATE VIA PAYPAL]8;;\
   ❤️ ]8;;https://github.com/sponsors/benedictchen\💖 SPONSOR ON GITHUB]8;;\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")
