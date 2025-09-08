"""
Parallel Learning Module - Multi-threaded CPD Learning for DeepParameters
==========================================================================

This module implements parallel learning capabilities to optimize parameter learning
time by bounded execution across factor groups. The maximum time is bounded by the
largest factor group, enabling significant speedup for complex Bayesian networks.

Key Features:
- Factor group decomposition for parallel execution
- Time-bounded learning with early termination
- Progress tracking across parallel workers
- Memory-efficient multi-processing support
- Automatic load balancing and resource management
"""

import numpy as np
import pandas as pd
import time
import warnings
from typing import List, Dict, Tuple, Optional, Any, Union
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import Manager, Queue, Value
from threading import Lock
import networkx as nx
from abc import ABC, abstractmethod
import logging

# Suppress warnings
warnings.filterwarnings('ignore')

# Core dependencies
try:
    from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
except ImportError:
    from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD

# Package imports
from .core import learn_cpd_for_node
from .utils import validate_inputs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FactorGroup:
    """Represents a group of nodes that can be learned in parallel."""
    
    def __init__(self, nodes: List[str], group_id: int):
        self.nodes = nodes
        self.group_id = group_id
        self.estimated_complexity = len(nodes)  # Simple complexity metric
        self.learned_cpds = {}
        self.start_time = None
        self.end_time = None
        self.success = False
        
    def __len__(self):
        return len(self.nodes)
    
    def __repr__(self):
        return f"FactorGroup(id={self.group_id}, nodes={self.nodes}, complexity={self.estimated_complexity})"


