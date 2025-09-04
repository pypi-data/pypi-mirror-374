"""
🔥 Deep Information Bottleneck Implementation
===========================================

Deep learning implementation of Information Bottleneck using
variational approximations and neural networks.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Alemi et al. (2017) "Deep Variational Information Bottleneck"
"""

import numpy as np
from typing import Dict, Optional, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class DeepInformationBottleneck:
    """
    Deep Variational Information Bottleneck implementation
    
    Uses deep neural networks with variational bounds to implement
    the Information Bottleneck principle for high-dimensional data.
    
    Based on Alemi et al. (2017) "Deep Variational Information Bottleneck"
    """
    
    def __init__(
        self,
        encoder_layers: List[int],
        decoder_layers: List[int],
        latent_dim: int,
        beta: float = 1.0,
        kl_weight: float = 1.0
    ):
        """
        Initialize Deep Information Bottleneck
        
        Args:
            encoder_layers: Architecture for encoder network
            decoder_layers: Architecture for decoder network  
            latent_dim: Dimensionality of latent bottleneck
            beta: IB trade-off parameter
            kl_weight: Weight for KL divergence term
        """
        
        self.encoder_layers = encoder_layers
        self.decoder_layers = decoder_layers
        self.latent_dim = latent_dim
        self.beta = beta
        self.kl_weight = kl_weight
        
        # Check for PyTorch availability
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            import torch.nn.functional as F
            
            self.torch = torch
            self.nn = nn
            self.optim = optim
            self.F = F
            self._use_pytorch = True
            
            # Build networks
            self._build_networks()
            
        except ImportError:
            print("⚠️  PyTorch not available. Deep IB requires PyTorch.")
            print("   Install PyTorch: pip install torch torchvision")
            self._use_pytorch = False
        
        print(f"🔥 Deep Information Bottleneck initialized:")
        print(f"   • Encoder: {encoder_layers} → {latent_dim}")
        print(f"   • Decoder: {latent_dim} → {decoder_layers[-1]}")
        print(f"   • β = {beta}, KL weight = {kl_weight}")
        
    def _build_networks(self):
        """Build encoder and decoder networks"""
        
        # Encoder network
        encoder_modules = []
        for i in range(len(self.encoder_layers) - 1):
            encoder_modules.append(
                self.nn.Linear(self.encoder_layers[i], self.encoder_layers[i+1])
            )
            encoder_modules.append(self.nn.ReLU())
            encoder_modules.append(self.nn.BatchNorm1d(self.encoder_layers[i+1]))
            encoder_modules.append(self.nn.Dropout(0.2))
        
        # Final encoder layers for mu and log_var
        encoder_modules.append(self.nn.Linear(self.encoder_layers[-1], 2 * self.latent_dim))
        self.encoder = self.nn.Sequential(*encoder_modules)
        
        # Decoder network
        decoder_modules = []
        for i in range(len(self.decoder_layers) - 1):
            decoder_modules.append(
                self.nn.Linear(self.decoder_layers[i], self.decoder_layers[i+1])
            )
            if i < len(self.decoder_layers) - 2:  # No activation on final layer
                decoder_modules.append(self.nn.ReLU())
                decoder_modules.append(self.nn.BatchNorm1d(self.decoder_layers[i+1]))
                decoder_modules.append(self.nn.Dropout(0.2))
        
        self.decoder = self.nn.Sequential(*decoder_modules)
        
        # Move to GPU if available
        if self.torch.cuda.is_available():
            self.encoder.cuda()
            self.decoder.cuda()
            self.device = 'cuda'
        else:
            self.device = 'cpu'
    
    def encode(self, x):
        """Encode input to latent parameters"""
        if not self._use_pytorch:
            raise RuntimeError("PyTorch required for Deep IB")
        
        output = self.encoder(x)
        mu = output[:, :self.latent_dim]
        log_var = output[:, self.latent_dim:]
        
        return mu, log_var
    
    def reparameterize(self, mu, log_var):
        """Reparameterization trick for variational inference"""
        std = self.torch.exp(0.5 * log_var)
        eps = self.torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z):
        """Decode latent representation to output"""
        return self.decoder(z)
    
    def forward(self, x):
        """Full forward pass through Deep IB"""
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        recon = self.decode(z)
        return recon, mu, log_var, z
    
    def compute_loss(self, x, y, recon, mu, log_var, task_type='classification'):
        """Compute Deep IB loss function"""
        
        batch_size = x.size(0)
        
        # Reconstruction loss
        if task_type == 'classification':
            recon_loss = self.F.cross_entropy(recon, y, reduction='sum')
        else:
            recon_loss = self.F.mse_loss(recon, y, reduction='sum')
        
        # KL divergence loss (regularization term)
        kl_loss = -0.5 * self.torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        
        # Information Bottleneck loss
        total_loss = recon_loss + self.kl_weight * kl_loss / self.beta
        
        return {
            'total_loss': total_loss,
            'reconstruction_loss': recon_loss,
            'kl_loss': kl_loss,
            'avg_total_loss': total_loss / batch_size,
            'avg_recon_loss': recon_loss / batch_size,
            'avg_kl_loss': kl_loss / batch_size
        }
    
    def fit(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        lr: float = 0.001,
        task_type: str = 'classification',
        validation_split: float = 0.2,
        verbose: bool = True
    ) -> Dict[str, List[float]]:
        """
        Train Deep Information Bottleneck
        
        Args:
            X: Input data
            Y: Target data
            epochs: Number of training epochs
            batch_size: Batch size for training
            lr: Learning rate
            task_type: 'classification' or 'regression'
            validation_split: Fraction of data for validation
            verbose: Print training progress
            
        Returns:
            Training history dictionary
        """
        
        if not self._use_pytorch:
            raise RuntimeError("PyTorch required for Deep IB")
        
        # Convert data to PyTorch tensors
        X_tensor = self.torch.FloatTensor(X).to(self.device)
        
        if task_type == 'classification':
            Y_tensor = self.torch.LongTensor(Y).to(self.device)
        else:
            Y_tensor = self.torch.FloatTensor(Y).to(self.device)
        
        # Split into train/validation
        n_samples = X_tensor.size(0)
        n_val = int(validation_split * n_samples)
        n_train = n_samples - n_val
        
        indices = self.torch.randperm(n_samples)
        train_indices = indices[:n_train]
        val_indices = indices[n_train:]
        
        X_train, Y_train = X_tensor[train_indices], Y_tensor[train_indices]
        X_val, Y_val = X_tensor[val_indices], Y_tensor[val_indices]
        
        # Setup optimizer
        optimizer = self.optim.Adam(
            list(self.encoder.parameters()) + list(self.decoder.parameters()),
            lr=lr
        )
        
        # Training history
        history = {
            'train_loss': [],
            'train_recon': [],
            'train_kl': [],
            'val_loss': [],
            'val_recon': [],
            'val_kl': []
        }
        
        print(f"🎯 Training Deep IB for {epochs} epochs...")
        print(f"   • Train: {n_train} samples, Val: {n_val} samples")
        print(f"   • Batch size: {batch_size}, Learning rate: {lr}")
        
        for epoch in range(epochs):
            
            # Training phase
            self.encoder.train()
            self.decoder.train()
            
            train_losses = {'total': [], 'recon': [], 'kl': []}
            
            # Mini-batch training
            for i in range(0, n_train, batch_size):
                end_idx = min(i + batch_size, n_train)
                batch_X = X_train[i:end_idx]
                batch_Y = Y_train[i:end_idx]
                
                optimizer.zero_grad()
                
                # Forward pass
                recon, mu, log_var, z = self.forward(batch_X)
                
                # Compute loss
                loss_dict = self.compute_loss(batch_X, batch_Y, recon, mu, log_var, task_type)
                
                # Backward pass
                loss_dict['total_loss'].backward()
                optimizer.step()
                
                # Store losses
                train_losses['total'].append(loss_dict['avg_total_loss'].item())
                train_losses['recon'].append(loss_dict['avg_recon_loss'].item())
                train_losses['kl'].append(loss_dict['avg_kl_loss'].item())
            
            # Validation phase
            self.encoder.eval()
            self.decoder.eval()
            
            with self.torch.no_grad():
                val_recon, val_mu, val_log_var, val_z = self.forward(X_val)
                val_loss_dict = self.compute_loss(X_val, Y_val, val_recon, val_mu, val_log_var, task_type)
            
            # Store epoch results
            history['train_loss'].append(np.mean(train_losses['total']))
            history['train_recon'].append(np.mean(train_losses['recon']))
            history['train_kl'].append(np.mean(train_losses['kl']))
            
            history['val_loss'].append(val_loss_dict['avg_total_loss'].item())
            history['val_recon'].append(val_loss_dict['avg_recon_loss'].item())
            history['val_kl'].append(val_loss_dict['avg_kl_loss'].item())
            
            # Print progress
            if verbose and (epoch + 1) % 10 == 0:
                print(f"   Epoch {epoch+1:3d}/{epochs}: "
                      f"Loss={history['train_loss'][-1]:.4f}, "
                      f"Val={history['val_loss'][-1]:.4f}, "
                      f"KL={history['train_kl'][-1]:.4f}")
        
        print("✅ Deep IB training completed!")
        return history
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data to latent representation"""
        if not self._use_pytorch:
            raise RuntimeError("PyTorch required for Deep IB")
        
        self.encoder.eval()
        
        with self.torch.no_grad():
            X_tensor = self.torch.FloatTensor(X).to(self.device)
            mu, log_var = self.encode(X_tensor)
            
            # Return mean of latent distribution
            return mu.cpu().numpy()
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using trained Deep IB"""
        if not self._use_pytorch:
            raise RuntimeError("PyTorch required for Deep IB")
        
        self.encoder.eval()
        self.decoder.eval()
        
        with self.torch.no_grad():
            X_tensor = self.torch.FloatTensor(X).to(self.device)
            recon, mu, log_var, z = self.forward(X_tensor)
            
            return recon.cpu().numpy()
    
    def get_information_statistics(self) -> Dict[str, Any]:
        """Get information-theoretic statistics"""
        
        total_params = sum(p.numel() for p in self.encoder.parameters())
        total_params += sum(p.numel() for p in self.decoder.parameters())
        
        return {
            'latent_dim': self.latent_dim,
            'beta': self.beta,
            'kl_weight': self.kl_weight,
            'encoder_layers': self.encoder_layers,
            'decoder_layers': self.decoder_layers,
            'total_parameters': total_params,
            'device': self.device if self._use_pytorch else 'cpu'
        }