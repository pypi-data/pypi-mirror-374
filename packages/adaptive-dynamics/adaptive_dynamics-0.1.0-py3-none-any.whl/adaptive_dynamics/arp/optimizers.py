"""
PyTorch implementation of the ARP optimizer.
"""

from collections.abc import Iterable

import torch
from torch.optim.optimizer import Optimizer

from .arp_ode import ARPSystem


class ARP(Optimizer):
    r"""
    ARP optimizer: dG/dt = α|I| - μG
    
    Uses a conductance-like state to modulate effective step sizes.
    The optimizer adapts learning rates based on gradient magnitude history,
    similar to how electrical conductance adapts in certain systems.
    
    Args:
        params: Iterable of parameters to optimize
        lr: Learning rate
        alpha: Adaptation rate (default: 0.01)
        mu: Decay rate (default: 0.001)
        weight_decay: Weight decay factor (L2 penalty)
        
    Example:
        >>> model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))
        >>> optimizer = ARP(model.parameters(), lr=3e-3, alpha=0.01, mu=0.001)
        >>> for input, target in dataset:
        >>>     optimizer.zero_grad()
        >>>     output = model(input)
        >>>     loss = loss_fn(output, target)
        >>>     loss.backward()
        >>>     optimizer.step()
    """
    
    def __init__(
        self,
        params: Iterable[torch.Tensor],
        lr: float = 1e-3,
        alpha: float = 0.01,
        mu: float = 0.001,
        weight_decay: float = 0.0
    ):
        """Initialize the ARP optimizer."""
        defaults = dict(lr=lr, alpha=alpha, mu=mu, weight_decay=weight_decay)
        super().__init__(params, defaults)
        
        # Create ARP system for reference (not directly used in optimization)
        self.arp_system = ARPSystem(alpha=alpha, mu=mu)
    
    @torch.no_grad()
    def step(self, closure: callable = None) -> torch.Tensor | None:
        """
        Perform a single optimization step.
        
        Args:
            closure: A closure that reevaluates the model and returns the loss
            
        Returns:
            Loss value if closure is provided, otherwise None
        """
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
                
        for group in self.param_groups:
            alpha = group["alpha"]
            mu = group["mu"]
            weight_decay = group["weight_decay"]
            lr = group["lr"]
            
            for p in group["params"]:
                if p.grad is None:
                    continue
                
                # Get gradient
                grad = p.grad
                
                # Apply weight decay if specified
                if weight_decay != 0:
                    grad = grad.add(p, alpha=weight_decay)
                
                # Get state for this parameter
                state = self.state.setdefault(p, {})
                
                # Initialize conductance state if needed
                if len(state) == 0:
                    state["G"] = torch.zeros_like(p)
                
                # Get conductance state
                G = state["G"]
                
                # Calculate input current (gradient magnitude)
                I = torch.abs(grad)
                
                # Update conductance: dG/dt = α|I| - μG
                G = G + alpha * I - mu * G
                state["G"] = G
                
                # Apply update with conductance-modulated learning rate
                p.addcdiv_(-lr, grad, 1.0 + G)
        
        return loss
    
    def get_adaptive_lr(self) -> dict[str, torch.Tensor]:
        """
        Get the current adaptive learning rates for all parameters.
        
        Returns:
            Dictionary mapping parameter tensors to their effective learning rates
        """
        effective_lrs = {}
        
        for group in self.param_groups:
            base_lr = group["lr"]
            
            for p in group["params"]:
                state = self.state.get(p)
                if state is None or "G" not in state:
                    effective_lrs[p] = base_lr
                else:
                    G = state["G"]
                    effective_lrs[p] = base_lr / (1.0 + G)
                    
        return effective_lrs
    
    def reset_conductance(self) -> None:
        """Reset the conductance state for all parameters."""
        for group in self.param_groups:
            for p in group["params"]:
                state = self.state.get(p)
                if state is not None and "G" in state:
                    state["G"].zero_()


