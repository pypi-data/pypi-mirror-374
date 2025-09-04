"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Method Library
===================================

Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"

This library implements the foundational information-theoretic framework that 
revolutionized understanding of learning and representation in AI systems.

🔬 Research Foundation:
- Naftali Tishby's Information Bottleneck Method
- Noam Slonim's Agglomerative Information Bottleneck  
- Elena Voita's Information Bottleneck analysis of NLP
- Deep Learning through the Information Bottleneck principle

🎯 Key Features:
- Classical Information Bottleneck optimization
- Neural Information Bottleneck implementations
- Mutual information estimation and visualization
- Research-accurate implementations of core algorithms
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   \\033]8;;mailto:benedict@benedictchen.com\\033\\\\benedict@benedictchen.com\\033]8;;\\033\\\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \\033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\\033\\\\💳 CLICK HERE TO DONATE VIA PAYPAL\\033]8;;\\033\\\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")

from .core import (
    InformationBottleneck,
    NeuralInformationBottleneck, 
    DeepInformationBottleneck,
    InformationBottleneckClassifier,
    IBOptimizer,
    MutualInfoEstimator,
    MutualInfoCore
)

# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════

# Complete MI estimation system - fixes critical O(n³) complexity issue
from .complete_mi_estimator import (
    CompleteMutualInformationEstimator,
    EfficientKSGEstimator,
    LegacyKSGEstimator,
    AdaptiveBinningEstimator,
    MINEEstimator,
    HistogramEstimator,
    SklearnMIEstimator,
    MIEstimationResult,
    create_efficient_mi_estimator,
    create_research_mi_estimator,
    create_legacy_mi_estimator
)

# Complete configuration system for MI estimation
from .mi_estimation_config import (
    MIEstimationConfig,
    MIEstimationMethod,
    OptimizationStrategy,
    DataCharacteristics,
    create_research_accurate_config,
    create_high_performance_config,
    create_legacy_compatible_config,
    create_ensemble_config,
    create_gpu_accelerated_config
)

from .config import (
    IBConfig,
    NeuralIBConfig,
    DeepIBConfig,
    EvaluationConfig,
    IBMethod,
    InitializationMethod,
    MutualInfoEstimator as MutualInfoEstimatorEnum,
    OptimizationMethod,
    create_discrete_ib_config,
    create_neural_ib_config,
    create_deep_ib_config
)

from .utils import (
    # Math utilities
    compute_mutual_information_discrete,
    compute_mutual_information_ksg,
    safe_log,
    safe_divide,
    entropy_discrete,
    kl_divergence_discrete,
    
    # Data utilities  
    normalize_data,
    discretize_data,
    create_synthetic_ib_data,
    validate_ib_inputs,
    
    # Metrics
    compute_classification_metrics,
    compute_clustering_metrics,
    compute_information_theoretic_metrics
)

from .viz import (
    IBVisualization,
    InteractiveIBVisualization,
    setup_publication_style,
    plot_mutual_information_heatmap,
    create_visualization_report
)

# Show attribution on library import
_print_attribution()

__version__ = "1.1.1"
__authors__ = ["Based on Tishby, Pereira & Bialek (1999)"]

# Define explicit public API - UNIFIED STRUCTURE
__all__ = [
    # Core algorithms (consolidated from scattered files) - ALL PRESERVED
    "InformationBottleneck", 
    "NeuralInformationBottleneck",
    "DeepInformationBottleneck",
    "InformationBottleneckClassifier",
    "IBOptimizer",
    "MutualInfoEstimator",
    "MutualInfoCore",
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # Complete MI estimation system - fixes critical O(n³) complexity issue
    "CompleteMutualInformationEstimator",
    "create_efficient_mi_estimator",
    "create_research_mi_estimator", 
    "create_legacy_mi_estimator",
    "MIEstimationResult",
    
    # Individual estimator classes for advanced usage
    "EfficientKSGEstimator",
    "LegacyKSGEstimator",
    "AdaptiveBinningEstimator",
    "MINEEstimator",
    "HistogramEstimator",
    "SklearnMIEstimator",
    
    # Configuration classes (unified config system) - ALL PRESERVED
    "IBConfig",
    "NeuralIBConfig",
    "DeepIBConfig", 
    "EvaluationConfig",
    "IBMethod",
    "InitializationMethod",
    "MutualInfoEstimatorEnum",
    "OptimizationMethod",
    
    # NEW: Complete MI estimation configuration system
    "MIEstimationConfig",
    "MIEstimationMethod", 
    "OptimizationStrategy",
    "DataCharacteristics",
    "create_research_accurate_config",
    "create_high_performance_config",
    "create_legacy_compatible_config",
    "create_ensemble_config",
    "create_gpu_accelerated_config",
    
    # Factory functions for easy configuration
    "create_discrete_ib_config",
    "create_neural_ib_config", 
    "create_deep_ib_config",
    
    # Utility functions (mathematical and data processing)
    "compute_mutual_information_discrete",
    "compute_mutual_information_ksg",
    "safe_log",
    "safe_divide", 
    "entropy_discrete",
    "kl_divergence_discrete",
    "normalize_data",
    "discretize_data",
    "compute_classification_metrics",
    "compute_clustering_metrics", 
    "compute_information_theoretic_metrics",
    "validate_ib_inputs",
    "create_synthetic_ib_data",
    
    # Visualization functions (publication-quality plotting)
    "IBVisualization",
    "InteractiveIBVisualization",
    "setup_publication_style",
    "plot_mutual_information_heatmap",
    "create_visualization_report",
]

# Set flag for successful import
MAIN_IB_AVAILABLE = True

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Information Bottleneck Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""