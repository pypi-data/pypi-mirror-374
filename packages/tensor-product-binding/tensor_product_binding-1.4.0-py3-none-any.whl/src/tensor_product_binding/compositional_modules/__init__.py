"""
📋   Init  
============

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
📦 Compositional Semantics - Modular Components
==============================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE ORGANIZATION:
=====================
This modular architecture splits the original 1010-line compositional_semantics.py
into focused, maintainable components:

📊 MODULAR BREAKDOWN:
====================
• semantic_structures.py (124 lines) - Core semantic data structures
  - SemanticType, SemanticFrame, ConceptualRole, ConceptualSpace, SemanticRole, SemanticConcept

• semantic_engine.py (472 lines) - Main compositional semantics engine
  - CompositionalSemantics class with tensor product binding functionality
  - Role-filler binding, thematic role assignment, compositional construction

• advanced_composition.py (391 lines) - Advanced compositional methods
  - Frame-based composition, sentence processing, logical form composition
  - Semantic decomposition, WordNet integration, similarity analysis

• utilities.py (178 lines) - Utility functions for semantic processing
  - Lexicon creation, semantic frame definition, logical form parsing, similarity matrices

🔬 RESEARCH ACCURACY:
====================
All modules preserve the original Smolensky (1990) research implementations:
✅ Tensor product variable binding mechanics
✅ Compositional semantic construction
✅ Thematic role assignment and constraints
✅ Frame-based semantic representation
✅ Systematic compositional productivity

💡 USAGE PATTERNS:
=================
```python
# Import main engine
from .semantic_engine import CompositionalSemantics

# Import data structures
from .semantic_structures import SemanticType, SemanticFrame, SemanticConcept

# Import utilities
from .utilities import create_semantic_lexicon, create_standard_semantic_frames

# Create complete semantic system
semantics = CompositionalSemantics(
    vector_dim=256,
    semantic_lexicon=create_semantic_lexicon([...]),
    semantic_frames=create_standard_semantic_frames()
)
```

This modular design maintains full backward compatibility while enabling
focused development and maintenance of semantic processing components.
"""

from .semantic_structures import (
    SemanticType,
    SemanticFrame,
    ConceptualRole,
    ConceptualSpace,
    SemanticRole,
    SemanticConcept
)

from .semantic_engine import CompositionalSemantics

from .utilities import (
    create_semantic_lexicon,
    create_standard_semantic_frames,
    parse_simple_logical_form,
    semantic_similarity_matrix
)

# Export all components
__all__ = [
    # Semantic data structures
    'SemanticType',
    'SemanticFrame', 
    'ConceptualRole',
    'ConceptualSpace',
    'SemanticRole',
    'SemanticConcept',
    
    # Main semantic engine
    'CompositionalSemantics',
    
    # Utility functions
    'create_semantic_lexicon',
    'create_standard_semantic_frames',
    'parse_simple_logical_form', 
    'semantic_similarity_matrix'
]


if __name__ == "__main__":
    print("📦 Compositional Semantics - Modular Components")
    print("=" * 51)
    # print("🏗️ MODULAR ARCHITECTURE SUMMARY:")
    print("  ├─ semantic_structures.py (124 lines) - Core data structures") 
    print("  ├─ semantic_engine.py (412 lines) - Main compositional engine")
    print("  └─ utilities.py (178 lines) - Utility functions")
    print("")
    # Removed print spam: "...
    # # Removed print spam: "...
    print("")
    print("🔬 Smolensky (1990) tensor product semantics - modularized!")

print("""
💰 MODULE SUPPORT - Made possible by Benedict Chen
   ]8;;mailto:benedict@benedictchen.com\benedict@benedictchen.com]8;;\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 ]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\💳 CLICK HERE TO DONATE VIA PAYPAL]8;;\
   ❤️ ]8;;https://github.com/sponsors/benedictchen\💖 SPONSOR ON GITHUB]8;;\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")
