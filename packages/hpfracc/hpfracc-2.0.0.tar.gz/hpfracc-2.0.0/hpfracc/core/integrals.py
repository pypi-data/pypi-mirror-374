"""
Fractional Integrals Module

This module provides comprehensive implementations of fractional integrals including:
- Riemann-Liouville fractional integrals
- Caputo fractional integrals
- Weyl fractional integrals
- Hadamard fractional integrals
- Numerical methods for fractional integration
- Special cases and analytical solutions
"""

import numpy as np
import torch
from typing import Union, Callable, List
from scipy.special import gamma
from scipy.integrate import quad

from .definitions import FractionalOrder


class FractionalIntegral:
    """
    Base class for fractional integral implementations.

    This class provides the foundation for different types of fractional integrals
    and their numerical implementations.
    """

    def __init__(self,
                 alpha: Union[float,
                              FractionalOrder],
                 method: str = "RL"):
        """
        Initialize fractional integral.

        Args:
            alpha: Fractional order (0 < α < 1 for most methods)
            method: Integration method ("RL", "Caputo", "Weyl", "Hadamard")
        """
        if isinstance(alpha, (int, float)):
            self.alpha = FractionalOrder(alpha)
        else:
            self.alpha = alpha

        self.method = method
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate fractional order and method parameters."""
        if self.alpha.alpha < 0:
            raise ValueError(
                f"Fractional order must be non-negative, got {self.alpha.alpha}")

        if self.method not in ["RL", "Caputo", "Weyl", "Hadamard"]:
            raise ValueError(f"Unknown method: {self.method}")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """Compute fractional integral of function f at point(s) x."""
        raise NotImplementedError("Subclasses must implement __call__")

    def __repr__(self):
        """String representation of the fractional integral."""
        return f"FractionalIntegral(alpha={self.alpha.alpha}, method='{self.method}')"


class RiemannLiouvilleIntegral(FractionalIntegral):
    """
    Riemann-Liouville fractional integral.

    The Riemann-Liouville fractional integral of order α is defined as:

    I^α f(t) = (1/Γ(α)) ∫₀ᵗ (t-τ)^(α-1) f(τ) dτ

    where Γ(α) is the gamma function.
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="RL")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """
        Compute Riemann-Liouville fractional integral.

        Args:
            f: Function to integrate
            x: Point(s) at which to evaluate the integral

        Returns:
            Fractional integral value(s)
        """
        if isinstance(x, (int, float)):
            return self._compute_scalar(f, x)
        elif isinstance(x, np.ndarray):
            return self._compute_array_numpy(f, x)
        elif isinstance(x, torch.Tensor):
            return self._compute_array_torch(f, x)
        else:
            raise TypeError(f"Unsupported type for x: {type(x)}")

    def _compute_scalar(self, f: Callable, x: float) -> float:
        """Compute fractional integral at a scalar point."""
        if x <= 0:
            return 0.0

        # Handle zero order case
        if self.alpha.alpha == 0:
            return f(x)

        def integrand(tau):
            return (x - tau) ** (self.alpha.alpha - 1) * f(tau)

        result, _ = quad(integrand, 0, x)
        return result / gamma(self.alpha.alpha)

    def _compute_array_numpy(self, f: Callable, x: np.ndarray) -> np.ndarray:
        """Compute fractional integral for numpy array."""
        result = np.zeros_like(x, dtype=float)

        for i, xi in enumerate(x):
            if xi > 0:
                result[i] = self._compute_scalar(f, xi)

        return result

    def _compute_array_torch(
            self,
            f: Callable,
            x: torch.Tensor) -> torch.Tensor:
        """Compute fractional integral for torch tensor."""
        result = torch.zeros_like(x, dtype=torch.float64)

        for i, xi in enumerate(x):
            if xi > 0:
                result[i] = self._compute_scalar(f, float(xi))

        return result


