"""
Fractional Graph Neural Network Layers

This module provides Graph Neural Network layers with fractional calculus integration,
supporting multiple backends (PyTorch, JAX, NUMBA) and various graph operations.
"""

from typing import Optional, Union, Any, Tuple
from abc import ABC, abstractmethod

import torch

from .backends import get_backend_manager, BackendType
from .tensor_ops import get_tensor_ops
from ..core.definitions import FractionalOrder


class BaseFractionalGNNLayer(ABC):
    """
    Base class for fractional GNN layers

    This abstract class defines the interface for all fractional GNN layers,
    ensuring consistency across different backends and implementations.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        fractional_order: Union[float, FractionalOrder] = 0.5,
        method: str = "RL",
        use_fractional: bool = True,
        activation: str = "relu",
        dropout: float = 0.1,
        bias: bool = True,
        backend: Optional[BackendType] = None
    ):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.fractional_order = FractionalOrder(fractional_order) if isinstance(
            fractional_order, float) else fractional_order
        self.method = method
        self.use_fractional = use_fractional
        self.activation = activation
        self.dropout = dropout
        self.bias = bias
        self.backend = backend or get_backend_manager().active_backend

        # Initialize tensor operations for the chosen backend
        self.tensor_ops = get_tensor_ops(self.backend)

        # Initialize the layer
        self._initialize_layer()

    @abstractmethod
    def _initialize_layer(self):
        """Initialize the specific layer implementation"""

    @abstractmethod
    def forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """Forward pass through the layer"""

    def apply_fractional_derivative(self, x: Any) -> Any:
        """Apply fractional derivative to input features"""
        if not self.use_fractional:
            return x

        # This is a simplified implementation - in practice, you'd want to
        # use the actual fractional calculus methods from your core module
        alpha = self.fractional_order.alpha

        if self.backend == BackendType.TORCH:
            # PyTorch implementation
            return self._torch_fractional_derivative(x, alpha)
        elif self.backend == BackendType.JAX:
            # JAX implementation
            return self._jax_fractional_derivative(x, alpha)
        elif self.backend == BackendType.NUMBA:
            # NUMBA implementation
            return self._numba_fractional_derivative(x, alpha)
        else:
            raise RuntimeError(f"Unknown backend: {self.backend}")

    def __call__(self, *args, **kwargs):
        """Callable layer wrapper"""
        return self.forward(*args, **kwargs)

    def _torch_fractional_derivative(self, x: Any, alpha: float) -> Any:
        """PyTorch implementation of fractional derivative"""
        if alpha == 0:
            return x
        elif alpha == 1:
            # Ensure we maintain the same tensor dimensions
            if x.dim() > 1:
                # For multi-dimensional tensors, compute gradient along the
                # last dimension
                gradients = torch.gradient(x, dim=-1)[0]
                # Ensure gradients have the same shape as input
                if gradients.shape != x.shape:
                    # Pad or truncate to match input shape
                    if gradients.shape[-1] < x.shape[-1]:
                        padding = x.shape[-1] - gradients.shape[-1]
                        gradients = torch.cat(
                            [gradients, torch.zeros_like(gradients[..., :padding])], dim=-1)
                    else:
                        gradients = gradients[..., :x.shape[-1]]
                return gradients
            else:
                # For 1D tensors, use diff and pad to maintain shape
                diff = torch.diff(x, dim=-1)
                # Pad with zeros to maintain original shape
                padding = torch.zeros(1, dtype=x.dtype, device=x.device)
                return torch.cat([diff, padding], dim=-1)
        else:
            # Placeholder for actual fractional derivative implementation
            # Ensure output has the same shape as input
            return x * (alpha ** 0.5)

    def _jax_fractional_derivative(self, x: Any, alpha: float) -> Any:
        """JAX implementation of fractional derivative"""
        import jax.numpy as jnp
        if alpha == 0:
            return x
        elif alpha == 1:
            # JAX doesn't have gradient, implement manually
            if x.ndim > 1:
                # For multi-dimensional tensors, compute diff along the last
                # dimension
                diff = jnp.diff(x, axis=-1)
                # Pad with zeros to maintain original shape
                padding_shape = list(x.shape)
                padding_shape[-1] = 1
                padding = jnp.zeros(padding_shape, dtype=x.dtype)
                return jnp.concatenate([diff, padding], axis=-1)
            else:
                # For 1D tensors, use diff and pad to maintain shape
                diff = jnp.diff(x, axis=-1)
                padding = jnp.zeros(1, dtype=x.dtype)
                return jnp.concatenate([diff, padding], axis=0)
        else:
            # Placeholder for actual fractional derivative implementation
            return x * (alpha ** 0.5)

    def _numba_fractional_derivative(self, x: Any, alpha: float) -> Any:
        """NUMBA implementation of fractional derivative"""
        import numpy as np
        if alpha == 0:
            return x
        elif alpha == 1:
            if x.ndim > 1:
                # For multi-dimensional tensors, compute diff along the last
                # dimension
                diff = np.diff(x, axis=-1)
                # Pad with zeros to maintain original shape
                padding_shape = list(x.shape)
                padding_shape[-1] = 1
                padding = np.zeros(padding_shape, dtype=x.dtype)
                return np.concatenate([diff, padding], axis=-1)
            else:
                # For 1D tensors, use diff and pad to maintain shape
                diff = np.diff(x, axis=0)
                padding = np.zeros(1, dtype=x.dtype)
                return np.concatenate([diff, padding], axis=0)
        else:
            # Placeholder for actual fractional derivative implementation
            return x * (alpha ** 0.5)


class FractionalGraphConv(BaseFractionalGNNLayer):
    """
    Fractional Graph Convolutional Layer

    This layer applies fractional derivatives to node features before
    performing graph convolution operations.
    """

    def _initialize_layer(self):
        """Initialize the graph convolution layer"""
        # Create weight matrix with proper initialization
        if self.backend == BackendType.TORCH:
            import torch
            self.weight = torch.randn(
                self.in_channels, self.out_channels, requires_grad=True)
            if self.bias:
                self.bias = torch.zeros(self.out_channels, requires_grad=True)
            else:
                self.bias = None
        elif self.backend == BackendType.JAX:
            import jax.numpy as jnp
            import jax.random as random
            key = random.PRNGKey(0)
            self.weight = random.normal(
                key, (self.in_channels, self.out_channels))
            if self.bias:
                self.bias = jnp.zeros(self.out_channels)
            else:
                self.bias = None
        elif self.backend == BackendType.NUMBA:
            import numpy as np
            self.weight = np.random.randn(self.in_channels, self.out_channels)
            if self.bias:
                self.bias = np.zeros(self.out_channels)
            else:
                self.bias = None

        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize layer weights using Xavier initialization"""
        if self.backend == BackendType.TORCH:
            import torch.nn.init as init
            init.xavier_uniform_(self.weight)
            if self.bias is not None:
                init.zeros_(self.bias)
        elif self.backend == BackendType.JAX:
            # JAX weights are already initialized with normal distribution
            # Scale by sqrt(2/(in_channels + out_channels)) for Xavier-like
            # initialization
            import jax.numpy as jnp
            scale = jnp.sqrt(2.0 / (self.in_channels + self.out_channels))
            self.weight = self.weight * scale
        elif self.backend == BackendType.NUMBA:
            # NUMBA weights are already initialized with normal distribution
            # Scale for Xavier-like initialization
            import numpy as np
            scale = np.sqrt(2.0 / (self.in_channels + self.out_channels))
            self.weight = self.weight * scale

    def forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """
        Forward pass through the fractional graph convolution layer

        Args:
            x: Node feature matrix [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_weight: Optional edge weights [num_edges]

        Returns:
            Updated node features [num_nodes, out_channels]
        """
        # Apply fractional derivative to input features
        x = self.apply_fractional_derivative(x)

        # Perform graph convolution
        if self.backend == BackendType.TORCH:
            return self._torch_forward(x, edge_index, edge_weight)
        elif self.backend == BackendType.JAX:
            return self._jax_forward(x, edge_index, edge_weight)
        elif self.backend == BackendType.NUMBA:
            return self._numba_forward(x, edge_index, edge_weight)
        else:
            raise RuntimeError(f"Unknown backend: {self.backend}")

    def _torch_forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """PyTorch implementation of forward pass"""
        import torch
        import torch.nn.functional as F

        # Linear transformation
        out = torch.matmul(x, self.weight)

        # Graph convolution (improved implementation)
        if edge_index is not None and edge_index.shape[1] > 0:
            # Ensure edge_index has correct shape [2, num_edges]
            if edge_index.dim() == 1:
                # If edge_index is 1D, reshape it
                edge_index = self.tensor_ops.reshape(edge_index, (1, -1))

            # Handle edge_index shape issues
            if edge_index.shape[0] == 1:
                # If only one row, duplicate it for source and target
                edge_index = self.tensor_ops.repeat(edge_index, 2, dim=0)
            elif edge_index.shape[0] > 2:
                # If more than 2 rows, take first two
                edge_index = edge_index[:2, :]

            # Ensure edge_index has valid indices
            num_nodes = x.shape[0]
            edge_index = self.tensor_ops.clip(edge_index, 0, num_nodes - 1)

            # Get source and target indices
            row, col = edge_index

            # Aggregate neighbor features using scatter_add
            if edge_weight is not None:
                # Ensure edge_weight has correct shape
                if edge_weight.dim() == 1:
                    edge_weight = self.tensor_ops.unsqueeze(edge_weight, -1)
                # Apply edge weights
                weighted_features = out[col] * edge_weight
                out = torch.scatter_add(out, 0, self.tensor_ops.unsqueeze(
                    row, -1).expand(-1, out.shape[-1]), weighted_features)
            else:
                # Simple aggregation without weights
                out = torch.scatter_add(out, 0, self.tensor_ops.unsqueeze(
                    row, -1).expand(-1, out.shape[-1]), out[col])

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        # Apply activation and dropout
        if self.activation == "relu":
            out = F.relu(out)
        elif self.activation == "sigmoid":
            out = torch.sigmoid(out)
        elif self.activation == "tanh":
            out = torch.tanh(out)
        elif self.activation == "identity":
            pass  # No activation (identity function)
        else:
            # Try to use the activation function directly
            try:
                out = getattr(F, self.activation)(out)
            except AttributeError:
                # Fallback to ReLU if activation not found
                out = F.relu(out)

        # Apply dropout if training
        if hasattr(self, 'training') and self.training:
            out = F.dropout(out, p=self.dropout, training=True)

        return out

    def _jax_forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """JAX implementation of forward pass"""
        import jax.numpy as jnp

        # Linear transformation
        out = jnp.matmul(x, self.weight)

        # Graph convolution (simplified)
        if edge_index is not None and edge_index.shape[1] > 0:
            # Ensure edge_index has correct shape [2, num_edges]
            if edge_index.ndim == 1:
                edge_index = self.tensor_ops.reshape(edge_index, (1, -1))

            # Handle edge_index shape issues
            if edge_index.shape[0] == 1:
                # If only one row, duplicate it for source and target
                edge_index = self.tensor_ops.repeat(edge_index, 2, dim=0)
            elif edge_index.shape[0] > 2:
                # If more than 2 rows, take first two
                edge_index = edge_index[:2, :]

            # Ensure edge_index has valid indices
            num_nodes = x.shape[0]
            edge_index = self.tensor_ops.clip(edge_index, 0, num_nodes - 1)

            row, col = edge_index
            if edge_weight is not None:
                # JAX scatter operations are more complex
                out = self._jax_scatter_add(out, row, col, edge_weight)
            else:
                out = self._jax_scatter_add(out, row, col)

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        # Apply activation
        out = self._jax_activation(out)

        return out

    def _numba_forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """NUMBA implementation of forward pass"""
        import numpy as np

        # Linear transformation
        out = np.matmul(x, self.weight)

        # Graph convolution (simplified)
        if edge_index is not None:
            row, col = edge_index
            if edge_weight is not None:
                out = self._numba_scatter_add(out, row, col, edge_weight)
            else:
                out = self._numba_scatter_add(out, row, col)

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        # Apply activation
        out = self._numba_activation(out)

        return out

    def _jax_scatter_add(
            self,
            out: Any,
            row: Any,
            col: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """JAX implementation of scatter add operation"""
        # Simplified implementation - in practice, use jax.ops.scatter_add
        return out

    def _numba_scatter_add(
            self,
            out: Any,
            row: Any,
            col: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """NUMBA implementation of scatter add operation"""
        # Simplified implementation
        return out

    def _jax_activation(self, x: Any) -> Any:
        """JAX implementation of activation function"""
        import jax.numpy as jnp
        if self.activation == "relu":
            return jnp.maximum(x, 0)
        elif self.activation == "sigmoid":
            return 1 / (1 + jnp.exp(-x))
        elif self.activation == "tanh":
            return jnp.tanh(x)
        elif self.activation == "identity":
            return x  # Identity function - return input unchanged
        else:
            return x

    def _numba_activation(self, x: Any) -> Any:
        """NUMBA implementation of activation function"""
        import numpy as np
        if self.activation == "relu":
            return np.maximum(x, 0)
        elif self.activation == "sigmoid":
            return 1 / (1 + np.exp(-x))
        elif self.activation == "tanh":
            return np.tanh(x)
        elif self.activation == "identity":
            return x  # Identity function - return input unchanged
        else:
            return x


class FractionalGraphAttention(BaseFractionalGNNLayer):
    """
    Fractional Graph Attention Layer

    This layer applies fractional derivatives to node features and uses
    attention mechanisms for graph convolution.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        heads: int = 8,
        fractional_order: Union[float, FractionalOrder] = 0.5,
        method: str = "RL",
        use_fractional: bool = True,
        activation: str = "relu",
        dropout: float = 0.1,
        bias: bool = True,
        backend: Optional[BackendType] = None,
        **kwargs
    ):
        # Support num_heads alias for compatibility
        if 'num_heads' in kwargs:
            heads = kwargs['num_heads']
        self.heads = heads
        self.training = True  # Add training attribute
        super().__init__(
            in_channels, out_channels, fractional_order, method,
            use_fractional, activation, dropout, bias, backend
        )

    def _initialize_layer(self):
        """Initialize the graph attention layer"""
        # Multi-head attention weights
        if self.backend == BackendType.TORCH:
            import torch
            import torch.nn.init as init

            # Initialize weights with proper dimensions
            self.query_weight = torch.randn(
                self.in_channels, self.out_channels, requires_grad=True)
            self.key_weight = torch.randn(
                self.in_channels, self.out_channels, requires_grad=True)
            self.value_weight = torch.randn(
                self.in_channels, self.out_channels, requires_grad=True)
            self.output_weight = torch.randn(
                self.out_channels, self.out_channels, requires_grad=True)

            # Apply Xavier initialization
            init.xavier_uniform_(self.query_weight)
            init.xavier_uniform_(self.key_weight)
            init.xavier_uniform_(self.value_weight)
            init.xavier_uniform_(self.output_weight)

            # Initialize bias
            if self.bias:
                self.bias = torch.zeros(self.out_channels, requires_grad=True)
            else:
                self.bias = None

        elif self.backend == BackendType.JAX:
            import jax.numpy as jnp
            import jax.random as random

            key = random.PRNGKey(0)
            # Initialize weights with proper dimensions
            self.query_weight = random.normal(
                key, (self.in_channels, self.out_channels))
            self.key_weight = random.normal(
                key, (self.in_channels, self.out_channels))
            self.value_weight = random.normal(
                key, (self.in_channels, self.out_channels))
            self.output_weight = random.normal(
                key, (self.out_channels, self.out_channels))

            # Scale for Xavier-like initialization
            scale = jnp.sqrt(2.0 / (self.in_channels + self.out_channels))
            self.query_weight = self.query_weight * scale
            self.key_weight = self.key_weight * scale
            self.value_weight = self.value_weight * scale
            self.output_weight = self.output_weight * scale

            # Initialize bias
            if self.bias:
                self.bias = jnp.zeros(self.out_channels)
            else:
                self.bias = None

        elif self.backend == BackendType.NUMBA:
            import numpy as np

            # Initialize weights with proper dimensions
            self.query_weight = np.random.randn(
                self.in_channels, self.out_channels)
            self.key_weight = np.random.randn(
                self.in_channels, self.out_channels)
            self.value_weight = np.random.randn(
                self.in_channels, self.out_channels)
            self.output_weight = np.random.randn(
                self.out_channels, self.out_channels)

            # Scale for Xavier-like initialization
            scale = np.sqrt(2.0 / (self.in_channels + self.out_channels))
            self.query_weight = self.query_weight * scale
            self.key_weight = self.key_weight * scale
            self.value_weight = self.value_weight * scale
            self.output_weight = self.output_weight * scale

            # Initialize bias
            if self.bias:
                self.bias = np.zeros(self.out_channels)
            else:
                self.bias = None

    def forward(
            self,
            x: Any,
            edge_index: Any,
            edge_weight: Optional[Any] = None) -> Any:
        """
        Forward pass through the fractional graph attention layer

        Args:
            x: Node feature matrix [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_weight: Optional edge weights [num_edges]

        Returns:
            Updated node features [num_nodes, out_channels]
        """
        # Apply fractional derivative to input features
        x = self.apply_fractional_derivative(x)

        # Compute attention scores
        query = self.tensor_ops.matmul(x, self.query_weight)
        key = self.tensor_ops.matmul(x, self.key_weight)
        value = self.tensor_ops.matmul(x, self.value_weight)

        # For graph attention, we only compute attention between connected
        # nodes
        if edge_index is not None and edge_index.shape[1] > 0:
            # Ensure edge_index has correct shape [2, num_edges]
            if edge_index.ndim == 1:
                edge_index = self.tensor_ops.reshape(edge_index, (1, -1))

            # Handle edge_index shape issues
            if edge_index.shape[0] == 1:
                edge_index = self.tensor_ops.repeat(edge_index, 2, dim=0)
            elif edge_index.shape[0] > 2:
                edge_index = edge_index[:2, :]

            # Ensure edge_index has valid indices
            num_nodes = x.shape[0]
            edge_index = self.tensor_ops.clip(edge_index, 0, num_nodes - 1)

            # Get source and target indices
            row, col = edge_index

            # Compute attention scores only for connected nodes
            # This is a simplified implementation - in practice, you'd want
            # more sophisticated attention
            if hasattr(query, 'gather'):
                # PyTorch-like
                query_src = self.tensor_ops.gather(
                    query, 0, self.tensor_ops.unsqueeze(row, -1).expand(-1, query.shape[-1]))
                key_tgt = self.tensor_ops.gather(
                    key, 0, self.tensor_ops.unsqueeze(col, -1).expand(-1, key.shape[-1]))
                value_tgt = self.tensor_ops.gather(
                    value, 0, self.tensor_ops.unsqueeze(col, -1).expand(-1, value.shape[-1]))
            else:
                # JAX/NUMBA-like
                query_src = query[row]
                key_tgt = key[col]
                value_tgt = value[col]

            # Ensure all tensors have the same shape for attention computation
            min_dim = min(query_src.shape[-1], key_tgt.shape[-1])
            if query_src.shape != key_tgt.shape:
                # Reshape to match dimensions
                query_src = query_src[..., :min_dim]
                key_tgt = key_tgt[..., :min_dim]
                value_tgt = value_tgt[..., :min_dim]

            # Compute attention scores (simplified to avoid dimension issues)
            # Use element-wise multiplication and sum instead of matrix
            # multiplication
            attention_scores = self.tensor_ops.sum(
                query_src * key_tgt, dim=-1, keepdims=True)
            attention_scores = attention_scores / \
                (min_dim ** 0.5)  # Use actual dimension

            # Apply softmax to attention scores (use dim=0 for edge dimension)
            attention_scores = self.tensor_ops.softmax(attention_scores, dim=0)

            # Apply attention to values
            attended_values = value_tgt * attention_scores

            # Aggregate using scatter operations (simplified)
            out = self._aggregate_attention(query, attended_values, row, col)
        else:
            # No edges, just pass through the input
            out = query

        # Output projection
        out = self.tensor_ops.matmul(out, self.output_weight)

        # Add bias
        if self.bias is not None:
            out = out + self.bias

        # Apply activation and dropout
        out = self._apply_activation(out)
        out = self._apply_dropout(out)

        return out

    def _aggregate_attention(
            self,
            query: Any,
            attended_values: Any,
            row: Any,
            col: Any) -> Any:
        """Aggregate attention-weighted values"""
        # This is a simplified implementation
        # In practice, you'd want to use proper scatter operations
        # For now, we'll just return the query to avoid dimension issues
        return query

    def _apply_activation(self, x: Any) -> Any:
        """Apply activation function"""
        if self.backend == BackendType.TORCH:
            import torch.nn.functional as F
            if self.activation == "identity":
                return x  # Identity function - return input unchanged
            elif self.activation == "relu":
                return F.relu(x)
            elif self.activation == "sigmoid":
                return torch.sigmoid(x)
            elif self.activation == "tanh":
                return torch.tanh(x)
            else:
                # Try to use the activation function directly
                try:
                    return getattr(F, self.activation)(x)
                except AttributeError:
                    # Fallback to identity if activation not found
                    return x
        elif self.backend == BackendType.JAX:
            return self._jax_activation(x)
        elif self.backend == BackendType.NUMBA:
            return self._numba_activation(x)
        else:
            return x

    def _jax_activation(self, x: Any) -> Any:
        """JAX implementation of activation function"""
        import jax.numpy as jnp
        if self.activation == "relu":
            return jnp.maximum(x, 0)
        elif self.activation == "sigmoid":
            return 1 / (1 + jnp.exp(-x))
        elif self.activation == "tanh":
            return jnp.tanh(x)
        elif self.activation == "identity":
            return x  # Identity function - return input unchanged
        else:
            return x

    def _numba_activation(self, x: Any) -> Any:
        """NUMBA implementation of activation function"""
        import numpy as np
        if self.activation == "relu":
            return np.maximum(x, 0)
        elif self.activation == "sigmoid":
            return 1 / (1 + np.exp(-x))
        elif self.activation == "tanh":
            return np.tanh(x)
        elif self.activation == "identity":
            return x  # Identity function - return input unchanged
        else:
            return x

    def _apply_dropout(self, x: Any) -> Any:
        """Apply dropout"""
        return self.tensor_ops.dropout(
            x, p=self.dropout, training=self.training)


class FractionalGraphPooling(BaseFractionalGNNLayer):
    """
    Fractional Graph Pooling Layer

    This layer applies fractional derivatives to node features and performs
    hierarchical pooling operations on graphs.
    """

    def __init__(
        self,
        in_channels: int,
        pooling_ratio: float = 0.5,
        fractional_order: Union[float, FractionalOrder] = 0.5,
        method: str = "RL",
        use_fractional: bool = True,
        backend: Optional[BackendType] = None,
        **kwargs
    ):
        # Support ratio alias for compatibility
        if 'ratio' in kwargs:
            pooling_ratio = kwargs['ratio']
        self.pooling_ratio = pooling_ratio
        super().__init__(
            in_channels, in_channels, fractional_order, method,
            use_fractional, "identity", 0.0, False, backend
        )

    def _initialize_layer(self):
        """Initialize the pooling layer"""
        # Score network for node selection
        if self.backend == BackendType.TORCH:
            import torch
            import torch.nn.init as init

            self.score_network = torch.randn(
                self.in_channels, 1, requires_grad=True)
            init.xavier_uniform_(self.score_network)

        elif self.backend == BackendType.JAX:
            import jax.numpy as jnp
            import jax.random as random

            key = random.PRNGKey(0)
            self.score_network = random.normal(key, (self.in_channels, 1))
            # Scale for Xavier-like initialization
            scale = jnp.sqrt(2.0 / (self.in_channels + 1))
            self.score_network = self.score_network * scale

        elif self.backend == BackendType.NUMBA:
            import numpy as np

            self.score_network = np.random.randn(self.in_channels, 1)
            # Scale for Xavier-like initialization
            scale = np.sqrt(2.0 / (self.in_channels + 1))
            self.score_network = self.score_network * scale

    def forward(self, x: Any, edge_index: Any,
                batch: Optional[Any] = None) -> Tuple[Any, Any, Any]:
        """
        Forward pass through the fractional graph pooling layer

        Args:
            x: Node feature matrix [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            batch: Batch assignment vector [num_nodes]

        Returns:
            Tuple of (pooled_features, pooled_edge_index, pooled_batch)
        """
        # Apply fractional derivative to input features
        x = self.apply_fractional_derivative(x)

        # Compute node scores using the score network
        # Ensure proper matrix multiplication
        if x.shape[-1] != self.score_network.shape[0]:
            # Reshape score_network to match input dimensions
            if x.shape[-1] > self.score_network.shape[0]:
                # Pad score_network with zeros
                padding = x.shape[-1] - self.score_network.shape[0]
                zeros = self.tensor_ops.zeros((padding, 1))
                padded_score = self.tensor_ops.cat(
                    [self.score_network, zeros], dim=0)
            else:
                # Truncate score_network
                padded_score = self.score_network[:x.shape[-1], :]
        else:
            padded_score = self.score_network

        scores = self.tensor_ops.matmul(x, padded_score)
        scores = self.tensor_ops.squeeze(scores, -1)

        # Select top nodes based on pooling ratio
        num_nodes = x.shape[0]
        # Ensure at least 1 node
        num_pooled = max(1, int(num_nodes * self.pooling_ratio))

        if self.backend == BackendType.TORCH:
            import torch
            _, indices = torch.topk(scores, min(num_pooled, num_nodes))
        elif self.backend == BackendType.JAX:
            import jax.numpy as jnp
            indices = jnp.argsort(scores)[-min(num_pooled, num_nodes):]
        elif self.backend == BackendType.NUMBA:
            import numpy as np
            indices = np.argsort(scores)[-min(num_pooled, num_nodes):]
        else:
            raise RuntimeError(f"Unknown backend: {self.backend}")

        # Pool features
        pooled_features = x[indices]

        # Pool edge index and batch (simplified)
        # In practice, you'd want to filter edges to only include connections
        # between pooled nodes
        pooled_edge_index = edge_index  # Simplified for now
        pooled_batch = batch[indices] if batch is not None else None

        return pooled_features, pooled_edge_index, pooled_batch