class ParallelLearningProgress:
    """Tracks progress across parallel learning workers."""
    
    def __init__(self, total_groups: int, total_nodes: int):
        self.total_groups = total_groups
        self.total_nodes = total_nodes
        self.completed_groups = 0
        self.completed_nodes = 0
        self.failed_nodes = 0
        self.start_time = time.time()
        self.group_progress = {}
        self.lock = Lock()
    
    def update_group_progress(self, group_id: int, completed_nodes: int, total_nodes: int):
        """Update progress for a specific group."""
        with self.lock:
            self.group_progress[group_id] = {
                'completed': completed_nodes,
                'total': total_nodes,
                'progress': completed_nodes / total_nodes if total_nodes > 0 else 0.0
            }
    
    def mark_group_completed(self, group_id: int, success: bool = True):
        """Mark a group as completed."""
        with self.lock:
            self.completed_groups += 1
            if group_id in self.group_progress:
                if success:
                    self.completed_nodes += self.group_progress[group_id]['total']
                else:
                    self.failed_nodes += self.group_progress[group_id]['total']
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall progress statistics."""
        with self.lock:
            elapsed_time = time.time() - self.start_time
            return {
                'groups_completed': self.completed_groups,
                'total_groups': self.total_groups,
                'group_progress': self.completed_groups / self.total_groups if self.total_groups > 0 else 0.0,
                'nodes_completed': self.completed_nodes,
                'nodes_failed': self.failed_nodes,
                'total_nodes': self.total_nodes,
                'node_progress': self.completed_nodes / self.total_nodes if self.total_nodes > 0 else 0.0,
                'elapsed_time': elapsed_time,
                'estimated_remaining': self._estimate_remaining_time(elapsed_time)
            }
    
    def _estimate_remaining_time(self, elapsed_time: float) -> float:
        """Estimate remaining time based on current progress."""
        if self.completed_nodes == 0:
            return float('inf')
        
        rate = self.completed_nodes / elapsed_time
        remaining_nodes = self.total_nodes - self.completed_nodes
        return remaining_nodes / rate if rate > 0 else float('inf')


class ParallelCPDLearner:
    """Main class for parallel CPD learning with factor group decomposition."""
    
    def __init__(self, 
                 max_workers: Optional[int] = None,
                 max_time_per_group: Optional[float] = None,
                 use_threading: bool = True,
                 parallel_style: str = 'topological',
                 progress_callback: Optional[callable] = None,
                 verbose: bool = True):
        """
        Initialize parallel CPD learner.
        
        Parameters:
        -----------
        max_workers : int, optional
            Maximum number of parallel workers. Default: CPU count
        max_time_per_group : float, optional
            Maximum time allowed per factor group (seconds). Default: unlimited
        use_threading : bool, default=True
            Use threading instead of multiprocessing (better for I/O bound tasks)
        parallel_style : str, default='topological'
            Parallel decomposition style:
            - 'topological': Group nodes by topological levels
            - 'parent_child': Group nodes by parent-child relationships
        progress_callback : callable, optional
            Callback function to report progress updates
        verbose : bool, default=True
            Enable verbose output
        """
        self.max_workers = max_workers
        self.max_time_per_group = max_time_per_group
        self.use_threading = use_threading
        self.parallel_style = parallel_style
        self.progress_callback = progress_callback
        self.verbose = verbose
        
        # Internal state
        self.factor_groups = []
        self.progress = None
        self.learned_cpds = {}
        
    def learn_network_parameters(self,
                                data: pd.DataFrame,
                                true_model: BayesianNetwork,
                                learnt_bn_structure: BayesianNetwork,
                                network_type: str = "simple",
                                sampling_method: str = "1",
                                epochs: int = 100,
                                batch_size: int = 32,
                                learning_rate: float = 0.001,
                                validation_split: float = 0.2,
                                early_stopping: bool = True,
                                random_state: int = 42,
                                **kwargs) -> Dict[str, TabularCPD]:
        """
        Learn CPDs for all nodes in the network using parallel execution.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Training data containing all variables
        true_model : BayesianNetwork
            The true Bayesian network structure
        learnt_bn_structure : BayesianNetwork
            The learned Bayesian network structure
        network_type : str, default="simple"
            Type of neural network architecture
        sampling_method : str, default="1"
            Sampling method for CPD refinement
        epochs : int, default=100
            Number of training epochs
        batch_size : int, default=32
            Training batch size
        learning_rate : float, default=0.001
            Learning rate for optimization
        validation_split : float, default=0.2
            Fraction of data for validation
        early_stopping : bool, default=True
            Whether to use early stopping
        random_state : int, default=42
            Random seed for reproducibility
        **kwargs : dict
            Additional parameters for CPD learning
            
        Returns:
        --------
        Dict[str, TabularCPD]
            Dictionary mapping node names to learned CPDs
        """
        if self.verbose:
            print("🚀 Starting Parallel CPD Learning")
            print("=" * 50)
        
        # 1. Decompose network into factor groups
        self.factor_groups = self._decompose_into_factor_groups(learnt_bn_structure, self.parallel_style)
        
        if self.verbose:
            print(f"📊 Network decomposed into {len(self.factor_groups)} factor groups:")
            for group in self.factor_groups:
                print(f"   Group {group.group_id}: {group.nodes} (complexity: {group.estimated_complexity})")
        
        # 2. Initialize progress tracking
        total_nodes = sum(len(group.nodes) for group in self.factor_groups)
        self.progress = ParallelLearningProgress(len(self.factor_groups), total_nodes)
        
        # 3. Execute parallel learning
        start_time = time.time()
        
        if self.use_threading:
            executor_class = ThreadPoolExecutor
        else:
            executor_class = ProcessPoolExecutor
        
        max_workers = self.max_workers or min(len(self.factor_groups), 4)
        
        if self.verbose:
            print(f"⚡ Starting parallel execution with {max_workers} workers")
            print(f"📋 Total nodes to learn: {total_nodes}")
        
        with executor_class(max_workers=max_workers) as executor:
            # Submit all factor groups for parallel processing
            future_to_group = {}
            
            for group in self.factor_groups:
                future = executor.submit(
                    self._learn_factor_group,
                    group, data, true_model, learnt_bn_structure,
                    network_type, sampling_method, epochs, batch_size,
                    learning_rate, validation_split, early_stopping,
                    random_state, **kwargs
                )
                future_to_group[future] = group
            
            # Collect results as they complete
            completed_groups = 0
            for future in as_completed(future_to_group, timeout=self.max_time_per_group):
                group = future_to_group[future]
                
                try:
                    group_cpds = future.result()
                    self.learned_cpds.update(group_cpds)
                    group.success = True
                    group.learned_cpds = group_cpds
                    
                    if self.verbose:
                        print(f"✅ Group {group.group_id} completed successfully ({len(group_cpds)} CPDs)")
                    
                except Exception as e:
                    if self.verbose:
                        print(f"❌ Group {group.group_id} failed: {str(e)}")
                    group.success = False
                    logger.error(f"Group {group.group_id} learning failed: {e}")
                
                # Update progress
                completed_groups += 1
                self.progress.mark_group_completed(group.group_id, group.success)
                
                if self.progress_callback:
                    self.progress_callback(self.progress.get_overall_progress())
                
                if self.verbose:
                    progress_info = self.progress.get_overall_progress()
                    print(f"📈 Progress: {completed_groups}/{len(self.factor_groups)} groups, "
                          f"{progress_info['nodes_completed']}/{total_nodes} nodes "
                          f"({progress_info['node_progress']:.1%})")
        
        total_time = time.time() - start_time
        
        if self.verbose:
            print("=" * 50)
            print(f"🎯 Parallel CPD Learning Completed!")
            print(f"⏱️  Total time: {total_time:.2f} seconds")
            print(f"✅ Successfully learned: {len(self.learned_cpds)} CPDs")
            print(f"❌ Failed nodes: {self.progress.failed_nodes}")
            
            # Calculate speedup estimate
            sequential_estimate = total_nodes * (total_time / len(self.factor_groups))
            speedup = sequential_estimate / total_time if total_time > 0 else 1.0
            print(f"🚀 Estimated speedup: {speedup:.1f}x")
        
        return self.learned_cpds
    
    def _decompose_into_factor_groups(self, bn_structure: BayesianNetwork, parallel_style: str = 'topological') -> List[FactorGroup]:
        """
        Decompose Bayesian network into factor groups for parallel learning.
        
        Parameters:
        -----------
        bn_structure : BayesianNetwork
            The Bayesian network structure
        parallel_style : str
            Decomposition strategy:
            - 'topological': Group by topological levels (current implementation)
            - 'parent_child': Group by parent-child relationships
        
        Returns:
        --------
        List[FactorGroup]
            List of factor groups for parallel execution
        """
        valid_styles = ['topological', 'parent_child']
        if parallel_style not in valid_styles:
            raise ValueError(f"Invalid parallel_style '{parallel_style}'. "
                           f"Valid options: {valid_styles}")
        
        if parallel_style == 'parent_child':
            return self._decompose_parent_child_groups(bn_structure)
        else:  # topological (default)
            return self._decompose_topological_groups(bn_structure)
    
    def _decompose_topological_groups(self, bn_structure: BayesianNetwork) -> List[FactorGroup]:
        """
        Decompose using topological levels (original implementation).
        
        Factor groups are sets of nodes that can be learned independently
        based on the network structure and dependencies.
        """
        # Convert to NetworkX graph for easier analysis
        graph = nx.DiGraph()
        graph.add_nodes_from(bn_structure.nodes())
        graph.add_edges_from(bn_structure.edges())
        
        # Find strongly connected components and topological ordering
        try:
            # For DAGs, SCCs are just individual nodes
            topo_order = list(nx.topological_sort(graph))
        except nx.NetworkXError:
            # Fallback for non-DAG graphs
            topo_order = list(graph.nodes())
        
        # Group nodes by their level in the topological order
        # Nodes at the same level can potentially be learned in parallel
        node_levels = {}
        for i, node in enumerate(topo_order):
            # Calculate the maximum distance from root nodes
            predecessors = list(graph.predecessors(node))
            if not predecessors:
                node_levels[node] = 0  # Root node
            else:
                max_pred_level = max(node_levels.get(pred, 0) for pred in predecessors)
                node_levels[node] = max_pred_level + 1
        
        # Group nodes by level
        level_groups = {}
        for node, level in node_levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
        
        # Create factor groups
        factor_groups = []
        for level, nodes in sorted(level_groups.items()):
            # Further split large groups to balance load
            if len(nodes) > 4:  # Threshold for splitting
                # Split into smaller sub-groups
                chunk_size = max(1, len(nodes) // 3)  # Target 3 sub-groups max
                for i in range(0, len(nodes), chunk_size):
                    chunk = nodes[i:i + chunk_size]
                    group = FactorGroup(chunk, len(factor_groups))
                    group.estimated_complexity = self._estimate_group_complexity(chunk, graph)
                    factor_groups.append(group)
            else:
                group = FactorGroup(nodes, len(factor_groups))
                group.estimated_complexity = self._estimate_group_complexity(nodes, graph)
                factor_groups.append(group)
        
        # Sort groups by complexity (largest first for better load balancing)
        factor_groups.sort(key=lambda g: g.estimated_complexity, reverse=True)
        
        # Reassign group IDs after sorting
        for i, group in enumerate(factor_groups):
            group.group_id = i
        
        return factor_groups
    
    def _decompose_parent_child_groups(self, bn_structure: BayesianNetwork) -> List[FactorGroup]:
        """
        Decompose using parent-child relationships for better scalability.
        
        This approach groups sibling nodes (nodes with the same parents) together,
        which often provides better performance characteristics.
        """
        # Convert to NetworkX graph for easier analysis
        graph = nx.DiGraph()
        graph.add_nodes_from(bn_structure.nodes())
        graph.add_edges_from(bn_structure.edges())
        
        # Group nodes by their parent signature
        parent_groups = {}
        
        for node in graph.nodes():
            # Get sorted parent list as signature
            parents = tuple(sorted(graph.predecessors(node)))
            
            if parents not in parent_groups:
                parent_groups[parents] = []
            parent_groups[parents].append(node)
        
        # Create factor groups from parent groups
        factor_groups = []
        
        # Sort parent groups by complexity (number of parents + number of nodes)
        sorted_parent_groups = sorted(
            parent_groups.items(),
            key=lambda x: len(x[0]) + len(x[1]),  # parents + nodes count
            reverse=True
        )
        
        for group_id, (parents, nodes) in enumerate(sorted_parent_groups):
            # Further split large sibling groups for load balancing
            if len(nodes) > 6:  # Threshold for splitting sibling groups
                chunk_size = max(2, len(nodes) // 3)  # Target 3 sub-groups
                for i in range(0, len(nodes), chunk_size):
                    chunk = nodes[i:i + chunk_size]
                    group = FactorGroup(chunk, len(factor_groups))
                    group.estimated_complexity = self._estimate_parent_child_complexity(
                        chunk, parents, graph
                    )
                    factor_groups.append(group)
            else:
                group = FactorGroup(nodes, group_id)
                group.estimated_complexity = self._estimate_parent_child_complexity(
                    nodes, parents, graph
                )
                factor_groups.append(group)
        
        # Re-assign group IDs after potential splitting
        for i, group in enumerate(factor_groups):
            group.group_id = i
        
        return factor_groups
    
    def _estimate_parent_child_complexity(self, nodes: List[str], parents: tuple, graph: nx.DiGraph) -> float:
        """
        Estimate computational complexity for parent-child groups.
        """
        base_complexity = len(nodes)
        
        # Add complexity based on number of parents
        parent_complexity = len(parents) * 0.8
        
        # Add complexity based on children connections
        children_complexity = 0
        for node in nodes:
            children_complexity += len(list(graph.successors(node))) * 0.3
        
        # Sibling groups with the same parents are more efficient
        sibling_efficiency = max(0.5, 1.0 - (len(nodes) - 1) * 0.1)
        
        total_complexity = (base_complexity + parent_complexity + children_complexity) * sibling_efficiency
        
        return total_complexity
    
    def _estimate_group_complexity(self, nodes: List[str], graph: nx.DiGraph) -> float:
        """Estimate computational complexity of learning a factor group."""
        complexity = 0.0
        
        for node in nodes:
            # Base complexity per node
            node_complexity = 1.0
            
            # Add complexity based on number of parents
            num_parents = len(list(graph.predecessors(node)))
            node_complexity += num_parents * 0.5
            
            # Add complexity based on number of children (affects data dependencies)
            num_children = len(list(graph.successors(node)))
            node_complexity += num_children * 0.2
            
            complexity += node_complexity
        
        return complexity
    
    def _learn_factor_group(self,
                           group: FactorGroup,
                           data: pd.DataFrame,
                           true_model: BayesianNetwork,
                           learnt_bn_structure: BayesianNetwork,
                           network_type: str,
                           sampling_method: str,
                           epochs: int,
                           batch_size: int,
                           learning_rate: float,
                           validation_split: float,
                           early_stopping: bool,
                           random_state: int,
                           **kwargs) -> Dict[str, TabularCPD]:
        """
        Learn CPDs for all nodes in a factor group.
        
        This function runs in a separate process/thread.
        """
        group.start_time = time.time()
        group_cpds = {}
        
        try:
            for i, node in enumerate(group.nodes):
                # Check time limit
                if self.max_time_per_group:
                    elapsed = time.time() - group.start_time
                    if elapsed > self.max_time_per_group:
                        logger.warning(f"Group {group.group_id} exceeded time limit, stopping early")
                        break
                
                # Learn CPD for this node
                try:
                    # Estimate num_parameters based on node structure
                    num_parents = len(list(learnt_bn_structure.predecessors(node)))
                    num_parameters = max(4, num_parents * 2)
                    
                    cpd = learn_cpd_for_node(
                        node=node,
                        data=data,
                        true_model=true_model,
                        learnt_bn_structure=learnt_bn_structure,
                        num_parameters=num_parameters,
                        network_type=network_type,
                        sampling_method=sampling_method,
                        epochs=epochs,
                        batch_size=batch_size,
                        learning_rate=learning_rate,
                        validation_split=validation_split,
                        early_stopping=early_stopping,
                        verbose=False,  # Suppress individual node verbosity
                        random_state=random_state + hash(node) % 1000,  # Unique seed per node
                        **{k: v for k, v in kwargs.items() if k != 'verbose'}  # Exclude duplicate verbose
                    )
                    
                    group_cpds[node] = cpd
                    
                    # Update progress
                    if self.progress:
                        self.progress.update_group_progress(group.group_id, i + 1, len(group.nodes))
                
                except Exception as e:
                    logger.error(f"Failed to learn CPD for node {node} in group {group.group_id}: {e}")
                    # Continue with other nodes in the group
                    continue
        
        except Exception as e:
            logger.error(f"Fatal error in group {group.group_id}: {e}")
            raise e
        
        finally:
            group.end_time = time.time()
        
        return group_cpds
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the parallel learning process."""
        if not self.factor_groups or not self.progress:
            return {}
        
        total_time = max(
            (group.end_time - group.start_time for group in self.factor_groups if group.end_time),
            default=0.0
        )
        
        group_times = [
            group.end_time - group.start_time
            for group in self.factor_groups
            if group.start_time and group.end_time
        ]
        
        successful_groups = [group for group in self.factor_groups if group.success]
        failed_groups = [group for group in self.factor_groups if not group.success]
        
        stats = {
            'total_groups': len(self.factor_groups),
            'successful_groups': len(successful_groups),
            'failed_groups': len(failed_groups),
            'success_rate': len(successful_groups) / len(self.factor_groups) if self.factor_groups else 0.0,
            'total_time': total_time,
            'avg_group_time': np.mean(group_times) if group_times else 0.0,
            'max_group_time': max(group_times) if group_times else 0.0,
            'min_group_time': min(group_times) if group_times else 0.0,
            'learned_cpds': len(self.learned_cpds),
            'factor_groups': [
                {
                    'group_id': group.group_id,
                    'nodes': group.nodes,
                    'complexity': group.estimated_complexity,
                    'success': group.success,
                    'time': group.end_time - group.start_time if group.start_time and group.end_time else None,
                    'cpds_learned': len(group.learned_cpds)
                }
                for group in self.factor_groups
            ]
        }
        
        return stats


