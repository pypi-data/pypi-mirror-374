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
Defines convenienve functions to interface with other softwares.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

import logging

import h5py
import numpy
from packaging.version import Version
from scipy.interpolate import make_interp_spline

logger = logging.getLogger(__name__)


def _slice(data, skipped):
    """Slice data if it is an array with more than one element.

    * If ``data`` is a scalar, return the scalar.
    * If ``data`` is is one-element array, extract and return it.
    * If ``data`` is any other array, slice it according to `skipped` and return it.

    Args:
        data (scalar or array-like): input array
        skipped (bool): number of samples to skip the beginning

    Returns:
        (scalar or array-like) Sliced data
    """
    if numpy.isscalar(data):
        return data
    if data.size == 1:
        return data[0]
    return data[skipped:]


class Data:
    """Interface to load data and use them to evaluate combinations.

    The data can be loaded from various sources, including HDF5 files and
    objects, e.g.,

    .. code-block:: python

        data = Data.from_orbits('my-orbits.h5')
        data = Data.from_lisanode('my-file.h5')
        data = Data.from_instrument(i)

    The data object can then be used to build combinations, either explicitely
    or using the double-star syntax,

    .. code-block:: python

        my_combination.build(data.delays, data.fs)(data.measurements)
        my_combination.build(**data.args)(data.measurements)

    Args:
        measurements (dict): beatnote measurements
        delays (dict): delays [s]
        fs (float): sampling frequency [Hz]
        delay_derivatives (dict): delay time derivatives [s/s]
    """

    #: List of MOSA double indices.
    MOSAS = ["12", "23", "31", "13", "32", "21"]

    #: list: List of valid measurements.
    MEASUREMENTS = [
        *[f"sci_{mosa}" for mosa in MOSAS],
        *[f"tmi_{mosa}" for mosa in MOSAS],
        *[f"ref_{mosa}" for mosa in MOSAS],
        *[f"sci_sb_{mosa}" for mosa in MOSAS],
        *[f"ref_sb_{mosa}" for mosa in MOSAS],
    ]

    LISANODE_FLUCTUATIONS = {
        **{f"sci_{mosa}": f"isi_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tmi_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"rfi_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isi_sb_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"rfi_sb_fluctuations_{mosa}" for mosa in MOSAS},
    }

    LISANODE_OFFSETS = {
        **{f"sci_{mosa}": f"isi_c_offsets_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tmi_c_offsets_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"rfi_c_offsets_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isi_sb_offsets_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"rfi_sb_offsets_{mosa}" for mosa in MOSAS},
    }

    LISANODE_TOTALFREQS = {
        **{f"sci_{mosa}": f"isi_c_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tmi_c_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"rfi_c_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isi_sb_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"rfi_sb_{mosa}" for mosa in MOSAS},
    }

    LISANODE_MPRS = {f"d_{mosa}": f"mpr_{mosa}" for mosa in MOSAS}

    LISANODE_FLUCTUATIONS_PRE_V1_4 = {
        **{f"sci_{mosa}": f"isc_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tm_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"ref_c_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isc_sb_fluctuations_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"ref_sb_fluctuations_{mosa}" for mosa in MOSAS},
    }

    LISANODE_OFFSETS_PRE_V1_4 = {
        **{f"sci_{mosa}": f"isc_c_frequency_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tm_c_frequency_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"ref_c_frequency_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isc_sb_frequency_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"ref_sb_frequency_{mosa}" for mosa in MOSAS},
    }

    LISANODE_TOTALFREQS_PRE_V1_4 = {
        **{f"sci_{mosa}": f"isc_c_{mosa}" for mosa in MOSAS},
        **{f"tmi_{mosa}": f"tm_c_{mosa}" for mosa in MOSAS},
        **{f"ref_{mosa}": f"ref_c_{mosa}" for mosa in MOSAS},
        **{f"sci_sb_{mosa}": f"isc_sb_{mosa}" for mosa in MOSAS},
        **{f"ref_sb_{mosa}": f"ref_sb_{mosa}" for mosa in MOSAS},
    }

    def __init__(self, measurements, delays, fs, delay_derivatives=None):
        logger.info("Initializing data object")

        self.measurements = measurements
        self.delays = delays
        self.fs = fs
        self.delay_derivatives = delay_derivatives

    @property
    def args(self):
        """Return dict of arguments for :meth:`pytdi.TDICombination.build`.

        This includes the delay derivatives if available.

        Returns:
            dict: Dictionary of delays, sampling frequency, and delay derivatives.
        """
        return {
            "delays": self.delays,
            "fs": self.fs,
            "delay_derivatives": self.delay_derivatives,
        }

    def compute_delay_derivatives(self):
        """Compute delay derivatives from delays.

        We use a simple two-point numerical derivative, using :meth:`numpy.gradient`.
        """
        self.delay_derivatives = {}
        logger.info("Computing delay derivatives")
        for key, delay in self.delays.items():
            self.delay_derivatives[key] = numpy.gradient(delay, 1 / self.fs)

    @classmethod
    def from_orbits(cls, path, fs, t0="orbits", dataset="tps/ppr", **kwargs):
        """Load delays from an `orbit file`__ with custom measurement data.

        .. __: https://gitlab.in2p3.fr/lisa-simulation/orbits

        **Delays** are taken as the proper pseudoranges (PPRs) in the receiver
        spacecraft proper times (TPS) if ``dataset='tps/ppr'``. If
        ``dataset='tcb/ltt'``, they are taken as the light travel times (LTTs)
        in the barycentric time frame (TCB).

        **Delay derivatives** are computed using
        :meth:`pytdi.Data.compute_delay_derivatives`.

        At least one **measurement** must be specified as a Numpy array using
        keyword arguments. Valid keywords are specified in
        :attr:`pytdi.Data.MEASUREMENTS` and include carrier and upper-sideband
        SCI and REF beatnotes, as well as carrier TMI beatnotes.

        Non-specified measurements are set to 0.

        Example:
            Use this method as follows.

            .. code-block:: python

                data = Data.from_orbits('orbits.h5', fs=4, sci_12=my_array)

        Args:
            path (str):
                path to orbit file
            fs (float):
                measurement sampling frequency [Hz]
            t0 (float):
                measurement initial time [s], or ``'orbits'`` to match that of
                orbit file
            dataset (str):
                orbit dataset to use, either ``'tps/ppr'`` or ``'tcb/ltt'``
            **kwargs:
                non-vanishing measurements, keys must be in
                :attr:`pytdi.Data.MEASUREMENTS`

        Raises:
            TypeError: if a keyword argument is not a valid measurement
            ValueError: if no measurement specified

        Returns:
            :class:`pytdi.Data`: A data object.
        """
        # Check that we have at least one measurement
        if not kwargs:
            raise ValueError("from_orbits() requires at least one measurement")
        # Check that keywords are valid measurements
        size = 0
        for key, arg in kwargs.items():
            if isinstance(arg, (int, float)):
                size = max(size, 1)
            else:
                size = max(size, len(arg))
            if key not in cls.MEASUREMENTS:
                raise TypeError(f"from_orbits() has invalid measurement key '{key}'")
        # Check that `dataset` is valid
        if dataset not in ["tps/ppr", "tcb/ltt"]:
            raise ValueError(f"invalid dataset '{dataset}', use 'tps/ppr' or 'tcb/ltt'")
        # Check orbit file version
        with h5py.File(path, "r") as orbitf:
            version = Version(orbitf.attrs["version"])
            logger.debug("Using orbit file version %s", version)
            if version.is_devrelease or version.local is not None:
                logger.warning("You are using an orbit file in a development version")
            if version > Version("2.3"):
                logger.warning(
                    "You are using an orbit file in a version that might "
                    "not be fully supported"
                )
        # Build time vector for interpolation
        if t0 == "orbits":
            with h5py.File(path, "r") as orbitf:
                if version >= Version("2.0.dev"):
                    t0 = float(orbitf.attrs["t0"])
                else:
                    attr = "t0" if dataset == "tcb/ltt" else "tau0"
                    t0 = float(orbitf.attrs[attr])
        logger.debug(
            "Using interpolating time vector (fs=%s, size=%s, t0=%s)", fs, size, t0
        )
        t = t0 + numpy.arange(size) / fs
        # Load orbits
        delays = {}
        logger.info("Loading orbit file '%s'", path)
        with h5py.File(path, "r") as orbitf:
            if version >= Version("2.0.dev"):
                times = (
                    orbitf.attrs["t0"]
                    + numpy.arange(orbitf.attrs["size"]) * orbitf.attrs["dt"]
                )
                values = orbitf[dataset]
                for i, mosa in enumerate(cls.MOSAS):
                    delays[f"d_{mosa}"] = make_interp_spline(times, values[:, i], 5)(t)
            else:
                times = (
                    orbitf["tcb"]["t"][:]
                    if dataset == "tcb/ltt"
                    else orbitf["tps"]["tau"][:]
                )
                for mosa in cls.MOSAS:
                    values = (
                        orbitf[f"tcb/l_{mosa}"]["tt"]
                        if dataset == "tcb/ltt"
                        else orbitf[f"tps/l_{mosa}"]["ppr"]
                    )
                    delays[f"d_{mosa}"] = make_interp_spline(times, values, 5)(t)
        # Create measurements dictionary
        measurements = {key: kwargs.get(key, 0) for key in cls.MEASUREMENTS}
        # Create instance
        data = cls(measurements, delays, fs)
        data.compute_delay_derivatives()
        return data

    @classmethod
    def from_lisanode(
        cls, path, signals="fluctuations", skipped=0, central_freq=2.816e14
    ):
        """Load delays and measurement from `LISANode`__.

        .. __: https://gitlab.in2p3.fr/j2b.bayle/LISANode

        **Delays** are taken as the measured pseudoranges (MPRs).

        **Delay derivatives** are computed using
        :meth:`pytdi.Data.compute_delay_derivatives`.

        The **measurements** dictionary is populated with carrier SCI, TMI, and
        REF beatnotes, as well as the sideband SCI and REF beatnotes. If
        ``signals='fluctuations'`` (default behavior), the frequency
        fluctuations are used; if ``signals='offsets'``, the frequency offsets
        are used; if ``signals='total'``, the total frequencies are used.

        Example:
            Use this method as follows.

            .. code-block:: python

                data = Data.from_lisanode('lisa.h5')

        Note:
            Prior to version 1.4, LISANode produced fractional frequency
            fluctuations (unit-less) that are not corrected for the beatnote
            polarity, frequency offsets in MHz and total frequencies in Hz. For
            compatibility reasons the fractional frequency fluctuations are
            beatnote corrected and converted to frequency fluctuations in Hz by
            multiplying by the sign of the offsets and the central laser
            frequency. Furthermore, the offsets are converted from MHz to Hz by
            scaling them by $10^6$.

        Args:
            path (str):
                path to LISANode output file
            signals (str):
                signal to use, one of ``'fluctuations'``, ``'offsets'``,
                ``'total'``
            skipped (bool):
                number of samples to skip the beginning
            central_freq (float):
                central laser frequency (for versions < 1.4) [Hz]

        Returns:
            :class:`pytdi.Data`: A data object, ``measurements`` are in units of
            Hz.
        """
        # pylint: disable=too-many-branches
        delays = {}
        measurements = {}
        logger.info("Opening LISANode output file '%s'", path)

        with h5py.File(path, "r") as hdf5:

            # Check version and load data
            if "version" in hdf5.attrs.keys():
                version = Version(hdf5.attrs["version"])
            else:
                version = Version("0.0")
            logger.debug("Using measurement file version %s", version)

            if version.is_devrelease or version.local is not None:
                logger.warning("You are using a LISANode file in a development version")
            if version > Version("1.4"):
                logger.warning(
                    "You are using an LISANode file in a version that might "
                    "not be fully supported"
                )

            if version >= Version("1.4.dev"):

                # Read sampling rate from MPR dataset since it is always present
                any_value = next(iter(cls.LISANODE_MPRS.values()))
                fs = 1.0 / hdf5[any_value].attrs["dt"]
                # Load measurements
                if signals == "fluctuations":
                    for key in cls.LISANODE_FLUCTUATIONS:
                        key_fluctuations = cls.LISANODE_FLUCTUATIONS[key]
                        key_offsets = cls.LISANODE_OFFSETS[key]
                        measurements[key] = hdf5[key_fluctuations][skipped:]
                elif signals == "offsets":
                    for key, key_offsets in cls.LISANODE_OFFSETS.items():
                        measurements[key] = hdf5[key_offsets][skipped:]
                elif signals == "total":
                    for key, key_totals in cls.LISANODE_TOTALFREQS.items():
                        measurements[key] = hdf5[key_totals][skipped:]
                else:
                    raise ValueError(f"invalid signals parameter '{signals}'")
                # Load MPRs
                for key, key_mprs in cls.LISANODE_MPRS.items():
                    delays[key] = hdf5[key_mprs][skipped:]
                logger.debug("Closing LISANode output file '%s'", path)

            else:

                # Read sampling rate from MPR dataset since it is always present
                any_value = next(iter(cls.LISANODE_MPRS.values()))
                fs = hdf5[any_value].attrs["sampling_frequency"][0]
                # Load measurements
                if signals == "fluctuations":
                    for key in cls.LISANODE_FLUCTUATIONS_PRE_V1_4:
                        key_fluctuations = cls.LISANODE_FLUCTUATIONS_PRE_V1_4[key]
                        key_offsets = cls.LISANODE_OFFSETS_PRE_V1_4[key]
                        # Correct for beatnote polarity and convert to Hz
                        measurements[key] = (
                            central_freq
                            * hdf5[key_fluctuations][skipped:, 1]
                            * numpy.sign(hdf5[key_offsets][skipped:, 1])
                        )
                elif signals == "offsets":
                    for key, key_offsets in cls.LISANODE_OFFSETS_PRE_V1_4.items():
                        # Convert from MHz to Hz
                        measurements[key] = 1e6 * hdf5[key_offsets][skipped:, 1]
                elif signals == "total":
                    for key, key_totals in cls.LISANODE_TOTALFREQS_PRE_V1_4.items():
                        measurements[key] = hdf5[key_totals][skipped:, 1]
                else:
                    raise ValueError(f"invalid signals parameter '{signals}'")
                # Load MPRs
                for key, key_mprs in cls.LISANODE_MPRS.items():
                    delays[key] = hdf5[key_mprs][skipped:, 1]
                logger.debug("Closing LISANode output file '%s'", path)

        # Create instance
        data = cls(measurements, delays, fs)
        data.compute_delay_derivatives()
        return data

    @classmethod
    def from_instrument(cls, instrument_or_path, signals="fluctuations", skipped=0):
        """Load delays and measurement from `LISA Instrument`__.

        .. __: https://gitlab.in2p3.fr/lisa-simulation/instrument

        **Delays** are taken as the measured pseudoranges (MPRs).

        **Delay derivatives** are computed using
        :meth:`pytdi.Data.compute_delay_derivatives`.

        The **measurements** dictionary is populated with carrier SCI, TMI, and
        REF beatnotes, as well as the sideband SCI and REF beatnote. If
        ``signals='fluctuations'`` (default behavior), the frequency
        fluctuations are used; if ``signals='offsets'``, the frequency offsets
        are used; if ``signals='total'``, the total frequencies are used.

        Example:
            Use this method with a :class:`lisainstrument.Instrument` object or
            a measurement file produced with LISA Instrument.

            .. code-block:: python

                instru = Instrument(...)
                instru.write('measuremnets.h5')

                data = Data.from_instrument(instru)
                data = Data.from_instrument('measurements.h5')

        Args:
            instrument_or_path (str or :class:`lisainstrument.Instrument`):
                instrument object or path to measurement file
            signals (str):
                signal to use, one of ``'fluctuations'``, ``'offsets'``,
                ``'total'``
            skipped (bool):
                number of samples to skip the beginning

        Returns:
            :class:`pytdi.Data`: A data object.
        """
        if isinstance(instrument_or_path, str):
            return cls._from_instrument_file(instrument_or_path, signals, skipped)
        if isinstance(instrument_or_path, object):
            return cls._from_instrument_object(instrument_or_path, signals, skipped)
        raise TypeError(f"unsupported object type '{type(instrument_or_path)}'")

    @classmethod
    def _from_instrument_object(cls, instrument, signals="fluctuations", skipped=0):
        """Load data from :class:`lisainstrument.Instrument` object.

        Args:
            instrument (:class:`lisainstrument.Instrument`:
                instrument object
            signals (str):
                signal to use, one of ``'fluctuations'``, ``'offsets'``,
                ``'total'``
            skipped (bool):
                number of samples to skip the beginning

        Returns:
            :class:`pytdi.Data`: A data object.
        """
        # pylint: disable=too-many-statements
        delays = {}
        measurements = {}
        logger.info("Loading instrument object '%s'", instrument)
        # Check that simulation has been run
        if not instrument.simulated:
            raise ValueError("simulation must be run before loading data")
        # Check version and load data
        version = Version(instrument.version)
        logger.debug("Using lisainstrument version %s", version)
        if version.is_devrelease or version.local is not None:
            logger.warning("You are using LISA Instrument in a development version")
        if version > Version("1.4"):
            logger.warning(
                "You are using LISA Instrument in a version that might "
                "not be fully supported"
            )
        if version >= Version("1.1.dev"):
            fs = instrument.fs
            for mosa in cls.MOSAS:
                # Load measurements
                if signals == "fluctuations":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isi_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.rfi_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tmi_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isi_usb_fluctuations[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.rfi_usb_fluctuations[mosa], skipped
                    )
                elif signals == "offsets":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isi_carrier_offsets[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.rfi_carrier_offsets[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tmi_carrier_offsets[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isi_usb_offsets[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.rfi_usb_offsets[mosa], skipped
                    )
                elif signals == "total":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isi_carriers[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.rfi_carriers[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tmi_carriers[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isi_usbs[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.rfi_usbs[mosa], skipped
                    )
                # Load MPRs
                delays[f"d_{mosa}"] = _slice(instrument.mprs[mosa], skipped)
        else:
            fs = instrument.fs
            for mosa in cls.MOSAS:
                # Load measurements
                if signals == "fluctuations":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isc_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.ref_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tm_carrier_fluctuations[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isc_usb_fluctuations[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.ref_usb_fluctuations[mosa], skipped
                    )
                elif signals == "offsets":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isc_carrier_offsets[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.ref_carrier_offsets[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tm_carrier_offsets[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isc_usb_offsets[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.ref_usb_offsets[mosa], skipped
                    )
                elif signals == "total":
                    measurements[f"sci_{mosa}"] = _slice(
                        instrument.isc_carriers[mosa], skipped
                    )
                    measurements[f"ref_{mosa}"] = _slice(
                        instrument.ref_carriers[mosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = _slice(
                        instrument.tm_carriers[mosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        instrument.isc_usbs[mosa], skipped
                    )
                    measurements[f"ref_sb_{mosa}"] = _slice(
                        instrument.ref_usbs[mosa], skipped
                    )
                # Load MPRs
                delays[f"d_{mosa}"] = _slice(instrument.mprs[mosa], skipped)
        # Create instance
        data = cls(measurements, delays, fs)
        data.compute_delay_derivatives()
        return data

    @classmethod
    def _from_instrument_file(cls, path, signals="fluctuations", skipped=0):
        """Load data from LISA Instrument measurement file.

        Args:
            path (str):
                path to measurement file
            signals (str):
                signal to use, one of ``'fluctuations'``, ``'offsets'``,
                ``'total'``
            skipped (bool):
                number of samples to skip the beginning

        Returns:
            :class:`pytdi.Data`: A data object.
        """
        # pylint: disable=too-many-statements
        delays = {}
        measurements = {}
        logger.info("Loading measurement file '%s'", path)
        with h5py.File(path, "r") as hdf5:
            # Check version and load data
            version = Version(hdf5.attrs["version"])
            logger.debug("Using measurement file version %s", version)
            if version.is_devrelease or version.local is not None:
                logger.warning(
                    "You are using a measurement file in a development version"
                )
            if version > Version("1.4"):
                logger.warning(
                    "You are using a measurement file in a version that might "
                    "not be fully supported"
                )
            if version >= Version("1.1.dev"):
                fs = hdf5.attrs["fs"]
                for mosa in cls.MOSAS:
                    # Load measurements
                    if signals == "fluctuations":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isi_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["rfi_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tmi_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isi_usb_fluctuations"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["rfi_usb_fluctuations"][mosa], skipped
                        )
                    elif signals == "offsets":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isi_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["rfi_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tmi_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isi_usb_offsets"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["rfi_usb_offsets"][mosa], skipped
                        )
                    elif signals == "total":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isi_carriers"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["rfi_carriers"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tmi_carriers"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isi_usbs"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["rfi_usbs"][mosa], skipped
                        )
                    # Load MPRs
                    delays[f"d_{mosa}"] = _slice(hdf5["mprs"][mosa], skipped)
            else:
                fs = hdf5.attrs["fs"]
                for mosa in cls.MOSAS:
                    # Load measurements
                    if signals == "fluctuations":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isc_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["ref_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tm_carrier_fluctuations"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isc_usb_fluctuations"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["ref_usb_fluctuations"][mosa], skipped
                        )
                    elif signals == "offsets":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isc_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["ref_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tm_carrier_offsets"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isc_usb_offsets"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["ref_usb_offsets"][mosa], skipped
                        )
                    elif signals == "total":
                        measurements[f"sci_{mosa}"] = _slice(
                            hdf5["isc_carriers"][mosa], skipped
                        )
                        measurements[f"ref_{mosa}"] = _slice(
                            hdf5["ref_carriers"][mosa], skipped
                        )
                        measurements[f"tmi_{mosa}"] = _slice(
                            hdf5["tm_carriers"][mosa], skipped
                        )
                        measurements[f"sci_sb_{mosa}"] = _slice(
                            hdf5["isc_usbs"][mosa], skipped
                        )
                        measurements[f"ref_sb_{mosa}"] = _slice(
                            hdf5["ref_usbs"][mosa], skipped
                        )
                    # Load MPRs
                    delays[f"d_{mosa}"] = _slice(hdf5["mprs"][mosa], skipped)
        # Create instance
        data = cls(measurements, delays, fs)
        data.compute_delay_derivatives()
        return data

    @classmethod
    def from_gws(
        cls, path, orbits, *, skipped=0, gw_dataset="tps", orbit_dataset="tps/ppr"
    ):
        """Load data from `LISA GW Response`__.

        .. __: https://gitlab.in2p3.fr/lisa-simulation/gw-response

        **Delays** are read from an orbit file, c.f.
        :meth:`pytdi.Data.from_orbits`. Use the parameter ``orbit_dataset`` to
        switch between proper pseudoranges and light travel times.

        **Delay derivatives** are computed using
        :meth:`pytdi.Data.compute_delay_derivatives`.

        **Measurements** are set to zero, except for the carrier and sideband
        SCI beatnotes, which are taken as the GW link responses, read from a GW
        file.

        Example:
            Use this method as follows.

            .. code-block:: python

                data = Data.from_gws('gws.h5', 'my-orbits.h5', skipped=200)

        Args:
            path (str):
                path to gravitational-wave file
            orbits (str):
                path to orbit file
            skipped (bool):
                number of samples to skip the beginning
            gw_dataset (str):
                GW dataset to use, either ``'tps'`` or ``'tcb'``
            orbit_dataset (str):
                orbit dataset to use, either ``'tps/ppr'`` or ``'tcb/ltt'``
        """
        # Warn if inconsistent GW and orbit datasets
        if (gw_dataset == "tps" and orbit_dataset != "tps/ppr") or (
            gw_dataset == "tcb" and orbit_dataset != "tcb/ltt"
        ):
            logger.warning(
                "Using inconsistent orbits and GW file datasets ('%s' and '%s')",
                orbit_dataset,
                gw_dataset,
            )

        # Load measurements
        logger.info("Loading gravitational-wave file '%s'", path)
        with h5py.File(path, "r") as gwf:
            version = Version(gwf.attrs["version"])
            logger.debug("Using GW file version %s", version)
            if version.is_devrelease or version.local is not None:
                logger.warning("You are using a GW file in a development version")
            if version > Version("2.3"):
                logger.warning(
                    "You are using a GW file in a version that might "
                    "not be fully supported"
                )
            if version >= Version("2.0.dev"):
                if gw_dataset not in gwf:
                    raise KeyError(f"cannot find dataset '{gw_dataset}' in '{path}'")
                measurements = {}
                for imosa, mosa in enumerate(cls.MOSAS):
                    measurements[f"sci_{mosa}"] = _slice(
                        gwf[f"{gw_dataset}/y"][:, imosa], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        gwf[f"{gw_dataset}/y"][:, imosa], skipped
                    )
                    measurements[f"tmi_{mosa}"] = 0.0
                    measurements[f"ref_{mosa}"] = 0.0
                    measurements[f"ref_sb_{mosa}"] = 0.0
                fs = gwf.attrs["fs"]
                t0 = gwf.attrs["t0"]
            elif version >= Version("1.1.dev"):
                if gw_dataset not in gwf:
                    raise KeyError(f"cannot find dataset '{gw_dataset}' in '{path}'")
                measurements = {}
                for mosa in cls.MOSAS:
                    measurements[f"sci_{mosa}"] = _slice(
                        gwf[f"{gw_dataset}/l_{mosa}"], skipped
                    )
                    measurements[f"sci_sb_{mosa}"] = _slice(
                        gwf[f"{gw_dataset}/l_{mosa}"], skipped
                    )
                    measurements[f"tmi_{mosa}"] = 0.0
                    measurements[f"ref_{mosa}"] = 0.0
                    measurements[f"ref_sb_{mosa}"] = 0.0
                fs = gwf.attrs["fs"]
                t0 = gwf.attrs["t0"]
            else:
                measurements = {}
                for mosa in cls.MOSAS:
                    measurements[f"sci_{mosa}"] = _slice(gwf[f"l_{mosa}"], skipped)
                    measurements[f"sci_sb_{mosa}"] = _slice(gwf[f"l_{mosa}"], skipped)
                    measurements[f"tmi_{mosa}"] = 0.0
                    measurements[f"ref_{mosa}"] = 0.0
                    measurements[f"ref_sb_{mosa}"] = 0.0
                fs = gwf.attrs["fs"]
                t0 = gwf.attrs["t0"]
        # Load delays from orbit file
        return cls.from_orbits(orbits, fs, t0, orbit_dataset, **measurements)

    def astype(self, dtype):
        """Return the same data as a particular type.

        Args:
            dtype (str or dtype): Typecode or data-type to which the array is cast.

        Returns:
            (Data) Copy of data for a particular type.
        """
        measurements = {
            key: (
                dtype(measurement)
                if numpy.isscalar(measurement)
                else measurement.astype(dtype)
            )
            for key, measurement in self.measurements.items()
        }

        delays = {
            key: dtype(delay) if numpy.isscalar(delay) else delay.astype(dtype)
            for key, delay in self.delays.items()
        }

        if self.delay_derivatives is not None:
            delay_derivatives = {
                key: (
                    dtype(derivative)
                    if numpy.isscalar(derivative)
                    else derivative.astype(dtype)
                )
                for key, derivative in self.delay_derivatives.items()
            }
        else:
            delay_derivatives = None

        return Data(
            measurements=measurements,
            delays=delays,
            delay_derivatives=delay_derivatives,
            fs=self.fs,
        )
