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
Tests for `LISATDICombination` class.

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

from pytdi import LISATDICombination

toymodel = {
    "y_12": [(-1, []), (1, ["D_12"])],
    "y_21": [(1, []), (-1, ["D_21"])],
}


def test_init():
    """Check components of a combination are correctly initialized."""
    combination = LISATDICombination(toymodel)
    assert combination.components == toymodel


def test_addition():
    """Check that components are correctly added together."""
    tdi_comb1 = LISATDICombination({"y_12": [(1, [])]})
    tdi_comb2 = LISATDICombination({"y_12": [(2, [])]})
    tdi_comb3 = LISATDICombination({"y_12": [(1, ["D_12"])]})
    tdi_comb4 = LISATDICombination({"x_23": [(1, ["D_23"])]})
    assert (tdi_comb1 + tdi_comb2).components == {"y_12": [(3, [])]}
    assert (tdi_comb1 + tdi_comb3).components == {"y_12": [(1, []), (1, ["D_12"])]}
    assert (tdi_comb1 + tdi_comb4).components == {
        "x_23": [(1, ["D_23"])],
        "y_12": [(1, [])],
    }


def test_rotatation():
    """Test rotation transformation."""
    combination = LISATDICombination(toymodel)
    assert combination.rotated(0) == combination
    assert combination.rotated() == combination.rotated(1)
    assert combination.rotated(1).components == {
        "y_23": [(-1, []), (1, ["D_23"])],
        "y_32": [(1, []), (-1, ["D_32"])],
    }
    assert combination.rotated(2).components == {
        "y_31": [(-1, []), (1, ["D_31"])],
        "y_13": [(1, []), (-1, ["D_13"])],
    }
    assert combination.rotated(3) == combination


def test_reflection():
    """Test reflection transformation."""
    combination = LISATDICombination(
        {
            "y_12": [(-1, []), (5, ["D_12"])],
            "y_23": [(-0.5, []), (1, ["D_32"])],
            "y_31": [(1, []), (-1, ["D_21"])],
        }
    )
    assert combination.reflected(1).components == {
        "y_13": [(-1, []), (5, ["D_13"])],
        "y_32": [(-0.5, []), (1, ["D_23"])],
        "y_21": [(1, []), (-1, ["D_31"])],
    }
    assert combination.reflected(2).components == {
        "y_32": [(-1, []), (5, ["D_32"])],
        "y_21": [(-0.5, []), (1, ["D_12"])],
        "y_13": [(1, []), (-1, ["D_23"])],
    }
    assert combination.reflected(3).components == {
        "y_21": [(-1, []), (5, ["D_21"])],
        "y_13": [(-0.5, []), (1, ["D_31"])],
        "y_32": [(1, []), (-1, ["D_12"])],
    }
