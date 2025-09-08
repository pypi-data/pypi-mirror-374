"""
DeepParameters: Advanced Neural Network CPD Learning with Parallel Execution

A comprehensive package for learning Conditional Probability Distributions (CPDs) 
using various neural network architectures including LSTM, BNN, VAE, Normalizing 
Flows, and more. Now with parallel learning capabilities for optimal performance.

Key Features:
- 9 neural network architectures (Simple NN, Advanced NN, LSTM, Autoencoder, 
  VAE, BNN, Normalizing Flow, Ultra, Mega)
- 12 sampling methods for CPD refinement (including new Bayesian methods)
- Parallel learning with factor group decomposition
- Time-bounded execution for maximum efficiency
- Comprehensive performance evaluation with 7 metrics
- Simple, unified interface: learn_cpd_for_node()
- Production-ready with extensive documentation

Quick Start:
    >>> from deepparameters import learn_cpd_for_node
    >>> cpd = learn_cpd_for_node('B', data, true_model, learnt_model, 
    ...                         num_parameters=10, network_type='simple')
    
    # For parallel learning of entire networks:
    >>> from deepparameters import learn_network_parameters_parallel
    >>> cpds = learn_network_parameters_parallel(data, true_model, learnt_model)

For more examples and documentation, visit:
https://github.com/rudzanimulaudzi/DeepParameters
"""

__version__ = "2.0.6"
__author__ = "Rudzani Mulaudzi"
__email__ = "rudzani.mulaudzi2@students.wits.ac.za"
__license__ = "MIT"

# Main interface
from .core import learn_cpd_for_node, DeepParametersLearner
from .utils import compare_cpds, print_comparison_metrics, visualize_cpd

# Import parallel learning if available
try:
    from .parallel import (
        learn_network_parameters_parallel,
        ParallelCPDLearner,
        ParallelLearningBenchmark
    )
    PARALLEL_AVAILABLE = True
    
    # Add parallel functions to __all__
    parallel_exports = [
        'learn_network_parameters_parallel',
        'ParallelCPDLearner', 
        'ParallelLearningBenchmark'
    ]
except ImportError:
    PARALLEL_AVAILABLE = False
    parallel_exports = []

# Make the main functions easily accessible
__all__ = [
    'learn_cpd_for_node',
    'DeepParametersLearner',
    'compare_cpds',
    'print_comparison_metrics', 
    'visualize_cpd'
] + parallel_exports

def welcome():
    """Display welcome message for the DeepParameters package."""
    print("DeepParameters v{} - Advanced Neural Network CPD Learning with Parallel Execution".format(__version__))
    print("Usage: learn_cpd_for_node('B', data, true_model, learnt_model, num_parameters=10)")
    if PARALLEL_AVAILABLE:
        print("Parallel: learn_network_parameters_parallel(data, true_model, learnt_model)")
    print("Documentation: https://github.com/rudzanimulaudzi/DeepParameters")