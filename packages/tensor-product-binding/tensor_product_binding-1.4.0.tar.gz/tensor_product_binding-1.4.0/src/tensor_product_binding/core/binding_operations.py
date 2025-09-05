"""
🔗 Tensor Product Binding - Neural Grammar Magic Engine
======================================================

🎯 ELI5 EXPLANATION:
==================
Think of Tensor Product Binding like creating a magical grammar system that lets computers understand language structure like humans do!

Imagine you're playing with LEGO blocks, but instead of just stacking them, you have a special "binding tool" that can magically fuse any two blocks together in a way that preserves both their individual properties AND their relationship. That's exactly what tensor product binding does with information:

1. 🎭 **Role Vectors**: Like grammar slots - "subject", "verb", "object" in a sentence
2. 🎯 **Filler Vectors**: Like the actual words - "John", "loves", "Mary"  
3. 🔗 **Binding Magic**: Mathematically fuse role+filler so you can store "John-is-subject" as one compact representation
4. 🧠 **Neural Compatible**: Works with how real brains might process structured information!

It's like having a universal translator that can take any sentence structure and compress it into brain-friendly vectors while keeping all the grammatical relationships intact!

🔬 RESEARCH FOUNDATION:
======================
Core neural symbolic architecture theory from cognitive science pioneers:
- **Smolensky (1990)**: "Tensor product variable binding" - Original neural binding breakthrough  
- **Plate (1995)**: "Holographic reduced representations" - Vector symbolic architectures
- **Hinton (1990)**: "Mapping part-whole hierarchies into connectionist networks" - Structured representations
- **Marcus (2001)**: "The algebraic mind" - Symbolic structure in neural systems

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Tensor Product Binding:**
role ⊗ filler = R ⊗ F (outer product creates structured representation)

**Circular Convolution Binding:**
(r ⊛ f)ₖ = Σᵢ rᵢ f₍ₖ₋ᵢ₎ mod n (memory-efficient alternative)

**Unbinding Recovery:**
F̂ = (R ⊗ F) ⊗ R⁻¹ (recover filler given role)

**Superposition:**
S = α₁(R₁ ⊗ F₁) + α₂(R₂ ⊗ F₂) + ... (multiple bindings)

📊 TENSOR PRODUCT BINDING VISUALIZATION:
=======================================
```
🔗 TENSOR PRODUCT BINDING ENGINE 🔗

Grammar Structure           Binding Operations              Neural Representation
┌─────────────────┐        ┌─────────────────────────────┐  ┌─────────────────┐
│ 🎭 ROLES        │        │                             │  │ 🧠 BOUND MEMORY │
│ "subject"       │ ────→  │  🔗 OUTER PRODUCT:          │→ │ Compact vectors │
│ "verb"          │        │  • R ⊗ F tensor operation  │  │ storing full    │
│ "object"        │        │  • Preserves structure     │  │ sentence info   │
└─────────────────┘        │  • Neural compatible       │  │                 │
                           │                             │  │ 🔍 RETRIEVAL    │
┌─────────────────┐        │  🌀 CIRCULAR CONVOLUTION:   │  │ Extract any     │
│ 🎯 FILLERS      │ ────→  │  • Memory efficient        │  │ role-filler     │
│ "John"          │        │  • FFT optimized           │  │ combination     │
│ "loves"         │        │  • Robust binding          │  │                 │
│ "Mary"          │        │                             │  │ ✨ COMPOSITION  │
└─────────────────┘        │  ➕ SUPERPOSITION:          │  │ Multiple        │
                           │  • Combine multiple bindings│  │ sentences in    │
┌─────────────────┐        │  • Weighted summation      │  │ single vector   │
│ ⚙️ Operations    │ ────→  │  • Hierarchical structure  │  │                 │
│ bind(), unbind()│        │                             │  │ 🎯 GRAMMAR      │
│ superpose()     │        └─────────────────────────────┘  │ Structured      │
└─────────────────┘                       │                 │ representations │
                                          ▼                 │ for neural nets │
                               RESULT: Neural grammar that  └─────────────────┘
                                      computers understand! 🚀
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky's foundational tensor product binding theory
"""

import numpy as np
from typing import Union, List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import warnings


class BindingOperation(Enum):
    """
    🔗 Types of binding operations for tensor product binding.
    
    Mathematical approaches to combine role and filler vectors:
    - OUTER_PRODUCT: Standard tensor product (role ⊗ filler) 
    - CIRCULAR_CONVOLUTION: Circular convolution binding (memory efficient)
    - ADDITION: Simple vector addition (least structured)
    - MULTIPLICATION: Element-wise multiplication (component binding)
    """
    OUTER_PRODUCT = "outer_product"
    CIRCULAR_CONVOLUTION = "circular_convolution"
    ADDITION = "addition" 
    MULTIPLICATION = "multiplication"


