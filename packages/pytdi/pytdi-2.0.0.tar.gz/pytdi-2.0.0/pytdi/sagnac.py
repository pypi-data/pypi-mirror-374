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
Defines TDI first-and-second-generation Sagnac variables.

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

from . import core, intervar

#: First-generation :math:`\alpha_1` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ALPHA1_ETA = core.LISATDICombination.from_string("1321 -1321")

#: First-generation :math:`\beta_1` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
BETA1_ETA = ALPHA1_ETA.rotated()

#: First-generation :math:`\gamma_1` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
GAMMA1_ETA = BETA1_ETA.rotated()

#: First-generation :math:`\zeta_1` fully-symmetric Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ZETA1_ETA = core.LISATDICombination(
    {
        "eta_12": [(1, ["D_23"])],
        "eta_23": [(1, ["D_31"])],
        "eta_31": [(1, ["D_12"])],
        "eta_13": [(-1, ["D_32"])],
        "eta_32": [(-1, ["D_21"])],
        "eta_21": [(-1, ["D_13"])],
    }
)

#: First-generation :math:`\alpha_1` Sagnac combination.
#:
#: This combination is the composition of ``ALPHA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ALPHA1 = ALPHA1_ETA @ intervar.ETA_SET

#: First-generation :math:`\beta_1` Sagnac combination.
#:
#: This combination is the composition of ``BETA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
BETA1 = BETA1_ETA @ intervar.ETA_SET

#: First-generation :math:`\gamma_1` Sagnac combination.
#:
#: This combination is the composition of ``GAMMA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
GAMMA1 = GAMMA1_ETA @ intervar.ETA_SET

#: First-generation :math:`\zeta_1` fully-symmetric Sagnac combination.
#:
#: This combination is the composition of ``ZETA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ZETA1 = ZETA1_ETA @ intervar.ETA_SET

#: Second-generation :math:`\alpha_2` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ALPHA2_ETA = core.LISATDICombination.from_string("1231321 -1321231")

#: Second-generation :math:`\beta_2` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
BETA2_ETA = ALPHA2_ETA.rotated()

#: Second-generation :math:`\gamma_2` Sagnac combination.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
GAMMA2_ETA = BETA2_ETA.rotated()

#: Second-generation :math:`\zeta_{21}` fully-symmetric Sagnac comb. of first kind.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ZETA21_ETA = core.LISATDICombination(
    {
        "eta_12": [(1, ["D_23", "D_32"]), (-1, ["D_13", "D_21", "D_32"])],
        "eta_23": [(1, ["D_32", "D_13"]), (-1, ["D_12", "D_31", "D_13"])],
        "eta_31": [(1, ["D_23", "D_12"]), (-1, ["D_13", "D_21", "D_12"])],
        "eta_13": [(1, ["D_12", "D_31", "D_23"]), (-1, ["D_32", "D_23"])],
        "eta_32": [(1, ["D_13", "D_21", "D_12"]), (-1, ["D_23", "D_12"])],
        "eta_21": [(1, ["D_12", "D_31", "D_13"]), (-1, ["D_32", "D_13"])],
    }
)

#: Second-generation :math:`\zeta_{22}` fully-symmetric Sagnac comb. of second kind.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ZETA22_ETA = ZETA21_ETA.rotated()

#: Second-generation :math:`\zeta_{23}` fully-symmetric Sagnac comb. of third kind.
#:
#: This combination is defined as a function of the :math:`\eta` intermediary
#: variables. Use them with the inter-spacecraft beatnotes if you want to
#: bypass intermediary variables.
ZETA23_ETA = ZETA22_ETA.rotated()

#: Second-generation :math:`\alpha_2` Sagnac combination.
#:
#: This combination is the composition of ``ALPHA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ALPHA2 = ALPHA2_ETA @ intervar.ETA_SET

#: Second-generation :math:`\beta_2` Sagnac combination.
#:
#: This combination is the composition of ``BETA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
BETA2 = BETA2_ETA @ intervar.ETA_SET

#: Second-generation :math:`\gamma_2` Sagnac combination.
#:
#: This combination is the composition of ``GAMMA1_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
GAMMA2 = GAMMA2_ETA @ intervar.ETA_SET

#: Second-generation :math:`\zeta_{21}` fully-symmetric Sagnac comb. of first kind.
#:
#: This combination is the composition of ``ZETA21_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ZETA21 = ZETA21_ETA @ intervar.ETA_SET

#: Second-generation :math:`\zeta_{22}` fully-symmetric Sagnac comb. of second kind.
#:
#: This combination is the composition of ``ZETA21_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ZETA22 = ZETA22_ETA @ intervar.ETA_SET

#: Second-generation :math:`\zeta_{23}` fully-symmetric Sagnac comb. of third kind.
#:
#: This combination is the composition of ``ZETA21_ETA`` and the intermediary
#: variables. Therefore, it is function of the beatnote measurements.
ZETA23 = ZETA23_ETA @ intervar.ETA_SET


