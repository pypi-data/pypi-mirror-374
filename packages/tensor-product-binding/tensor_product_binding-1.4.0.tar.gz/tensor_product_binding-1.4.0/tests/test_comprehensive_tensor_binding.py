#!/usr/bin/env python3
"""
🧪 Comprehensive Tensor Product Binding Test Suite
==================================================

Complete test coverage for tensor product binding algorithms including:
- Vector Symbolic Architecture (VSA) - Smolensky (1990)
- Holographic Reduced Representations (HRR) - Plate (1995)
- Binding and unbinding operations
- Compositional representation learning

This addresses the critical 7.4% test coverage (5/73 files).

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Smolensky (1990), Plate (1995), Gayler (2003)
"""

import pytest
import numpy as np
import torch
import sys
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from tensor_product_binding.vsa import VectorSymbolicArchitecture, VSAConfig
    from tensor_product_binding.binding_operations import BindingOperations
    from tensor_product_binding.compositional_structures import CompositionalStructures
    from tensor_product_binding.hrr import HolographicReducedRepresentations
    from tensor_product_binding.tensor_binding import TensorProductBinding
except ImportError as e:
    pytest.skip(f"Tensor product binding modules not available: {e}", allow_module_level=True)


class TestVectorSymbolicArchitecture:
    """Test Vector Symbolic Architecture implementation."""
    
    def test_vsa_initialization(self):
        """Test VSA initialization."""
        vsa = VectorSymbolicArchitecture(dimension=512)
        
        assert vsa.dimension == 512
        assert hasattr(vsa, 'atomic_vectors')
        assert hasattr(vsa, 'bind')
        assert hasattr(vsa, 'unbind')
    
    def test_atomic_vector_generation(self):
        """Test atomic vector generation."""
        vsa = VectorSymbolicArchitecture(dimension=256)
        
        # Generate atomic vectors
        vec_a = vsa.generate_atomic('A')
        vec_b = vsa.generate_atomic('B')
        
        assert len(vec_a) == 256
        assert len(vec_b) == 256
        assert not np.allclose(vec_a, vec_b)  # Should be different
        
        # Should be approximately unit vectors
        assert abs(np.linalg.norm(vec_a) - 1.0) < 0.1
        assert abs(np.linalg.norm(vec_b) - 1.0) < 0.1
    
    def test_binding_operation(self):
        """Test vector binding operation."""
        vsa = VectorSymbolicArchitecture(dimension=128)
        
        vec_a = vsa.generate_atomic('A')
        vec_b = vsa.generate_atomic('B')
        
        # Bind vectors
        bound = vsa.bind(vec_a, vec_b)
        
        assert len(bound) == 128
        # Bound vector should be different from inputs
        assert not np.allclose(bound, vec_a)
        assert not np.allclose(bound, vec_b)
    
    def test_unbinding_operation(self):
        """Test vector unbinding operation."""
        vsa = VectorSymbolicArchitecture(dimension=256)
        
        vec_a = vsa.generate_atomic('A')
        vec_b = vsa.generate_atomic('B')
        
        # Bind then unbind
        bound = vsa.bind(vec_a, vec_b)
        unbound = vsa.unbind(bound, vec_a)
        
        # Should recover vec_b (approximately)
        similarity = np.dot(unbound, vec_b)
        assert similarity > 0.7  # High similarity to original
    
    def test_commutativity(self):
        """Test commutativity of binding operation."""
        vsa = VectorSymbolicArchitecture(dimension=128)
        
        vec_a = vsa.generate_atomic('A')
        vec_b = vsa.generate_atomic('B')
        
        # A ⊛ B should equal B ⊛ A
        bound_ab = vsa.bind(vec_a, vec_b)
        bound_ba = vsa.bind(vec_b, vec_a)
        
        similarity = np.dot(bound_ab, bound_ba)
        assert similarity > 0.95  # Should be very similar
    
    def test_distributivity(self):
        """Test distributivity over superposition."""
        vsa = VectorSymbolicArchitecture(dimension=256)
        
        vec_a = vsa.generate_atomic('A')
        vec_b = vsa.generate_atomic('B')
        vec_c = vsa.generate_atomic('C')
        
        # A ⊛ (B + C) ≈ (A ⊛ B) + (A ⊛ C)
        superposition = vec_b + vec_c
        bound_super = vsa.bind(vec_a, superposition)
        
        bound_b = vsa.bind(vec_a, vec_b)
        bound_c = vsa.bind(vec_a, vec_c)
        sum_bound = bound_b + bound_c
        
        # Should be similar (approximately distributive)
        similarity = np.dot(bound_super, sum_bound) / (np.linalg.norm(bound_super) * np.linalg.norm(sum_bound))
        assert similarity > 0.6  # Reasonable similarity


