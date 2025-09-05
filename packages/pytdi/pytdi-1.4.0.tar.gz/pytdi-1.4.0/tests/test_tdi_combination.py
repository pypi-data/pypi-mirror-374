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
Tests for `TDICombination` class.

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

import numpy as np
from pytest import approx, raises

from pytdi import TDICombination

toymodel = {
    "y_12": [(-1, []), (1, ["D_21"])],
    "y_21": [(1, []), (-1, ["D_12"])],
}


def test_init():
    """Check components of a combination are correctly initialized."""
    combination = TDICombination(toymodel)
    assert combination.components == toymodel


def test_measurements():
    """Check that `measurements` returns the correct set of measurements."""
    combination = TDICombination(
        {
            "y_12": [(-1, []), (1, ["D_21", "A_21"])],
            "y_21": [(1, []), (-1, ["D_12", "A_12"])],
        }
    )
    assert combination.measurements == set(["y_12", "y_21"])


def test_delays():
    """Check that `delays` returns the correct set of delay operators."""
    combination = TDICombination(
        {
            "y_12": [(-1, []), (1, ["D_21", "A_21"])],
            "y_21": [(1, []), (-1, ["D_12", "A_12"])],
        }
    )
    assert combination.delays == set(["D_12", "D_21"])


def test_advancements():
    """Check that `advancements` returns the correct set of advancement operators."""
    combination = TDICombination(
        {
            "y_12": [(-1, []), (1, ["D_21", "A_21"])],
            "y_21": [(1, []), (-1, ["D_12", "A_12"])],
        }
    )
    assert combination.advancements == set(["A_12", "A_21"])


def test_transformed():
    """Check that `transformed()` returns a new combination with correct mapping."""
    combination = TDICombination(toymodel)
    with raises(ValueError):
        combination.transformed({})
        combination.transformed({1: 2})
        combination.transformed({1: 1, 2: 1})
    assert combination.transformed({1: 1, 2: 2}) == combination
    assert combination.transformed({1: 2, 2: 1}).components == {
        "y_21": [(-1, []), (1, ["D_12"])],
        "y_12": [(1, []), (-1, ["D_21"])],
    }


def test_simplify():
    """Check that `simplified()` returns an equivalent simplified combination."""
    assert TDICombination(toymodel).simplified().components == {
        "y_12": [(-1, []), (1, ["D_21"])],
        "y_21": [(-1, ["D_12"]), (1, [])],
    }

    combination = TDICombination(
        {
            "y_12": [
                (1.0, []),
                (2.0, []),
                (-3.5, ["A_21", "D_12"]),
                (0.0, ["D_12", "D_21"]),
            ],
            "y_21": [],
        }
    )
    assert combination.simplified().components == {"y_12": [(-0.5, [])]}


def test_add_tdi_combination():
    """Check that addition of two combination is the merger of their components.."""
    combination1 = TDICombination({"y_12": [(1.0, [])]})
    combination2 = TDICombination({"y_12": [(2.0, [])]})
    combination3 = TDICombination({"y_12": [(1.0, ["D_12"])]})
    combination4 = TDICombination({"x_12": [(1.0, ["D_21"])]})
    assert (combination1 + combination2).components == {"y_12": [(3.0, [])]}
    assert (combination1 + combination3).components == {
        "y_12": [(1.0, []), (1.0, ["D_12"])]
    }
    assert (combination1 + combination4).components == {
        "x_12": [(1.0, ["D_21"])],
        "y_12": [(1.0, [])],
    }


def test_subtract():
    """Check subtraction of two combinations."""
    combination1 = TDICombination({"y_12": [(1.0, [])]})
    combination2 = TDICombination({"y_12": [(2.0, [])]})
    combination3 = TDICombination({"y_12": [(1.0, ["D_12"])]})
    combination4 = TDICombination({"x_12": [(1.0, ["D_21"])]})
    assert combination1 - combination1 == TDICombination({})
    assert combination2 - combination2 == TDICombination({})
    assert combination3 - combination3 == TDICombination({})
    assert combination4 - combination4 == TDICombination({})
    assert (combination1 - combination2).components == {"y_12": [(-1.0, [])]}
    assert (combination1 - combination3).components == {
        "y_12": [(-1.0, ["D_12"]), (1.0, [])]
    }
    assert (combination1 - combination4).components == {
        "x_12": [(-1.0, ["D_21"])],
        "y_12": [(1.0, [])],
    }


def test_multiplication():
    """Check multiplication of a combination by a scalar and delays."""
    combination = TDICombination({"y_12": [(1.0, [])]})
    assert 1 * combination == combination
    assert 0 * combination == TDICombination({})
    assert (-1 * combination).components == {"y_12": [(-1.0, [])]}
    assert (["D_12", "D_21"] * combination).components == {
        "y_12": [(1.0, ["D_12", "D_21"])]
    }
    assert ((-1.0, ["D_12", "D_21"]) * combination).components == {
        "y_12": [(-1.0, ["D_12", "D_21"])]
    }


def test_neg():
    """Check opposite of combination."""
    combination = TDICombination(toymodel)
    assert (-combination) + combination == TDICombination({})
    assert (-combination).components == {
        "y_12": [(-1, ["D_21"]), (1, [])],
        "y_21": [(-1, []), (1, ["D_12"])],
    }


