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
🔧 Configuration Module for Holographic Memory
============================================

This module provides configuration classes, enums, and default settings
for the holographic memory system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .enums import (
    BindingMethod,
    CleanupStrategy,
    VectorDistribution,
    MemoryType,
    StorageFormat
)

from .config_classes import (
    HolographicConfig,
    VectorConfig,
    MemoryConfig,
    CleanupConfig,
    PerformanceConfig,
    ExperimentConfig
)

from .defaults import (
    DEFAULT_HOLOGRAPHIC_CONFIG,
    DEFAULT_VECTOR_CONFIG,
    DEFAULT_MEMORY_CONFIG,
    DEFAULT_CLEANUP_CONFIG,
    DEFAULT_PERFORMANCE_CONFIG,
    PRESET_CONFIGS
)

__all__ = [
    # Enums
    'BindingMethod',
    'CleanupStrategy', 
    'VectorDistribution',
    'MemoryType',
    'StorageFormat',
    
    # Config Classes
    'HolographicConfig',
    'VectorConfig',
    'MemoryConfig',
    'CleanupConfig',
    'PerformanceConfig',
    'ExperimentConfig',
    
    # Defaults and Presets
    'DEFAULT_HOLOGRAPHIC_CONFIG',
    'DEFAULT_VECTOR_CONFIG',
    'DEFAULT_MEMORY_CONFIG',
    'DEFAULT_CLEANUP_CONFIG',
    'DEFAULT_PERFORMANCE_CONFIG',
    'PRESET_CONFIGS'
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
