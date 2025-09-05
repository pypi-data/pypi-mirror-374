"""
🎛️ Information Bottleneck Optimizer - Smart Parameter Learning Engine
====================================================================

🎯 ELI5 EXPLANATION:
==================
Think of the Information Bottleneck Optimizer like a master chef perfecting a recipe through countless experiments!

Imagine you're developing the perfect recipe, but you have dozens of ingredients (parameters) and need to find exactly the right amounts. Too much salt ruins the dish, too little makes it bland. The IB Optimizer is like having a genius chef who:

1. 🔥 **Annealing Schedule**: Slowly adjusts heat (β parameter) to find perfect balance between flavor and complexity
2. 🎯 **Parameter Search**: Tries thousands of ingredient combinations to find the perfect recipe
3. 🔄 **Multiple Attempts**: Restarts from scratch multiple times to avoid getting stuck on bad recipes
4. 📊 **Smart Learning**: Analyzes what works and converges to the optimal solution!

Just like a master chef who knows exactly when to adjust temperature and timing, this optimizer finds the perfect parameters for information compression and prediction accuracy!

🔬 RESEARCH FOUNDATION:
======================
Core optimization theory from machine learning pioneers:
- **Rose et al. (1990)**: "Deterministic annealing for clustering" - Annealing methodology
- **Tishby et al. (2000)**: "The information bottleneck method" - Parameter optimization theory
- **Slonim et al. (2002)**: "Agglomerative information bottleneck" - Practical optimization
- **Bergstra & Bengio (2012)**: "Random search for hyper-parameter optimization" - Search strategies

🧮 MATHEMATICAL PRINCIPLES:
==========================
**Deterministic Annealing:**
β(t) = β₀ × exp(t/τ) - Exponential temperature schedule

**Multi-Objective Optimization:**
L = min I(X,T) - β × max I(T,Y)
Find optimal β that balances compression vs prediction

**Parameter Search Space:**
Θ = {β, n_clusters, convergence_tolerance, ...}
Search over hyperparameter space for optimal performance

📊 OPTIMIZER ARCHITECTURE VISUALIZATION:
=======================================
```
🎛️ INFORMATION BOTTLENECK OPTIMIZER 🎛️

Parameter Space            Optimization Strategy              Optimal Solution
┌─────────────────┐       ┌──────────────────────────────┐   ┌─────────────────┐
│ 🎛️ Hyperparams   │       │                              │   │ 🎯 BEST PARAMS  │
│ β: [0.1, 10.0]  │ ───→  │  🔥 ANNEALING SCHEDULE:      │ → │ β*: 2.47        │
│ clusters: [5,50]│       │  • Slow temperature increase │   │ clusters*: 23   │
│ tolerance: 1e-6 │       │  • Smooth parameter evolution│   │ tolerance*: 1e-4│
└─────────────────┘       │                              │   │                 │
                          │  🔍 SEARCH STRATEGIES:       │   │ 🏆 PERFORMANCE  │
┌─────────────────┐       │  • Random search trials     │   │ Best objective: │
│ 📊 Search Space  │ ───→  │  • Evolutionary optimization│   │ 0.2847         │
│ Multi-dimensional│       │  • Multi-restart robustness │   │                 │
│ Complex landscape│       │                              │   │ 📈 CONVERGENCE  │
└─────────────────┘       │  📊 CONVERGENCE ANALYSIS:    │   │ Stable after    │
                          │  • Progress monitoring       │   │ 47 iterations   │
┌─────────────────┐       │  • Stabilization detection  │   │                 │
│ 🎯 Objectives     │ ───→  │  • Quality assessment       │   │ ✨ ROBUSTNESS   │
│ Min compression │       │                              │   │ Consistent      │
│ Max prediction  │       └──────────────────────────────┘   │ across restarts │
└─────────────────┘                      │                   └─────────────────┘
                                         ▼
                              RESULT: Perfect parameter tuning 
                                     for optimal IB! 🚀
```

💰 SUPPORT THIS RESEARCH:
=========================
🙏 If this library helps your research:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
💖 GitHub Sponsors: https://github.com/sponsors/benedictchen

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Advanced optimization methods for information theory
"""

