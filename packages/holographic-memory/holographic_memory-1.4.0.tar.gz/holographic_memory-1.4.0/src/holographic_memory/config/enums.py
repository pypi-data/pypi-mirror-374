"""
📋 Enums
=========

🔬 Research Foundation:
======================
Based on holographic and vector symbolic architectures:
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges"
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
📋 Enumerations for Holographic Memory Configuration
==================================================

This module defines enumeration types used throughout the holographic
memory system for consistent parameter specification.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from enum import Enum, auto


class BindingMethod(Enum):
    """Methods for binding vectors in HRR operations."""
    CIRCULAR_CONVOLUTION = "circular_convolution"
    CORRELATION = "correlation"
    XOR = "xor"
    HADAMARD = "hadamard"
    TENSOR_PRODUCT = "tensor_product"
    FOURIER_TRANSFORM = "fourier_transform"


class CleanupStrategy(Enum):
    """Strategies for vector cleanup in associative memory."""
    AUTO_ASSOCIATIVE = "auto_associative"
    HETERO_ASSOCIATIVE = "hetero_associative"
    ITERATIVE_THRESHOLD = "iterative_threshold"
    WINNER_TAKE_ALL = "winner_take_all"
    COMPETITIVE = "competitive"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    NONE = "none"


class VectorDistribution(Enum):
    """Probability distributions for random vector generation."""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    BINARY = "binary"
    BIPOLAR = "bipolar"
    SPARSE = "sparse"
    ORTHOGONAL = "orthogonal"
    COMPLEX_GAUSSIAN = "complex_gaussian"


class MemoryType(Enum):
    """Types of memory systems for storage."""
    DISTRIBUTED = "distributed"
    LOCALIST = "localist"
    HYBRID = "hybrid"
    HOLOGRAPHIC = "holographic"
    ASSOCIATIVE = "associative"
    CONTENT_ADDRESSABLE = "content_addressable"


class StorageFormat(Enum):
    """Formats for storing and loading memory states."""
    NUMPY = "numpy"
    JSON = "json"
    PICKLE = "pickle"
    HDF5 = "hdf5"
    CSV = "csv"
    BINARY = "binary"


class CompositionMethod(Enum):
    """Methods for composing multiple vectors."""
    SUPERPOSITION = "superposition"
    WEIGHTED_SUM = "weighted_sum"
    AVERAGE = "average"
    MAX_POOLING = "max_pooling"
    MIN_POOLING = "min_pooling"
    MULTIPLICATION = "multiplication"


class SimilarityMetric(Enum):
    """Metrics for computing vector similarity."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    CORRELATION = "correlation"
    JACCARD = "jaccard"
    HAMMING = "hamming"


class NoiseType(Enum):
    """Types of noise that can be added to vectors."""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    SALT_PEPPER = "salt_pepper"
    DROPOUT = "dropout"
    QUANTIZATION = "quantization"
    NONE = "none"


class OptimizationMethod(Enum):
    """Optimization methods for learning and adaptation."""
    NONE = "none"
    GRADIENT_DESCENT = "gradient_descent"
    ADAM = "adam"
    RMS_PROP = "rmsprop"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"


class VectorSpaceType(Enum):
    """Types of vector spaces for different representations."""
    REAL = "real"
    COMPLEX = "complex"
    BINARY = "binary"
    SPARSE = "sparse"
    PHASE = "phase"
    FREQUENCY = "frequency"


class ArchitectureType(Enum):
    """Architecture types for holographic memory systems."""
    STANDARD_HRR = "standard_hrr"
    COMPOSITIONAL = "compositional"
    HIERARCHICAL = "hierarchical"
    DISTRIBUTED = "distributed"
    MODULAR = "modular"
    NEURAL_HYBRID = "neural_hybrid"