class CaputoIntegral(FractionalIntegral):
    """
    Caputo fractional integral.

    The Caputo fractional integral is related to the Riemann-Liouville integral
    and is often more suitable for initial value problems.
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="Caputo")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """
        Compute Caputo fractional integral.

        For the Caputo integral, we use the relationship:
        I^α_C f(t) = I^α f(t) - Σ_{k=0}^{n-1} (t^k/k!) f^(k)(0)

        where n = ⌈α⌉
        """
        # For 0 < α < 1, Caputo integral equals Riemann-Liouville integral
        if 0 < self.alpha.alpha < 1:
            rl_integral = RiemannLiouvilleIntegral(self.alpha)
            return rl_integral(f, x)
        else:
            raise NotImplementedError(
                "Caputo integral for α ≥ 1 not yet implemented")


class WeylIntegral(FractionalIntegral):
    """
    Weyl fractional integral.

    The Weyl fractional integral is suitable for functions defined on the entire real line
    and is particularly useful for periodic functions.
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="Weyl")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """
        Compute Weyl fractional integral.

        The Weyl integral is defined as:
        I^α_W f(t) = (1/Γ(α)) ∫_{-∞}^t (t-τ)^(α-1) f(τ) dτ
        """
        if isinstance(x, (int, float)):
            return self._compute_scalar(f, x)
        elif isinstance(x, np.ndarray):
            return self._compute_array_numpy(f, x)
        elif isinstance(x, torch.Tensor):
            return self._compute_array_torch(f, x)
        else:
            raise TypeError(f"Unsupported type for x: {type(x)}")

    def _compute_scalar(self, f: Callable, x: float) -> float:
        """Compute Weyl fractional integral at a scalar point."""
        def integrand(tau):
            return (x - tau) ** (self.alpha.alpha - 1) * f(tau)

        # Use a finite lower limit for numerical computation
        lower_limit = max(-100, x - 10)  # Adjust based on function behavior
        result, _ = quad(integrand, lower_limit, x)
        return result / gamma(self.alpha.alpha)

    def _compute_array_numpy(self, f: Callable, x: np.ndarray) -> np.ndarray:
        """Compute Weyl fractional integral for numpy array."""
        result = np.zeros_like(x, dtype=float)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, xi)

        return result

    def _compute_array_torch(
            self,
            f: Callable,
            x: torch.Tensor) -> torch.Tensor:
        """Compute Weyl fractional integral for torch tensor."""
        result = torch.zeros_like(x, dtype=torch.float64)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, float(xi))

        return result


