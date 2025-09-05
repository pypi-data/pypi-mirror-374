"""
🔧 Vector Utils
================

🔬 Research Foundation:
======================
Based on holographic and vector symbolic architectures:
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges"
🎯 ELI5 Summary:
This is like a toolbox full of helpful utilities! Just like how a carpenter has 
different tools for different jobs (hammer, screwdriver, saw), this file contains helpful 
functions that other parts of our code use to get their work done.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

"""
"""
🧮 Vector Utility Functions for Holographic Memory Systems
=========================================================

🧠 ELI5 Explanation:
Think of holographic memory like a magic photo album where each photo can store thousands 
of overlapping images. When you want to remember something, you shine a "search light" 
(query vector) on the photo, and all related memories light up at once. The vector 
utilities here are like the tools for creating these magic photos - they help make 
vectors (mathematical lists of numbers) that can store and retrieve memories by:

1. Creating random "memory slots" (vectors) that don't interfere with each other
2. Making sure all vectors have the right "brightness" (normalization) so they work together
3. Adding controlled "static" (noise) to test how robust the memories are
4. Measuring how "similar" different memories are to find the right one
5. Organizing vectors so they're independent (orthogonalization) like separate TV channels

Just like how a hologram can store multiple 3D images in one piece of film, these vectors 
can store multiple memories in one mathematical space. The key insight from Tony Plate's 
research is that you can bind concepts together using special math operations (like 
circular convolution) and later unbind them to get the original concepts back.

📚 Research Foundation:  
- Plate, T. (1995) "Holographic Reduced Representations" IEEE Transactions on Neural Networks
- Plate, T. (2003) "Holographic Reduced Representation: Distributed Representation of Cognitive Structures"
- Kanerva, P. (2009) "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation"
- Gayler, R. (2003) "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience"

Key mathematical insight: Circular convolution (⊛) allows binding of concepts:
    memory = concept_A ⊛ concept_B
    concept_A ≈ memory ⊛ concept_B⁻¹  (where concept_B⁻¹ is approximate inverse)

🏗️ Vector Operations Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    VECTOR SPACE OPERATIONS                   │
├─────────────────────────────────────────────────────────────┤
│  Random Vector Creation → Normalization → Binding/Storage   │
│           ↓                      ↓             ↓            │
│    [0.1, -0.3, 0.7,...]  →  [L2 norm = 1]  →  Memory       │
│           ↓                      ↓             ↓            │
│    Gaussian/Uniform      →   Unit vectors   →  Holographic  │
│    Binary/Sparse         →   L1/L2/Max     →  Representation│
│                                                              │
│  Query → Similarity Computation → Memory Retrieval          │
│    ↓           ↓                      ↓                     │
│ [query]  → cosine/dot/correlation → [best_match]           │
│                                                              │
│  Noise Addition ← Robustness Testing ← Statistical Analysis │
│        ↓               ↓                      ↓              │
│ Gaussian/Salt&Pepper → Performance → Sparsity/Norms         │
└─────────────────────────────────────────────────────────────┘

🔧 Usage Examples:
```python
# Create a set of orthogonal "concept" vectors for a vocabulary
vocab_vectors = create_random_vectors(
    n_vectors=1000,      # 1000 word concepts
    vector_dim=512,      # 512-dimensional space
    distribution='gaussian',
    normalize=True,      # Unit vectors for stable binding
    seed=42
)

# Bind two concepts together (simplified - real binding uses convolution)
concept_A = vocab_vectors[0]  # "red"
concept_B = vocab_vectors[1]  # "car"
# In full implementation: bound_concept = circular_convolve(concept_A, concept_B)

# Test memory robustness with noise
noisy_query = add_noise(concept_A, noise_level=0.1, noise_type='gaussian')
similarity = compute_similarity(concept_A, noisy_query, metric='cosine')
print(f"Robustness: {similarity:.3f}")  # Should be high (>0.9)

# Analyze vector space properties
stats = vector_statistics(vocab_vectors)
print(f"Average similarity: {stats['similarities']['mean']:.3f}")  # Should be near 0
```

⚙️ Mathematical Foundations:
- **Normalization**: ||v||₂ = 1 ensures stable circular convolution operations
- **Orthogonality**: ⟨vᵢ, vⱼ⟩ ≈ 0 for i≠j minimizes interference between concepts  
- **Binding**: c = a ⊛ b where ⊛ is circular convolution: cₖ = Σᵢ aᵢ × b₍ₖ₋ᵢ₎mod n
- **Unbinding**: a ≈ c ⊛ b* where b* is approximate inverse of b
- **Similarity**: Used for cleanup/retrieval via cosine similarity or correlation
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Union
import warnings


def create_random_vectors(n_vectors: int, 
                         vector_dim: int,
                         distribution: str = 'gaussian',
                         normalize: bool = True,
                         seed: Optional[int] = None) -> np.ndarray:
    """
    🎲 Create Random Concept Vectors for Holographic Memory
    
    Creates a vocabulary of random vectors that serve as the foundation for holographic 
    memory operations. Each vector represents a unique concept that can be bound with 
    others using circular convolution to form complex memories.
    
    🧠 Holographic Memory Context:
    In Plate's HRR system, we need a vocabulary of approximately orthogonal vectors
    to represent atomic concepts (words, objects, relations). These vectors must be:
    - Nearly orthogonal to minimize interference when bound together
    - Unit normalized for stable circular convolution operations  
    - Randomly distributed to ensure good coverage of the vector space
    
    Parameters
    ----------
    n_vectors : int
        Number of concept vectors to create (typical: 1000-10000 for vocabulary)
    vector_dim : int
        Dimension of vector space (typical: 512-2048 for good capacity)
    distribution : str, default='gaussian'
        Distribution type ('gaussian', 'uniform', 'binary', 'sparse')
        Note: Gaussian is preferred for HRR as it approximates orthogonality
    normalize : bool, default=True
        Whether to normalize to unit length (required for stable binding)
    seed : int, optional
        Random seed for reproducible concept vocabularies
        
    Returns
    -------
    np.ndarray
        Concept vocabulary array of shape (n_vectors, vector_dim)
        Each row is a unit-normalized concept vector ready for binding
        
    Mathematical Note:
    For HRR stability, vectors should satisfy: ||vᵢ|| = 1 and ⟨vᵢ, vⱼ⟩ ≈ 0 for i≠j
    """
    if seed is not None:
        np.random.seed(seed)
    
    if distribution == 'gaussian':
        vectors = np.random.randn(n_vectors, vector_dim)
    elif distribution == 'uniform':
        vectors = np.random.uniform(-1, 1, (n_vectors, vector_dim))
    elif distribution == 'binary':
        vectors = np.random.choice([-1, 1], (n_vectors, vector_dim))
    elif distribution == 'sparse':
        vectors = np.random.randn(n_vectors, vector_dim)
        # Make 90% of elements zero for sparsity
        mask = np.random.random((n_vectors, vector_dim)) > 0.1
        vectors[~mask] = 0
    else:
        raise ValueError(f"Unknown distribution: {distribution}")
    
    if normalize:
        vectors = normalize_vector(vectors)
    
    return vectors


def normalize_vector(vectors: np.ndarray, 
                    method: str = 'l2',
                    axis: int = -1) -> np.ndarray:
    """
    📏 Normalize Vectors for Holographic Memory Operations
    
    Normalizes vectors to ensure stable circular convolution binding operations.
    In holographic memory systems, normalization is critical because circular 
    convolution can cause vector magnitudes to grow exponentially with repeated 
    binding operations.
    
    🧠 HRR Mathematical Foundation:
    L2 normalization ensures ||v|| = 1, which is essential because:
    - Circular convolution preserves magnitude: ||a ⊛ b|| ≈ ||a|| × ||b||
    - Unit vectors prevent exponential growth during recursive binding
    - Stable magnitudes enable reliable similarity-based retrieval
    
    Parameters
    ----------
    vectors : np.ndarray
        Vector(s) to normalize (can be single vector or batch)
    method : str, default='l2'
        Normalization method:
        - 'l2': Euclidean norm (preferred for HRR)
        - 'l1': Manhattan norm 
        - 'max': Max element normalization
        - 'unit_variance': Z-score normalization
    axis : int, default=-1
        Axis along which to normalize (-1 for last dimension)
        
    Returns
    -------
    np.ndarray
        Normalized vector(s) with ||v||₂ = 1 (for L2 method)
        
    Note:
    L2 normalization is strongly recommended for HRR to maintain the 
    mathematical properties that make circular convolution invertible.
    """
    if method == 'l2':
        norms = np.linalg.norm(vectors, axis=axis, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return vectors / norms
    
    elif method == 'l1':
        norms = np.sum(np.abs(vectors), axis=axis, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms
    
    elif method == 'max':
        max_vals = np.max(np.abs(vectors), axis=axis, keepdims=True)
        max_vals = np.where(max_vals == 0, 1, max_vals)
        return vectors / max_vals
    
    elif method == 'unit_variance':
        mean = np.mean(vectors, axis=axis, keepdims=True)
        std = np.std(vectors, axis=axis, keepdims=True)
        std = np.where(std == 0, 1, std)
        return (vectors - mean) / std
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def add_noise(vectors: np.ndarray,
              noise_level: float,
              noise_type: str = 'gaussian') -> np.ndarray:
    """
    🌊 Add Noise for Holographic Memory Robustness Testing
    
    Adds controlled noise to test the robustness of holographic memory retrieval.
    Real-world memories are always corrupted by neural noise, transmission errors,
    or partial cues. Testing with noise validates that the holographic system can
    still retrieve correct memories from degraded inputs.
    
    🧠 Cognitive Neuroscience Context:
    Biological neural networks are inherently noisy, yet memory retrieval remains
    robust. HRR systems should maintain this robustness by:
    - Graceful degradation with increasing noise levels
    - Successful retrieval even with 10-20% corruption
    - Clean separation between signal and noise in similarity space
    
    Parameters
    ----------
    vectors : np.ndarray
        Input concept vectors or memory traces
    noise_level : float
        Noise magnitude (0.0 = no noise, 1.0 = 100% noise)
        Typical testing range: 0.01-0.3 for realistic scenarios
    noise_type : str, default='gaussian'
        Type of corruption:
        - 'gaussian': Additive white noise (most realistic)
        - 'uniform': Uniform random corruption
        - 'salt_pepper': Sparse extreme-value corruption
        
    Returns
    -------
    np.ndarray
        Corrupted vectors for robustness evaluation
        
    Research Note:
    Plate (1995) showed that HRR can tolerate significant noise levels while
    maintaining retrieval accuracy, a key advantage over traditional memory models.
    """
    if noise_level <= 0:
        return vectors.copy()
    
    shape = vectors.shape
    
    if noise_type == 'gaussian':
        noise = np.random.normal(0, noise_level, shape)
        
    elif noise_type == 'uniform':
        noise = np.random.uniform(-noise_level, noise_level, shape)
        
    elif noise_type == 'salt_pepper':
        noise = np.zeros(shape)
        # Salt noise (set to maximum)
        salt_mask = np.random.random(shape) < noise_level / 2
        noise[salt_mask] = 1.0
        # Pepper noise (set to minimum)
        pepper_mask = np.random.random(shape) < noise_level / 2
        noise[pepper_mask] = -1.0
        
    else:
        raise ValueError(f"Unknown noise type: {noise_type}")
    
    return vectors + noise


def compute_similarity(vector1: np.ndarray,
                      vector2: np.ndarray,
                      metric: str = 'cosine') -> float:
    """
    🔍 Compute Vector Similarity for Memory Retrieval
    
    Computes similarity between vectors to implement the "cleanup" phase of 
    holographic memory retrieval. After unbinding operations produce noisy 
    approximations, similarity matching finds the closest clean concept vector
    from the stored vocabulary.
    
    🧠 HRR Cleanup Process:
    1. Bind query with inverse: query ⊛ memory_inverse → noisy_concept
    2. Compare noisy_concept with all vocabulary vectors using similarity
    3. Return vocabulary vector with highest similarity (cleanup)
    4. This process recovers the original clean concept from noisy retrieval
    
    Mathematical Foundation:
    Cosine similarity cos(θ) = (a·b)/(||a|| × ||b||) is preferred because:
    - Invariant to vector magnitude (works with unit vectors)
    - Measures angle between vectors (conceptual relatedness)
    - Range [-1, 1] with clear interpretation (1=identical, 0=orthogonal, -1=opposite)
    
    Parameters
    ----------
    vector1, vector2 : np.ndarray
        Vectors to compare (typically query vs. vocabulary concept)
    metric : str, default='cosine'
        Similarity metric:
        - 'cosine': Angle-based similarity (preferred for HRR)
        - 'correlation': Pearson correlation coefficient
        - 'dot': Raw dot product (magnitude-sensitive)
        - 'euclidean': Negative distance (closer = more similar)
        
    Returns
    -------
    float
        Similarity value (higher = more similar)
        Cosine: [-1, 1], Correlation: [-1, 1], Dot: [-∞, ∞], Euclidean: [-∞, 0]
        
    Usage in HRR:
    best_match_idx = argmax([compute_similarity(noisy_result, vocab[i]) 
                            for i in range(len(vocabulary))])
    """
    if vector1.shape != vector2.shape:
        raise ValueError("Vectors must have same shape")
    
    if metric == 'cosine':
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(vector1, vector2) / (norm1 * norm2)
    
    elif metric == 'correlation':
        return np.corrcoef(vector1, vector2)[0, 1]
    
    elif metric == 'dot':
        return np.dot(vector1, vector2)
    
    elif metric == 'euclidean':
        return -np.linalg.norm(vector1 - vector2)  # Negative for similarity
    
    else:
        raise ValueError(f"Unknown similarity metric: {metric}")


def orthogonalize_vectors(vectors: np.ndarray,
                         method: str = 'gram_schmidt') -> np.ndarray:
    """
    📐 Create Orthogonal Basis for Interference-Free Memory
    
    Creates orthogonal concept vectors to minimize interference during binding
    operations. In holographic memory, non-orthogonal vectors create crosstalk
    that corrupts memory retrieval - orthogonal vectors act like independent
    "channels" that don't interfere with each other.
    
    🧠 HRR Theoretical Foundation:
    Perfect orthogonality ensures:
    - Zero interference: ⟨vᵢ, vⱼ⟩ = 0 for i ≠ j
    - Clean unbinding: (a ⊛ b) ⊛ b⁻¹ = a exactly (no crosstalk)
    - Maximum capacity: n orthogonal vectors in n-dimensional space
    - Stable retrieval: noise doesn't spread between orthogonal concepts
    
    However, truly orthogonal vectors are rare in high dimensions. Near-orthogonal
    random vectors often suffice for practical HRR applications with graceful
    degradation as orthogonality decreases.
    
    Parameters
    ----------
    vectors : np.ndarray
        Input vectors to orthogonalize (shape: n_vectors, vector_dim)
        Note: Can only orthogonalize min(n_vectors, vector_dim) vectors
    method : str, default='gram_schmidt'
        Orthogonalization algorithm:
        - 'gram_schmidt': Classical iterative orthogonalization
        - 'qr': QR decomposition (more numerically stable)
        
    Returns
    -------
    np.ndarray
        Orthonormal vectors with ⟨vᵢ, vⱼ⟩ = δᵢⱼ (Kronecker delta)
        Shape: same as input, but vectors are now orthogonal and unit-normalized
        
    Mathematical Note:
    If input has more vectors than dimensions, only the first vector_dim vectors
    can be made orthogonal. Additional vectors are linearly dependent.
    
    Usage in HRR:
    Use for creating structured concept hierarchies where exact orthogonality
    is critical, such as basis vectors for compositional representations.
    """
    if method == 'gram_schmidt':
        orthogonal = np.zeros_like(vectors)
        
        for i in range(len(vectors)):
            orthogonal[i] = vectors[i].copy()
            
            # Subtract projections onto previous orthogonal vectors
            for j in range(i):
                projection = np.dot(orthogonal[i], orthogonal[j]) / np.dot(orthogonal[j], orthogonal[j])
                orthogonal[i] -= projection * orthogonal[j]
            
            # Normalize
            norm = np.linalg.norm(orthogonal[i])
            if norm > 0:
                orthogonal[i] /= norm
        
        return orthogonal
    
    elif method == 'qr':
        Q, R = np.linalg.qr(vectors.T)
        return Q.T
    
    else:
        raise ValueError(f"Unknown orthogonalization method: {method}")


def project_vector(vector: np.ndarray,
                  onto: np.ndarray) -> np.ndarray:
    """
    📊 Project Vector for Holographic Memory Analysis
    
    Projects one vector onto another to analyze conceptual relationships in
    holographic memory space. Projection reveals how much of one concept is
    "contained" in another, useful for analyzing bound memories and measuring
    conceptual overlap.
    
    🧠 HRR Analysis Applications:
    - Measuring concept similarity: larger projections = more related concepts
    - Analyzing bound memories: project (A⊛B) onto A to see A's contribution
    - Decomposing complex memories into constituent concept components
    - Studying interference patterns between overlapping memories
    
    Mathematical Foundation:
    Vector projection: proj_b(a) = (a·b/||b||²) × b
    This gives the component of vector a that lies along direction b.
    The magnitude ||proj_b(a)|| = |a·b|/||b|| measures alignment strength.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to project (e.g., complex bound memory)
    onto : np.ndarray
        Target direction vector (e.g., concept to analyze)
        
    Returns
    -------
    np.ndarray
        Projected vector component along the target direction
        
    Example in HRR:
    If memory = RED ⊛ CAR, then:
    red_component = project_vector(memory, RED_vector)
    measures how much RED contributes to the bound memory
    """
    dot_product = np.dot(vector, onto)
    norm_squared = np.dot(onto, onto)
    
    if norm_squared == 0:
        return np.zeros_like(vector)
    
    return (dot_product / norm_squared) * onto


def vector_statistics(vectors: np.ndarray) -> Dict[str, Any]:
    """
    📈 Analyze Vector Space Properties for HRR Validation
    
    Computes comprehensive statistics to validate that a vector collection
    satisfies the mathematical requirements for stable holographic memory
    operations. Good HRR vectors should be approximately orthogonal, unit-
    normalized, and evenly distributed in the vector space.
    
    🧠 HRR Quality Metrics:
    - **Low average similarity**: ⟨vᵢ, vⱼ⟩ ≈ 0 indicates near-orthogonality
    - **Unit norms**: ||vᵢ|| ≈ 1 ensures stable circular convolution
    - **Even distribution**: Balanced mean/std prevents bias in retrieval
    - **Low sparsity**: Dense vectors utilize full representational capacity
    - **Controlled noise**: Statistics reveal vector space quality
    
    Research Validation Targets (from Plate 1995, Kanerva 2009):
    - Average pairwise similarity: < 0.1 (near-orthogonal)
    - Norm standard deviation: < 0.05 (consistent magnitudes)
    - Mean close to zero: prevents systematic bias
    
    Parameters
    ----------
    vectors : np.ndarray
        Collection of concept vectors (shape: n_vectors, vector_dim)
        Typically a vocabulary of concepts for holographic memory
        
    Returns
    -------
    Dict[str, Any]
        Comprehensive statistics including:
        - n_vectors, vector_dim: basic dimensions
        - mean_values: distribution of vector means
        - std_values: distribution of vector standard deviations  
        - range_values: min/max values across all elements
        - norms: distribution of vector magnitudes
        - similarities: pairwise similarity statistics
        - sparsity: fraction of near-zero elements
        - memory_usage_mb: storage requirements
        
    Usage:
    stats = vector_statistics(concept_vocabulary)
    if stats['similarities']['mean'] > 0.1:
        print("Warning: Vectors not sufficiently orthogonal for HRR")
    if stats['norms']['std'] > 0.1:
        print("Warning: Vector norms not consistent - renormalize")
    """
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    
    n_vectors, vector_dim = vectors.shape
    
    # Basic statistics
    means = np.mean(vectors, axis=0)
    stds = np.std(vectors, axis=0)
    mins = np.min(vectors, axis=0)
    maxs = np.max(vectors, axis=0)
    
    # Norms
    norms = np.linalg.norm(vectors, axis=1)
    
    # Pairwise similarities (sample if too many vectors)
    if n_vectors <= 100:
        similarities = []
        for i in range(n_vectors):
            for j in range(i + 1, n_vectors):
                sim = compute_similarity(vectors[i], vectors[j])
                similarities.append(sim)
        similarities = np.array(similarities)
    else:
        # Sample 1000 random pairs
        indices = np.random.choice(n_vectors, size=(1000, 2), replace=True)
        similarities = []
        for i, j in indices:
            if i != j:
                sim = compute_similarity(vectors[i], vectors[j])
                similarities.append(sim)
        similarities = np.array(similarities)
    
    # Sparsity (fraction of near-zero elements)
    sparsity = np.mean(np.abs(vectors) < 1e-6)
    
    return {
        'n_vectors': n_vectors,
        'vector_dim': vector_dim,
        'mean_values': {
            'mean': np.mean(means),
            'std': np.std(means),
            'min': np.min(means),
            'max': np.max(means)
        },
        'std_values': {
            'mean': np.mean(stds),
            'std': np.std(stds),
            'min': np.min(stds),
            'max': np.max(stds)
        },
        'range_values': {
            'min': np.min(mins),
            'max': np.max(maxs),
            'range': np.max(maxs) - np.min(mins)
        },
        'norms': {
            'mean': np.mean(norms),
            'std': np.std(norms),
            'min': np.min(norms),
            'max': np.max(norms)
        },
        'similarities': {
            'mean': np.mean(similarities) if len(similarities) > 0 else 0.0,
            'std': np.std(similarities) if len(similarities) > 0 else 0.0,
            'min': np.min(similarities) if len(similarities) > 0 else 0.0,
            'max': np.max(similarities) if len(similarities) > 0 else 0.0,
            'n_pairs': len(similarities)
        },
        'sparsity': sparsity,
        'memory_usage_mb': vectors.nbytes / (1024 * 1024)
    }