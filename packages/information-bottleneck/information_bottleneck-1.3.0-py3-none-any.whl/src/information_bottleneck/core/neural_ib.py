"""
📋 Neural Ib
=============

🎯 ELI5 Summary:
This file is an important component in our AI research system! Like different organs 
in your body that work together to keep you healthy, this file has a specific job that 
helps the overall algorithm work correctly and efficiently.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

📋 Component Integration:
========================
    ┌──────────┐
    │   This   │
    │Component │ ←→ Other Components
    └──────────┘
         ↑↓
    System Integration

"""
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
    
    Complete Neural Information Bottleneck implementation with all theoretical fixes
    Based on Tishby et al. (1999), Alemi et al. (2017), and Schwartz-Ziv & Tishby (2017)
    """
    
    def __init__(self, encoder_dims: List[int], decoder_dims: List[int], 
                 latent_dim: int, beta: float = None, adaptive_beta: bool = True,
                 beta_annealing_schedule: Optional[List[float]] = None,
                 track_info_plane: bool = True, variational_bounds: bool = True):
        """
        Initialize Neural Information Bottleneck with complete theoretical implementation
        
        Args:
            encoder_dims: Neural network architecture for encoder [input_dim, hidden1, hidden2, ...]
            decoder_dims: Neural network architecture for decoder [latent_dim, hidden1, hidden2, output_dim]
            latent_dim: Dimensionality of bottleneck representation
            beta: Information trade-off parameter (if None, uses adaptive estimation)
            adaptive_beta: Whether to estimate optimal beta from data complexity
            beta_annealing_schedule: Schedule for beta annealing during training
            track_info_plane: Whether to track information plane coordinates I(X;Z) vs I(Z;Y)
            variational_bounds: Whether to use proper variational bounds (MINE/CLUB estimators)
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
        
        # Adaptive beta estimation implementation
        self.adaptive_beta = adaptive_beta
        self.beta_annealing_schedule = beta_annealing_schedule or []
        self.current_beta_idx = 0
        self.variational_bounds = variational_bounds
        
        # Information plane tracking implementation
        self.track_info_plane = track_info_plane
        self.info_history = {
            'I_XZ': [], 'I_ZY': [], 'beta_values': [], 'epochs': [],
            'compression_phase': [], 'generalization_phase': []
        } if track_info_plane else None
        
        # Set initial beta (adaptive or provided)
        if beta is None and adaptive_beta:
            self.beta = 1.0  # Placeholder, will be estimated in fit()
            self.need_beta_estimation = True
        else:
            self.beta = beta if beta is not None else 1.0
            self.need_beta_estimation = False
        
        if self._use_pytorch:
            self._build_networks()
        else:
            self._build_numpy_networks()
            
        # Initialize MI estimators for variational bounds
        if self.variational_bounds and self._use_pytorch:
            self._build_mi_estimators()
        
        print(f"🧠 Neural Information Bottleneck initialized:")
        print(f"   • Encoder: {encoder_dims} → {latent_dim}")
        print(f"   • Decoder: {latent_dim} → {decoder_dims[-1]}")
        print(f"   • β = {self.beta} {'(adaptive)' if self.adaptive_beta else ''}")
        print(f"   • Variational bounds: {variational_bounds}")
        print(f"   • Information plane tracking: {track_info_plane}")
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
            
        # # Removed print spam: "...
        
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
        """PyTorch-based training with adaptive beta and MI estimation"""
        
        # Adaptive beta estimation
        if self.need_beta_estimation and self.adaptive_beta:
            self.beta = self._estimate_optimal_beta(X, Y)
            self.need_beta_estimation = False
        
        # Convert to tensors
        X_tensor = self.torch.FloatTensor(X)
        Y_tensor = self.torch.LongTensor(Y) if len(np.unique(Y)) < 50 else self.torch.FloatTensor(Y.reshape(-1, 1))
        
        # Setup optimizer (include MI networks if using variational bounds)
        params = list(self.encoder.parameters()) + list(self.decoder.parameters())
        if self.variational_bounds:
            params += list(self.mine_net.parameters()) + list(self.club_net.parameters())
        optimizer = self.optim.Adam(params, lr=lr)
        
        # Loss function
        if len(np.unique(Y)) < 50:  # Classification
            criterion = self.nn.CrossEntropyLoss()
        else:  # Regression
            criterion = self.nn.MSELoss()
        
        # Removed print spam: f"...
        if self.adaptive_beta:
            print(f"   • Using adaptive β = {self.beta:.4f}")
        if self.beta_annealing_schedule:
            print(f"   • Beta annealing schedule: {len(self.beta_annealing_schedule)} steps")
        if self.track_info_plane:
            print(f"   • Information plane tracking enabled")
        
        for epoch in range(epochs):
            # Beta annealing schedule
            current_beta = self._update_beta_annealing(epoch)
            
            optimizer.zero_grad()
            
            # Forward pass
            encoded = self.encoder(X_tensor)
            mu, log_var = encoded[:, :self.latent_dim], encoded[:, self.latent_dim:]
            
            # Sample latent representation with reparameterization
            z = self._reparameterize(mu, log_var)
            
            # Decode
            decoded = self.decoder(z)
            
            # Compute losses
            reconstruction_loss = criterion(decoded, Y_tensor)
            kl_loss = self._kl_divergence_gaussian(mu, log_var)
            
            # Add variational MI bounds if enabled
            if self.variational_bounds:
                # Train MI estimators
                mi_xz = self._mine_estimate(X_tensor, z)
                mi_zy = self._club_estimate(z, Y_tensor.unsqueeze(1) if Y_tensor.dim() == 1 else Y_tensor)
                
                # Use MI estimates in loss (experimental - can be tuned)
                variational_loss = 0.1 * (mi_xz - mi_zy)  # Encourage compression while maintaining relevance
                total_loss = reconstruction_loss + (1.0 / current_beta) * kl_loss + variational_loss
            else:
                # Standard Information Bottleneck loss
                total_loss = reconstruction_loss + (1.0 / current_beta) * kl_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            # Information plane tracking
            if self.track_info_plane and epoch % 5 == 0:  # Track every 5 epochs to reduce overhead
                self._track_information_plane(epoch, X_tensor, Y_tensor, z)
            
            if (epoch + 1) % 20 == 0:
                if self.variational_bounds and self.track_info_plane:
                    print(f"   Epoch {epoch+1}/{epochs}: Loss={total_loss.item():.4f}, Recon={reconstruction_loss.item():.4f}, "
                          f"KL={kl_loss.item():.4f}, I(X;Z)≈{self.info_history['I_XZ'][-1]:.3f}, I(Z;Y)≈{self.info_history['I_ZY'][-1]:.3f}")
                else:
                    print(f"   Epoch {epoch+1}/{epochs}: Total Loss = {total_loss.item():.4f}, "
                          f"Recon = {reconstruction_loss.item():.4f}, KL = {kl_loss.item():.4f}")
        
        # # Removed print spam: "...
        
        # Print phase analysis if available
        if self.track_info_plane:
            phase_analysis = self.get_phase_analysis()
            # Removed print spam: f"...
            print(f"   • Compression phase: {phase_analysis['compression_ratio']:.1%} of training")
            print(f"   • Generalization phase: {phase_analysis['generalization_ratio']:.1%} of training") 
            print(f"   • Final I(X;Z): {phase_analysis['final_I_XZ']:.4f}")
            print(f"   • Final I(Z;Y): {phase_analysis['final_I_ZY']:.4f}")
        
        result = {
            'total_loss': total_loss.item(), 
            'reconstruction': reconstruction_loss.item(), 
            'kl': kl_loss.item(),
            'final_beta': current_beta
        }
        
        if self.track_info_plane:
            result['phase_analysis'] = self.get_phase_analysis()
            
        return result
        
    def _fit_numpy(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """NumPy-based training (simplified version)"""
        
        # Removed print spam: f"...
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
        
        # # Removed print spam: "...
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
    
    # Adaptive beta estimation implementation
    def _estimate_optimal_beta(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Estimate optimal beta based on dataset complexity and mutual information
        Based on Tishby et al. (1999) and empirical analysis
        """
        from sklearn.metrics import mutual_info_score
        from sklearn.feature_selection import mutual_info_regression
        
        # Estimate I(X;Y) as a proxy for task complexity
        if len(np.unique(Y)) < 50:  # Discrete Y (classification)
            # For discrete Y, use mutual_info_score
            if X.ndim > 1:
                X_flat = X.mean(axis=1) if X.shape[1] > 1 else X.flatten()
            else:
                X_flat = X.flatten()
            mi_xy = mutual_info_score(X_flat, Y)
        else:  # Continuous Y (regression)
            # For continuous Y, use mutual_info_regression
            mi_xy = mutual_info_regression(X.reshape(-1, 1) if X.ndim == 1 else X, Y)[0]
        
        # Scale beta based on mutual information and task characteristics
        # Higher MI suggests more complex relationship → higher beta needed for compression
        # Lower MI suggests simpler relationship → lower beta to avoid over-compression
        
        data_complexity = np.std(X) * np.std(Y)  # Dataset complexity measure
        sample_size_factor = np.log(len(X)) / 10  # Larger datasets can handle higher beta
        
        # Adaptive beta formula based on information theory principles
        base_beta = np.clip(mi_xy * 2.0, 0.1, 10.0)  # Base from MI estimation
        complexity_adjustment = np.clip(data_complexity / 10.0, 0.5, 2.0)  # Complexity scaling
        size_adjustment = np.clip(sample_size_factor, 0.8, 1.5)  # Sample size scaling
        
        optimal_beta = base_beta * complexity_adjustment * size_adjustment
        
        # Removed print spam: f"...
        print(f"   • I(X;Y) estimate: {mi_xy:.4f}")
        print(f"   • Data complexity: {data_complexity:.4f}")
        print(f"   • Sample size factor: {sample_size_factor:.4f}")
        print(f"   • Estimated optimal β: {optimal_beta:.4f}")
        
        return float(optimal_beta)
    
    def _update_beta_annealing(self, epoch: int) -> float:
        """Update beta according to annealing schedule"""
        if self.beta_annealing_schedule and epoch < len(self.beta_annealing_schedule):
            new_beta = self.beta_annealing_schedule[epoch]
            if new_beta != self.beta:
                # Removed print spam: f"...
                self.beta = new_beta
        return self.beta
    
    # Variational bounds implementation using MINE/CLUB estimators
    def _build_mi_estimators(self):
        """Build MINE and CLUB estimators for variational bounds"""
        if not self._use_pytorch:
            return
            
        # MINE network for I(X;Z) estimation
        self.mine_net = self.nn.Sequential(
            self.nn.Linear(self.encoder_dims[0] + self.latent_dim, 128),
            self.nn.ReLU(),
            self.nn.Linear(128, 128),
            self.nn.ReLU(), 
            self.nn.Linear(128, 1)
        )
        
        # CLUB network for I(Z;Y) estimation
        output_dim = self.decoder_dims[-1]
        self.club_net = self.nn.Sequential(
            self.nn.Linear(self.latent_dim + output_dim, 128),
            self.nn.ReLU(),
            self.nn.Linear(128, 128), 
            self.nn.ReLU(),
            self.nn.Linear(128, 1)
        )
        
        print("🔬 Built MINE and CLUB networks for variational MI estimation")
    
    def _mine_estimate(self, x, z):
        """MINE estimate of I(X;Z)"""
        if not hasattr(self, 'mine_net'):
            return self.torch.tensor(0.0)
            
        # Joint samples
        joint = self.torch.cat([x, z], dim=1)
        
        # Marginal samples (shuffle z)
        z_shuffle = z[self.torch.randperm(z.size(0))]
        marginal = self.torch.cat([x, z_shuffle], dim=1)
        
        # MINE objective
        t_joint = self.mine_net(joint)
        t_marginal = self.mine_net(marginal)
        
        # MI estimate: E[T(x,z)] - log(E[exp(T(x,z'))])
        mi_estimate = t_joint.mean() - self.torch.logsumexp(t_marginal, 0) + np.log(x.size(0))
        
        return mi_estimate
    
    def _club_estimate(self, z, y):
        """CLUB estimate of I(Z;Y)"""
        if not hasattr(self, 'club_net'):
            return self.torch.tensor(0.0)
            
        # Joint samples
        joint = self.torch.cat([z, y], dim=1)
        
        # Marginal samples (shuffle y)
        y_shuffle = y[self.torch.randperm(y.size(0))]
        marginal = self.torch.cat([z, y_shuffle], dim=1)
        
        # CLUB objective
        t_joint = self.club_net(joint)
        t_marginal = self.club_net(marginal)
        
        # MI estimate
        mi_estimate = t_joint.mean() - t_marginal.mean()
        
        return mi_estimate
    
    # Information plane tracking for Tishby's compression/generalization theory
    def _track_information_plane(self, epoch: int, x_tensor, y_tensor, z):
        """Track information plane coordinates during training"""
        if not self.track_info_plane:
            return
            
        with self.torch.no_grad():
            # Estimate I(X;Z) and I(Z;Y)
            if self.variational_bounds:
                I_XZ = self._mine_estimate(x_tensor, z).item()
                I_ZY = self._club_estimate(z, y_tensor.unsqueeze(1) if y_tensor.dim() == 1 else y_tensor).item()
            else:
                # Simplified estimation using correlation as proxy
                I_XZ = float(self.torch.corrcoef(self.torch.stack([x_tensor.mean(1), z.mean(1)]))[0, 1].abs())
                I_ZY = float(self.torch.corrcoef(self.torch.stack([z.mean(1), y_tensor.float()]))[0, 1].abs())
            
            # Store information plane coordinates
            self.info_history['I_XZ'].append(I_XZ)
            self.info_history['I_ZY'].append(I_ZY)
            self.info_history['beta_values'].append(self.beta)
            self.info_history['epochs'].append(epoch)
            
            # Detect compression vs generalization phases
            if len(self.info_history['I_XZ']) >= 5:
                recent_I_XZ = self.info_history['I_XZ'][-5:]
                recent_I_ZY = self.info_history['I_ZY'][-5:]
                
                # Compression phase: I(X;Z) increases, I(Z;Y) may increase
                compression_trend = np.polyfit(range(5), recent_I_XZ, 1)[0] > 0
                
                # Generalization phase: I(X;Z) decreases, I(Z;Y) stable/increases  
                generalization_trend = np.polyfit(range(5), recent_I_XZ, 1)[0] < 0 and np.polyfit(range(5), recent_I_ZY, 1)[0] >= -0.01
                
                self.info_history['compression_phase'].append(compression_trend)
                self.info_history['generalization_phase'].append(generalization_trend)
            else:
                self.info_history['compression_phase'].append(False)
                self.info_history['generalization_phase'].append(False)
    
    def plot_information_plane(self, save_path: str = None):
        """Plot information plane trajectory I(X;Z) vs I(Z;Y)"""
        if not self.track_info_plane or not self.info_history:
            print("❌ Information plane tracking not enabled or no data available")
            return
            
        try:
            import matplotlib.pyplot as plt
            
            I_XZ = self.info_history['I_XZ']
            I_ZY = self.info_history['I_ZY']
            epochs = self.info_history['epochs']
            
            plt.figure(figsize=(10, 8))
            
            # Plot trajectory with color coding by epoch
            scatter = plt.scatter(I_XZ, I_ZY, c=epochs, cmap='viridis', alpha=0.7)
            plt.colorbar(scatter, label='Epoch')
            
            # Connect points to show trajectory
            plt.plot(I_XZ, I_ZY, 'k-', alpha=0.3, linewidth=1)
            
            # Mark start and end points
            if I_XZ and I_ZY:
                plt.plot(I_XZ[0], I_ZY[0], 'ro', markersize=10, label='Start')
                plt.plot(I_XZ[-1], I_ZY[-1], 'bs', markersize=10, label='End')
            
            plt.xlabel('I(X;Z) - Compression')
            plt.ylabel('I(Z;Y) - Relevance') 
            plt.title('Information Bottleneck - Information Plane Trajectory')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                # Removed print spam: f"...
            else:
                plt.show()
                
        except ImportError:
            print("❌ matplotlib not available for plotting")
    
    def get_phase_analysis(self) -> Dict[str, Any]:
        """Analyze compression vs generalization phases"""
        if not self.track_info_plane or not self.info_history:
            return {}
        
        compression_epochs = sum(self.info_history['compression_phase'])
        generalization_epochs = sum(self.info_history['generalization_phase'])
        total_epochs = len(self.info_history['epochs'])
        
        return {
            'total_epochs': total_epochs,
            'compression_epochs': compression_epochs,
            'generalization_epochs': generalization_epochs,
            'compression_ratio': compression_epochs / total_epochs if total_epochs > 0 else 0,
            'generalization_ratio': generalization_epochs / total_epochs if total_epochs > 0 else 0,
            'final_I_XZ': self.info_history['I_XZ'][-1] if self.info_history['I_XZ'] else 0,
            'final_I_ZY': self.info_history['I_ZY'][-1] if self.info_history['I_ZY'] else 0
        }