try:
    import tensorflow as tf
    
    class TensorFlowARP(tf.keras.optimizers.Optimizer):
        """
        TensorFlow implementation of the ARP optimizer.
        
        This optimizer follows the same dynamics as the PyTorch version:
        dG/dt = α|I| - μG
        
        Args:
            learning_rate: Initial learning rate
            alpha: Adaptation rate (default: 0.01)
            mu: Decay rate (default: 0.001)
            weight_decay: Weight decay factor (L2 penalty)
            name: Optional name for the optimizer
        """
        
        def __init__(
            self,
            learning_rate: float = 0.001,
            alpha: float = 0.01,
            mu: float = 0.001,
            weight_decay: float = 0.0,
            name: str = "ARP",
            **kwargs
        ):
            """Initialize the optimizer."""
            super().__init__(name=name, **kwargs)
            self._set_hyper("learning_rate", learning_rate)
            self._set_hyper("alpha", alpha)
            self._set_hyper("mu", mu)
            self._set_hyper("weight_decay", weight_decay)
        
        def _create_slots(self, var_list: list) -> None:
            """Create optimizer state variables for each model variable."""
            for var in var_list:
                self.add_slot(var, "G")  # Conductance state
        
        def _resource_apply_dense(self, grad, var, apply_state=None) -> tf.Tensor:
            """Apply gradients to variables."""
            var_dtype = var.dtype.base_dtype
            lr = self._get_hyper("learning_rate", var_dtype)
            alpha = self._get_hyper("alpha", var_dtype)
            mu = self._get_hyper("mu", var_dtype)
            weight_decay = self._get_hyper("weight_decay", var_dtype)
            
            G = self.get_slot(var, "G")
            
            # Apply weight decay if specified
            if weight_decay > 0:
                grad = grad + weight_decay * var
                
            # Update conductance: dG/dt = α|I| - μG
            G_new = G + alpha * tf.abs(grad) - mu * G
            self._resource_apply_assign(G, G_new)
            
            # Apply update with conductance-modulated learning rate
            var_update = var - lr * grad / (1.0 + G_new)
            self._resource_apply_assign(var, var_update)
            
            return var_update
        
        def _resource_apply_sparse(self, grad, var, indices, apply_state=None):
            """Apply sparse gradients to variables."""
            # This is a simplified sparse implementation
            # For production, this would need more optimization
            var_dtype = var.dtype.base_dtype
            lr = self._get_hyper("learning_rate", var_dtype)
            alpha = self._get_hyper("alpha", var_dtype)
            mu = self._get_hyper("mu", var_dtype)
            
            G = self.get_slot(var, "G")
            
            # Update conductance for sparse indices
            sparse_grad_abs = tf.abs(tf.IndexedSlices(grad, indices, var.shape))
            
            # Full update for decay term (applies to all elements)
            G_update = G * (1.0 - mu)
            
            # Sparse update for growth term (applies only to indices with gradients)
            G_update = tf.tensor_scatter_nd_add(
                G_update, 
                tf.expand_dims(indices, axis=1), 
                alpha * sparse_grad_abs
            )
            
            self._resource_apply_assign(G, G_update)
            
            # Apply update with conductance-modulated learning rate
            var_update = tf.tensor_scatter_nd_sub(
                var, 
                tf.expand_dims(indices, axis=1), 
                lr * grad / (1.0 + tf.gather(G_update, indices))
            )
            self._resource_apply_assign(var, var_update)
            
            return var_update
        
        def get_config(self) -> dict:
            """Return the optimizer configuration."""
            config = super().get_config()
            config.update({
                "learning_rate": self._serialize_hyperparameter("learning_rate"),
                "alpha": self._serialize_hyperparameter("alpha"),
                "mu": self._serialize_hyperparameter("mu"),
                "weight_decay": self._serialize_hyperparameter("weight_decay")
            })
            return config
            
except ImportError:
    # TensorFlow not available
    pass