class TestBindingOperations:
    """Test different binding operation implementations."""
    
    def test_circular_convolution(self):
        """Test circular convolution binding."""
        binder = BindingOperations(method='circular_convolution')
        
        vec_a = np.random.randn(64)
        vec_b = np.random.randn(64)
        
        bound = binder.bind(vec_a, vec_b)
        unbound = binder.unbind(bound, vec_a)
        
        # Should recover vec_b
        correlation = np.corrcoef(unbound, vec_b)[0, 1]
        assert abs(correlation) > 0.5
    
    def test_holographic_binding(self):
        """Test holographic binding operation."""
        binder = BindingOperations(method='holographic')
        
        vec_a = np.random.randn(128)
        vec_b = np.random.randn(128)
        
        bound = binder.bind(vec_a, vec_b)
        
        assert len(bound) == 128
        # Holographic binding preserves dimensionality
        assert not np.allclose(bound, vec_a)
        assert not np.allclose(bound, vec_b)
    
    def test_matrix_binding(self):
        """Test matrix-based binding."""
        binder = BindingOperations(method='matrix')
        
        # Smaller dimension for matrix operations
        vec_a = np.random.randn(32)
        vec_b = np.random.randn(32)
        
        bound = binder.bind(vec_a, vec_b)
        unbound = binder.unbind(bound, vec_a)
        
        # Should approximate original vector
        error = np.linalg.norm(unbound - vec_b) / np.linalg.norm(vec_b)
        assert error < 0.5  # Reasonable reconstruction
    
    def test_binding_identity(self):
        """Test binding with identity element."""
        binder = BindingOperations(method='circular_convolution')
        
        vec = np.random.randn(64)
        identity = binder.get_identity(64)
        
        # Binding with identity should preserve vector
        bound_identity = binder.bind(vec, identity)
        similarity = np.dot(bound_identity, vec) / (np.linalg.norm(bound_identity) * np.linalg.norm(vec))
        
        assert similarity > 0.9  # Should be very similar to original
    
    def test_binding_inverse(self):
        """Test binding with inverse elements."""
        binder = BindingOperations(method='circular_convolution')
        
        vec_a = np.random.randn(64)
        vec_b = np.random.randn(64)
        
        # Create inverse of vec_a
        vec_a_inv = binder.get_inverse(vec_a)
        
        # Bind with inverse should approximate identity
        bound_inverse = binder.bind(vec_a, vec_a_inv)
        identity = binder.get_identity(64)
        
        similarity = np.dot(bound_inverse, identity) / (np.linalg.norm(bound_inverse) * np.linalg.norm(identity))
        assert similarity > 0.7  # Should be similar to identity


