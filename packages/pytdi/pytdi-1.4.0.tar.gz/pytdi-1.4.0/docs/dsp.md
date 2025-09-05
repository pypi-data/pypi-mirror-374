# Digital signal processing

This module defines utility functions used in TDI to process data, in particular time shift operations (time delays and advancements).

## Time shift

A general time shift is defined as shifting a functions time argument by an amount $s(t)$.

```{math}
\mathbf{S}x(t) = x(t + s(t)) \qs
```

In TDI we have to process random and discrete time series. Thus, we require an interpolation method that reconstructs the signal at times that are not covered by the samples. For high numerical efficiency this is achieved by a finite length fractional delay filter. Further discussion on the general topic can be found in [^1].

[^1]: Shaddock et al, *Postprocessed time-delay interferometry for LISA*, PhysRevD.70.081101, 2004. [arXiv:gr-qc/0406106](https://arxiv.org/abs/gr-qc/0406106)

### Lagrange interpolation

Lagrange interpolation is a special case of a fractional delay filter implementation. It interpolates the data by connecting $N+1$ centered neighboring points via a Lagrange polynomial of degree $N$. The formula for an odd interpolation order can be found in [^2].

[^2]: H. Halloin, *Note on decimation and interpolation filters for LISA simulation*, internal technical note, 2017.

```{eval-rst}
.. autofunction:: pytdi.dsp.lagrange_taps
```

### Implementation

The time shift operation via Lagrange interpolation is implemented in {meth}`pytdi.dsp.timeshift`. The two arguments `data` and `shifts` can either be a single number or arrays of same length. If `data` is a single number the time series is treated as constant and no operation is performed. If `shifts` is a single number the time shift is assumed to be constant. This speeds up the computations since the coefficients of the filter are identical for each time step (FIR filter applied via convolution). Finally, if both `data` and `shifts` are arrays (of same length) the operation is implemented as matrix multiplication of the filter coefficient matrix and the data vector. This requires substantially more resources as for the constant shift case as $(N+1) \times M$ coefficients have to be stored, where $M$ is the length of the time series and $N$ the order of the Lagrange polynomial.

```{eval-rst}
.. autofunction:: pytdi.dsp.timeshift
```

### Time advancement

Time delay and advancement are intimately connected since one represents the inverse operation of the other ($\adv\delay x(t) = x(t)$). Thus, they are related by the following expression

```{math}
\adv\delay x(t) = x(t+a(t)-d(t+a(t))) = x(t) \iff a(t) = d(t + a(t)) \qs
```

The function {meth}`pytdi.dsp.calculate_advancements` solves this implicit equation iteratively. The convergence condition is formulated via the maximum allowed root mean-square error between two successive iterations.

```{eval-rst}
.. autofunction:: pytdi.dsp.calculate_advancements
```
