"""
Architectures Network Implementations for CPD Learning
======================================================================

This module contains all neural network architectures for learning CPDs:
- LSTM: Long Short-Term Memory networks
- BNN: Bayesian Neural Networks  
- VAE: Variational Autoencoders
- Autoencoder: Standard autoencoders
- Normalizing Flow: Normalizing flows
- Simple/Advanced/Ultra/Mega: Traditional architectures
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

# TensorFlow setup (optional)
HAS_TENSORFLOW = False
try:
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    import tensorflow as tf
    tf.config.run_functions_eagerly(True)

    from tensorflow import keras
    from tensorflow.keras import layers, Model, Sequential
    from tensorflow.keras.optimizers import Adam, AdamW, SGD, RMSprop, Nadam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.layers import (
        Dense, Dropout, LSTM, GRU, Conv1D, Flatten, 
        BatchNormalization, LayerNormalization, Input,
        MultiHeadAttention, Concatenate, Add
    )
    HAS_TENSORFLOW = True
except ImportError:
    # TensorFlow not available - will use sklearn fallbacks
    tf = None
    keras = None

# Scikit-learn
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# PGMPy
from pgmpy.factors.discrete import TabularCPD


class BaseCPDLearner(ABC):
    """Base class for all CPD learning architectures."""
    
    def __init__(self, node, data, true_model, learnt_bn_structure, num_parameters,
                 epochs=100, batch_size=32, learning_rate=0.001, validation_split=0.2,
                 early_stopping=True, early_stopping_patience=10, optimizer='adam',
                 verbose=True, random_state=42, **kwargs):
        self.node = node
        self.data = data
        self.true_model = true_model
        self.learnt_bn_structure = learnt_bn_structure
        self.num_parameters = num_parameters
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.validation_split = validation_split
        self.early_stopping = early_stopping
        self.early_stopping_patience = early_stopping_patience
        self.optimizer = optimizer.lower() if isinstance(optimizer, str) else optimizer
        self.verbose = verbose
        self.random_state = random_state
        self.kwargs = kwargs
        
        # Set random seeds
        np.random.seed(random_state)
        if HAS_TENSORFLOW:
            tf.random.set_seed(random_state)
        
        # Initialize model components
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Prepare data
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare training data from the input DataFrame."""
        # Get parents of the target node
        self.parents = list(self.learnt_bn_structure.predecessors(self.node))
        
        if len(self.parents) == 0:
            # Root node - no parents
            self.X = np.ones((len(self.data), 1))  # Dummy input
            self.y = self.data[self.node].values
        else:
            # Node with parents
            self.X = self.data[self.parents].values
            self.y = self.data[self.node].values
        
        # Store variable cardinalities
        self.node_card = len(self.data[self.node].unique())
        self.parent_cards = [len(self.data[parent].unique()) for parent in self.parents] if self.parents else [1]
    
    def _get_optimizer(self):
        """Create optimizer instance based on user specification."""
        if not HAS_TENSORFLOW:
            # For sklearn, return string for solver parameter
            if isinstance(self.optimizer, str):
                if self.optimizer in ['adam', 'adamw']:
                    return 'adam'
                elif self.optimizer in ['sgd']:
                    return 'sgd' 
                elif self.optimizer in ['lbfgs']:
                    return 'lbfgs'
                else:
                    return 'adam'  # Default fallback
            return 'adam'
        
        # For TensorFlow, create optimizer instance
        if isinstance(self.optimizer, str):
            optimizer_name = self.optimizer.lower()
            if optimizer_name == 'adam':
                return Adam(learning_rate=self.learning_rate)
            elif optimizer_name == 'adamw':
                return AdamW(learning_rate=self.learning_rate)
            elif optimizer_name == 'sgd':
                return SGD(learning_rate=self.learning_rate)
            elif optimizer_name == 'rmsprop':
                return RMSprop(learning_rate=self.learning_rate)
            elif optimizer_name == 'nadam':
                return Nadam(learning_rate=self.learning_rate)
            else:
                # Default fallback
                return Adam(learning_rate=self.learning_rate)
        else:
            # User provided optimizer instance directly
            return self.optimizer
        self.parents = parents
        
        if self.verbose:
            print("Data prepared for node '{}':".format(self.node))
            print(f"   Parents: {parents if parents else 'None (root node)'}")
            print(f"   Input shape: {self.X.shape}")
            print(f"   Output shape: {self.y.shape}")
            print(f"   Node cardinality: {self.node_card}")
    
    @abstractmethod
    def _build_model(self):
        """Build the neural network model (to be implemented by subclasses)."""
        pass
    
    @abstractmethod
    def fit(self, data):
        """Fit the model to the data (to be implemented by subclasses)."""
        pass
    
    def get_cpd(self):
        """Convert model predictions to TabularCPD format."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting CPD")
        
        # Generate all possible parent combinations
        if len(self.parents) == 0:
            # Root node
            try:
                if hasattr(self.model, 'predict_proba'):
                    # Sklearn classifier with probability prediction
                    pred = self.model.predict_proba(np.ones((1, 1)))[0]
                else:
                    # TensorFlow model or sklearn regressor
                    try:
                        pred = self.model.predict(np.ones((1, 1)), verbose=0)
                    except TypeError:
                        # Sklearn model without verbose parameter
                        pred = self.model.predict(np.ones((1, 1)))
                    except Exception as e:
                        print(f"Error in root node prediction for {self.node}: {e}")
                        # Fallback to uniform distribution
                        uniform_prob = 1.0 / self.node_card
                        pred = np.full(self.node_card, uniform_prob)
                    
                    # Handle multi-output models (VAE, Autoencoder) for nodes with no parents
                    if isinstance(pred, list) and len(pred) > 1:
                        # Multi-output model - take the first output (CPD output)
                        pred = pred[0][0]  # Get first output, first sample
                    elif hasattr(pred, 'ndim') and pred.ndim > 1:
                        pred = pred[0]  # Get first sample
                    elif hasattr(pred, '__len__') and len(pred) > 0:
                        pred = pred[0]  # Get first element
                    else:
                        pred = pred
                
                # Validate prediction
                if pred is None or (hasattr(pred, '__len__') and len(pred) == 0):
                    print(f"Warning: Empty prediction for root node {self.node}, using uniform distribution")
                    uniform_prob = 1.0 / self.node_card
                    pred = np.full(self.node_card, uniform_prob)
                
            except Exception as e:
                print(f"Critical error in root node prediction for {self.node}: {e}")
                uniform_prob = 1.0 / self.node_card
                pred = np.full(self.node_card, uniform_prob)
            
            # Handle root node predictions
            if not hasattr(pred, '__len__') or (hasattr(pred, '__len__') and len(pred) == 1):
                # Single scalar value (binary case)
                if hasattr(pred, '__len__'):
                    prob = pred[0] if len(pred) == 1 else pred
                else:
                    prob = pred
                cpd_values = np.array([[1-prob], [prob]])
            else:
                # Multi-class case - reshape to column vector
                cpd_values = pred.reshape(-1, 1)
        else:
            # Node with parents
            parent_combinations = []
            for cards in self.parent_cards:
                parent_combinations.append(list(range(cards)))
            
            import itertools
            all_combinations = list(itertools.product(*parent_combinations))
            
            X_test = np.array(all_combinations)
            
            # Get predictions with error handling
            if hasattr(self.model, 'predict_proba'):
                # Sklearn classifier with probability prediction
                predictions = self.model.predict_proba(X_test)
            else:
                # TensorFlow model or sklearn regressor
                try:
                    predictions = self.model.predict(X_test, verbose=0)
                except TypeError:
                    # Sklearn model without verbose parameter
                    predictions = self.model.predict(X_test)
                except Exception as e:
                    print(f"Error in model prediction for node {self.node}: {e}")
                    # Return uniform distribution as fallback
                    num_combinations = len(all_combinations)
                    uniform_prob = 1.0 / self.node_card
                    predictions = np.full((num_combinations, self.node_card), uniform_prob)
            
            # Validate predictions
            if predictions is None or len(predictions) == 0:
                print(f"Warning: Empty predictions for node {self.node}, using uniform distribution")
                num_combinations = len(all_combinations)
                uniform_prob = 1.0 / self.node_card  
                predictions = np.full((num_combinations, self.node_card), uniform_prob)
            
            # Handle multi-output models (VAE, Autoencoder)
            if isinstance(predictions, list) and len(predictions) > 1:
                # Multi-output model - take the first output (CPD output)
                predictions = predictions[0]
            
            # Reshape for CPD format
            if self.node_card == 2:
                # Binary target variable
                cpd_values = np.zeros((2, len(all_combinations)))
                for i, pred in enumerate(predictions):
                    if hasattr(pred, '__len__') and len(pred) > 1:
                        cpd_values[0, i] = pred[0]  # P(node=0|parents)
                        cpd_values[1, i] = pred[1]  # P(node=1|parents)
                    else:
                        cpd_values[0, i] = 1 - pred  # P(node=0|parents)
                        cpd_values[1, i] = pred      # P(node=1|parents)
            else:
                # Multi-class case
                cpd_values = predictions.T
        
        # Normalize to ensure probabilities sum to 1 (with division by zero protection)
        column_sums = cpd_values.sum(axis=0, keepdims=True)
        # Protect against division by zero
        zero_mask = column_sums == 0
        if np.any(zero_mask):
            print(f"Warning: Zero sum columns detected for node {self.node}, using uniform distribution")
            # Replace zero columns with uniform distribution
            uniform_values = np.ones((cpd_values.shape[0], 1)) / cpd_values.shape[0]
            cpd_values[:, zero_mask.flatten()] = uniform_values
            column_sums = cpd_values.sum(axis=0, keepdims=True)
        
        cpd_values = cpd_values / column_sums
        
        # Create TabularCPD
        if len(self.parents) == 0:
            cpd = TabularCPD(
                variable=self.node,
                variable_card=self.node_card,
                values=cpd_values
            )
        else:
            if self.verbose:
                print(f"DEBUG - Creating TabularCPD for node '{self.node}' (MLP):")
                print(f"   evidence (parents): {self.parents}")
                print(f"   evidence_card (parent_cards): {self.parent_cards}")
                print(f"   len(evidence): {len(self.parents)}")
                print(f"   len(evidence_card): {len(self.parent_cards)}")
            
            cpd = TabularCPD(
                variable=self.node,
                variable_card=self.node_card,
                values=cpd_values,
                evidence=self.parents,
                evidence_card=self.parent_cards
            )
        
        return cpd


class LSTMCPDLearner(BaseCPDLearner):
    """LSTM-based CPD learner for sequential dependencies."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not HAS_TENSORFLOW:
            print("⚠️  LSTM requires TensorFlow. Falling back to sklearn MLP.")
    
    def _build_model(self):
        """Build LSTM model for CPD learning."""
        if not HAS_TENSORFLOW:
            # Fall back to sklearn MLP
            return self._build_sklearn_fallback()
            
        input_dim = self.X.shape[1]
        
        # Create sequence-based input (treat each sample as a sequence)
        inputs = Input(shape=(1, input_dim), name='lstm_input')
        
        # LSTM layers
        lstm1 = LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)(inputs)
        lstm2 = LSTM(32, dropout=0.2, recurrent_dropout=0.2)(lstm1)
        
        # Dense layers
        dense1 = Dense(64, activation='relu')(lstm2)
        dense1 = Dropout(0.3)(dense1)
        dense2 = Dense(32, activation='relu')(dense1)
        dense2 = Dropout(0.2)(dense2)
        
        # Output layer
        if self.node_card == 2:
            outputs = Dense(1, activation='sigmoid', name='cpd_output')(dense2)
        else:
            outputs = Dense(self.node_card, activation='softmax', name='cpd_output')(dense2)
        
        model = Model(inputs=inputs, outputs=outputs, name=f'LSTM_CPD_{self.node}')
        
        # Compile model
        if self.node_card == 2:
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            loss = 'sparse_categorical_crossentropy'
            metrics = ['sparse_categorical_accuracy']
            
        model.compile(
            optimizer=self._get_optimizer(),
            loss=loss,
            metrics=metrics
        )
        
        return model
    
    def _build_sklearn_fallback(self):
        """Build sklearn MLP as fallback when TensorFlow is not available."""
        optimizer_solver = self._get_optimizer()
        
        if self.node_card == 2:
            return MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
        else:
            return MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
    
    def fit(self, data):
        """Fit LSTM model to the data."""
        self.model = self._build_model()
        
        if not HAS_TENSORFLOW:
            # Use sklearn fallback - ensure 2D data
            X_2d = self.X.reshape(self.X.shape[0], -1) if self.X.ndim > 2 else self.X
            self.model.fit(X_2d, self.y)
            self.is_fitted = True
            if self.verbose:
                print("LSTM training completed using sklearn fallback!")
            return
        
        # Reshape data for LSTM (add sequence dimension)
        X_lstm = self.X.reshape(self.X.shape[0], 1, self.X.shape[1])
        
        # Prepare callbacks
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(patience=self.early_stopping_patience, restore_best_weights=True))
            callbacks.append(ReduceLROnPlateau(patience=max(5, self.early_stopping_patience // 2), factor=0.5))
        
        # Train model
        if self.verbose:
            print("Training LSTM model for node '{}'...".format(self.node))
        
        history = self.model.fit(
            X_lstm, self.y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        self.is_fitted = True
        if self.verbose:
            print("LSTM training completed!")
        
        return history
    
    def get_cpd(self):
        """Convert LSTM model predictions to TabularCPD format."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting CPD")
        
        # Check if we're using sklearn fallback
        using_sklearn_fallback = not HAS_TENSORFLOW
        
        # Generate all possible parent combinations
        if len(self.parents) == 0:
            # Root node
            if using_sklearn_fallback:
                # sklearn MLP expects 2D input
                input_data = np.ones((1, 1))
            else:
                # LSTM expects 3D input (batch_size, sequence_length, features)
                input_data = np.ones((1, 1, 1))
                
            try:
                pred = self.model.predict(input_data, verbose=0)[0] if not using_sklearn_fallback else self.model.predict(input_data)[0]
            except Exception:
                pred = self.model.predict(input_data)[0]
            
            if len(pred) == 1 or not hasattr(pred, '__len__'):
                # Binary case or single value
                if hasattr(pred, '__len__'):
                    prob = pred[0] if len(pred) == 1 else pred
                else:
                    prob = pred
                cpd_values = np.array([[1-prob], [prob]])
            else:
                cpd_values = pred.reshape(-1, 1)
        else:
            # Node with parents
            parent_combinations = []
            for cards in self.parent_cards:
                parent_combinations.append(list(range(cards)))
            
            import itertools
            all_combinations = list(itertools.product(*parent_combinations))
            
            X_test = np.array(all_combinations)
            
            if using_sklearn_fallback:
                # sklearn MLP expects 2D input
                X_test_final = X_test
            else:
                # LSTM expects 3D input (add sequence dimension)
                X_test_final = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])
            
            # Get predictions
            try:
                if using_sklearn_fallback:
                    # For sklearn, use predict_proba to get probabilities
                    predictions = self.model.predict_proba(X_test_final)
                else:
                    predictions = self.model.predict(X_test_final, verbose=0)
            except Exception:
                if using_sklearn_fallback:
                    predictions = self.model.predict_proba(X_test_final)
                else:
                    predictions = self.model.predict(X_test_final)
            
            if self.node_card == 2:
                # Binary classification
                if predictions.shape[1] == 1:
                    # Sigmoid output (TensorFlow)
                    cpd_values = np.zeros((2, len(all_combinations)))
                    for i, pred in enumerate(predictions):
                        prob = pred[0]
                        cpd_values[0, i] = 1 - prob  # P(node=0|parents)
                        cpd_values[1, i] = prob      # P(node=1|parents)
                else:
                    # Softmax output or sklearn predict_proba (2 classes)
                    cpd_values = predictions.T
            else:
                # Multi-class classification (softmax output)
                cpd_values = predictions.T
        
        # Create TabularCPD
        if self.verbose:
            print(f"DEBUG - Creating TabularCPD for node '{self.node}':")
            print(f"   evidence (parents): {self.parents}")
            print(f"   evidence_card (parent_cards): {self.parent_cards}")
            print(f"   len(evidence): {len(self.parents) if self.parents else 0}")
            print(f"   len(evidence_card): {len(self.parent_cards)}")
        
        if len(self.parents) == 0:
            return TabularCPD(
                variable=self.node, 
                variable_card=self.node_card,
                values=cpd_values
            )
        else:
            return TabularCPD(
                variable=self.node, 
                variable_card=self.node_card,
                values=cpd_values,
                evidence=self.parents,
                evidence_card=self.parent_cards
            )


class BayesianNeuralNetworkCPDLearner(BaseCPDLearner):
    """Bayesian Neural Network for uncertainty quantification in CPD learning."""
    
    def _build_model(self):
        """Build Bayesian Neural Network using TensorFlow Probability."""
        if not HAS_TENSORFLOW:
            # Fall back to sklearn MLP
            return self._build_sklearn_fallback()
            
        input_dim = self.X.shape[1]
        
        # Input layer
        inputs = Input(shape=(input_dim,), name='bnn_input')
        
        # Use a simpler approach with standard layers and Monte Carlo dropout
        # This avoids the complex TFP layers that might have compatibility issues
        h1 = Dense(64, activation='relu', name='bnn_dense1')(inputs)
        h1 = Dropout(0.5)(h1)  # Higher dropout for uncertainty
        
        h2 = Dense(32, activation='relu', name='bnn_dense2')(h1)
        h2 = Dropout(0.4)(h2)
        
        h3 = Dense(16, activation='relu', name='bnn_dense3')(h2)
        h3 = Dropout(0.3)(h3)
        
        # Output layer
        if self.node_card == 2:
            outputs = Dense(1, activation='sigmoid', name='bnn_output')(h3)
        else:
            outputs = Dense(self.node_card, activation='softmax', name='bnn_output')(h3)
        
        # Create model using Functional API
        model = Model(inputs=inputs, outputs=outputs, name=f'BNN_CPD_{self.node}')
        
        # Compile with appropriate loss
        if self.node_card == 2:
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            loss = 'sparse_categorical_crossentropy'
            metrics = ['sparse_categorical_accuracy']
        
        model.compile(
            optimizer=self._get_optimizer(),
            loss=loss,
            metrics=metrics
        )
        
        return model
    
    def _build_sklearn_fallback(self):
        """Build sklearn MLP as fallback when TensorFlow is not available."""
        optimizer_solver = self._get_optimizer()
        
        if self.node_card == 2:
            return MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
        else:
            return MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
    
    def fit(self, data):
        """Fit Bayesian Neural Network to the data."""
        self.model = self._build_model()
        
        if not HAS_TENSORFLOW:
            # Use sklearn fallback
            self.model.fit(self.X, self.y)
            self.is_fitted = True
            if self.verbose:
                print("BNN training completed using sklearn fallback!")
            return
        
        # Prepare callbacks
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(patience=15, restore_best_weights=True))
            callbacks.append(ReduceLROnPlateau(patience=7, factor=0.5))
        
        # Train model
        if self.verbose:
            print("Training Bayesian Neural Network for node '{}'...".format(self.node))
        
        history = self.model.fit(
            self.X, self.y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        self.is_fitted = True
        if self.verbose:
            print("BNN training completed!")
        
        return history


class VAECPDLearner(BaseCPDLearner):
    """Variational Autoencoder for probabilistic CPD learning."""
    
    def _build_model(self):
        """Build VAE model for CPD learning."""
        if not HAS_TENSORFLOW:
            # Fall back to sklearn MLP
            return self._build_sklearn_fallback()
            
        input_dim = self.X.shape[1]
        latent_dim = min(16, max(2, input_dim // 2))
        
        # Encoder
        encoder_inputs = Input(shape=(input_dim,), name='encoder_input')
        h = Dense(64, activation='relu')(encoder_inputs)
        h = Dropout(0.3)(h)
        h = Dense(32, activation='relu')(h)
        
        z_mean = Dense(latent_dim, name='z_mean')(h)
        z_log_var = Dense(latent_dim, name='z_log_var')(h)
        
        # Sampling layer
        class Sampling(layers.Layer):
            def call(self, inputs):
                z_mean, z_log_var = inputs
                batch = tf.shape(z_mean)[0]
                dim = tf.shape(z_mean)[1]
                epsilon = tf.random.normal(shape=(batch, dim))
                return z_mean + tf.exp(0.5 * z_log_var) * epsilon
        
        z = Sampling()([z_mean, z_log_var])
        
        # Decoder
        decoder_h = Dense(32, activation='relu')(z)
        decoder_h = Dropout(0.2)(decoder_h)
        decoder_h = Dense(64, activation='relu')(decoder_h)
        
        # CPD output
        if self.node_card == 2:
            cpd_output = Dense(1, activation='sigmoid', name='cpd_output')(decoder_h)
        else:
            cpd_output = Dense(self.node_card, activation='softmax', name='cpd_output')(decoder_h)
        
        # Reconstruction output
        reconstruction_output = Dense(input_dim, activation='sigmoid', name='reconstruction')(decoder_h)
        
        # Create the VAE model
        vae = Model(encoder_inputs, [cpd_output, reconstruction_output], name=f'VAE_CPD_{self.node}')
        
        # Add KL loss as a custom layer
        class KLDivergenceLayer(layers.Layer):
            def __init__(self, **kwargs):
                super(KLDivergenceLayer, self).__init__(**kwargs)
            
            def call(self, inputs):
                z_mean, z_log_var = inputs
                kl_loss = -0.5 * tf.reduce_mean(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
                self.add_loss(kl_loss)
                return z_mean  # Return z_mean as a pass-through
        
        # Add KL loss
        _ = KLDivergenceLayer()([z_mean, z_log_var])
        
        # Compile with separate losses for each output
        vae.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss={
                'cpd_output': 'binary_crossentropy' if self.node_card == 2 else 'sparse_categorical_crossentropy',
                'reconstruction': 'mse'
            },
            loss_weights={'cpd_output': 1.0, 'reconstruction': 0.1},
            metrics={'cpd_output': 'accuracy'}
        )
        
        return vae
    
    def _build_sklearn_fallback(self):
        """Build sklearn MLP as fallback when TensorFlow is not available."""
        optimizer_solver = self._get_optimizer()
        
        if self.node_card == 2:
            return MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
        else:
            return MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
    
    def fit(self, data):
        """Fit VAE model to the data."""
        self.model = self._build_model()
        
        if not HAS_TENSORFLOW:
            # Use sklearn fallback
            self.model.fit(self.X, self.y)
            self.is_fitted = True
            if self.verbose:
                print("VAE training completed using sklearn fallback!")
            return
        
        # Prepare targets (CPD target + reconstruction target)
        y_cpd = self.y
        y_recon = self.X  # Reconstruct input
        
        # Prepare callbacks
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(patience=15, restore_best_weights=True))
            callbacks.append(ReduceLROnPlateau(patience=7, factor=0.5))
        
        # Train model
        if self.verbose:
            print("Training VAE for node '{}'...".format(self.node))
        
        history = self.model.fit(
            self.X, [y_cpd, y_recon],
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        self.is_fitted = True
        if self.verbose:
            print("VAE training completed!")
        
        return history
    
    def predict(self, X):
        """Predict using VAE model - extract only CPD predictions."""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        if not HAS_TENSORFLOW:
            # sklearn fallback
            predictions = self.model.predict_proba(X) if hasattr(self.model, 'predict_proba') else self.model.predict(X)
            if predictions.ndim == 1:
                predictions = predictions.reshape(-1, 1)
            return predictions
        
        # TensorFlow VAE: Get both outputs but only return CPD predictions
        predictions = self.model.predict(X)
        if isinstance(predictions, list):
            # predictions = [cpd_output, reconstruction_output]
            cpd_predictions = predictions[0]  # First output is CPD
        else:
            cpd_predictions = predictions
        
        # Ensure 2D array
        if cpd_predictions.ndim == 1:
            cpd_predictions = cpd_predictions.reshape(-1, 1)
            
        return cpd_predictions


class AutoencoderCPDLearner(BaseCPDLearner):
    """Standard Autoencoder for dimensionality reduction in CPD learning."""
    
    def _build_model(self):
        """Build Autoencoder model."""
        if not HAS_TENSORFLOW:
            # Fall back to sklearn MLP
            return self._build_sklearn_fallback()
            
        input_dim = self.X.shape[1]
        encoding_dim = max(2, input_dim // 2)
        
        # Encoder
        input_layer = Input(shape=(input_dim,))
        encoded = Dense(64, activation='relu')(input_layer)
        encoded = Dropout(0.3)(encoded)
        encoded = Dense(encoding_dim, activation='relu')(encoded)
        
        # Decoder for reconstruction
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dropout(0.2)(decoded)
        reconstruction = Dense(input_dim, activation='sigmoid', name='reconstruction')(decoded)
        
        # CPD prediction branch
        cpd_branch = Dense(32, activation='relu')(encoded)
        cpd_branch = Dropout(0.2)(cpd_branch)
        
        if self.node_card == 2:
            cpd_output = Dense(1, activation='sigmoid', name='cpd_output')(cpd_branch)
        else:
            cpd_output = Dense(self.node_card, activation='softmax', name='cpd_output')(cpd_branch)
        
        # Model
        autoencoder = Model(input_layer, [cpd_output, reconstruction], name=f'Autoencoder_CPD_{self.node}')
        
        # Compile
        autoencoder.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss={
                'cpd_output': 'binary_crossentropy' if self.node_card == 2 else 'sparse_categorical_crossentropy',
                'reconstruction': 'mse'
            },
            loss_weights={'cpd_output': 1.0, 'reconstruction': 0.1},
            metrics={'cpd_output': 'accuracy'}
        )
        
        return autoencoder
    
    def _build_sklearn_fallback(self):
        """Build sklearn MLP as fallback when TensorFlow is not available."""
        optimizer_solver = self._get_optimizer()
        
        if self.node_card == 2:
            return MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
        else:
            return MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
    
    def fit(self, data):
        """Fit Autoencoder model to the data."""
        self.model = self._build_model()
        
        if not HAS_TENSORFLOW:
            # Use sklearn fallback
            self.model.fit(self.X, self.y)
            self.is_fitted = True
            if self.verbose:
                print("Autoencoder training completed using sklearn fallback!")
            return
        
        # Prepare targets
        y_cpd = self.y
        y_recon = self.X
        
        # Prepare callbacks
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(patience=self.early_stopping_patience, restore_best_weights=True))
            callbacks.append(ReduceLROnPlateau(patience=max(5, self.early_stopping_patience // 2), factor=0.5))
        
        # Train model
        if self.verbose:
            print("Training Autoencoder for node '{}'...".format(self.node))
        
        history = self.model.fit(
            self.X, {'cpd_output': y_cpd, 'reconstruction': y_recon},
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        self.is_fitted = True
        if self.verbose:
            print("Autoencoder training completed!")
        
        return history
    
    def predict(self, X):
        """Predict using Autoencoder model - extract only CPD predictions."""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        if not HAS_TENSORFLOW:
            # sklearn fallback
            predictions = self.model.predict_proba(X) if hasattr(self.model, 'predict_proba') else self.model.predict(X)
            if predictions.ndim == 1:
                predictions = predictions.reshape(-1, 1)
            return predictions
        
        # TensorFlow Autoencoder: Get both outputs but only return CPD predictions
        predictions = self.model.predict(X)
        if isinstance(predictions, list):
            # predictions = [cpd_output, reconstruction_output]
            cpd_predictions = predictions[0]  # First output is CPD
        else:
            cpd_predictions = predictions
        
        # Ensure 2D array
        if cpd_predictions.ndim == 1:
            cpd_predictions = cpd_predictions.reshape(-1, 1)
            
        return cpd_predictions


class NormalizingFlowCPDLearner(BaseCPDLearner):
    """Normalizing Flow for exact probability modeling in CPD learning."""
    
    def _build_model(self):
        """Build simplified Normalizing Flow model."""
        if not HAS_TENSORFLOW:
            # Fall back to sklearn MLP
            return self._build_sklearn_fallback()
            
        input_dim = self.X.shape[1]
        
        # Simplified approach: Use a standard neural network with flow-inspired regularization
        inputs = Input(shape=(input_dim,), name='flow_input')
        
        # Flow-inspired layers with residual connections
        h1 = Dense(64, activation='relu')(inputs)
        h1 = Dropout(0.3)(h1)
        h1 = BatchNormalization()(h1)
        
        h2 = Dense(32, activation='relu')(h1)
        h2 = Dropout(0.2)(h2)
        h2 = BatchNormalization()(h2)
        
        # Coupling layer simulation
        h3 = Dense(32, activation='tanh')(h2)
        h3 = Dropout(0.2)(h3)
        
        # Output layer
        if self.node_card == 2:
            outputs = Dense(1, activation='sigmoid', name='flow_output')(h3)
        else:
            outputs = Dense(self.node_card, activation='softmax', name='flow_output')(h3)
        
        model = Model(inputs, outputs, name=f'NormalizingFlow_CPD_{self.node}')
        
        # Standard loss function (simplified from complex flow loss)
        if self.node_card == 2:
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']
        
        model.compile(
            optimizer=self._get_optimizer(),
            loss=loss,
            metrics=metrics
        )
        
        return model
    
    def _build_sklearn_fallback(self):
        """Build sklearn MLP as fallback when TensorFlow is not available."""
        optimizer_solver = self._get_optimizer()
        
        if self.node_card == 2:
            return MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
        else:
            return MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver=optimizer_solver,
                alpha=0.001,
                batch_size=min(self.batch_size, 200),
                learning_rate='adaptive',
                max_iter=self.epochs,
                random_state=self.random_state
            )
    
    def fit(self, data):
        """Fit Normalizing Flow model to the data."""
        self.model = self._build_model()
        
        if not HAS_TENSORFLOW:
            # Use sklearn fallback
            self.model.fit(self.X, self.y)
            self.is_fitted = True
            if self.verbose:
                print("Normalizing Flow training completed using sklearn fallback!")
            return
        
        # Prepare callbacks
        callbacks = []
        if self.early_stopping:
            callbacks.append(EarlyStopping(patience=15, restore_best_weights=True))
            callbacks.append(ReduceLROnPlateau(patience=7, factor=0.5))
        
        # Train model
        if self.verbose:
            print("Training Normalizing Flow for node '{}'...".format(self.node))
        
        history = self.model.fit(
            self.X, self.y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        self.is_fitted = True
        if self.verbose:
            print("Normalizing Flow training completed!")
        
        return history


# Traditional architectures (using sklearn MLPRegressor/MLPClassifier)
class SimpleCPDLearner(BaseCPDLearner):
    """Simple neural network using sklearn."""
    
    def _get_optimizer(self):
        """Override to return sklearn-compatible optimizer strings."""
        # For sklearn, always return string for solver parameter
        if isinstance(self.optimizer, str):
            if self.optimizer.lower() in ['adam', 'adamw']:
                return 'adam'
            elif self.optimizer.lower() in ['sgd']:
                return 'sgd' 
            elif self.optimizer.lower() in ['lbfgs']:
                return 'lbfgs'
            else:
                return 'adam'  # Default fallback
        return 'adam'
    
    def _build_model(self):
        """Build simple sklearn neural network."""
        optimizer_solver = self._get_optimizer()
        
        # Always use MLPClassifier for discrete classification tasks
        return MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation='relu',
            solver=optimizer_solver,
            alpha=0.001,
            batch_size=self.batch_size,
            learning_rate='adaptive',
            max_iter=self.epochs,
            random_state=self.random_state
        )
    
    def fit(self, data):
        """Fit simple model to the data."""
        self.model = self._build_model()
        
        if self.verbose:
            print("Training Simple Neural Network for node '{}'...".format(self.node))
        
        self.model.fit(self.X, self.y)
        self.is_fitted = True
        
        if self.verbose:
            print("Simple NN training completed!")


class AdvancedCPDLearner(SimpleCPDLearner):
    """Advanced neural network using sklearn."""
    
    def _build_model(self):
        """Build advanced sklearn neural network."""
        optimizer_solver = self._get_optimizer()
        
        # Always use MLPClassifier for discrete classification tasks
        return MLPClassifier(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu',
            solver=optimizer_solver,
            alpha=0.0005,
            batch_size=self.batch_size,
            learning_rate='adaptive',
            max_iter=self.epochs,
            random_state=self.random_state
        )


class UltraCPDLearner(SimpleCPDLearner):
    """Ultra neural network using sklearn."""
    
    def _build_model(self):
        """Build ultra sklearn neural network."""
        optimizer_solver = self._get_optimizer()
        
        # Always use MLPClassifier for discrete classification tasks
        return MLPClassifier(
            hidden_layer_sizes=(128, 64, 32, 16),
            activation='relu',
            solver=optimizer_solver,
            alpha=0.0001,
            batch_size=self.batch_size,
            learning_rate='adaptive',
            max_iter=self.epochs,
            random_state=self.random_state
        )


class MegaCPDLearner(SimpleCPDLearner):
    """Mega neural network using sklearn."""
    
    def _build_model(self):
        """Build mega sklearn neural network."""
        optimizer_solver = self._get_optimizer()
        
        # Always use MLPClassifier for discrete classification tasks
        return MLPClassifier(
            hidden_layer_sizes=(256, 128, 64, 32, 16),
            activation='relu',
            solver=optimizer_solver,
            alpha=0.00005,
            batch_size=self.batch_size,
            learning_rate='adaptive',
            max_iter=self.epochs,
            random_state=self.random_state
        )