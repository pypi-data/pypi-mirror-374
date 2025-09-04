#!/usr/bin/env python3
"""
🧪 Comprehensive Holographic Memory Test Suite
==============================================

Complete test coverage for holographic memory algorithms including:
- Holographic Reduced Representations (HRR) - Plate (1995)
- Associative memory operations
- Capacity analysis and performance
- Vector Symbolic Architecture applications

This addresses the critical 7.4% test coverage (5/73 files).

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Plate (1995), Kanerva (1988), Smolensky (1990)
"""

import pytest
import numpy as np
import torch
import sys
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from holographic_memory.hrr_memory import HolographicMemory, HRRConfig
    from holographic_memory.associative_memory import AssociativeMemory
    from holographic_memory.vector_operations import VectorOperations
    from holographic_memory.capacity_analysis import CapacityAnalysis
    from holographic_memory.cleanup_memory import CleanupMemory
except ImportError as e:
    pytest.skip(f"Holographic memory modules not available: {e}", allow_module_level=True)


class TestHolographicMemory:
    """Test core holographic memory implementation."""
    
    def test_hrr_initialization(self):
        """Test HRR memory initialization."""
        config = HRRConfig(dimension=256, noise_level=0.1)
        memory = HolographicMemory(config=config)
        
        assert memory.dimension == 256
        assert memory.noise_level == 0.1
        assert hasattr(memory, 'convolution_bind')
        assert hasattr(memory, 'correlation_unbind')
    
    def test_vector_generation(self):
        """Test random vector generation."""
        memory = HolographicMemory(dimension=128)
        
        # Generate random vectors
        vec1 = memory.generate_vector('ITEM1')
        vec2 = memory.generate_vector('ITEM2')
        
        assert len(vec1) == 128
        assert len(vec2) == 128
        assert not np.allclose(vec1, vec2)  # Should be different
        
        # Should be approximately unit vectors
        assert abs(np.linalg.norm(vec1) - 1.0) < 0.1
        assert abs(np.linalg.norm(vec2) - 1.0) < 0.1
    
    def test_convolution_binding(self):
        """Test circular convolution binding operation."""
        memory = HolographicMemory(dimension=64)
        
        vec_a = np.random.randn(64)
        vec_b = np.random.randn(64)
        
        # Perform circular convolution
        bound = memory.convolution_bind(vec_a, vec_b)
        
        assert len(bound) == 64
        # Result should be different from inputs
        assert not np.allclose(bound, vec_a)
        assert not np.allclose(bound, vec_b)
    
    def test_correlation_unbinding(self):
        """Test circular correlation unbinding operation."""
        memory = HolographicMemory(dimension=128)
        
        vec_a = np.random.randn(128)
        vec_b = np.random.randn(128)
        
        # Bind then unbind
        bound = memory.convolution_bind(vec_a, vec_b)
        unbound = memory.correlation_unbind(bound, vec_a)
        
        # Should recover vec_b with reasonable accuracy
        similarity = np.corrcoef(unbound, vec_b)[0, 1]
        assert abs(similarity) > 0.4  # Should have significant correlation
    
    def test_approximate_inverse(self):
        """Test approximate inverse computation."""
        memory = HolographicMemory(dimension=256)
        
        vec = np.random.randn(256)
        vec_inv = memory.approximate_inverse(vec)
        
        # Binding with inverse should approximate identity
        identity_approx = memory.convolution_bind(vec, vec_inv)
        
        # Check that result has properties of identity (impulse-like)
        # In circular convolution, identity has peak at position 0
        peak_value = abs(identity_approx[0])
        other_values = np.mean(np.abs(identity_approx[1:]))
        
        assert peak_value > 2 * other_values  # Peak should be prominent
    
    def test_superposition_storage(self):
        """Test storage via superposition."""
        memory = HolographicMemory(dimension=512)
        
        # Create multiple associations
        associations = []
        for i in range(5):
            key = memory.generate_vector(f'KEY_{i}')
            value = memory.generate_vector(f'VALUE_{i}')
            association = memory.convolution_bind(key, value)
            associations.append((key, value, association))
        
        # Create superposition
        superposition = sum(assoc[2] for assoc in associations)
        
        # Test retrieval
        key_0, value_0, _ = associations[0]
        retrieved = memory.correlation_unbind(superposition, key_0)
        
        # Should retrieve something similar to value_0
        similarity = np.corrcoef(retrieved, value_0)[0, 1]
        assert abs(similarity) > 0.2  # Some degradation expected with superposition


