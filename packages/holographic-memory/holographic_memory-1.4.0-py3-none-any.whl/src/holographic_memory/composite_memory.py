"""
🧠 Holographic Memory - Composite Memory Module
===============================================

🎯 ELI5 EXPLANATION:
==================
Imagine your brain storing memories like a hologram - where every piece contains the whole picture!

Think about how a holographic sticker works: if you cut it in half, each piece still shows the complete image, just a bit fuzzier. Your brain does something similar with complex memories like "my trip to Paris" - it doesn't store each detail separately but creates a rich, interconnected representation where everything connects to everything else.

Composite Memory takes this holographic principle to build AI memory systems:
1. 🏗️ **Hierarchical**: Build complex memories from simpler parts (like "Paris trip" from "Eiffel Tower" + "croissants" + "hotel")
2. 🔗 **Associative**: Every part connects to every other part naturally  
3. 📊 **Sequential**: Handle time series and ordered events
4. 🧠 **Emergent**: Complex behaviors arise from simple mathematical operations

🔬 RESEARCH FOUNDATION:
======================
Implements Tony Plate's revolutionary Holographic Reduced Representations:
- Plate (1995): "Holographic Reduced Representations" (Original HRR paper)
- Kanerva (2009): "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation"
- Gayler (2003): "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience"
- Levy & Gayler (2008): "Vector Symbolic Architectures: A New Building Material for Artificial General Intelligence"

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Convolution-Based Binding (Core Operation):**
C = A ⊛ B (circular convolution for binding)
C[k] = Σᵢ A[i] × B[(k-i) mod d]

**Correlation-Based Unbinding:**
A ≈ C ⊛ B⁻¹ (where B⁻¹ is the inverse via correlation)
B⁻¹[i] = B[-i mod d]

**Hierarchical Structure Building:**
MEMORY = CONTEXT ⊛ (ITEM₁ + ITEM₂ + ... + ITEMₙ)

**Sequential Memory:**
SEQUENCE = POS₁⊛ITEM₁ + POS₂⊛ITEM₂ + ... + POSₙ⊛ITEMₙ

Where positions use systematic patterns like powers: POS₁, POS₁², POS₁³, ...

📊 ARCHITECTURE VISUALIZATION:
==============================
```
🌊 HOLOGRAPHIC COMPOSITE MEMORY 🌊

Simple Memories              Composite Operations           Complex Structures
┌─────────────────┐         ┌────────────────────────────┐  ┌─────────────────┐
│ 🗼 "Eiffel"     │         │   🔗 HIERARCHICAL BUILD    │  │ 🏰 "Paris Trip" │
│    [0.2,-0.1,   │─────────│                            │─→│                 │
│     0.5, 0.3...]│         │   Context ⊛ (Item₁ + Item₂) │  │  Contains ALL   │
│                 │         │                            │  │  memories but   │
│ 🥐 "Croissant"  │─────────│   🔄 BINDING & UNBINDING   │  │  in holographic │
│    [0.1, 0.4,   │         │                            │  │  superposition  │
│    -0.2, 0.7...]│         │   ⊛ = circular convolution │  │                 │
│                 │         │   ⊛⁻¹ = correlation       │  │ 🔍 Query: "food"│
│ 🏨 "Hotel"      │─────────│                            │─→│  → Returns 🥐   │
│    [-0.3, 0.6,  │         │   📊 SEQUENCE MEMORY       │  │                 │
│     0.1,-0.4...]│         │                            │  │ 🔍 Query: "place"│
│                 │         │   Pos₁⊛A + Pos₂⊛B + ...   │  │  → Returns 🗼   │
└─────────────────┘         └────────────────────────────┘  └─────────────────┘
         ↑                             ↑                              ↑
   Independent            Mathematical operations              Emergent composite
   vector memories       preserve all information              memories with rich
                        in superposition                       associative structure

🎯 HOLOGRAPHIC PRINCIPLE:
   - Each part contains information about the whole
   - Graceful degradation under noise
   - Constant memory size regardless of content
   - Natural associative recall
```

💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider supporting:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
⭐ GitHub Sponsors: https://github.com/sponsors/benedictchen

Your support enables cutting-edge AI research for everyone! 🚀

"""
"""
Composite memory operations for Holographic Memory
Handles hierarchical structures, sequences, and complex memory operations
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Union, Optional


class CompositeMemoryOperations:
    """Handles composite memory operations for HolographicMemory systems"""
    
    def __init__(self, memory_instance):
        self.memory = memory_instance
    
    def create_hierarchy(self, structure: Dict, name: str) -> np.ndarray:
        """
        Create hierarchical structure using nested binding
        
        This implements hierarchical HRR encoding where nested dictionaries
        are recursively bound into composite structures.
        
        Args:
            structure: Dictionary structure to encode
            name: Name for the composite structure
            
        Returns:
            Encoded hierarchical vector
        """
        def encode_dict(data: Dict, prefix: str = "") -> np.ndarray:
            if not data:
                return np.zeros(self.memory.vector_dim)
                
            bindings = []
            for key, value in data.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                # Create key vector if it doesn't exist
                if full_key not in self.memory.memory_items:
                    self.memory.create_vector(full_key)
                
                if isinstance(value, dict):
                    # Recursive case: encode sub-dictionary
                    sub_encoded = encode_dict(value, full_key)
                    binding = self.memory.vector_ops.bind(self.memory.memory_items[full_key].vector, sub_encoded)
                else:
                    # Leaf case: bind key to value
                    value_str = str(value)
                    if value_str not in self.memory.memory_items:
                        self.memory.create_vector(value_str)
                    binding = self.memory.vector_ops.bind(full_key, value_str)
                
                bindings.append(binding)
            
            # Superpose all bindings
            return self.memory.vector_ops.superpose(bindings)
        
        # Encode the structure
        encoded = encode_dict(structure)
        
        # Store in composite memories
        self.memory.composite_memories[name] = encoded
        
        return encoded
    
    def create_composite_memory(self, bindings: List[Tuple[str, str]], memory_name: str) -> np.ndarray:
        """
        Create composite memory from multiple role-filler bindings
        
        Implements superposition of multiple bound pairs as described
        in Section V of Plate 1995.
        """
        
        def encode_structure(struct, prefix=""):
            """Recursively encode nested structure"""
            if isinstance(struct, dict):
                result = np.zeros(self.memory.vector_dim)
                for key, value in struct.items():
                    full_key = f"{prefix}_{key}" if prefix else key
                    
                    # Ensure key vector exists
                    if full_key not in self.memory.memory_items:
                        self.memory.create_vector(full_key)
                        
                    if isinstance(value, dict):
                        # Recursive case: bind key with encoded substructure
                        sub_encoded = encode_structure(value, full_key)
                        bound = self.memory.vector_ops.bind(self.memory.memory_items[full_key].vector, sub_encoded)
                    else:
                        # Terminal case: bind key directly with value
                        if isinstance(value, str) and value not in self.memory.memory_items:
                            self.memory.create_vector(value)
                        
                        if isinstance(value, str):
                            bound = self.memory.vector_ops.bind(full_key, value)
                        else:
                            # Value is already a vector
                            bound = self.memory.vector_ops.bind(self.memory.memory_items[full_key].vector, value)
                    
                    result += bound
                    
                if self.memory.normalize:
                    result = self.memory.vector_ops._normalize_vector(result)
                
                return result
            else:
                # Not a dict, treat as terminal value
                return struct if isinstance(struct, np.ndarray) else self.memory.memory_items[str(struct)].vector
        
        # Create composite from bindings
        composite_vector = np.zeros(self.memory.vector_dim)
        
        for role, filler in bindings:
            # Ensure both role and filler vectors exist
            if role not in self.memory.memory_items:
                self.memory.create_vector(role)
            if filler not in self.memory.memory_items:
                self.memory.create_vector(filler)
            
            # Bind role to filler
            bound = self.memory.vector_ops.bind(role, filler)
            composite_vector += bound
        
        # Normalize composite
        if self.memory.normalize:
            composite_vector = self.memory.vector_ops._normalize_vector(composite_vector)
        
        # Store composite memory
        self.memory.composite_memories[memory_name] = composite_vector
        
        return composite_vector
    
    def query_memory(self, memory_name: str, cue_role: str) -> Tuple[np.ndarray, str, float]:
        """Query composite memory with a role cue"""
        if memory_name not in self.memory.composite_memories:
            raise ValueError(f"Composite memory '{memory_name}' not found")
        
        composite = self.memory.composite_memories[memory_name]
        
        # Unbind with role cue
        result = self.memory.vector_ops.unbind(composite, cue_role)
        
        # Find best matching filler
        best_match = None
        best_similarity = -1
        
        for name, item in self.memory.memory_items.items():
            if name == cue_role:  # Skip the role itself
                continue
            sim = self.memory.vector_ops.similarity(result, item.vector)
            if sim > best_similarity:
                best_similarity = sim
                best_match = name
        
        return result, best_match, best_similarity
    
    def create_sequence(self, items: List[str], sequence_name: str) -> np.ndarray:
        """Create sequence representation using positional binding"""
        if not items:
            return np.zeros(self.memory.vector_dim)
        
        sequence_vector = np.zeros(self.memory.vector_dim)
        
        for i, item in enumerate(items):
            # Create position vector
            pos_name = f"pos_{i}"
            if pos_name not in self.memory.memory_items:
                self.memory.create_vector(pos_name)
            
            # Ensure item vector exists
            if item not in self.memory.memory_items:
                self.memory.create_vector(item)
            
            # Bind position with item
            bound = self.memory.vector_ops.bind(pos_name, item)
            sequence_vector += bound
        
        # Normalize
        if self.memory.normalize:
            sequence_vector = self.memory.vector_ops._normalize_vector(sequence_vector)
        
        # Store sequence
        self.memory.composite_memories[sequence_name] = sequence_vector
        
        return sequence_vector
    
    def query_sequence_position(self, sequence_name: str, position: int) -> Tuple[np.ndarray, str, float]:
        """Query sequence at specific position"""
        if sequence_name not in self.memory.composite_memories:
            raise ValueError(f"Sequence '{sequence_name}' not found")
        
        pos_name = f"pos_{position}"
        if pos_name not in self.memory.memory_items:
            raise ValueError(f"Position '{position}' not in memory")
        
        sequence = self.memory.composite_memories[sequence_name]
        
        # Unbind with position cue
        result = self.memory.vector_ops.unbind(sequence, pos_name)
        
        # Find best matching item
        best_match = None
        best_similarity = -1
        
        for name, item in self.memory.memory_items.items():
            if name.startswith("pos_"):  # Skip position vectors
                continue
            sim = self.memory.vector_ops.similarity(result, item.vector)
            if sim > best_similarity:
                best_similarity = sim
                best_match = name
        
        return result, best_match, best_similarity
    
    def create_hierarchical_structure(self, structure: Dict, structure_name: str) -> np.ndarray:
        """Create hierarchical structure with role-filler bindings"""
        # This is an alias for create_hierarchy for backwards compatibility
        return self.create_hierarchy(structure, structure_name)