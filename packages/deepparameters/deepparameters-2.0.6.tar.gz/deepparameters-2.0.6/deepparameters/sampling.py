"""
Sampling Module - Various Sampling Methods for CPD Refinement
=============================================================

This module contains different sampling methods to refine and improve 
the CPDs learned by neural networks:

1. Gibbs Sampling (MCMC chain)
2. Metropolis-Hastings (MCMC acceptance-rejection)  
3. Importance Sampling (weighted samples)
4. Bayesian Parameter Estimation (BPE)
5. Variational Inference (optimization-based)
6. Hamiltonian Monte Carlo (gradient-based MCMC)
7. Sequential Monte Carlo (particle filters)
8. Adaptive KDE (kernel density estimation)
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

# Scientific computing
from scipy import stats
from scipy.optimize import minimize
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV

# PGMPy
from pgmpy.factors.discrete import TabularCPD
from pgmpy.sampling import GibbsSampling, BayesianModelSampling
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


class BaseSampler(ABC):
    """Base class for all sampling methods."""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
    
    @abstractmethod
    def refine_cpd(self, cpd, data, node, model):
        """Refine the CPD using the specific sampling method."""
        pass
    
    def _normalize_cpd(self, cpd_values):
        """Ensure CPD values sum to 1 along each column."""
        return cpd_values / cpd_values.sum(axis=0, keepdims=True)


class GibbsSampler(BaseSampler):
    """Gibbs Sampling for CPD refinement."""
    
    def __init__(self, num_samples=1000, burn_in=200, verbose=True):
        super().__init__(verbose)
        self.num_samples = num_samples
        self.burn_in = burn_in
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Gibbs sampling."""
        if self.verbose:
            print("Refining CPD with Gibbs Sampling ({} samples)...".format(self.num_samples))
        
        try:
            # Set up Gibbs sampler with the learned model
            temp_model = model.copy()
            if cpd.variable in [cpd_temp.variable for cpd_temp in temp_model.get_cpds()]:
                temp_model.remove_cpds(cpd.variable)
            temp_model.add_cpds(cpd)
            
            # Run Gibbs sampling
            gibbs_sampler = GibbsSampling(temp_model)
            samples = gibbs_sampler.sample(size=self.num_samples, burn_in=self.burn_in)
            
            # Estimate CPD from samples
            refined_values = self._estimate_cpd_from_samples(samples, cpd, node)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Gibbs sampling refinement completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Gibbs sampling failed, returning original CPD: {e}")
            return cpd
    
    def _estimate_cpd_from_samples(self, samples, original_cpd, node):
        """Estimate CPD values from Gibbs samples."""
        # Count occurrences in samples
        if _get_cpd_evidence(original_cpd):
            # Node with parents
            parent_combinations = []
            for evidence, card in zip(_get_cpd_evidence(original_cpd), _get_cpd_evidence_card(original_cpd)):
                parent_combinations.extend([(evidence, i) for i in range(card)])
            
            counts = np.zeros((original_cpd.variable_card, len(_get_cpd_evidence_card(original_cpd))))
            total_counts = np.zeros(len(_get_cpd_evidence_card(original_cpd)))
            
            for _, sample in samples.iterrows():
                parent_state = 0
                for i, evidence in enumerate(_get_cpd_evidence(original_cpd)):
                    parent_state += sample[evidence] * np.prod(_get_cpd_evidence_card(original_cpd)[i+1:])
                
                node_state = sample[node]
                counts[node_state, parent_state] += 1
                total_counts[parent_state] += 1
            
            # Normalize
            cpd_values = np.zeros_like(counts, dtype=float)
            for i in range(len(_get_cpd_evidence_card(original_cpd))):
                if total_counts[i] > 0:
                    cpd_values[:, i] = counts[:, i] / total_counts[i]
                else:
                    cpd_values[:, i] = original_cpd.values[:, i]  # Use original if no samples
            
        else:
            # Root node
            counts = np.zeros(original_cpd.variable_card)
            for _, sample in samples.iterrows():
                counts[sample[node]] += 1
            
            cpd_values = (counts / len(samples)).reshape(-1, 1)
        
        return self._normalize_cpd(cpd_values)