class TestAssociativeMemory:
    """Test associative memory operations."""
    
    def test_association_storage(self):
        """Test storing key-value associations."""
        memory = AssociativeMemory(dimension=256)
        
        # Store associations
        key1 = 'PERSON1'
        value1 = 'JOHN_SMITH'
        memory.store_association(key1, value1)
        
        key2 = 'PERSON2' 
        value2 = 'MARY_JONES'
        memory.store_association(key2, value2)
        
        assert len(memory.associations) == 2
        assert key1 in memory.associations
        assert key2 in memory.associations
    
    def test_associative_retrieval(self):
        """Test retrieving values by keys."""
        memory = AssociativeMemory(dimension=256)
        
        # Store test association
        key = 'CAPITAL_FRANCE'
        value = 'PARIS'
        memory.store_association(key, value)
        
        # Retrieve
        retrieved = memory.retrieve(key)
        
        # Should retrieve vector similar to stored value
        stored_value = memory.get_vector(value)
        similarity = np.dot(retrieved, stored_value) / (np.linalg.norm(retrieved) * np.linalg.norm(stored_value))
        
        assert similarity > 0.7  # Should have high similarity
    
    def test_partial_key_retrieval(self):
        """Test retrieval with partial/noisy keys."""
        memory = AssociativeMemory(dimension=512)
        
        # Store association
        key = 'COMPLETE_KEY'
        value = 'STORED_VALUE'
        memory.store_association(key, value)
        
        # Create noisy version of key
        original_key_vec = memory.get_vector(key)
        noisy_key = original_key_vec + 0.2 * np.random.randn(512)
        
        # Retrieve with noisy key
        retrieved = memory.retrieve_by_vector(noisy_key)
        
        # Should still retrieve reasonable result
        expected_value_vec = memory.get_vector(value)
        similarity = np.dot(retrieved, expected_value_vec) / (np.linalg.norm(retrieved) * np.linalg.norm(expected_value_vec))
        
        assert similarity > 0.3  # Should maintain some similarity despite noise
    
    def test_content_addressable_retrieval(self):
        """Test content-addressable memory retrieval."""
        memory = AssociativeMemory(dimension=256)
        
        # Store multiple related associations
        memory.store_association('ANIMAL_CAT', 'MEOW_SOUND')
        memory.store_association('ANIMAL_DOG', 'BARK_SOUND')
        memory.store_association('ANIMAL_COW', 'MOO_SOUND')
        
        # Query with partial information
        query_vec = memory.get_vector('ANIMAL_DOG')
        
        # Find most similar association
        best_match = memory.find_best_match(query_vec)
        
        assert best_match is not None
        # Should match the dog association
        assert 'DOG' in best_match or 'BARK' in best_match
    
    def test_heteroassociative_memory(self):
        """Test heteroassociative memory (different domains)."""
        memory = AssociativeMemory(dimension=512)
        
        # Store cross-modal associations (word -> image, sound -> word)
        word_image_pairs = [
            ('WORD_APPLE', 'IMAGE_RED_FRUIT'),
            ('WORD_OCEAN', 'IMAGE_BLUE_WATER'),
            ('WORD_MOUNTAIN', 'IMAGE_HIGH_PEAK')
        ]
        
        for word, image in word_image_pairs:
            memory.store_association(word, image)
        
        # Test retrieval across modalities
        retrieved_image = memory.retrieve('WORD_APPLE')
        expected_image = memory.get_vector('IMAGE_RED_FRUIT')
        
        similarity = np.dot(retrieved_image, expected_image) / (np.linalg.norm(retrieved_image) * np.linalg.norm(expected_image))
        
        assert similarity > 0.5  # Should retrieve associated image
    
    def test_autoassociative_memory(self):
        """Test autoassociative memory (pattern completion)."""
        memory = AssociativeMemory(dimension=256, autoassociative=True)
        
        # Store patterns
        patterns = ['COMPLETE_PATTERN_1', 'COMPLETE_PATTERN_2', 'COMPLETE_PATTERN_3']
        for pattern in patterns:
            memory.store_pattern(pattern)
        
        # Test pattern completion with partial input
        original_pattern = memory.get_vector('COMPLETE_PATTERN_1')
        partial_pattern = original_pattern.copy()
        partial_pattern[100:150] = 0  # Remove part of pattern
        
        # Complete pattern
        completed = memory.complete_pattern(partial_pattern)
        
        # Should be more similar to original than partial
        sim_original = np.dot(completed, original_pattern) / (np.linalg.norm(completed) * np.linalg.norm(original_pattern))
        sim_partial = np.dot(partial_pattern, original_pattern) / (np.linalg.norm(partial_pattern) * np.linalg.norm(original_pattern))
        
        assert sim_original > sim_partial  # Completion should improve similarity


