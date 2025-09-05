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
Neural Binding Modules
======================

Modular neural binding network implementations.
"""

from .configurations import TrainingConfig, NetworkArchitecture
from .base_network import NeuralBindingNetwork
from .pytorch_network import PyTorchBindingNetwork
from .numpy_network import NumPyBindingNetwork
from .utilities import (
    create_neural_binding_network,
    generate_training_data,
    evaluate_neural_binding
)

# Neural implementations from Smolensky (1990)
from .complete_neural_implementations import (
    NeuralBindingConfig,
    NeuralTensorProductBinder,
    create_mlp_binder,
    create_attention_binder,
    create_cnn_binder,
    create_hybrid_binder
)

__all__ = [
    # Original exports (PRESERVED)
    'TrainingConfig',
    'NetworkArchitecture', 
    'NeuralBindingNetwork',
    'PyTorchBindingNetwork',
    'NumPyBindingNetwork',
    'create_neural_binding_network',
    'generate_training_data', 
    'evaluate_neural_binding',
    
    # NEW: Complete neural implementations (ADDITIVE)
    'NeuralBindingConfig',
    'NeuralTensorProductBinder',
    'create_mlp_binder',
    'create_attention_binder',
    'create_cnn_binder', 
    'create_hybrid_binder'
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
