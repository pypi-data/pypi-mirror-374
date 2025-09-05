"""
📋   Init  
============

🔬 Research Foundation:
======================
Based on qualitative reasoning and physics:
- Forbus, K.D. (1984). "Qualitative Process Theory"
- de Kleer, J. & Brown, J.S. (1984). "A Qualitative Physics Based on Confluences"
- Kuipers, B. (1994). "Qualitative Reasoning: Modeling and Simulation with Incomplete Knowledge"
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
Qualitative Reasoning Package

A comprehensive Python library for qualitative reasoning systems based on
Forbus's Process Theory and de Kleer's Qualitative Physics framework.

This package enables AI systems to reason about physical systems using
qualitative relationships rather than precise numerical values, similar
to how humans understand physics intuitively.

Features:
- Modular architecture with clean separation of concerns
- Security-first constraint evaluation (no eval() vulnerabilities)
- Rich visualization and analysis capabilities
- Factory functions for common use cases
- Full backward compatibility with original implementation

Modules:
- qr_core: Integrated qualitative reasoning core
- qualitative_reasoning_modules: Individual specialized components

Author: Benedict Chen
"""

print("""
🧠 Qualitative Reasoning Library - Made possible by Benedict Chen
   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\💳 CLICK HERE TO DONATE VIA PAYPAL\033]8;;\033\\
   ❤️ \033]8;;https://github.com/sponsors/benedictchen\033\\💖 SPONSOR ON GITHUB\033]8;;\033\\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")

__version__ = "1.0.0"

# Import from the new modular core
from .qr_core import (
    # Main class
    QualitativeReasoner,
    
    # Core types
    QualitativeValue,
    QualitativeDirection,
    QualitativeQuantity,
    QualitativeState, 
    QualitativeProcess,
    
    # Configuration classes
    ConstraintEvaluationMethod,
    ConstraintEvaluationConfig,
    VisualizationConfig,
    VisualizationReport,
    
    # Analysis classes
    CausalChain,
    RelationshipAnalysis,
    BehaviorExplanation,
    
    # Utility functions
    compare_qualitative_values,
    qualitative_to_numeric,
    numeric_to_qualitative,
    create_quantity,
    validate_qualitative_state,
    
    # Type aliases
    QValue,
    QDirection,
    QQuantity,
    QState,
    QProcess,
    
    # Factory functions
    create_educational_reasoner,
    create_research_reasoner,
    create_production_reasoner,
    create_demo_reasoner
)

__all__ = [
    # Main class
    "QualitativeReasoner",
    
    # Core types
    "QualitativeValue",
    "QualitativeDirection", 
    "QualitativeQuantity",
    "QualitativeState",
    "QualitativeProcess",
    
    # Configuration classes
    "ConstraintEvaluationMethod",
    "ConstraintEvaluationConfig", 
    "VisualizationConfig",
    "VisualizationReport",
    
    # Analysis classes
    "CausalChain",
    "RelationshipAnalysis",
    "BehaviorExplanation",
    
    # Utility functions
    "compare_qualitative_values",
    "qualitative_to_numeric",
    "numeric_to_qualitative", 
    "create_quantity",
    "validate_qualitative_state",
    
    # Type aliases
    "QValue",
    "QDirection",
    "QQuantity", 
    "QState",
    "QProcess",
    
    # Factory functions
    "create_educational_reasoner",
    "create_research_reasoner", 
    "create_production_reasoner",
    "create_demo_reasoner"
]

# Backward-compatible aliases for common name variants
QualitativeReasoningEngine = QualitativeReasoner  # Common alternate name
QREngine = QualitativeReasoner  # Short alias