class TestVectorOperations:
    """Test vector operations for holographic memory."""
    
    def test_circular_convolution(self):
        """Test circular convolution implementation."""
        ops = VectorOperations()
        
        a = np.array([1, 2, 3, 4])
        b = np.array([0.5, 1, 0.5, 0])
        
        result = ops.circular_convolution(a, b)
        
        assert len(result) == 4
        # Check specific properties of circular convolution
        assert np.allclose(result, ops.circular_convolution(b, a))  # Commutative
    
    def test_circular_correlation(self):
        """Test circular correlation implementation."""
        ops = VectorOperations()
        
        a = np.random.randn(8)
        b = np.random.randn(8)
        
        # Convolution followed by correlation should approximate original
        convolved = ops.circular_convolution(a, b)
        correlated = ops.circular_correlation(convolved, a)
        
        # Should be similar to b
        similarity = np.corrcoef(correlated, b)[0, 1]
        assert abs(similarity) > 0.5
    
    def test_permutation_operations(self):
        """Test permutation-based operations."""
        ops = VectorOperations()
        
        vec = np.array([1, 2, 3, 4, 5, 6])
        
        # Test permutation and inverse permutation
        permuted = ops.permute(vec, shift=2)
        unpermuted = ops.unpermute(permuted, shift=2)
        
        assert np.allclose(vec, unpermuted)  # Should recover original
    
    def test_normalization_operations(self):
        """Test vector normalization."""
        ops = VectorOperations()
        
        # Test different normalization methods
        vec = np.array([3, 4, 5, 12])  # Non-unit vector
        
        # L2 normalization
        normalized_l2 = ops.normalize(vec, method='l2')
        assert abs(np.linalg.norm(normalized_l2) - 1.0) < 1e-10
        
        # Unit variance normalization
        normalized_var = ops.normalize(vec, method='unit_variance')
        assert abs(np.std(normalized_var) - 1.0) < 1e-10
    
    def test_similarity_measures(self):
        """Test various similarity measures."""
        ops = VectorOperations()
        
        # Similar vectors
        vec_a = np.array([1, 2, 3, 4, 5])
        vec_b = np.array([1.1, 2.1, 2.9, 4.1, 4.9])  # Slightly different
        vec_c = np.array([-1, -2, -3, -4, -5])  # Opposite
        
        # Cosine similarity
        cos_ab = ops.cosine_similarity(vec_a, vec_b)
        cos_ac = ops.cosine_similarity(vec_a, vec_c)
        
        assert cos_ab > cos_ac  # Similar vectors should have higher cosine similarity
        assert cos_ab > 0.9     # Should be high for similar vectors
        assert cos_ac < -0.9    # Should be negative for opposite vectors
        
        # Euclidean distance
        dist_ab = ops.euclidean_distance(vec_a, vec_b)
        dist_ac = ops.euclidean_distance(vec_a, vec_c)
        
        assert dist_ab < dist_ac  # Similar vectors should have smaller distance
    
    def test_fourier_domain_operations(self):
        """Test operations in Fourier domain."""
        ops = VectorOperations()
        
        # Circular convolution via FFT should match direct computation
        a = np.random.randn(16)
        b = np.random.randn(16)
        
        # Direct circular convolution
        direct_result = ops.circular_convolution(a, b)
        
        # FFT-based convolution
        fft_result = ops.fft_convolution(a, b)
        
        assert np.allclose(direct_result, fft_result, atol=1e-10)


