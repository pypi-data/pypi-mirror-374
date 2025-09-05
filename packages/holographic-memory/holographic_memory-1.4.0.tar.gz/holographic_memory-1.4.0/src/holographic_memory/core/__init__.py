"""
📋   Init  
============

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
🌀 Core Module for Holographic Memory System
===========================================

This module provides the core functionality for Holographic Reduced Representations (HRR)
and Vector Symbolic Architecture (VSA) operations. It implements the foundational
algorithms from Tony Plate's research and modern extensions.

Main Components:
- HolographicMemory: Main memory system class
- HRROperations: Core binding and unbinding operations  
- AssociativeMemory: Associative memory with cleanup
- MemoryTrace: Individual memory trace management
- CompositionalHRR: Compositional structure operations

Based on:
- Plate (1995) "Holographic Reduced Representations"
- Hinton (1981) "Implementing Semantic Networks in Parallel Hardware"
"""

from .holographic_memory import HolographicMemory
from .hrr_operations import HRROperations, HRRVector
from .associative_memory import AssociativeMemory, MemoryTrace
from .compositional_hrr import CompositionalHRR
from .memory_management import MemoryManager

__all__ = [
    'HolographicMemory',
    'HRROperations', 
    'HRRVector',
    'AssociativeMemory',
    'MemoryTrace',
    'CompositionalHRR',
    'MemoryManager'
]

print("""
💰 MODULE SUPPORT - Made possible by Benedict Chen
   ]8;;mailto:benedict@benedictchen.com\benedict@benedictchen.com]8;;\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 ]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\💳 CLICK HERE TO DONATE VIA PAYPAL]8;;\
   ❤️ ]8;;https://github.com/sponsors/benedictchen\💖 SPONSOR ON GITHUB]8;;\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")
