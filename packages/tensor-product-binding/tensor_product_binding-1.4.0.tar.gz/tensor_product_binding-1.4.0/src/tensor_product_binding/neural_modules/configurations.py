"""
⚙️ Configurations
==================

🔬 Research Foundation:
======================
Based on tensor product representation theory:
- Smolensky, P. (1990). "Tensor Product Variable Binding and the Representation of Symbolic Structures"
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience"
🎯 ELI5 Summary:
Think of this like a control panel for our algorithm! Just like how your TV remote 
has different buttons for volume, channels, and brightness, this file has all the settings 
that control how our AI algorithm behaves. Researchers can adjust these settings to get 
the best results for their specific problem.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

⚙️ Configuration Architecture:
==============================
    ┌─────────────────────────┐
    │    USER SETTINGS        │
    ├─────────────────────────┤
    │ • Algorithm Parameters  │
    │ • Performance Options   │
    │ • Research Preferences  │
    │ • Output Formats        │
    └─────────────────────────┘
              ↓
    ┌─────────────────────────┐
    │      ALGORITHM          │
    │    (Configured)         │
    └─────────────────────────┘

"""
"""
Neural Binding Configurations
=============================

Author: Benedict Chen (benedict@benedictchen.com)

Configuration classes for neural binding networks.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TrainingConfig:
    """Configuration for neural binding training"""
    learning_rate: float = 0.001
    batch_size: int = 32
    n_epochs: int = 100
    weight_decay: float = 1e-5
    dropout_rate: float = 0.1
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    gradient_clip_norm: float = 1.0


@dataclass
class NetworkArchitecture:
    """Configuration for neural network architecture"""
    hidden_layers: List[int]
    activation_function: str = "relu"
    use_batch_norm: bool = False
    use_dropout: bool = True
    initialization_method: str = "xavier"