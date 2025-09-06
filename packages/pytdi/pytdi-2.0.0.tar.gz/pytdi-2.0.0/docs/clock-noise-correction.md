# Clock noise correction

For any combination that can be described as a valid interference of photon paths (see {ref}`tdi-combination:virtual photon paths`), it is possible to construct another combination, in which clock noise enters identically[^1]. This clock-noise correcting combination is specific to the original combination, and is built from the inter-spacecraft (SCI) carrier and sideband beatnotes.

[^1]: Olaf Hartwig, Jean-Baptiste Bayle, *Clock-jitter reduction in LISA time-delay interferometry combinations*, (2020), [arXiv:2005.02430](https://arxiv.org/abs/2005.02430).

Evaluating these combinations, and subtracting the result of clock-noise correcting combination from the original combination yields a clock noise-free quantities.

```{warning}
The current implementation of the clock noise correction algorithm only allows to operate on frequency units. Using phase units as an input will yield wrong results.
```

## Usage

To generate a clock-noise correcting combination, simply initialize a {class}`pytdi.LISAClockCorrection` object with a {class}`pytdi.LISATDICombination` instance defined in terms of $\eta$ variables.

```python
from pytdi.michelson import X2, X2_ETA
KX2 = LISAClockCorrection(X2_ETA)

data_x = X2.build(delays, fs)(fluctuations)
data_k = KX2.build(delays, fs)(fluctuations, offsets)

data_xc = data_x - data_k
```

You can pass a custom dictionary of modulation frequencies. By default, REF sidebands are used to reduce the higher modulation noise in the right-sided MOSAs; you can disable this feature by setting the option `modulation_reduction=False`.

```python
correction = LISAClockCorrection(my_combination, modulation_reduction=False)
```

## LISAClockCorrection

```{eval-rst}
.. autoclass:: pytdi.LISAClockCorrection
    :members:
    :inherited-members:
```
