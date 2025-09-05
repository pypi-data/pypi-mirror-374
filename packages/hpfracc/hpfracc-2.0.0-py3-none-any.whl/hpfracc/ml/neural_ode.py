"""
Neural Fractional Ordinary Differential Equations (Neural fODE)

This module implements neural networks that can learn to represent
fractional differential equations, extending the concept of Neural ODEs
to fractional calculus.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Union, Optional, List, Dict
from abc import ABC, abstractmethod
import warnings

from ..core.definitions import FractionalOrder
from ..core.utilities import validate_fractional_order


class BaseNeuralODE(nn.Module, ABC):
    """
    Base class for Neural ODE implementations.

    This abstract class provides the foundation for neural networks
    that can learn to represent ordinary differential equations.
    """

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int,
                 num_layers: int = 3, activation: str = "tanh",
                 use_adjoint: bool = True):
        """
        Initialize base neural ODE.

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden layer dimension
            output_dim: Output dimension
            num_layers: Number of hidden layers
            activation: Activation function ("tanh", "relu", "sigmoid")
            use_adjoint: Whether to use adjoint method for gradients
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.activation = activation
        self.use_adjoint = use_adjoint

        # Build neural network
        self._build_network()

    def _build_network(self):
        """Build the neural network architecture."""
        layers = []

        # Input layer: time + input_dim -> hidden_dim
        layers.append(nn.Linear(self.input_dim + 1, self.hidden_dim))

        # Hidden layers
        for _ in range(self.num_layers - 1):
            layers.append(nn.Linear(self.hidden_dim, self.hidden_dim))

        # Output layer
        layers.append(nn.Linear(self.hidden_dim, self.output_dim))

        self.network = nn.Sequential(*layers)

        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def _get_activation(self, x: torch.Tensor) -> torch.Tensor:
        """Apply activation function."""
        if self.activation == "tanh":
            return torch.tanh(x)
        elif self.activation == "relu":
            return F.relu(x)
        elif self.activation == "sigmoid":
            return torch.sigmoid(x)
        else:
            return torch.tanh(x)  # Default to tanh

    @abstractmethod
    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the neural ODE.

        Args:
            x: Input tensor
            t: Time tensor

        Returns:
            Output tensor
        """

    def ode_func(self, t: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        """
        ODE function that defines the dynamics.

        Args:
            t: Time tensor
            x: State tensor

        Returns:
            Derivative tensor
        """
        # Check if this was originally a single input
        was_single_input = len(x.shape) == 1

        # Ensure x has correct shape
        if was_single_input:
            x = x.unsqueeze(0)

        # Handle time tensor shape
        if len(t.shape) == 0:
            t = t.unsqueeze(0)

        # Expand time to match batch size
        batch_size = x.shape[0]
        if t.numel() == 1:
            t = t.expand(batch_size)

        # Concatenate time and state: [t, x]
        t_expanded = t.unsqueeze(-1)  # Shape: (batch_size, 1)
        # Shape: (batch_size, 1 + input_dim)
        input_tensor = torch.cat([t_expanded, x], dim=-1)

        # Pass through network
        output = self.network(input_tensor)

        # Apply activation
        output = self._get_activation(output)

        # Handle output shape for single inputs
        if was_single_input and output.shape[0] == 1:
            # Remove batch dimension for single input
            output = output.squeeze(0)

        return output


class NeuralODE(BaseNeuralODE):
    """
    Standard Neural ODE implementation.

    This class implements a neural network that learns to represent
    ordinary differential equations of the form dx/dt = f(x, t).
    """

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int,
                 num_layers: int = 3, activation: str = "tanh",
                 use_adjoint: bool = True, solver: str = "dopri5",
                 rtol: float = 1e-5, atol: float = 1e-5):
        """
        Initialize Neural ODE.

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden layer dimension
            output_dim: Output dimension
            num_layers: Number of hidden layers
            activation: Activation function
            use_adjoint: Whether to use adjoint method
            solver: ODE solver ("dopri5", "euler", "rk4")
            rtol: Relative tolerance for adaptive solvers
            atol: Absolute tolerance for adaptive solvers
        """
        super().__init__(input_dim, hidden_dim, output_dim,
                         num_layers, activation, use_adjoint)

        self.solver = solver
        self.rtol = rtol
        self.atol = atol

        # Try to import torchdiffeq for advanced solvers
        try:
            self.has_torchdiffeq = True
        except ImportError:
            self.has_torchdiffeq = False
            warnings.warn(
                "torchdiffeq not available. Using basic Euler solver.")

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the neural ODE.

        Args:
            x: Input tensor of shape (batch_size, input_dim)
            t: Time tensor of shape (time_steps,) or (batch_size, time_steps)

        Returns:
            Output tensor of shape (batch_size, time_steps, output_dim)
        """
        batch_size = x.shape[0]

        if len(t.shape) == 1:
            t = t.unsqueeze(0).expand(batch_size, -1)

        # Solve ODE
        if self.has_torchdiffeq and self.solver == "dopri5":
            solution = self._solve_torchdiffeq(x, t)
        else:
            solution = self._solve_basic(x, t)

        return solution

    def _solve_torchdiffeq(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Solve using torchdiffeq if available."""
        if not self.has_torchdiffeq:
            raise ImportError("torchdiffeq is not available")

        # Ensure t is 1D time vector
        if t.dim() > 1:
            t_vec = t[0]
        else:
            t_vec = t

        # Initial state for integration should match output_dim
        if x.dim() == 1:
            y0 = x[: self.output_dim].unsqueeze(0)
        else:
            y0 = x[:, : self.output_dim]

        # Wrap the ODE function as an nn.Module for adjoint API
        class _ODEFunc(nn.Module):
            def __init__(self, parent: 'BaseNeuralODE'):
                super().__init__()
                self.parent = parent

            def forward(self, time: torch.Tensor, state: torch.Tensor) -> torch.Tensor:
                # state: (batch, output_dim). Map to input_dim for network
                if state.dim() == 1:
                    state = state.unsqueeze(0)
                batch_size, out_dim = state.shape
                if self.parent.input_dim <= out_dim:
                    ode_input = state[:, : self.parent.input_dim]
                else:
                    ode_input = torch.zeros(
                        batch_size, self.parent.input_dim, device=state.device, dtype=state.dtype
                    )
                    ode_input[:, : out_dim] = state
                deriv = self.parent.ode_func(time, ode_input)
                # Ensure derivative matches state shape (batch, output_dim)
                if deriv.dim() == 1:
                    deriv = deriv.unsqueeze(0)
                if deriv.shape[1] > self.parent.output_dim:
                    deriv = deriv[:, : self.parent.output_dim]
                elif deriv.shape[1] < self.parent.output_dim:
                    padded = torch.zeros(
                        batch_size, self.parent.output_dim, device=deriv.device, dtype=deriv.dtype
                    )
                    padded[:, : deriv.shape[1]] = deriv
                    deriv = padded
                return deriv

        func_module = _ODEFunc(self)
        # Local import to ensure symbol is available
        import torchdiffeq as _tde

        solution = _tde.odeint_adjoint(
            func_module,
            y0,
            t_vec,
            rtol=self.rtol,
            atol=self.atol,
            method=self.solver if self.solver != "euler" else None,
        )

        # torchdiffeq returns (time_steps, batch, dim). Convert to (batch, time, dim)
        if solution.dim() == 3:
            solution = solution.permute(1, 0, 2).contiguous()
        return solution

    def _solve_basic(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Solve ODE using basic numerical methods."""
        batch_size, time_steps = t.shape
        solution = torch.zeros(batch_size, time_steps,
                               self.output_dim, device=x.device)

        # Handle input shape properly
        if len(x.shape) == 2:
            # x has shape (batch_size, input_dim), need to preserve full input dimensions
            # For the initial condition, we want to preserve both input dimensions
            # but map them to output dimensions
            if self.input_dim >= self.output_dim:
                # Take the first output_dim dimensions from each input
                # dimension
                solution[:, 0, :] = x[:, :self.output_dim]
            else:
                # If input_dim < output_dim, pad with zeros
                solution[:, 0, :x.shape[1]] = x
                solution[:, 0, x.shape[1]:] = 0.0
        else:
            solution[:, 0, :] = x

        # Use Euler method for basic solving
        for i in range(1, time_steps):
            dt = t[:, i] - t[:, i - 1]

            # Get the current state for the ODE function
            # We need to ensure the input has the right shape for the network
            # Shape: (batch_size, output_dim)
            current_state = solution[:, i - 1, :]

            # The network expects input with shape (batch_size, input_dim + 1)
            # We need to map from output_dim back to input_dim for the ODE
            # function
            if current_state.shape[1] > self.input_dim:
                # If output_dim > input_dim, truncate
                ode_input = current_state[:, :self.input_dim]
            else:
                # If output_dim <= input_dim, pad with zeros
                ode_input = torch.zeros(
                    batch_size, self.input_dim, device=x.device)
                ode_input[:, :current_state.shape[1]] = current_state

            # Get derivative from ODE function
            derivative = self.ode_func(t[:, i - 1], ode_input)

            # Ensure derivative has correct shape
            if len(derivative.shape) == 1:
                derivative = derivative.unsqueeze(0)

            # Update solution using Euler method
            # The derivative should have shape (batch_size, output_dim) to
            # match solution
            if derivative.shape[1] == self.output_dim:
                solution[:, i, :] = solution[:, i - 1, :] + \
                    dt.unsqueeze(-1) * derivative
            else:
                # If derivative has different shape, pad or truncate
                if derivative.shape[1] > self.output_dim:
                    solution[:, i, :] = solution[:, i - 1, :] + \
                        dt.unsqueeze(-1) * derivative[:, :self.output_dim]
                else:
                    # Pad with zeros if derivative is smaller
                    solution[:, i, :derivative.shape[1]] = solution[:, i - 1,
                                                                    :derivative.shape[1]] + dt.unsqueeze(-1) * derivative
                    solution[:, i, derivative.shape[1]:] = solution[:, i - 1, derivative.shape[1]:]

        return solution


class NeuralFODE(BaseNeuralODE):
    """
    Neural Fractional ODE implementation.

    This class extends Neural ODEs to fractional calculus,
    learning to represent fractional differential equations.
    """

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int,
                 fractional_order: Union[float, FractionalOrder] = 0.5,
                 num_layers: int = 3, activation: str = "tanh",
                 use_adjoint: bool = True, solver: str = "fractional_euler",
                 rtol: float = 1e-5, atol: float = 1e-5):
        """
        Initialize Neural Fractional ODE.

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden layer dimension
            output_dim: Output dimension
            fractional_order: Fractional order α
            num_layers: Number of hidden layers
            activation: Activation function
            use_adjoint: Whether to use adjoint method
            solver: Fractional ODE solver
            rtol: Relative tolerance
            atol: Absolute tolerance
        """
        super().__init__(input_dim, hidden_dim, output_dim,
                         num_layers, activation, use_adjoint)

        self.alpha = validate_fractional_order(fractional_order)
        self.solver = solver
        self.rtol = rtol
        self.atol = atol

        # Initialize fractional derivative operator (placeholder for now)
        self.fractional_derivative = None

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the neural fractional ODE.

        Args:
            x: Input tensor of shape (batch_size, input_dim)
            t: Time tensor of shape (time_steps,) or (batch_size, time_steps)

        Returns:
            Output tensor of shape (batch_size, time_steps, output_dim)
        """
        batch_size = x.shape[0]

        if len(t.shape) == 1:
            t = t.unsqueeze(0).expand(batch_size, -1)

        # Solve fractional ODE
        solution = self._solve_fractional_ode(x, t)

        return solution

    def _solve_fractional_ode(
            self,
            x: torch.Tensor,
            t: torch.Tensor) -> torch.Tensor:
        """Solve fractional ODE using basic methods."""
        batch_size, time_steps = t.shape
        solution = torch.zeros(batch_size, time_steps,
                               self.output_dim, device=x.device)

        # Handle input shape properly
        if len(x.shape) == 2:
            # x has shape (batch_size, input_dim), need to expand to (batch_size, 1, output_dim)
            # Take first output_dim elements
            solution[:, 0, :] = x[:, :self.output_dim]
        else:
            solution[:, 0, :] = x

        # Use fractional Euler method
        for i in range(1, time_steps):
            dt = t[:, i] - t[:, i - 1]

            # Get the current state for the ODE function
            # We need to ensure the input has the right shape for the network
            # Shape: (batch_size, output_dim)
            current_state = solution[:, i - 1, :]

            # The network expects input with shape (batch_size, input_dim + 1)
            # We need to map from output_dim back to input_dim for the ODE
            # function
            if current_state.shape[1] > self.input_dim:
                # If output_dim > input_dim, truncate
                ode_input = current_state[:, :self.input_dim]
            else:
                # If output_dim <= input_dim, pad with zeros
                ode_input = torch.zeros(
                    batch_size, self.input_dim, device=x.device)
                ode_input[:, :current_state.shape[1]] = current_state

            # Compute fractional derivative approximation
            derivative = self.ode_func(t[:, i - 1], ode_input)

            # Ensure derivative has correct shape
            if len(derivative.shape) == 1:
                derivative = derivative.unsqueeze(0)

            # Fractional Euler update (simplified)
            # In practice, this would use proper fractional calculus
            # Simplified without gamma function
            alpha_factor = torch.pow(dt, self.alpha.alpha)

            # Update solution using fractional Euler method
            # Ensure alpha_factor has the right shape for broadcasting
            # Shape: (batch_size, 1)
            alpha_factor_expanded = alpha_factor.unsqueeze(-1)

            if derivative.shape[1] == self.output_dim:
                solution[:, i, :] = solution[:, i - 1, :] + \
                    alpha_factor_expanded * derivative
            else:
                # If derivative has different shape, pad or truncate
                if derivative.shape[1] > self.output_dim:
                    solution[:, i, :] = solution[:, i - 1, :] + \
                        alpha_factor_expanded * derivative[:, :self.output_dim]
                else:
                    # Pad with zeros if derivative is smaller
                    solution[:, i, :derivative.shape[1]] = solution[:, i - 1,
                                                                    :derivative.shape[1]] + alpha_factor_expanded * derivative
                    solution[:, i, derivative.shape[1]:] = solution[:, i - 1, derivative.shape[1]:]

        return solution

    def get_fractional_order(self) -> float:
        """Get the fractional order."""
        return self.alpha.alpha


class NeuralODETrainer:
    """
    Trainer for Neural ODE models.

    This class provides training infrastructure for neural ODEs
    including loss functions, optimizers, and training loops.
    """

    def __init__(self, model: Union[NeuralODE, NeuralFODE],
                 optimizer: str = "adam", learning_rate: float = 1e-3,
                 loss_function: str = "mse"):
        """
        Initialize Neural ODE trainer.

        Args:
            model: Neural ODE model to train
            optimizer: Optimizer type ("adam", "sgd", "rmsprop")
            learning_rate: Learning rate
            loss_function: Loss function ("mse", "mae", "huber")
        """
        self.model = model
        self.learning_rate = learning_rate
        self.loss_function = loss_function

        # Set up optimizer
        self.optimizer = self._setup_optimizer(optimizer)

        # Set up loss function
        self.criterion = self._setup_loss_function(loss_function)

        # Training history
        self.training_history = {
            "loss": [],
            "val_loss": [],
            "epochs": []
        }

    def _setup_optimizer(self, optimizer_type: str) -> torch.optim.Optimizer:
        """Set up optimizer."""
        if optimizer_type == "adam":
            return torch.optim.Adam(
                self.model.parameters(),
                lr=self.learning_rate)
        elif optimizer_type == "sgd":
            return torch.optim.SGD(
                self.model.parameters(),
                lr=self.learning_rate)
        elif optimizer_type == "rmsprop":
            return torch.optim.RMSprop(
                self.model.parameters(),
                lr=self.learning_rate)
        else:
            return torch.optim.Adam(
                self.model.parameters(),
                lr=self.learning_rate)

    def _setup_loss_function(self, loss_type: str) -> nn.Module:
        """Set up loss function."""
        if loss_type == "mse":
            return nn.MSELoss()
        elif loss_type == "mae":
            return nn.L1Loss()
        elif loss_type == "huber":
            return nn.SmoothL1Loss()
        else:
            return nn.MSELoss()

    def train_step(self, x: torch.Tensor, y_target: torch.Tensor,
                   t: torch.Tensor) -> float:
        """
        Single training step.

        Args:
            x: Input tensor
            y_target: Target tensor
            t: Time tensor

        Returns:
            Loss value
        """
        self.optimizer.zero_grad()

        # Forward pass
        y_pred = self.model(x, t)

        # Compute loss
        loss = self.criterion(y_pred, y_target)

        # Backward pass
        loss.backward()

        # Update parameters
        self.optimizer.step()

        return loss.item()

    def train(self, train_loader: torch.utils.data.DataLoader,
              val_loader: Optional[torch.utils.data.DataLoader] = None,
              num_epochs: int = 100, verbose: bool = True) -> Dict[str, List[float]]:
        """
        Train the model.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader (optional)
            num_epochs: Number of training epochs
            verbose: Whether to print progress

        Returns:
            Training history
        """
        self.model.train()

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            num_batches = 0

            for batch in train_loader:
                if len(batch) == 3:
                    x, y_target, t = batch
                else:
                    x, y_target = batch
                    t = torch.linspace(0, 1, y_target.shape[1])

                loss = self.train_step(x, y_target, t)
                epoch_loss += loss
                num_batches += 1

            avg_loss = epoch_loss / num_batches
            self.training_history["loss"].append(avg_loss)
            self.training_history["epochs"].append(epoch)

            # Validation
            if val_loader is not None:
                val_loss = self._validate(val_loader)
                self.training_history["val_loss"].append(val_loss)

                if verbose:
                    print(f"Epoch {epoch+1}/{num_epochs}, "
                          f"Train Loss: {avg_loss:.6f}, "
                          f"Val Loss: {val_loss:.6f}")
            else:
                if verbose:
                    print(f"Epoch {epoch+1}/{num_epochs}, "
                          f"Train Loss: {avg_loss:.6f}")

        return self.training_history

    def _validate(self, val_loader: torch.utils.data.DataLoader) -> float:
        """Compute validation loss."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                if len(batch) == 3:
                    x, y_target, t = batch
                else:
                    x, y_target = batch
                    t = torch.linspace(0, 1, y_target.shape[1])

                y_pred = self.model(x, t)
                loss = self.criterion(y_pred, y_target)
                total_loss += loss.item()
                num_batches += 1

        self.model.train()
        return total_loss / num_batches


# Factory functions for creating neural ODE models
def create_neural_ode(model_type: str = "standard", **
                      kwargs) -> Union[NeuralODE, NeuralFODE]:
    """
    Factory function to create neural ODE models.

    Args:
        model_type: Type of model ("standard", "fractional")
        **kwargs: Additional arguments for model initialization

    Returns:
        Neural ODE model instance

    Raises:
        ValueError: If model_type is not recognized
    """
    if model_type == "standard":
        return NeuralODE(**kwargs)
    elif model_type == "fractional":
        return NeuralFODE(**kwargs)
    else:
        raise ValueError(
            f"Unknown model type: {model_type}. Must be one of: standard, fractional")


def create_neural_ode_trainer(
        model: Union[NeuralODE, NeuralFODE], **kwargs) -> NeuralODETrainer:
    """
    Factory function to create neural ODE trainer.

    Args:
        model: Neural ODE model
        **kwargs: Additional arguments for trainer initialization

    Returns:
        Neural ODE trainer instance
    """
    return NeuralODETrainer(model, **kwargs)
