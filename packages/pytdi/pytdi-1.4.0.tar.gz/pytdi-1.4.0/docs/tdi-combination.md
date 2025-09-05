# TDI combination

## Definition

In all generalities, a combination $Y(t)$ is defined as a sum of time-shift polynomials $P_k$ applied on measurements $x_k(t)$. Each time-shift polynomial $P_k$ is itself a linear combination of chained time-shift operators, i.e., the sum of terms that include a constant scalar factor and the mathematical composition of time-shift operators.

Time-shift operators come in two flavours:

* delay operators $\delay_{ij}$ associated with delay $d_{ij}(t)$, defined as $\delay_{ij} x(t) = x(t - d_{ij}(t))$, and
* advancement operators $\adv_{ij}$ associated with advancement $a_{ij}$, defined as $\adv_{ij} x(t) = x(t + a_{ij}(t))$ such that $\adv_{ij} \delay_{ji} = \delay_{ij} \adv_{ji} = 1$.

Use the {meth}`pytdi.TDICombination.build` method to evaluate the combination for a given set of measurements and delays.

Advancements are computed by solving iteratively the equation $\adv_{ij} \delay_{ji} x(t) = x(t)$, i.e., $a_{ij}(t) = d_{ji}(t + a_{ij}(t))$. More details are given in the [associated documentation](dsp).

TDI combinations support summation, subtraction, multiplication, and composition (`@` operator).

As a subclass, {class}`pytdi.LISATDICombination` adds the symmetry transformations to mirror the LISA constellation along a given axis or rotate it by 60 degrees. The user is advised to make use of that class if the combination is related to LISA-like systems that exhibit the symmetry of the order-6 dihedral group (D3).

## Virtual photon paths

Following the **geometrical interpretation** proposed by M. Vallisneri[^1], you can create a combination from the virtual interference of multiple beams. Use the constructor {meth}`pytdi.TDICombination.from_string` to define a TDI combination as an interference of multiple virtual beams.

[^1]: M. Vallisneri, *Geometric Time Delay Interferometry*, Phys.Rev.D72:042003, 2005. [arXiv:gr-qc/0504145](https://arxiv.org/abs/gr-qc/0504145).

The setup is defined by a list of sequences of numbers. Each sequence represents the paths of virtual photons propagating along the constellation, with each index representing one visited spacecraft.

* Positive sequences represent a path that follows a photon from the event of emission from the spacecraft indicated by the leftmost index to the event of reception indicated by the rightmost index. This is a path forward in time, computed using advancements.

* This order is reversed for negative substrings, which represent a path that follows a photon from the event of reception at the spacecraft indicated by the leftmost index to the event of emission indicated by the rightmost index. This is a path backwards in time, computed using delays.

Laser noise is cancelled if the overall path from the first index to the last index starts and ends at the same spacecraft, and the overall light travel time along this path is sufficiently small.

The full algorithm to construct a combination is as follows:

1. Extend sequence into lists of single links $ij$, for example, $(12131, -12131)$
   yields $(12, 21, 13, 31, -12, -21, -13, -31)$.

2. Initialize an empty combination $C(t)$ and a zero total time shift $\mathrm{T}$.

3. Iterate through all single links with indices $ij$. If the link is an
   advancement, add $\mathrm{T} \adv_{ij} \eta_{ji}$ to $C(t)$ and append the advancement to the total time shift $\mathrm{T} = \mathrm{T} \adv_{ij}$. If the link is a delay, subtract $\mathrm{T} \eta_{ij}$ from $C(t)$ and append the delay to the total time shift $\mathrm{T} = \mathrm{T} \delay_{ij}$.

To reduce the number of total time shifts, the whole combination can be shifted by the inverse of the first half of operators in $\mathrm{T}$. This yields expressions which are close to the 'standard' combinations in the literature.

## Units

The actual numerical evaluation of a TDI combination depends on the unit of input measurements. In case of phase units, the time-shift operator only shifts the time argument of the function it is applied to, e.g. $\mathbf{D} \Phi(t) = \Phi(t-d(t))$. This also holds for any other unit that can be related to phase by a simple factor, e.g. displacement.

However, a combination can also be applied to frequency data, which is given as the time derivative of the phase, i.e. $\nu(t) = \dot\Phi(t)$. The equivalent time-shift operation can be derived by looking at $\frac{\mathrm{d}}{\mathrm{d}t}\mathbf{D}\Phi(t)=(1 - \dot d(t))\mathbf{D}\nu(t)$. We note that the frequency $\nu(t)$ is not only shifted in time but also scaled by a Doppler factor. As {class}`pytdi.TDICombination` objects are unit-agnostic, one must provide a unit parameter when evaluating a combination and choose either `unit='phase'` or `unit='frequency'` (default behavior).

## TDICombination

```{eval-rst}
.. autoclass:: pytdi.TDICombination
    :members:
    :inherited-members:
```

## LISATDICombination

```{eval-rst}
.. autoclass:: pytdi.LISATDICombination
    :members:
    :inherited-members:
```
