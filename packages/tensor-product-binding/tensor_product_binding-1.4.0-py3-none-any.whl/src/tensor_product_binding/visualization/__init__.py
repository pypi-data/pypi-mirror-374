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
📊 Visualization Module for Tensor Product Binding
==================================================

This module provides visualization utilities for the tensor product binding
system. It includes functions for plotting vectors, binding operations,
structural representations, and analysis results.

Main Components:
- Vector visualization and similarity plots
- Binding operation visualizations
- Structural representation diagrams
- Analysis result plots
- Interactive visualization tools
"""

from .vector_plots import (
    plot_vector,
    plot_vector_comparison,
    plot_similarity_matrix,
    plot_vector_space,
    plot_pca_projection
)
from .binding_plots import (
    plot_binding_operation,
    plot_unbinding_quality,
    plot_binding_statistics,
    plot_reconstruction_accuracy
)
from .structure_plots import (
    plot_structure_tree,
    plot_compositional_structure,
    plot_hierarchical_binding,
    plot_semantic_network
)
from .analysis_plots import (
    plot_quality_metrics,
    plot_complexity_analysis,
    plot_coherence_analysis,
    plot_performance_benchmark
)
from .interactive import (
    create_interactive_vector_explorer,
    create_binding_dashboard,
    create_structure_inspector
)

__all__ = [
    # Vector plots
    'plot_vector',
    'plot_vector_comparison', 
    'plot_similarity_matrix',
    'plot_vector_space',
    'plot_pca_projection',
    
    # Binding plots
    'plot_binding_operation',
    'plot_unbinding_quality',
    'plot_binding_statistics',
    'plot_reconstruction_accuracy',
    
    # Structure plots
    'plot_structure_tree',
    'plot_compositional_structure', 
    'plot_hierarchical_binding',
    'plot_semantic_network',
    
    # Analysis plots
    'plot_quality_metrics',
    'plot_complexity_analysis',
    'plot_coherence_analysis', 
    'plot_performance_benchmark',
    
    # Interactive
    'create_interactive_vector_explorer',
    'create_binding_dashboard',
    'create_structure_inspector'
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
