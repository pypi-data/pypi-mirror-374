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
Test that orthogonal combinations (AET) can reduce laser noise (using LISANode data).
"""

from integration import BASE_PATH, psd_threshold, read_from_lisanode

import pytdi.intervar
import pytdi.ortho


def test_ortho_1st_gen():
    """Test that the first-generation AET combinations reduce laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    combinations = {"A1": pytdi.ortho.A1, "E1": pytdi.ortho.E1, "T1": pytdi.ortho.T1}
    for name, tdi in combinations.items():
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[200:], 1e-39, freq_range=(1e-4, 8e-1), fs=3.2, name=name)


def test_factorized_ortho_1st_gen():
    """Test that the factorized first-generation AET combinations reduce laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    ortho = pytdi.ortho.compute_factorized_ortho(data, generation=1, unit="phase")
    psd_threshold(
        ortho["A"][200:], 1e-39, freq_range=(1e-4, 8e-1), fs=3.2, name="facto-A1"
    )
    psd_threshold(
        ortho["E"][200:], 1e-39, freq_range=(1e-4, 8e-1), fs=3.2, name="facto-E1"
    )
    psd_threshold(
        ortho["T"][200:], 1e-39, freq_range=(1e-4, 8e-1), fs=3.2, name="facto-T1"
    )


def test_ortho_2nd_gen():
    """Test that the second-generation AET combinations reduce laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    combinations = {"A2": pytdi.ortho.A2, "E2": pytdi.ortho.E2, "T2": pytdi.ortho.T2}
    for name, tdi in combinations.items():
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[500:], 1e-41, freq_range=(1e-4, 6e-1), fs=3.2, name=name)


def test_factorized_ortho_2nd_gen():
    """Test that the factorized second-generation AET combinations reduce laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    ortho = pytdi.ortho.compute_factorized_ortho(data, generation=2, unit="phase")
    psd_threshold(
        ortho["A"][500:], 1e-41, freq_range=(1e-4, 6e-1), fs=3.2, name="facto-A2"
    )
    psd_threshold(
        ortho["E"][500:], 1e-41, freq_range=(1e-4, 6e-1), fs=3.2, name="facto-E2"
    )
    psd_threshold(
        ortho["T"][500:], 1e-41, freq_range=(1e-4, 6e-1), fs=3.2, name="facto-T2"
    )
