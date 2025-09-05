"""
📋 Deep Ib
===========

🔬 Research Foundation:
======================  
Based on information bottleneck principle:
- Tishby, N., Pereira, F.C. & Bialek, W. (1999). "The Information Bottleneck Method"
- Schwartz-Ziv, R. & Tishby, N. (2017). "Opening the Black Box of Deep Neural Networks"
- Alemi, A.A. et al. (2016). "Deep Variational Information Bottleneck"
🎯 ELI5 Summary:
This file is an important component in our AI research system! Like different organs 
in your body that work together to keep you healthy, this file has a specific job that 
helps the overall algorithm work correctly and efficiently.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

"""
"""
🔥 Deep Information Bottleneck - Neural Compression & Generalization Engine  
===========================================================================

🧠 ELI5 Explanation:
Imagine you're trying to teach someone about elephants by showing them thousands of photos. 
You want to find the "essence" of what makes an elephant - the key features that matter most 
for recognition while ignoring irrelevant details like background, lighting, or camera angle.

The Deep Information Bottleneck is like having a smart compression system that:

1. **Learns what matters**: It automatically discovers which features in your data are truly 
   important for the task (like trunk, ears, size) and which are just noise (like shadows, grass).

2. **Creates perfect summaries**: It compresses complex data into compact representations that 
   keep everything important but throw away everything irrelevant - like creating the perfect 
   "elephant essence" that captures what you need to know.

3. **Prevents overfitting**: By forcing information through a narrow "bottleneck," it can't 
   memorize specific examples, so it learns general patterns that work on new, unseen data.

Think of it as an intelligent data diet - it keeps the nutrients (relevant information) and 
discards the junk (irrelevant details), making your AI models both smaller and smarter!

📚 Research Foundation:  
- Tishby, N. & Zaslavsky, N. (2015) "Deep learning and the information bottleneck principle"
- Alemi, A. et al. (2017) "Deep Variational Information Bottleneck"
- Schwarz-Ziv, R. & Tishby, N. (2017) "Opening the black box of deep neural networks via information"
- Kolchinsky, A. et al. (2019) "Nonlinear Information Bottleneck"

Key mathematical insight: Find representation Z that minimizes I(X,Z) - βI(Z,Y)
This balances compression (small I(X,Z)) with prediction (large I(Z,Y)) optimally.

🏗️ Deep Information Bottleneck Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEEP VARIATIONAL INFORMATION BOTTLENECK              │
├─────────────────────────────────────────────────────────────────────────┤
│  Input X → Encoder → Bottleneck Z → Decoder → Prediction Y              │
│     ↓         ↓           ↓            ↓            ↓                   │
│  [Data]  → [μ(X),σ(X)] → [Z~N(μ,σ)] → [Neural Net] → [Task Output]    │
│                                                                         │
│  INFORMATION FLOW CONTROL:                                              │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ Compression ←→ Prediction Trade-off                           │     │
│  │      ↓               ↑                                        │     │
│  │  I(X,Z) ← β → I(Z,Y)                                         │     │
│  │   (less)     (more)                                          │     │
│  │                                                              │     │
│  │ Loss = -I(Z,Y) + β·I(X,Z)                                   │     │
│  │        ^^^^^^^^   ^^^^^^^^                                   │     │
│  │       Prediction  Compression                               │     │
│  │        Accuracy    Penalty                                  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  VARIATIONAL APPROXIMATION:                                             │
│  • Encoder: q(z|x) ≈ N(μₑ(x), σₑ(x))  [Learned distributions]         │
│  • Decoder: p(y|z) via neural network   [Task-specific head]           │
│  • KL Term: KL(q(z|x)||p(z)) ≈ I(X,Z)  [Compression measure]          │
└─────────────────────────────────────────────────────────────────────────┘

🔧 Usage Examples:
```python
# Learn compressed representations for image classification
import numpy as np
from information_bottleneck.core import DeepInformationBottleneck

# Create deep IB model for MNIST-like data
dib = DeepInformationBottleneck(
    encoder_layers=[784, 512, 256],  # Input → hidden → bottleneck
    decoder_layers=[128, 64, 10],    # Bottleneck → hidden → classes
    latent_dim=64,                   # Bottleneck size (compression)
    beta=0.01,                       # Compression strength
    kl_weight=1.0                    # KL divergence weight
)

# Train on data - learns optimal compression automatically
X_train = np.random.randn(1000, 784)  # Images
y_train = np.random.randint(0, 10, 1000)  # Labels

dib.fit(X_train, y_train, epochs=100)

# Extract compressed representations (the "essence" of your data)
compressed = dib.encode(X_train)
print(f"Original: {X_train.shape} → Compressed: {compressed.shape}")

# The model learned to keep only information relevant for classification!
predictions = dib.predict(X_test)
```

⚙️ Mathematical Foundations:
- **Variational Objective**: L = E_q[log p(y|z)] - β·KL(q(z|x)||p(z))
- **Encoder Distribution**: q(z|x) = N(μₑ(x), σₑ²(x)) learned by neural network
- **Information Terms**: I(X,Z) ≈ KL(q(z|x)||p(z)), I(Z,Y) ≈ E[log p(y|z)]
- **β-VAE Connection**: β controls compression-prediction trade-off optimally
- **Reparameterization**: z = μ + σ⊙ε where ε~N(0,I) enables backpropagation

💰 FUNDING APPEAL - PLEASE DONATE! 💰
=====================================
🌟 This deep information bottleneck research is made possible by Benedict Chen
   📧 Contact: benedict@benedictchen.com
   
💳 PLEASE DONATE! Your support keeps this research alive! 💳
   🔗 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   🔗 GitHub Sponsors: https://github.com/sponsors/benedictchen
   
☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!
(Start small, dream big! Every donation helps advance AI research! 😄)

💡 Why donate? This implementation bridges information theory and deep learning - the foundation 
   of modern AI's ability to generalize! Your support helps unlock the secrets of intelligence! 🤖✨
"""

"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Made possible by Benedict Chen (benedict@benedictchen.com)
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
        
        # Removed print spam: f"...
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
        
        # # Removed print spam: "...
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