# Standard combinations

PyTDI provides a list of commonly-used standard combinations.

Most combinations are first defined as functions of $\eta_{ij}$ (c.f. {ref}`standard-combinations:intermediary variables`), and then composed with the latter to provide combinations defined directly in terms of beatnotes. We follow the indexing conventions presented in {doc}`lisa-conventions`.

## Intermediary variables

Intermediary variables take advantage of the split interferometry optical design to suppress spacecraft jitter and reduce the problem from 6 to 3 lasers[^1][^2].

[^1]: Otto, M. (2015). *Time-Delay Interferometry Simulations for the Laser Interferometer Space Antenna*.

[^2]: Hartwig, O. (2021). *Instrumental modeling and noise reduction algorithms for the Laser Interferometer Space Antenna*.

### Spacecraft jitter reduction ($\xi_{ij}$)

The $\xi_{ij}$ combinations[^1] reduce spacecraft jitter by combining the inter-spacecraft beatnote with the difference of reference and test-mass beatnotes to construct a virtual test-mass to test-mass measurement.

```{math}
\xi_{12} = \text{sci}_{12} + \frac{\text{ref}_{12} - \text{tmi}_{12}}{2}
+ \frac{\delay_{12}(\text{ref}_{21} - \text{tmi}_{21})}{2} \qs
```

The expressions for all other 6 optical benches can be deduced by applying the rotation and reflection of the indices.

```{eval-rst}
.. autodata:: pytdi.intervar.XI_12
.. autodata:: pytdi.intervar.XI_23
.. autodata:: pytdi.intervar.XI_31
.. autodata:: pytdi.intervar.XI_13
.. autodata:: pytdi.intervar.XI_21
.. autodata:: pytdi.intervar.XI_32

.. autodata:: pytdi.intervar.XI_SET
```

### Reduction to 3 lasers ($\eta_{ij}$)

The $\eta_{ij}$ combinations[^1] remove the noise of half the lasers in the constellation.

```{math}
\eta_{12} &= \xi_{12} + \frac{\delay_{12}(\text{ref}_{21} - \text{ref}_{23})}{2} \qc

\eta_{13} &= \xi_{13} + \frac{\text{ref}_{12} - \text{ref}_{13}}{2} \qs
```

The expressions for the other spacecraft can be deduced from cyclic index permutation.

#### The $\eta_{ij}$ as functions of $\xi_{ij}$

```{eval-rst}
.. autodata:: pytdi.intervar.ETA_12_XI
.. autodata:: pytdi.intervar.ETA_23_XI
.. autodata:: pytdi.intervar.ETA_31_XI
.. autodata:: pytdi.intervar.ETA_13_XI
.. autodata:: pytdi.intervar.ETA_21_XI
.. autodata:: pytdi.intervar.ETA_32_XI

.. autodata:: pytdi.intervar.ETA_XI_SET
```

#### The $\eta_{ij}$ as functions of beatnotes

```{eval-rst}
.. autodata:: pytdi.intervar.ETA_SET
.. autofunction:: pytdi.intervar.compute_etas
```

## Michelson combinations