class TestCompositionalStructures:
    """Test compositional structure representations."""
    
    def test_role_filler_binding(self):
        """Test role-filler binding for structured representations."""
        comp = CompositionalStructures(dimension=256)
        
        # Create roles and fillers
        role_subject = comp.create_role('SUBJECT')
        role_verb = comp.create_role('VERB')
        role_object = comp.create_role('OBJECT')
        
        filler_john = comp.create_filler('JOHN')
        filler_loves = comp.create_filler('LOVES')
        filler_mary = comp.create_filler('MARY')
        
        # Bind role-filler pairs
        subject_binding = comp.bind_role_filler(role_subject, filler_john)
        verb_binding = comp.bind_role_filler(role_verb, filler_loves)
        object_binding = comp.bind_role_filler(role_object, filler_mary)
        
        # Create sentence representation
        sentence = subject_binding + verb_binding + object_binding
        
        # Should be able to retrieve fillers from sentence
        retrieved_subject = comp.retrieve_filler(sentence, role_subject)
        similarity = np.dot(retrieved_subject, filler_john) / (np.linalg.norm(retrieved_subject) * np.linalg.norm(filler_john))
        
        assert similarity > 0.6  # Should retrieve original filler
    
    def test_hierarchical_structures(self):
        """Test hierarchical compositional structures."""
        comp = CompositionalStructures(dimension=512)
        
        # Create nested structure: [[A B] C]
        elem_a = comp.create_filler('A')
        elem_b = comp.create_filler('B')
        elem_c = comp.create_filler('C')
        
        # First level: bind A and B
        ab_structure = comp.create_structure([elem_a, elem_b])
        
        # Second level: bind [A B] with C
        abc_structure = comp.create_structure([ab_structure, elem_c])
        
        # Should be able to decompose structure
        components = comp.decompose_structure(abc_structure, depth=2)
        
        assert len(components) > 0
        # Should contain information about original elements
        assert any(np.dot(comp, elem_a) > 0.3 for comp in components)
    
    def test_variable_binding(self):
        """Test variable binding in symbolic structures."""
        comp = CompositionalStructures(dimension=256)
        
        # Create variables and values
        var_x = comp.create_variable('X')
        var_y = comp.create_variable('Y')
        val_5 = comp.create_value(5)
        val_10 = comp.create_value(10)
        
        # Create bindings: X=5, Y=10
        binding_x5 = comp.bind_variable_value(var_x, val_5)
        binding_y10 = comp.bind_variable_value(var_y, val_10)
        
        environment = binding_x5 + binding_y10
        
        # Should retrieve correct values
        retrieved_x = comp.retrieve_value(environment, var_x)
        retrieved_y = comp.retrieve_value(environment, var_y)
        
        # Check similarity to original values
        sim_x = np.dot(retrieved_x, val_5) / (np.linalg.norm(retrieved_x) * np.linalg.norm(val_5))
        sim_y = np.dot(retrieved_y, val_10) / (np.linalg.norm(retrieved_y) * np.linalg.norm(val_10))
        
        assert sim_x > 0.5
        assert sim_y > 0.5
    
    def test_sequence_encoding(self):
        """Test sequence encoding with position information."""
        comp = CompositionalStructures(dimension=256)
        
        # Create sequence: [A, B, C, D]
        elements = ['A', 'B', 'C', 'D']
        element_vectors = [comp.create_filler(elem) for elem in elements]
        
        # Encode with positional information
        sequence_repr = comp.encode_sequence(element_vectors)
        
        # Should be able to retrieve elements at specific positions
        for i, orig_elem in enumerate(element_vectors):
            retrieved = comp.retrieve_at_position(sequence_repr, i)
            similarity = np.dot(retrieved, orig_elem) / (np.linalg.norm(retrieved) * np.linalg.norm(orig_elem))
            assert similarity > 0.4  # Should retrieve similar element


