"""
Fractional derivative and integral implementations.

This module provides concrete implementations of fractional derivatives
and integrals that can be registered with the factory.
"""

import numpy as np
from typing import Union, Callable, Tuple, List, Dict, Any
from .derivatives import BaseFractionalDerivative
from .definitions import FractionalOrder, DefinitionType


class RiemannLiouvilleDerivative(BaseFractionalDerivative):
    """
    Riemann-Liouville fractional derivative implementation.

    Uses the optimized implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.optimized_methods import OptimizedRiemannLiouville
        self._optimized_impl = OptimizedRiemannLiouville(alpha)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Riemann-Liouville fractional derivative."""
        return self._optimized_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the derivative numerically from function values."""
        return self._optimized_impl.compute(f_values, x_values, **kwargs)


class CaputoDerivative(BaseFractionalDerivative):
    """
    Caputo fractional derivative implementation.

    Uses the optimized implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.optimized_methods import OptimizedCaputo
        self._optimized_impl = OptimizedCaputo(alpha)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Caputo fractional derivative."""
        return self._optimized_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the derivative numerically from function values."""
        return self._optimized_impl.compute(f_values, x_values, **kwargs)


class GrunwaldLetnikovDerivative(BaseFractionalDerivative):
    """
    Grunwald-Letnikov fractional derivative implementation.

    Uses the optimized implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.optimized_methods import OptimizedGrunwaldLetnikov
        self._optimized_impl = OptimizedGrunwaldLetnikov(alpha)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Grunwald-Letnikov fractional derivative."""
        return self._optimized_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the derivative numerically from function values."""
        return self._optimized_impl.compute(f_values, x_values, **kwargs)


class CaputoFabrizioDerivative(BaseFractionalDerivative):
    """
    Caputo-Fabrizio fractional derivative implementation.

    Uses the novel implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.novel_derivatives import CaputoFabrizioDerivative as CFDerivative
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._novel_impl = CFDerivative(alpha, **filtered_kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Caputo-Fabrizio fractional derivative."""
        if isinstance(x, (int, float)):
            x = np.array([x])
        elif isinstance(x, np.ndarray) and x.ndim == 0:
            x = np.array([x])

        result = self._novel_impl.compute(f, x, **kwargs)

        # Return scalar if input was scalar
        if isinstance(
            x, (int, float)) or (
            isinstance(
                x, np.ndarray) and x.size == 1):
            return result[0] if isinstance(result, np.ndarray) else result
        return result

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the derivative numerically from function values."""
        return self._novel_impl.compute(f_values, x_values, **kwargs)


class AtanganaBaleanuDerivative(BaseFractionalDerivative):
    """
    Atangana-Baleanu fractional derivative implementation.

    Uses the novel implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.novel_derivatives import AtanganaBaleanuDerivative as ABDerivative
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._novel_impl = ABDerivative(alpha, **filtered_kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Atangana-Baleanu fractional derivative."""
        if isinstance(x, (int, float)):
            x = np.array([x])
        elif isinstance(x, np.ndarray) and x.ndim == 0:
            x = np.array([x])

        result = self._novel_impl.compute(f, x, **kwargs)

        # Return scalar if input was scalar
        if isinstance(
            x, (int, float)) or (
            isinstance(
                x, np.ndarray) and x.size == 1):
            return result[0] if isinstance(result, np.ndarray) else result
        return result

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the derivative numerically from function values."""
        return self._novel_impl.compute(f_values, x_values, **kwargs)


class FractionalLaplacian(BaseFractionalDerivative):
    """
    Fractional Laplacian operator implementation.

    Uses the special implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.special_methods import FractionalLaplacian as FracLaplacian
        self._special_impl = FracLaplacian(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the fractional Laplacian."""
        return self._special_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the fractional Laplacian numerically from function values."""
        return self._special_impl.compute_numerical(
            f_values, x_values, **kwargs)


class FractionalFourierTransform(BaseFractionalDerivative):
    """
    Fractional Fourier Transform implementation.

    Uses the special implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.special_methods import FractionalFourierTransform as FracFT
        self._special_impl = FracFT(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the fractional Fourier transform."""
        return self._special_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the fractional Fourier transform numerically from function values."""
        return self._special_impl.compute_numerical(
            f_values, x_values, **kwargs)


class FractionalLaplacian(BaseFractionalDerivative):
    """
    Fractional Laplacian operator implementation.

    Uses the special implementation from algorithms.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.special_methods import FractionalLaplacian as FracLaplacian
        self._special_impl = FracLaplacian(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the fractional Laplacian."""
        return self._special_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the fractional Laplacian numerically from function values."""
        return self._special_impl.compute_numerical(
            f_values, x_values, **kwargs)


class MillerRossDerivative(BaseFractionalDerivative):
    """
    Miller-Ross fractional derivative implementation.

    This is a generalization of the Riemann-Liouville derivative.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Miller-Ross fractional derivative."""
        # For now, use Riemann-Liouville as approximation
        # This can be enhanced with specific Miller-Ross implementation
        from .fractional_implementations import RiemannLiouvilleDerivative
        rl_derivative = RiemannLiouvilleDerivative(self.alpha)
        return rl_derivative.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Miller-Ross fractional derivative numerically."""
        from .fractional_implementations import RiemannLiouvilleDerivative
        rl_derivative = RiemannLiouvilleDerivative(self.alpha)
        return rl_derivative.compute_numerical(f_values, x_values, **kwargs)


class WeylDerivative(BaseFractionalDerivative):
    """
    Weyl fractional derivative implementation.

    Uses the advanced implementation from algorithms with FFT convolution
    and parallel processing optimizations.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.advanced_methods import WeylDerivative as AdvancedWeyl
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._advanced_impl = AdvancedWeyl(alpha, **filtered_kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Weyl fractional derivative using advanced methods."""
        return self._advanced_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Weyl fractional derivative numerically using advanced methods."""
        return self._advanced_impl.compute(f_values, x_values, **kwargs)


class MarchaudDerivative(BaseFractionalDerivative):
    """
    Marchaud fractional derivative implementation.

    Uses the advanced implementation from algorithms with difference quotient
    convolution and memory optimization.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.advanced_methods import MarchaudDerivative as AdvancedMarchaud
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._advanced_impl = AdvancedMarchaud(alpha, **filtered_kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Marchaud fractional derivative using advanced methods."""
        return self._advanced_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Marchaud fractional derivative numerically using advanced methods."""
        return self._advanced_impl.compute(f_values, x_values, **kwargs)


class HadamardDerivative(BaseFractionalDerivative):
    """
    Hadamard fractional derivative implementation.

    Uses the advanced implementation from algorithms with logarithmic kernels.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.advanced_methods import HadamardDerivative as AdvancedHadamard
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._advanced_impl = AdvancedHadamard(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Hadamard fractional derivative using advanced methods."""
        return self._advanced_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Hadamard fractional derivative numerically using advanced methods."""
        return self._advanced_impl.compute(f_values, x_values, **kwargs)


class ReizFellerDerivative(BaseFractionalDerivative):
    """
    Reiz-Feller fractional derivative implementation.

    Uses the advanced implementation from algorithms with spectral methods.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.advanced_methods import ReizFellerDerivative as AdvancedReizFeller
        self._advanced_impl = AdvancedReizFeller(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Reiz-Feller fractional derivative using advanced methods."""
        return self._advanced_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Reiz-Feller fractional derivative numerically using advanced methods."""
        return self._advanced_impl.compute(f_values, x_values, **kwargs)


class ParallelOptimizedRiemannLiouville(BaseFractionalDerivative):
    """
    Parallel-optimized Riemann-Liouville fractional derivative.

    Uses parallel processing and load balancing for high-performance computation.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.parallel_optimized_methods import ParallelOptimizedRiemannLiouville as ParallelRL
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._parallel_impl = ParallelRL(alpha, **filtered_kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the parallel-optimized Riemann-Liouville derivative."""
        return self._parallel_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the parallel-optimized Riemann-Liouville derivative numerically."""
        return self._parallel_impl.compute_numerical(
            f_values, x_values, **kwargs)


class ParallelOptimizedCaputo(BaseFractionalDerivative):
    """
    Parallel-optimized Caputo fractional derivative.

    Uses parallel processing and load balancing for high-performance computation.
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        super().__init__(alpha, **kwargs)
        # Lazy import to avoid circular dependencies
        from ..algorithms.parallel_optimized_methods import ParallelOptimizedCaputo as ParallelCaputo
        # Filter out factory-specific arguments
        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['use_jax', 'use_numba']}
        self._parallel_impl = ParallelCaputo(alpha, **kwargs)

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the parallel-optimized Caputo derivative."""
        return self._parallel_impl.compute(f, x, **kwargs)

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the parallel-optimized Caputo derivative numerically."""
        return self._parallel_impl.compute_numerical(
            f_values, x_values, **kwargs)


class RieszFisherOperator(BaseFractionalDerivative):
    """
    Riesz-Fisher fractional operator implementation.

    The Riesz-Fisher operator is a combination of left and right fractional
    derivatives/integrals that is particularly useful in signal processing
    and image analysis. It's defined as:

    R^α f(x) = (1/2) * [D^α_+ f(x) + D^α_- f(x)]

    where D^α_+ is the left-sided and D^α_- is the right-sided operator.

    For α > 0: acts as a derivative
    For α < 0: acts as an integral
    For α = 0: acts as identity
    """

    def __init__(self, alpha: Union[float, FractionalOrder], **kwargs):
        # Handle negative orders by bypassing the base class validation
        if isinstance(alpha, (int, float)):
            self.alpha = FractionalOrder(alpha, validate=False)
        else:
            self.alpha = alpha

        # Store the original alpha value for internal logic
        self._original_alpha = alpha if isinstance(
            alpha, (int, float)) else alpha.alpha

        self._use_derivative = self._original_alpha > 0
        self._use_integral = self._original_alpha < 0

        # Initialize the underlying operators
        if self._use_derivative:
            from .fractional_implementations import RiemannLiouvilleDerivative
            self._left_op = RiemannLiouvilleDerivative(
                abs(self._original_alpha))
            self._right_op = RiemannLiouvilleDerivative(
                abs(self._original_alpha))
        elif self._use_integral:
            from .fractional_implementations import create_fractional_integral
            self._left_op = create_fractional_integral(
                "RL", abs(self._original_alpha))
            self._right_op = create_fractional_integral(
                "RL", abs(self._original_alpha))
        else:
            # α = 0, identity operator
            self._left_op = None
            self._right_op = None

    def compute(self,
                f: Callable,
                x: Union[float,
                         np.ndarray],
                **kwargs) -> Union[float,
                                   np.ndarray]:
        """Compute the Riesz-Fisher fractional operator."""
        if self._original_alpha == 0:
            # Identity operator
            if callable(f):
                return f(x)
            else:
                return f

        # For α ≠ 0, compute left and right operators
        if self._use_derivative:
            left_result = self._left_op.compute(f, x, **kwargs)
            right_result = self._right_op.compute(f, x, **kwargs)
        else:  # self._use_integral
            left_result = self._left_op(f, x)
            right_result = self._right_op(f, x)

        # Combine results
        result = 0.5 * (left_result + right_result)
        return result

    def compute_numerical(
            self,
            f_values: np.ndarray,
            x_values: np.ndarray,
            **kwargs) -> np.ndarray:
        """Compute the Riesz-Fisher fractional operator numerically."""
        if self._original_alpha == 0:
            # Identity operator
            return f_values

        # For α ≠ 0, compute left and right operators
        if self._use_derivative:
            left_result = self._left_op.compute_numerical(
                f_values, x_values, **kwargs)
            right_result = self._right_op.compute_numerical(
                f_values, x_values, **kwargs)
        else:  # self._use_integral
            # For integrals, we need to handle the array input differently
            # This is a simplified approach - in practice, you might want more sophisticated
            # handling of the integral computation from arrays
            left_result = np.zeros_like(f_values)
            right_result = np.zeros_like(f_values)

            for i, xi in enumerate(x_values):
                # Create a function that interpolates the array values
                def f_interp(t):
                    # Simple linear interpolation
                    if t <= x_values[0]:
                        return f_values[0]
                    elif t >= x_values[-1]:
                        return f_values[-1]
                    else:
                        # Find the interval and interpolate
                        for j in range(len(x_values) - 1):
                            if x_values[j] <= t <= x_values[j + 1]:
                                t1, t2 = x_values[j], x_values[j + 1]
                                f1, f2 = f_values[j], f_values[j + 1]
                                return f1 + (f2 - f1) * (t - t1) / (t2 - t1)
                        return f_values[-1]  # fallback

                left_result[i] = self._left_op(f_interp, xi)
                right_result[i] = self._right_op(f_interp, xi)

        # Combine results
        result = 0.5 * (left_result + right_result)
        return result

    def __repr__(self):
        """String representation of the Riesz-Fisher operator."""
        return f"RieszFisherOperator(alpha={self.alpha.alpha})"


class AdomianDecompositionMethod:
    """
    Adomian Decomposition Method for solving fractional differential equations.

    This is an analytical method that decomposes the solution into a series
    of components that can be computed iteratively.
    """

    def __init__(self, max_terms: int = 10, tolerance: float = 1e-6):
        """
        Initialize the Adomian Decomposition Method.

        Args:
            max_terms: Maximum number of terms to compute
            tolerance: Convergence tolerance
        """
        self.max_terms = max_terms
        self.tolerance = tolerance

    def solve(self, equation: Callable, initial_condition: Callable,
              domain: Union[Tuple[float, float], np.ndarray], **kwargs) -> Dict[str, Any]:
        """
        Solve a fractional differential equation using Adomian decomposition.

        Args:
            equation: The fractional differential equation
            initial_condition: Initial condition function
            domain: Solution domain or array of points
            **kwargs: Additional parameters

        Returns:
            Solution dictionary with components and convergence info
        """
        # Lazy import to avoid circular dependencies
        from ..algorithms.advanced_methods import AdomianDecomposition
        adomian_solver = AdomianDecomposition(
            max_terms=self.max_terms, tolerance=self.tolerance)
        return adomian_solver.solve(
            equation, initial_condition, domain, **kwargs)

    def compute_adomian_polynomials(
            self,
            nonlinear_term: Callable,
            u_series: List[Callable],
            order: int) -> List[Callable]:
        """
        Compute Adomian polynomials for nonlinear terms.

        Args:
            nonlinear_term: The nonlinear term in the equation
            u_series: Series of solution components
            order: Order of the polynomial to compute

        Returns:
            List of Adomian polynomial functions
        """
        from ..algorithms.advanced_methods import AdomianDecomposition
        adomian_solver = AdomianDecomposition(
            max_terms=self.max_terms, tolerance=self.tolerance)
        return adomian_solver.compute_adomian_polynomials(
            nonlinear_term, u_series, order)


def create_fractional_integral(
        method: str, alpha: Union[float, FractionalOrder], **kwargs):
    """
    Create a fractional integral implementation.

    Args:
        method: Integration method ("RL" for Riemann-Liouville)
        alpha: Fractional order
        **kwargs: Additional parameters

    Returns:
        Fractional integral implementation
    """
    from .integrals import create_fractional_integral as create_integral
    return create_integral(method, alpha, **kwargs)


def create_riesz_fisher_operator(
        alpha: Union[float, FractionalOrder], **kwargs):
    """
    Create a Riesz-Fisher fractional operator.

    Args:
        alpha: Fractional order
            - α > 0: acts as a derivative
            - α < 0: acts as an integral
            - α = 0: acts as identity
        **kwargs: Additional parameters

    Returns:
        RieszFisherOperator instance
    """
    return RieszFisherOperator(alpha, **kwargs)


def register_fractional_implementations():
    """
    Register all fractional derivative implementations with the factory.

    This function should be called during package initialization.
    """
    from .derivatives import derivative_factory

    # Register derivative implementations
    derivative_factory.register_implementation(
        DefinitionType.RIEMANN_LIOUVILLE,
        RiemannLiouvilleDerivative
    )
    derivative_factory.register_implementation(
        DefinitionType.CAPUTO,
        CaputoDerivative
    )
    derivative_factory.register_implementation(
        DefinitionType.GRUNWALD_LETNIKOV,
        GrunwaldLetnikovDerivative
    )

    # Register novel derivative implementations
    derivative_factory.register_implementation(
        "caputo_fabrizio",
        CaputoFabrizioDerivative
    )
    derivative_factory.register_implementation(
        "atangana_baleanu",
        AtanganaBaleanuDerivative
    )

    # Register special derivative implementations
    derivative_factory.register_implementation(
        "fractional_laplacian",
        FractionalLaplacian
    )
    derivative_factory.register_implementation(
        "fractional_fourier_transform",
        FractionalFourierTransform
    )

    # Register additional derivative implementations
    derivative_factory.register_implementation(
        DefinitionType.MILLER_ROSS,
        MillerRossDerivative
    )
    derivative_factory.register_implementation(
        DefinitionType.WEYL,
        WeylDerivative
    )
    derivative_factory.register_implementation(
        DefinitionType.MARCHAUD,
        MarchaudDerivative
    )

    # Register advanced methods
    derivative_factory.register_implementation(
        "hadamard",
        HadamardDerivative
    )
    derivative_factory.register_implementation(
        "reiz_feller",
        ReizFellerDerivative
    )

    # Register parallel-optimized methods
    derivative_factory.register_implementation(
        "parallel_riemann_liouville",
        ParallelOptimizedRiemannLiouville
    )
    derivative_factory.register_implementation(
        "parallel_caputo",
        ParallelOptimizedCaputo
    )

    # Register special operators
    derivative_factory.register_implementation(
        "riesz_fisher",
        RieszFisherOperator
    )

    print("Fractional derivative implementations registered successfully!")


# Auto-register implementations when module is imported
try:
    register_fractional_implementations()
except Exception as e:
    print(f"Auto-registration failed: {e}")