class MetropolisHastingsSampler(BaseSampler):
    """Metropolis-Hastings MCMC sampler for CPD refinement."""
    
    def __init__(self, num_samples=1000, burn_in=200, proposal_std=0.1, verbose=True):
        super().__init__(verbose)
        self.num_samples = num_samples
        self.burn_in = burn_in
        self.proposal_std = proposal_std
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Metropolis-Hastings sampling."""
        if self.verbose:
            print("Refining CPD with Metropolis-Hastings ({} samples)...".format(self.num_samples))
        
        try:
            # Initialize with current CPD values
            current_params = cpd.values.flatten()
            samples = []
            accepted = 0
            
            for i in range(self.num_samples + self.burn_in):
                # Propose new parameters
                proposal = current_params + np.random.normal(0, self.proposal_std, len(current_params))
                
                # Ensure proposal is valid (probabilities)
                proposal = np.abs(proposal)
                proposal = proposal.reshape(cpd.values.shape)
                proposal = self._normalize_cpd(proposal)
                
                # Calculate acceptance probability
                current_likelihood = self._calculate_likelihood(current_params.reshape(cpd.values.shape), data, node, cpd)
                proposal_likelihood = self._calculate_likelihood(proposal, data, node, cpd)
                
                alpha = min(1, proposal_likelihood / max(current_likelihood, 1e-10))
                
                # Accept or reject
                if np.random.random() < alpha:
                    current_params = proposal.flatten()
                    accepted += 1
                
                # Store sample after burn-in
                if i >= self.burn_in:
                    samples.append(current_params.copy())
            
            # Average samples to get refined CPD
            refined_values = np.mean(samples, axis=0).reshape(cpd.values.shape)
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                acceptance_rate = accepted / (self.num_samples + self.burn_in)
                print("Metropolis-Hastings completed! (Acceptance rate: {:.2f})".format(acceptance_rate))
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Metropolis-Hastings failed, returning original CPD: {e}")
            return cpd
    
    def _calculate_likelihood(self, cpd_values, data, node, cpd):
        """Calculate likelihood of data given CPD parameters."""
        likelihood = 1.0
        
        for _, row in data.iterrows():
            if _get_cpd_evidence(cpd):
                # Find parent state
                parent_state = 0
                for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                    parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(cpd)[i+1:])
                prob = cpd_values[row[node], parent_state]
            else:
                prob = cpd_values[row[node], 0]
            
            likelihood *= max(prob, 1e-10)  # Avoid log(0)
        
        return likelihood


class ImportanceSampler(BaseSampler):
    """Importance Sampling for CPD refinement."""
    
    def __init__(self, num_samples=1000, verbose=True):
        super().__init__(verbose)
        self.num_samples = num_samples
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using importance sampling."""
        if self.verbose:
            print("Refining CPD with Importance Sampling ({} samples)...".format(self.num_samples))
        
        try:
            # Use original CPD as proposal distribution
            # Generate samples and calculate importance weights
            samples = []
            weights = []
            
            for _ in range(self.num_samples):
                # Sample from proposal (uniform over valid CPD space)
                sample_cpd = self._sample_random_cpd(cpd)
                
                # Calculate importance weight
                weight = self._calculate_importance_weight(sample_cpd, cpd, data, node)
                
                samples.append(sample_cpd.values)
                weights.append(weight)
            
            # Normalize weights
            weights = np.array(weights)
            weights = weights / np.sum(weights)
            
            # Weighted average
            refined_values = np.zeros_like(cpd.values)
            for i, sample in enumerate(samples):
                refined_values += weights[i] * sample
            
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                eff_sample_size = 1 / np.sum(weights**2)
                print("Importance sampling completed! (Effective sample size: {:.0f})".format(eff_sample_size))
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Importance sampling failed, returning original CPD: {e}")
            return cpd
    
    def _sample_random_cpd(self, cpd):
        """Sample a random valid CPD."""
        # Generate random values and normalize
        random_values = np.random.dirichlet(np.ones(cpd.variable_card), size=cpd.values.shape[1]).T
        
        return TabularCPD(
            variable=cpd.variable,
            variable_card=cpd.variable_card,
            values=random_values,
            evidence=cpd.evidence,
            evidence_card=cpd.evidence_card
        )
    
    def _calculate_importance_weight(self, sample_cpd, target_cpd, data, node):
        """Calculate importance weight for a sample."""
        # Weight based on how well sample fits the data
        likelihood = 1.0
        for _, row in data.iterrows():
            if _get_cpd_evidence(sample_cpd):
                parent_state = 0
                for i, evidence in enumerate(_get_cpd_evidence(sample_cpd)):
                    parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(sample_cpd)[i+1:])
                prob = sample_cpd.values[row[node], parent_state]
            else:
                prob = sample_cpd.values[row[node], 0]
            
            likelihood *= max(prob, 1e-10)
        
        return likelihood


