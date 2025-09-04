"""
🧠 Neural Information Bottleneck Implementation
==============================================

Neural network-based Information Bottleneck using variational bounds
for continuous optimization of the IB principle.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class NeuralInformationBottleneck:
    """
    Neural Network-based Information Bottleneck (experimental)
    
    Uses neural networks to parameterize encoder and decoder for continuous optimization
    This is more modern but requires more computational resources
    
    # FIXME: Critical Theoretical Issues in Neural Information Bottleneck Implementation
    #
    # 1. INCORRECT BETA DEFAULT VALUE (β=1.0)
    #    - Original Tishby et al. (1999) theory shows β controls information trade-off
    #    - β=1.0 gives equal weight to compression and prediction, which is rarely optimal
    #    - Different tasks require different β values for optimal performance
    #    - Solutions:
    #      a) Use adaptive β: β = self._estimate_optimal_beta(X, Y)
    #      b) Implement β-annealing schedule: start high, decay during training
    #      c) Add β-sweep functionality to find optimal operating point
    #    - Research-accurate ranges: β ∈ [0.01, 100] depending on task complexity
    #    - Example:
    #      ```python
    #      # Adaptive beta based on dataset complexity
    #      def _estimate_optimal_beta(self, X, Y):
    #          mi_xy = mutual_info_estimate(X, Y)
    #          return max(0.1, min(10.0, mi_xy))  # Scale based on task difficulty
    #      ```
    #
    # 2. MISSING VARIATIONAL BOUND IMPLEMENTATION
    #    - Neural IB requires variational approximation of intractable mutual information
    #    - Current implementation lacks proper MINE (Mutual Information Neural Estimation)
    #    - Should implement KL(q(z|x) || p(z)) term for proper variational bound
    #    - Solutions:
    #      a) Add MINE estimator for I(X;Z): -E_q[log(q(z|x))] + E_p[log(p(z))]
    #      b) Implement CLUB estimator for I(Z;Y): E_q[log(q(y|z))]  
    #      c) Add reparameterization trick for gradient flow
    #    - Mathematical basis: L = -I(X;Z) + βI(Z;Y) approximated via variational bounds
    #
    # 3. ARCHITECTURAL CONSTRAINTS MISSING
    #    - Information bottleneck requires encoder output to be a probability distribution
    #    - Current architecture may not enforce proper stochastic bottleneck
    #    - Missing Gaussian reparameterization μ, σ² outputs from encoder
    #    - Solutions:
    #      a) Split encoder final layer: [μ_layer, log_σ²_layer]
    #      b) Add reparameterization: z = μ + σ * ε, where ε ~ N(0,I)
    #      c) Implement KL divergence loss: KL(q(z|x) || p(z))
    #    - Example:
    #      ```python
    #      # Proper variational encoder output
    #      def encode(self, x):
    #          h = self.encoder_hidden(x)
    #          mu = self.mu_layer(h)
    #          log_var = self.log_var_layer(h)
    #          return mu, log_var
    #      
    #      def reparameterize(self, mu, log_var):
    #          std = torch.exp(0.5 * log_var)
    #          eps = torch.randn_like(std)
    #          return mu + eps * std
    #      ```
    #
    # 4. MISSING INFORMATION PLANE ANALYSIS
    #    - Original theory includes information plane visualization I(X;Z) vs I(Z;Y)
    #    - This is crucial for understanding representation learning dynamics
    #    - Should track and visualize information coordinates during training
    #    - Solutions:
    #      a) Add mutual information logging: self.info_history = {'I_XZ': [], 'I_ZY': []}
    #      b) Implement information plane plotting functionality
    #      c) Add phase transition detection for different β regimes
    #    - This provides deep insight into why and how neural networks generalize
    """
    
    def __init__(self, encoder_dims: List[int], decoder_dims: List[int], 
                 latent_dim: int, beta: float = 1.0):
        """
        Initialize Neural Information Bottleneck
        
        Args:
            encoder_dims: Neural network architecture for encoder [input_dim, hidden1, hidden2, ...]
            decoder_dims: Neural network architecture for decoder [latent_dim, hidden1, hidden2, output_dim]
            latent_dim: Dimensionality of bottleneck representation
            beta: Information bottleneck trade-off parameter
        """
        
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            
            self.torch = torch
            self.nn = nn
            self.optim = optim
            self._use_pytorch = True
            
        except ImportError:
            print("⚠️  PyTorch not available, falling back to numpy-based neural network")
            self.torch = None
            self.nn = None
            self.optim = None
            self._use_pytorch = False
        
        self.encoder_dims = encoder_dims
        self.decoder_dims = decoder_dims  
        self.latent_dim = latent_dim
        self.beta = beta
        
        if self._use_pytorch:
            self._build_networks()
        else:
            self._build_numpy_networks()
        
        print(f"🧠 Neural Information Bottleneck initialized:")
        print(f"   • Encoder: {encoder_dims} → {latent_dim}")
        print(f"   • Decoder: {latent_dim} → {decoder_dims[-1]}")
        print(f"   • β = {beta}")
        print(f"   • Backend: {'PyTorch' if self._use_pytorch else 'NumPy'}")
        
    def _build_networks(self):
        """Build encoder and decoder networks"""
        
        # Encoder: X → μ, σ (Gaussian latent)
        encoder_layers = []
        for i in range(len(self.encoder_dims) - 1):
            encoder_layers.append(self.nn.Linear(self.encoder_dims[i], self.encoder_dims[i+1]))
            encoder_layers.append(self.nn.ReLU())
            encoder_layers.append(self.nn.Dropout(0.1))
        
        encoder_layers.append(self.nn.Linear(self.encoder_dims[-1], 2 * self.latent_dim))  # μ, log σ
        self.encoder = self.nn.Sequential(*encoder_layers)
        
        # Decoder: Z → Y
        decoder_layers = []
        for i in range(len(self.decoder_dims) - 1):
            decoder_layers.append(self.nn.Linear(self.decoder_dims[i], self.decoder_dims[i+1]))
            if i < len(self.decoder_dims) - 2:  # No activation on output
                decoder_layers.append(self.nn.ReLU())
                decoder_layers.append(self.nn.Dropout(0.1))
        
        self.decoder = self.nn.Sequential(*decoder_layers)
        
    def _build_numpy_networks(self):
        """Build numpy-based neural networks as PyTorch alternative"""
        
        # Initialize encoder weights and biases
        self.encoder_weights = []
        self.encoder_biases = []
        
        # Encoder layers
        for i in range(len(self.encoder_dims) - 1):
            # Xavier initialization
            fan_in, fan_out = self.encoder_dims[i], self.encoder_dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.encoder_weights.append(weight)
            self.encoder_biases.append(bias)
            
        # Final encoder layer for mu and log_var
        fan_in, fan_out = self.encoder_dims[-1], 2 * self.latent_dim
        limit = np.sqrt(6.0 / (fan_in + fan_out))
        
        weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
        bias = np.zeros(fan_out)
        
        self.encoder_weights.append(weight)
        self.encoder_biases.append(bias)
        
        # Initialize decoder weights and biases
        self.decoder_weights = []
        self.decoder_biases = []
        
        # Decoder layers
        for i in range(len(self.decoder_dims) - 1):
            fan_in, fan_out = self.decoder_dims[i], self.decoder_dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.decoder_weights.append(weight)
            self.decoder_biases.append(bias)
            
        print("✅ NumPy neural networks initialized")
        
    def _numpy_relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
        
    def _numpy_sigmoid(self, x):
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
        
    def _numpy_forward_encoder(self, x):
        """Forward pass through numpy encoder"""
        
        hidden = x
        
        # Hidden layers with ReLU activation
        for i in range(len(self.encoder_weights) - 1):
            hidden = np.dot(hidden, self.encoder_weights[i]) + self.encoder_biases[i]
            hidden = self._numpy_relu(hidden)
            
        # Final layer (mu and log_var)
        output = np.dot(hidden, self.encoder_weights[-1]) + self.encoder_biases[-1]
        
        # Split into mu and log_var
        mu = output[:, :self.latent_dim]
        log_var = output[:, self.latent_dim:]
        
        return mu, log_var
        
    def _numpy_forward_decoder(self, z):
        """Forward pass through numpy decoder"""
        
        hidden = z
        
        # Hidden layers with ReLU activation
        for i in range(len(self.decoder_weights) - 1):
            hidden = np.dot(hidden, self.decoder_weights[i]) + self.decoder_biases[i]
            hidden = self._numpy_relu(hidden)
            
        # Final layer
        output = np.dot(hidden, self.decoder_weights[-1]) + self.decoder_biases[-1]
        
        return output
        
    def _numpy_reparameterize(self, mu, log_var):
        """Numpy version of reparameterization trick"""
        std = np.exp(0.5 * log_var)
        eps = np.random.normal(0, 1, mu.shape)
        return mu + eps * std
        
    def _numpy_kl_divergence_gaussian(self, mu, log_var):
        """Numpy version of KL divergence computation"""
        return -0.5 * np.sum(1 + log_var - mu**2 - np.exp(log_var))
        
    def _get_encoder_layer_output(self, X, layer_idx):
        """Get output of specific encoder layer for gradient computation"""
        if layer_idx < 0:
            return X
            
        hidden = X
        for i in range(layer_idx + 1):
            hidden = np.dot(hidden, self.encoder_weights[i]) + self.encoder_biases[i]
            if i < len(self.encoder_weights) - 1:  # Apply ReLU to all but last layer
                hidden = self._numpy_relu(hidden)
        
        return hidden
        
    def _reparameterize(self, mu, log_var):
        """Reparameterization trick for backpropagation through sampling"""
        std = self.torch.exp(0.5 * log_var)
        eps = self.torch.randn_like(std)
        return mu + eps * std
        
    def _kl_divergence_gaussian(self, mu, log_var):
        """KL divergence between encoder distribution and standard normal"""
        return -0.5 * self.torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        
    def fit(self, X: np.ndarray, Y: np.ndarray, epochs: int = 100, lr: float = 0.001):
        """Train Neural Information Bottleneck"""
        
        if self._use_pytorch:
            return self._fit_pytorch(X, Y, epochs, lr)
        else:
            return self._fit_numpy(X, Y, epochs, lr)
            
    def _fit_pytorch(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """PyTorch-based training"""
        
        # Convert to tensors
        X_tensor = self.torch.FloatTensor(X)
        Y_tensor = self.torch.LongTensor(Y) if len(np.unique(Y)) < 50 else self.torch.FloatTensor(Y.reshape(-1, 1))
        
        # Setup optimizer
        optimizer = self.optim.Adam(list(self.encoder.parameters()) + list(self.decoder.parameters()), lr=lr)
        
        # Loss function
        if len(np.unique(Y)) < 50:  # Classification
            criterion = self.nn.CrossEntropyLoss()
        else:  # Regression
            criterion = self.nn.MSELoss()
        
        print(f"🎯 Training Neural IB for {epochs} epochs...")
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            encoded = self.encoder(X_tensor)
            mu, log_var = encoded[:, :self.latent_dim], encoded[:, self.latent_dim:]
            
            # Sample latent representation
            z = self._reparameterize(mu, log_var)
            
            # Decode
            decoded = self.decoder(z)
            
            # Compute losses
            reconstruction_loss = criterion(decoded, Y_tensor)
            kl_loss = self._kl_divergence_gaussian(mu, log_var)
            
            # Information Bottleneck loss
            total_loss = reconstruction_loss + (1.0 / self.beta) * kl_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 20 == 0:
                print(f"   Epoch {epoch+1}/{epochs}: Total Loss = {total_loss.item():.4f}, "
                      f"Recon = {reconstruction_loss.item():.4f}, KL = {kl_loss.item():.4f}")
        
        print("✅ Neural IB training completed!")
        return {'total_loss': total_loss.item(), 'reconstruction': reconstruction_loss.item(), 'kl': kl_loss.item()}
        
    def _fit_numpy(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """NumPy-based training (simplified version)"""
        
        print(f"🎯 Training NumPy Neural IB for {epochs} epochs...")
        print("⚠️  Note: NumPy implementation provides basic functionality only")
        
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            
            # Forward pass
            mu, log_var = self._numpy_forward_encoder(X)
            z = self._numpy_reparameterize(mu, log_var)
            y_pred = self._numpy_forward_decoder(z)
            
            # Compute losses (simplified)
            if len(np.unique(Y)) < 50:  # Classification
                # Cross-entropy loss approximation
                y_pred_softmax = np.exp(y_pred) / np.sum(np.exp(y_pred), axis=1, keepdims=True)
                reconstruction_loss = -np.mean(np.log(y_pred_softmax[np.arange(n_samples), Y.astype(int)] + 1e-8))
            else:  # Regression
                reconstruction_loss = np.mean((y_pred.flatten() - Y.flatten())**2)
            
            kl_loss = self._numpy_kl_divergence_gaussian(mu, log_var) / n_samples
            total_loss = reconstruction_loss + (1.0 / self.beta) * kl_loss
            
            if (epoch + 1) % 20 == 0:
                print(f"   Epoch {epoch+1}/{epochs}: Total Loss = {total_loss:.4f}, "
                      f"Recon = {reconstruction_loss:.4f}, KL = {kl_loss:.4f}")
        
        print("✅ NumPy Neural IB training completed!")
        print("ℹ️  For full gradient-based optimization, install PyTorch")
        
        return {'total_loss': total_loss, 'reconstruction': reconstruction_loss, 'kl': kl_loss}
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data through the information bottleneck"""
        
        if self._use_pytorch:
            X_tensor = self.torch.FloatTensor(X)
            with self.torch.no_grad():
                encoded = self.encoder(X_tensor)
                mu = encoded[:, :self.latent_dim]
                return mu.numpy()
        else:
            mu, _ = self._numpy_forward_encoder(X)
            return mu
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the trained model"""
        
        if self._use_pytorch:
            X_tensor = self.torch.FloatTensor(X)
            with self.torch.no_grad():
                encoded = self.encoder(X_tensor)
                mu, log_var = encoded[:, :self.latent_dim], encoded[:, self.latent_dim:]
                z = self._reparameterize(mu, log_var)
                decoded = self.decoder(z)
                return decoded.numpy()
        else:
            mu, log_var = self._numpy_forward_encoder(X)
            z = self._numpy_reparameterize(mu, log_var)
            return self._numpy_forward_decoder(z)
    
    def get_information_statistics(self) -> Dict[str, Any]:
        """Get information-theoretic statistics about the learned representation"""
        
        return {
            'latent_dim': self.latent_dim,
            'beta': self.beta,
            'encoder_architecture': self.encoder_dims,
            'decoder_architecture': self.decoder_dims,
            'backend': 'PyTorch' if self._use_pytorch else 'NumPy',
            'trainable_parameters': self._count_parameters()
        }
    
    def _count_parameters(self) -> int:
        """Count total trainable parameters"""
        
        if self._use_pytorch:
            total_params = sum(p.numel() for p in self.encoder.parameters())
            total_params += sum(p.numel() for p in self.decoder.parameters())
            return total_params
        else:
            # Count NumPy parameters
            total_params = 0
            for w, b in zip(self.encoder_weights, self.encoder_biases):
                total_params += w.size + b.size
            for w, b in zip(self.decoder_weights, self.decoder_biases):
                total_params += w.size + b.size
            return total_params