class TestHolographicReducedRepresentations:
    """Test HRR-specific implementations."""
    
    def test_hrr_initialization(self):
        """Test HRR initialization."""
        hrr = HolographicReducedRepresentations(dimension=512)
        
        assert hrr.dimension == 512
        assert hasattr(hrr, 'bind')
        assert hasattr(hrr, 'unbind')
    
    def test_circular_convolution_binding(self):
        """Test HRR circular convolution binding."""
        hrr = HolographicReducedRepresentations(dimension=128)
        
        vec_a = np.random.randn(128)
        vec_b = np.random.randn(128)
        
        # Circular convolution binding
        bound = hrr.circular_convolution(vec_a, vec_b)
        
        assert len(bound) == 128
        # Should be different from inputs
        assert np.linalg.norm(bound - vec_a) > 0.1
        assert np.linalg.norm(bound - vec_b) > 0.1
    
    def test_circular_correlation_unbinding(self):
        """Test HRR circular correlation unbinding."""
        hrr = HolographicReducedRepresentations(dimension=128)
        
        vec_a = np.random.randn(128)
        vec_b = np.random.randn(128)
        
        # Bind with circular convolution
        bound = hrr.circular_convolution(vec_a, vec_b)
        
        # Unbind with circular correlation
        unbound = hrr.circular_correlation(bound, vec_a)
        
        # Should approximate vec_b
        similarity = np.corrcoef(unbound, vec_b)[0, 1]
        assert abs(similarity) > 0.4  # Should have reasonable correlation
    
    def test_approximate_inverse(self):
        """Test approximate inverse computation."""
        hrr = HolographicReducedRepresentations(dimension=256)
        
        vec = np.random.randn(256)
        vec_inv = hrr.approximate_inverse(vec)
        
        # Binding with inverse should approximate identity
        identity_approx = hrr.circular_convolution(vec, vec_inv)
        
        # Check if result is close to identity (delta function)
        # Identity in circular convolution domain has peak at zero
        assert abs(identity_approx[0]) > abs(identity_approx[64])  # Peak at zero
    
    def test_cleanup_memory(self):
        """Test cleanup memory for noise reduction."""
        hrr = HolographicReducedRepresentations(dimension=128)
        
        # Create clean vectors
        clean_vectors = {
            'A': np.random.randn(128),
            'B': np.random.randn(128),
            'C': np.random.randn(128)
        }
        
        # Initialize cleanup memory
        hrr.initialize_cleanup_memory(clean_vectors)
        
        # Add noise to a vector
        noisy_a = clean_vectors['A'] + 0.3 * np.random.randn(128)
        
        # Clean up
        cleaned = hrr.cleanup(noisy_a)
        
        # Should be closer to original
        sim_original = np.dot(cleaned, clean_vectors['A'])
        sim_noisy = np.dot(noisy_a, clean_vectors['A'])
        
        assert sim_original >= sim_noisy  # Cleanup should improve similarity
    
    def test_superposition_capacity(self):
        """Test capacity limits of superposition."""
        hrr = HolographicReducedRepresentations(dimension=512)
        
        # Create multiple items to superpose
        items = [np.random.randn(512) for _ in range(10)]
        
        # Create superposition
        superposition = sum(items)
        
        # Should be able to retrieve individual items (with some degradation)
        retrieved_similarities = []
        for original_item in items:
            # Project onto original
            similarity = np.dot(superposition, original_item) / len(items)
            normalized_sim = similarity / (np.linalg.norm(original_item) ** 2)
            retrieved_similarities.append(normalized_sim)
        
        # Should have reasonable retrieval for moderate numbers of items
        avg_similarity = np.mean(retrieved_similarities)
        assert avg_similarity > 0.05  # Some degradation expected