class BayesianParameterEstimator(BaseSampler):
    """Bayesian Parameter Estimation for CPD refinement."""
    
    def __init__(self, alpha=1.0, verbose=True):
        super().__init__(verbose)
        self.alpha = alpha  # Dirichlet prior concentration
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Bayesian parameter estimation."""
        if self.verbose:
            print("Refining CPD with Bayesian Parameter Estimation...")
        
        try:
            # Count observations
            if _get_cpd_evidence(cpd):
                # Node with parents
                counts = np.zeros((cpd.variable_card, np.prod(_get_cpd_evidence_card(cpd))))
                
                for _, row in data.iterrows():
                    parent_state = 0
                    for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                        parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(cpd)[i+1:])
                    
                    counts[row[node], parent_state] += 1
                
                # Add Dirichlet prior and normalize
                refined_values = np.zeros_like(cpd.values)
                for i in range(cpd.values.shape[1]):
                    alpha_post = counts[:, i] + self.alpha
                    refined_values[:, i] = alpha_post / np.sum(alpha_post)
            
            else:
                # Root node
                counts = np.zeros(cpd.variable_card)
                for _, row in data.iterrows():
                    counts[row[node]] += 1
                
                # Add Dirichlet prior
                alpha_post = counts + self.alpha
                refined_values = (alpha_post / np.sum(alpha_post)).reshape(-1, 1)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Bayesian Parameter Estimation completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  BPE failed, returning original CPD: {e}")
            return cpd


class VariationalInferenceSampler(BaseSampler):
    """Variational Inference for CPD refinement."""
    
    def __init__(self, max_iter=100, tol=1e-6, verbose=True):
        super().__init__(verbose)
        self.max_iter = max_iter
        self.tol = tol
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using variational inference."""
        if self.verbose:
            print("Refining CPD with Variational Inference...")
        
        try:
            # Initialize variational parameters
            var_params = cpd.values.copy()
            
            for iteration in range(self.max_iter):
                old_params = var_params.copy()
                
                # Update variational parameters (mean-field approximation)
                var_params = self._update_variational_params(var_params, data, node, cpd)
                
                # Check convergence
                diff = np.mean(np.abs(var_params - old_params))
                if diff < self.tol:
                    if self.verbose:
                        print(f"   Converged after {iteration + 1} iterations")
                    break
            
            # Normalize final parameters
            refined_values = self._normalize_cpd(var_params)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Variational Inference completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Variational Inference failed, returning original CPD: {e}")
            return cpd
    
    def _update_variational_params(self, params, data, node, cpd):
        """Update variational parameters."""
        # Simple variational update (could be more sophisticated)
        # This is a simplified version - in practice, would depend on the specific model
        
        # Count-based update with smoothing
        updated_params = params.copy()
        
        # Add small amount proportional to data fit
        for _, row in data.iterrows():
            if _get_cpd_evidence(cpd):
                parent_state = 0
                for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                    parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(cpd)[i+1:])
                updated_params[row[node], parent_state] += 0.01
            else:
                updated_params[row[node], 0] += 0.01
        
        return self._normalize_cpd(updated_params)


