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
Test that Sagnac combinations can reduce laser noise (using LISANode data).
"""

from integration import BASE_PATH, psd_threshold, read_from_lisanode

import pytdi.intervar
import pytdi.sagnac


def test_sagnac_1():
    """Test that the entire first-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    names = ["alpha-1", "beta-1", "gamma-1"]
    tdivars = [pytdi.sagnac.ALPHA1, pytdi.sagnac.BETA1, pytdi.sagnac.GAMMA1]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[200:], 1e-35, freq_range=(1e-4, 5e-1), fs=3.2, name=name)


def test_factorized_sagnac_1():
    """Test that the factorized first-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    etas = pytdi.intervar.compute_etas(data, unit="phase")
    names = ["facto-alpha-1", "facto-beta-1", "facto-gamma-1"]
    for i, name in enumerate(names):
        data_x = pytdi.sagnac.compute_factorized_sagnac(
            data, etas, rot=i, generation=1, unit="phase"
        )
        psd_threshold(data_x[200:], 1e-35, freq_range=(1e-4, 5e-1), fs=3.2, name=name)


def test_symmetric_sagnac_1():
    """Test that the entire first-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    names = ["zeta-1"]
    tdivars = [pytdi.sagnac.ZETA1]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[200:], 1e-30, freq_range=(1e-4, 5e-1), fs=3.2, name=name)


def test_sagnac_2():
    """Test that the entire second-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    names = ["alpha-2", "beta-2", "gamma-2"]
    tdivars = [pytdi.sagnac.ALPHA2, pytdi.sagnac.BETA2, pytdi.sagnac.GAMMA2]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[200:], 1e-41, freq_range=(1e-4, 5e-1), fs=3.2, name=name)


def test_factorized_sagnac_2():
    """Test that the factorized second-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    etas = pytdi.intervar.compute_etas(data, unit="phase")
    names = ["facto-alpha-2", "facto-beta-2", "facto-gamma-2"]
    for i, name in enumerate(names):
        data_x = pytdi.sagnac.compute_factorized_sagnac(
            data, etas, rot=i, generation=2, unit="phase"
        )
        psd_threshold(data_x[200:], 1e-41, freq_range=(1e-4, 5e-1), fs=3.2, name=name)


def test_symmetric_sagnac_2():
    """Test that the entire second-generation Sagnac combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    names = ["zeta-21", "zeta-22", "zeta-23"]
    tdivars = [pytdi.sagnac.ZETA21, pytdi.sagnac.ZETA22, pytdi.sagnac.ZETA23]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(data_x[200:], 1e-38, freq_range=(1e-4, 5e-1), fs=3.2, name=name)
