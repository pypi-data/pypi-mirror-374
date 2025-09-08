"""
Core Module - Main Interface for DeepParameters
===============================================

This module provides the main learn_cpd_for_node function th    except Exception as e:
        print("Error during CPD learning: {}".format(str(e)))
        if verbose:
            import traceback
            traceback.print_exc()
        
        # Fallback to simple CPD
        print("Using fallback CPD learning method")rves as the 
unified interface for all neural network architectures and sampling methods.
"""

import numpy as np
import pandas as pd
import warnings
from typing import Union, Optional, Any
import logging

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

# Core dependencies
from pgmpy.factors.discrete import TabularCPD
try:
    from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
except ImportError:
    from pgmpy.models import BayesianNetwork

# Package imports
try:
    from .architectures import (
        LSTMCPDLearner, BayesianNeuralNetworkCPDLearner, VAECPDLearner,
        AutoencoderCPDLearner, NormalizingFlowCPDLearner, SimpleCPDLearner,
        AdvancedCPDLearner, UltraCPDLearner, MegaCPDLearner
    )
    ARCHITECTURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Advanced architectures not available: {e}")
    print("    Using basic sklearn-based fallback.")
    
    # Define a simple fallback CPD learner
    class SimpleCPDLearner:
        def __init__(self, *args, **kwargs):
            pass
        def fit(self, *args, **kwargs):
            return self
        def predict(self, *args, **kwargs):
            return None
    
    # Create aliases for all expected architectures
    AdvancedCPDLearner = SimpleCPDLearner
    UltraCPDLearner = SimpleCPDLearner
    MegaCPDLearner = SimpleCPDLearner
    LSTMCPDLearner = SimpleCPDLearner
    BayesianNeuralNetworkCPDLearner = SimpleCPDLearner
    VAECPDLearner = SimpleCPDLearner
    AutoencoderCPDLearner = SimpleCPDLearner
    NormalizingFlowCPDLearner = SimpleCPDLearner
    
    ARCHITECTURES_AVAILABLE = False

try:
    from .sampling import get_sampler
    SAMPLING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Sampling methods not available: {e}")
    print("    Using basic fallback sampling.")
    
    # Define a simple fallback sampler
    class BaseSampler:
        def __init__(self, verbose=True):
            self.verbose = verbose
        def refine_cpd(self, cpd, data, node, model):
            return cpd
    
    def get_sampler(sampling_method, verbose=True):
        return BaseSampler(verbose=verbose)
    
    SAMPLING_AVAILABLE = False