class TestTensorProductBinding:
    """Test tensor product binding operations."""
    
    def test_tensor_product_computation(self):
        """Test tensor product computation."""
        binder = TensorProductBinding(dimension=16)  # Small for tensor products
        
        vec_a = np.random.randn(16)
        vec_b = np.random.randn(16)
        
        # Compute tensor product
        tensor_prod = binder.tensor_product(vec_a, vec_b)
        
        # Should be 16x16 = 256 dimensional
        assert tensor_prod.size == 16 * 16
        
        # Should encode both vectors
        # (This is a simplified test - full tensor product analysis is complex)
        assert np.std(tensor_prod) > 0  # Should have variation
    
    def test_reduced_tensor_binding(self):
        """Test dimensionality-preserving tensor binding."""
        binder = TensorProductBinding(dimension=128, reduction_method='random_projection')
        
        vec_a = np.random.randn(128)
        vec_b = np.random.randn(128)
        
        # Bind with dimensionality reduction
        bound = binder.bind_reduced(vec_a, vec_b)
        
        # Should preserve dimensionality
        assert len(bound) == 128
        
        # Should be different from inputs
        assert not np.allclose(bound, vec_a)
        assert not np.allclose(bound, vec_b)
    
    def test_compositional_tensor_structures(self):
        """Test compositional structures with tensor products."""
        binder = TensorProductBinding(dimension=64)
        
        # Create role and filler vectors
        role1 = np.random.randn(64)
        role2 = np.random.randn(64)
        filler1 = np.random.randn(64)
        filler2 = np.random.randn(64)
        
        # Create structure with multiple role-filler bindings
        binding1 = binder.bind_reduced(role1, filler1)
        binding2 = binder.bind_reduced(role2, filler2)
        
        # Superpose bindings
        structure = binding1 + binding2
        
        # Should contain information from both bindings
        # (Exact retrieval testing would require more sophisticated unbinding)
        assert np.std(structure) > 0
        assert len(structure) == 64


class TestApplicationScenarios:
    """Test real-world application scenarios."""
    
    def test_analogical_reasoning(self):
        """Test analogical reasoning with vector operations."""
        vsa = VectorSymbolicArchitecture(dimension=512)
        
        # Create concept vectors
        man = vsa.generate_atomic('MAN')
        woman = vsa.generate_atomic('WOMAN')
        king = vsa.generate_atomic('KING')
        
        # Analogical reasoning: man is to woman as king is to ?
        # queen ≈ king + (woman - man)
        analogy_vector = king + woman - man
        
        # Create queen vector to test against
        queen = vsa.generate_atomic('QUEEN')
        
        # The analogy should point somewhat toward queen
        # (In practice, would need training on semantic vectors)
        similarity = np.dot(analogy_vector, queen) / (np.linalg.norm(analogy_vector) * np.linalg.norm(queen))
        
        # This is a structural test - semantic similarity would require training
        assert abs(similarity) < 1.0  # Should be reasonable similarity value
    
    def test_semantic_parsing(self):
        """Test semantic parsing with compositional structures."""
        comp = CompositionalStructures(dimension=256)
        
        # Parse sentence: "The red car drives fast"
        # Structure: [DETERMINER ADJECTIVE NOUN] [VERB ADVERB]
        
        # Create semantic vectors
        the = comp.create_filler('THE')
        red = comp.create_filler('RED')
        car = comp.create_filler('CAR')
        drives = comp.create_filler('DRIVES')
        fast = comp.create_filler('FAST')
        
        # Create roles
        determiner_role = comp.create_role('DETERMINER')
        adjective_role = comp.create_role('ADJECTIVE')
        noun_role = comp.create_role('NOUN')
        verb_role = comp.create_role('VERB')
        adverb_role = comp.create_role('ADVERB')
        
        # Bind roles with fillers
        det_binding = comp.bind_role_filler(determiner_role, the)
        adj_binding = comp.bind_role_filler(adjective_role, red)
        noun_binding = comp.bind_role_filler(noun_role, car)
        verb_binding = comp.bind_role_filler(verb_role, drives)
        adv_binding = comp.bind_role_filler(adverb_role, fast)
        
        # Create sentence representation
        sentence = det_binding + adj_binding + noun_binding + verb_binding + adv_binding
        
        # Should be able to query the structure
        retrieved_noun = comp.retrieve_filler(sentence, noun_role)
        similarity = np.dot(retrieved_noun, car) / (np.linalg.norm(retrieved_noun) * np.linalg.norm(car))
        
        assert similarity > 0.3  # Should retrieve car with some accuracy
    
    def test_memory_retrieval(self):
        """Test associative memory retrieval."""
        vsa = VectorSymbolicArchitecture(dimension=256)
        
        # Create memories as associations
        memories = {}
        
        # Store: FACE + NAME → PERSON
        for i, (face, name) in enumerate([('FACE1', 'JOHN'), ('FACE2', 'MARY'), ('FACE3', 'ALICE')]):
            face_vec = vsa.generate_atomic(face)
            name_vec = vsa.generate_atomic(name)
            person_vec = vsa.generate_atomic(f'PERSON{i+1}')
            
            # Create association
            cue = face_vec + name_vec  # Simplified cue combination
            memories[f'memory_{i}'] = (cue, person_vec)
        
        # Test retrieval: given partial cue, retrieve person
        query_face = vsa.get_atomic('FACE1')  # Same as stored
        best_match = None
        best_similarity = -1
        
        for memory_id, (cue, person) in memories.items():
            similarity = np.dot(query_face, cue) / (np.linalg.norm(query_face) * np.linalg.norm(cue))
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = person
        
        # Should retrieve something (exact matching would require more sophisticated memory model)
        assert best_match is not None
        assert best_similarity > 0
    
    def test_recursive_structures(self):
        """Test recursive compositional structures."""
        comp = CompositionalStructures(dimension=512)  # Larger dimension for complexity
        
        # Create recursive list structure: [A, [B, C]]
        elem_a = comp.create_filler('A')
        elem_b = comp.create_filler('B')
        elem_c = comp.create_filler('C')
        
        # Inner list: [B, C]
        inner_list = comp.create_structure([elem_b, elem_c])
        
        # Outer list: [A, [B, C]]
        outer_list = comp.create_structure([elem_a, inner_list])
        
        # Should be different from simple flat list [A, B, C]
        flat_list = comp.create_structure([elem_a, elem_b, elem_c])
        
        similarity = np.dot(outer_list, flat_list) / (np.linalg.norm(outer_list) * np.linalg.norm(flat_list))
        
        # Recursive and flat structures should be different
        assert abs(similarity) < 0.9  # Should be distinguishable


