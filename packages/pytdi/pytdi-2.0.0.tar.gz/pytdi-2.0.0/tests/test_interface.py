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
Test PyTDI's interfaces to other modules through the :class:`pytdi.Data` class.
"""

from h5py import File
from pytest import approx

from pytdi import Data
from pytdi.michelson import X1


def test_gw_file_1_1():
    """Test that we can read GW files v1.1 with orbit files v1.0.2.

    Test GW file can be generated using LISA GW Response and the following script.

        from h5py import File
        from lisagwresponse import GalacticBinary

        orbits = 'tests/keplerian-orbits-1-0-2.h5'
        with File(orbits, 'r') as f:
            t0 = f.attrs['t0'] + 10

        galbin = GalacticBinary(
            A=1.0,
            f=1E-3,
            orbits=orbits,
            t0=t0,
            size=100,
            gw_beta=0, gw_lambda=0,
        )

        galbin.write('tests/gws-1-1.h5')
    """
    gw_file = "tests/gws-1-1.h5"
    orbit_file = "tests/keplerian-orbits-1-0-2.h5"

    with File(gw_file, "r") as gwf:

        data = Data.from_gws(gw_file, orbit_file)
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tcb")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tps")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)


def test_gw_file_2_0():
    """Test that we can read GW files v2.0 with orbit files v2.0.

    Test GW file can be generated using LISA GW Response and the following script.

        from h5py import File
        from lisagwresponse import GalacticBinary

        orbits = 'tests/keplerian-orbits-2-0.h5'
        with File(orbits, 'r') as f:
            t0 = f.attrs['t0'] + 10

        galbin = GalacticBinary(
            A=1.0,
            f=1E-3,
            orbits=orbits,
            t0=t0,
            size=100,
            gw_beta=0, gw_lambda=0,
        )

        galbin.write('tests/gws-2-0.h5')
    """
    gw_file = "tests/gws-2-0.h5"
    orbit_file = "tests/keplerian-orbits-2-0.h5"

    with File(gw_file, "r") as gwf:

        data = Data.from_gws(gw_file, orbit_file)
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tcb")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tps")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)


def test_gw_file_2_3():
    """Test that we can read GW files v2.3 with orbit files v2.3.

    Test GW file can be generated using LISA GW Response and the following script.

        from h5py import File
        from lisagwresponse import GalacticBinary

        orbits = 'tests/keplerian-orbits-2-3.h5'
        with File(orbits, 'r') as f:
            t0 = f.attrs['t0'] + 10

        galbin = GalacticBinary(
            A=1.0,
            f=1E-3,
            orbits=orbits,
            t0=t0,
            size=100,
            gw_beta=0, gw_lambda=0,
        )

        galbin.write('tests/gws-2-3.h5')
    """
    gw_file = "tests/gws-2-3.h5"
    orbit_file = "tests/keplerian-orbits-2-3.h5"

    with File(gw_file, "r") as gwf:

        data = Data.from_gws(gw_file, orbit_file)
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tcb")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)

        data = Data.from_gws(gw_file, orbit_file, gw_dataset="tps")
        X1.build(**data.args)(data.measurements)
        assert data.fs == gwf.attrs["fs"]
        for mosa in Data.MOSAS:
            assert data.measurements[f"sci_{mosa}"] != approx(0.0)
            assert data.measurements[f"sci_sb_{mosa}"] != approx(0.0)
            assert data.measurements[f"tmi_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_{mosa}"] == approx(0.0)
            assert data.measurements[f"ref_sb_{mosa}"] == approx(0.0)


def test_lisanode_file_1_4():
    """Test that we can read LISANode files v1.4.

    The test LISANode file can generated using LISANode v1.4, compiling with
    default configuration using

        lisanode run --build lisanode:LISA

    and then running (with LISA Orbits 2.0),

        ./LISA --duration 300.0 --time-origin 2073211130.8175 --orbit-path
        'esa-trailing-orbits.h5' --output 'lisanode-1-4.h5'

    """
    lisanode_file = "tests/lisanode-1-4.h5"

    with File(lisanode_file, "r") as lisanodef:

        data = Data.from_lisanode(lisanode_file)
        X1.build(**data.args)(data.measurements)
        assert data.fs == 1.0 / lisanodef["mpr_12"].attrs["dt"]
        for mosa in Data.MOSAS:
            assert all(
                data.measurements[f"sci_{mosa}"]
                == lisanodef[f"isi_c_fluctuations_{mosa}"]
            )
            assert all(
                data.measurements[f"sci_sb_{mosa}"]
                == lisanodef[f"isi_sb_fluctuations_{mosa}"]
            )
            assert all(
                data.measurements[f"tmi_{mosa}"]
                == lisanodef[f"tmi_c_fluctuations_{mosa}"]
            )
            assert all(
                data.measurements[f"ref_{mosa}"]
                == lisanodef[f"rfi_c_fluctuations_{mosa}"]
            )
            assert all(
                data.measurements[f"ref_sb_{mosa}"]
                == lisanodef[f"rfi_sb_fluctuations_{mosa}"]
            )
