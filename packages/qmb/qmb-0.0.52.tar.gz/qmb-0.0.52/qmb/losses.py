"""
This file contains various loss functions used in the other script.

These functions help calculate the difference between the target wave function and the current state wave function.
"""

import math
import torch


@torch.jit.script
def _scaled_abs(s_abs: torch.Tensor, min_magnitude: float) -> torch.Tensor:
    s_large = torch.log(s_abs)
    s_small = (s_abs - min_magnitude) / min_magnitude + math.log(min_magnitude)
    return torch.where(s_abs > min_magnitude, s_large, s_small)


@torch.jit.script
def _scaled_angle(scale: torch.Tensor, min_magnitude: float) -> torch.Tensor:
    return 1 / (1 + min_magnitude / scale)


@torch.jit.script
def hybrid(s: torch.Tensor, t: torch.Tensor, min_magnitude: float = 1e-12) -> torch.Tensor:
    """
    Compute the loss using a hybrid strategy that specifically accounts for the small magnitudes of the wave function.
    """
    # In typical data scales, taking the difference of the log of s and t as the loss is appropriate.
    # However, issues arise when s or t is particularly small.
    # The log function amplifies the loss near small values and diminishes the loss near large values.
    # This is generally reasonable, as we expect the same level of effort for changes like 0.1 to 0.01 and 1 to 0.1.
    # But when the absolute value is extremely small, such as wanting 1e-20 to become 1e-30, we have little motivation to optimize this.
    # Therefore, we need to reduce the gradient of the mapping function (currently log) near small values.
    # We decide to make it linear near small values because we do not want to optimize it further.
    # Even if the number of Hamiltonian terms reaches 1e8, the accumulated error of 1e-12 terms would only be 1e-4, less than chemical precision.
    # On the other hand, changes in the angle near small values are also meaningless.
    # However, for sufficiently large values, we want them to be optimized uniformly.
    # For example, we want the effort for changes from -1 to +1 to be similar to that from -0.1 to +0.1.
    # Therefore, the angle difference should be multiplied by a factor that is constant at 1 near large values but linearly converges to 0 near small values.

    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = _scaled_abs(s_abs, min_magnitude)
    t_magnitude = _scaled_abs(t_abs, min_magnitude)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    scale = torch.where(s_abs > t_abs, s_abs, t_abs)
    error_imag = error_imag * _scaled_angle(scale, min_magnitude)

    loss = error_real**2 + error_imag**2
    return loss.mean()


@torch.jit.script
def log(s: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the log of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = torch.log(s_abs)
    t_magnitude = torch.log(t_abs)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    loss = error_real**2 + error_imag**2
    return loss.mean()


@torch.jit.script
def sum_reweighted_log(s: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the log of the current state wave function and the target wave function,
    but reweighted by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = torch.log(s_abs)
    t_magnitude = torch.log(t_abs)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    loss = error_real**2 + error_imag**2
    loss = loss * (t_abs + s_abs)
    return loss.mean()


@torch.jit.script
def sum_filtered_log(s: torch.Tensor, t: torch.Tensor, min_magnitude: float = 1e-10) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the log of the current state wave function and the target wave function,
    but filtered by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = torch.log(s_abs)
    t_magnitude = torch.log(t_abs)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    loss = error_real**2 + error_imag**2
    loss = loss * _scaled_angle(t_abs + s_abs, min_magnitude)
    return loss.mean()


@torch.jit.script
def sum_filtered_scaled_log(s: torch.Tensor, t: torch.Tensor, min_magnitude: float = 1e-10) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the scaled log of the current state wave function and the target wave function,
    but filtered by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = _scaled_abs(s_abs, min_magnitude)
    t_magnitude = _scaled_abs(t_abs, min_magnitude)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    loss = error_real**2 + error_imag**2
    loss = loss * _scaled_angle(t_abs + s_abs, min_magnitude)
    return loss.mean()


@torch.jit.script
def sum_reweighted_angle_log(s: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the log of the current state wave function and the target wave function,
    but angle only reweighted by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = torch.log(s_abs)
    t_magnitude = torch.log(t_abs)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    error_imag = error_imag * (t_abs + s_abs)
    loss = error_real**2 + error_imag**2
    return loss.mean()


@torch.jit.script
def sum_filtered_angle_log(s: torch.Tensor, t: torch.Tensor, min_magnitude: float = 1e-10) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the log of the current state wave function and the target wave function,
    but angle only filtered by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = torch.log(s_abs)
    t_magnitude = torch.log(t_abs)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    error_imag = error_imag * _scaled_angle(t_abs + s_abs, min_magnitude)
    loss = error_real**2 + error_imag**2
    return loss.mean()


@torch.jit.script
def sum_filtered_angle_scaled_log(s: torch.Tensor, t: torch.Tensor, min_magnitude: float = 1e-10) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the scaled log of the current state wave function and the target wave function,
    but angle only filtered by the sum of the abs of the current state wave function and the target wave function.
    """
    s_abs = torch.sqrt(s.real**2 + s.imag**2)
    t_abs = torch.sqrt(t.real**2 + t.imag**2)

    s_angle = torch.atan2(s.imag, s.real)
    t_angle = torch.atan2(t.imag, t.real)

    s_magnitude = _scaled_abs(s_abs, min_magnitude)
    t_magnitude = _scaled_abs(t_abs, min_magnitude)

    error_real = (s_magnitude - t_magnitude) / (2 * torch.pi)
    error_imag = (s_angle - t_angle) / (2 * torch.pi)
    error_imag = error_imag - error_imag.round()

    error_imag = error_imag * _scaled_angle(t_abs + s_abs, min_magnitude)
    loss = error_real**2 + error_imag**2
    return loss.mean()


@torch.jit.script
def direct(s: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
    """
    Calculate the loss based on the difference between the current state wave function and the target wave function directly.
    """
    error = s - t
    loss = error.real**2 + error.imag**2
    return loss.mean()
