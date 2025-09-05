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
🧠 Tensor Product Binding - Core Module
=======================================

Core algorithms and implementations for tensor product variable binding.

Based on Smolensky (1990) "Tensor Product Variable Binding and the 
Representation of Symbolic Structures in Connectionist Systems"

This module provides:
- Main TensorProductBinding class
- Core binding operations
- Vector space management
- Binding/unbinding algorithms
"""

from .binding_operations import TensorProductBinding, TPRVector, BindingOperation
from .vector_spaces import VectorSpace, SymbolicVector
from .algorithms import bind_vectors, unbind_vectors, cleanup_vector

# Create TensorProductBinder as an alias for TensorProductBinding
# This provides a simpler, more intuitive name for users
TensorProductBinder = TensorProductBinding

__all__ = [
    'TensorProductBinding',
    'TensorProductBinder',  # Add the alias to exports
    'TPRVector', 
    'BindingOperation',
    'VectorSpace',
    'SymbolicVector',
    'bind_vectors',
    'unbind_vectors',
    'cleanup_vector'
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