@dataclass
class TPRVector:
    """
    🎯 Tensor Product Binding Vector
    
    Represents a vector in the TPB space with metadata.
    
    Attributes
    ----------
    data : np.ndarray
        The actual vector data
    role : str, optional
        Role name if this is a role vector
    filler : str, optional  
        Filler name if this is a filler vector
    is_bound : bool
        Whether this represents a bound role-filler pair
    binding_info : dict
        Metadata about binding operations
    """
    data: np.ndarray
    role: Optional[str] = None
    filler: Optional[str] = None
    is_bound: bool = False
    binding_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.binding_info is None:
            self.binding_info = {}
        
        # Ensure data is numpy array
        if not isinstance(self.data, np.ndarray):
            self.data = np.array(self.data)
    
    @property
    def dimension(self) -> int:
        """Get vector dimension"""
        return len(self.data) if self.data.ndim == 1 else self.data.size
    
    @property
    def norm(self) -> float:
        """Get vector norm"""
        return np.linalg.norm(self.data)
    
    def normalize(self) -> 'TPRVector':
        """Return normalized copy of vector"""
        norm = self.norm
        if norm > 0:
            normalized_data = self.data / norm
        else:
            normalized_data = self.data.copy()
        
        return TPRVector(
            data=normalized_data,
            role=self.role,
            filler=self.filler,
            is_bound=self.is_bound,
            binding_info=self.binding_info.copy()
        )
    
    def similarity(self, other: 'TPRVector') -> float:
        """Compute cosine similarity with another TPB vector"""
        if self.data.shape != other.data.shape:
            raise ValueError("Vectors must have same shape for similarity")
        
        norm_self = self.norm
        norm_other = other.norm
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.data.flatten(), other.data.flatten()) / (norm_self * norm_other)