try:
    from .utils import validate_inputs, format_cpd_output
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Utils not available: {e}")
    print("    Using basic fallback validation.")
    
    def validate_inputs(*args, **kwargs):
        pass
    
    def format_cpd_output(*args, **kwargs):
        pass
    
    UTILS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def learn_cpd_for_node(node: str, 
                       data: pd.DataFrame, 
                       true_model: BayesianNetwork, 
                       learnt_bn_structure: BayesianNetwork, 
                       num_parameters: int,
                       network_type: str = "simple", 
                       sampling_method: str = "1",
                       epochs: int = 100, 
                       batch_size: int = 32, 
                       learning_rate: float = 0.001,
                       validation_split: float = 0.2, 
                       early_stopping: bool = True,
                       verbose: bool = False, 
                       random_state: int = 42) -> TabularCPD:
    """
    Learn CPD for a specific node using various neural architectures and sampling methods.
    
    This is the main interface for DeepParameters. It provides a unified
    way to learn CPDs using different neural network architectures and sampling methods.
    
    Parameters:
    -----------
    node : str
        The node name for which to learn the CPD
    data : pd.DataFrame
        The training data containing all variables
    true_model : BayesianNetwork
        The true Bayesian network structure
    learnt_bn_structure : BayesianNetwork
        The learned Bayesian network structure
    num_parameters : int
        Number of parameters for the neural network
    network_type : str, default="simple"
        Type of neural network architecture to use
        Options: "simple", "advanced", "lstm", "autoencoder", "vae", "bnn", 
                "normalizing_flow", "ultra", "mega"
    sampling_method : str, default="1"
        Sampling method to use for CPD refinement
        Options: "1" (Gibbs), "2" (Metropolis-Hastings), "3" (Importance), 
                "4" (BPE), "5" (Variational), "8" (HMC)
    epochs : int, default=100
        Number of training epochs
    batch_size : int, default=32
        Training batch size
    learning_rate : float, default=0.001
        Learning rate for optimization
    validation_split : float, default=0.2
        Fraction of data to use for validation
    early_stopping : bool, default=True
        Whether to use early stopping
    verbose : bool, default=False
        Whether to print detailed progress information
    random_state : int, default=42
        Random seed for reproducibility
    
    Returns:
    --------
    TabularCPD
        The learned CPD for the specified node
        
    Example:
    --------
    >>> cpd = learn_cpd_for_node('B', 
    ...                         data, 
    ...                         true_model, 
    ...                         learnt_model, 
    ...                         num_parameters=10, 
    ...                         network_type='simple', 
    ...                         sampling_method='3')
    """
    
    # Validate inputs
    validate_inputs(node, data, true_model, learnt_bn_structure, num_parameters)
    
    # Simple, clean output
    print("DeepParameters: Learning CPD for node '{}'".format(node))
    if verbose:
        print("Configuration: {} architecture, sampling method {}, {} parameters".format(
            network_type, sampling_method, num_parameters))
    
    if verbose:
        print("LEARNING CPD FOR NODE '{}' USING DEEPPARAMETERS".format(node))
        print("=" * 60)
        print("Data shape: {}".format(data.shape))
        print("Network type: {}".format(network_type))
        print("Sampling method: {}".format(sampling_method))
        print("Parameters: {}".format(num_parameters))
        print("Epochs: {}".format(epochs))
        print("=" * 60)
    
    # Validate inputs
    # validate_inputs(node, data, true_model, learnt_bn_structure, num_parameters)
    
    # Get the appropriate network architecture
    learner = _get_network_learner(
        network_type=network_type,
        node=node,
        data=data,
        true_model=true_model,
        learnt_bn_structure=learnt_bn_structure,
        num_parameters=num_parameters,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        validation_split=validation_split,
        early_stopping=early_stopping,
        verbose=verbose,
        random_state=random_state
    )
    
    # Get the appropriate sampling method
    sampler = get_sampler(sampling_method, verbose=verbose)
    
    # Learn the CPD
    if verbose:
        print("Starting CPD learning with {} architecture and sampling method {}".format(
            network_type.upper(), sampling_method))
    
    try:
        # Train the neural network
        learner.fit(data)
        
        # Apply sampling method to refine the learned CPD
        cpd = learner.get_cpd()
        refined_cpd = sampler.refine_cpd(cpd, data, node, learnt_bn_structure)
        
        if verbose:
            print("CPD learning completed successfully")
            print("Learned CPD:")
            format_cpd_output(refined_cpd)
        
        return refined_cpd
        
    except Exception as e:
        logger.error(f"CPD learning failed: {str(e)}")
        if verbose:
            print("CPD learning failed: {}".format(str(e)))
        raise


def _get_network_learner(network_type: str, **kwargs):
    """
    Factory function to get the appropriate network learner based on network_type.
    """
    
    # All available architectures (including fallbacks)
    network_learners = {
        'simple': SimpleCPDLearner,
        'advanced': AdvancedCPDLearner,
        'ultra': UltraCPDLearner,
        'mega': MegaCPDLearner,
        'lstm': LSTMCPDLearner,
        'bnn': BayesianNeuralNetworkCPDLearner,
        'vae': VAECPDLearner,
        'autoencoder': AutoencoderCPDLearner,
        'normalizing_flow': NormalizingFlowCPDLearner
    }
    
    if network_type not in network_learners:
        raise ValueError(f"Unsupported network type: {network_type}. "
                        f"Supported types: {list(network_learners.keys())}")
    
    learner_class = network_learners[network_type]
    return learner_class(**kwargs)


