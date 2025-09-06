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

import h5py
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage
import scipy.signal
import scipy.stats

BASE_PATH = "tests/data/"
COEFFS_AA = np.load(BASE_PATH + "filter_coeffs.npy")


def filter_tf_derivative(freq, coeffs, fs):
    """Calculate squared modulus of derivative of filter transfer function.

    Args:
        freq: frequency bins to evaluate
        coeffs: filter coefficients
        fs: sampling frequency of the data [Hz]

    Returns:
        squared modulus of derivative of filter transer function
    """
    res = 0
    for i, coeff in enumerate(coeffs):
        factor = i / (10 * fs)
        res += 2 * coeff * factor * np.sin(2 * np.pi * freq * factor)
    return res**2


def psd_threshold(data, threshold, freq_range, fs=1, name=None, plotting=True):
    """Check that data is below certain threshold.

    This methods checks that the power spectral density, computed with Welch method,
    remains below a certain threshold.

    We only check the psd inside the given frequency range.

    Args:
        data: array of data given as a time series
        fs: sampling frequency of the data [Hz]
        threshold: constant threshold
        freq_range: couple (min_freq, max_freq) defining the frequency range to check
    """
    # Check that frequencies are consistent
    min_freq, max_freq = freq_range
    assert min_freq >= 0
    assert max_freq <= fs / 2
    # Compute the nperseg so that we reach the min frequency (margin of 10 samples)
    # Check that we have enough data for at least two averages
    nperseg = fs / min_freq + 10
    nseg = len(data) // nperseg
    assert nseg >= 2
    # Compute Welch method, and model
    freq, estimate = scipy.signal.welch(
        data, fs=fs, nperseg=nperseg, noverlap=0, detrend=False, window="nuttall"
    )
    # Only consider frequency range, dc and Nyquist frequency are excluded
    mask = np.logical_and(freq > min_freq, freq < max_freq)
    # Plot results
    if plotting:
        plt.figure(figsize=(16, 8))
        plt.axvline(x=min_freq, ls="--", color="grey")
        plt.axvline(x=max_freq, ls="--", color="grey")
        plt.loglog(freq, estimate, label="psd")
        plt.axhline(y=threshold, color="black", label="threshold")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power spectral density (1/Hz)")
        plt.legend(loc="upper left")
        plt.savefig(name + ".pdf")
        plt.close()

    assert np.all(estimate[mask] < threshold)


