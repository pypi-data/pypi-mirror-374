"""
Binomial coefficients for fractional calculus.

This module provides optimized implementations of binomial coefficients,
which are fundamental in the Grünwald-Letnikov definition of fractional derivatives.
"""

import numpy as np
import jax
import jax.numpy as jnp
from numba import jit
from typing import Union
import scipy.special as scipy_special
from .gamma_beta import gamma


class BinomialCoefficients:
    """
    Binomial coefficients implementation with multiple optimization strategies.

    The binomial coefficient is defined as:
    C(n,k) = n! / (k! * (n-k)!) = Γ(n+1) / (Γ(k+1) * Γ(n-k+1))

    For fractional calculus, we need generalized binomial coefficients:
    C(α,k) = Γ(α+1) / (Γ(k+1) * Γ(α-k+1))
    where α can be any real number.
    """

    def __init__(
            self,
            use_jax: bool = False,
            use_numba: bool = True,
            cache_size: int = 1000):
        """
        Initialize binomial coefficients calculator.

        Args:
            use_jax: Whether to use JAX implementation for vectorized operations
            use_numba: Whether to use NUMBA JIT compilation for scalar operations
            cache_size: Size of the cache for frequently used coefficients
        """
        self.use_jax = use_jax
        self.use_numba = use_numba
        self.cache_size = cache_size
        self._cache = {}

        if use_jax:
            self._binomial_jax = jax.jit(self._binomial_jax_impl)

    def compute(
        self,
        n: Union[float, int, np.ndarray, jnp.ndarray],
        k: Union[float, int, np.ndarray, jnp.ndarray],
    ) -> Union[float, np.ndarray, jnp.ndarray]:
        """
        Compute the binomial coefficient C(n,k).

        Args:
            n: Upper parameter (can be fractional)
            k: Lower parameter (integer)

        Returns:
            Binomial coefficient value(s)
        """
        if (
            self.use_jax
            and isinstance(n, (jnp.ndarray, float, int))
            and isinstance(k, (jnp.ndarray, float, int))
        ):
            return self._binomial_jax(n, k)
        elif (
            self.use_numba
            and isinstance(n, (float, int))
            and isinstance(k, (float, int))
        ):
            return self._binomial_numba_scalar(n, k)
        else:
            return self._binomial_scipy(n, k)

    @staticmethod
    def _binomial_scipy(
        n: Union[float, np.ndarray], k: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """SciPy implementation for reference and fallback."""
        return scipy_special.binom(n, k)

    @staticmethod
    @jit(nopython=True)
    def _binomial_numba_scalar(n: float, k: float) -> float:
        """
        NUMBA-optimized binomial coefficient for scalar inputs.

        Uses the gamma function relationship for generalized binomial coefficients.
        """
        # Handle special cases
        if k < 0 or k > n:
            return 0.0
        if k == 0 or k == n:
            return 1.0
        if k == 1 or k == n - 1:
            return n

        # Use gamma function for generalized binomial coefficients
        return gamma(n + 1) / (gamma(k + 1) * gamma(n - k + 1))

    @staticmethod
    def _binomial_jax_impl(n: jnp.ndarray, k: jnp.ndarray) -> jnp.ndarray:
        """
        JAX implementation of binomial coefficient.

        Uses JAX's built-in binomial function for vectorized operations.
        """
        return jax.scipy.special.binom(n, k)

    def compute_fractional(
        self,
        alpha: Union[float, np.ndarray, jnp.ndarray],
        k: Union[int, np.ndarray, jnp.ndarray],
    ) -> Union[float, np.ndarray, jnp.ndarray]:
        """
        Compute the generalized binomial coefficient C(α,k) for fractional α.

        Args:
            alpha: Fractional parameter
            k: Integer parameter

        Returns:
            Generalized binomial coefficient value(s)
        """
        if (
            self.use_jax
            and isinstance(alpha, (jnp.ndarray, float))
            and isinstance(k, (jnp.ndarray, int))
        ):
            return self._binomial_fractional_jax(alpha, k)
        elif (
            self.use_numba
            and isinstance(alpha, (float, int))
            and isinstance(k, (int, float))
        ):
            return self._binomial_fractional_numba_scalar(alpha, k)
        else:
            return self._binomial_fractional_scipy(alpha, k)

    @staticmethod
    def _binomial_fractional_scipy(
        alpha: Union[float, np.ndarray], k: Union[int, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """SciPy implementation for fractional binomial coefficients."""
        return scipy_special.binom(alpha, k)

    @staticmethod
    @jit(nopython=True)
    def _binomial_fractional_numba_scalar(alpha: float, k: int) -> float:
        """
        NUMBA-optimized fractional binomial coefficient for scalar inputs.

        Uses the gamma function relationship for generalized binomial coefficients.
        """
        # Handle special cases
        if k < 0:
            return 0.0
        if k == 0:
            return 1.0
        if k == 1:
            return alpha

        # Use gamma function for generalized binomial coefficients
        return gamma(alpha + 1) / (gamma(k + 1) * gamma(alpha - k + 1))

    @staticmethod
    def _binomial_fractional_jax(
            alpha: jnp.ndarray,
            k: jnp.ndarray) -> jnp.ndarray:
        """
        JAX implementation of fractional binomial coefficient.

        Uses JAX's built-in binomial function for vectorized operations.
        """
        return jax.scipy.special.binom(alpha, k)

    def compute_sequence(self, alpha: float, max_k: int) -> np.ndarray:
        """
        Compute the sequence of binomial coefficients C(α,k) for k = 0, 1, ..., max_k.

        Args:
            alpha: Fractional parameter
            max_k: Maximum value of k

        Returns:
            Array of binomial coefficients [C(α,0), C(α,1), ..., C(α,max_k)]
        """
        if self.use_jax:
            k = jnp.arange(max_k + 1)
            return jax.scipy.special.binom(alpha, k)
        else:
            k = np.arange(max_k + 1)
            return scipy_special.binom(alpha, k)

    def compute_alternating_sequence(
            self, alpha: float, max_k: int) -> np.ndarray:
        """
        Compute the alternating sequence of binomial coefficients (-1)^k * C(α,k).

        Args:
            alpha: Fractional parameter
            max_k: Maximum value of k

        Returns:
            Array of alternating binomial coefficients
        """
        coeffs = self.compute_sequence(alpha, max_k)
        signs = (-1) ** np.arange(max_k + 1)
        return coeffs * signs


class GrunwaldLetnikovCoefficients:
    """
    Specialized binomial coefficients for Grünwald-Letnikov fractional derivatives.

    These coefficients appear in the Grünwald-Letnikov definition:
    D^α f(x) = lim_{h→0} h^(-α) * Σ_{k=0}^∞ (-1)^k * C(α,k) * f(x - kh)
    """

    def __init__(self, use_jax: bool = False, use_numba: bool = True):
        """
        Initialize Grünwald-Letnikov coefficients calculator.

        Args:
            use_jax: Whether to use JAX implementation
            use_numba: Whether to use NUMBA implementation
        """
        self.use_jax = use_jax
        self.use_numba = use_numba
        self.binomial = BinomialCoefficients(
            use_jax=use_jax, use_numba=use_numba)

    def compute_coefficients(self, alpha: float, max_k: int) -> np.ndarray:
        """
        Compute Grünwald-Letnikov coefficients for fractional order α.

        Args:
            alpha: Fractional order
            max_k: Maximum number of coefficients

        Returns:
            Array of coefficients [w_0, w_1, ..., w_max_k]
        """
        if self.use_jax:
            k = jnp.arange(max_k + 1)
            return (-1) ** k * jax.scipy.special.binom(alpha, k)
        else:
            k = np.arange(max_k + 1)
            return (-1) ** k * scipy_special.binom(alpha, k)

    def compute_weighted_coefficients(
        self, alpha: float, max_k: int, h: float
    ) -> np.ndarray:
        """
        Compute weighted Grünwald-Letnikov coefficients with step size h.

        Args:
            alpha: Fractional order
            max_k: Maximum number of coefficients
            h: Step size

        Returns:
            Array of weighted coefficients
        """
        coeffs = self.compute_coefficients(alpha, max_k)
        return coeffs / (h**alpha)


# Note: NUMBA vectorization removed for compatibility
# Use the class methods for optimized computations instead


# Convenience functions
def binomial(
    n: Union[float, np.ndarray, jnp.ndarray],
    k: Union[float, np.ndarray, jnp.ndarray],
    use_jax: bool = False,
    use_numba: bool = True,
) -> Union[float, np.ndarray, jnp.ndarray]:
    """
    Convenience function to compute binomial coefficient.

    Args:
        n: Upper parameter
        k: Lower parameter
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Binomial coefficient value(s)
    """
    binomial_func = BinomialCoefficients(use_jax=use_jax, use_numba=use_numba)
    return binomial_func.compute(n, k)


def binomial_fractional(
    alpha: Union[float, np.ndarray, jnp.ndarray],
    k: Union[int, np.ndarray, jnp.ndarray],
    use_jax: bool = False,
    use_numba: bool = True,
) -> Union[float, np.ndarray, jnp.ndarray]:
    """
    Convenience function to compute fractional binomial coefficient.

    Args:
        alpha: Fractional parameter
        k: Integer parameter
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Fractional binomial coefficient value(s)
    """
    binomial_func = BinomialCoefficients(use_jax=use_jax, use_numba=use_numba)
    return binomial_func.compute_fractional(alpha, k)


def grunwald_letnikov_coefficients(
    alpha: float, max_k: int, use_jax: bool = False, use_numba: bool = True
) -> np.ndarray:
    """
    Convenience function to compute Grünwald-Letnikov coefficients.

    Args:
        alpha: Fractional order
        max_k: Maximum number of coefficients
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Array of Grünwald-Letnikov coefficients
    """
    gl_coeffs = GrunwaldLetnikovCoefficients(
        use_jax=use_jax, use_numba=use_numba)
    return gl_coeffs.compute_coefficients(alpha, max_k)


def grunwald_letnikov_weighted_coefficients(
        alpha: float,
        max_k: int,
        h: float,
        use_jax: bool = False,
        use_numba: bool = True) -> np.ndarray:
    """
    Convenience function to compute weighted Grünwald-Letnikov coefficients.

    Args:
        alpha: Fractional order
        max_k: Maximum number of coefficients
        h: Step size
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Array of weighted Grünwald-Letnikov coefficients
    """
    gl_coeffs = GrunwaldLetnikovCoefficients(
        use_jax=use_jax, use_numba=use_numba)
    return gl_coeffs.compute_weighted_coefficients(alpha, max_k, h)


# Special sequences
def pascal_triangle(
    n: int, use_jax: bool = False, use_numba: bool = True
) -> np.ndarray:
    """
    Generate Pascal's triangle up to row n.

    Args:
        n: Number of rows
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Pascal's triangle as a 2D array
    """
    if use_jax:
        triangle = jnp.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                triangle = triangle.at[i, j].set(jax.scipy.special.binom(i, j))
        return triangle
    else:
        triangle = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                triangle[i, j] = scipy_special.binom(i, j)
        return triangle


def fractional_pascal_triangle(
    alpha: float, n: int, use_jax: bool = False, use_numba: bool = True
) -> np.ndarray:
    """
    Generate fractional Pascal's triangle for parameter α up to row n.

    Args:
        alpha: Fractional parameter
        n: Number of rows
        use_jax: Whether to use JAX implementation
        use_numba: Whether to use NUMBA implementation

    Returns:
        Fractional Pascal's triangle as a 2D array
    """
    if use_jax:
        triangle = jnp.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                triangle = triangle.at[i, j].set(
                    jax.scipy.special.binom(alpha + i, j))
        return triangle
    else:
        triangle = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                triangle[i, j] = scipy_special.binom(alpha + i, j)
        return triangle
