"""
⚙️ Configuration
=================

🔬 Research Foundation:
======================
Based on holographic and vector symbolic architectures:
- Plate, T.A. (1995). "Holographic Reduced Representations"
- Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation"
- Gayler, R.W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges"
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
Configuration Module for Holographic Memory System

Contains configuration dataclasses and settings for the HRR memory system.
Based on Tony Plate's Vector Symbolic Architecture (VSA).

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional
import time


@dataclass
class HRRMemoryItem:
    """Individual memory item in HRR system"""
    vector: np.ndarray
    name: str
    created_at: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class HRRConfig:
    """Complete configuration for HRR memory system"""
    vector_dim: int = 512
    normalize: bool = True
    noise_level: float = 0.0
    random_seed: Optional[int] = None
    cleanup_memory: bool = True
    capacity_threshold: Optional[int] = None
    similarity_preservation: bool = True
    unitary_vectors: bool = False
    trace_composition: str = "addition"
    
    # Advanced options
    binding_operation: str = 'circular_convolution'
    memory_model: str = 'distributed'
    cleanup_memory_type: str = 'hopfield'
    capacity_formula: str = 'plate1995'
    distributional_constraints: str = 'warn'
    noncommutative_mode: bool = False
    walsh_hadamard: bool = False
    sequence_encoding: str = 'positional'
    fast_cleanup: bool = True
    capacity_monitoring: bool = False
    memory_compression: bool = False
    gpu_acceleration: bool = False

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.vector_dim <= 0:
            raise ValueError("vector_dim must be positive")
        if self.noise_level < 0:
            raise ValueError("noise_level must be non-negative")
        if self.binding_operation not in ['circular_convolution', 'walsh_hadamard']:
            raise ValueError(f"Unknown binding_operation: {self.binding_operation}")
        if self.sequence_encoding not in ['positional', 'chaining', 'ngram']:
            raise ValueError(f"Unknown sequence_encoding: {self.sequence_encoding}")


def create_config(memory_type: str = "standard", **kwargs) -> HRRConfig:
    """
    Factory function to create different types of memory configurations
    
    Parameters:
    -----------
    memory_type : str
        Type of memory: "standard", "high_capacity", "fast", or "research"
    **kwargs : additional arguments for memory configuration
    
    Returns:
    --------
    config : HRRConfig
        Configured memory system settings
    """
    
    if memory_type == "standard":
        config = HRRConfig(vector_dim=512, normalize=True, cleanup_memory=True)
        
    elif memory_type == "high_capacity":
        config = HRRConfig(
            vector_dim=2048, 
            normalize=True, 
            cleanup_memory=True,
            capacity_monitoring=True,
            fast_cleanup=True
        )
        
    elif memory_type == "fast":
        config = HRRConfig(
            vector_dim=256,
            normalize=True,
            cleanup_memory=False,  # Disable for speed
            fast_cleanup=True
        )
        
    elif memory_type == "research":
        config = HRRConfig(
            vector_dim=1024,
            normalize=True,
            cleanup_memory=True,
            capacity_monitoring=True,
            unitary_vectors=True,  # For exact operations
            similarity_preservation=True
        )
        
    else:
        raise ValueError(f"Unknown memory_type: {memory_type}")
    
    # Apply any override parameters
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")
    
    return config