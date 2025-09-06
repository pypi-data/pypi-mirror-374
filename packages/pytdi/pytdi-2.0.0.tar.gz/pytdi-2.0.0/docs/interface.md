# Data interface

The {class}`pytdi.Data` class collects measurements and delays in one object to conveniently build and call {class}`pytdi.TDICombination` objects. Furthermore, it provides a convenient interface to load data from one of the supported LISA simulators [LISANode](https://gitlab.in2p3.fr/j2b.bayle/LISANode), [LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument), [LISA Orbits](https://gitlab.in2p3.fr/lisa-simulation/orbits) and [LISA GW Response](https://gitlab.in2p3.fr/lisa-simulation/gw-response).

For labeling the measurements and delays, we follow the standard {doc}`lisa-conventions`. Valid measurement keys are listed in {attr}`pytdi.Data.MEASUREMENTS`.

## Usage

The following examples show how to construct a {class}`pytdi.Data` object from a [LISANode](https://gitlab.in2p3.fr/j2b.bayle/LISANode) output file and evaluate one of the [standard combinations](standard-combinations).

```python
import pytdi.michelson
import pytdi.Data

data = Data.from_lisanode('lisa.h5')

X2 = pytdi.michelson.X2.build(**data.args)
X2_data = X2(data.measurements)
```

Loading data and evaluating it for other LISA simulators works analogously by replacing `Data.from_lisanode('lisa.h5')` with the appropriate constructor listed below. [LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument) presents a special case since data cannot only be read from file but also directly loaded from a `lisainstrument.Instrument` object, e.g.

```python
import lisainstrument
import pytdi.michelson
import pytdi.Data

instrument = lisainstrument.Instrument()
instrument.simulate()

data = Data.from_instrument(instrument)

X2 = pytdi.michelson.X2.build(**data.args)
X2_data = X2(data.measurements)
```

```{admonition} Frequency fluctuations, frequency offsets or total frequency
LISA Instrument outputs beatnote measurements in terms of total frequency, or the decomposed frequency offsets and fluctuations. By default, beatnote frequency fluctuations are loaded. Use the argument `signals` to change it to frequency offsets or total frequency.

```python
data = Data.from_instrument(instru, signals='offsets')
data = Data.from_instrument(instru, signals='total')
```

```{admonition} Skip samples in the beginning
Usually, LISA Simulators require a certain time in the beginning of a simulation to initialize noise production and filters. This leads to errornous samples which should be truncated before evaluating them with TDI. Use the argument `skipped` to determine the number of samples to be skipped in the beginning of the simulation.

```python
data = Data.from_instrument(instru, skipped=1000)
```

## Data

```{eval-rst}
.. autoclass:: pytdi.Data
    :members:
    :inherited-members:
```