class TensorProductBinding:
    """
    🧠 Main Tensor Product Binding System
    
    Implements Smolensky's tensor product variable binding for neural-compatible
    structured representation. Supports multiple binding operations and provides
    efficient encoding/decoding of symbolic structures.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of role and filler vectors
    binding_method : BindingOperation, default=OUTER_PRODUCT
        Method used for binding operations
    cleanup_vectors : dict, optional
        Dictionary of cleanup vectors for unbinding
    normalize : bool, default=True
        Whether to normalize vectors after operations
    noise_level : float, default=0.0
        Noise level for robust representations
    """
    
    def __init__(self,
                 vector_dim: int = 100,
                 binding_method: BindingOperation = BindingOperation.OUTER_PRODUCT,
                 cleanup_vectors: Optional[Dict[str, np.ndarray]] = None,
                 normalize: bool = True,
                 noise_level: float = 0.0):
        
        self.vector_dim = vector_dim
        self.binding_method = binding_method
        self.normalize = normalize
        self.noise_level = noise_level
        
        # Initialize vector storage
        self.role_vectors: Dict[str, TPRVector] = {}
        self.filler_vectors: Dict[str, TPRVector] = {} 
        self.cleanup_vectors = cleanup_vectors or {}
        
        # Binding operation statistics
        self.binding_stats = {
            'total_bindings': 0,
            'successful_unbindings': 0,
            'failed_unbindings': 0
        }
    
    def create_role_vector(self, role_name: str, vector_data: Optional[np.ndarray] = None) -> TPRVector:
        """
        Create or retrieve a role vector.
        
        Parameters
        ----------
        role_name : str
            Name of the role
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random vector generated
            
        Returns
        -------
        TPRVector
            The role vector
        """
        if role_name in self.role_vectors:
            return self.role_vectors[role_name]
        
        if vector_data is None:
            # Generate random role vector
            vector_data = np.random.randn(self.vector_dim)
            if self.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
        
        role_vector = TPRVector(
            data=vector_data,
            role=role_name,
            is_bound=False,
            binding_info={'type': 'role', 'created': 'auto-generated'}
        )
        
        self.role_vectors[role_name] = role_vector
        return role_vector
    
    def create_filler_vector(self, filler_name: str, vector_data: Optional[np.ndarray] = None) -> TPRVector:
        """
        Create or retrieve a filler vector.
        
        Parameters
        ----------
        filler_name : str
            Name of the filler
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random vector generated
            
        Returns
        -------
        TPRVector
            The filler vector
        """
        if filler_name in self.filler_vectors:
            return self.filler_vectors[filler_name]
        
        if vector_data is None:
            # Generate random filler vector
            vector_data = np.random.randn(self.vector_dim)
            if self.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
        
        filler_vector = TPRVector(
            data=vector_data,
            filler=filler_name,
            is_bound=False,
            binding_info={'type': 'filler', 'created': 'auto-generated'}
        )
        
        self.filler_vectors[filler_name] = filler_vector
        return filler_vector
    
    def bind(self, role: Union[str, TPRVector, np.ndarray], filler: Union[str, TPRVector, np.ndarray]) -> TPRVector:
        """
        Bind a role vector to a filler vector.
        
        Parameters
        ----------
        role : str, TPRVector, or np.ndarray
            Role to bind (creates TPRVector if string or numpy array)
        filler : str, TPRVector, or np.ndarray
            Filler to bind (creates TPRVector if string or numpy array)
            
        Returns
        -------
        TPRVector
            Bound representation
        """
        # Convert strings to vectors
        if isinstance(role, str):
            role = self.create_role_vector(role)
        elif isinstance(role, np.ndarray):
            role = TPRVector(data=role, role="numpy_role", filler=None, is_bound=False)
        
        if isinstance(filler, str):
            filler = self.create_filler_vector(filler)
        elif isinstance(filler, np.ndarray):
            filler = TPRVector(data=filler, role=None, filler="numpy_filler", is_bound=False)
        
        # Perform binding based on method
        if self.binding_method == BindingOperation.OUTER_PRODUCT:
            bound_data = self._outer_product_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.CIRCULAR_CONVOLUTION:
            bound_data = self._circular_convolution_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.ADDITION:
            bound_data = self._addition_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.MULTIPLICATION:
            bound_data = self._multiplication_bind(role.data, filler.data)
        else:
            raise ValueError(f"Unknown binding method: {self.binding_method}")
        
        # Add noise if specified
        if self.noise_level > 0:
            noise = np.random.randn(*bound_data.shape) * self.noise_level
            bound_data = bound_data + noise
        
        # Normalize if specified
        if self.normalize and np.linalg.norm(bound_data) > 0:
            bound_data = bound_data / np.linalg.norm(bound_data)
        
        # Create bound vector
        bound_vector = TPRVector(
            data=bound_data,
            role=role.role,
            filler=filler.filler,
            is_bound=True,
            binding_info={
                'method': self.binding_method.value,
                'role_dim': len(role.data),
                'filler_dim': len(filler.data),
                'noise_level': self.noise_level
            }
        )
        
        self.binding_stats['total_bindings'] += 1
        return bound_vector
    
    def _outer_product_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Outer product binding (standard tensor product)"""
        return np.outer(role_data, filler_data).flatten()
    
    def _circular_convolution_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Circular convolution binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Circular convolution requires same-dimension vectors")
        return np.fft.ifft(np.fft.fft(role_data) * np.fft.fft(filler_data)).real
    
    def _addition_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Simple addition binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Addition binding requires same-dimension vectors")
        return role_data + filler_data
    
    def _multiplication_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Element-wise multiplication binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Multiplication binding requires same-dimension vectors")
        return role_data * filler_data
    
    def unbind(self, bound_vector: Union[TPRVector, np.ndarray], role: Union[str, TPRVector, np.ndarray]) -> TPRVector:
        """
        Attempt to unbind a filler from a bound vector using a role.
        
        Parameters
        ----------
        bound_vector : TPRVector or np.ndarray
            The bound vector to unbind from
        role : str, TPRVector, or np.ndarray
            The role vector to use for unbinding
            
        Returns
        -------
        TPRVector
            Reconstructed filler vector
        """
        # Handle numpy array inputs
        if isinstance(bound_vector, np.ndarray):
            bound_vector = TPRVector(data=bound_vector, role=None, filler=None, is_bound=True)
            
        if isinstance(role, str):
            if role in self.role_vectors:
                role = self.role_vectors[role]
            else:
                warnings.warn(f"Role '{role}' not found in stored vectors")
                return None
        elif isinstance(role, np.ndarray):
            role = TPRVector(data=role, role="numpy_role", filler=None, is_bound=False)
        
        # Perform unbinding based on original binding method
        method = bound_vector.binding_info.get('method', self.binding_method.value)
        
        try:
            if method == 'outer_product':
                unbound_data = self._outer_product_unbind(bound_vector.data, role.data)
            elif method == 'circular_convolution':
                unbound_data = self._circular_convolution_unbind(bound_vector.data, role.data)
            elif method in ['addition', 'multiplication']:
                # These methods are not easily reversible
                warnings.warn(f"Unbinding not reliable for method: {method}")
                unbound_data = bound_vector.data  # Return original
            else:
                raise ValueError(f"Unknown unbinding method: {method}")
            
            # Create unbound vector
            unbound_vector = TPRVector(
                data=unbound_data,
                role=None,
                filler=f"unbound_from_{bound_vector.filler or 'unknown'}",
                is_bound=False,
                binding_info={
                    'type': 'unbound_filler',
                    'original_method': method,
                    'unbound_with_role': role.role
                }
            )
            
            self.binding_stats['successful_unbindings'] += 1
            return unbound_vector
            
        except Exception as e:
            self.binding_stats['failed_unbindings'] += 1
            warnings.warn(f"Unbinding failed: {e}")
            return None
    
    def _outer_product_unbind(self, bound_data: np.ndarray, role_data: np.ndarray) -> np.ndarray:
        """Unbind using outer product (approximate)"""
        # Reshape bound data back to matrix form
        bound_matrix = bound_data.reshape(len(role_data), -1)
        
        # Use pseudo-inverse to approximate unbinding
        role_norm = np.linalg.norm(role_data)
        if role_norm > 0:
            role_normalized = role_data / role_norm
            return bound_matrix.T @ role_normalized
        else:
            return np.zeros(bound_matrix.shape[1])
    
    def _circular_convolution_unbind(self, bound_data: np.ndarray, role_data: np.ndarray) -> np.ndarray:
        """Unbind using circular convolution"""
        # Circular convolution unbinding uses correlation
        role_fft = np.fft.fft(role_data)
        bound_fft = np.fft.fft(bound_data)
        
        # Avoid division by zero
        role_fft_conj = np.conj(role_fft)
        denominator = np.abs(role_fft)**2
        safe_denominator = np.where(denominator > 1e-12, denominator, 1e-12)
        
        unbound_fft = bound_fft * role_fft_conj / safe_denominator
        return np.fft.ifft(unbound_fft).real
    
    def superpose(self, vectors: List[TPRVector], weights: Optional[List[float]] = None) -> TPRVector:
        """
        Create superposition of multiple bound vectors.
        
        Parameters
        ----------
        vectors : List[TPRVector]
            Vectors to superpose
        weights : List[float], optional
            Weights for each vector
            
        Returns
        -------
        TPRVector
            Superposed vector
        """
        if not vectors:
            raise ValueError("Cannot superpose empty vector list")
        
        if weights is None:
            weights = [1.0] * len(vectors)
        
        if len(weights) != len(vectors):
            raise ValueError("Number of weights must match number of vectors")
        
        # Initialize with first vector
        superposed_data = weights[0] * vectors[0].data.copy()
        
        # Add remaining vectors
        for i in range(1, len(vectors)):
            if vectors[i].data.shape != superposed_data.shape:
                raise ValueError("All vectors must have same shape for superposition")
            superposed_data += weights[i] * vectors[i].data
        
        # Normalize if specified
        if self.normalize and np.linalg.norm(superposed_data) > 0:
            superposed_data = superposed_data / np.linalg.norm(superposed_data)
        
        # Create superposed vector
        role_names = [v.role for v in vectors if v.role]
        filler_names = [v.filler for v in vectors if v.filler]
        
        superposed_vector = TPRVector(
            data=superposed_data,
            role=f"superposed_roles_{'+'.join(role_names[:3])}" if role_names else None,
            filler=f"superposed_fillers_{'+'.join(filler_names[:3])}" if filler_names else None,
            is_bound=any(v.is_bound for v in vectors),
            binding_info={
                'type': 'superposition',
                'num_vectors': len(vectors),
                'weights': weights,
                'component_methods': [v.binding_info.get('method', 'unknown') for v in vectors]
            }
        )
        
        return superposed_vector
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get binding operation statistics"""
        total_attempts = (self.binding_stats['successful_unbindings'] + 
                         self.binding_stats['failed_unbindings'])
        
        return {
            'total_bindings': self.binding_stats['total_bindings'],
            'total_unbinding_attempts': total_attempts,
            'successful_unbindings': self.binding_stats['successful_unbindings'],
            'failed_unbindings': self.binding_stats['failed_unbindings'],
            'unbinding_success_rate': (
                self.binding_stats['successful_unbindings'] / total_attempts 
                if total_attempts > 0 else 0.0
            ),
            'stored_role_vectors': len(self.role_vectors),
            'stored_filler_vectors': len(self.filler_vectors),
            'vector_dimension': self.vector_dim,
            'binding_method': self.binding_method.value,
            'normalization_enabled': self.normalize,
            'noise_level': self.noise_level
        }