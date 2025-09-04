"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Visualization - UNIFIED IMPLEMENTATION
===========================================================

This module consolidates all visualization functions for the Information
Bottleneck method from the scattered structure into a single, unified location.

Consolidated from:
- ib_visualization.py (22KB - main visualization class)
- Various plotting functions scattered across modules

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d import Axes3D
import warnings
from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path

# Try to import optional dependencies
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ============================================================================
# PUBLICATION-QUALITY PLOTTING SETUP
# ============================================================================

def setup_publication_style(style: str = 'seaborn', dpi: int = 300,
                           font_size: int = 12, figure_format: str = 'png'):
    """
    Setup matplotlib for publication-quality figures.
    
    Parameters
    ----------
    style : str
        Matplotlib style ('seaborn', 'ggplot', 'classic')
    dpi : int
        Figure resolution
    font_size : int
        Base font size
    figure_format : str
        Default figure format for saving
    """
    # Set style
    plt.style.use('default')  # Reset first
    
    # Configure for publication quality
    plt.rcParams.update({
        'font.size': font_size,
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Computer Modern Roman'],
        'text.usetex': False,  # Set to True if LaTeX is available
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        'savefig.format': figure_format,
        'savefig.bbox': 'tight',
        'axes.linewidth': 1.2,
        'axes.labelsize': font_size,
        'axes.titlesize': font_size + 2,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 1,
        'figure.titlesize': font_size + 4,
        'lines.linewidth': 2.0,
        'lines.markersize': 6
    })
    
    # Set color palette
    if style == 'seaborn':
        sns.set_palette("husl", 8)
    elif style == 'colorbrewer':
        sns.set_palette("Set2", 8)


# ============================================================================
# CORE VISUALIZATION CLASS
# ============================================================================