class TestCapacityAnalysis:
    """Test capacity analysis for holographic memory."""
    
    def test_theoretical_capacity_bounds(self):
        """Test theoretical capacity calculations."""
        analyzer = CapacityAnalysis(dimension=512)
        
        # Calculate theoretical bounds
        capacity_bound = analyzer.theoretical_capacity()
        
        assert isinstance(capacity_bound, float)
        assert capacity_bound > 0
        # Should be related to dimension (Plate's formula: ~n/(2*log(n)))
        expected_order = 512 / (2 * np.log(512))
        assert 0.1 * expected_order < capacity_bound < 10 * expected_order
    
    def test_empirical_capacity_measurement(self):
        """Test empirical capacity measurement."""
        analyzer = CapacityAnalysis(dimension=256)
        
        # Generate test vectors
        n_items = 10  # Small number for testing
        test_vectors = [np.random.randn(256) for _ in range(n_items)]
        
        # Measure capacity with retrieval accuracy
        capacity_estimate = analyzer.measure_empirical_capacity(test_vectors, threshold=0.5)
        
        assert isinstance(capacity_estimate, int)
        assert 0 <= capacity_estimate <= n_items
    
    def test_capacity_vs_dimension(self):
        """Test how capacity scales with dimension."""
        dimensions = [64, 128, 256]
        capacities = []
        
        for dim in dimensions:
            analyzer = CapacityAnalysis(dimension=dim)
            capacity = analyzer.theoretical_capacity()
            capacities.append(capacity)
        
        # Capacity should generally increase with dimension
        assert capacities[1] > capacities[0]  # 128 > 64
        assert capacities[2] > capacities[1]  # 256 > 128
    
    def test_noise_tolerance_analysis(self):
        """Test noise tolerance of memory operations."""
        analyzer = CapacityAnalysis(dimension=512)
        
        # Create clean association
        key = np.random.randn(512)
        value = np.random.randn(512)
        
        # Test retrieval accuracy with different noise levels
        noise_levels = [0.0, 0.1, 0.2, 0.5]
        accuracies = []
        
        for noise_level in noise_levels:
            accuracy = analyzer.test_noise_tolerance(key, value, noise_level, n_trials=10)
            accuracies.append(accuracy)
        
        # Accuracy should decrease with noise
        assert accuracies[0] >= accuracies[1]  # Clean >= low noise
        assert accuracies[1] >= accuracies[2]  # Low >= medium noise
        assert accuracies[2] >= accuracies[3]  # Medium >= high noise
    
    def test_interference_analysis(self):
        """Test interference between stored memories."""
        analyzer = CapacityAnalysis(dimension=256)
        
        # Store multiple associations
        n_memories = 5
        memories = []
        for i in range(n_memories):
            key = np.random.randn(256)
            value = np.random.randn(256)
            memories.append((key, value))
        
        # Measure interference
        interference_score = analyzer.measure_interference(memories)
        
        assert isinstance(interference_score, float)
        assert 0 <= interference_score <= 1  # Normalized interference measure
    
    def test_retrieval_accuracy_analysis(self):
        """Test retrieval accuracy analysis."""
        analyzer = CapacityAnalysis(dimension=128)
        
        # Create test memory system
        memory = HolographicMemory(dimension=128)
        
        # Store test patterns
        n_patterns = 8
        patterns = []
        for i in range(n_patterns):
            key = f'KEY_{i}'
            value = f'VALUE_{i}'
            memory.store_association(key, value)
            patterns.append((key, value))
        
        # Analyze retrieval accuracy
        accuracy_results = analyzer.analyze_retrieval_accuracy(memory, patterns)
        
        assert 'mean_accuracy' in accuracy_results
        assert 'std_accuracy' in accuracy_results
        assert 'individual_accuracies' in accuracy_results
        assert len(accuracy_results['individual_accuracies']) == n_patterns


