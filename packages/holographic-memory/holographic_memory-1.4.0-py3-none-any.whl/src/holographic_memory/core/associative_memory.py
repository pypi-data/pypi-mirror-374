"""
🧠 Associative Memory - The Brain's Perfect Memory Recall System
==============================================================

🎯 ELI5 EXPLANATION:
==================
Think of Associative Memory like having a magical librarian inside your brain who can find any book even if you only remember a tiny fragment of the title!

Imagine you walk into a library and say "I need that book... it had something about dragons... and maybe magic?" A regular librarian would struggle, but this magical one instantly says "Ah yes, 'The Complete Guide to Dragon Magic, Third Edition' - here it is!" That's exactly what associative memory does with information:

1. 🔑 **Perfect Key-Value Storage**: Store millions of associations between concepts and their meanings
2. 🧹 **Noise Cleanup**: Take corrupted, partial, or noisy memories and restore them to perfection  
3. 🎯 **Content-Based Retrieval**: Find the right memory even from incomplete or distorted cues
4. 🌟 **Pattern Completion**: Fill in missing pieces of memories automatically

It's like having a superintelligent memory system that never forgets and can always find exactly what you're looking for, even from the faintest clues!

🔬 RESEARCH FOUNDATION:
======================
Core associative memory theory from cognitive science and neural network pioneers:
- **Tony Plate (1995)**: "Holographic reduced representations" - Foundation of distributed associative memory
- **Geoffrey Hinton (1981)**: "Implementing semantic networks in parallel hardware" - Neural associative networks
- **Pentti Kanerva (2009)**: "Hyperdimensional computing" - High-dimensional associative storage
- **James Anderson (1972)**: "A simple neural network generating an interactive memory" - Mathematical foundations

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Auto-Associative Memory Matrix:**
M = Σᵢ vᵢ ⊗ vᵢ (sum of outer products)

**Hetero-Associative Storage:**
M = Σᵢ yᵢ ⊗ xᵢ (associate output yᵢ with input xᵢ)

**Cleanup Dynamics:**
v(t+1) = f(M · v(t)) (iterative pattern completion)

**Similarity Matching:**
sim(v, vᵢ) = (v · vᵢ) / (||v|| ||vᵢ||) (cosine similarity)

📊 ASSOCIATIVE MEMORY VISUALIZATION:
==================================
```
🧠 ASSOCIATIVE MEMORY SYSTEM 🧠

Memory Storage            Associative Processing           Perfect Recall
┌─────────────────┐      ┌────────────────────────────────┐ ┌─────────────────┐
│ 🔑 KEY-VALUE     │      │                                │ │ ✨ CLEANED      │
│ ASSOCIATIONS    │ ──→  │  🧹 NOISE CLEANUP:             │→│ MEMORIES        │
│ "dragon" → full │      │  • Iterative refinement       │ │ Perfect recall  │
│ concept vector  │      │  • Pattern completion         │ │ from fragments  │
└─────────────────┘      │  • Error correction           │ │                 │
                         │                                │ │ 🎯 CONTENT      │
┌─────────────────┐      │  🔍 SIMILARITY SEARCH:         │ │ ADDRESSABLE     │
│ 🔊 NOISY INPUT  │ ──→  │  • Cosine similarity          │ │ Find by content │
│ Corrupted cue   │      │  • Best match selection       │ │ not by address  │
│ [0.1,?,0.8,?..] │      │  • Confidence scoring         │ │                 │
└─────────────────┘      │                                │ │ 🌟 ROBUST       │
                         │  ⚖️  ASSOCIATIVE MATRIX:        │ │ Works with      │
┌─────────────────┐      │  • M = Σ vᵢ ⊗ vᵢ              │ │ partial/noisy   │
│ ⚙️ Parameters    │ ──→  │  • Distributed storage        │ │ inputs          │
│ Thresholds,     │      │  • Holographic properties     │ │                 │
│ iterations, etc │      │                                │ │ 🔮 GENERATIVE   │
└─────────────────┘      └────────────────────────────────┘ │ Complete        │
                                        │                    │ patterns from   │
                                        ▼                    │ fragments       │
                              RESULT: Perfect memory system  └─────────────────┘
                                     like the human brain! 🚀
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Tony Plate's foundational holographic associative memory theory
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import warnings

from .hrr_operations import HRRVector


@dataclass
class MemoryTrace:
    """
    🔗 Represents a memory trace in associative memory.
    
    A memory trace encapsulates a stored association between a key and value
    with additional metadata for memory management.
    
    Attributes
    ----------
    key_vector : np.ndarray
        Key vector for retrieval
    value_vector : np.ndarray
        Associated value vector
    trace_strength : float, default=1.0
        Strength of the association
    access_count : int, default=0
        Number of times this trace has been accessed
    creation_time : int, default=0
        Timestamp when trace was created
    metadata : dict, optional
        Additional metadata about the trace
    """
    key_vector: np.ndarray
    value_vector: np.ndarray
    trace_strength: float = 1.0
    access_count: int = 0
    creation_time: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CleanupResult:
    """
    📊 Result from associative cleanup operation.
    
    Contains the cleaned vector and diagnostic information about
    the cleanup process.
    
    Attributes
    ----------
    cleaned_vector : HRRVector
        The cleaned up vector
    confidence : float
        Confidence in the cleanup result (0-1)
    original_similarity : float
        Similarity between input and output
    iterations : int
        Number of cleanup iterations performed
    converged : bool
        Whether the cleanup process converged
    candidate_matches : List[Tuple[str, float]]
        List of (name, similarity) candidate matches
    """
    cleaned_vector: HRRVector
    confidence: float
    original_similarity: float
    iterations: int
    converged: bool
    candidate_matches: List[Tuple[str, float]] = field(default_factory=list)


class AssociativeMemory:
    """
    🧠 Associative Memory with Cleanup Networks
    
    Implements both auto-associative (pattern completion) and hetero-associative
    (pattern transformation) cleanup using correlation-based storage and retrieval.
    
    This system provides robust retrieval of stored patterns even from noisy or
    incomplete input vectors.
    
    Parameters
    ----------
    vector_dim : int, default=512
        Dimension of vectors to store
    capacity_threshold : int, optional
        Maximum number of traces to store
    cleanup_threshold : float, default=0.3
        Similarity threshold for successful cleanup
    convergence_threshold : float, default=0.001
        Threshold for cleanup convergence
    max_cleanup_iterations : int, default=10
        Maximum cleanup iterations
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 capacity_threshold: Optional[int] = None,
                 cleanup_threshold: float = 0.3,
                 convergence_threshold: float = 0.001,
                 max_cleanup_iterations: int = 10):
        
        self.vector_dim = vector_dim
        self.capacity_threshold = capacity_threshold or (vector_dim * 2)
        self.cleanup_threshold = cleanup_threshold
        self.convergence_threshold = convergence_threshold
        self.max_cleanup_iterations = max_cleanup_iterations
        
        # Storage for memory traces
        self.traces: Dict[str, MemoryTrace] = {}
        self.trace_counter = 0
        
        # Auto-associative memory matrix
        self.auto_memory = np.zeros((vector_dim, vector_dim))
        
        # Statistics
        self.stats = {
            'total_stores': 0,
            'total_retrievals': 0,
            'successful_retrievals': 0,
            'cleanup_operations': 0,
            'successful_cleanups': 0,
            'average_cleanup_iterations': 0
        }
    
    def store(self, key: str, value: Union[HRRVector, np.ndarray], 
              strength: float = 1.0) -> bool:
        """
        Store a key-value association in memory.
        
        Parameters
        ----------
        key : str
            String key for retrieval
        value : HRRVector or np.ndarray
            Vector to associate with the key
        strength : float, default=1.0
            Association strength (0.0-1.0)
            
        Returns
        -------
        bool
            True if stored successfully
        """
        # Check capacity
        if len(self.traces) >= self.capacity_threshold:
            # Remove oldest trace to make space
            oldest_key = min(self.traces.keys(), 
                           key=lambda k: self.traces[k].creation_time)
            self._remove_trace(oldest_key)
            warnings.warn(f"Memory capacity reached, removed trace: {oldest_key}")
        
        # Convert value to array if needed
        if isinstance(value, HRRVector):
            value_data = value.data
        else:
            value_data = value
        
        if len(value_data) != self.vector_dim:
            raise ValueError(f"Vector dimension {len(value_data)} doesn't match {self.vector_dim}")
        
        # Create key vector (simple hash-based approach)
        key_vector = self._create_key_vector(key)
        
        # Store trace
        trace = MemoryTrace(
            key_vector=key_vector,
            value_vector=value_data.copy(),
            trace_strength=strength,
            creation_time=self.trace_counter,
            metadata={'key': key}
        )
        
        self.traces[key] = trace
        self.trace_counter += 1
        
        # Update auto-associative memory matrix
        self._update_auto_memory(value_data, strength)
        
        self.stats['total_stores'] += 1
        return True
    
    def retrieve(self, key: str) -> Optional[HRRVector]:
        """
        Retrieve value associated with key.
        
        Parameters
        ----------
        key : str
            Key to retrieve
            
        Returns
        -------
        HRRVector or None
            Retrieved vector, or None if not found
        """
        self.stats['total_retrievals'] += 1
        
        if key not in self.traces:
            return None
        
        trace = self.traces[key]
        trace.access_count += 1
        
        # Return retrieved vector
        retrieved_vector = HRRVector(
            data=trace.value_vector.copy(),
            name=f"retrieved_{key}",
            metadata={
                'retrieval_key': key,
                'access_count': trace.access_count,
                'trace_strength': trace.trace_strength
            }
        )
        
        self.stats['successful_retrievals'] += 1
        return retrieved_vector
    
    def cleanup(self, 
                noisy_vector: Union[HRRVector, np.ndarray],
                candidates: Optional[List[Union[str, HRRVector]]] = None) -> CleanupResult:
        """
        Clean up a noisy vector using stored patterns.
        
        Parameters
        ----------
        noisy_vector : HRRVector or np.ndarray
            Noisy vector to clean up
        candidates : List[str or HRRVector], optional
            Candidate vectors for cleanup
            
        Returns
        -------
        CleanupResult
            Cleanup result with diagnostics
        """
        self.stats['cleanup_operations'] += 1
        
        # Convert to array if needed
        if isinstance(noisy_vector, HRRVector):
            input_data = noisy_vector.data
            input_name = noisy_vector.name
        else:
            input_data = noisy_vector
            input_name = "unknown"
        
        # Try cleanup using stored traces first
        if candidates is None:
            # Use all stored traces as candidates
            candidate_matches = []
            
            for key, trace in self.traces.items():
                similarity = self._cosine_similarity(input_data, trace.value_vector)
                candidate_matches.append((key, similarity))
            
            # Sort by similarity
            candidate_matches.sort(key=lambda x: x[1], reverse=True)
            
        else:
            # Use provided candidates
            candidate_matches = []
            for candidate in candidates:
                if isinstance(candidate, str) and candidate in self.traces:
                    trace = self.traces[candidate]
                    similarity = self._cosine_similarity(input_data, trace.value_vector)
                    candidate_matches.append((candidate, similarity))
                elif isinstance(candidate, HRRVector):
                    similarity = self._cosine_similarity(input_data, candidate.data)
                    candidate_matches.append((candidate.name or "unnamed", similarity))
        
        # Check if we have a good match
        if candidate_matches and candidate_matches[0][1] > self.cleanup_threshold:
            # Use best match
            best_key, best_similarity = candidate_matches[0]
            
            if best_key in self.traces:
                cleaned_data = self.traces[best_key].value_vector.copy()
            else:
                # Fallback to iterative cleanup
                cleaned_data = self._iterative_cleanup(input_data)
                best_similarity = self._cosine_similarity(input_data, cleaned_data)
            
            cleaned_vector = HRRVector(
                data=cleaned_data,
                name=f"cleaned_{input_name}",
                metadata={
                    'cleanup_method': 'candidate_match',
                    'best_match': best_key,
                    'original_similarity': best_similarity
                }
            )
            
            result = CleanupResult(
                cleaned_vector=cleaned_vector,
                confidence=best_similarity,
                original_similarity=best_similarity,
                iterations=1,
                converged=True,
                candidate_matches=candidate_matches[:5]  # Top 5 matches
            )
            
            self.stats['successful_cleanups'] += 1
            
        else:
            # Use iterative auto-associative cleanup
            cleaned_data, iterations, converged = self._iterative_cleanup(input_data)
            original_similarity = self._cosine_similarity(input_data, cleaned_data)
            
            cleaned_vector = HRRVector(
                data=cleaned_data,
                name=f"cleaned_{input_name}",
                metadata={
                    'cleanup_method': 'iterative',
                    'iterations': iterations,
                    'converged': converged
                }
            )
            
            confidence = original_similarity if converged else 0.5
            
            result = CleanupResult(
                cleaned_vector=cleaned_vector,
                confidence=confidence,
                original_similarity=original_similarity,
                iterations=iterations,
                converged=converged,
                candidate_matches=candidate_matches[:5]
            )
            
            if converged and original_similarity > self.cleanup_threshold:
                self.stats['successful_cleanups'] += 1
        
        # Update average iterations
        total_ops = self.stats['cleanup_operations']
        if total_ops > 1:
            current_avg = self.stats['average_cleanup_iterations']
            new_avg = (current_avg * (total_ops - 1) + result.iterations) / total_ops
            self.stats['average_cleanup_iterations'] = new_avg
        else:
            self.stats['average_cleanup_iterations'] = result.iterations
        
        return result
    
    def _create_key_vector(self, key: str) -> np.ndarray:
        """Create a deterministic vector from a string key using content-based encoding."""
        # Content-based vector generation (no fake hash features)
        # Use character-based encoding following Vector Symbolic Architecture principles
        key_bytes = key.encode('utf-8')
        
        # Create deterministic vector from character values
        key_vector = np.zeros(self.vector_dim)
        for i, byte_val in enumerate(key_bytes):
            # Distribute character information across vector dimensions
            idx = i % self.vector_dim
            key_vector[idx] += (byte_val / 255.0) * (1.0 / (i + 1))  # Decay by position
            
        # Add positional encoding for character order
        for i in range(len(key)):
            pos_idx = (i * 7) % self.vector_dim  # Prime number spacing
            key_vector[pos_idx] += np.sin(i * 0.1) * 0.1
            
        # Normalize to unit vector
        key_vector = key_vector / np.linalg.norm(key_vector)
        return key_vector
    
    def _update_auto_memory(self, vector: np.ndarray, strength: float):
        """Update auto-associative memory matrix."""
        # Outer product update with strength weighting
        self.auto_memory += strength * np.outer(vector, vector)
    
    def _iterative_cleanup(self, noisy_vector: np.ndarray) -> Tuple[np.ndarray, int, bool]:
        """Perform iterative cleanup using auto-associative memory."""
        current_vector = noisy_vector.copy()
        
        for iteration in range(self.max_cleanup_iterations):
            # Apply auto-associative memory
            updated_vector = self.auto_memory @ current_vector
            
            # Normalize
            norm = np.linalg.norm(updated_vector)
            if norm > 0:
                updated_vector = updated_vector / norm
            
            # Check convergence
            change = np.linalg.norm(updated_vector - current_vector)
            if change < self.convergence_threshold:
                return updated_vector, iteration + 1, True
            
            current_vector = updated_vector
        
        return current_vector, self.max_cleanup_iterations, False
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def _remove_trace(self, key: str):
        """Remove a trace from memory."""
        if key in self.traces:
            # Remove from auto-associative memory (approximate)
            trace = self.traces[key]
            self.auto_memory -= trace.trace_strength * np.outer(trace.value_vector, trace.value_vector)
            
            # Remove trace
            del self.traces[key]
    
    def clear(self):
        """Clear all stored traces."""
        self.traces.clear()
        self.auto_memory.fill(0.0)
        self.trace_counter = 0
        
        # Reset statistics except configuration
        for key in ['total_stores', 'total_retrievals', 'successful_retrievals', 
                   'cleanup_operations', 'successful_cleanups']:
            self.stats[key] = 0
        self.stats['average_cleanup_iterations'] = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = self.stats.copy()
        stats.update({
            'num_traces': len(self.traces),
            'capacity_utilization': len(self.traces) / self.capacity_threshold,
            'vector_dim': self.vector_dim,
            'cleanup_threshold': self.cleanup_threshold,
            'retrieval_success_rate': (
                self.stats['successful_retrievals'] / max(1, self.stats['total_retrievals'])
            ),
            'cleanup_success_rate': (
                self.stats['successful_cleanups'] / max(1, self.stats['cleanup_operations'])
            )
        })
        return stats
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state for serialization."""
        return {
            'traces': {k: {
                'key_vector': v.key_vector,
                'value_vector': v.value_vector,
                'trace_strength': v.trace_strength,
                'access_count': v.access_count,
                'creation_time': v.creation_time,
                'metadata': v.metadata
            } for k, v in self.traces.items()},
            'auto_memory': self.auto_memory,
            'trace_counter': self.trace_counter,
            'stats': self.stats,
            'config': {
                'vector_dim': self.vector_dim,
                'capacity_threshold': self.capacity_threshold,
                'cleanup_threshold': self.cleanup_threshold,
                'convergence_threshold': self.convergence_threshold,
                'max_cleanup_iterations': self.max_cleanup_iterations
            }
        }
    
    def load_state(self, state: Dict[str, Any]):
        """Load state from serialization."""
        # Restore configuration
        config = state['config']
        self.vector_dim = config['vector_dim']
        self.capacity_threshold = config['capacity_threshold']
        self.cleanup_threshold = config['cleanup_threshold']
        self.convergence_threshold = config['convergence_threshold']
        self.max_cleanup_iterations = config['max_cleanup_iterations']
        
        # Restore traces
        self.traces = {}
        for key, trace_data in state['traces'].items():
            self.traces[key] = MemoryTrace(
                key_vector=trace_data['key_vector'],
                value_vector=trace_data['value_vector'],
                trace_strength=trace_data['trace_strength'],
                access_count=trace_data['access_count'],
                creation_time=trace_data['creation_time'],
                metadata=trace_data['metadata']
            )
        
        # Restore other state
        self.auto_memory = state['auto_memory']
        self.trace_counter = state['trace_counter']
        self.stats = state['stats']