Michelson combinations synthesize a virtual Michelson interferometer to reduce laser noise in a 3-laser configuration. Note that the sign of the combinations are arbitrary; we follow here the [LISA Data Challenge](https://lisa-ldc.lal.in2p3.fr/static/data/pdf/LDC-manual-002.pdf) conventions.

### First generation ($X_1$, $Y_1$, $Z_1$)

The first generation Michelson combination $X_1$ is given by

```{math}
X_1 &= (1 - \delay_{121})(\eta_{13} + \delay_{13} \eta_{31})

&\qquad - (1 - \delay_{131}) (\eta_{12} + \delay_{12} \eta_{21}) \qc
```

with $Y_1$ and $Z_1$ given by circular permutation of the indices.

#### $X_1$, $Y_1$, $Z_1$ as functions of $\eta_{ij}$

```{eval-rst}
.. autodata:: pytdi.michelson.X1_ETA
.. autodata:: pytdi.michelson.Y1_ETA
.. autodata:: pytdi.michelson.Z1_ETA
```

#### $X_1$, $Y_1$, $Z_1$ as functions of beatnotes

```{eval-rst}
.. autodata:: pytdi.michelson.X1
.. autodata:: pytdi.michelson.Y1
.. autodata:: pytdi.michelson.Z1
```

### Second generation ($X_2$, $Y_2$, $Z_2$)

The second generation Michelson combination $X_2$ is given by

```{math}
X_2 &= (1 - \delay_{121} - \delay_{12131} + \delay_{1312121})(\eta_{13} + \delay_{13} \eta_{31})

&\qquad - (1 - \delay_{131} - \delay_{13121} + \delay_{1213131}) (\eta_{12} + \delay_{12} \eta_{21})
```

with $Y_2$ and $Z_2$ given by circular permutation of the indices.

#### $X_2$, $Y_2$, $Z_2$ as functions of $\eta_{ij}$

```{eval-rst}
.. autodata:: pytdi.michelson.X2_ETA
.. autodata:: pytdi.michelson.Y2_ETA
.. autodata:: pytdi.michelson.Z2_ETA
```

#### $X_2$, $Y_2, $Z_2$ as functions of beatnotes

```{eval-rst}
.. autodata:: pytdi.michelson.X2
.. autodata:: pytdi.michelson.Y2
.. autodata:: pytdi.michelson.Z2
```

### Factorized Michelson combinations

Michelson combinations can be factorized and computed in multiple steps (using intermediary combinations). This reduces computation time (less delays to compute) and in some instances also improves numerical precision if intermediary results are already small. We provide functions to compute the factorized Michelson combinations of first and second generations.

```{eval-rst}
.. autofunction:: pytdi.michelson.compute_factorized_michelson
```

## Orthogonal combinations

The orthogonal combinations are linear combination of the {ref}`standard-combinations:michelson combinations`, in which noises are uncorrelated (under simplifying assumptions). We take the definitions given in the [LDC manual](https://lisa-ldc.lal.in2p3.fr).

```{math}
E_i &= \frac{X_i - 2Y_i + Z_i}{\sqrt{6}} \qc

A_i &= \frac{Z_i - X_i}{\sqrt{2}} \qc

T_i &= \frac{X_i + Y_i + Z_i}{\sqrt{3}} \qc
```

where $i$ is 1 or 2 for the first and second generations, respectively.

### First generation  ($A_1$, $E_1$, $T_1$)

```{eval-rst}
.. autodata:: pytdi.ortho.A1
.. autodata:: pytdi.ortho.E1
.. autodata:: pytdi.ortho.T1
```

### Second generation  ($A_2$, $E_2$, $T_2$)

```{eval-rst}
.. autodata:: pytdi.ortho.A2
.. autodata:: pytdi.ortho.E2
.. autodata:: pytdi.ortho.T2
```

### Factorized orthogonal combinations

Computing the three orthogonal combinations by evaluating the pre-defined objects one after the other is highly inefficient, as the underlying Michelson or Sagnac combinations are computed multiple times. We provide functions to compute the three orthogonal combinations (from Michelson or Sagnac combinations of first and second generations) in a single step, using factorized expressions.

This reduces computation time very significantly (less delays to compute) and in some instances also improves numerical precision if intermediary results are already small.

```{eval-rst}
.. autofunction:: pytdi.ortho.compute_factorized_ortho
```

## Sagnac combinations

First and second-generation Sagnac combinations $\alpha_i$, $\beta_i$, $\gamma_i$ (with $i=1,2$) synthesize the interference of photons circulating clockwise and counterclockwise the constellation.

The fully symmetric first-generation Sagnac combination $\zeta_1$ combines all measurements with exactly one delay. Its second-generation counterpart is no longer fully symmetric and exists in three kinds $\zeta_{21}$, $\zeta_{22}$, $\zeta_{23}$.

Note that $\alpha_1$, $\beta_1$, $\gamma_1$, $\zeta_1$ are the generators of the first-generation TDI combination space[^4]. Therefore, all first-generation combination can be written as a linear combination of the latter.

[^4]: Tinto, M., Estabrook, F. B., Armstrong, J. W. (2002). *Time-delay interferometry for LISA*. Physical Review D - Particles, Fields, Gravitation and Cosmology. [arXiv:gr-qc/0409034](https://arxiv.org/abs/gr-qc/0409034).

### First generation ($\alpha_1$, $\beta_1$, $\gamma_1$, $\zeta_1$)

The first Sagnac combination is given by

```{math}
\alpha_1 = \eta_{12} + \delay_{12} \eta_{23} + \delay_{123} \eta_{31} - \eta_{13} - \delay_{13} \eta_{32} - \delay_{132} \eta_{21}
\qc
```

with $\beta_1$ and $\gamma_1$ given by circular permutation of the indices.

The fully-symmetric Sagnac combination reads

```{math}
\zeta_1 = \delay_{23} \eta_{12} + \delay_{31} \eta_{23} + \delay_{12} \eta_{31} - \delay_{23} \eta_{13} - \delay_{12} \eta_{32} - \delay_{31} \eta_{21}
\qs
```

Because it is fully symmetric, usual LISA transformations (circular permutation of indices and reflections) only yield the same combination or with an opposite sign. Therefore, we only define one first-generation $\zeta_1$.

Note that $\alpha_1$, $\beta_1$, $\gamma_1$, $\zeta_1$ are the generators of the first-generation TDI combination space[^4].

#### $\alpha_1$, $\beta_1$, $\gamma_1$, $\zeta_1$ as functions of $\eta_{ij}$

```{eval-rst}
.. autodata:: pytdi.sagnac.ALPHA1_ETA
.. autodata:: pytdi.sagnac.BETA1_ETA
.. autodata:: pytdi.sagnac.GAMMA1_ETA
.. autodata:: pytdi.sagnac.ZETA1_ETA
```

#### $\alpha_1$, $\beta_1$, $\gamma_1$, $\zeta_1$ as functions of beatnotes

```{eval-rst}
.. autodata:: pytdi.sagnac.ALPHA1
.. autodata:: pytdi.sagnac.BETA1
.. autodata:: pytdi.sagnac.GAMMA1
.. autodata:: pytdi.sagnac.ZETA1
```

### Second generation ($\alpha_2$, $\beta_2$, $\gamma_2$, $\zeta_{2i}$)

The first Sagnac combination is given by

```{math}
\alpha_2 &= \eta_{12} + \delay_{12} \eta_{23} + \delay_{123} \eta_{31} + \delay_{1231} \eta_{13} + \delay_{12313} \eta_{32} + \delay_{123132} \eta_{21}

&\qquad - \eta_{13} - \delay_{13} \eta_{32} - \delay_{132} \eta_{21} - \delay_{1321} \eta_{12} - \delay_{13212} \eta_{23} - \delay_{132123} \eta_{31}
\qc
```

with $\beta_2$ and $\gamma_2$ given by circular permutation of the indices.

The fully-symmetric Sagnac combination of the first kind reads

```{math}
\zeta_{21} &= (\delay_{232} - \delay_{13} \delay_{21} \delay_{32}) \eta_{12}
+ (\delay_{32} \delay_{13} - \delay_{12} \delay_{313}) \eta_{23}

&\qquad + (\delay_{23} \delay_{12} - \delay_{13} \delay_{212}) \eta_{31}
- (\delay_{313} - \delay_{12} \delay_{31} \delay_{23}) \eta_{13}

&\qquad - (\delay_{32} \delay_{13} - \delay_{12} \delay_{313}) \eta_{21}
- (\delay_{23} \delay_{12} - \delay_{13} \delay_{212}) \eta_{32}
\qc
```

and $\zeta_{22}$ and $\zeta_{23}$ are obtained by circular permutation of the indices.

#### $\alpha_2, \beta_2, \gamma_2, \zeta_{2i}$ as functions of $\eta_{ij}$

```{eval-rst}
.. autodata:: pytdi.sagnac.ALPHA2_ETA
.. autodata:: pytdi.sagnac.BETA2_ETA
.. autodata:: pytdi.sagnac.GAMMA2_ETA

.. autodata:: pytdi.sagnac.ZETA21_ETA
.. autodata:: pytdi.sagnac.ZETA22_ETA
.. autodata:: pytdi.sagnac.ZETA23_ETA
```

#### $\alpha_2, \beta_2, \gamma_2, \zeta_{2i}$ as functions of beatnotes

```{eval-rst}
.. autodata:: pytdi.sagnac.ALPHA2
.. autodata:: pytdi.sagnac.BETA2
.. autodata:: pytdi.sagnac.GAMMA2

.. autodata:: pytdi.sagnac.ZETA21
.. autodata:: pytdi.sagnac.ZETA22
.. autodata:: pytdi.sagnac.ZETA23
```

### Factorized Sagnac combinations

Sagnac combinations can be factorized and computed in multiple steps (using intermediary combinations). This reduces computation time (less delays to compute) and in some instances also improves numerical precision if intermediary results are already small. We provide functions to compute the factorized Sagnac combinations of first and second generations.

```{eval-rst}
.. autofunction:: pytdi.sagnac.compute_factorized_sagnac
```
