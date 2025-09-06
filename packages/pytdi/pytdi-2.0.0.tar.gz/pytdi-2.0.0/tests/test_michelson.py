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
Test that Michelson combinations can reduce laser noise (using LISANode data).
"""

import numpy as np
import scipy
from integration import (
    BASE_PATH,
    COEFFS_AA,
    filter_tf_derivative,
    psd_model,
    psd_threshold,
    read_from_lisanode,
)

import pytdi.intervar
import pytdi.michelson
import pytdi.naming


def test_laser_noise_reduction_with_michelson_1():
    """Test that first-generation Michelson combinations reduce laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-threelasers-lasernoise-staticorbits.h5"
    )
    data_eta = {}
    for i, j in pytdi.naming.lisa_indices():
        name_eta = pytdi.naming.join_indices("eta", i, j)
        name_isc = pytdi.naming.join_indices("sci", i, j)
        data_eta[name_eta] = data_ln[name_isc]
    tdivars = [pytdi.michelson.X1_ETA, pytdi.michelson.Y1_ETA, pytdi.michelson.Z1_ETA]
    names = ["X1_ETA", "Y1_ETA", "Z1_ETA"]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_eta, unit="phase")
        psd_threshold(
            data_x[200:],
            1e-46,
            freq_range=(1e-4, 5e-1),
            fs=3.2,
            name=f"test_laser_noise_reduction_with_michelson_1:{name}",
        )


def test_reduction_to_3_laser_laser_noise_reduction_with_michelson_1():
    """Test that first-generation Michelson combinations reduce to 3 lasers and laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-staticorbits.h5"
    )
    data_xi = {}
    for i, j in pytdi.naming.lisa_indices():
        name_xi = pytdi.naming.join_indices("xi", i, j)
        name_isc = pytdi.naming.join_indices("sci", i, j)
        name_ref = pytdi.naming.join_indices("ref", i, j)
        data_xi[name_xi] = data_ln[name_isc]
        data_xi[name_ref] = data_ln[name_ref]

    data_eta = {}
    for key, var in pytdi.intervar.ETA_XI_SET.items():
        data_eta[key] = var.build(delays, 3.2)(data_xi, unit="phase")

    tdivars = [pytdi.michelson.X1_ETA, pytdi.michelson.Y1_ETA, pytdi.michelson.Z1_ETA]
    names = ["X1_ETA", "Y1_ETA", "Z1_ETA"]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_eta, unit="phase")
        psd_threshold(
            data_x[200:],
            1e-46,
            freq_range=(1e-4, 5e-1),
            fs=3.2,
            name=f"test_reduction_to_3_laser_laser_noise_reduction_with_michelson_1:{name}",
        )


def test_michelson_1():
    """Test that the entire first-generation Michelson combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-staticorbits.h5"
    )
    tdivars = [pytdi.michelson.X1, pytdi.michelson.Y1, pytdi.michelson.Z1]
    names = ["X1", "Y1", "Z1"]
    for tdi, name in zip(tdivars, names):
        data_x = tdi.build(delays, 3.2)(data_ln, unit="phase")
        psd_threshold(
            data_x[200:],
            1e-46,
            freq_range=(1e-4, 5e-1),
            fs=3.2,
            name=f"test_michelson_1:{name}",
        )


def test_factorized_michelson_1():
    """Test that the entire factorized first-generation Michelson combinations reduces laser noise."""
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-staticorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    etas = pytdi.intervar.compute_etas(data, unit="phase")
    names = ["X1", "Y1", "Z1"]
    for i, name in enumerate(names):
        data_x = pytdi.michelson.compute_factorized_michelson(
            data, etas, rot=i, generation=1, unit="phase"
        )
        psd_threshold(
            data_x[200:],
            1e-46,
            freq_range=(1e-4, 5e-1),
            fs=3.2,
            name=f"test_factorized_michelson_1:{name}",
        )


def flexing_filtering_model(freq, arm, delays, fs):
    """Return model for flexing-filtering coupling in the second-generation Michelson combinations"""
    omega = 2 * np.pi * freq
    # Calculate mean delays and doppler velocities
    # times = np.arange(len(next(iter(delays)))) / fs
    times = np.arange(len(delays["d_12"])) / fs
    doppler1, tt1, _, _, _ = scipy.stats.linregress(times, delays[arm[0][0]])
    doppler1_p, tt1_p, _, _, _ = scipy.stats.linregress(times, delays[arm[0][1]])
    doppler2, tt2, _, _, _ = scipy.stats.linregress(times, delays[arm[1][0]])
    doppler2_p, tt2_p, _, _, _ = scipy.stats.linregress(times, delays[arm[1][1]])
    doppler1s2 = doppler1**2 + doppler1_p**2
    doppler2s2 = doppler2**2 + doppler2_p**2
    kf2 = filter_tf_derivative(freq, COEFFS_AA, fs)

    tts1 = tt1 + tt1_p
    tts2 = tt2 + tt2_p
    return (
        2
        * omega**2
        * 1e-26
        * kf2
        * (
            (
                2
                - 2 * np.cos(omega * tts1)
                + np.cos(omega * tts2)
                - 2 * np.cos(omega * (tts1 + tts2))
                + np.cos(omega * (tts2 + 2 * tts1))
            )
            * doppler2s2
            + (
                2
                - 2 * np.cos(omega * tts2)
                + np.cos(omega * tts1)
                - 2 * np.cos(omega * (tts1 + tts2))
                + np.cos(omega * (tts1 + 2 * tts2))
            )
            * doppler1s2
        )
    )