def psd_model(
    data,
    model,
    freq_range,
    fs=1,
    freq_res=None,
    threshold=0,
    confidence=0.9,
    name=None,
    plotting=True,
):
    """Check that data follows a power spectral density model.

    This methods checks that the power spectral density of the model, computed with Welch method,
    remains within the confidence interval around the model. If you specify a threshold,
    data below this level is accepted.

    We only check that the data follows the model inside the given frequency range.

    Args:
        data: array of data given as a time series
        fs: sampling frequency of the data [Hz]
        model: function returning the model PSD as a function of frequency in Hz
        freq_range: couple (min_freq, max_freq) defining the frequency range to check
        threshold: noise floor level
        confidence: confidence interval around the model

    Returns:
        True if the data follows the model, otherwise returns False.
    """

    # pylint: disable=too-many-locals
    def model_spectral_leakage(model, window, nperseg, fs):
        win = window(nperseg)
        freq = np.fft.fftshift(np.fft.fftfreq(nperseg, d=1 / fs))
        win_fft = np.fft.fft(win)
        expected = (
            scipy.ndimage.convolve1d(model(freq), np.abs(win_fft) ** 2, mode="wrap")
            / np.sum(win**2)
            / nperseg
        )
        return expected[: nperseg // 2 + 1]

    def calculate_confidence_intervall(estimate, expected, nseg, confidence):
        # Calculate the degrees of freedom
        df = 2 * nseg  # pylint: disable=invalid-name
        # Each element of df*estimate/expected is chi^2-distributed with degrees of freedom df
        # Probability that a single point is outside of the confidence interval
        alpha = 1 - confidence ** (1 / len(estimate))
        # Compute confidence interval
        ratio_lower = scipy.stats.chi2.ppf(alpha / 2, df)
        ratio_upper = scipy.stats.chi2.ppf(1 - alpha / 2, df)
        return expected / df * ratio_lower, expected / df * ratio_upper

    def plot(freq, estimate, expected, intervall, mask_valid, freq_range, threshold):
        freq_min, freq_max = freq_range
        expected_lower, expected_upper = intervall
        mask_out = np.logical_or(
            expected_lower > estimate[mask_valid], expected_upper < estimate[mask_valid]
        )
        plt.figure(figsize=(16, 8))
        plt.axvline(x=freq_min, ls="--", color="grey")
        plt.axvline(x=freq_max, ls="--", color="grey")
        plt.axhline(y=threshold, ls="--", color="grey")
        plt.loglog(freq[mask_valid], expected_lower, ls="--", color="black")
        plt.loglog(freq[mask_valid], expected_upper, ls="--", color="black")
        plt.loglog(freq, estimate, label="psd")
        plt.loglog(freq, expected, color="black", label="model")
        plt.scatter(
            freq[mask_valid][mask_out], estimate[mask_valid][mask_out], color="red"
        )
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power spectral density (1/Hz)")
        plt.legend(loc="upper left")
        plt.savefig(name + ".pdf")
        plt.close()

    # Check that frequencies are consistent
    freq_min, freq_max = freq_range
    assert freq_min >= 0
    assert freq_max <= fs / 2
    # Compute the nperseg so that we reach the min frequency (margin of 10 samples)
    # Check that we have enough data for at least two averages
    if freq_res is None:
        nperseg = int(fs / freq_min + 10)
    else:
        nperseg = int(fs / freq_res)
    nseg = len(data) // nperseg
    assert nseg >= 2
    # Compute Welch method, and model
    freq, estimate = scipy.signal.welch(
        data, fs=fs, nperseg=nperseg, noverlap=0, detrend=False, window="nuttall"
    )
    expected = model_spectral_leakage(model, scipy.signal.windows.nuttall, nperseg, fs)
    # Only consider frequency range, dc and Nyquist frequency are excluded
    mask_freq = np.logical_and(freq > freq_min, freq < freq_max)
    mask_floor = estimate > threshold
    mask_valid = np.logical_and(mask_freq, mask_floor)
    intervall = calculate_confidence_intervall(
        estimate[mask_valid], expected[mask_valid], nseg, confidence
    )

    # Plot results
    if plotting:
        plot(freq, estimate, expected, intervall, mask_valid, freq_range, threshold)

    expected_lower, expected_upper = intervall
    assert np.all(expected_lower < estimate[mask_valid])
    assert np.all(expected_upper > estimate[mask_valid])


def read_from_lisanode(path, skipped=0):
    """Read data from LISANode simulations.

    Args:
        path: path to HDF5 simulation product file
        skipped: number of samples to skip
    """
    pm_names = {
        "sci_12": "s_c_fluctuations1",
        "sci_13": "s_c_fluctuations1_p",
        "sci_23": "s_c_fluctuations2",
        "sci_21": "s_c_fluctuations2_p",
        "sci_31": "s_c_fluctuations3",
        "sci_32": "s_c_fluctuations3_p",
        "ref_12": "ref_c_fluctuations1",
        "ref_13": "ref_c_fluctuations1_p",
        "ref_23": "ref_c_fluctuations2",
        "ref_21": "ref_c_fluctuations2_p",
        "ref_31": "ref_c_fluctuations3",
        "ref_32": "ref_c_fluctuations3_p",
        "tmi_12": "tm_c_fluctuations1",
        "tmi_13": "tm_c_fluctuations1_p",
        "tmi_23": "tm_c_fluctuations2",
        "tmi_21": "tm_c_fluctuations2_p",
        "tmi_31": "tm_c_fluctuations3",
        "tmi_32": "tm_c_fluctuations3_p",
    }

    ranging_names = {
        "d_12": "ranging1",
        "d_13": "ranging1_p",
        "d_23": "ranging2",
        "d_21": "ranging2_p",
        "d_31": "ranging3",
        "d_32": "ranging3_p",
    }

    beatnotes = {
        "sci_12": -10,
        "sci_13": 10,
        "sci_23": -10,
        "sci_21": 10,
        "sci_31": -10,
        "sci_32": 10,
        "ref_12": -10,
        "ref_13": 10,
        "ref_23": -10,
        "ref_21": 10,
        "ref_31": -10,
        "ref_32": 10,
        "tmi_12": -10,
        "tmi_13": 10,
        "tmi_23": -10,
        "tmi_21": 10,
        "tmi_31": -10,
        "tmi_32": 10,
    }

    data = {}
    delays = {}
    with h5py.File(path, "r") as hdf5:
        phasemeasurements = {}
        for key, name in pm_names.items():
            phasemeasurements[key] = hdf5[name][skipped:]

        for key, beatnote in beatnotes.items():
            data[key] = phasemeasurements[key] * np.sign(beatnote)

        for key, name in ranging_names.items():
            delays[key] = hdf5[name][skipped:]

    return data, delays