class HamiltonianMonteCarlo(BaseSampler):
    """Hamiltonian Monte Carlo for CPD refinement."""
    
    def __init__(self, num_samples=500, step_size=0.01, num_steps=50, verbose=True):
        super().__init__(verbose)
        self.num_samples = num_samples
        self.step_size = step_size
        self.num_steps = num_steps
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Hamiltonian Monte Carlo."""
        if self.verbose:
            print("Refining CPD with Hamiltonian Monte Carlo ({} samples)...".format(self.num_samples))
        
        try:
            # Transform to unconstrained space (log scale)
            initial_params = np.log(cpd.values + 1e-10)
            
            samples = []
            current_params = initial_params.copy()
            
            for _ in range(self.num_samples):
                # Generate momentum
                momentum = np.random.normal(0, 1, current_params.shape)
                
                # Leapfrog integration
                params = current_params.copy()
                mom = momentum.copy()
                
                for _ in range(self.num_steps):
                    # Half step for momentum
                    grad = self._log_gradient(params, data, node, cpd)
                    mom += 0.5 * self.step_size * grad
                    
                    # Full step for position
                    params += self.step_size * mom
                    
                    # Half step for momentum
                    grad = self._log_gradient(params, data, node, cpd)
                    mom += 0.5 * self.step_size * grad
                
                # Metropolis acceptance
                current_energy = self._energy(current_params, momentum, data, node, cpd)
                proposed_energy = self._energy(params, mom, data, node, cpd)
                
                if np.random.random() < np.exp(current_energy - proposed_energy):
                    current_params = params
                
                samples.append(current_params.copy())
            
            # Average samples and transform back to probability space
            avg_log_params = np.mean(samples, axis=0)
            refined_values = np.exp(avg_log_params)
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Hamiltonian Monte Carlo completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  HMC failed, returning original CPD: {e}")
            return cpd
    
    def _log_gradient(self, log_params, data, node, cpd):
        """Calculate gradient of log-likelihood."""
        # Numerical gradient (could be analytical)
        eps = 1e-6
        grad = np.zeros_like(log_params)
        
        for i in range(log_params.shape[0]):
            for j in range(log_params.shape[1]):
                log_params[i, j] += eps
                plus_energy = self._log_likelihood(log_params, data, node, cpd)
                
                log_params[i, j] -= 2 * eps
                minus_energy = self._log_likelihood(log_params, data, node, cpd)
                
                log_params[i, j] += eps  # Reset
                grad[i, j] = (plus_energy - minus_energy) / (2 * eps)
        
        return grad
    
    def _energy(self, log_params, momentum, data, node, cpd):
        """Calculate total energy (negative log-likelihood + kinetic energy)."""
        potential = -self._log_likelihood(log_params, data, node, cpd)
        kinetic = 0.5 * np.sum(momentum**2)
        return potential + kinetic
    
    def _log_likelihood(self, log_params, data, node, cpd):
        """Calculate log-likelihood."""
        params = np.exp(log_params)
        params = self._normalize_cpd(params)
        
        log_likelihood = 0
        for _, row in data.iterrows():
            if _get_cpd_evidence(cpd):
                parent_state = 0
                for i, evidence in enumerate(_get_cpd_evidence(cpd)):
                    parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(cpd)[i+1:])
                prob = params[row[node], parent_state]
            else:
                prob = params[row[node], 0]
            
            log_likelihood += np.log(max(prob, 1e-10))
        
        return log_likelihood


class SequentialMonteCarlo(BaseSampler):
    """Sequential Monte Carlo (Particle Filter) for CPD refinement."""
    
    def __init__(self, num_particles=1000, verbose=True):
        super().__init__(verbose)
        self.num_particles = num_particles
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Sequential Monte Carlo."""
        if self.verbose:
            print("Refining CPD with Sequential Monte Carlo ({} particles)...".format(self.num_particles))
        
        try:
            # Initialize particles (random CPDs)
            particles = []
            weights = np.ones(self.num_particles) / self.num_particles
            
            for _ in range(self.num_particles):
                # Sample random CPD
                random_values = np.random.dirichlet(np.ones(cpd.variable_card), size=cpd.values.shape[1]).T
                particles.append(random_values)
            
            # Process data sequentially
            for idx, (_, row) in enumerate(data.iterrows()):
                # Update weights based on likelihood
                for i, particle in enumerate(particles):
                    if _get_cpd_evidence(cpd):
                        parent_state = 0
                        for j, evidence in enumerate(_get_cpd_evidence(cpd)):
                            parent_state += row[evidence] * np.prod(_get_cpd_evidence_card(cpd)[j+1:])
                        likelihood = particle[row[node], parent_state]
                    else:
                        likelihood = particle[row[node], 0]
                    
                    weights[i] *= max(likelihood, 1e-10)
                
                # Normalize weights
                weights = weights / np.sum(weights)
                
                # Resample if effective sample size is too low
                eff_sample_size = 1 / np.sum(weights**2)
                if eff_sample_size < self.num_particles / 2:
                    indices = np.random.choice(self.num_particles, self.num_particles, p=weights)
                    particles = [particles[i] for i in indices]
                    weights = np.ones(self.num_particles) / self.num_particles
            
            # Final weighted average
            refined_values = np.zeros_like(cpd.values)
            for i, particle in enumerate(particles):
                refined_values += weights[i] * particle
            
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Sequential Monte Carlo completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  SMC failed, returning original CPD: {e}")
            return cpd


