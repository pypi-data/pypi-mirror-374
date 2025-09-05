# DeepParameters

**Advanced Neural Network CPD Learning for Bayesian Networks**
*Version 2.0.3 - Beta Release*

DeepParameters is a comprehensive Python package for learning Conditional Probability Distributions (CPDs) using state-of-the-art neural network architectures. It provides a unified interface for experimenting with various deep learning approaches to probabilistic modeling.

> 🎉 **Version 2.0.1** brings significant improvements: 9 neural architectures, 8 sampling methods, enhanced performance (26.5%-41.7% improvement), and beta stability!

## 🚀 Key Features

- **9 Neural Network Architectures**: Simple NN, Advanced NN, LSTM, Autoencoder, VAE, BNN, Normalizing Flow, Ultra, Mega
- **8 Sampling Methods**: Gibbs, Metropolis-Hastings, Importance, BPE, Variational, HMC, and more
- **Comprehensive Evaluation**: 7 performance metrics including MAE, KL divergence, and probability consistency
- **Simple Interface**: Unified `learn_cpd_for_node()` function for all architectures

## 📦 Installation

```bash
pip install deepparameters
# For the latest 2.0.1 features:
pip install --upgrade deepparameters
```

### What's New in 2.0.1

- **9 Neural Architectures**: From simple feedforward to advanced VAE and Normalizing Flows
- **8 Sampling Methods**: Comprehensive probabilistic inference toolkit
- **Performance Boost**: 26.5% to 41.7% improvement over previous versions
- **Beta Stability**: Continuously improving with extensive error handling
- **Better Documentation**: Complete workflow guides and migration assistance

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

# Advanced usage with custom architecture and sampling
cpd = learn_cpd_for_node(
    node='B',
    data=data,
    true_model=true_model,
    learnt_bn_structure=learnt_model,
    num_parameters=20,
    network_type='lstm',           # Try: simple, advanced, lstm, autoencoder, vae, bnn
    sampling_method='4',           # Try: 1-8 for different sampling methods
    epochs=200,
    verbose=True
)
```

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
# Full parameter configuration
cpd = learn_cpd_for_node(
    node='B',
    data=data,
    true_model=true_model,
    learnt_bn_structure=learnt_model,
    num_parameters=50,
    network_type='vae',
    sampling_method='8',
    epochs=500,
    batch_size=64,
    learning_rate=0.001,
    validation_split=0.2,
    early_stopping=True,
    verbose=True,
    random_state=42
)
```

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
@software{deepparameters2024,
  title={DeepParameters: Neural Network Bayesian Network CPD Learning},
  author={Rudzani Mulaudzi},
  year={2025},
  url={https://github.com/rudzanimulaudzi/DeepParameters}
}
```

## 🆘 Support

Coming Soon

---

**DeepParameters** - Making advanced CPD learning accessible to everyone.
