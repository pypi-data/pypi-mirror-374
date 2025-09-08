"""
Utils Module - Utility Functions for DeepParameters
===================================================

This module contains utility functions for validation, formatting,
testing, and visualization of CPDs.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, List, Optional
import warnings
warnings.filterwarnings('ignore')

# PGMPy
from pgmpy.factors.discrete import TabularCPD
try:
    from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
except ImportError:
    from pgmpy.models import BayesianNetwork


def _get_cpd_evidence(cpd):
    """Helper function to get evidence variables from CPD (backwards compatibility)."""
    if hasattr(cpd, 'evidence'):
        return _get_cpd_evidence(cpd)
    else:
        # For newer pgmpy versions, evidence variables are variables[1:]
        return cpd.variables[1:] if len(cpd.variables) > 1 else []


def _get_cpd_evidence_card(cpd):
    """Helper function to get evidence cardinalities from CPD (backwards compatibility)."""
    if hasattr(cpd, 'evidence_card'):
        return cpd.evidence_card
    else:
        # For newer pgmpy versions, get cardinalities from variable_card
        return cpd.cardinality[1:] if len(cpd.cardinality) > 1 else []


def validate_inputs(node: str, 
                    data: pd.DataFrame, 
                    true_model: BayesianNetwork, 
                    learnt_bn_structure: BayesianNetwork, 
                    num_parameters: int):
    """
    Validate inputs for the learn_cpd_for_node function.
    
    Parameters:
    -----------
    node : str
        The node name
    data : pd.DataFrame
        The data
    true_model : BayesianNetwork
        True Bayesian network
    learnt_bn_structure : BayesianNetwork
        Learned network structure
    num_parameters : int
        Number of parameters
    
    Raises:
    -------
    ValueError
        If inputs are invalid
    """
    
    # Check node exists
    if node not in data.columns:
        raise ValueError(f"Node '{node}' not found in data columns: {list(data.columns)}")
    
    if node not in learnt_bn_structure.nodes():
        raise ValueError(f"Node '{node}' not found in learned network nodes: {list(learnt_bn_structure.nodes())}")
    
    # Check data is not empty
    if len(data) == 0:
        raise ValueError("Data cannot be empty")
    
    # Check data contains all required variables
    required_vars = set(learnt_bn_structure.nodes())
    data_vars = set(data.columns)
    missing_vars = required_vars - data_vars
    if missing_vars:
        raise ValueError(f"Data missing required variables: {missing_vars}")
    
    # Check num_parameters is positive
    if num_parameters <= 0:
        raise ValueError("num_parameters must be positive")
    
    # Check for missing values
    if data.isnull().any().any():
        print("Warning: Data contains missing values. Consider preprocessing.")
    
    # Check data types (should be numeric for neural networks)
    non_numeric = data.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        print(f"Warning: Non-numeric columns detected: {non_numeric}. Consider encoding.")


def format_cpd_output(cpd: TabularCPD, precision: int = 10):
    """
    Format and display CPD in a nice table format.
    
    Parameters:
    -----------
    cpd : TabularCPD
        The CPD to format
    precision : int, default=10
        Number of decimal places to display
    """
    
    print("Learned CPD for node '{}':".format(cpd.variable))
    
    if _get_cpd_evidence(cpd):
        # CPD with parents
        print(f"   Parents: {_get_cpd_evidence(cpd)}")
        print(f"   Evidence cards: {_get_cpd_evidence_card(cpd)}")
        
        # Create header
        headers = []
        if len(_get_cpd_evidence(cpd)) == 1:
            # Single parent
            parent = _get_cpd_evidence(cpd)[0]
            for i in range(_get_cpd_evidence_card(cpd)[0]):
                headers.append(f"{parent}({i})")
        else:
            # Multiple parents
            import itertools
            parent_combinations = []
            for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                parent_combinations.append(list(range(_get_cpd_evidence_card(cpd)[i])))
            
            all_combinations = list(itertools.product(*parent_combinations))
            for combo in all_combinations:
                header = ",".join([f"{_get_cpd_evidence(cpd)[i]}({combo[i]})" for i in range(len(combo))])
                headers.append(header)
        
        # Create table
        print("+------+" + "+".join(["-" * 20 for _ in headers]) + "+")
        print(f"| {cpd.variable:<4} |" + "|".join([f"{h:^20}" for h in headers]) + "|")
        print("+------+" + "+".join(["-" * 20 for _ in headers]) + "+")
        
        # Debug information
        print(f"DEBUG - CPD values shape: {cpd.values.shape}, Headers count: {len(headers)}")
        
        for i in range(cpd.variable_card):
            row = f"| {cpd.variable}({i}) |"
            for j in range(len(headers)):
                # Add bounds checking to prevent index errors
                if j < cpd.values.shape[1]:
                    value = cpd.values[i, j]
                    # Ensure we have a scalar value for formatting
                    try:
                        if hasattr(value, 'item') and value.size == 1:
                            value = value.item()
                        elif isinstance(value, (list, tuple)) and len(value) == 1:
                            value = value[0]
                        elif hasattr(value, '__len__') and len(value) == 1:
                            value = float(value[0])
                        else:
                            value = float(value)
                    except (ValueError, TypeError, AttributeError):
                        value = float(np.asarray(value).flatten()[0])
                else:
                    # If we're out of bounds, show N/A
                    value = 0.0  # or could use np.nan or "N/A"
                row += f"{value:^20.{precision}f}|"
            print(row)
        
        print("+------+" + "+".join(["-" * 20 for _ in headers]) + "+")
    
    else:
        # Root node (no parents)
        print("   No parents (root node)")
        print("+------+--------------------+")
        print(f"| {cpd.variable:<4} | Probability        |")
        print("+------+--------------------+")
        
        for i in range(cpd.variable_card):
            # Handle both 1D and 2D value arrays
            if cpd.values.ndim == 1:
                value = cpd.values[i]
            else:
                value = cpd.values[i, 0]
            
            # Ensure we have a scalar value for formatting
            try:
                if hasattr(value, 'item') and value.size == 1:
                    value = value.item()
                elif isinstance(value, (list, tuple)) and len(value) == 1:
                    value = value[0]
                elif hasattr(value, '__len__') and len(value) == 1:
                    value = float(value[0])
                else:
                    value = float(value)
            except (ValueError, TypeError, AttributeError):
                value = float(np.asarray(value).flatten()[0])
            print(f"| {cpd.variable}({i}) | {value:^18.{precision}f} |")
        
        print("+------+--------------------+")
    
    print()


def create_test_data(structure: str = "simple", n_samples: int = 1000, random_state: int = 42) -> tuple:
    """
    Create test data and Bayesian network for testing.
    
    Parameters:
    -----------
    structure : str, default="simple"
        Type of structure to create: 'simple', 'complex', 'chain'
    n_samples : int, default=1000
        Number of samples to generate
    random_state : int, default=42
        Random seed
    
    Returns:
    --------
    tuple
        (data, model) - DataFrame and BayesianNetwork
    """
    
    np.random.seed(random_state)
    
    if structure == "simple":
        # Simple A → B structure
        model = BayesianNetwork([('A', 'B')])
        
        # Generate data
        A = np.random.randint(0, 2, n_samples)
        B = np.zeros(n_samples)
        
        for i in range(n_samples):
            if A[i] == 0:
                B[i] = np.random.choice([0, 1], p=[0.7, 0.3])
            else:
                B[i] = np.random.choice([0, 1], p=[0.3, 0.7])
        
        data = pd.DataFrame({'A': A, 'B': B.astype(int)})
        
        # Add true CPDs
        from pgmpy.factors.discrete import TabularCPD
        cpd_a = TabularCPD('A', 2, [[0.5], [0.5]])
        cpd_b = TabularCPD('B', 2, [[0.7, 0.3], [0.3, 0.7]], evidence=['A'], evidence_card=[2])
        model.add_cpds(cpd_a, cpd_b)
    
    elif structure == "complex":
        # Complex A, B → C structure
        model = BayesianNetwork([('A', 'C'), ('B', 'C')])
        
        # Generate data
        A = np.random.randint(0, 2, n_samples)
        B = np.random.randint(0, 2, n_samples)
        C = np.zeros(n_samples)
        
        # Complex interaction: P(C=1|A,B)
        prob_c = {
            (0, 0): 0.1,  # P(C=1|A=0,B=0) = 0.1
            (0, 1): 0.4,  # P(C=1|A=0,B=1) = 0.4
            (1, 0): 0.6,  # P(C=1|A=1,B=0) = 0.6
            (1, 1): 0.9   # P(C=1|A=1,B=1) = 0.9 (strong interaction)
        }
        
        for i in range(n_samples):
            p = prob_c[(A[i], B[i])]
            C[i] = np.random.choice([0, 1], p=[1-p, p])
        
        data = pd.DataFrame({'A': A, 'B': B, 'C': C.astype(int)})
        
        # Add true CPDs
        from pgmpy.factors.discrete import TabularCPD
        cpd_a = TabularCPD('A', 2, [[0.5], [0.5]])
        cpd_b = TabularCPD('B', 2, [[0.5], [0.5]])
        cpd_c = TabularCPD('C', 2, [[0.9, 0.6, 0.4, 0.1], [0.1, 0.4, 0.6, 0.9]], 
                          evidence=['A', 'B'], evidence_card=[2, 2])
        model.add_cpds(cpd_a, cpd_b, cpd_c)
    
    elif structure == "chain":
        # Chain A → B → C structure
        model = BayesianNetwork([('A', 'B'), ('B', 'C')])
        
        # Generate data
        A = np.random.randint(0, 2, n_samples)
        B = np.zeros(n_samples)
        C = np.zeros(n_samples)
        
        # A → B
        for i in range(n_samples):
            if A[i] == 0:
                B[i] = np.random.choice([0, 1], p=[0.8, 0.2])
            else:
                B[i] = np.random.choice([0, 1], p=[0.2, 0.8])
        
        # B → C
        for i in range(n_samples):
            if B[i] == 0:
                C[i] = np.random.choice([0, 1], p=[0.6, 0.4])
            else:
                C[i] = np.random.choice([0, 1], p=[0.1, 0.9])
        
        data = pd.DataFrame({'A': A, 'B': B.astype(int), 'C': C.astype(int)})
        
        # Add true CPDs
        from pgmpy.factors.discrete import TabularCPD
        cpd_a = TabularCPD('A', 2, [[0.5], [0.5]])
        cpd_b = TabularCPD('B', 2, [[0.8, 0.2], [0.2, 0.8]], evidence=['A'], evidence_card=[2])
        cpd_c = TabularCPD('C', 2, [[0.6, 0.1], [0.4, 0.9]], evidence=['B'], evidence_card=[2])
        model.add_cpds(cpd_a, cpd_b, cpd_c)
    
    else:
        raise ValueError(f"Unknown structure: {structure}. Use 'simple', 'complex', or 'chain'")
    
    return data, model


def visualize_cpd(cpd: TabularCPD, save_path: Optional[str] = None, figsize: tuple = (10, 6)):
    """
    Visualize CPD as a heatmap.
    
    Parameters:
    -----------
    cpd : TabularCPD
        The CPD to visualize
    save_path : str, optional
        Path to save the plot
    figsize : tuple, default=(10, 6)
        Figure size
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap
    im = ax.imshow(cpd.values, cmap='Blues', aspect='auto')
    
    # Set labels
    ax.set_title(f"CPD for Variable '{cpd.variable}'", fontsize=14, fontweight='bold')
    ax.set_ylabel(f"{cpd.variable} States", fontsize=12)
    
    if _get_cpd_evidence(cpd):
        if len(_get_cpd_evidence(cpd)) == 1:
            # Single parent
            parent_labels = [f"{_get_cpd_evidence(cpd)[0]}={i}" for i in range(_get_cpd_evidence_card(cpd)[0])]
        else:
            # Multiple parents
            import itertools
            parent_combinations = []
            for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                parent_combinations.append(list(range(_get_cpd_evidence_card(cpd)[i])))
            
            all_combinations = list(itertools.product(*parent_combinations))
            parent_labels = []
            for combo in all_combinations:
                label = ",".join([f"{_get_cpd_evidence(cpd)[i]}={combo[i]}" for i in range(len(combo))])
                parent_labels.append(label)
        
        ax.set_xlabel("Parent Configurations", fontsize=12)
        ax.set_xticks(range(len(parent_labels)))
        ax.set_xticklabels(parent_labels, rotation=45)
    else:
        ax.set_xlabel("No Parents (Root Node)", fontsize=12)
        ax.set_xticks([0])
        ax.set_xticklabels(['Root'])
    
    # Set y-axis
    ax.set_yticks(range(cpd.variable_card))
    ax.set_yticklabels([f"{cpd.variable}={i}" for i in range(cpd.variable_card)])
    
    # Add text annotations
    for i in range(cpd.variable_card):
        for j in range(cpd.values.shape[1]):
            text = ax.text(j, i, f'{cpd.values[i, j]:.3f}', 
                          ha="center", va="center", color="white" if cpd.values[i, j] > 0.5 else "black")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Probability', rotation=270, labelpad=15)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print("CPD visualization saved to: {}".format(save_path))
    else:
        plt.show()
    
    return fig, ax