def learn_network_parameters_parallel(data: pd.DataFrame,
                                     true_model: BayesianNetwork,
                                     learnt_bn_structure: BayesianNetwork,
                                     max_workers: Optional[int] = None,
                                     max_time_per_group: Optional[float] = None,
                                     parallel_style: str = 'topological',
                                     network_type: str = "simple",
                                     sampling_method: str = "1",
                                     epochs: int = 100,
                                     verbose: bool = True,
                                     **kwargs) -> Dict[str, TabularCPD]:
    """
    Convenience function for parallel CPD learning.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Training data containing all variables
    true_model : BayesianNetwork
        The true Bayesian network structure
    learnt_bn_structure : BayesianNetwork
        The learned Bayesian network structure
    max_workers : int, optional
        Maximum number of parallel workers
    max_time_per_group : float, optional
        Maximum time allowed per factor group (seconds)
    parallel_style : str, default='topological'
        Parallel decomposition style:
        - 'topological': Group nodes by topological levels
        - 'parent_child': Group nodes by parent-child relationships
    network_type : str, default="simple"
        Type of neural network architecture
    sampling_method : str, default="1"
        Sampling method for CPD refinement
    epochs : int, default=100
        Number of training epochs
    verbose : bool, default=True
        Enable verbose output
    **kwargs : dict
        Additional parameters for CPD learning
        
    Returns:
    --------
    Dict[str, TabularCPD]
        Dictionary mapping node names to learned CPDs
    """
    learner = ParallelCPDLearner(
        max_workers=max_workers,
        max_time_per_group=max_time_per_group,
        parallel_style=parallel_style,
        verbose=verbose
    )
    
    return learner.learn_network_parameters(
        data=data,
        true_model=true_model,
        learnt_bn_structure=learnt_bn_structure,
        network_type=network_type,
        sampling_method=sampling_method,
        epochs=epochs,
        **kwargs
    )