import numpy as np
from typing import Dict, List, Optional, Any, Callable, Tuple
from scipy.optimize import minimize, differential_evolution
import warnings
warnings.filterwarnings('ignore')


class IBOptimizer:
    """
    Advanced optimization methods for Information Bottleneck
    
    Provides sophisticated optimization strategies including:
    - Deterministic annealing schedules
    - Multi-objective optimization
    - Hyperparameter tuning
    - Convergence analysis
    """
    
    def __init__(
        self,
        ib_model,
        optimization_method: str = 'deterministic_annealing',
        n_restarts: int = 5,
        random_seed: Optional[int] = None
    ):
        """
        Initialize IB Optimizer
        
        Args:
            ib_model: Information Bottleneck model to optimize
            optimization_method: Optimization strategy
            n_restarts: Number of random restarts
            random_seed: Random seed for reproducibility
        """
        
        self.ib_model = ib_model
        self.optimization_method = optimization_method
        self.n_restarts = n_restarts
        self.random_seed = random_seed
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Optimization history
        self.optimization_history = {
            'objectives': [],
            'beta_schedules': [],
            'convergence_info': []
        }
        
    def create_beta_schedule(
        self,
        schedule_type: str = 'exponential',
        beta_min: float = 0.01,
        beta_max: float = 10.0,
        n_steps: int = 100,
        **kwargs
    ) -> List[float]:
        """
        Create beta annealing schedule
        
        Args:
            schedule_type: Type of schedule ('linear', 'exponential', 'cosine', 'adaptive')
            beta_min: Starting beta value
            beta_max: Final beta value
            n_steps: Number of optimization steps
            
        Returns:
            List of beta values for annealing
        """
        
        if schedule_type == 'linear':
            return np.linspace(beta_min, beta_max, n_steps).tolist()
            
        elif schedule_type == 'exponential':
            return np.logspace(np.log10(beta_min), np.log10(beta_max), n_steps).tolist()
            
        elif schedule_type == 'cosine':
            t = np.linspace(0, np.pi/2, n_steps)
            return (beta_min + (beta_max - beta_min) * np.sin(t)**2).tolist()
            
        elif schedule_type == 'sigmoid':
            t = np.linspace(-6, 6, n_steps)
            sigmoid = 1.0 / (1.0 + np.exp(-t))
            return (beta_min + (beta_max - beta_min) * sigmoid).tolist()
            
        elif schedule_type == 'adaptive':
            # Starts slow, accelerates, then slows down
            t = np.linspace(0, 1, n_steps)
            adaptive_curve = 3*t**2 - 2*t**3  # Smooth S-curve
            return (beta_min + (beta_max - beta_min) * adaptive_curve).tolist()
            
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
    
    def optimize_with_annealing(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        schedule_type: str = 'exponential',
        beta_min: float = 0.01,
        beta_max: float = 10.0,
        n_steps: int = 100,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize IB using deterministic annealing
        
        Args:
            X: Input data
            Y: Target data
            schedule_type: Beta annealing schedule
            beta_min: Starting beta value
            beta_max: Final beta value
            n_steps: Number of annealing steps
            verbose: Print progress
            
        Returns:
            Optimization results and statistics
        """
        
        # Create beta schedule
        beta_schedule = self.create_beta_schedule(
            schedule_type, beta_min, beta_max, n_steps
        )
        
        if verbose:
            print(f"🔥 Optimizing IB with {schedule_type} annealing...")
            print(f"   • β: {beta_min:.3f} → {beta_max:.3f} in {n_steps} steps")
        
        # Store original settings
        original_beta = self.ib_model.beta
        original_max_iter = self.ib_model.max_iter
        
        # Set iterations per beta step
        self.ib_model.max_iter = max(10, original_max_iter // n_steps)
        
        best_objective = float('inf')
        best_result = None
        objectives = []
        
        for i, beta in enumerate(beta_schedule):
            self.ib_model.beta = beta
            
            # Fit with current beta
            result = self.ib_model.fit(X, Y, verbose=False)
            objective = result.get('final_objective', float('inf'))
            objectives.append(objective)
            
            if objective < best_objective:
                best_objective = objective
                best_result = result
            
            if verbose and (i + 1) % 20 == 0:
                print(f"   Step {i+1:3d}/{n_steps}: β={beta:.3f}, "
                      f"Obj={objective:.4f}, Best={best_objective:.4f}")
        
        # Restore original settings
        self.ib_model.beta = original_beta
        self.ib_model.max_iter = original_max_iter
        
        # Store optimization history
        self.optimization_history['objectives'].append(objectives)
        self.optimization_history['beta_schedules'].append(beta_schedule)
        self.optimization_history['convergence_info'].append({
            'best_objective': best_objective,
            'final_beta': beta_schedule[-1],
            'n_steps': n_steps,
            'schedule_type': schedule_type
        })
        
        if verbose:
            # Removed print spam: f"...
            print(f"   • Best objective: {best_objective:.4f}")
            print(f"   • Final β: {beta_schedule[-1]:.3f}")
        
        return {
            'best_objective': best_objective,
            'best_result': best_result,
            'objectives': objectives,
            'beta_schedule': beta_schedule,
            'optimization_type': 'deterministic_annealing'
        }
    
    def hyperparameter_search(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        param_ranges: Dict[str, Tuple[float, float]],
        n_trials: int = 50,
        method: str = 'random',
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Search for optimal hyperparameters
        
        Args:
            X: Input data
            Y: Target data
            param_ranges: Dictionary of parameter ranges to search
            n_trials: Number of search trials
            method: Search method ('random', 'grid', 'evolutionary')
            verbose: Print progress
            
        Returns:
            Best parameters and search results
        """
        
        if verbose:
            # Removed print spam: f"...
            print(f"   • Parameters: {list(param_ranges.keys())}")
            print(f"   • Trials: {n_trials}")
        
        def objective_function(params_list):
            """Objective function for optimization"""
            
            # Convert list back to parameter dictionary
            param_names = list(param_ranges.keys())
            params = dict(zip(param_names, params_list))
            
            # Set parameters
            for param_name, param_value in params.items():
                if hasattr(self.ib_model, param_name):
                    setattr(self.ib_model, param_name, param_value)
            
            try:
                # Fit model with current parameters
                result = self.ib_model.fit(X, Y, verbose=False)
                objective = result.get('final_objective', float('inf'))
                
                # For minimization, return positive value
                return objective
                
            except Exception as e:
                if verbose:
                    print(f"   Warning: Parameter set failed: {params}")
                return float('inf')
        
        # Parameter bounds for optimization
        bounds = list(param_ranges.values())
        
        if method == 'random':
            # Random search
            best_objective = float('inf')
            best_params = None
            all_results = []
            
            for trial in range(n_trials):
                # Sample random parameters
                params_list = []
                for param_min, param_max in bounds:
                    if isinstance(param_min, int) and isinstance(param_max, int):
                        param_val = np.random.randint(param_min, param_max + 1)
                    else:
                        param_val = np.random.uniform(param_min, param_max)
                    params_list.append(param_val)
                
                # Evaluate objective
                objective = objective_function(params_list)
                
                param_names = list(param_ranges.keys())
                trial_params = dict(zip(param_names, params_list))
                all_results.append((objective, trial_params))
                
                if objective < best_objective:
                    best_objective = objective
                    best_params = trial_params
                
                if verbose and (trial + 1) % 10 == 0:
                    print(f"   Trial {trial+1:3d}/{n_trials}: "
                          f"Obj={objective:.4f}, Best={best_objective:.4f}")
        
        elif method == 'evolutionary':
            # Evolutionary optimization
            result = differential_evolution(
                objective_function,
                bounds,
                maxiter=n_trials,
                seed=self.random_seed
            )
            
            best_objective = result.fun
            param_names = list(param_ranges.keys())
            best_params = dict(zip(param_names, result.x))
            all_results = [(best_objective, best_params)]
            
        else:
            raise ValueError(f"Unknown search method: {method}")
        
        if verbose:
            # Removed print spam: f"...
            print(f"   • Best objective: {best_objective:.4f}")
            print(f"   • Best parameters: {best_params}")
        
        return {
            'best_objective': best_objective,
            'best_params': best_params,
            'all_results': all_results,
            'search_method': method,
            'n_trials': n_trials
        }
    
    def multi_restart_optimization(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        n_restarts: int = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize with multiple random restarts
        
        Args:
            X: Input data
            Y: Target data
            n_restarts: Number of restarts (uses self.n_restarts if None)
            verbose: Print progress
            
        Returns:
            Best result from all restarts
        """
        
        if n_restarts is None:
            n_restarts = self.n_restarts
        
        if verbose:
            print(f"🔄 Multi-restart optimization with {n_restarts} restarts...")
        
        best_objective = float('inf')
        best_result = None
        all_results = []
        
        for restart in range(n_restarts):
            # Set random seed for this restart
            if self.random_seed is not None:
                np.random.seed(self.random_seed + restart)
            
            try:
                # Fit model
                result = self.ib_model.fit(X, Y, verbose=False)
                objective = result.get('final_objective', float('inf'))
                all_results.append(result)
                
                if objective < best_objective:
                    best_objective = objective
                    best_result = result
                
                if verbose:
                    print(f"   Restart {restart+1:2d}: Obj={objective:.4f}, "
                          f"Best={best_objective:.4f}")
                    
            except Exception as e:
                if verbose:
                    print(f"   Restart {restart+1:2d}: Failed ({e})")
                continue
        
        if verbose:
            # Removed print spam: f"...
            print(f"   • Best objective: {best_objective:.4f}")
        
        return {
            'best_objective': best_objective,
            'best_result': best_result,
            'all_results': all_results,
            'n_restarts': n_restarts
        }
    
    def analyze_convergence(self, training_history: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Analyze convergence properties of optimization
        
        Args:
            training_history: Training history from IB model
            
        Returns:
            Convergence analysis results
        """
        
        objectives = training_history.get('ib_objective', [])
        if not objectives:
            return {'error': 'No objective history available'}
        
        objectives = np.array(objectives)
        
        # Basic convergence metrics
        analysis = {
            'converged': len(objectives) > 0,
            'final_objective': objectives[-1] if len(objectives) > 0 else None,
            'best_objective': np.min(objectives) if len(objectives) > 0 else None,
            'n_iterations': len(objectives),
            'objective_improvement': objectives[0] - objectives[-1] if len(objectives) > 1 else 0
        }
        
        if len(objectives) > 10:
            # Convergence rate analysis
            recent_objectives = objectives[-10:]
            early_objectives = objectives[:10]
            
            analysis.update({
                'recent_variance': np.var(recent_objectives),
                'early_variance': np.var(early_objectives),
                'convergence_rate': (early_objectives[-1] - recent_objectives[0]) / len(objectives),
                'stabilization_iteration': self._find_stabilization_point(objectives)
            })
        
        return analysis
    
    def _find_stabilization_point(self, objectives: np.ndarray, window: int = 20) -> int:
        """Find iteration where objective stabilizes"""
        if len(objectives) < window * 2:
            return len(objectives)
        
        # Calculate rolling variance
        variances = []
        for i in range(window, len(objectives) - window):
            window_objectives = objectives[i-window:i+window]
            variances.append(np.var(window_objectives))
        
        # Find point where variance becomes consistently low
        variance_threshold = np.percentile(variances, 25)  # Bottom quartile
        for i, var in enumerate(variances):
            if var <= variance_threshold:
                return i + window
        
        return len(objectives)