def compare_cpds(learned_cpd: TabularCPD, true_cpd: TabularCPD) -> dict:
    """
    Compare learned CPD with true CPD and compute metrics.
    
    Parameters:
    -----------
    learned_cpd : TabularCPD
        The learned CPD
    true_cpd : TabularCPD
        The true CPD
    
    Returns:
    --------
    dict
        Dictionary of comparison metrics
    """
    
    # Ensure CPDs have the same structure
    if (learned_cpd.variable != true_cpd.variable or
        learned_cpd.variable_card != true_cpd.variable_card or
        _get_cpd_evidence(learned_cpd) != _get_cpd_evidence(true_cpd) or
        _get_cpd_evidence_card(learned_cpd) != _get_cpd_evidence_card(true_cpd)):
        raise ValueError("CPDs have different structures and cannot be compared")
    
    # Calculate metrics
    diff = learned_cpd.values - true_cpd.values
    
    metrics = {
        'mean_absolute_error': np.mean(np.abs(diff)),
        'mean_squared_error': np.mean(diff**2),
        'max_absolute_error': np.max(np.abs(diff)),
        'total_variation_distance': 0.5 * np.sum(np.abs(diff)),
        'kl_divergence': np.sum(true_cpd.values * np.log(
            (true_cpd.values + 1e-10) / (learned_cpd.values + 1e-10)
        )),
        'frobenius_norm': np.linalg.norm(diff, 'fro'),
        'cosine_similarity': np.sum(learned_cpd.values.flatten() * true_cpd.values.flatten()) / (
            np.linalg.norm(learned_cpd.values.flatten()) * np.linalg.norm(true_cpd.values.flatten())
        )
    }
    
    return metrics


