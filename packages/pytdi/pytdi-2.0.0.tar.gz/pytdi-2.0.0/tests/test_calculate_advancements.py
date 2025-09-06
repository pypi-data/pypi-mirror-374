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
Test time-shifting functions (delays and time advancements).
"""

import numpy as np
from pytest import approx

import pytdi.dsp


def test_constant_delay():
    """Test `calculate_advancement()` with constant delays"""
    delay = 10.234
    size = 100
    fs = 1
    order = 5
    delta = 1e-9
    maxiter = 10

    delays = np.full(size, delay)
    advancements = pytdi.dsp.calculate_advancements(
        delays, fs, order=order, delta=delta, maxiter=maxiter
    )

    num_tabs = order + 1
    k = int(delay * fs)
    assert np.all(advancements[: -(k + num_tabs // 2)] == approx(delay))


def test_variable_linear_delay():
    """Test `calculate_advancement()` with variable delays"""
    offset = 10.234
    slope = 0.0321
    size = 100
    fs = 1
    order = 5
    delta = 1e-9
    maxiter = 10

    def delay(times):
        return offset + slope * times

    def advancement(times):
        return (offset + slope * times) / (1 - slope)

    times = np.arange(size) / fs
    delays = delay(times)
    advancements = pytdi.dsp.calculate_advancements(
        delays, fs, order=order, delta=delta, maxiter=maxiter
    )
    advancements_model = advancement(times)

    num_tabs = order + 1
    k_max = np.max(np.floor(advancements_model * fs)).astype(int)
    cut_end = -(k_max + num_tabs // 2)
    assert np.all(advancements[:-cut_end] == approx(advancements_model[:-cut_end]))
