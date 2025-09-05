"""
DeepParameters: Advanced Neural Network CPD Learning

A comprehensive package for learning Conditional Probability Distributions (CPDs) 
using various neural network architectures including LSTM, BNN, VAE, Normalizing 
Flows, and more.

Key Features:
- 9 neural network architectures (Simple NN, Advanced NN, LSTM, Autoencoder, 
  VAE, BNN, Normalizing Flow, Ultra, Mega)
- 8 sampling methods for CPD refinement
- Comprehensive performance evaluation with 7 metrics
- Simple, unified interface: learn_cpd_for_node()
- Production-ready with extensive documentation

Quick Start:
    >>> from deepparameters import learn_cpd_for_node
    >>> cpd = learn_cpd_for_node('B', data, true_model, learnt_model, 
    ...                         num_parameters=10, network_type='simple')

For more examples and documentation, visit:
https://github.com/rudzanimulaudzi/DeepParameters
"""

__version__ = "2.0.3"
__author__ = "Rudzani Mulaudzi"
__email__ = "rudzani.mulaudzi2@students.wits.ac.za"
__license__ = "MIT"

# Main interface
from .core import learn_cpd_for_node, DeepParametersLearner
from .utils import compare_cpds, print_comparison_metrics, visualize_cpd

# Make the main function easily accessible
__all__ = [
    'learn_cpd_for_node',
    'DeepParametersLearner',
    'compare_cpds',
    'print_comparison_metrics', 
    'visualize_cpd'
]

def welcome():
    """Display welcome message for the DeepParameters package."""
    print("DeepParameters v{} - Advanced Neural Network CPD Learning".format(__version__))
    print("Usage: learn_cpd_for_node('B', data, true_model, learnt_model, num_parameters=10)")
    print("Documentation: https://github.com/rudzanimulaudzi/DeepParameters")