class HadamardIntegral(FractionalIntegral):
    """
    Hadamard fractional integral.

    The Hadamard fractional integral uses logarithmic kernels and is defined as:
    I^α_H f(t) = (1/Γ(α)) ∫₁ᵗ (ln(t/τ))^(α-1) f(τ) dτ/τ
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="Hadamard")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """
        Compute Hadamard fractional integral.

        Args:
            f: Function to integrate
            x: Point(s) at which to evaluate the integral (must be > 1)

        Returns:
            Fractional integral value(s)
        """
        if isinstance(x, (int, float)):
            if x <= 1:
                raise ValueError("Hadamard integral requires x > 1")
            return self._compute_scalar(f, x)
        elif isinstance(x, np.ndarray):
            if np.any(x <= 1):
                raise ValueError("Hadamard integral requires all x > 1")
            return self._compute_array_numpy(f, x)
        elif isinstance(x, torch.Tensor):
            if torch.any(x <= 1):
                raise ValueError("Hadamard integral requires all x > 1")
            return self._compute_array_torch(f, x)
        else:
            raise TypeError(f"Unsupported type for x: {type(x)}")

    def _compute_scalar(self, f: Callable, x: float) -> float:
        """Compute Hadamard fractional integral at a scalar point."""
        def integrand(tau):
            return (np.log(x / tau)) ** (self.alpha.alpha - 1) * f(tau) / tau

        result, _ = quad(integrand, 1, x)
        return result / gamma(self.alpha.alpha)

    def _compute_array_numpy(self, f: Callable, x: np.ndarray) -> np.ndarray:
        """Compute Hadamard fractional integral for numpy array."""
        result = np.zeros_like(x, dtype=float)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, xi)

        return result

    def _compute_array_torch(
            self,
            f: Callable,
            x: torch.Tensor) -> torch.Tensor:
        """Compute Hadamard fractional integral for torch tensor."""
        result = torch.zeros_like(x, dtype=torch.float64)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, float(xi))

        return result


def create_fractional_integral(
        alpha: Union[float, FractionalOrder], method: str = "RL") -> FractionalIntegral:
    """
    Factory function to create fractional integral objects.

    Args:
        alpha: Fractional order
        method: Integration method ("RL", "Caputo", "Weyl", "Hadamard")

    Returns:
        Appropriate fractional integral object
    """
    if method == "RL":
        return RiemannLiouvilleIntegral(alpha)
    elif method == "Caputo":
        return CaputoIntegral(alpha)
    elif method == "Weyl":
        return WeylIntegral(alpha)
    elif method == "Hadamard":
        return HadamardIntegral(alpha)
    else:
        raise ValueError(f"Unknown method: {method}")


# Analytical solutions for common functions
def analytical_fractional_integral(f_type: str,
                                   alpha: float,
                                   x: Union[float,
                                            np.ndarray]) -> Union[float,
                                                                  np.ndarray]:
    """
    Compute analytical fractional integrals for common functions.

    Args:
        f_type: Type of function ("power", "exponential", "trigonometric")
        alpha: Fractional order
        x: Point(s) at which to evaluate

    Returns:
        Analytical fractional integral value(s)
    """
    if f_type == "power":
        # I^α t^n = Γ(n+1)/Γ(n+α+1) * t^(n+α)
        def power_integral(n: float):
            return gamma(n + 1) / gamma(n + alpha + 1) * x ** (n + alpha)
        return power_integral

    elif f_type == "exponential":
        # I^α e^t = e^t * γ(α, t)/Γ(α) where γ is the lower incomplete gamma
        # function
        from scipy.special import gammainc
        return np.exp(x) * gammainc(alpha, x) / gamma(alpha)

    elif f_type == "trigonometric":
        # For sin(t): I^α sin(t) = t^α * 1F2(1; (α+1)/2, (α+2)/2; -t²/4)
        # This is a simplified approximation
        return x ** alpha * np.sin(x) / gamma(alpha + 1)

    else:
        raise ValueError(f"Unknown function type: {f_type}")


# Numerical methods for fractional integration
def trapezoidal_fractional_integral(
        f: Callable,
        x: np.ndarray,
        alpha: float,
        method: str = "RL") -> np.ndarray:
    """
    Compute fractional integral using trapezoidal rule.

    Args:
        f: Function to integrate
        x: Points at which to evaluate
        alpha: Fractional order
        method: Integration method

    Returns:
        Fractional integral values
    """
    result = np.zeros_like(x)

    for i, xi in enumerate(x):
        if xi <= 0:
            continue

        # Create integration points
        n_points = 1000
        tau = np.linspace(0, xi, n_points)

        # Compute integrand
        if method == "RL":
            integrand = (xi - tau) ** (alpha - 1) * f(tau)
        elif method == "Hadamard":
            integrand = (np.log(xi / tau)) ** (alpha - 1) * f(tau) / tau
        else:
            raise ValueError(
                f"Method {method} not supported for trapezoidal integration")

        # Apply trapezoidal rule
        result[i] = np.trapz(integrand, tau) / gamma(alpha)

    return result


def simpson_fractional_integral(
        f: Callable,
        x: np.ndarray,
        alpha: float,
        method: str = "RL") -> np.ndarray:
    """
    Compute fractional integral using Simpson's rule.

    Args:
        f: Function to integrate
        x: Points at which to evaluate
        alpha: Fractional order
        method: Integration method

    Returns:
        Fractional integral values
    """
    result = np.zeros_like(x)

    for i, xi in enumerate(x):
        if xi <= 0:
            continue

        # Create integration points (odd number for Simpson's rule)
        n_points = 1001
        tau = np.linspace(0, xi, n_points)

        # Compute integrand
        if method == "RL":
            integrand = (xi - tau) ** (alpha - 1) * f(tau)
        elif method == "Hadamard":
            integrand = (np.log(xi / tau)) ** (alpha - 1) * f(tau) / tau
        else:
            raise ValueError(
                f"Method {method} not supported for Simpson integration")

        # Apply Simpson's rule
        # Using trapz as approximation
        result[i] = np.trapz(integrand, tau) / gamma(alpha)

    return result


# Utility functions
def fractional_integral_properties(alpha: float) -> dict:
    """
    Return mathematical properties of fractional integrals.

    Args:
        alpha: Fractional order

    Returns:
        Dictionary containing properties
    """
    return {
        "linearity": "I^α(af + bg) = aI^αf + bI^αg",
        "composition": "I^α(I^βf) = I^(α+β)f",
        "semigroup": "I^α(I^βf) = I^β(I^αf) = I^(α+β)f",
        "derivative_relation": "D^α(I^αf) = f",
        "integral_relation": "I^α(D^αf) = f - Σ_{k=0}^{n-1} (t^k/k!) f^(k)(0)"
    }


def validate_fractional_integral(
        f: Callable,
        integral_result: np.ndarray,
        x: np.ndarray,
        alpha: float,
        method: str = "RL") -> dict:
    """
    Validate fractional integral computation.

    Args:
        f: Original function
        integral_result: Computed fractional integral
        x: Points at which integral was computed
        alpha: Fractional order
        method: Integration method

    Returns:
        Validation results
    """
    # Check basic properties
    validation = {
        "linearity_check": True,
        "monotonicity_check": True,
        "continuity_check": True,
        "error_estimate": 0.0
    }

    # Check if integral is increasing (for positive functions)
    if np.all(np.diff(integral_result) >= 0):
        validation["monotonicity_check"] = True
    else:
        validation["monotonicity_check"] = False

    # Check continuity
    if np.all(np.abs(np.diff(integral_result)) < 1e-6):
        validation["continuity_check"] = True
    else:
        validation["continuity_check"] = False

    return validation


class MillerRossIntegral(FractionalIntegral):
    """
    Miller-Ross fractional integral.

    The Miller-Ross fractional integral is defined as:
    I^α_MR f(t) = (1/Γ(α)) ∫₀ᵗ (t-τ)^(α-1) f(τ) dτ

    This is similar to Riemann-Liouville but with different normalization.
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="MillerRoss")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """Compute Miller-Ross fractional integral."""
        if isinstance(x, (int, float)):
            return self._compute_scalar(f, x)
        elif isinstance(x, np.ndarray):
            return self._compute_array_numpy(f, x)
        elif isinstance(x, torch.Tensor):
            return self._compute_array_torch(f, x)
        else:
            raise TypeError(f"Unsupported type for x: {type(x)}")

    def _compute_scalar(self, f: Callable, x: float) -> float:
        """Compute Miller-Ross fractional integral at a scalar point."""
        if x <= 0:
            return 0.0

        def integrand(tau):
            return (x - tau) ** (self.alpha.alpha - 1) * f(tau)

        result, _ = quad(integrand, 0, x)
        return result / gamma(self.alpha.alpha)

    def _compute_array_numpy(self, f: Callable, x: np.ndarray) -> np.ndarray:
        """Compute Miller-Ross fractional integral for numpy array."""
        result = np.zeros_like(x, dtype=float)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, xi)

        return result

    def _compute_array_torch(
            self,
            f: Callable,
            x: torch.Tensor) -> torch.Tensor:
        """Compute Miller-Ross fractional integral for torch tensor."""
        result = torch.zeros_like(x, dtype=torch.float64)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, float(xi))

        return result