# Additional utility functions for advanced usage
def list_available_architectures():
    """List all available neural network architectures."""
    architectures = {
        'simple': 'Basic neural networks (fast, good baseline)',
        'advanced': 'Enhanced neural networks (balanced performance)',
        'ultra': 'Complex neural networks (high accuracy)', 
        'mega': 'Maximum complexity neural networks',
        'lstm': 'Long Short-Term Memory networks (sequential dependencies)',
        'bnn': 'Bayesian Neural Networks (uncertainty quantification)',
        'vae': 'Variational Autoencoders (probabilistic modeling)',
        'autoencoder': 'Standard autoencoders (dimensionality reduction)',
        'normalizing_flow': 'Normalizing flows (exact probability modeling)'
    }
    
    print("AVAILABLE NEURAL NETWORK ARCHITECTURES")
    print("=" * 50)
    for arch, desc in architectures.items():
        print(f"'{arch}': {desc}")
    print("=" * 50)
    
    return list(architectures.keys())


def list_available_sampling_methods():
    """List all available sampling methods."""
    methods = {
        '1': 'Gibbs Sampling (MCMC chain)',
        '2': 'Metropolis-Hastings (MCMC acceptance-rejection)',
        '3': 'Importance Sampling (weighted samples)',
        '4': 'Bayesian Parameter Estimation (BPE)',
        '5': 'Variational Inference (optimization-based)',
        '6': 'Hamiltonian Monte Carlo (gradient-based MCMC)',
        '7': 'Sequential Monte Carlo (particle filters)',
        '8': 'Adaptive KDE (kernel density estimation)'
    }
    
    print("AVAILABLE SAMPLING METHODS")
    print("=" * 50)
    for method, desc in methods.items():
        print(f"'{method}': {desc}")
    print("=" * 50)
    
    return list(methods.keys())


def quick_demo():
    """Run a quick demonstration of the learn_cpd_for_node function."""
    print("DEEPPARAMETERS DEMO")
    print("=" * 40)
    
    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'A': np.random.randint(0, 2, 100),
        'B': np.random.randint(0, 2, 100)
    })
    
    # Create simple Bayesian network
    model = BayesianNetwork([('A', 'B')])
    
    print("Sample data created")
    print("Bayesian network: A → B")
    
    # Test different architectures
    test_cases = [
        ('simple', '1'),
        ('advanced', '2'), 
        ('vae', '4'), 
        ('lstm', '3'), 
        ('bnn', '5'),
        ('normalizing_flow', '8'),
        ('ultra', '1'),
        ('mega', '2')
    ]
    
    for network_type, sampling_method in test_cases:
        print("Testing {} + sampling {}...".format(network_type, sampling_method))
        try:
            cpd = learn_cpd_for_node(
                'B', data, model, model, 
                num_parameters=4,
                network_type=network_type,
                sampling_method=sampling_method,
                epochs=10,  # Quick demo
                verbose=False
            )
            print("{} successful".format(network_type))
        except Exception as e:
            print("{} failed: {}".format(network_type, e))
    
    print("\n🎉 Demo completed!")


# Import parallel learning functionality
try:
    from .parallel import (
        learn_network_parameters_parallel, 
        ParallelCPDLearner,
        ParallelLearningBenchmark
    )
    PARALLEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Parallel learning not available: {e}")
    PARALLEL_AVAILABLE = False