class IBVisualization:
    """
    Comprehensive visualization suite for Information Bottleneck analysis.
    
    Provides publication-quality visualizations including:
    - Information bottleneck curves (compression vs. relevance)
    - Information plane plots (I(X;T) vs I(T;Y))
    - Training dynamics and convergence plots
    - Representation analysis and clustering visualization
    - Beta parameter sensitivity analysis
    """
    
    def __init__(self, style: str = 'publication', figsize: Tuple[int, int] = (10, 8)):
        """
        Initialize visualization suite.
        
        Parameters
        ----------
        style : str
            Plotting style ('publication', 'seaborn', 'default')
        figsize : Tuple[int, int]
            Default figure size
        """
        self.style = style
        self.default_figsize = figsize
        
        # Setup plotting style
        if style == 'publication':
            setup_publication_style('seaborn', dpi=300, font_size=12)
        elif style == 'seaborn':
            sns.set_style("whitegrid")
            sns.set_palette("husl", 8)
        
        # Color schemes
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'dark': '#343a40'
        }
    
    def plot_information_bottleneck_curve(self, 
                                        results: List[Dict], 
                                        xlabel: str = "Compression I(X;T) [nats]",
                                        ylabel: str = "Relevance I(T;Y) [nats]",
                                        title: str = "Information Bottleneck Curve",
                                        figsize: Optional[Tuple[int, int]] = None,
                                        save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot the famous Information Bottleneck curve.
        
        Shows the fundamental trade-off between compression and relevance
        that is central to the Information Bottleneck principle.
        
        Parameters
        ----------
        results : List[Dict]
            List of results with 'I_XT', 'I_TY', 'beta' keys
        xlabel, ylabel : str
            Axis labels
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        figsize = figsize or self.default_figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        # Extract data
        compression = [r['I_XT'] for r in results]
        relevance = [r['I_TY'] for r in results]
        betas = [r['beta'] for r in results]
        
        # Create the curve
        scatter = ax.scatter(compression, relevance, c=betas, 
                           s=100, alpha=0.8, cmap='viridis',
                           edgecolors='black', linewidth=0.5)
        
        # Connect points with lines
        ax.plot(compression, relevance, 'k-', alpha=0.3, linewidth=1)
        
        # Add colorbar for beta values
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('β (Trade-off Parameter)', fontsize=12)
        
        # Annotations for key points
        if len(results) > 0:
            # Low beta point (high compression, low relevance)
            low_beta_idx = np.argmin(betas)
            ax.annotate(f'Low β={betas[low_beta_idx]:.2f}\n(High compression)', 
                       xy=(compression[low_beta_idx], relevance[low_beta_idx]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, ha='left',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            # High beta point (low compression, high relevance)
            high_beta_idx = np.argmax(betas)
            ax.annotate(f'High β={betas[high_beta_idx]:.2f}\n(High relevance)', 
                       xy=(compression[high_beta_idx], relevance[high_beta_idx]),
                       xytext=(-10, -20), textcoords='offset points',
                       fontsize=10, ha='right',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.set_title(title, fontsize=16, pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_information_plane(self, X: np.ndarray, Y: np.ndarray, T: np.ndarray,
                              title: str = "Information Plane Visualization",
                              figsize: Optional[Tuple[int, int]] = None,
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot data points in the information plane (I(X;T) vs I(T;Y)).
        
        This visualization shows where different data points lie in the
        fundamental information-theoretic space.
        
        Parameters
        ----------
        X : np.ndarray
            Input data
        Y : np.ndarray
            Target data  
        T : np.ndarray
            Bottleneck representations
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        from .utils import compute_mutual_information_discrete
        
        figsize = figsize or self.default_figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        # Compute information quantities
        I_XT = compute_mutual_information_discrete(X, T)
        I_TY = compute_mutual_information_discrete(T, Y) 
        I_XY = compute_mutual_information_discrete(X, Y)
        
        # Plot theoretical bounds
        # Rate bound: 0 ≤ I(X;T) ≤ I(X;Y)
        ax.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Rate bounds')
        ax.axvline(x=I_XY, color='red', linestyle='--', alpha=0.7)
        
        # Distortion bound: 0 ≤ I(T;Y) ≤ I(X;Y)
        ax.axhline(y=0, color='blue', linestyle='--', alpha=0.7, label='Distortion bounds')
        ax.axhline(y=I_XY, color='blue', linestyle='--', alpha=0.7)
        
        # Plot current point
        ax.scatter(I_XT, I_TY, c='green', s=200, marker='*', 
                  edgecolors='black', linewidth=2, 
                  label=f'Current: I(X;T)={I_XT:.3f}, I(T;Y)={I_TY:.3f}',
                  zorder=5)
        
        # Plot information bottleneck optimality line
        # For optimal solution: I(T;Y) = I(X;Y) - I(X;T)
        x_range = np.linspace(0, I_XY, 100)
        optimal_line = I_XY - x_range
        ax.plot(x_range, np.maximum(optimal_line, 0), 'orange', linewidth=2, 
               linestyle=':', label='Optimal IB line: I(T;Y) = I(X;Y) - I(X;T)')
        
        # Shade feasible region
        x_fill = np.linspace(0, I_XY, 100)
        y_upper = np.minimum(np.full_like(x_fill, I_XY), I_XY - x_fill)
        ax.fill_between(x_fill, 0, y_upper, alpha=0.1, color='gray', 
                       label='Feasible region')
        
        ax.set_xlabel('Compression I(X;T) [nats]', fontsize=14)
        ax.set_ylabel('Relevance I(T;Y) [nats]', fontsize=14)
        ax.set_title(title, fontsize=16, pad=20)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Set axis limits with some padding
        ax.set_xlim(-0.05 * I_XY, 1.1 * I_XY)
        ax.set_ylim(-0.05 * I_XY, 1.1 * I_XY)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_training_history(self, history: Dict[str, List[float]],
                             title: str = "Information Bottleneck Training History",
                             figsize: Optional[Tuple[int, int]] = None,
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot training history showing convergence of IB objective.
        
        Parameters
        ----------
        history : Dict[str, List[float]]
            Training history with metrics over iterations
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        figsize = figsize or self.default_figsize
        
        # Determine subplot layout
        n_metrics = len(history)
        if n_metrics <= 2:
            fig, axes = plt.subplots(1, n_metrics, figsize=(figsize[0]*n_metrics//2, figsize[1]))
        else:
            n_cols = min(3, n_metrics)
            n_rows = (n_metrics + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize[0]*n_cols//2, figsize[1]*n_rows//2))
        
        if n_metrics == 1:
            axes = [axes]
        elif n_metrics > 1 and not isinstance(axes, np.ndarray):
            axes = [axes]
        else:
            axes = axes.flatten()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, (metric_name, values) in enumerate(history.items()):
            ax = axes[i]
            iterations = range(1, len(values) + 1)
            
            ax.plot(iterations, values, color=colors[i % len(colors)], 
                   linewidth=2, marker='o', markersize=4, alpha=0.8)
            
            ax.set_title(f'{metric_name.replace("_", " ").title()}', fontsize=12)
            ax.set_xlabel('Iteration', fontsize=11)
            ax.set_ylabel('Value', fontsize=11)
            ax.grid(True, alpha=0.3)
            
            # Add convergence annotation if values are decreasing/converging
            if len(values) > 10:
                recent_change = abs(values[-1] - values[-5]) / abs(values[-5] + 1e-8)
                if recent_change < 0.01:  # Converged
                    ax.annotate('Converged', xy=(len(values), values[-1]),
                               xytext=(len(values)*0.7, values[-1]),
                               fontsize=9, color='green',
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgreen', alpha=0.7),
                               arrowprops=dict(arrowstyle='->', color='green'))
        
        # Hide empty subplots
        for i in range(len(history), len(axes)):
            axes[i].set_visible(False)
        
        fig.suptitle(title, fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_beta_sensitivity(self, beta_values: np.ndarray, 
                             metrics: Dict[str, np.ndarray],
                             title: str = "Sensitivity to β Parameter",
                             figsize: Optional[Tuple[int, int]] = None,
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot how IB performance varies with β parameter.
        
        Parameters
        ----------
        beta_values : np.ndarray
            Range of β values tested
        metrics : Dict[str, np.ndarray]
            Performance metrics for each β value
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        figsize = figsize or self.default_figsize
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(figsize[0]*1.5, figsize[1]))
        
        # Plot information measures vs beta
        if 'I_XT' in metrics and 'I_TY' in metrics:
            ax1.plot(beta_values, metrics['I_XT'], 'b-o', label='I(X;T) - Compression', 
                    linewidth=2, markersize=6)
            ax1.plot(beta_values, metrics['I_TY'], 'r-s', label='I(T;Y) - Relevance', 
                    linewidth=2, markersize=6)
            
            ax1.set_xlabel('β (Trade-off Parameter)', fontsize=12)
            ax1.set_ylabel('Mutual Information [nats]', fontsize=12)
            ax1.set_title('Information vs β', fontsize=14)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xscale('log')
        
        # Plot IB objective vs beta
        if 'objective' in metrics:
            ax2.plot(beta_values, metrics['objective'], 'g-^', linewidth=2, 
                    markersize=6, label='IB Objective')
            
            # Find optimal beta
            optimal_idx = np.argmax(metrics['objective'])
            optimal_beta = beta_values[optimal_idx]
            optimal_obj = metrics['objective'][optimal_idx]
            
            ax2.axvline(x=optimal_beta, color='orange', linestyle='--', 
                       label=f'Optimal β = {optimal_beta:.3f}')
            ax2.scatter(optimal_beta, optimal_obj, color='orange', s=100, 
                       zorder=5, edgecolors='black')
            
            ax2.set_xlabel('β (Trade-off Parameter)', fontsize=12)
            ax2.set_ylabel('IB Objective Value', fontsize=12)
            ax2.set_title('Objective vs β', fontsize=14)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xscale('log')
        
        fig.suptitle(title, fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_representation_analysis(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray,
                                   method: str = 'pca',
                                   title: str = "Bottleneck Representation Analysis",
                                   figsize: Optional[Tuple[int, int]] = None,
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualize bottleneck representations using dimensionality reduction.
        
        Parameters
        ----------
        X : np.ndarray
            Original input data
        T : np.ndarray
            Bottleneck representations
        Y : np.ndarray
            Target labels/values
        method : str
            Dimensionality reduction method ('pca', 'tsne')
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        if not SKLEARN_AVAILABLE:
            warnings.warn("sklearn not available, skipping representation analysis")
            return plt.figure()
            
        figsize = figsize or self.default_figsize
        fig, axes = plt.subplots(1, 2, figsize=(figsize[0]*1.5, figsize[1]))
        
        # Ensure 2D representation for visualization
        if T.ndim == 1:
            T = T.reshape(-1, 1)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
            
        # Apply dimensionality reduction if needed
        if T.shape[1] > 2:
            if method == 'pca':
                reducer = PCA(n_components=2, random_state=42)
            elif method == 'tsne':
                reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(T)//4))
            else:
                raise ValueError(f"Unknown method: {method}")
                
            T_2d = reducer.fit_transform(T)
        else:
            T_2d = T
            
        # Similar for X if high-dimensional
        if X.shape[1] > 2:
            if method == 'pca':
                reducer_x = PCA(n_components=2, random_state=42)
            elif method == 'tsne':
                reducer_x = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X)//4))
            X_2d = reducer_x.fit_transform(X)
        else:
            X_2d = X
            
        # Plot original data
        scatter1 = axes[0].scatter(X_2d[:, 0], X_2d[:, 1], c=Y, cmap='viridis', 
                                 alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
        axes[0].set_title('Original Data X', fontsize=14)
        axes[0].set_xlabel(f'{method.upper()} Component 1', fontsize=12)
        axes[0].set_ylabel(f'{method.upper()} Component 2', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # Plot bottleneck representations
        scatter2 = axes[1].scatter(T_2d[:, 0], T_2d[:, 1], c=Y, cmap='viridis', 
                                 alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
        axes[1].set_title('Bottleneck Representations T', fontsize=14)
        axes[1].set_xlabel(f'{method.upper()} Component 1', fontsize=12)
        axes[1].set_ylabel(f'{method.upper()} Component 2', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        # Add colorbars
        plt.colorbar(scatter1, ax=axes[0], label='Target Y')
        plt.colorbar(scatter2, ax=axes[1], label='Target Y')
        
        fig.suptitle(title, fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig
    
    def plot_clustering_analysis(self, X: np.ndarray, cluster_labels: np.ndarray,
                               cluster_centers: Optional[np.ndarray] = None,
                               title: str = "Information Bottleneck Clustering",
                               figsize: Optional[Tuple[int, int]] = None,
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualize clustering results from Information Bottleneck.
        
        Parameters
        ----------
        X : np.ndarray
            Input data
        cluster_labels : np.ndarray
            Cluster assignments
        cluster_centers : np.ndarray, optional
            Cluster centers
        title : str
            Plot title
        figsize : Tuple[int, int], optional
            Figure size
        save_path : str, optional
            Path to save figure
            
        Returns
        -------
        plt.Figure
            The created figure
        """
        figsize = figsize or self.default_figsize
        
        # Handle 1D data
        if X.ndim == 1:
            X = X.reshape(-1, 1)
            
        # Apply PCA if high-dimensional
        if X.shape[1] > 2 and SKLEARN_AVAILABLE:
            pca = PCA(n_components=2, random_state=42)
            X_plot = pca.fit_transform(X)
            if cluster_centers is not None and cluster_centers.shape[1] > 2:
                centers_plot = pca.transform(cluster_centers)
            else:
                centers_plot = cluster_centers
        else:
            X_plot = X[:, :2] if X.shape[1] >= 2 else np.column_stack([X[:, 0], np.zeros(len(X))])
            centers_plot = cluster_centers
            
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot data points colored by cluster
        n_clusters = len(np.unique(cluster_labels))
        colors = plt.cm.Set3(np.linspace(0, 1, n_clusters))
        
        for i, cluster_id in enumerate(np.unique(cluster_labels)):
            mask = cluster_labels == cluster_id
            ax.scatter(X_plot[mask, 0], X_plot[mask, 1], 
                      c=[colors[i]], alpha=0.7, s=50, 
                      label=f'Cluster {cluster_id}',
                      edgecolors='black', linewidth=0.5)
        
        # Plot cluster centers if provided
        if centers_plot is not None:
            ax.scatter(centers_plot[:, 0], centers_plot[:, 1], 
                      c='red', marker='x', s=200, linewidth=3,
                      label='Cluster Centers')
        
        ax.set_xlabel('Principal Component 1' if X.shape[1] > 2 else 'X', fontsize=12)
        ax.set_ylabel('Principal Component 2' if X.shape[1] > 2 else 'Constant', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig


# ============================================================================
# INTERACTIVE VISUALIZATION (PLOTLY)
# ============================================================================

class InteractiveIBVisualization:
    """
    Interactive visualization suite using Plotly.
    
    Provides interactive plots for exploration of Information Bottleneck
    results with zooming, hovering, and animation capabilities.
    """
    
    def __init__(self):
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is required for interactive visualizations. "
                            "Install with: pip install plotly")
    
    def plot_interactive_ib_curve(self, results: List[Dict],
                                 title: str = "Interactive Information Bottleneck Curve"):
        """
        Create interactive Information Bottleneck curve with Plotly.
        
        Parameters
        ----------
        results : List[Dict]
            Results with 'I_XT', 'I_TY', 'beta' keys
        title : str
            Plot title
            
        Returns
        -------
        plotly.graph_objects.Figure
            Interactive figure
        """
        compression = [r['I_XT'] for r in results]
        relevance = [r['I_TY'] for r in results]
        betas = [r['beta'] for r in results]
        
        fig = go.Figure()
        
        # Add scatter plot with color coding
        fig.add_trace(go.Scatter(
            x=compression,
            y=relevance,
            mode='markers+lines',
            marker=dict(
                size=12,
                color=betas,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="β Parameter"),
                line=dict(width=1, color='black')
            ),
            text=[f'β: {b:.3f}<br>I(X;T): {c:.3f}<br>I(T;Y): {r:.3f}' 
                  for b, c, r in zip(betas, compression, relevance)],
            hovertemplate='%{text}<extra></extra>',
            name='IB Curve'
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title="Compression I(X;T) [nats]",
            yaxis_title="Relevance I(T;Y) [nats]",
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig
    
    def plot_interactive_3d_surface(self, beta_range: np.ndarray, 
                                   n_clusters_range: np.ndarray,
                                   objective_surface: np.ndarray,
                                   title: str = "IB Objective Surface"):
        """
        Create interactive 3D surface plot of IB objective.
        
        Parameters
        ----------
        beta_range : np.ndarray
            Range of β values
        n_clusters_range : np.ndarray
            Range of cluster numbers
        objective_surface : np.ndarray
            IB objective values (2D grid)
        title : str
            Plot title
            
        Returns
        -------
        plotly.graph_objects.Figure
            Interactive 3D figure
        """
        fig = go.Figure(data=[go.Surface(
            x=beta_range,
            y=n_clusters_range,
            z=objective_surface,
            colorscale='Viridis',
            hovertemplate='β: %{x:.3f}<br>Clusters: %{y}<br>Objective: %{z:.3f}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            scene=dict(
                xaxis_title="β Parameter",
                yaxis_title="Number of Clusters",
                zaxis_title="IB Objective",
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            )
        )
        
        return fig


# ============================================================================
# SPECIALIZED PLOTTING FUNCTIONS
# ============================================================================

def plot_mutual_information_heatmap(data_matrix: np.ndarray, 
                                   feature_names: Optional[List[str]] = None,
                                   title: str = "Mutual Information Heatmap",
                                   figsize: Tuple[int, int] = (10, 8),
                                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot heatmap of pairwise mutual information between features.
    
    Parameters
    ----------
    data_matrix : np.ndarray
        Pairwise MI matrix
    feature_names : List[str], optional
        Names for features
    title : str
        Plot title
    figsize : Tuple[int, int]
        Figure size
    save_path : str, optional
        Path to save figure
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap
    im = ax.imshow(data_matrix, cmap='viridis', aspect='auto')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Mutual Information [nats]', fontsize=12)
    
    # Set ticks and labels
    n_features = data_matrix.shape[0]
    if feature_names is None:
        feature_names = [f'Feature {i+1}' for i in range(n_features)]
        
    ax.set_xticks(range(n_features))
    ax.set_yticks(range(n_features))
    ax.set_xticklabels(feature_names, rotation=45, ha='right')
    ax.set_yticklabels(feature_names)
    
    # Add text annotations
    for i in range(n_features):
        for j in range(n_features):
            text = ax.text(j, i, f'{data_matrix[i, j]:.3f}',
                         ha="center", va="center", color="white" if data_matrix[i, j] > 0.5 else "black")
    
    ax.set_title(title, fontsize=16, pad=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_compression_distortion_tradeoff(results: List[Dict],
                                        title: str = "Compression-Distortion Trade-off",
                                        figsize: Tuple[int, int] = (10, 8),
                                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot the compression-distortion trade-off curve.
    
    Parameters
    ----------
    results : List[Dict]
        Results with compression and distortion metrics
    title : str
        Plot title
    figsize : Tuple[int, int]
        Figure size
    save_path : str, optional
        Path to save figure
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    compression = [r['compression'] for r in results]
    distortion = [r['distortion'] for r in results]
    
    # Plot the trade-off curve
    ax.plot(compression, distortion, 'bo-', linewidth=2, markersize=8, 
           label='IB Trade-off')
    
    # Add annotations for key points
    if len(results) > 0:
        # Best compression point
        best_comp_idx = np.argmin(compression)
        ax.annotate(f'Best Compression\n({compression[best_comp_idx]:.3f}, {distortion[best_comp_idx]:.3f})',
                   xy=(compression[best_comp_idx], distortion[best_comp_idx]),
                   xytext=(20, 20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'))
        
        # Best distortion point  
        best_dist_idx = np.argmin(distortion)
        ax.annotate(f'Best Distortion\n({compression[best_dist_idx]:.3f}, {distortion[best_dist_idx]:.3f})',
                   xy=(compression[best_dist_idx], distortion[best_dist_idx]),
                   xytext=(-20, -30), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral'),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2'))
    
    ax.set_xlabel('Compression (bits)', fontsize=14)
    ax.set_ylabel('Distortion', fontsize=14)
    ax.set_title(title, fontsize=16, pad=20)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_all_figures(figures: Dict[str, plt.Figure], 
                    output_dir: str, 
                    format: str = 'png',
                    dpi: int = 300) -> None:
    """
    Save all figures to specified directory.
    
    Parameters
    ----------
    figures : Dict[str, plt.Figure]
        Dictionary mapping figure names to Figure objects
    output_dir : str
        Output directory path
    format : str
        Figure format ('png', 'pdf', 'svg')
    dpi : int
        Figure resolution
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for name, fig in figures.items():
        filename = f"{name}.{format}"
        filepath = output_path / filename
        fig.savefig(filepath, format=format, dpi=dpi, bbox_inches='tight')
        print(f"Saved: {filepath}")


def create_visualization_report(ib_model, X: np.ndarray, Y: np.ndarray,
                              output_dir: str = "ib_analysis",
                              interactive: bool = False) -> Dict[str, plt.Figure]:
    """
    Create comprehensive visualization report for IB analysis.
    
    Parameters
    ----------
    ib_model
        Trained Information Bottleneck model
    X : np.ndarray
        Input data
    Y : np.ndarray
        Target data
    output_dir : str
        Output directory for saving figures
    interactive : bool
        Whether to create interactive plots
        
    Returns
    -------
    Dict[str, plt.Figure]
        Dictionary of created figures
    """
    viz = IBVisualization()
    figures = {}
    
    # Get bottleneck representations
    T = ib_model.transform(X)
    
    # Information plane visualization
    figures['information_plane'] = viz.plot_information_plane(X, Y, T)
    
    # Representation analysis
    if SKLEARN_AVAILABLE:
        figures['representation_pca'] = viz.plot_representation_analysis(
            X, T, Y, method='pca', title='PCA Representation Analysis'
        )
        
        if len(X) <= 1000:  # t-SNE is slow for large datasets
            figures['representation_tsne'] = viz.plot_representation_analysis(
                X, T, Y, method='tsne', title='t-SNE Representation Analysis'
            )
    
    # Clustering analysis if discrete IB
    if hasattr(ib_model, 'p_t_given_x_'):
        cluster_labels = np.argmax(ib_model.p_t_given_x_, axis=1)
        figures['clustering'] = viz.plot_clustering_analysis(X, cluster_labels)
    
    # Save all figures
    save_all_figures(figures, output_dir)
    
    return figures