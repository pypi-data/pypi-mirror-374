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
Defines TDI intermediary variables ξ (xi) and η (eta).

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
    Olaf Hartwig <olaf.hartwig@aei.mpg.de>
"""

from . import core

#: :math:`\xi_{12}` spacecraft jitter-reducing intermediary variable.
XI_12 = core.LISATDICombination(
    {
        "sci_12": [(1.0, [])],
        "ref_12": [(0.5, [])],
        "ref_21": [(0.5, ["D_12"])],
        "tmi_12": [(-0.5, [])],
        "tmi_21": [(-0.5, ["D_12"])],
    }
)

#: :math:`\xi_{23}` spacecraft jitter-reducing intermediary variable.
XI_23 = XI_12.rotated()

#: :math:`\xi_{31}` spacecraft jitter-reducing intermediary variable.
XI_31 = XI_23.rotated()

#: :math:`\xi_{13}` spacecraft jitter-reducing intermediary variable.
XI_13 = XI_12.reflected(1)

#: :math:`\xi_{21}` spacecraft jitter-reducing intermediary variable.
XI_21 = XI_23.reflected(2)

#: :math:`\xi_{31}` spacecraft jitter-reducing intermediary variable.
XI_32 = XI_31.reflected(3)

#: dict: Dictionary of all 6 :math:`\xi_{ij}` variables.
#:
#: This dictionary is intended to be used for composition of combinations.
XI_SET = {
    "xi_12": XI_12,
    "xi_23": XI_23,
    "xi_31": XI_31,
    "xi_13": XI_13,
    "xi_21": XI_21,
    "xi_32": XI_32,
}

#: :math:`\eta_{12}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_12_XI = core.LISATDICombination(
    {
        "xi_12": [(1.0, [])],
        "ref_23": [(-0.5, ["D_12"])],
        "ref_21": [(0.5, ["D_12"])],
    },
    allow_reflections=False,
)

#: :math:`\eta_{23}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_23_XI = ETA_12_XI.rotated()

#: :math:`\eta_{31}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_31_XI = ETA_23_XI.rotated()

#: :math:`\eta_{13}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_13_XI = core.LISATDICombination(
    {
        "xi_13": [(1.0, [])],
        "ref_12": [(0.5, [])],
        "ref_13": [(-0.5, [])],
    },
    allow_reflections=False,
)

#: :math:`\eta_{21}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_21_XI = ETA_13_XI.rotated()

#: :math:`\eta_{32}` intermediary variable to reduce the problem to 3 lasers.
#:
#: This combination is defined as a function of :math:`\xi` measurements in
#: addition to the reference beatnotes.
ETA_32_XI = ETA_21_XI.rotated()

#: dict: Dictionary of all 6 :math:`\eta_{ij}` variables.
#:
#: The :math:`\eta_{ij}` are defined as a function of the :math:`\xi` measurements in
#: addition to the reference beatnotes.
#:
#: This dictionary is intended to be used for composition of combinations.
ETA_XI_SET = {
    "eta_12": ETA_12_XI,
    "eta_23": ETA_23_XI,
    "eta_31": ETA_31_XI,
    "eta_13": ETA_13_XI,
    "eta_21": ETA_21_XI,
    "eta_32": ETA_32_XI,
}

#: dict: Dictionary of all 6 :math:`\eta_{ij}` variables.
#:
#: The :math:`\eta_{ij}` are defined as a function of the beatnotes.
#:
#: This dictionary is intended to be used for composition of combinations.
ETA_SET = {
    "eta_12": ETA_12_XI @ XI_SET,
    "eta_23": ETA_23_XI @ XI_SET,
    "eta_31": ETA_31_XI @ XI_SET,
    "eta_13": ETA_13_XI @ XI_SET,
    "eta_21": ETA_21_XI @ XI_SET,
    "eta_32": ETA_32_XI @ XI_SET,
}


def compute_etas(data, order=45, delay_order=5, unit="frequency"):
    r"""Evaluate intermediary variables :math:`\eta_{ij}`.

    This can be used as an alternative to concatenation, to evaluate numerically
    intermediary variables and use them as input to construct other variables.
    It might save time if the same intermediary variables are used multiple times.

    Args:
        data (pytdi.interface.Data): data object
        order (int): interpolation order to evaluate measurements
        delay_order (int): interpolation order to evaluate delays
        unit (str): unit of input data, either 'frequency' or 'phase'
    """
    return {
        key: eta.build(**data.args, order=delay_order)(
            data.measurements, order=order, unit=unit
        )
        for key, eta in ETA_SET.items()
    }