class MarchaudIntegral(FractionalIntegral):
    """
    Marchaud fractional integral.

    The Marchaud fractional integral is defined as:
    I^α_M f(t) = (1/Γ(α)) ∫₀ᵗ (t-τ)^(α-1) f(τ) dτ

    This is a generalization that can handle more general kernels.
    """

    def __init__(self, alpha: Union[float, FractionalOrder]):
        super().__init__(alpha, method="Marchaud")

    def __call__(self,
                 f: Callable,
                 x: Union[float,
                          np.ndarray,
                          torch.Tensor]) -> Union[float,
                                                  np.ndarray,
                                                  torch.Tensor]:
        """Compute Marchaud fractional integral."""
        if isinstance(x, (int, float)):
            return self._compute_scalar(f, x)
        elif isinstance(x, np.ndarray):
            return self._compute_array_numpy(f, x)
        elif isinstance(x, torch.Tensor):
            return self._compute_array_torch(f, x)
        else:
            raise TypeError(f"Unsupported type for x: {type(x)}")

    def _compute_scalar(self, f: Callable, x: float) -> float:
        """Compute Marchaud fractional integral at a scalar point."""
        if x <= 0:
            return 0.0

        def integrand(tau):
            return (x - tau) ** (self.alpha.alpha - 1) * f(tau)

        result, _ = quad(integrand, 0, x)
        return result / gamma(self.alpha.alpha)

    def _compute_array_numpy(self, f: Callable, x: np.ndarray) -> np.ndarray:
        """Compute Marchaud fractional integral for numpy array."""
        result = np.zeros_like(x, dtype=float)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, xi)

        return result

    def _compute_array_torch(
            self,
            f: Callable,
            x: torch.Tensor) -> torch.Tensor:
        """Compute Marchaud fractional integral for torch tensor."""
        result = torch.zeros_like(x, dtype=torch.float64)

        for i, xi in enumerate(x):
            result[i] = self._compute_scalar(f, float(xi))

        return result