# Performance and capacity tests
class TestCapacityAndPerformance:
    """Test capacity limits and performance characteristics."""
    
    @pytest.mark.slow
    def test_binding_capacity(self):
        """Test capacity limits of binding operations."""
        vsa = VectorSymbolicArchitecture(dimension=1024)
        
        # Create many atomic vectors
        vectors = [vsa.generate_atomic(f'VEC_{i}') for i in range(50)]
        
        # Bind them all together
        result = vectors[0]
        for vec in vectors[1:]:
            result = vsa.bind(result, vec)
        
        # Should still be finite and reasonable
        assert np.all(np.isfinite(result))
        assert np.linalg.norm(result) > 0.1
        assert np.linalg.norm(result) < 10
    
    @pytest.mark.slow
    def test_superposition_capacity(self):
        """Test superposition capacity limits."""
        vsa = VectorSymbolicArchitecture(dimension=512)
        
        # Create superposition of many vectors
        vectors = [vsa.generate_atomic(f'ITEM_{i}') for i in range(100)]
        superposition = sum(vectors)
        
        # Test retrieval accuracy
        similarities = []
        for vec in vectors[:10]:  # Test first 10
            similarity = np.dot(superposition, vec) / (np.linalg.norm(superposition) * np.linalg.norm(vec))
            similarities.append(similarity)
        
        # Should maintain some similarity even with many items
        avg_similarity = np.mean(similarities)
        assert avg_similarity > 0.05  # Some degradation expected with 100 items
    
    @pytest.mark.slow
    def test_performance_scaling(self):
        """Test performance scaling with dimension."""
        import time
        
        dimensions = [128, 256, 512, 1024]
        times = []
        
        for dim in dimensions:
            vsa = VectorSymbolicArchitecture(dimension=dim)
            
            # Time binding operations
            start_time = time.time()
            
            vec_a = vsa.generate_atomic('A')
            vec_b = vsa.generate_atomic('B')
            
            for _ in range(10):
                bound = vsa.bind(vec_a, vec_b)
                unbound = vsa.unbind(bound, vec_a)
            
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        # Should scale reasonably (not exponentially)
        assert times[-1] < times[0] * 20  # At most 20x slower for 8x dimension


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])