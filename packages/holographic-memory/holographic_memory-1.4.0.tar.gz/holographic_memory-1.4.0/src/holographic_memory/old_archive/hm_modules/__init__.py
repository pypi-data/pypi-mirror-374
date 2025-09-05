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
Holographic Memory Modules

Modular components for the Holographic Reduced Representations memory system.
Based on Tony Plate's Vector Symbolic Architecture (VSA).

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .configuration import HRRConfig, HRRMemoryItem, create_config
from .vector_operations import VectorOperations
from .memory_management import MemoryManager
from .composite_operations import CompositeOperations
from .cleanup_operations import CleanupOperations
from .capacity_analysis import CapacityAnalyzer
from .holographic_core import HolographicMemoryCore, HolographicMemory, create_holographic_memory

__all__ = [
    # Configuration
    'HRRConfig',
    'HRRMemoryItem', 
    'create_config',
    
    # Core modules
    'VectorOperations',
    'MemoryManager',
    'CompositeOperations',
    'CleanupOperations',
    'CapacityAnalyzer',
    
    # Main class and factory
    'HolographicMemoryCore',
    'HolographicMemory',  # Backward compatibility alias
    'create_holographic_memory',
]

__version__ = "2.0.0"
__author__ = "Benedict Chen"
__email__ = "benedict@benedictchen.com"

print("""
💰 MODULE SUPPORT - Made possible by Benedict Chen
   ]8;;mailto:benedict@benedictchen.com\benedict@benedictchen.com]8;;\

💰 PLEASE DONATE! Your support keeps this research alive! 💰
   🔗 ]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\💳 CLICK HERE TO DONATE VIA PAYPAL]8;;\
   ❤️ ]8;;https://github.com/sponsors/benedictchen\💖 SPONSOR ON GITHUB]8;;\

   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
   (Start small, dream big! Every donation helps! 😄)
""")