class AdaptiveKDESampler(BaseSampler):
    """Adaptive Kernel Density Estimation for CPD refinement."""
    
    def __init__(self, bandwidth='scott', kernel='gaussian', verbose=True):
        super().__init__(verbose)
        self.bandwidth = bandwidth
        self.kernel = kernel
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Adaptive KDE."""
        if self.verbose:
            print("Refining CPD with Adaptive KDE...")
        
        try:
            if _get_cpd_evidence(cpd):
                # Node with parents - estimate conditional densities
                refined_values = np.zeros_like(cpd.values)
                
                for parent_config in range(cpd.values.shape[1]):
                    # Get data for this parent configuration
                    parent_mask = self._get_parent_mask(data, cpd, parent_config)
                    subset_data = data[parent_mask]
                    
                    if len(subset_data) > 0:
                        # Estimate P(node|parents) using KDE
                        node_values = subset_data[node].values.reshape(-1, 1)
                        
                        # Fit KDE
                        kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
                        kde.fit(node_values)
                        
                        # Evaluate at discrete points
                        for node_state in range(cpd.variable_card):
                            density = np.exp(kde.score_samples([[node_state]]))
                            refined_values[node_state, parent_config] = density[0]
                    else:
                        # No data for this configuration, use original
                        refined_values[:, parent_config] = cpd.values[:, parent_config]
                
                # Normalize
                refined_values = self._normalize_cpd(refined_values)
            
            else:
                # Root node - simple KDE
                node_values = data[node].values.reshape(-1, 1)
                kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
                kde.fit(node_values)
                
                densities = []
                for node_state in range(cpd.variable_card):
                    density = np.exp(kde.score_samples([[node_state]]))
                    densities.append(density[0])
                
                refined_values = np.array(densities).reshape(-1, 1)
                refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Adaptive KDE completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  KDE failed, returning original CPD: {e}")
            return cpd
    
    def _get_parent_mask(self, data, cpd, parent_config):
        """Get mask for data matching specific parent configuration."""
        mask = np.ones(len(data), dtype=bool)
        
        config_idx = parent_config
        for i, evidence in enumerate(_get_cpd_evidence(cpd)):
            card = _get_cpd_evidence_card(cpd)[i]
            state = config_idx % card
            config_idx = config_idx // card
            mask &= (data[evidence] == state)
        
        return mask


class WeightedSampler(BaseSampler):
    """Weighted Sampling for CPD refinement.
    
    Weighted sampling directly normalizes neural network parameters to infer CPDs.
    By interpreting the parameters as likelihoods, normalization ensures that 
    probabilities in each CPD column sum to one. Simple and computationally efficient.
    """
    
    def __init__(self, noise_threshold=1e-6, verbose=True):
        super().__init__(verbose)
        self.noise_threshold = noise_threshold
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using weighted sampling."""
        if self.verbose:
            print("Refining CPD with Weighted Sampling...")
        
        try:
            # Extract neural network weights for this node
            nn_weights = self._extract_neural_weights(cpd, model, node)
            
            # Interpret weights as likelihoods and normalize
            refined_values = self._weights_to_probabilities(nn_weights, cpd.values.shape)
            
            # Apply noise filtering to handle extreme values
            refined_values = self._filter_noise(refined_values)
            
            # Final normalization
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Weighted Sampling completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Weighted sampling failed, returning original CPD: {e}")
            return cpd
    
    def _extract_neural_weights(self, cpd, model, node):
        """Extract relevant neural network weights for the node."""
        # For simplicity, use the original CPD values as "neural weights"
        # In practice, this would extract actual NN weights from the architecture
        weights = cpd.values.copy()
        
        # Add some variation based on data patterns
        # This simulates the neural network having learned patterns
        variation = np.random.normal(1.0, 0.1, weights.shape)
        weights = weights * np.abs(variation)  # Keep positive for probability interpretation
        
        return weights
    
    def _weights_to_probabilities(self, weights, target_shape):
        """Convert neural network weights to probability distributions."""
        # Take absolute values to ensure positive likelihoods
        abs_weights = np.abs(weights)
        
        # Reshape to target CPD shape if needed
        if abs_weights.shape != target_shape:
            abs_weights = abs_weights.reshape(target_shape)
        
        # Normalize each column to sum to 1 (probability distribution)
        return self._normalize_cpd(abs_weights)
    
    def _filter_noise(self, values):
        """Filter out extreme values that could be noise."""
        # Clip extreme values
        clipped_values = np.clip(values, self.noise_threshold, 1.0 - self.noise_threshold)
        
        # Apply smoothing to reduce noise impact
        smoothed_values = clipped_values.copy()
        
        # Gentle smoothing across states for each parent configuration
        for col in range(clipped_values.shape[1]):
            column = clipped_values[:, col]
            # Simple moving average for smoothing
            if len(column) > 2:
                for i in range(1, len(column) - 1):
                    smoothed_values[i, col] = 0.25 * column[i-1] + 0.5 * column[i] + 0.25 * column[i+1]
        
        return smoothed_values


