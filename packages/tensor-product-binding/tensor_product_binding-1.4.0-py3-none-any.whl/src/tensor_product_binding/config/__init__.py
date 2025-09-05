"""
📋   Init  
============

🔬 Research Foundation:
======================
Based on tensor product representation theory:
- Smolensky, P. (1990). "Tensor Product Variable Binding and the Representation of Symbolic Structures"
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience"
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
🔧 Configuration Module for Tensor Product Binding
==================================================

This module provides all configuration parameters, enums, and data classes
for the tensor product binding system. It consolidates settings and provides
a clean interface for configuring TPB operations.

Main Components:
- BindingOperation: Different binding operation types  
- TensorBindingConfig: Main configuration class
- BindingPair: Data class for variable-value binding pairs
- Performance settings and optimization parameters
"""

from .enums import (
    BindingOperation,
    BindingMethod,
    UnbindingMethod,
    VectorSpaceType,
    StructureType
)
from .config_classes import (
    TensorBindingConfig,
    BindingPair,
    VectorSpaceConfig,
    PerformanceConfig
)
from .defaults import (
    DEFAULT_CONFIG,
    DEFAULT_VECTOR_DIM,
    DEFAULT_BINDING_STRENGTH,
    OPTIMIZATION_PRESETS,
    apply_preset,
    get_preset_description,
    list_presets
)

__all__ = [
    # Enums
    'BindingOperation',
    'BindingMethod', 
    'UnbindingMethod',
    'VectorSpaceType',
    'StructureType',
    
    # Configuration Classes
    'TensorBindingConfig',
    'BindingPair',
    'VectorSpaceConfig',
    'PerformanceConfig',
    
    # Defaults
    'DEFAULT_CONFIG',
    'DEFAULT_VECTOR_DIM',
    'DEFAULT_BINDING_STRENGTH',
    'OPTIMIZATION_PRESETS',
    
    # Preset utilities
    'apply_preset',
    'get_preset_description',
    'list_presets'
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
