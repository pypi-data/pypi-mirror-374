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
Qualitative Reasoning Modules Package

This package contains modularized components of the qualitative reasoning system,
broken down from the monolithic qualitative_reasoning.py file for better
maintainability, testability, and extensibility.

Modules:
- core_types: Basic data structures and enums
- constraint_engine: Constraint evaluation and safety systems  
- process_engine: Process management and causal reasoning
- simulation_engine: Qualitative simulation and state management
- analysis_engine: Relationship analysis and behavior explanation
- visualization_engine: System state visualization and reporting
- safety_config: Configuration management for safe constraint evaluation

Author: Benedict Chen
"""

__version__ = "1.0.0"

from .core_types import (
    QualitativeValue,
    QualitativeDirection, 
    QualitativeQuantity,
    QualitativeState,
    QualitativeProcess,
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
    QProcess
)

# Constraint engine - safety-critical constraint evaluation
from .constraint_engine import (
    ConstraintEvaluationMethod,
    ConstraintEvaluationConfig,
    ConstraintEngineMixin
)

# Analysis engine - intelligence layer for behavior analysis
from .analysis_engine import (
    AnalysisEngineMixin,
    CausalChain,
    RelationshipAnalysis,
    BehaviorExplanation
)

# Visualization engine - presentation layer for results display
from .visualization_engine import (
    VisualizationEngineMixin,
    VisualizationConfig,
    VisualizationReport
)

# Process engine - process management and causal reasoning
from .process_engine import ProcessEngineMixin

# Simulation engine - qualitative simulation and state evolution  
from .simulation_engine import SimulationEngineMixin

__all__ = [
    # Core types
    "QualitativeValue",
    "QualitativeDirection",
    "QualitativeQuantity", 
    "QualitativeState",
    "QualitativeProcess",
    
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
    
    # Constraint engine components
    "ConstraintEvaluationMethod",
    "ConstraintEvaluationConfig", 
    "ConstraintEngineMixin",
    
    # Analysis engine components
    "AnalysisEngineMixin",
    "CausalChain",
    "RelationshipAnalysis", 
    "BehaviorExplanation",
    
    # Visualization engine components
    "VisualizationEngineMixin",
    "VisualizationConfig",
    "VisualizationReport",
    
    # Engine mixins
    "ProcessEngineMixin", 
    "SimulationEngineMixin",
    
    # Note: Other components will be added as they are implemented
    # "SafetyConfigManager"
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