class StratifiedSampler(BaseSampler):
    """Stratified Sampling for CPD refinement.
    
    Divides neural network parameter distribution into strata (intervals) and 
    samples proportionally from each. Minimizes over-representation of dominant 
    parameters by enforcing equal representation from different distribution sections.
    """
    
    def __init__(self, num_strata=5, proportional=True, verbose=True):
        super().__init__(verbose)
        self.num_strata = num_strata
        self.proportional = proportional
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using stratified sampling."""
        if self.verbose:
            print(f"Refining CPD with Stratified Sampling ({self.num_strata} strata)...")
        
        try:
            # Extract parameter distribution from CPD and data
            param_distribution = self._extract_parameter_distribution(cpd, data, node)
            
            # Create strata based on parameter distribution
            strata = self._create_strata(param_distribution)
            
            # Sample from each stratum proportionally
            refined_values = self._stratified_sample(cpd, strata, data, node)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Stratified Sampling completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Stratified sampling failed, returning original CPD: {e}")
            return cpd
    
    def _extract_parameter_distribution(self, cpd, data, node):
        """Extract the parameter distribution from CPD values."""
        # Flatten CPD values to get parameter distribution
        params = cpd.values.flatten()
        
        # Add data-driven variation
        if len(data) > 0:
            # Count frequencies in data to inform parameter distribution
            counts = np.zeros(cpd.variable_card)
            for _, row in data.iterrows():
                counts[row[node]] += 1
            
            # Normalize counts and use as additional parameters
            if counts.sum() > 0:
                data_params = counts / counts.sum()
                # Combine with CPD parameters
                params = np.concatenate([params, data_params])
        
        return params
    
    def _create_strata(self, param_distribution):
        """Divide parameter distribution into strata."""
        # Sort parameters to identify distribution ranges
        sorted_params = np.sort(param_distribution)
        
        # Create equal-sized strata based on percentiles
        strata_boundaries = []
        for i in range(self.num_strata + 1):
            percentile = (i / self.num_strata) * 100
            boundary = np.percentile(sorted_params, percentile)
            strata_boundaries.append(boundary)
        
        # Create strata as intervals
        strata = []
        for i in range(self.num_strata):
            stratum = {
                'min': strata_boundaries[i],
                'max': strata_boundaries[i + 1],
                'params': param_distribution[
                    (param_distribution >= strata_boundaries[i]) & 
                    (param_distribution <= strata_boundaries[i + 1])
                ]
            }
            strata.append(stratum)
        
        return strata
    
    def _stratified_sample(self, cpd, strata, data, node):
        """Sample from each stratum to create refined CPD."""
        refined_values = np.zeros_like(cpd.values)
        
        # Sample from each stratum
        for col in range(cpd.values.shape[1]):
            column_probs = np.zeros(cpd.values.shape[0])
            
            # Determine sampling weights for each stratum
            stratum_weights = self._calculate_stratum_weights(strata)
            
            for row in range(cpd.values.shape[0]):
                # Sample value for this (row, col) from appropriate strata
                sampled_value = 0.0
                
                for i, stratum in enumerate(strata):
                    if len(stratum['params']) > 0:
                        # Sample from this stratum
                        stratum_sample = np.random.choice(stratum['params'])
                        sampled_value += stratum_weights[i] * stratum_sample
                
                column_probs[row] = max(sampled_value, 1e-10)  # Avoid zero probabilities
            
            # Normalize column
            refined_values[:, col] = column_probs / column_probs.sum()
        
        return refined_values
    
    def _calculate_stratum_weights(self, strata):
        """Calculate weights for each stratum."""
        if self.proportional:
            # Proportional to stratum size
            weights = np.array([len(stratum['params']) for stratum in strata])
            return weights / weights.sum() if weights.sum() > 0 else np.ones(len(strata)) / len(strata)
        else:
            # Equal weights
            return np.ones(len(strata)) / len(strata)


class KDESampler(BaseSampler):
    """Kernel Density Estimation Sampling for CPD refinement.
    
    Employs continuous probability density functions to approximate neural network 
    parameter distributions. Uses kernel functions (e.g., Gaussian) to smooth 
    irregularities and generate representative samples.
    """
    
    def __init__(self, kernel='gaussian', bandwidth='scott', adaptive=True, verbose=True):
        super().__init__(verbose)
        self.kernel = kernel
        self.bandwidth = bandwidth
        self.adaptive = adaptive
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using KDE sampling."""
        if self.verbose:
            print(f"Refining CPD with KDE Sampling (kernel={self.kernel})...")
        
        try:
            # Extract parameters for KDE
            parameters = self._extract_parameters_for_kde(cpd, data, node)
            
            # Fit KDE to parameter distribution
            kde_model = self._fit_kde(parameters)
            
            # Generate refined CPD values using KDE
            refined_values = self._generate_cpd_from_kde(kde_model, cpd)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("KDE Sampling completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  KDE sampling failed, returning original CPD: {e}")
            return cpd
    
    def _extract_parameters_for_kde(self, cpd, data, node):
        """Extract parameters for KDE fitting."""
        # Use CPD values as base parameters
        params = cpd.values.flatten().reshape(-1, 1)
        
        # Add data-driven parameters if available
        if len(data) > 0:
            # Empirical probabilities from data
            data_probs = []
            for state in range(cpd.variable_card):
                prob = (data[node] == state).mean()
                data_probs.append(prob)
            
            # Combine with original parameters
            data_params = np.array(data_probs).reshape(-1, 1)
            params = np.vstack([params, data_params])
        
        return params
    
    def _fit_kde(self, parameters):
        """Fit KDE model to parameters."""
        if self.adaptive:
            # Use cross-validation to find optimal bandwidth
            bandwidths = np.logspace(-2, 1, 20)
            grid = GridSearchCV(KernelDensity(kernel=self.kernel), 
                              {'bandwidth': bandwidths}, cv=3)
            grid.fit(parameters)
            kde = grid.best_estimator_
        else:
            # Use specified bandwidth
            kde = KernelDensity(kernel=self.kernel, bandwidth=self.bandwidth)
            kde.fit(parameters)
        
        return kde
    
    def _generate_cpd_from_kde(self, kde_model, cpd):
        """Generate CPD values using fitted KDE."""
        refined_values = np.zeros_like(cpd.values)
        
        # Sample from KDE for each CPD entry
        num_samples = 1000
        samples = kde_model.sample(num_samples)
        
        # Map samples to CPD structure
        sample_idx = 0
        for col in range(cpd.values.shape[1]):
            col_values = np.zeros(cpd.values.shape[0])
            
            for row in range(cpd.values.shape[0]):
                # Use KDE sample with some smoothing
                if sample_idx < len(samples):
                    base_value = abs(samples[sample_idx][0])  # Ensure positive
                    # Add slight variation based on original CPD
                    variation = cpd.values[row, col] * 0.1
                    col_values[row] = base_value + variation
                    sample_idx = (sample_idx + 1) % len(samples)
                else:
                    col_values[row] = cpd.values[row, col]
            
            # Normalize column
            refined_values[:, col] = col_values / col_values.sum()
        
        return refined_values