class ParallelLearningBenchmark:
    """Benchmark tool to compare sequential vs parallel learning performance."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {}
    
    def benchmark_performance(self,
                            data: pd.DataFrame,
                            true_model: BayesianNetwork,
                            learnt_bn_structure: BayesianNetwork,
                            network_type: str = "simple",
                            sampling_method: str = "1",
                            epochs: int = 50,
                            max_workers_list: List[int] = [1, 2, 4],
                            parallel_style: str = 'topological',
                            **kwargs) -> Dict[str, Any]:
        """
        Benchmark parallel vs sequential learning performance.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Training data
        true_model : BayesianNetwork
            True network structure
        learnt_bn_structure : BayesianNetwork
            Learned network structure
        network_type : str
            Neural network architecture type
        sampling_method : str
            Sampling method for refinement
        epochs : int
            Training epochs
        max_workers_list : List[int]
            List of worker counts to test
        parallel_style : str
            Parallel decomposition style ('topological' or 'parent_child')
        **kwargs : dict
            Additional learning parameters
            
        Returns:
        --------
        Dict[str, Any]
            Benchmark results with timing and performance metrics
        """
        if self.verbose:
            print("🔬 Starting Parallel Learning Benchmark")
            print("=" * 50)
        
        results = {}
        
        for max_workers in max_workers_list:
            if self.verbose:
                print(f"\n⚡ Testing with {max_workers} worker(s)...")
            
            start_time = time.time()
            
            try:
                learner = ParallelCPDLearner(
                    max_workers=max_workers,
                    parallel_style=parallel_style,
                    verbose=False  # Suppress detailed output during benchmark
                )
                
                learned_cpds = learner.learn_network_parameters(
                    data=data,
                    true_model=true_model,
                    learnt_bn_structure=learnt_bn_structure,
                    network_type=network_type,
                    sampling_method=sampling_method,
                    epochs=epochs,
                    **kwargs
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                stats = learner.get_learning_statistics()
                
                results[f"{max_workers}_workers"] = {
                    'max_workers': max_workers,
                    'execution_time': execution_time,
                    'learned_cpds': len(learned_cpds),
                    'success_rate': stats.get('success_rate', 0.0),
                    'avg_group_time': stats.get('avg_group_time', 0.0),
                    'max_group_time': stats.get('max_group_time', 0.0),
                    'total_groups': stats.get('total_groups', 0),
                    'speedup': None  # Will be calculated later
                }
                
                if self.verbose:
                    print(f"   ✅ Completed in {execution_time:.2f}s")
                    print(f"   📊 Learned {len(learned_cpds)} CPDs")
                    print(f"   🎯 Success rate: {stats.get('success_rate', 0.0):.1%}")
                
            except Exception as e:
                if self.verbose:
                    print(f"   ❌ Failed: {str(e)}")
                
                results[f"{max_workers}_workers"] = {
                    'max_workers': max_workers,
                    'execution_time': float('inf'),
                    'error': str(e),
                    'learned_cpds': 0,
                    'success_rate': 0.0
                }
        
        # Calculate speedups relative to single worker
        baseline_time = results.get('1_workers', {}).get('execution_time', float('inf'))
        for key, result in results.items():
            if 'error' not in result and baseline_time != float('inf'):
                speedup = baseline_time / result['execution_time']
                result['speedup'] = speedup
        
        # Store results
        self.results = results
        
        if self.verbose:
            print("\n📊 Benchmark Results Summary:")
            print("-" * 30)
            for key, result in results.items():
                if 'error' not in result:
                    print(f"{result['max_workers']} workers: {result['execution_time']:.2f}s "
                          f"(speedup: {result.get('speedup', 'N/A'):.1f}x)")
                else:
                    print(f"{result['max_workers']} workers: FAILED")
        
        return results


# Example usage and testing functions
def create_test_network() -> Tuple[pd.DataFrame, BayesianNetwork]:
    """Create a test network for demonstrating parallel learning."""
    # Create a complex network: A->B->C, A->D->E, F->G->H, I->J
    bn = BayesianNetwork()
    bn.add_edges_from([
        ('A', 'B'), ('B', 'C'),
        ('A', 'D'), ('D', 'E'),
        ('F', 'G'), ('G', 'H'),
        ('I', 'J')
    ])
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    data = {}
    # Root nodes
    for node in ['A', 'F', 'I']:
        data[node] = np.random.randint(0, 2, n_samples)
    
    # Dependent nodes
    data['B'] = ((data['A'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['C'] = ((data['B'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['D'] = ((data['A'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['E'] = ((data['D'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['G'] = ((data['F'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['H'] = ((data['G'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    data['J'] = ((data['I'] + np.random.randint(0, 2, n_samples)) > 0).astype(int)
    
    df = pd.DataFrame(data)
    
    return df, bn


def demo_parallel_learning():
    """Demonstrate parallel learning capabilities."""
    print("🎯 DeepParameters Parallel Learning Demo")
    print("=" * 50)
    
    # Create test data
    data, bn = create_test_network()
    print(f"📊 Created test network with {len(bn.nodes())} nodes and {len(bn.edges())} edges")
    print(f"📋 Nodes: {list(bn.nodes())}")
    print(f"🔗 Edges: {list(bn.edges())}")
    
    # Run parallel learning
    learned_cpds = learn_network_parameters_parallel(
        data=data,
        true_model=bn,
        learnt_bn_structure=bn,
        max_workers=3,
        network_type="simple",
        sampling_method="1",
        epochs=20,
        verbose=True
    )
    
    print(f"\n✅ Successfully learned {len(learned_cpds)} CPDs")
    print("🎉 Parallel learning demo completed!")
    
    return learned_cpds


def benchmark_parallel_learning():
    """Run a comprehensive benchmark of parallel learning."""
    print("🔬 DeepParameters Parallel Learning Benchmark")
    print("=" * 50)
    
    # Create test data
    data, bn = create_test_network()
    
    # Run benchmark
    benchmark = ParallelLearningBenchmark(verbose=True)
    results = benchmark.benchmark_performance(
        data=data,
        true_model=bn,
        learnt_bn_structure=bn,
        network_type="simple",
        sampling_method="1",
        epochs=30,
        max_workers_list=[1, 2, 3, 4]
    )
    
    return results


if __name__ == "__main__":
    # Run demo
    demo_parallel_learning()
    
    print("\n" + "=" * 50)
    
    # Run benchmark
    benchmark_parallel_learning()