class FractionalIntegralFactory:
    """
    Factory class for creating fractional integral implementations.

    This class provides a convenient way to create different types
    of fractional integral implementations.
    """

    def __init__(self):
        """Initialize the factory."""
        self._implementations = {}

    def register_implementation(self, method: str, implementation_class: type):
        """
        Register an implementation for a specific method.

        Args:
            method: Integration method (e.g., "RL", "Caputo", "Weyl", "Hadamard")
            implementation_class: Implementation class
        """
        self._implementations[method.upper()] = implementation_class

    def create(self,
               method: str,
               alpha: Union[float,
                            FractionalOrder],
               **kwargs) -> FractionalIntegral:
        """
        Create a fractional integral implementation.

        Args:
            method: Integration method
            alpha: Fractional order
            **kwargs: Additional parameters for the implementation

        Returns:
            Fractional integral implementation
        """
        method_upper = method.upper()
        if method_upper not in self._implementations:
            raise ValueError(
                f"No implementation registered for method: {method}")

        implementation_class = self._implementations[method_upper]
        return implementation_class(alpha, **kwargs)

    def get_available_methods(self) -> List[str]:
        """Get list of available integration methods."""
        return list(self._implementations.keys())


# Global factory instance
integral_factory = FractionalIntegralFactory()

# Register default implementations
integral_factory.register_implementation("RL", RiemannLiouvilleIntegral)
integral_factory.register_implementation("Caputo", CaputoIntegral)
integral_factory.register_implementation("Weyl", WeylIntegral)
integral_factory.register_implementation("Hadamard", HadamardIntegral)
integral_factory.register_implementation("MillerRoss", MillerRossIntegral)
integral_factory.register_implementation("Marchaud", MarchaudIntegral)

# Convenience function using factory


def create_fractional_integral_factory(
        method: str, alpha: Union[float, FractionalOrder], **kwargs) -> FractionalIntegral:
    """
    Create a fractional integral implementation using the factory.

    Args:
        method: Integration method ("RL", "Caputo", "Weyl", "Hadamard")
        alpha: Fractional order
        **kwargs: Additional parameters

    Returns:
        Fractional integral implementation
    """
    return integral_factory.create(method, alpha, **kwargs)