class TestCleanupMemory:
    """Test cleanup memory for noise reduction."""
    
    def test_cleanup_initialization(self):
        """Test cleanup memory initialization."""
        cleanup = CleanupMemory(dimension=256, n_prototypes=10)
        
        assert cleanup.dimension == 256
        assert cleanup.n_prototypes == 10
        assert hasattr(cleanup, 'prototypes')
    
    def test_prototype_learning(self):
        """Test learning prototypes from training data."""
        cleanup = CleanupMemory(dimension=128, n_prototypes=5)
        
        # Generate training patterns (clustered)
        training_patterns = []
        for i in range(5):
            center = np.random.randn(128)
            for j in range(10):  # 10 patterns per cluster
                pattern = center + 0.3 * np.random.randn(128)
                training_patterns.append(pattern)
        
        # Learn prototypes
        cleanup.learn_prototypes(training_patterns)
        
        assert len(cleanup.prototypes) == 5
        for prototype in cleanup.prototypes:
            assert len(prototype) == 128
    
    def test_cleanup_operation(self):
        """Test noise cleanup operation."""
        cleanup = CleanupMemory(dimension=64, n_prototypes=3)
        
        # Create clean prototypes
        clean_patterns = [np.random.randn(64) for _ in range(3)]
        cleanup.prototypes = clean_patterns
        
        # Add noise to a pattern
        noisy_pattern = clean_patterns[0] + 0.4 * np.random.randn(64)
        
        # Clean up
        cleaned = cleanup.cleanup(noisy_pattern)
        
        # Should be closer to original than noisy version
        sim_original = np.dot(cleaned, clean_patterns[0])
        sim_noisy = np.dot(noisy_pattern, clean_patterns[0])
        
        assert sim_original >= sim_noisy  # Cleanup should improve similarity
    
    def test_attractor_dynamics(self):
        """Test attractor dynamics in cleanup memory."""
        cleanup = CleanupMemory(dimension=32, n_prototypes=2)
        
        # Simple prototypes
        prototype_1 = np.array([1] * 16 + [-1] * 16)  # Half positive, half negative
        prototype_2 = np.array([-1] * 16 + [1] * 16)  # Opposite pattern
        cleanup.prototypes = [prototype_1, prototype_2]
        
        # Test point closer to prototype 1
        test_point = prototype_1 + 0.2 * np.random.randn(32)
        
        # Iterative cleanup (attractor dynamics)
        cleaned = cleanup.iterative_cleanup(test_point, n_iterations=5)
        
        # Should converge to prototype 1
        sim_1 = np.dot(cleaned, prototype_1)
        sim_2 = np.dot(cleaned, prototype_2)
        
        assert sim_1 > sim_2  # Should be closer to prototype 1
    
    def test_basin_of_attraction(self):
        """Test basin of attraction analysis."""
        cleanup = CleanupMemory(dimension=16, n_prototypes=1)
        
        # Single prototype
        prototype = np.random.randn(16)
        cleanup.prototypes = [prototype]
        
        # Test points at different distances
        distances = [0.1, 0.5, 1.0, 2.0]
        attraction_results = []
        
        for distance in distances:
            test_point = prototype + distance * np.random.randn(16)
            cleaned = cleanup.cleanup(test_point)
            
            # Measure how much it moved toward prototype
            improvement = (np.dot(cleaned, prototype) - np.dot(test_point, prototype))
            attraction_results.append(improvement)
        
        # Close points should be attracted more strongly
        assert attraction_results[0] >= 0  # Should improve
    
    def test_multiple_attractors(self):
        """Test behavior with multiple attractors."""
        cleanup = CleanupMemory(dimension=20, n_prototypes=3)
        
        # Create well-separated prototypes
        prototype_1 = np.concatenate([np.ones(10), np.zeros(10)])
        prototype_2 = np.concatenate([np.zeros(10), np.ones(10)])
        prototype_3 = np.concatenate([-np.ones(10), np.zeros(10)])
        
        cleanup.prototypes = [prototype_1, prototype_2, prototype_3]
        
        # Test cleanup with ambiguous input (equidistant from multiple prototypes)
        ambiguous_input = (prototype_1 + prototype_2) / 2
        
        cleaned = cleanup.cleanup(ambiguous_input)
        
        # Should settle to one of the prototypes
        similarities = [np.dot(cleaned, p) for p in cleanup.prototypes]
        max_sim = max(similarities)
        
        # Should be close to at least one prototype
        assert max_sim > 0.7