def print_comparison_metrics(metrics: dict):
    """
    Print comparison metrics in a nice format.
    
    Parameters:
    -----------
    metrics : dict
        Metrics from compare_cpds function
    """
    
    print("CPD COMPARISON METRICS")
    print("=" * 40)
    print(f"Mean Absolute Error:      {metrics['mean_absolute_error']:.6f}")
    print(f"Mean Squared Error:       {metrics['mean_squared_error']:.6f}")
    print(f"Max Absolute Error:       {metrics['max_absolute_error']:.6f}")
    print(f"Total Variation Distance: {metrics['total_variation_distance']:.6f}")
    print(f"KL Divergence:           {metrics['kl_divergence']:.6f}")
    print(f"Frobenius Norm:          {metrics['frobenius_norm']:.6f}")
    print(f"Cosine Similarity:       {metrics['cosine_similarity']:.6f}")
    print("=" * 40)


def benchmark_architectures(data: pd.DataFrame, model: BayesianNetwork, node: str,
                           architectures: List[str] = None, sampling_methods: List[str] = None,
                           num_parameters: int = 4, epochs: int = 50, verbose: bool = True) -> pd.DataFrame:
    """
    Benchmark different architectures and sampling methods.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Training data
    model : BayesianNetwork
        Bayesian network
    node : str
        Node to learn CPD for
    architectures : List[str], optional
        List of architectures to test
    sampling_methods : List[str], optional
        List of sampling methods to test
    num_parameters : int, default=4
        Number of parameters
    epochs : int, default=50
        Number of epochs
    verbose : bool, default=True
        Whether to print progress
    
    Returns:
    --------
    pd.DataFrame
        Results dataframe with metrics for each combination
    """
    
    if architectures is None:
        architectures = ['simple', 'advanced', 'lstm', 'vae']
    
    if sampling_methods is None:
        sampling_methods = ['1', '2', '4', '8']
    
    # Import here to avoid circular imports
    from .core import learn_cpd_for_node
    
    results = []
    
    # Get true CPD if available
    true_cpd = None
    try:
        true_cpd = model.get_cpds(node)
    except:
        pass
    
    total_combinations = len(architectures) * len(sampling_methods)
    current = 0
    
    for arch in architectures:
        for sample_method in sampling_methods:
            current += 1
            if verbose:
                print("Testing {}/{}: {} + sampling {}".format(current, total_combinations, arch, sample_method))
            
            try:
                # Learn CPD
                learned_cpd = learn_cpd_for_node(
                    node=node,
                    data=data,
                    true_model=model,
                    learnt_bn_structure=model,
                    num_parameters=num_parameters,
                    network_type=arch,
                    sampling_method=sample_method,
                    epochs=epochs,
                    verbose=False
                )
                
                # Calculate metrics
                result = {
                    'architecture': arch,
                    'sampling_method': sample_method,
                    'success': True,
                    'error': None
                }
                
                if true_cpd is not None:
                    metrics = compare_cpds(learned_cpd, true_cpd)
                    result.update(metrics)
                
                results.append(result)
                
                if verbose:
                    status = "Success"
                    if true_cpd is not None:
                        status += f" (MAE: {result['mean_absolute_error']:.4f})"
                    print(f"   {status}")
                
            except Exception as e:
                result = {
                    'architecture': arch,
                    'sampling_method': sample_method,
                    'success': False,
                    'error': str(e)
                }
                results.append(result)
                
                if verbose:
                    print("   Failed: {}".format(e))
    
    return pd.DataFrame(results)


def save_benchmark_results(results_df: pd.DataFrame, save_path: str):
    """
    Save benchmark results with visualization.
    
    Parameters:
    -----------
    results_df : pd.DataFrame
        Results from benchmark_architectures
    save_path : str
        Path to save results (without extension)
    """
    
    # Save CSV
    results_df.to_csv(f"{save_path}.csv", index=False)
    print(f"📄 Results saved to: {save_path}.csv")
    
    # Create visualization if we have metrics
    if 'mean_absolute_error' in results_df.columns:
        successful_results = results_df[results_df['success'] == True]
        
        if len(successful_results) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # MAE heatmap
            pivot_mae = successful_results.pivot(index='architecture', columns='sampling_method', values='mean_absolute_error')
            sns.heatmap(pivot_mae, annot=True, fmt='.4f', cmap='viridis_r', ax=axes[0,0])
            axes[0,0].set_title('Mean Absolute Error')
            
            # MSE heatmap
            pivot_mse = successful_results.pivot(index='architecture', columns='sampling_method', values='mean_squared_error')
            sns.heatmap(pivot_mse, annot=True, fmt='.4f', cmap='viridis_r', ax=axes[0,1])
            axes[0,1].set_title('Mean Squared Error')
            
            # KL Divergence heatmap
            pivot_kl = successful_results.pivot(index='architecture', columns='sampling_method', values='kl_divergence')
            sns.heatmap(pivot_kl, annot=True, fmt='.4f', cmap='viridis_r', ax=axes[1,0])
            axes[1,0].set_title('KL Divergence')
            
            # Cosine Similarity heatmap
            pivot_cos = successful_results.pivot(index='architecture', columns='sampling_method', values='cosine_similarity')
            sns.heatmap(pivot_cos, annot=True, fmt='.4f', cmap='viridis', ax=axes[1,1])
            axes[1,1].set_title('Cosine Similarity')
            
            plt.tight_layout()
            plt.savefig(f"{save_path}_visualization.png", dpi=300, bbox_inches='tight')
            print("Visualization saved to: {}_visualization.png".format(save_path))
            plt.close()


# Quick test function
def quick_test():
    """Run a quick test of the utilities."""
    print("🧪 Running DeepParameters Utils Quick Test")
    print("=" * 50)
    
    # Create test data
    data, model = create_test_data("simple", n_samples=100)
    print("Test data created")
    
    # Test validation
    try:
        validate_inputs('B', data, model, model, 4)
        print("Input validation passed")
    except Exception as e:
        print("Input validation failed: {}".format(e))
    
    # Test CPD formatting
    try:
        true_cpd = model.get_cpds('B')
        format_cpd_output(true_cpd)
        print("CPD formatting works")
    except Exception as e:
        print("CPD formatting failed: {}".format(e))
    
    print("\n🎉 Utils test completed!")


def create_synthetic_data(num_samples: int = 1000, num_variables: int = 3, random_state: int = 42) -> pd.DataFrame:
    """
    Create synthetic data for testing (Colab-friendly function).
    
    This is a simplified wrapper around create_test_data for easy use in Google Colab.
    
    Parameters:
    -----------
    num_samples : int, default=1000
        Number of samples to generate
    num_variables : int, default=3
        Number of variables (2 or 3 supported)
    random_state : int, default=42
        Random seed for reproducibility
    
    Returns:
    --------
    pd.DataFrame
        Synthetic dataset with binary variables
    
    Examples:
    ---------
    >>> # In Google Colab
    >>> data = create_synthetic_data(500, 2)
    >>> print(data.head())
    """
    
    np.random.seed(random_state)
    
    if num_variables == 2:
        # Simple A → B structure
        data, _ = create_test_data("simple", num_samples, random_state)
        return data
    
    elif num_variables == 3:
        # Complex A, B → C structure  
        data, _ = create_test_data("complex", num_samples, random_state)
        return data
    
    elif num_variables > 3:
        # Chain structure for more variables
        # Start with base A → B → C
        A = np.random.randint(0, 2, num_samples)
        data_dict = {'A': A}
        
        # Create chain A → B → C → D → ...
        prev_var = A
        var_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        
        for i in range(1, min(num_variables, len(var_names))):
            current_var = np.zeros(num_samples)
            for j in range(num_samples):
                if prev_var[j] == 0:
                    current_var[j] = np.random.choice([0, 1], p=[0.7, 0.3])
                else:
                    current_var[j] = np.random.choice([0, 1], p=[0.3, 0.7])
            
            data_dict[var_names[i]] = current_var.astype(int)
            prev_var = current_var
        
        return pd.DataFrame(data_dict)
    
    else:
        raise ValueError("num_variables must be >= 2")


if __name__ == "__main__":
    quick_test()