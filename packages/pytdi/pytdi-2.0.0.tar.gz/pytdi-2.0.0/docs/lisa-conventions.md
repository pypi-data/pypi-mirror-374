# LISA conventions

## Indexing

```{sidebar}
```{image} _static/img/indexing.png
:width: 400px
```

We follow the standard LISA conventions given in the [LDC Manual](https://lisa-ldc.lal.in2p3.fr). Spacecraft are indexed from 1 to 3 clockwise when looking down on the $z$-axis. MOSAs are indexed with two numbers $ij$, where $i$ is the index of the spacecraft the system is mounted on (local spacecraft), and $j$ is the index of the spacecraft the light is received from (distant spacecraft).

Measurements are indexed according to the MOSA they are performed on.

Delays and delay derivatives are indexed according to the MOSA they are measured on, i.e., the receiving spacecraft. Similarly, the link unit vectors are lablled according to the MOSA they point at.

```{admonition} Double-index conventions
**Double-indexed quantities are indexed $ij$, where $i$ is the receiver spacecraft and $j$ is the emitter spacecraft**. As an example, the delay $d_{ij}$ is the time of flight of a photon emitted by spacecraft $j$ and received at spacecraft $i$.
```

## Measurements

The main scientific output of LISA are beatnote phases or frequencies of multiple heterodyne interferometers. Each MOSA hosts three of them: the inter-spacecraft interferometer (SCI), the reference interferometer (REF) and the test-mass interferometer (TMI). The SCI and REF both not only track the carrier-carrier beatnotes but also the sideband-sideband beatnotes.

```{admonition} Labeling in PyTDI
In PyTDI interferometric measurements are labeled by the name (lowercase) and a pair of indices, e.g. `'sci_12'`. The sideband-sideband beatnotes are distinguished by an additional `sb` in their dictionary keys, e.g.`'sci_sb_12'`. For delay and delay derivatives we use the same labels, e.g. `'d_12'`.
```
