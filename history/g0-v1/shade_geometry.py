"""Original synthetic shade controls for Hikage-machi, 2026.

Author: Francisco Angulo de Lafuente. AI implementation assistance: Codex.
SPDX-License-Identifier: MIT
This is a new horizontal-rectangle operator, not an existing Neuro3D operator.
"""
import math
import torch


def coordinates(points, suns, parameters):
    """Ground points [P,2], unit directions to sun [S,3], dimensions in metres.

    parameters = [centre_x, centre_y, width, depth, height, angle_radians].
    Returns projected rectangle coordinates [P,S] in its rotated local frame.
    Only upward directions are supported; below-horizon input is rejected.
    """
    if points.ndim != 2 or points.shape[1] != 2 or suns.ndim != 2 or suns.shape[1] != 3 or parameters.shape != (6,):
        raise ValueError("Invalid geometry shape")
    if not (torch.isfinite(points).all() and torch.isfinite(suns).all() and torch.isfinite(parameters).all()):
        raise ValueError("Non-finite geometry")
    if (suns[:, 2] <= 1e-3).any() or (parameters[2:5] <= 0).any():
        raise ValueError("Sun must be above horizon; dimensions and height must be positive")
    cx, cy, width, depth, height, angle = parameters.unbind()
    projected = points[:, None, :] + height * suns[None, :, :2] / suns[None, :, 2:3]
    dx = projected[..., 0] - cx
    dy = projected[..., 1] - cy
    c, s = torch.cos(angle), torch.sin(angle)
    return c * dx + s * dy, -s * dx + c * dy


def hard_shadow(points, suns, parameters):
    u, v = coordinates(points, suns, parameters)
    return (u.abs() <= parameters[2] / 2) & (v.abs() <= parameters[3] / 2)


def smooth_shadow(points, suns, parameters, tau=0.15):
    """A numerical edge relaxation, not a physical penumbra or irradiance model."""
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError("tau must be positive metres")
    u, v = coordinates(points, suns, parameters)
    return torch.sigmoid((parameters[2]/2-u.abs())/tau) * torch.sigmoid((parameters[3]/2-v.abs())/tau)


def expected_periodic_wait_minutes(headways):
    """Uniform passenger arrivals over a periodic schedule: E[W]=sum(h^2)/(2sum(h)).

    This does not predict actual passenger arrivals, cancellations or delays.
    Headways must refer to a usable service/destination, not all buses pooled.
    """
    h = [float(x) for x in headways]
    if not h or any(not math.isfinite(x) or x <= 0 for x in h):
        raise ValueError("Headways must be positive finite minutes")
    return sum(x*x for x in h)/(2*sum(h))