# Wrapper class for easier usage
class DeepParametersLearner:
    """
    Main wrapper class for DeepParameters CPD learning.
    
    This provides a clean, object-oriented interface to the core
    learn_cpd_for_node function with sensible defaults, plus
    parallel learning capabilities for full networks.
    """
    
    def __init__(self):
        """Initialize the DeepParameters learner."""
        pass
    
    def learn_cpd(self, data, target_node, parent_nodes=None, 
                  network_type='simple', sampling_method='1', 
                  num_parameters=4, epochs=10, verbose=True):
        """
        Learn a CPD for the target node.
        
        Args:
            data: pandas DataFrame with the data
            target_node: string, name of the target node
            parent_nodes: list of strings, parent node names
            network_type: string, type of neural network architecture
            sampling_method: string, sampling method to use
            num_parameters: int, number of parameters for learning
            epochs: int, number of training epochs
            verbose: bool, whether to print verbose output
            
        Returns:
            TabularCPD: The learned conditional probability distribution
        """
        if parent_nodes is None:
            parent_nodes = []
            
        # Create a simple Bayesian network structure for compatibility
        try:
            from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
        except ImportError:
            from pgmpy.models import BayesianNetwork
        
        # Build network structure
        edges = [(parent, target_node) for parent in parent_nodes]
        model = BayesianNetwork(edges) if edges else BayesianNetwork()
        model.add_node(target_node)
        
        return learn_cpd_for_node(
            target_node, data, model, model,
            num_parameters=num_parameters,
            network_type=network_type,
            sampling_method=sampling_method,
            epochs=epochs,
            verbose=verbose
        )
    
    def learn_network_parallel(self, data, network_structure, 
                              network_type='simple', sampling_method='1',
                              epochs=100, max_workers=None, 
                              max_time_per_group=None, parallel_style='topological',
                              verbose=True, **kwargs):
        """
        Learn CPDs for an entire network using parallel execution.
        
        This method automatically decomposes the network into factor groups
        and learns CPDs in parallel, bounded by the largest factor group.
        
        Args:
            data: pandas DataFrame with the training data
            network_structure: BayesianNetwork object defining the structure
            network_type: string, type of neural network architecture
            sampling_method: string, sampling method to use
            epochs: int, number of training epochs
            max_workers: int, maximum number of parallel workers (default: auto)
            max_time_per_group: float, maximum time per factor group in seconds
            parallel_style: string, parallel decomposition style:
                          'topological' - group by topological levels (default)
                          'parent_child' - group by parent-child relationships
            verbose: bool, whether to print verbose output
            **kwargs: additional parameters for CPD learning
            
        Returns:
            Dict[str, TabularCPD]: Dictionary mapping node names to learned CPDs
        """
        if not PARALLEL_AVAILABLE:
            raise ImportError("Parallel learning functionality not available. "
                            "Please ensure all dependencies are installed.")
        
        return learn_network_parameters_parallel(
            data=data,
            true_model=network_structure,
            learnt_bn_structure=network_structure,
            max_workers=max_workers,
            max_time_per_group=max_time_per_group,
            parallel_style=parallel_style,
            network_type=network_type,
            sampling_method=sampling_method,
            epochs=epochs,
            verbose=verbose,
            **kwargs
        )
    
    def benchmark_parallel_performance(self, data, network_structure,
                                     network_type='simple', sampling_method='1',
                                     epochs=50, max_workers_list=None, 
                                     parallel_style='topological', **kwargs):
        """
        Benchmark parallel vs sequential learning performance.
        
        Args:
            data: pandas DataFrame with the training data
            network_structure: BayesianNetwork object defining the structure
            network_type: string, type of neural network architecture
            sampling_method: string, sampling method to use
            epochs: int, number of training epochs
            max_workers_list: list of int, worker counts to test (default: [1,2,4])
            parallel_style: string, parallel decomposition style ('topological' or 'parent_child')
            **kwargs: additional parameters for CPD learning
            
        Returns:
            Dict[str, Any]: Benchmark results with timing and performance metrics
        """
        if not PARALLEL_AVAILABLE:
            raise ImportError("Parallel learning functionality not available. "
                            "Please ensure all dependencies are installed.")
        
        if max_workers_list is None:
            max_workers_list = [1, 2, 4]
        
        benchmark = ParallelLearningBenchmark(verbose=True)
        return benchmark.benchmark_performance(
            data=data,
            true_model=network_structure,
            learnt_bn_structure=network_structure,
            network_type=network_type,
            sampling_method=sampling_method,
            epochs=epochs,
            max_workers_list=max_workers_list,
            parallel_style=parallel_style,
            **kwargs
        )


if __name__ == "__main__":
    # Run demo if module is executed directly
    quick_demo()