class TestApplicationScenarios:
    """Test real-world application scenarios."""
    
    def test_episodic_memory(self):
        """Test episodic memory storage and retrieval."""
        memory = HolographicMemory(dimension=512)
        
        # Store episodic memories (time + event + context)
        episodes = [
            ('MORNING', 'BREAKFAST', 'HOME'),
            ('AFTERNOON', 'MEETING', 'OFFICE'),
            ('EVENING', 'DINNER', 'RESTAURANT')
        ]
        
        stored_episodes = []
        for time, event, context in episodes:
            time_vec = memory.generate_vector(time)
            event_vec = memory.generate_vector(event)
            context_vec = memory.generate_vector(context)
            
            # Bind time + event + context
            episode_vec = memory.convolution_bind(
                time_vec,
                memory.convolution_bind(event_vec, context_vec)
            )
            stored_episodes.append(episode_vec)
        
        # Create episodic memory as superposition
        episodic_memory = sum(stored_episodes)
        
        # Query: What happened in the morning?
        time_query = memory.generate_vector('MORNING')
        response = memory.correlation_unbind(episodic_memory, time_query)
        
        # Should contain information about breakfast and home
        breakfast_vec = memory.generate_vector('BREAKFAST')
        home_vec = memory.generate_vector('HOME')
        
        breakfast_sim = np.dot(response, breakfast_vec) / (np.linalg.norm(response) * np.linalg.norm(breakfast_vec))
        home_sim = np.dot(response, home_vec) / (np.linalg.norm(response) * np.linalg.norm(home_vec))
        
        # Should have some similarity to breakfast and home concepts
        assert breakfast_sim > 0.1
        assert home_sim > 0.1
    
    def test_semantic_memory(self):
        """Test semantic memory for conceptual relationships."""
        memory = HolographicMemory(dimension=1024)  # Larger for semantic complexity
        
        # Store semantic relationships
        relations = [
            ('BIRD', 'CAN_FLY', 'TRUE'),
            ('PENGUIN', 'IS_A', 'BIRD'),
            ('PENGUIN', 'CAN_FLY', 'FALSE'),
            ('SPARROW', 'IS_A', 'BIRD'),
            ('SPARROW', 'CAN_FLY', 'TRUE')
        ]
        
        semantic_memory = np.zeros(1024)
        
        for subject, relation, object_val in relations:
            subj_vec = memory.generate_vector(subject)
            rel_vec = memory.generate_vector(relation)
            obj_vec = memory.generate_vector(object_val)
            
            # Create triple: subject-relation-object
            triple = memory.convolution_bind(
                subj_vec,
                memory.convolution_bind(rel_vec, obj_vec)
            )
            semantic_memory += triple
        
        # Query: Can penguins fly?
        penguin_vec = memory.generate_vector('PENGUIN')
        can_fly_vec = memory.generate_vector('CAN_FLY')
        
        # Unbind to get the answer
        query_vec = memory.convolution_bind(penguin_vec, can_fly_vec)
        answer = memory.correlation_unbind(semantic_memory, query_vec)
        
        # Check similarity to TRUE and FALSE
        true_vec = memory.generate_vector('TRUE')
        false_vec = memory.generate_vector('FALSE')
        
        true_sim = np.dot(answer, true_vec) / (np.linalg.norm(answer) * np.linalg.norm(true_vec))
        false_sim = np.dot(answer, false_vec) / (np.linalg.norm(answer) * np.linalg.norm(false_vec))
        
        # Should be more similar to FALSE (penguins can't fly)
        assert false_sim > true_sim
    
    def test_working_memory(self):
        """Test working memory for temporary storage."""
        working_mem = AssociativeMemory(dimension=256, decay_rate=0.1)
        
        # Store temporary items with decay
        items = ['ITEM1', 'ITEM2', 'ITEM3']
        for i, item in enumerate(items):
            working_mem.store_with_decay(item, f'VALUE_{i}', timestamp=i)
        
        # Later retrieval should show decay effects
        recent_item = working_mem.retrieve('ITEM3')  # Most recent
        old_item = working_mem.retrieve('ITEM1')     # Oldest
        
        # Recent items should be retrieved better
        assert np.linalg.norm(recent_item) >= np.linalg.norm(old_item)
    
    def test_analogical_mapping(self):
        """Test analogical reasoning with holographic memory."""
        memory = HolographicMemory(dimension=512)
        
        # Store analogical structure: A:B :: C:?
        # Example: King:Queen :: Man:Woman
        
        # Create concept vectors
        king = memory.generate_vector('KING')
        queen = memory.generate_vector('QUEEN')
        man = memory.generate_vector('MAN')
        
        # Compute analogy: King - Queen = Man - ?
        # So ? = Man - (King - Queen) = Man - King + Queen
        analogy_result = man - king + queen
        
        # Test if result is similar to 'WOMAN'
        woman = memory.generate_vector('WOMAN')
        similarity = np.dot(analogy_result, woman) / (np.linalg.norm(analogy_result) * np.linalg.norm(woman))
        
        # This is a structural test - actual semantic similarity would require training
        assert isinstance(similarity, float)  # Should compute without error
        assert -1 <= similarity <= 1  # Valid similarity range


