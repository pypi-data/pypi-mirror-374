#
# BSD 3-Clause License
#
# Copyright (c) 2022, California Institute of Technology and
# Max Planck Institute for Gravitational Physics (Albert Einstein Institute)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# This software may be subject to U.S. export control laws. By accepting this
# software, the user agrees to comply with all applicable U.S. export laws and
# regulations. User has the responsibility to obtain export licenses, or other
# export authority as may be required before exporting such information to
# foreign countries or providing access to foreign persons.
#
"""
Collections of methods for digital signal processing.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def diff(data, dt):
    """Calculate derivative in time.

    Args:
        data (float or array-like): input array
        dt (float): sampling time

    Returns:
        array-like: The array of derived data.
    """
    return 0 if np.isscalar(data) else np.gradient(data, dt)


def timeshift(data, shifts, order=31):
    """Time-shift data (delay or advancement) using Lagrange interpolation.

    The method computes the Lagrange coefficients for the possibly time-varying shifts,
    and apply them as a fractional-delay finite-impulse response Lagrange filter.

    Note:
        The ``shifts`` are given as dimensionless numbers of samples.

    Example:

        .. code-block:: python

            # Apply fractional time-varying delay
            data = np.array(...)
            delays = np.array(...)
            shifted = timeshift(data, -delays, order=11)

            # Apply fractional time-varying advancement
            advancements = np.array(...)
            shifted = timeshift(data, advancements, order=11)

    Args:
        data (float or array-like): input array
        shifts (float or array-like): time shifts [number of samples]
        order (odd int): interpolation order

    Returns:
        array-like: The array of shifted data, whose dimension is adapted to accomodate
        the time shifts.
    """
    if order % 2 == 0:
        raise ValueError(f"`order` must be an odd integer (got {order})")

    data = np.asarray(data)
    shifts = np.asarray(shifts)
    logger.debug("Time shifting data samples (order=%d)", order)

    # Handle constant input and vanishing shifts
    if data.size == 1:
        logger.debug("Input data is constant, skipping time-shift operation")
        return data.item()
    if np.all(shifts == 0):
        logger.debug("Time shifts are vanishing, skipping time-shift operation")
        return data

    logger.debug("Computing Lagrange coefficients")
    halfp = (order + 1) // 2
    shift_ints = np.floor(shifts)
    shift_fracs = shifts - shift_ints
    taps = lagrange_taps(shift_fracs, halfp)
    shift_ints = shift_ints.astype(int)

    # Handle constant shifts
    if shifts.size == 1:
        logger.debug("Constant shifts, using correlation method")
        i_min = shift_ints - (halfp - 1)
        i_max = shift_ints + halfp + data.size
        if i_max - 1 < 0 or i_min > data.size - 1:
            return np.zeros(data.size)
        logger.debug(
            "Padding data (left=%d, right=%d)",
            max(0, -i_min),
            max(0, i_max - data.size),
        )
        data_trimmed = data[max(0, i_min) : min(data.size, i_max)]
        data_padded = np.pad(data_trimmed, (max(0, -i_min), max(0, i_max - data.size)))
        logger.debug("Computing correlation product")
        return np.correlate(data_padded, taps[0], mode="valid")

    # Check that sizes or compatible
    if data.size != shifts.size:
        raise ValueError(
            f"data and shift must be of the same size (got {data.size}, {shifts.size})"
        )

    # Handle time-varying shifts
    logger.debug("Time-varying shifts, using sliding window view")
    indices = np.clip(
        np.arange(data.size) + shift_ints, -(halfp + 1), data.size + (halfp - 1)
    )
    padded = np.pad(data, 2 * halfp)
    slices = np.lib.stride_tricks.sliding_window_view(padded, 2 * halfp)
    slices = slices[indices + 2 * halfp - (halfp - 1)]
    logger.debug("Computing matrix-vector product")
    return np.einsum("ij,ij->i", taps, slices)


def lagrange_taps(shift_fracs, halfp):
    """Compute the Lagrange coefficients.

    Computes the Lagrange interpolating polynomial coefficients for a centered
    fractional delay filter.

    Args:
        shift_fracs (array-like): fractional time shifts [samples]
        halfp (int): number of points on each side, equivalent to ``(order + 1) // 2``

    Returns:
        array-like: Array of Lagrange coefficients, of dimension ``(N, 2 * halfp)``
        if N is the dimension of ``shift_fracs``.
    """
    taps = np.zeros((2 * halfp, shift_fracs.size), dtype=shift_fracs.dtype)

    if halfp > 1:
        factor = np.ones(shift_fracs.size, dtype=shift_fracs.dtype)
        factor *= shift_fracs * (1 - shift_fracs)

        for j in range(1, halfp):
            factor *= (-1) * (1 - j / halfp) / (1 + j / halfp)
            taps[halfp - 1 - j] = factor / (j + shift_fracs)
            taps[halfp + j] = factor / (j + 1 - shift_fracs)

        taps[halfp - 1] = 1 - shift_fracs
        taps[halfp] = shift_fracs

        for j in range(2, halfp):
            taps *= 1 - (shift_fracs / j) ** 2

        taps *= (1 + shift_fracs) * (1 - shift_fracs / halfp)
    else:
        taps[halfp - 1] = 1 - shift_fracs
        taps[halfp] = shift_fracs

    return taps.T


def calculate_advancements(delays, fs, order=5, delta=1e-12, maxiter=10):
    r"""Solve for advancements using delays as inputs.

    This solves iteratively for the advancement :math:`a_{ij}(t)`.

    .. math::

        a_{ij}(t) = d_{ji}(t + a_{ij}(t)) \qc

    with :math:`d_{ji}(t)` being the associated delay.

    Args:
        delays (array-like): time delays [s]
        fs (float): sampling frequency [Hz]
        order (odd int): interpolation order
        delta (float): allowed root mean-square error between two successive iterations
        max_iter (int): maximum number of iterations

    Returns:
        array-like: Array of time advancements, same dimension as ``delays``.
    """
    logger.debug(
        "Computing advancements from delays, solving for implicit equation "
        "(order=%d, delta=%f, maxiter=%d)",
        order,
        delta,
        maxiter,
    )

    delays = np.asarray(delays)
    if delays.size == 1:
        logger.debug("Delays are constant, skipping advancement calculation")
        return delays

    advancements = delays.copy()
    delta2 = delta**2
    mean_squared_error = delta2

    count = 0
    while mean_squared_error >= delta2:
        logger.debug("Computing iteration %d", count + 1)
        if count >= maxiter:
            logger.warning(
                "Maximum number of iterations %d reached, "
                "returning current advancement",
                maxiter,
            )
            break
        advancements_prev = advancements
        advancements = timeshift(delays, advancements_prev * fs, order=order)
        advancement_max = np.max(advancements_prev)
        num_tabs = order + 1
        k_max = int(advancement_max * fs)
        cut_start = max(-(k_max + 1) + num_tabs // 2, 0)
        cut_end = k_max + num_tabs // 2
        difference = (advancements - advancements_prev)[cut_start:-cut_end]
        mean_squared_error = np.mean(difference**2)
        logger.debug(
            "Mean squared error of iteration %d: '%f' (aim at %f)",
            count + 1,
            mean_squared_error,
            delta2,
        )
        count += 1

    return advancements