def test_composition():
    """Check composition (chaining) of combinations."""
    combination = TDICombination({"y_12": [(2.0, []), (1.0, ["D_21"])]})
    combination_y12 = TDICombination({"x_12": [(3.0, ["D_12"])]})
    assert (combination @ {"y_12": combination_y12}).components == {
        "x_12": [(3.0, ["D_21", "D_12"]), (6.0, ["D_12"])]
    }


def test_build_with_constant_delays():
    """Check computation of a combination with constant delays."""

    fs = 1.0
    size = 1000
    combination = TDICombination({"y_12": [(1, ["A_21"]), (-2, ["D_12"])]})

    def func_measurement(time):
        f_sin = 0.1
        return np.sin(2 * np.pi * f_sin * time)

    times = np.arange(size) / fs
    y12 = func_measurement(times)
    d12 = 8.765

    built = combination.build({"d_12": d12}, fs)
    result = built({"y_12": y12}, unit="phase")
    expected = func_measurement(times + d12) - 2 * func_measurement(times - d12)
    assert result[50:-50] == approx(expected[50:-50])


def test_build_with_variable_delays():
    """Check computation of a combination with variable delays."""

    fs = 1.0
    size = 1000
    combination = TDICombination({"y_12": [(1, []), (-2, ["D_12"])]})

    def func_measurement(time):
        f_sin = 0.1
        return np.sin(2 * np.pi * f_sin * time)

    def func_delays(time):
        slope, offset = 0.1, 0.0
        return slope * time + offset

    times = np.arange(size) / fs
    y12 = func_measurement(times)
    d12 = func_delays(times)

    built = combination.build({"d_12": d12}, fs)
    result = built({"y_12": y12}, unit="phase")
    expected = func_measurement(times) - 2 * func_measurement(
        times - func_delays(times)
    )
    assert result[50:-50] == approx(expected[50:-50])


def test_build_with_variable_delays_and_advancements():
    """Check computation of a combination with variable delays and advancements."""

    fs = 1.0
    size = 1000
    combination = TDICombination({"y_12": [(1, []), (-2, ["A_21", "D_12"])]})

    def func_measurement(time):
        f_sin = 0.1
        return np.sin(2 * np.pi * f_sin * time)

    def func_delays(time):
        slope, offset = 0.1, 0.0
        return slope * time + offset

    times = np.arange(size) / fs
    data = func_measurement(times)
    d12 = func_delays(times)

    built = combination.build({"d_12": d12}, fs, maxiter=100)
    result = built({"y_12": data}, unit="phase")
    expected = -func_measurement(times)
    assert result[50:-150] == approx(expected[50:-150])


def test_build_with_linear_delays_constant_delay_derivatives():
    """Check computation of a combination with linear delays and constant derivatives."""

    fs = 1.0
    size = 1000
    combination = TDICombination({"y_12": [(1, ["A_21"]), (-2, ["D_12"])]})

    def func_measurement(time):
        f_sin = 0.1
        return np.sin(2 * np.pi * f_sin * time)

    offset, slope = 0.0, 0.1

    def func_delays(time):
        return offset + slope * time

    def func_advancements(time):
        return (offset + slope * time) / (1 - slope)

    times = np.arange(size) / fs
    y12 = func_measurement(times)
    d12 = func_delays(times)

    built = combination.build(
        {"d_12": d12}, fs, delay_derivatives={"d_12": slope}, maxiter=100
    )
    result = built({"y_12": y12}, unit="frequency")
    expected = (1 + slope / (1 - slope)) * func_measurement(
        times + func_advancements(times)
    ) - 2 * (1 - slope) * func_measurement(times - func_delays(times))
    assert result[150:-150] == approx(expected[150:-150])


def test_build_with_variable_delays_variable_delay_derivatives():
    """Check computation of a combination with variable delays and variable derivatives."""

    fs = 1.0
    size = 1000
    combination = TDICombination({"y_12": [(1, ["A_21"]), (-2, ["D_12"])]})

    def func_measurement(time):
        fsig = 0.1
        return np.sin(2 * np.pi * fsig * time)

    offset, acceleration = 5.0, 0.00001

    def func_delays(time):
        return offset + acceleration * time**2 / 2

    def func_delay_derivatives(time):
        return acceleration * time

    def func_advancements(time):
        return (
            1
            - acceleration * time
            - np.sqrt(1 - 2 * offset * acceleration - 2 * acceleration * time)
        ) / acceleration

    def func_advancement_derivatives(time):
        return 1 / np.sqrt(1 - 2 * offset * acceleration - 2 * acceleration * time) - 1

    times = np.arange(size) / fs
    y12 = func_measurement(times)
    d12 = func_delays(times)
    dotd12 = func_delay_derivatives(times)

    built = combination.build(
        {"d_12": d12}, fs, delay_derivatives={"d_12": dotd12}, maxiter=100
    )
    result = built({"y_12": y12}, unit="frequency")
    expected = (1 + func_advancement_derivatives(times)) * func_measurement(
        times + func_advancements(times)
    ) - 2 * (1 - func_delay_derivatives(times)) * func_measurement(
        times - func_delays(times)
    )
    assert result[150:-150] == approx(expected[150:-150])
