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
Defines the core class `TDICombination`, used to build combinations.

Authors:
    Martin Staab <martin.staab@aei.mpg.de>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

import copy
import itertools
import logging

from . import dsp, naming

logger = logging.getLogger(__name__)


class TDICombination:
    """Defines a time-delay interferometry (TDI) combination.

    To create a combination, pass a component dictionary containing the measurements
    as keys and time-shift polynomials as values.

    Time-shift polynomials are defined as a list of couples ``(factor, operators)``,
    where ``factor`` is a scalar factor, and ``operators`` is a list of nested
    time-shift operators.

    .. code-block:: python

        mytdi = TDICombination({
            'y_12': [(1, ['D_12', 'D_23']), (-1, ['A_12'])],
            'y_21': [(0.5, ['A_23', 'D_23'])],
        })

    Delay operators are represented by the string ``D_ij``, where :math:`i` and
    :math:`j` are the usual indices, and advancement operators by ``A_ij``.

    Args:
        components (dict): dictionary of components
    """

    def __init__(self, components):
        logger.info("Initializing combination with components '%s'", components)
        #: dict: Dictionary of components.
        #:
        #: This is the dictionary of measurements associated with the list of
        #: time-shift polynomials, as couples ``(factor, operators)``.
        #:
        #: Refer to the documentation of :class:`pytdi.TDICombination` for more
        #: information.
        self.components = dict(components)

    @classmethod
    def from_string(cls, string, var_name="eta", half_way_shift=True):
        """Initialize a combination from virtual photon paths.

        Following the geometrical interpretation proposed by M. Vallisneri, you can
        create a combination from the virtual interference of multiple beams.

        .. code-block:: python

            X1 = LISATDICombination.from_string('13121 -13121')

        Args:
            string (str): virtual photon paths
            var_name (str): name of the measurement
            half_way_shift (bool): whether to compensate for half of the shifts

        Returns:
            :obj:`pytdi.TDICombination`: A new combination.
        """
        # Vanishing combination for empty string
        if not string:
            return cls({})

        beams = string.split(" ")
        combination = cls({})
        total_shifts = []

        for beam in beams:
            if beam[0] == "-":
                is_delay = True
                beam = beam[1:]
            else:
                is_delay = False

            indices = [int(i) for i in beam]
            for i, j in zip(indices[:-1], indices[1:]):
                if is_delay:
                    combination -= total_shifts * cls(
                        {naming.join_indices(var_name, i, j): [(1, [])]}
                    )
                    total_shifts.append(naming.join_indices("D", i, j))
                else:
                    combination += total_shifts * cls(
                        {
                            naming.join_indices(var_name, j, i): [
                                (1, [naming.join_indices("A", i, j)])
                            ]
                        }
                    )
                    total_shifts.append(naming.join_indices("A", i, j))

        if half_way_shift:
            half_shifts_inv = []
            for operator in reversed(total_shifts[: len(total_shifts) // 2]):
                name, i, j = naming.split_indices(operator)
                name_inv = "D" if name == "A" else "A"
                half_shifts_inv.append(naming.join_indices(name_inv, j, i))
            return half_shifts_inv * combination
        return combination

    @property
    def measurements(self):
        """Return the set of measurements in the combination."""
        return set(self.components.keys())

    @property
    def delays(self):
        """Return the set of all delay operators in the combination."""
        delays = set()
        for polynomial in self.components.values():
            for _, operators in polynomial:
                for operator in operators:
                    name, _, _ = naming.split_indices(operator)
                    if name == "D":
                        delays.add(operator)
        return delays

    @property
    def advancements(self):
        """Return the set of all advancement operators in the combination."""
        advancements = set()
        for polynomial in self.components.values():
            for _, operators in polynomial:
                for operator in operators:
                    name, _, _ = naming.split_indices(operator)
                    if name == "A":
                        advancements.add(operator)
        return advancements

    def build_shifts(
        self, delays, fs, delay_derivatives=None, *, order=5, delta=1e-12, maxiter=10
    ):
        """Precompute total shifts.

        Nested time-shifts are iteratively constructed from atomic time-shifts.
        If `delay_derivatives=None`, no shift derivatives are returned. Otherwise,
        derivatives of all nested time-shifts are calculated and returned.

        .. code-block:: python

            shifts, derivatives = mytdi.build_shifts(
                {'d_12': t12_array, 'd_21': t21_array}, fs,
            )

        Args:
            delays (dict): dictionary of delays [s]
            fs (double): sampling frequency [Hz]
            delay_derivatives: dictionary of delay time derivatives [s/s]
            order (int): Lagrange interpolation orders for delay interpolations
            delta (float): allowed timing accuracy for advancements calculation
            maxiter (int): maximum iterations for advancements calculation

        Returns:
            tuple of :obj:`np.ndarray`: Time-shifts and time-shift derivatives.
        """
        order = int(order)
        logger.debug("Using interpolation order '%d' for time shifts", order)

        shifts = {(): 0}
        derivatives = {(): 0}
        logger.debug("Computing delays")
        for delay in self.delays:
            logger.debug("Computing delay '%s'", delay)
            # split off indices from delay operator D_ij
            _, i, j = naming.split_indices(delay)
            shifts[(delay,)] = -delays[naming.join_indices("d", i, j)]
            if delay_derivatives:
                logger.debug("Computing delay derivative '%s'", delay)
                derivatives[(delay,)] = -delay_derivatives[
                    naming.join_indices("d", i, j)
                ]
        logger.debug("Computing advancements")
        for advancement in self.advancements:
            logger.debug("Computing advancement '%s'", advancement)
            _, i, j = naming.split_indices(advancement)
            delay = naming.join_indices("d", j, i)
            shifts[(advancement,)] = dsp.calculate_advancements(
                delays[delay], fs, order, delta, maxiter
            )
            if delay_derivatives:
                logger.debug("Computing advancement derivative '%s'", advancement)
                dotd_advanced = dsp.timeshift(
                    delay_derivatives[delay], shifts[(advancement,)] * fs
                )
                derivatives[(advancement,)] = dotd_advanced / (1 - dotd_advanced)

        # Find set of all nested operators
        nested_operators = set()
        for _, polynomial in self.components.items():
            for _, operators in polynomial:
                if len(operators) > 1:
                    nested_operators.add(tuple(operators))

        for operator in nested_operators:
            # Compute the global time shift to apply
            nested_shifts = 0
            nested_derivatives = 0
            for atom in operator:
                if delay_derivatives:
                    atomic_derivatives = derivatives[(atom,)]
                    nested_derivatives += dsp.timeshift(
                        atomic_derivatives, nested_shifts * fs, order
                    )
                atomic_shifts = shifts[(atom,)]
                nested_shifts += dsp.timeshift(atomic_shifts, nested_shifts * fs, order)
            shifts[operator] = nested_shifts
            derivatives[operator] = nested_derivatives
        if delay_derivatives:
            return shifts, derivatives
        return shifts, None

    def build(
        self, delays, fs, delay_derivatives=None, *, order=5, delta=1e-12, maxiter=10
    ):
        """Prepare the combination for a set of delays.

        This function prepares the actual combination by pre-computing nested
        delays and Doppler factors. It returns a callable object that evaluates
        the combination for a given set of measurements.

        .. code-block:: python

            built = mytdi.build(
                {'d_12': t12_array, 'd_21': t21_array}, fs,
            )
            tdi_data = built(
                {'y_12': y12_array,'y_21': y21_array},
            )

        If any advancement operators are used in the combination, they are
        computed iteratively.

        Args:
            delays (dict): dictionary of delays [s]
            fs (double): sampling frequency [Hz]
            delay_derivatives: dictionary of delay time derivatives [s/s]
            order (int): Lagrange interpolation orders for delay interpolations
            delta (float): allowed timing accuracy for advancements calculation
            maxiter (int): maximum iterations for advancements calculation

        Returns:
            callable: A callable object that returns the evaluated combinations
            and accepting the following arguments:

            * **measurements** (*dict*): dictionary of measurements
            * **order** (*int*): Lagrange interpolation orders for measurement
              interpolations
            * **unit** (*str*): unit of measurements, one of ``'phase'``,
              ``'frequency'``
        """
        logger.info("Building combination '%s'", self)

        shifts, derivatives = self.build_shifts(
            delays, fs, delay_derivatives, order=order, delta=delta, maxiter=maxiter
        )

        def call(measurements, order=31, unit="frequency"):
            """Evaluate combination for a set of measurements."""
            logger.info("Evaluate combination '%s'", self)

            order = int(order)
            logger.debug("Using interpolation order '%d' for measurements", order)

            result = 0
            for measurement, polynomial in self.components.items():
                logger.debug(
                    "Computing contributions from measurement '%s'", measurement
                )
                for factor, operator in polynomial:
                    # Shift the data, and add it to the result
                    shift = shifts[tuple(operator)]
                    shifted = dsp.timeshift(
                        measurements[measurement], shift * fs, order
                    )
                    if unit == "phase":
                        result += factor * shifted
                    elif unit == "frequency":
                        if derivatives:
                            derivative = derivatives[tuple(operator)]
                        else:
                            derivative = dsp.diff(shift, 1 / fs)
                        result += factor * (1 + derivative) * shifted
                    else:
                        raise ValueError(
                            f"Unit '{unit}' not available, choose one of "
                            "'phase', 'frequency'."
                        )
            return result

        return call

    def transformed(self, mapping):
        """Return a new combination by applying a transformation.

        A transformation is defined by a mapping of indices, e.g. ``{1: 2, 2: 1}``.

        Args:
            mapping (dict): mapping of indices

        Returns:
            A new combination, result of the transformation.
        """

        def transform_string(string, mapping):
            name, i, j = naming.split_indices(string)
            if i not in mapping:
                raise ValueError(
                    f"Incomplete mapping '{mapping}', should contain index '{i}'."
                )
            if j not in mapping:
                raise ValueError(
                    f"Incomplete mapping '{mapping}', should contain index '{j}'."
                )
            i, j = mapping[i], mapping[j]
            return naming.join_indices(name, i, j)

        logger.info("Transforming combination '%s' with mapping '%s'", self, mapping)
        transformed = copy.deepcopy(self)
        transformed.components = {}
        for measurement, polynomial in self.components.items():
            transformed_meas = transform_string(measurement, mapping)
            logger.debug(
                "Transforming measurement '%s' into '%s'", measurement, transformed_meas
            )
            if transformed_meas in transformed.components:
                raise ValueError(f"Invalid mapping '{mapping}', should be a bijection.")
            transformed.components[transformed_meas] = []
            for factor, operators in polynomial:
                transformed_term = (
                    factor,
                    [transform_string(operator, mapping) for operator in operators],
                )
                logger.debug(
                    "Transforming term '%s' into '%s'", operators, transformed_term
                )
                transformed.components[transformed_meas].append(transformed_term)
        return transformed

    def simplified(self):
        """Return a simplified unique representation of the combination.

        We try to apply the following rules, for each time-shift operator
        polynomial:

            * drop polynomial if vanishing,
            * drop terms with a vanishing factor,
            * collect terms with identifical time-shift operators with a unique
              factor,
            * drop delay and advancement operator which cancel out.

        We then sort the components of the simplified combination to get a
        unique representative.

        Returns:
            A new combination, simplified version of the one passed as argument.
        """
        logger.info("Simplifying combination '%s'", self)
        simplified = copy.deepcopy(self)
        for measurement, polynomial in simplified.components.items():
            # Drop variables that are not used
            if not polynomial:
                logger.debug(
                    "Empty polynomial for measurement '%s', removing", measurement
                )
                del simplified.components[measurement]
                return simplified.simplified()
            # Drop term with vanishing factor
            for factor, operators in list(polynomial):
                if not factor:
                    logger.debug("Vanishing factor for term '%s', removing", operators)
                    simplified.components[measurement].remove((factor, operators))
                    return simplified.simplified()
            # Collect terms with identical time-shift operator
            for (factor1, operators1), (factor2, operators2) in itertools.combinations(
                polynomial, 2
            ):
                if operators1 == operators2:
                    logger.debug(
                        "Collecting factors '%s' and '%s' for term '%s'",
                        factor1,
                        factor2,
                        operators1,
                    )
                    simplified.components[measurement].remove((factor1, operators1))
                    simplified.components[measurement].remove((factor2, operators2))
                    simplified.components[measurement].append(
                        (factor1 + factor2, operators1)
                    )
                    return simplified.simplified()
            # Simplify successive delay and advancement operation
            for factor, operators in list(polynomial):
                for i, (operator1, operator2) in enumerate(
                    zip(operators, operators[1:])
                ):
                    name1, i1, j1 = naming.split_indices(operator1)
                    name2, i2, j2 = naming.split_indices(operator2)
                    if (
                        (name1, name2) in [("A", "D"), ("D", "A")]
                        and i1 == j2
                        and j1 == i2
                    ):
                        logger.debug(
                            "Cancelling operators '%s' and '%s', removing",
                            operator1,
                            operator2,
                        )
                        del operators[i + 1]
                        del operators[i]
                        return simplified.simplified()
        # We sort components to return a unique representation
        for measurement in simplified.components:
            simplified.components[measurement].sort()
        return simplified

    def __eq__(self, other):
        simplified_self = self.simplified()
        simplified_other = other.simplified()
        return simplified_self.components == simplified_other.components

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if not isinstance(other, TDICombination):
            return NotImplemented

        logger.info("Adding combinations '%s' and '%s'", self, other)
        summation = copy.deepcopy(self)
        for other_measurement, other_polynomial in other.components.items():
            polynomial = summation.components.get(other_measurement, [])
            summation.components[other_measurement] = polynomial + other_polynomial
        return summation.simplified()

    def __sub__(self, other):
        return self + (-other)

    def __rmul__(self, other):
        if isinstance(other, tuple):
            factor_other, operators_other = other
        elif isinstance(other, list):
            factor_other, operators_other = 1, other
        elif isinstance(other, (int, float)):
            factor_other, operators_other = other, []
        else:
            return NotImplemented

        logger.info(
            "Multiplying term '%s %s' and '%s'", factor_other, operators_other, self
        )
        product = copy.deepcopy(self)
        for measurement, polynomial in self.components.items():
            for factor, operators in polynomial:
                product.components[measurement].remove((factor, operators))
                product.components[measurement].append(
                    (factor_other * factor, operators_other + operators)
                )

        return product.simplified()

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return (1 / other) * self
        return NotImplemented

    def __neg__(self):
        return (-1) * self

    def __matmul__(self, other):
        logger.info("Composing combinations '%s' and '%s'", self, other)
        composition = copy.deepcopy(self)
        for measurement, polynomial in self.components.items():
            if measurement in other:
                del composition.components[measurement]
                for term in polynomial:
                    composition += term * other[measurement]
        return composition.simplified()


class LISATDICombination(TDICombination):
    """Defines a combination for a LISA-like system.

    A LISA-like system possesses the symmetry of the order-6 dihedral group (D3).
    This subclass implements the relevant transformations.

    Args:
        allow_reflections (bool): whether reflection transformations are allowed
        components (dict): dictionary of components, c.f. :class:`pytdi.TDICombination`
    """

    def __init__(self, components, allow_reflections=True):
        super().__init__(components)
        self.allow_reflections = allow_reflections

    def rotated(self, nrot=1):
        """Returns a rotated combination.

        A rotation is a circular permutation of indices.

        Args:
            nrot (int): number of 120-degree rotations

        Returns:
            A new rotated combination.
        """
        nrot = nrot % 3
        logger.info("Rotating combination '%s' by %d degrees", self, 120 * nrot)
        if nrot == 0:
            mapping = {1: 1, 2: 2, 3: 3}
        elif nrot == 1:
            mapping = {1: 2, 2: 3, 3: 1}
        elif nrot == 2:
            mapping = {1: 3, 2: 1, 3: 2}
        else:
            raise ValueError(f"nrot must be 0, 1 or 2 (got {nrot})")

        return self.transformed(mapping)

    def reflected(self, axis=1):
        """Returns a reflected combination.

        A reflection leaves the axis unchanged, and swaps the others.

        Args:
            axis (int): index around which combination is reflected

        Returns:
            A new reflected combination.
        """
        logger.info("Reflecting combination '%s' around '%d'", self, axis)
        if not self.allow_reflections:
            raise UserWarning("Reflections are not allowed for this combination.")

        if axis == 1:
            mapping = {1: 1, 2: 3, 3: 2}
        elif axis == 2:
            mapping = {1: 3, 2: 2, 3: 1}
        elif axis == 3:
            mapping = {1: 2, 2: 1, 3: 3}
        else:
            raise ValueError(f"Invalid reflection axis '{axis}'.")

        return self.transformed(mapping)


class LISAClockCorrection:
    """Defines a quantity in which clock noise enters similarily to combination.

    Clock-noise corrections are automatically built from a
    :class:`pytdi.LISATDICombination`. To compute a clock noise-free
    combination, evaluate the difference of this combination and the correction
    quantity built with this class.

    Args:
        combination (:class:`pytdi.LISATDICombination`):
            uncorrected combination
        modulation_freqs (dict):
            constant modulation frequencies [Hz]
        modulation_reduction (bool):
            removes right-sided modulation noise using REF sidebands
    """

    # pylint: disable=invalid-name

    def __init__(self, combination, modulation_freqs=None, modulation_reduction=True):

        # Check that `combination` is a LISATDICombination
        if isinstance(combination, LISATDICombination):
            #: :class:`pytdi.LISATDICombination`: Uncorrected combination.
            self.combination = combination
        else:
            raise TypeError(
                f"invalid combination type {type(combination)}, use LISATDICombination"
            )

        logger.info(
            "Initializing clock-noise correction from combination '%s'",
            self.combination,
        )

        # Use default set of modulation frequencies, matching that of LISANode
        # and Instrument
        if modulation_freqs is None:
            modulation_freqs = {
                "12": 2.4e9,
                "23": 2.4e9,
                "31": 2.4e9,
                "13": 2.401e9,
                "32": 2.401e9,
                "21": 2.401e9,
            }

        # Check that only a single measurement name (`var_name`) is found in
        # `combination`
        var_name = None
        for measurement in combination.measurements:
            new_name, _, _ = naming.split_indices(measurement)
            if var_name is None:
                var_name = new_name
            elif var_name != new_name:
                raise ValueError(
                    "single measurement name allowed, "
                    f"found '{new_name}' and '{var_name}'"
                )

        # Build `Delta_M_ij`
        if modulation_reduction:
            logger.debug("Building the differential modulation noise (ΔM) combinations")
            self.delta_M = {
                i: LISATDICombination(
                    {
                        f"ref_sb_{i}{k}": [(1 / 2, [])],
                        f"ref_{i}{k}": [(-1 / 2, [])],
                        f"ref_sb_{i}{j}": [(-1 / 2, [])],
                        f"ref_{i}{j}": [(1 / 2, [])],
                    }
                )
                for i, j, k in ["123", "231", "312"]
            }
        else:
            self.delta_M = {i: LISATDICombination({}) for i in "123"}
        delta_M_set = {f"Delta_M_{i}": self.delta_M[i] for i in self.delta_M}

        # Build `r_ij`
        logger.debug(
            "Building the modulation-corrected clock-correction variables (rc)"
        )
        self.rc = {}
        for i, j, k in ["123", "231", "312"]:
            self.rc[f"{i}{j}"] = (
                LISATDICombination(
                    {
                        f"sci_sb_{i}{j}": [(1 / modulation_freqs[f"{j}{i}"], [])],
                        f"sci_{i}{j}": [(-1 / modulation_freqs[f"{j}{i}"], [])],
                        f"Delta_M_{j}": [
                            (1 / modulation_freqs[f"{j}{i}"], [f"D_{i}{j}"])
                        ],
                    }
                )
                @ delta_M_set
            )
            self.rc[f"{i}{k}"] = (
                LISATDICombination(
                    {
                        f"sci_sb_{i}{k}": [(1 / modulation_freqs[f"{k}{i}"], [])],
                        f"sci_{i}{k}": [(-1 / modulation_freqs[f"{k}{i}"], [])],
                        f"Delta_M_{i}": [(-1 / modulation_freqs[f"{k}{i}"], [])],
                    }
                )
                @ delta_M_set
            )
        rc_set = {f"rc_{mosa}": rc for mosa, rc in self.rc.items()}

        # Build `P_ij`
        # Note that `P_component` here is denoted `P_ij` in the article, while
        # `P` in this code corresponds to `P_ij rc_ij` in the article
        logger.debug("Building the delay polynomials (P)")
        self.P = {}
        self.P_component = {}
        for i, j in naming.lisa_indices():
            self.P_component[f"{i}{j}"] = self.combination.components.get(
                f"{var_name}_{i}{j}", []
            )
            self.P[f"{i}{j}"] = (
                LISATDICombination({f"rc_{i}{j}": self.P_component[f"{i}{j}"]}) @ rc_set
            )

        # Build `R_ij`
        logger.debug("Building the reconstructed photon path (R)")
        self.R_rc = {}
        self.R = {}
        for i, j in naming.lisa_indices():
            self.R_rc[f"{i}{j}"] = LISATDICombination({})
            for coeff, delays in self.P_component[f"{i}{j}"]:
                self.R_rc[f"{i}{j}"] -= coeff * LISATDICombination.from_string(
                    self.to_string(delays), half_way_shift=False, var_name="rc"
                )
            self.R[f"{i}{j}"] = self.R_rc[f"{i}{j}"] @ rc_set

    @staticmethod
    def to_string(delays):
        """Returns a string from a list of delay operators.

        Args:
            delays (list): delay operators
        """
        components = []
        for delay in delays:
            operator, i, j = naming.split_indices(delay)
            if operator == "D":
                components.append(f"-{i}{j}")
            elif operator == "A":
                components.append(f"{i}{j}")
            else:
                raise ValueError(
                    f"unsupported time-shift operator '{operator}', use 'A' or 'D'"
                )
        return " ".join(components)

    def build(self, *args, **kwargs):
        """Prepare the clock-noise correction from delays.

        This function prepares the actual correction by pre-computing nested
        delays and Doppler factors. It returns a callable object that evaluates
        the correction for a given set of measurements.

        .. code-block:: python

            built = mycorrection.build(
                {'d_12': t12_array, 'd_21': t21_array}, fs,
            )
            correction_data = built(
                {'y_12': y12_array,'y_21': y21_array},
            )

        If any advancement operators are used in the combination, they are
        computed iteratively.

        Args:
            delays (dict): dictionary of delays [s]
            fs (double): sampling frequency [Hz]
            delay_derivatives: dictionary of delay time derivatives [s/s]
            order (int): Lagrange interpolation orders for delay interpolations
            delta (float): allowed timing accuracy for advancements calculation
            maxiter (int): maximum iterations for advancements calculation

        Returns:
            callable: A callable object that returns the evaluated correction
            and accepting the following arguments:

            * **measurements** (*dict*): measurements, including sidebands [Hz]
            * **beatnote_freqs** (*dict*): beatnote frequencies [Hz]
            * **order** (*int*): Lagrange interpolation orders for measurement
              interpolations
            * **individual_rij** (*bool*): compute ``R_ij`` for each term
              individually
        """
        logger.info("Building clock-noise correction from combination")

        # Build the `P_ij`
        prepared_P = {mosa: P.build(*args, **kwargs) for mosa, P in self.P.items()}

        # Build the `R_ij`
        prepared_R = {mosa: R.build(*args, **kwargs) for mosa, R in self.R.items()}

        def call(measurements, beatnote_freqs, order=31, individual_rij=True):
            """Evaluate clock-noise correction for a set of measurements."""
            result = 0
            if individual_rij:
                # prepare rescaled measurements
                rescaled_measurements = {}
                for i, j, k in ["123", "231", "312"]:
                    rescaled_measurements[f"ref_{i}{j}"] = {
                        key: beatnote_freqs[f"ref_{i}{j}"] * value
                        for key, value in measurements.items()
                    }
                    rescaled_measurements[f"sci_{i}{j}"] = {
                        key: beatnote_freqs[f"sci_{i}{j}"] * value
                        for key, value in measurements.items()
                    }
                    rescaled_measurements[f"sci_{i}{k}"] = {
                        key: beatnote_freqs[f"sci_{i}{k}"] * value
                        for key, value in measurements.items()
                    }
                # compute correction
                for i, j, k in ["123", "231", "312"]:
                    result += (
                        prepared_R[f"{i}{j}"](
                            rescaled_measurements[f"ref_{j}{k}"], order=order
                        )
                        - prepared_R[f"{i}{j}"](
                            rescaled_measurements[f"sci_{i}{j}"], order=order
                        )
                        - prepared_R[f"{i}{k}"](
                            rescaled_measurements[f"ref_{i}{j}"], order=order
                        )
                        - prepared_R[f"{i}{k}"](
                            rescaled_measurements[f"sci_{i}{k}"], order=order
                        )
                        + prepared_P[f"{i}{j}"](
                            rescaled_measurements[f"ref_{j}{k}"], order=order
                        )
                    )
            else:
                # compute correction
                for i, j, k in ["123", "231", "312"]:
                    result += (
                        (beatnote_freqs[f"ref_{j}{k}"] - beatnote_freqs[f"sci_{i}{j}"])
                        * prepared_R[f"{i}{j}"](measurements, order=order)
                        - (
                            beatnote_freqs[f"ref_{i}{j}"]
                            + beatnote_freqs[f"sci_{i}{k}"]
                        )
                        * prepared_R[f"{i}{k}"](measurements, order=order)
                        + beatnote_freqs[f"ref_{j}{k}"]
                        * prepared_P[f"{i}{j}"](measurements, order=order)
                    )
            return result

        return call

    def is_valid(self):
        r"""Test whether clock-noise correction is valid.

        We check symbolically that

        .. math::

            P_{ij} q_i = R_{ij} \qs

        Returns:
            bool: Whether the clock-noise correction is valid.
        """
        test_rc = {
            f"{i}{j}": LISATDICombination(
                {f"q_{i}": [(-1, [])], f"q_{j}": [(1, [f"D_{i}{j}"])]}
            )
            for i, j in naming.lisa_indices()
        }
        test_rc_set = {f"rc_{mosa}": test_rc[mosa] for mosa in test_rc}

        # Check that P_ij q_i = R_ij for all i, j
        for i, j in naming.lisa_indices():
            P_q = LISATDICombination(
                {f"q_{i}": self.P_component[f"{i}{j}"]}
            ).simplified()
            if self.R_rc[f"{i}{j}"] @ test_rc_set != P_q:
                return False

        return True

    def __repr__(self):
        return f"<{self.__class__.__name__} based on {self.combination}>"
