"""
📋 Neural Binding
==================

🔬 Research Foundation:
======================
Based on tensor product representation theory:
- Smolensky, P. (1990). "Tensor Product Variable Binding and the Representation of Symbolic Structures"
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience"
🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

"""
"""
⚡ Tensor Product Variable Binding - Neural Networks
===================================================

🎯 ELI5 EXPLANATION:
==================
Think of tensor product binding like teaching a computer to understand grammar!

Imagine you want to represent "The red CAR chased the blue TRUCK". How do you make sure the computer knows RED goes with CAR and BLUE goes with TRUCK? You can't just throw all the words together!

Tensor Product Binding solves this by creating "bound" combinations:
1. 🎨 **Role-Filler Binding**: RED ⊗ COLOR creates a unique pattern
2. 🚗 **Object Binding**: CAR ⊗ OBJECT creates another pattern  
3. 🧠 **Compose**: Add them: RED⊗COLOR + CAR⊗OBJECT + BLUE⊗COLOR + TRUCK⊗OBJECT
4. 🔍 **Query**: What color is the CAR? Unbind: result ⊗ CAR ⊗ COLOR⁻¹ ≈ RED!

The tensor product (⊗) creates systematic structure - like organizing your closet so you can always find the right shirt with the right pants!

🔬 RESEARCH FOUNDATION:
======================
Implements Paul Smolensky's revolutionary connectionist approach:
- Smolensky (1990): "Tensor Product Variable Binding and the Representation of Symbolic Structures in Connectionist Systems"
- Smolensky (1991): "The Constituent Structure of Connectionist Mental States"
- Smolensky (2006): "Optimality Theory: Constraint interaction in generative grammar"

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Tensor Product Binding:**
(a ⊗ b)ᵢⱼ = aᵢ × bⱼ

**Neural Implementation:**
- Binding Layer: z = W_bind([x₁; x₂]) where [x₁; x₂] is concatenation
- Unbinding Layer: y = W_unbind(z)
- Training: Learn W_bind and W_unbind to approximate tensor operations

**Properties:**
• Systematic: Each role-filler pair gets unique representation
• Compositional: Complex structures = sum of bound components
• Neural: Implementable in standard neural architectures

📊 ARCHITECTURE VISUALIZATION:
==============================
```
⚡ TENSOR PRODUCT BINDING NETWORK ⚡

Input Variables                Binding Network                   Bound Representation
┌─────────────┐               ┌─────────────────────────────┐    ┌─────────────────┐
│    ROLE     │               │                             │    │                 │
│    "RED"    │ ──────────────┤   🧠 BINDING LAYER         │    │   RED ⊗ COLOR   │
│  [1,0,0,0]  │               │   W_bind: ℝⁿ×ℝᵐ → ℝⁿˣᵐ     │    │   [0.8, -0.3,   │
└─────────────┘               │                             │    │    0.5, 0.1]   │
                              │   ⚡ TENSOR PRODUCT          │    │                 │
┌─────────────┐               │   APPROXIMATION             │    │                 │
│   FILLER    │               │                             │    │                 │
│  "COLOR"    │ ──────────────┤                             │    │                 │
│  [0,1,0,0]  │               │   📊 COMPOSITION LAYER      │──→ │  🧠 COMPOSED    │
└─────────────┘               │   Σᵢ (roleᵢ ⊗ fillerᵢ)      │    │  REPRESENTATION │
                              │                             │    │                 │
┌─────────────┐               │   🔍 UNBINDING LAYER        │    │                 │
│    ROLE     │               │   W_unbind: ℝⁿˣᵐ → ℝᵐ       │    │                 │
│   "BLUE"    │ ──────────────┤                             │    │  BLUE ⊗ COLOR   │
│  [0,0,1,0]  │               │                             │    │  [0.2, 0.7,     │
└─────────────┘               └─────────────────────────────┘    │   -0.4, 0.9]    │
                                                                 └─────────────────┘
                                       │
                                       ▼
                              🔍 QUERY PROCESSING:
                              "What color is bound to CAR?"
                                       │
                                       ▼
                             result ⊗ CAR⁻¹ → RED! ✨
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
"""

# Import all components from modular structure for backward compatibility
from .neural_modules.configurations import TrainingConfig, NetworkArchitecture
from .neural_modules.base_network import NeuralBindingNetwork
from .neural_modules.pytorch_network import PyTorchBindingNetwork
from .neural_modules.numpy_network import NumPyBindingNetwork
from .neural_modules.utilities import (
    create_neural_binding_network,
    generate_training_data,
    evaluate_neural_binding
)

# Export all classes and functions for backward compatibility
__all__ = [
    # Configuration classes
    'TrainingConfig',
    'NetworkArchitecture',
    
    # Network classes
    'NeuralBindingNetwork',
    'PyTorchBindingNetwork',
    'NumPyBindingNetwork',
    
    # Utility functions
    'create_neural_binding_network',
    'generate_training_data',
    'evaluate_neural_binding'
]

# Modularization Summary:
# ======================
# Original neural_binding.py (1207 lines) split into:
# 1. configurations.py (28 lines) - Configuration classes
# 2. base_network.py (64 lines) - Abstract base class
# 3. pytorch_network.py (179 lines) - PyTorch implementation
# 4. numpy_network.py (62 lines) - NumPy implementation  
# 5. utilities.py (82 lines) - Factory functions and utilities
# 6. __init__.py (25 lines) - Module exports
#
# Total modular lines: ~440 lines (64% reduction through cleanup)
# Largest module: 179 lines (85% reduction from original)
# Benefits: Better separation, easier testing, cleaner imports