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
Defines TDI first-and-second-generation Michelson variables.

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
    Olaf Hartwig <olaf.hartwig@aei.mpg.de>
"""

from . import core, intervar

#: First-generation :math:`X_1` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
X1_ETA = core.LISATDICombination.from_string("12131 -12131")

#: First-generation :math:`Y_1` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
Y1_ETA = X1_ETA.rotated()


#: First-generation :math:`Z_1` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
Z1_ETA = Y1_ETA.rotated()

#: First-generation :math:`X_1` Michelson combination.
#:
#: This combination is the composition of ``X1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
X1 = X1_ETA @ intervar.ETA_SET

#: First-generation :math:`Y_1` Michelson combination.
#:
#: This combination is the composition of ``Y1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
Y1 = Y1_ETA @ intervar.ETA_SET

#: First-generation :math:`Z_1` Michelson combination.
#:
#: This combination is the composition of ``Z1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
Z1 = Z1_ETA @ intervar.ETA_SET


#: Second-generation :math:`X_2` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
X2_ETA = core.LISATDICombination.from_string("131212131 -121313121")

#: Second-generation :math:`Y_2` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
Y2_ETA = X2_ETA.rotated()

#: Second-generation :math:`Z_2` Michelson combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
Z2_ETA = Y2_ETA.rotated()

#: Second-generation :math:`X_2` Michelson combination.
#:
#: This combination is the composition of ``X2_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
X2 = X2_ETA @ intervar.ETA_SET

#: Second-generation :math:`Y_2` Michelson combination.
#:
#: This combination is the composition of ``Y2_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
Y2 = Y2_ETA @ intervar.ETA_SET

#: Second-generation :math:`Z_2` Michelson combination.
#:
#: This combination is the composition of ``Z2_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
Z2 = Z2_ETA @ intervar.ETA_SET


def compute_factorized_michelson(
    data, etas=None, *, rot=0, order=45, delay_order=5, generation=2, unit="frequency"
):
    r"""Numerically-optimized computation of the Michelson variables.

    These combinations can be factorized and evaluated in multiple steps. This
    reduces computation time (less delays to compute) and in some instances
    also improves numerical precision if intermediary results are already small.

    For first-generation combinations, we can write

    .. math::

        X_1 ={}& (1 - \delay_{121})(\eta_{13} + \delay_{13} \eta_{31}) \\
        &- (1 - \delay_{131}) (\eta_{12} + \delay_{12} \eta_{21}).

    Second-generations combinations can instead be written as

    .. math::

        X_2 ={}& (1 - \delay_{121} - \delay_{12131} + \delay_{1312121})
        (\eta_{13} + \delay_{13} \eta_{31}) \\
        &- (1 - \delay_{131} - \delay_{13121} + \delay_{1213131})
        (\eta_{12} + \delay_{12} \eta_{21}).

    We first define the single round-trips (transponder),

    .. math::

        a_1 = \eta_{12} + \delay_{12} \eta_{21},
        a2 = \eta_{13} + \delay_{13} \eta_{31}.

    In the case of X1, we directly compute the result

    .. math:: (\delay_{131} - 1) a_1 - (\delay_{121} - 1) a_2.

    For X2, we first compute two-arm roundtrip

    .. math::

        r_1 = a_1 + \delay_{121} a_2,
        r_2 = \delay_{131} a_1 + a_2,

    and then compute the final expression

    .. math:: (\delay_{13121} - 1) r_1 - (\delay_{12131} - 1) r_2.

    Note that the signs in these combinations are chosen to agree with the
    existing conventions in PyTDI and the LDC.

    Args:
        data (pytdi.interface.Data): data object
        etas (np.ndarray): pre-computed :math:`\eta_{ij}` intermediary variables
        rot (int): rotation of indices for :math:`X, Y, Z`
        order (int): interpolation order to evaluate measurements
        delay_order (int): interpolation order to evaluate delays
        unit (str): unit of the input data, either 'frequency' or 'phase'

    Returns:
        (np.ndarray) Evaluated TDI Michelson combination.
    """
    # Define rotations of the variables
    # We can't rely on PyTDIs built-in rotation as
    # the variable names are incompatible
    if rot == 0:
        links = ["12", "21", "13", "31"]
    elif rot == 1:
        links = ["23", "32", "21", "12"]
    elif rot == 2:
        links = ["31", "13", "32", "23"]
    else:
        raise ValueError(f"rot must be 0, 1 or 2 (got {rot})")

    # IFOs measuring single transponder
    # Use pre-computed etas if provided
    if etas is not None:
        x_arm_1 = core.LISATDICombination(
            {f"eta_{links[0]}": [(1, [])], f"eta_{links[1]}": [(1, [f"D_{links[0]}"])]}
        ).build(**data.args, order=delay_order)(etas, order=order, unit=unit)
        x_arm_2 = core.LISATDICombination(
            {f"eta_{links[2]}": [(1, [])], f"eta_{links[3]}": [(1, [f"D_{links[2]}"])]}
        ).build(**data.args, order=delay_order)(etas, order=order, unit=unit)
    else:
        # Use ETA_SET to compute result from IFO measurements
        x_arm_1 = (
            core.LISATDICombination(
                {
                    f"eta_{links[0]}": [(1, [])],
                    f"eta_{links[1]}": [(1, [f"D_{links[0]}"])],
                }
            )
            @ intervar.ETA_SET
        ).build(**data.args, order=delay_order)(
            data.measurements, order=order, unit=unit
        )
        x_arm_2 = (
            core.LISATDICombination(
                {
                    f"eta_{links[2]}": [(1, [])],
                    f"eta_{links[3]}": [(1, [f"D_{links[2]}"])],
                }
            )
            @ intervar.ETA_SET
        ).build(**data.args, order=delay_order)(
            data.measurements, order=order, unit=unit
        )

    if generation == 1:
        # Full combination
        result = core.LISATDICombination(
            {
                "x_arm_1": [(-1, []), (1, [f"D_{links[2]}", f"D_{links[3]}"])],
                "x_arm_2": [(1, []), (-1, [f"D_{links[0]}", f"D_{links[1]}"])],
            }
        ).build(**data.args, order=delay_order)(
            {"x_arm_1": x_arm_1, "x_arm_2": x_arm_2},
            order=order,
            unit=unit,
        )
    elif generation == 2:
        # IFOs measuring full roundtrip along both arms
        roundtrip_1 = core.LISATDICombination(
            {"arm_a": [(1, [])], "arm_b": [(1, [f"D_{links[0]}", f"D_{links[1]}"])]}
        ).build(**data.args, order=delay_order)(
            {"arm_a": x_arm_1, "arm_b": x_arm_2}, order=order, unit=unit
        )
        roundtrip_2 = core.LISATDICombination(
            {"arm_a": [(1, [f"D_{links[2]}", f"D_{links[3]}"])], "arm_b": [(1, [])]}
        ).build(**data.args, order=delay_order)(
            {"arm_a": x_arm_1, "arm_b": x_arm_2}, order=order, unit=unit
        )

        # Full combination
        result = core.LISATDICombination(
            {
                "roundtrip_a": [
                    (-1, []),
                    (
                        1,
                        [
                            f"D_{links[2]}",
                            f"D_{links[3]}",
                            f"D_{links[0]}",
                            f"D_{links[1]}",
                        ],
                    ),
                ],
                "roundtrip_b": [
                    (1, []),
                    (
                        -1,
                        [
                            f"D_{links[0]}",
                            f"D_{links[1]}",
                            f"D_{links[2]}",
                            f"D_{links[3]}",
                        ],
                    ),
                ],
            }
        ).build(**data.args, order=delay_order)(
            {"roundtrip_a": roundtrip_1, "roundtrip_b": roundtrip_2},
            order=order,
            unit=unit,
        )
    else:
        raise ValueError(f"invalid generation '{generation}', must be 1 or 2")

    return result