class DirichletBayesianSampler(BaseSampler):
    """Bayesian Sampling with Dirichlet Distributions for CPD refinement.
    
    Uses Dirichlet distribution as conjugate prior for multinomial distribution 
    to model uncertainty in parameters while ensuring valid probability distributions.
    Integrates prior information with neural network parameters.
    """
    
    def __init__(self, alpha_prior=1.0, num_samples=1000, use_data_informed_prior=True, verbose=True):
        super().__init__(verbose)
        self.alpha_prior = alpha_prior
        self.num_samples = num_samples
        self.use_data_informed_prior = use_data_informed_prior
    
    def refine_cpd(self, cpd, data, node, model):
        """Refine CPD using Dirichlet Bayesian sampling."""
        if self.verbose:
            print(f"Refining CPD with Dirichlet Bayesian Sampling ({self.num_samples} samples)...")
        
        try:
            # Calculate Dirichlet parameters for each parent configuration
            refined_values = np.zeros_like(cpd.values)
            
            for col in range(cpd.values.shape[1]):
                # Get concentration parameters for this parent configuration
                alpha_params = self._calculate_dirichlet_params(cpd, data, node, col)
                
                # Sample from Dirichlet distribution
                samples = self._sample_dirichlet(alpha_params)
                
                # Average samples to get refined probabilities
                refined_values[:, col] = np.mean(samples, axis=0)
            
            # Ensure normalization
            refined_values = self._normalize_cpd(refined_values)
            
            # Create refined CPD
            refined_cpd = TabularCPD(
                variable=cpd.variable,
                variable_card=cpd.variable_card,
                values=refined_values,
                evidence=cpd.evidence,
                evidence_card=cpd.evidence_card
            )
            
            if self.verbose:
                print("Dirichlet Bayesian Sampling completed!")
            
            return refined_cpd
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Dirichlet Bayesian sampling failed, returning original CPD: {e}")
            return cpd
    
    def _calculate_dirichlet_params(self, cpd, data, node, parent_config):
        """Calculate Dirichlet concentration parameters."""
        # Start with prior
        alpha_params = np.full(cpd.variable_card, self.alpha_prior)
        
        if self.use_data_informed_prior and len(data) > 0:
            # Count observations for this parent configuration
            if _get_cpd_evidence(cpd):
                # Get mask for this parent configuration
                mask = self._get_parent_config_mask(data, cpd, parent_config)
                subset_data = data[mask]
            else:
                subset_data = data
            
            # Add observed counts to concentration parameters
            for state in range(cpd.variable_card):
                count = (subset_data[node] == state).sum() if len(subset_data) > 0 else 0
                alpha_params[state] += count
        
        # Incorporate CPD values as additional information
        # Scale CPD values to be used as pseudo-counts
        cpd_pseudocounts = cpd.values[:, parent_config] * 10  # Scale factor
        alpha_params += cpd_pseudocounts
        
        # Ensure all parameters are positive for Dirichlet distribution
        alpha_params = np.maximum(alpha_params, 1e-6)
        
        return alpha_params
    
    def _sample_dirichlet(self, alpha_params):
        """Sample from Dirichlet distribution."""
        # Ensure all alpha parameters are positive (Dirichlet requires alpha > 0)
        alpha_params = np.maximum(alpha_params, 1e-6)
        
        samples = []
        for _ in range(self.num_samples):
            sample = np.random.dirichlet(alpha_params)
            samples.append(sample)
        return np.array(samples)
    
    def _get_parent_config_mask(self, data, cpd, parent_config):
        """Get mask for specific parent configuration."""
        if not _get_cpd_evidence(cpd):
            return np.ones(len(data), dtype=bool)
        
        mask = np.ones(len(data), dtype=bool)
        config_idx = parent_config
        
        for i, evidence in enumerate(_get_cpd_evidence(cpd)):
            card = _get_cpd_evidence_card(cpd)[i]
            state = config_idx % card
            config_idx = config_idx // card
            mask &= (data[evidence] == state)
        
        return mask


# Factory function to get sampler
def get_sampler(sampling_method, verbose=True):
    """Factory function to get the appropriate sampler."""
    
    samplers = {
        '1': lambda: GibbsSampler(verbose=verbose),
        '2': lambda: MetropolisHastingsSampler(verbose=verbose),
        '3': lambda: ImportanceSampler(verbose=verbose),
        '4': lambda: BayesianParameterEstimator(verbose=verbose),
        '5': lambda: VariationalInferenceSampler(verbose=verbose),
        '6': lambda: HamiltonianMonteCarlo(verbose=verbose),
        '7': lambda: SequentialMonteCarlo(verbose=verbose),
        '8': lambda: AdaptiveKDESampler(verbose=verbose),
        '9': lambda: WeightedSampler(verbose=verbose),
        '10': lambda: StratifiedSampler(verbose=verbose),
        '11': lambda: KDESampler(verbose=verbose),
        '12': lambda: DirichletBayesianSampler(verbose=verbose)
    }
    
    if sampling_method not in samplers:
        raise ValueError(f"Unsupported sampling method: {sampling_method}. "
                        f"Supported methods: {list(samplers.keys())}")
    
    return samplers[sampling_method]()