# Performance and stress tests
class TestPerformanceAndStress:
    """Performance and stress testing."""
    
    @pytest.mark.slow
    def test_large_scale_storage(self):
        """Test large-scale memory storage."""
        memory = HolographicMemory(dimension=1024)
        
        # Store many associations
        n_associations = 100
        associations = []
        
        for i in range(n_associations):
            key = f'KEY_{i:03d}'
            value = f'VALUE_{i:03d}'
            memory.store_association(key, value)
            associations.append((key, value))
        
        # Test retrieval accuracy
        correct_retrievals = 0
        for key, expected_value in associations[:10]:  # Test first 10
            retrieved = memory.retrieve(key)
            expected = memory.get_vector(expected_value)
            
            similarity = np.dot(retrieved, expected) / (np.linalg.norm(retrieved) * np.linalg.norm(expected))
            if similarity > 0.5:
                correct_retrievals += 1
        
        # Should retrieve most items correctly despite interference
        accuracy = correct_retrievals / 10
        assert accuracy > 0.3  # Some degradation expected with many items
    
    @pytest.mark.slow
    def test_memory_consolidation(self):
        """Test memory consolidation over time."""
        memory = HolographicMemory(dimension=256)
        
        # Store memories with different strengths
        strong_memories = [(f'STRONG_{i}', f'VAL_{i}') for i in range(5)]
        weak_memories = [(f'WEAK_{i}', f'VAL_{i}') for i in range(10)]
        
        # Store with different repetitions (strengthening)
        for key, value in strong_memories:
            for _ in range(5):  # Repeat 5 times
                memory.store_association(key, value)
        
        for key, value in weak_memories:
            memory.store_association(key, value)  # Store once
        
        # Test retrieval - strong memories should be better retrieved
        strong_similarities = []
        weak_similarities = []
        
        for key, value in strong_memories:
            retrieved = memory.retrieve(key)
            expected = memory.get_vector(value)
            sim = np.dot(retrieved, expected) / (np.linalg.norm(retrieved) * np.linalg.norm(expected))
            strong_similarities.append(sim)
        
        for key, value in weak_memories:
            retrieved = memory.retrieve(key)
            expected = memory.get_vector(value)
            sim = np.dot(retrieved, expected) / (np.linalg.norm(retrieved) * np.linalg.norm(expected))
            weak_similarities.append(sim)
        
        # Strong memories should have better average retrieval
        avg_strong = np.mean(strong_similarities)
        avg_weak = np.mean(weak_similarities)
        
        assert avg_strong >= avg_weak  # Strengthened memories should be better
    
    @pytest.mark.slow
    def test_memory_interference_patterns(self):
        """Test patterns of memory interference."""
        memory = HolographicMemory(dimension=512)
        
        # Create related memory groups that might interfere
        group1_memories = [('CAT', 'ANIMAL'), ('DOG', 'ANIMAL'), ('BIRD', 'ANIMAL')]
        group2_memories = [('ROSE', 'FLOWER'), ('DAISY', 'FLOWER'), ('TULIP', 'FLOWER')]
        
        # Store all memories
        for key, value in group1_memories + group2_memories:
            memory.store_association(key, value)
        
        # Test within-group vs between-group interference
        # Retrieve from group 1
        cat_retrieved = memory.retrieve('CAT')
        animal_vec = memory.get_vector('ANIMAL')
        flower_vec = memory.get_vector('FLOWER')
        
        # Should be more similar to 'ANIMAL' than 'FLOWER'
        sim_animal = np.dot(cat_retrieved, animal_vec) / (np.linalg.norm(cat_retrieved) * np.linalg.norm(animal_vec))
        sim_flower = np.dot(cat_retrieved, flower_vec) / (np.linalg.norm(cat_retrieved) * np.linalg.norm(flower_vec))
        
        assert sim_animal > sim_flower  # Should retrieve correct category


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])