def compute_factorized_sagnac(
    data, etas=None, *, rot=0, order=45, delay_order=5, generation=2, unit="frequency"
):
    r"""Numerically optimized computation of the Sagnac variables.

    These combinations can be factorized and evaluated in multiple steps. This
    reduces computation time (less delays to compute) and in some instances
    also improves numerical precision if intermediary results are already small.

    First-generation Sagnac combinations only use each :math:`\eta` once,
    so they cannot be factorized. However, the :math:`\eta_{ij}` can be
    pre-computed,

    .. math::

        \alpha_1 ={}&
        (\eta_{12} + \delay_{12} \eta_{23} + \delay_{123} \eta_{31}) \\
        - (\eta_{13} + \delay_{13} \eta_{32} + \delay_{132} \eta_{21}).

    For second-generation Sagnac combinations, we can instead write

    .. math::

        alpha2 ={}& (1 - \delay_{1321})
        (\eta_{12} + \delay_{12} \eta_{23} + \delay_{123} \eta_{31}) \\
        &- (1 - \delay_{1231})
        (\eta_{13} + \delay_{13} \eta_{32} + \delay_{132} \eta_{21}).

    We first define the single circle round-trips,

    .. math::

        \text{beam}_1 &= \eta_{12} + \delay_{12} \eta_{23} + \delay_{123} \eta_{31}, \\
        \text{beam}_2 &= \eta_{13} + \delay_{13} \eta_{32} + \delay_{132} \eta_{21}.

    In the case of :math:`\alpha_1`, we directly compute the result

    .. math:: \text{beam}_1 - \text{beam}_2,

    and for :math:`\alpha_2`,

    .. math:: (1 - \delay_{1321}) \text{beam}_1 - (1 - \delay_{1231}) \text{beam}_2.

    Note that the signs in these combinations are chosen to agree with the
    existing conventions in PyTDI and the LDC.

    Args:
        data (pytdi.interface.Data): data object
        etas (np.ndarray): pre-computed :math:`\eta_{ij}` intermediary variables
        rot (int): rotation of indices for :math:`\alpha, \beta, \gamma`
        order (int): interpolation order to evaluate measurements
        delay_order (int): interpolation order to evaluate delays
        unit (str): unit of input data, either 'frequency' or 'phase'

    Returns:
        (np.ndarray) Evaluated TDI Sagnac combination.
    """
    # Define rotations of the variables
    # We can't rely on PyTDIs built-in rotation as
    # the variable names are incompatible
    if rot == 0:
        links = ["12", "21", "23", "32", "31", "13"]
    elif rot == 1:
        links = ["23", "32", "31", "13", "12", "21"]
    elif rot == 2:
        links = ["31", "13", "12", "21", "23", "32"]
    else:
        raise ValueError(f"rot must be 0, 1 or 2 (got {rot})")

    # IFOs measuring single transponder
    # Use pre-computed etas if provided
    if etas is not None:
        beam_1 = core.LISATDICombination(
            {
                f"eta_{links[0]}": [(1, [])],
                f"eta_{links[2]}": [(1, [f"D_{links[0]}"])],
                f"eta_{links[4]}": [(1, [f"D_{links[0]}", f"D_{links[2]}"])],
            }
        ).build(**data.args, order=delay_order)(etas, order=order, unit=unit)
        beam_2 = core.LISATDICombination(
            {
                f"eta_{links[5]}": [(1, [])],
                f"eta_{links[3]}": [(1, [f"D_{links[5]}"])],
                f"eta_{links[1]}": [(1, [f"D_{links[5]}", f"D_{links[3]}"])],
            }
        ).build(**data.args, order=delay_order)(etas, order=order, unit=unit)
    else:
        # Use ETA_SET to compute result from IFO measurements
        beam_1 = (
            core.LISATDICombination(
                {
                    f"eta_{links[0]}": [(1, [])],
                    f"eta_{links[2]}": [(1, [f"D_{links[0]}"])],
                    f"eta_{links[4]}": [(1, [f"D_{links[0]}", f"D_{links[2]}"])],
                }
            )
            @ intervar.ETA_SET
        ).build(**data.args, order=delay_order)(
            data.measurements, order=order, unit=unit
        )
        beam_2 = (
            core.LISATDICombination(
                {
                    f"eta_{links[5]}": [(1, [])],
                    f"eta_{links[3]}": [(1, [f"D_{links[5]}"])],
                    f"eta_{links[1]}": [(1, [f"D_{links[5]}", f"D_{links[3]}"])],
                }
            )
            @ intervar.ETA_SET
        ).build(**data.args, order=delay_order)(
            data.measurements, order=order, unit=unit
        )

    if generation == 1:
        # Full combination
        result = beam_1 - beam_2
    elif generation == 2:
        # Full combination
        result = core.LISATDICombination(
            {
                "beam_1": [
                    (1, []),
                    (-1, [f"D_{links[5]}", f"D_{links[3]}", f"D_{links[1]}"]),
                ],
                "beam_2": [
                    (-1, []),
                    (1, [f"D_{links[0]}", f"D_{links[2]}", f"D_{links[4]}"]),
                ],
            }
        ).build(**data.args, order=delay_order)(
            {"beam_1": beam_1, "beam_2": beam_2}, order=order, unit=unit
        )
    else:
        raise ValueError(f"invalid generation '{generation}', must be 1 or 2")

    return result