def test_michelson_2():
    """Test that the entire second-generation Michelson combinations reduces laser noise."""
    fs = 3.2
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )

    tdivars = [pytdi.michelson.X2, pytdi.michelson.Y2, pytdi.michelson.Z2]
    names = ["X2", "Y2", "Z2"]
    arms = [
        (("d_12", "d_21"), ("d_13", "d_31")),
        (("d_21", "d_12"), ("d_23", "d_32")),
        (("d_31", "d_13"), ("d_32", "d_23")),
    ]
    for tdi, name, arm in zip(tdivars, names, arms):
        data_x = tdi.build(delays, fs)(data_ln, unit="phase")
        model = lambda freq, arm=arm: flexing_filtering_model(freq, arm, delays, fs)
        psd_model(
            data_x[400:],
            model,
            freq_range=(1e-4, 5e-1),
            fs=fs,
            freq_res=1e-4,
            threshold=1e-47,
            name=f"test_michelson_2:{name}",
            confidence=0.99,
        )


def test_factorized_michelson_2():
    """Test that the entire factorized second-generation Michelson combinations reduces laser noise."""
    fs = 3.2
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    etas = pytdi.intervar.compute_etas(data, unit="phase")
    names = ["X2", "Y2", "Z2"]
    arms = [
        (("d_12", "d_21"), ("d_13", "d_31")),
        (("d_21", "d_12"), ("d_23", "d_32")),
        (("d_31", "d_13"), ("d_32", "d_23")),
    ]
    for i, (name, arm) in enumerate(zip(names, arms)):
        data_x = pytdi.michelson.compute_factorized_michelson(
            data, etas, rot=i, generation=2, unit="phase"
        )
        model = lambda freq, arm=arm: flexing_filtering_model(freq, arm, delays, fs)
        psd_model(
            data_x[400:],
            model,
            freq_range=(1e-4, 5e-1),
            fs=fs,
            freq_res=1e-4,
            threshold=1e-47,
            name=f"test_factorized_michelson_2:{name}",
            confidence=0.99,
        )


def test_michelson_2_doppler():
    """Test that the entire second-generation Michelson combinations reduces laser noise."""
    fs = 3.2
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits-doppler.h5"
    )
    delay_derivatives = {}
    for delay in delays:
        delay_derivatives[delay] = np.gradient(delays[delay], 1 / fs)

    tdivars = [pytdi.michelson.X2, pytdi.michelson.Y2, pytdi.michelson.Z2]
    names = ["X2", "Y2", "Z2"]
    arms = [
        (("d_12", "d_21"), ("d_13", "d_31")),
        (("d_21", "d_12"), ("d_23", "d_32")),
        (("d_31", "d_13"), ("d_32", "d_23")),
    ]
    for tdi, name, arm in zip(tdivars, names, arms):
        data_x = tdi.build(delays, fs, delay_derivatives=delay_derivatives)(
            data_ln, unit="frequency"
        )
        model = lambda freq, arm=arm: flexing_filtering_model(freq, arm, delays, fs)
        psd_model(
            data_x[400:],
            model,
            freq_range=(1e-4, 5e-1),
            fs=fs,
            freq_res=1e-4,
            threshold=1e-47,
            name=f"test_michelson_2_doppler:{name}",
            confidence=0.99,
        )


def test_factorized_michelson_2_doppler():
    """Test that the entire factorized second-generation Michelson combinations reduces laser noise."""
    fs = 3.2
    data_ln, delays = read_from_lisanode(
        BASE_PATH + "lisa-sixlasers-lasernoise-keplerianorbits-doppler.h5"
    )
    data = pytdi.interface.Data(data_ln, delays, fs=3.2)
    etas = pytdi.intervar.compute_etas(data, unit="frequency")
    names = ["X2", "Y2", "Z2"]
    arms = [
        (("d_12", "d_21"), ("d_13", "d_31")),
        (("d_21", "d_12"), ("d_23", "d_32")),
        (("d_31", "d_13"), ("d_32", "d_23")),
    ]
    for i, (name, arm) in enumerate(zip(names, arms)):
        data_x = pytdi.michelson.compute_factorized_michelson(
            data, etas, rot=i, generation=2, unit="frequency"
        )
        model = lambda freq, arm=arm: flexing_filtering_model(freq, arm, delays, fs)
        psd_model(
            data_x[400:],
            model,
            freq_range=(1e-4, 5e-1),
            fs=fs,
            freq_res=1e-4,
            threshold=1e-47,
            name=f"test_factorized_michelson_2_doppler:{name}",
            confidence=0.99,
        )
