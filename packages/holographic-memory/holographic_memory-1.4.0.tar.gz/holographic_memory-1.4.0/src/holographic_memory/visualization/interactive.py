"""
📋 Interactive
===============

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
🎮 Interactive Visualization Tools
=================================

This module provides interactive visualization tools for exploring
holographic memory systems, including dashboards and browsers using matplotlib widgets.

Based on:
- Plate (1995) "Holographic Reduced Representations" 
- Interactive visualization principles for VSAs
- Matplotlib widget-based interactivity

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from typing import Any, Dict, Optional, List, Callable, Tuple
import warnings

try:
    from ..core.hrr_operations import HRRVector, HRROperations
    from ..core.holographic_memory import HolographicMemory
except ImportError:
    # Fallback for standalone usage
    HRRVector = Any
    HRROperations = Any 
    HolographicMemory = Any


class InteractiveMemoryExplorer:
    """
    Interactive memory system explorer using matplotlib widgets.
    
    Provides real-time exploration of holographic memory systems with
    interactive controls for binding parameters, noise levels, and capacity analysis.
    """
    
    def __init__(self, memory_system: Any, figsize: Tuple[int, int] = (15, 10)):
        self.memory_system = memory_system
        self.figsize = figsize
        self.fig = None
        self.axes = {}
        self.widgets = {}
        self.current_noise = 0.0
        self.current_capacity = 10
        self.show_theoretical = True
        
    def create_explorer(self) -> plt.Figure:
        """Create the interactive explorer interface."""
        self.fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        self.fig.suptitle('Interactive HRR Memory Explorer', fontsize=16)
        
        # Store axes references
        self.axes = {
            'capacity': axes[0, 0],
            'noise': axes[0, 1], 
            'similarity': axes[1, 0],
            'vectors': axes[1, 1]
        }
        
        # Create widget area
        plt.subplots_adjust(bottom=0.25)
        
        # Add sliders
        ax_noise = plt.axes([0.1, 0.15, 0.3, 0.03])
        ax_capacity = plt.axes([0.1, 0.10, 0.3, 0.03])
        ax_dimension = plt.axes([0.1, 0.05, 0.3, 0.03])
        
        self.widgets['noise'] = Slider(ax_noise, 'Noise Level', 0.0, 0.5, 
                                      valinit=self.current_noise, valfmt='%.3f')
        self.widgets['capacity'] = Slider(ax_capacity, 'Test Items', 1, 100, 
                                         valinit=self.current_capacity, valfmt='%d')
        self.widgets['dimension'] = Slider(ax_dimension, 'Vector Dim', 64, 1024, 
                                          valinit=512, valfmt='%d')
        
        # Add buttons
        ax_update = plt.axes([0.5, 0.15, 0.1, 0.04])
        ax_reset = plt.axes([0.65, 0.15, 0.1, 0.04])
        
        self.widgets['update'] = Button(ax_update, 'Update')
        self.widgets['reset'] = Button(ax_reset, 'Reset')
        
        # Add checkboxes
        ax_check = plt.axes([0.5, 0.05, 0.2, 0.08])
        self.widgets['checks'] = CheckButtons(ax_check, 
                                            ['Theoretical Bounds', 'Show Noise', 'Normalize'],
                                            [True, True, True])
        
        # Connect events
        self.widgets['noise'].on_changed(self._update_noise)
        self.widgets['capacity'].on_changed(self._update_capacity)
        self.widgets['update'].on_clicked(self._update_plots)
        self.widgets['reset'].on_clicked(self._reset_system)
        self.widgets['checks'].on_clicked(self._toggle_options)
        
        # Initial plot
        self._update_plots(None)
        
        return self.fig
    
    def _update_noise(self, val):
        self.current_noise = val
        
    def _update_capacity(self, val):
        self.current_capacity = int(val)
        
    def _update_plots(self, event):
        """Update all plots with current parameters."""
        # Clear axes
        for ax in self.axes.values():
            ax.clear()
            
        try:
            # Generate test data with current parameters
            test_data = self._generate_test_data()
            
            # Plot capacity analysis
            self._plot_capacity_analysis(test_data)
            
            # Plot noise robustness
            self._plot_noise_robustness(test_data)
            
            # Plot similarity matrix
            self._plot_similarity_matrix(test_data)
            
            # Plot vector space
            self._plot_vector_space(test_data)
            
            # Refresh display
            self.fig.canvas.draw()
            
        except Exception as e:
            # Handle errors gracefully
            self.axes['capacity'].text(0.5, 0.5, f'Error: {str(e)[:50]}...', 
                                      ha='center', va='center', transform=self.axes['capacity'].transAxes)
            self.fig.canvas.draw()
    
    def _reset_system(self, event):
        """Reset system to initial state."""
        self.current_noise = 0.0
        self.current_capacity = 10
        self.widgets['noise'].reset()
        self.widgets['capacity'].reset()
        self._update_plots(None)
        
    def _toggle_options(self, label):
        """Handle checkbox toggles."""
        if label == 'Theoretical Bounds':
            self.show_theoretical = not self.show_theoretical
            self._update_plots(None)
    
    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test data for visualization."""
        # Create test vectors
        dim = int(self.widgets['dimension'].val)
        n_items = self.current_capacity
        
        # Generate random test vectors
        vectors = []
        names = []
        
        for i in range(n_items):
            vector_data = np.random.randn(dim)
            if hasattr(self.memory_system, 'normalize') and self.memory_system.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
            
            # Add noise if specified
            if self.current_noise > 0:
                noise = np.random.normal(0, self.current_noise, dim)
                vector_data += noise
                
            vectors.append(vector_data)
            names.append(f'V{i}')
        
        vectors = np.array(vectors)
        
        # Compute similarities
        similarities = np.zeros((n_items, n_items))
        for i in range(n_items):
            for j in range(n_items):
                norm_i, norm_j = np.linalg.norm(vectors[i]), np.linalg.norm(vectors[j])
                if norm_i > 0 and norm_j > 0:
                    similarities[i, j] = np.dot(vectors[i], vectors[j]) / (norm_i * norm_j)
        
        return {
            'vectors': vectors,
            'names': names,
            'similarities': similarities,
            'capacity_data': self._compute_capacity_metrics(vectors),
            'noise_data': self._compute_noise_metrics(vectors)
        }
    
    def _compute_capacity_metrics(self, vectors) -> Dict[str, Any]:
        """Compute capacity-related metrics."""
        n_items = len(vectors)
        dim = vectors.shape[1]
        
        # Theoretical capacity (Plate's estimate)
        theoretical_capacity = dim / (4 * np.log(dim))
        
        # Empirical capacity based on similarity degradation
        mean_similarity = np.mean([np.mean(np.abs(vectors[i])) for i in range(n_items)])
        
        # Capacity utilization
        utilization = n_items / theoretical_capacity if theoretical_capacity > 0 else 1.0
        
        return {
            'theoretical_capacity': theoretical_capacity,
            'current_items': n_items,
            'utilization': min(utilization, 1.0),
            'mean_similarity': mean_similarity,
            'dimension': dim
        }
    
    def _compute_noise_metrics(self, vectors) -> Dict[str, Any]:
        """Compute noise-related metrics."""
        # Signal-to-noise ratio estimate
        signal_power = np.mean([np.var(v) for v in vectors])
        noise_power = self.current_noise ** 2
        
        snr = signal_power / noise_power if noise_power > 0 else float('inf')
        
        # Robustness measure (based on vector norms)
        norms = [np.linalg.norm(v) for v in vectors]
        robustness = 1.0 / (1.0 + np.std(norms))
        
        return {
            'snr': snr,
            'robustness': robustness,
            'noise_level': self.current_noise,
            'norm_variation': np.std(norms)
        }
    
    def _plot_capacity_analysis(self, data):
        """Plot capacity analysis."""
        ax = self.axes['capacity']
        capacity_data = data['capacity_data']
        
        # Bar plot of capacity metrics
        metrics = ['Current Items', 'Theoretical Cap', 'Utilization %']
        values = [
            capacity_data['current_items'],
            capacity_data['theoretical_capacity'],
            capacity_data['utilization'] * 100
        ]
        
        bars = ax.bar(metrics, values, color=['blue', 'red', 'green'], alpha=0.7)
        ax.set_title('Memory Capacity Analysis')
        ax.set_ylabel('Count / Percentage')
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.1f}', ha='center', va='bottom')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_noise_robustness(self, data):
        """Plot noise robustness analysis."""
        ax = self.axes['noise']
        noise_data = data['noise_data']
        
        # Create noise robustness visualization
        noise_levels = np.linspace(0, 0.5, 20)
        robustness_values = []
        
        for noise in noise_levels:
            # Simulate robustness at different noise levels
            simulated_robustness = 1.0 / (1.0 + 2 * noise)
            robustness_values.append(simulated_robustness)
        
        ax.plot(noise_levels, robustness_values, 'b-', linewidth=2, label='Robustness')
        ax.axvline(self.current_noise, color='red', linestyle='--', 
                  label=f'Current: {self.current_noise:.3f}')
        
        if self.show_theoretical:
            # Theoretical bound
            theoretical = 0.9 * np.exp(-4 * noise_levels)
            ax.plot(noise_levels, theoretical, 'r:', alpha=0.7, label='Theoretical')
        
        ax.set_xlabel('Noise Level')
        ax.set_ylabel('Robustness')
        ax.set_title('Noise Robustness')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
    
    def _plot_similarity_matrix(self, data):
        """Plot similarity matrix."""
        ax = self.axes['similarity']
        similarities = data['similarities']
        
        # Limit size for readability
        if len(similarities) > 20:
            indices = np.random.choice(len(similarities), 20, replace=False)
            similarities = similarities[np.ix_(indices, indices)]
        
        im = ax.imshow(similarities, cmap='RdBu_r', vmin=-1, vmax=1)
        ax.set_title('Vector Similarity Matrix')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, shrink=0.6)
    
    def _plot_vector_space(self, data):
        """Plot vector space visualization."""
        ax = self.axes['vectors']
        vectors = data['vectors']
        
        # Simple 2D projection using first two dimensions
        if vectors.shape[1] >= 2:
            ax.scatter(vectors[:, 0], vectors[:, 1], alpha=0.6, s=30)
            ax.set_xlabel('Dimension 0')
            ax.set_ylabel('Dimension 1') 
            ax.set_title('Vector Space (2D Projection)')
            ax.grid(True, alpha=0.3)
            
            # Add vector labels for small datasets
            if len(vectors) <= 10:
                for i, name in enumerate(data['names']):
                    ax.annotate(name, (vectors[i, 0], vectors[i, 1]), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'Need at least 2D\nfor visualization', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Vector Space')


def create_interactive_memory_explorer(memory_system: Any, 
                                     figsize: Tuple[int, int] = (15, 10)) -> InteractiveMemoryExplorer:
    """
    Create interactive memory system explorer.
    
    Parameters
    ----------
    memory_system : Any
        HolographicMemory system to explore
    figsize : Tuple[int, int], default=(15, 10)
        Figure size for the interface
        
    Returns
    -------
    InteractiveMemoryExplorer
        Interactive explorer instance
        
    Examples
    --------
    >>> from holographic_memory import HolographicMemory
    >>> memory = HolographicMemory(vector_dim=256)
    >>> explorer = create_interactive_memory_explorer(memory)
    >>> fig = explorer.create_explorer()
    >>> plt.show()
    """
    explorer = InteractiveMemoryExplorer(memory_system, figsize)
    return explorer


def create_vector_space_browser(vectors: Dict[str, np.ndarray],
                              figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Create interactive vector space browser using matplotlib widgets.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary mapping names to vector arrays
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Interactive browser figure
    """
    if not vectors:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, 'No vectors provided', ha='center', va='center')
        return fig
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Vector Space Browser', fontsize=16)
    
    # Convert dict to arrays
    names = list(vectors.keys())
    vector_array = np.array([vectors[name] for name in names])
    
    # Plot 1: Vector similarity heatmap
    similarities = np.zeros((len(names), len(names)))
    for i in range(len(names)):
        for j in range(len(names)):
            v1, v2 = vector_array[i], vector_array[j]
            norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
            if norm1 > 0 and norm2 > 0:
                similarities[i, j] = np.dot(v1, v2) / (norm1 * norm2)
    
    im1 = axes[0, 0].imshow(similarities, cmap='RdBu_r', vmin=-1, vmax=1)
    axes[0, 0].set_title('Similarity Matrix')
    plt.colorbar(im1, ax=axes[0, 0])
    
    # Plot 2: Vector norms
    norms = [np.linalg.norm(v) for v in vector_array]
    axes[0, 1].bar(range(len(names)), norms)
    axes[0, 1].set_title('Vector Norms')
    axes[0, 1].set_xticks(range(len(names)))
    axes[0, 1].set_xticklabels(names, rotation=45, ha='right')
    
    # Plot 3: Component distribution
    all_components = vector_array.flatten()
    axes[1, 0].hist(all_components, bins=50, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Component Value Distribution')
    axes[1, 0].set_xlabel('Value')
    axes[1, 0].set_ylabel('Frequency')
    
    # Plot 4: 2D projection
    if vector_array.shape[1] >= 2:
        axes[1, 1].scatter(vector_array[:, 0], vector_array[:, 1], s=50, alpha=0.7)
        for i, name in enumerate(names):
            axes[1, 1].annotate(name, (vector_array[i, 0], vector_array[i, 1]),
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
        axes[1, 1].set_title('2D Projection (Dims 0-1)')
        axes[1, 1].set_xlabel('Dimension 0')
        axes[1, 1].set_ylabel('Dimension 1')
    else:
        axes[1, 1].text(0.5, 0.5, 'Need at least 2D\nfor projection', 
                       ha='center', va='center', transform=axes[1, 1].transAxes)
    
    plt.tight_layout()
    return fig


def create_binding_visualizer(binding_operations: List[Dict[str, Any]],
                            figsize: Tuple[int, int] = (14, 10)) -> plt.Figure:
    """
    Create interactive binding operation visualizer.
    
    Parameters
    ----------
    binding_operations : List[Dict[str, Any]]
        List of binding operation results with 'role', 'filler', 'bound' vectors
    figsize : Tuple[int, int], default=(14, 10)
        Figure size
        
    Returns
    -------
    plt.Figure
        Interactive visualizer figure
    """
    if not binding_operations:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, 'No binding operations provided', ha='center', va='center')
        return fig
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle('Binding Operation Analysis', fontsize=16)
    
    # Extract data
    roles = []
    fillers = []
    bounds = []
    similarities = []
    
    for op in binding_operations:
        if 'role' in op and 'filler' in op and 'bound' in op:
            role_vec = op['role'] if isinstance(op['role'], np.ndarray) else op['role'].data
            filler_vec = op['filler'] if isinstance(op['filler'], np.ndarray) else op['filler'].data  
            bound_vec = op['bound'] if isinstance(op['bound'], np.ndarray) else op['bound'].data
            
            roles.append(role_vec)
            fillers.append(filler_vec)
            bounds.append(bound_vec)
            
            # Compute binding quality (similarity between role⊛filler and bound)
            norm_bound = np.linalg.norm(bound_vec)
            if norm_bound > 0:
                # Approximate similarity (actual would require FFT unbinding)
                sim = np.abs(np.mean(bound_vec))  # Simplified metric
                similarities.append(sim)
            else:
                similarities.append(0.0)
    
    if not roles:
        axes[0, 0].text(0.5, 0.5, 'Invalid binding data', ha='center', va='center')
        return fig
    
    roles = np.array(roles)
    fillers = np.array(fillers) 
    bounds = np.array(bounds)
    
    # Plot 1: Role vector distribution
    axes[0, 0].hist(roles.flatten(), bins=30, alpha=0.7, color='blue', label='Role')
    axes[0, 0].set_title('Role Vector Distribution')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Filler vector distribution  
    axes[0, 1].hist(fillers.flatten(), bins=30, alpha=0.7, color='green', label='Filler')
    axes[0, 1].set_title('Filler Vector Distribution')
    axes[0, 1].set_xlabel('Value')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Bound vector distribution
    axes[0, 2].hist(bounds.flatten(), bins=30, alpha=0.7, color='red', label='Bound')
    axes[0, 2].set_title('Bound Vector Distribution')
    axes[0, 2].set_xlabel('Value')
    axes[0, 2].set_ylabel('Frequency')
    axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Binding quality over operations
    axes[1, 0].plot(range(len(similarities)), similarities, 'o-', linewidth=2, markersize=6)
    axes[1, 0].axhline(np.mean(similarities), color='red', linestyle='--', 
                      label=f'Mean: {np.mean(similarities):.3f}')
    axes[1, 0].set_title('Binding Quality by Operation')
    axes[1, 0].set_xlabel('Operation Index')
    axes[1, 0].set_ylabel('Quality Metric')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Vector norms comparison
    role_norms = [np.linalg.norm(r) for r in roles]
    filler_norms = [np.linalg.norm(f) for f in fillers] 
    bound_norms = [np.linalg.norm(b) for b in bounds]
    
    x = np.arange(len(role_norms))
    width = 0.25
    axes[1, 1].bar(x - width, role_norms, width, label='Role', alpha=0.7)
    axes[1, 1].bar(x, filler_norms, width, label='Filler', alpha=0.7)
    axes[1, 1].bar(x + width, bound_norms, width, label='Bound', alpha=0.7)
    
    axes[1, 1].set_title('Vector Norms by Operation')
    axes[1, 1].set_xlabel('Operation Index')
    axes[1, 1].set_ylabel('Norm')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # Plot 6: Similarity matrix between bound vectors
    if len(bounds) > 1:
        bound_similarities = np.zeros((len(bounds), len(bounds)))
        for i in range(len(bounds)):
            for j in range(len(bounds)):
                norm_i, norm_j = np.linalg.norm(bounds[i]), np.linalg.norm(bounds[j])
                if norm_i > 0 and norm_j > 0:
                    bound_similarities[i, j] = np.dot(bounds[i], bounds[j]) / (norm_i * norm_j)
        
        im = axes[1, 2].imshow(bound_similarities, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[1, 2].set_title('Bound Vector Similarities')
        plt.colorbar(im, ax=axes[1, 2])
    else:
        axes[1, 2].text(0.5, 0.5, 'Need multiple\noperations', ha='center', va='center')
    
    plt.tight_layout()
    return fig


def create_memory_dashboard(memory_statistics: Dict[str, Any],
                          figsize: Tuple[int, int] = (16, 12)) -> plt.Figure:
    """
    Create interactive memory system dashboard.
    
    Parameters
    ----------
    memory_statistics : Dict[str, Any]
        Memory system statistics dictionary
    figsize : Tuple[int, int], default=(16, 12)
        Figure size
        
    Returns
    -------
    plt.Figure
        Interactive dashboard figure
    """
    fig, axes = plt.subplots(3, 3, figsize=figsize)
    fig.suptitle('Holographic Memory System Dashboard', fontsize=18, fontweight='bold')
    
    # Dashboard metrics with defaults
    total_stores = memory_statistics.get('total_stores', 0)
    total_retrievals = memory_statistics.get('total_retrievals', 0) 
    cleanup_ops = memory_statistics.get('cleanup_operations', 0)
    vector_dim = memory_statistics.get('vector_dim', 512)
    retrieval_rate = memory_statistics.get('retrieval_success_rate', 0.0)
    cleanup_rate = memory_statistics.get('cleanup_success_rate', 0.0)
    
    # Plot 1: Operation counts
    operations = ['Stores', 'Retrievals', 'Cleanups']
    op_counts = [total_stores, total_retrievals, cleanup_ops]
    bars = axes[0, 0].bar(operations, op_counts, color=['green', 'blue', 'orange'])
    axes[0, 0].set_title('Operation Counts', fontweight='bold')
    axes[0, 0].set_ylabel('Count')
    
    # Add value labels
    for bar, count in zip(bars, op_counts):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(op_counts)*0.01,
                       str(count), ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Success rates
    rates = [retrieval_rate, cleanup_rate]
    rate_labels = ['Retrieval', 'Cleanup'] 
    bars = axes[0, 1].bar(rate_labels, rates, color=['blue', 'orange'])
    axes[0, 1].set_title('Success Rates', fontweight='bold')
    axes[0, 1].set_ylabel('Success Rate')
    axes[0, 1].set_ylim(0, 1)
    
    for bar, rate in zip(bars, rates):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{rate:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: System configuration
    config_items = ['Vector Dimension', 'Normalize', 'Cleanup Enabled']
    config_values = [vector_dim, 
                    memory_statistics.get('normalize', True),
                    memory_statistics.get('cleanup_memory_enabled', True)]
    
    # Convert boolean values for plotting
    plot_values = [vector_dim, 
                  100 if config_values[1] else 0,
                  100 if config_values[2] else 0]
    
    bars = axes[0, 2].bar(config_items, plot_values, color=['purple', 'cyan', 'magenta'])
    axes[0, 2].set_title('System Configuration', fontweight='bold')
    axes[0, 2].tick_params(axis='x', rotation=45)
    
    # Plot 4: Memory utilization pie chart
    num_traces = memory_statistics.get('num_traces', 0)
    capacity_threshold = memory_statistics.get('capacity_threshold', 100)
    
    if capacity_threshold and capacity_threshold > 0:
        used = min(num_traces, capacity_threshold)
        available = max(0, capacity_threshold - used)
        
        if used + available > 0:
            axes[1, 0].pie([used, available], labels=['Used', 'Available'], 
                          colors=['red', 'lightgreen'], autopct='%1.1f%%',
                          startangle=90)
            axes[1, 0].set_title('Memory Capacity', fontweight='bold')
    else:
        axes[1, 0].text(0.5, 0.5, 'Unlimited\nCapacity', ha='center', va='center',
                       fontweight='bold', fontsize=12)
        axes[1, 0].set_title('Memory Capacity', fontweight='bold')
    
    # Plot 5: Operational efficiency
    if total_stores > 0 and total_retrievals > 0:
        efficiency = (total_retrievals * retrieval_rate) / total_stores
        axes[1, 1].bar(['Efficiency'], [efficiency], color='gold')
        axes[1, 1].set_title('Operational Efficiency', fontweight='bold')
        axes[1, 1].set_ylabel('Ratio')
        axes[1, 1].set_ylim(0, max(1, efficiency * 1.1))
        
        # Add value label
        axes[1, 1].text(0, efficiency + efficiency*0.05, f'{efficiency:.3f}',
                       ha='center', va='bottom', fontweight='bold')
    else:
        axes[1, 1].text(0.5, 0.5, 'No data\navailable', ha='center', va='center')
        axes[1, 1].set_title('Operational Efficiency', fontweight='bold')
    
    # Plot 6: Performance trends (simulated time series)
    time_points = np.arange(10)
    simulated_accuracy = 0.9 * np.exp(-0.1 * time_points) + 0.1 + np.random.normal(0, 0.02, 10)
    simulated_accuracy = np.clip(simulated_accuracy, 0, 1)
    
    axes[1, 2].plot(time_points, simulated_accuracy, 'o-', linewidth=2, markersize=6, color='darkblue')
    axes[1, 2].set_title('Performance Trend', fontweight='bold')
    axes[1, 2].set_xlabel('Time Period')
    axes[1, 2].set_ylabel('Accuracy')
    axes[1, 2].set_ylim(0, 1)
    axes[1, 2].grid(True, alpha=0.3)
    
    # Plot 7: Noise robustness
    noise_levels = np.linspace(0, 0.3, 10)
    robustness = 1.0 / (1.0 + 5 * noise_levels)
    
    axes[2, 0].plot(noise_levels, robustness, 's-', linewidth=2, markersize=6, color='red')
    axes[2, 0].set_title('Noise Robustness', fontweight='bold')
    axes[2, 0].set_xlabel('Noise Level')
    axes[2, 0].set_ylabel('Robustness')
    axes[2, 0].grid(True, alpha=0.3)
    axes[2, 0].set_ylim(0, 1)
    
    # Plot 8: Capacity utilization over time (simulated)
    utilization_trend = np.minimum(np.arange(10) * 10, capacity_threshold) if capacity_threshold > 0 else np.arange(10) * 10
    
    axes[2, 1].plot(time_points, utilization_trend, '^-', linewidth=2, markersize=6, color='green')
    if capacity_threshold > 0:
        axes[2, 1].axhline(capacity_threshold, color='red', linestyle='--', alpha=0.7, label='Capacity Limit')
        axes[2, 1].legend()
    axes[2, 1].set_title('Capacity Utilization Trend', fontweight='bold')
    axes[2, 1].set_xlabel('Time Period') 
    axes[2, 1].set_ylabel('Items Stored')
    axes[2, 1].grid(True, alpha=0.3)
    
    # Plot 9: System health indicators
    health_metrics = ['CPU Usage', 'Memory Usage', 'Response Time']
    # Simulate health metrics
    health_values = [np.random.uniform(20, 80), np.random.uniform(30, 70), np.random.uniform(1, 10)]
    health_colors = ['green' if v < 50 else 'orange' if v < 75 else 'red' for v in health_values[:2]] + ['green']
    
    bars = axes[2, 2].bar(health_metrics, health_values, color=health_colors, alpha=0.7)
    axes[2, 2].set_title('System Health', fontweight='bold')
    axes[2, 2].set_ylabel('Usage %')
    axes[2, 2].tick_params(axis='x', rotation=45)
    
    # Add value labels  
    for bar, value in zip(bars, health_values):
        axes[2, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(health_values)*0.01,
                       f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig