# DeepParameters

**Advanced Neural Network CPD Learning for Bayesian Networks**
*Version 2.0.5 - Beta Release*

🏠 **Homepage**: [https://github.com/rudzanimulaudzi/DeepParameters](https://github.com/rudzanimulaudzi/DeepParameters)

DeepParameters is a comprehensive Python package for learning Conditional Probability Distributions (CPDs) using state-of-the-art neural network architectures. It provides a unified interface for experimenting with various deep learning approaches to probabilistic modeling.

> 🎉 **Version 2.0.5** brings **configurable parallel learning styles**: Choose between topological level groups or parent-child factor groups for optimal performance on your network structure!

## 🚀 Key Features

- **9 Neural Network Architectures**: Simple NN, Advanced NN, LSTM, Autoencoder, VAE, BNN, Normalizing Flow, Ultra, Mega
- **8 Sampling Methods**: Gibbs, Metropolis-Hastings, Importance, BPE, Variational, HMC, and more
- **🆕 Configurable Parallel Learning**: Choose between 'topological' and 'parent_child' parallel execution styles
- **Parallel CPD Learning**: Multi-threaded parameter learning with factor group decomposition
- **Comprehensive Evaluation**: 7 performance metrics including MAE, KL divergence, and probability consistency
- **Simple Interface**: Unified `learn_cpd_for_node()` function for all architectures

## 📦 Installation

```bash
pip install deepparameters
# For the latest 2.0.5 features:
pip install --upgrade deepparameters
```

### What's New in 2.0.5

- **🎯 Parallel Style Selection**: Choose between 'topological' (dependency levels) and 'parent_child' (sibling relationships) decomposition
- **⚡ Optimized Parent-Child Groups**: New grouping strategy optimized for hierarchical network structures  
- **� Enhanced Parallel Interface**: Simple `parallel_style` parameter for easy configuration
- **�️ Comprehensive Validation**: Both parallel approaches thoroughly tested for equivalence and performance
- **📊 Interactive Examples**: Demo scripts to help users choose their optimal parallel strategy
- **🎛️ Tunable Optimizers**: Choose from adam, adamw, sgd, rmsprop, nadam for optimal training
- **⏹️ Configurable Early Stopping**: Prevent overfitting with adjustable patience settings

## 🎯 Quick Start

```python
from deepparameters import learn_cpd_for_node
import pandas as pd
from pgmpy.models import BayesianNetwork

# Load your data
data = pd.read_csv('your_data.csv')

# Define your Bayesian network structures
true_model = BayesianNetwork([('A', 'B'), ('C', 'B')])
learnt_model = BayesianNetwork([('A', 'B'), ('C', 'B')])

# Learn CPD with default settings
cpd = learn_cpd_for_node(
    node='B', 
    data=data, 
    true_model=true_model, 
    learnt_bn_structure=learnt_model,
    num_parameters=10
)

# NEW in 2.0.4: Tunable optimizers and early stopping
cpd = learn_cpd_for_node(
    node='B',
    data=data,
    true_model=true_model,
    learnt_bn_structure=learnt_model,
    num_parameters=20,
    network_type='lstm',           # Try: simple, advanced, lstm, autoencoder, vae, bnn
    sampling_method='4',           # Try: 1-8 for different sampling methods
    optimizer='adamw',             # NEW: adam, adamw, sgd, rmsprop, nadam
    early_stopping_patience=15,    # NEW: Configurable early stopping
    epochs=200,
    verbose=True
)
```

## ⚡ Parallel Learning (NEW in 2.0.5)

Learn CPDs for entire networks using configurable parallel execution:

```python
from deepparameters.core import DeepParametersLearner

# Initialize learner
learner = DeepParametersLearner()

# Option 1: Topological Level Groups (default)
# Groups nodes by dependency levels - reliable for complex networks
cpds = learner.learn_network_parallel(
    data=data,
    network_structure=bn,
    parallel_style='topological',  # Default
    max_workers=4,
    verbose=True
)

# Option 2: Parent-Child Factor Groups (optimized)
# Groups nodes by parent relationships - better for hierarchical structures
cpds = learner.learn_network_parallel(
    data=data,
    network_structure=bn,
    parallel_style='parent_child',  # Optimized for hierarchical networks
    max_workers=4,
    verbose=True
)

# Advanced parallel configuration
cpds = learner.learn_network_parallel(
    data=data,
    network_structure=bn,
    parallel_style='parent_child',   # Choose decomposition strategy
    network_type='advanced',         # Neural architecture
    sampling_method='3',             # Importance sampling
    epochs=100,
    max_workers=6,                   # Parallel workers
    max_time_per_group=60,           # Time limit per group
    verbose=True
)
```

### Choosing Your Parallel Style

- **🔀 Topological** (`'topological'`): Default, groups by dependency levels
  - ✅ Reliable for complex dependency patterns
  - ✅ Well-tested and stable
  - ✅ Good for networks with intricate relationships

- **👨‍👩‍👧‍👦 Parent-Child** (`'parent_child'`): Optimized for hierarchical structures
  - ✅ Groups sibling nodes together
  - ✅ Better performance on hierarchical networks
  - ✅ More efficient for parent-child relationships

## 🏗️ Architecture Overview

### Neural Network Architectures

| Architecture | Description | Best For |
|-------------|-------------|----------|
| `simple` | Basic feedforward network | Quick prototyping |
| `advanced` | Multi-layer with dropout and batch norm | General purpose |
| `lstm` | Long Short-Term Memory network | Sequential dependencies |
| `autoencoder` | Encoder-decoder architecture | Feature learning |
| `vae` | Variational Autoencoder | Probabilistic modeling |
| `bnn` | Bayesian Neural Network | Uncertainty quantification |
| `normalizing_flow` | Normalizing Flow model | Complex distributions |
| `ultra` | Advanced hybrid architecture | High-performance scenarios |
| `mega` | Maximum complexity architecture | Research applications |

### Sampling Methods

| Method | ID | Description | Strengths |
|--------|-------|-------------|-----------|
| Gibbs | `1` | Gibbs sampling | Simple, reliable |
| Metropolis-Hastings | `2` | MCMC sampling | Flexible |
| Importance | `3` | Importance sampling | Efficient for rare events |
| BPE | `4` | Belief Propagation Extension | Fast inference |
| Variational | `5` | Variational inference | Scalable |
| HMC | `8` | Hamiltonian Monte Carlo | High accuracy |

## 📊 Performance Evaluation

DeepParameters provides comprehensive evaluation metrics:

- **Mean Absolute Error (MAE)**: Primary accuracy metric
- **KL Divergence**: Distribution similarity measure  
- **Root Mean Square Error (RMSE)**: Error magnitude
- **Maximum Error**: Worst-case performance
- **JS Divergence**: Symmetric distribution distance
- **Cosine Similarity**: Directional similarity
- **Probability Consistency**: Probabilistic validity

```python
from deepparameters import evaluate_cpd_performance

# Evaluate learned CPD against ground truth
results = evaluate_cpd_performance(learned_cpd, true_cpd)
print(f"MAE: {results['mean_absolute_error']:.4f}")
print(f"KL Divergence: {results['kl_divergence']:.4f}")
```

## 🔧 Advanced Configuration

```python
# Full parameter configuration with v2.0.4 enhancements
cpd = learn_cpd_for_node(
    node='B',
    data=data,
    true_model=true_model,
    learnt_bn_structure=learnt_model,
    num_parameters=50,
    network_type='vae',              # Choose architecture
    sampling_method='8',             # HMC sampling
    optimizer='adamw',               # NEW: Tunable optimizer
    early_stopping_patience=20,     # NEW: Configurable early stopping
    epochs=500,
    batch_size=64,
    learning_rate=0.001,
    validation_split=0.2,
    early_stopping=True,
    verbose=True,
    random_state=42
)
```

### 🔧 New Optimizer Options (v2.0.4)

| Optimizer | Description | Best For |
|-----------|-------------|----------|
| `adam` | Adaptive moment estimation | General purpose (default) |
| `adamw` | Adam with weight decay | Better generalization |
| `sgd` | Stochastic gradient descent | Simple, reliable |
| `rmsprop` | Root mean square propagation | Recurrent networks |
| `nadam` | Nesterov-accelerated Adam | Faster convergence |

## 📚 Documentation

- **[Complete Workflow Guide](DEEPPARAMETERS_WORKFLOW_GUIDE.md)**: Step-by-step usage examples
- **[Performance Analysis](PERFORMANCE_ANALYSIS_REPORT.md)**: Detailed benchmarks and comparisons
- **[API Reference](DOCUMENTATION_INDEX.md)**: Complete function documentation

## 🧪 Example Workflows

Coming Soon

## 🤝 Contributing

We welcome contributions! For now email rudzani.mulaudzi2@students.wits.ac.za

## 📄 License

This project is licensed under the MIT License.

## 🎓 Citation

If you use DeepParameters in your research, please cite:

```bibtex
@software{deepparameters2025,
  title={DeepParameters: Neural Network Bayesian Network CPD Learning},
  author={Rudzani Mulaudzi},
  year={2025},
  version={2.0.4},
  url={https://github.com/rudzanimulaudzi/DeepParameters}
}
```

## 🆘 Support

Coming Soon

---

**DeepParameters** - Making advanced CPD learning accessible to everyone.
