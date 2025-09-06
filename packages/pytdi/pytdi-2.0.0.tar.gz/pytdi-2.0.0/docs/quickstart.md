# Quickstart

## Installation

The latest stable version of PyTDI can be easily installed using [pip](https://pip.pypa.io/en/stable/).

```shell
pip install pytdi
```

```{admonition} Versions < 1.2
You can also install earlier versions from before PyTDI was published. Since they are hosted in a private project on [gitlab.in2p3](https://gitlab.in2p3.fr), you will need to authenticate with your username and password. A list of available versions can be found on the project page. Run the following command providing the corresponding version tag:

    pip install git+https://gitlab.in2p3.fr/LISA/LDPG/wg6_inrep/pytdi.git@v1.0.1

Large data files used to run integration tests are currently commited to the project repository. **To reduce the download time, we recommend that you setup [Git LFS](https://git-lfs.github.com) to skip them before you install or clone the project.** Note that if Git LFS is not installed on your system, this step is not necessary.

    git lfs install --skip-smudge
```

## Using standard combinations

While PyTDI allows to define your own combinations and operate on them, most users will only want to interact with standard combinations. PyTDI offers a list of commonly used pre-defined combinations.

Import the required submodules (e.g., Michelson combinations are defined in {mod}`pytdi.michelson`, refer to [](standard-combinations) for other combinations), and prepare the combinations using {meth}`pytdi.TDICombination.build`. You need to pass a dictionary of delays and a sampling frequency.

```python
import pytdi.michelson

fs = 4 # Hz
delays = {'d_12': np.array(...), 'd_23': np.array(...), ...}
X2 = pytdi.michelson.X2.build(delays, fs)
```

The evaluation of a prepared combination depends on the unit of the data. Most literature discussing TDI gives the definitions of TDI combinations in units of phase since they only involve time-shifting operations and linear combination of measurements. However, realistic simulations produce frequency data that include Doppler shifts due to time-varying delays. [LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument) and [LISANode](https://gitlab.in2p3.fr/j2b.bayle/LISANode) include such effect by default.

The evaluations of combinations can be easily adapted to account for this Doppler effect[^1], using the delay time derivatives. To support the computation of the time derivative of nested delays the user can provide the time derivative of the simple delays via the optional `delay_derivatives` argument.

[^1]: Bayle, J.-B., Hartwig, O., Staab, M. (2021). *Adapting time-delay interferometry for LISA data in frequency*. Physical Review D, 104(2), 023006. [arXiv:2103.06976](http://arxiv.org/abs/2103.06976).

```python
import pytdi.michelson

fs = 4 # Hz
delays = {'d_12': np.array(...), 'd_23': np.array(...), ...}
delay_derivatives = {'d_12': np.array(...), 'd_23': np.array(...), ...}
X2_built = pytdi.michelson.X2.build(delays, fs, delay_derivatives=delay_derivatives)
```

The delay dictionary's (and delay derivative dictionary's) keys are `d_ij`, where *ij* are the indices of the delay, as defined by the standard [LISA conventions](lisa-conventions) (emitter *j* and receiver *i*).

```{admonition} Required delays
The delay and delay derivative dictionaries **must** contains all required keys.

To list the required delays to build a combination, use the {attr}`pytdi.TDICombination.delays` attribute. Alternatively, the required delays for each standard combinations are listed in the [associated documentation](standard-combinations).
```

You can evaluate a built combination by calling it with a dictionary of measurements (dictionary of required beatnote time series). You get as a result a Numpy array containing your TDI channel data.

```python
measurements = {'sci_12': np.array(...), 'sci_23': np.array(...), ...}
X2_data = X2_built(measurements)
```

When calling a built combination, one can specify the unit of the measurement via the unit parametr. It must be either `unit='phase'` or `unit='frequency'` (default behavior).

The measurement dictionary's keys refer to the interferometer acronyms, as defined in the standard [LISA conventions](lisa-conventions). E.g., inter-spacecraft, reference, and test-mass beatnotes on MOSA *ij* are labelled `sci_ij`, `ref_ij`, and `tmi_ij`, respectively.

```{admonition} Required measurements
The measurement dictionary **must** contains all required keys.

To list the required measurements to compute a combination, use the {attr}`pytdi.TDICombination.measurements` attribute. Alternatively, the required measurements for each standard combinations are listed in the [associated documentation](standard-combinations).

The {attr}`pytdi.TDICombination.measurements` attribute also provides a convenient way to start off with a dictionary of vanishing measurements, and then injecting signals in the desired interferometers.

```python
measurements = {key: 0 for key in X2.measurements}
measurements['sci_23'] = np.array(...)
```

## Loading data

PyTDI offers an easy-to-use interface to load data from various simulators. We recommend that you use this interface; see {ref}`quickstart:using standard combinations` to manually pass the data to combination objects.

Create first an instance of {class}`pytdi.Data` using one of the class methods described in the following sections. Then, use {attr}`pytdi.Data.args` to build your combination. Finally, evaluate the combination passing {attr}`pytdi.Data.measurements` as an argument.

```python
from pytdi import Data
import pytdi.ortho

# data = Data.from_something(), see below
A2 = pytdi.ortho.A2.build(**data.args)
A2_data = A2(data.measurements, unit='frequency')
```

### Data from LISA Instrument

Load the results of a [LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument) simulation from a {class}`lisainstrument.Instrument` object with the {meth}`pytdi.Data.from_instrument` method. Make sure that you have run the simulation before loading its results.

```python
from pytdi import Data
from lisainstrument import Instrument

instru = Instrument(...)
instru.simulate()
data = Data.from_instrument(instru)
```

Alternatively, you can load data from a measurement file on disk, generated using {meth}`lisainstrument.Instrument.write`. Refer to [LISA Instrument](https://gitlab.in2p3.fr/lisa-simulation/instrument)'s documentation for more information.

```python
from pytdi import Data
from lisainstrument import Instrument

instru = Instrument(...)
instru.simulate()
instr.write('measurements.h5', skipped=200)

data = Data.from_instrument('measurements.h5')
```

By default, measured pseudoranges (MPRs) are used as delays, a numerical derivative of the MPRs are used as the delay derivatives, and beatnote frequency fluctuations are used as measurements. Check out [](interface) for more information.

### Data from LISANode

Load the outputs of a [LISANode](https://gitlab.in2p3.fr/j2b.bayle/LISANode) simulation using the {meth}`pytdi.Data.from_lisanode` method. We currently only support the HDF5 format.

```python
from pytdi import Data

# Run, e.g., `lisanode run lisanode:LISA -d 1E5 -o outputs.h5
data = Data.from_lisanode('outputs.h5')
```

By default, measured pseudoranges (MPRs) are used as delays, a numerical derivative of the MPRs are used as the delay derivatives, and beatnote frequency fluctuations are used as measurements. Check out [](interface) for more information.

```{admonition} Units and beatnote polarity
LISANode produces three types of measurements. Fractional frequency fluctuations (unit-less), beatnote offsets in MHz and the total beatnote frequency in Hz. To be fully compatible with all of PyTDI's functionalities {meth}`pytdi.Data.from_lisanode` converts all three quantities to units of Hz. This is achieved by multiplying the fractional frequency fluctuations by the central laser frequency and the beatnote offsets by a factor of $10^6$. Additional, the frequency fluctuations are scaled by the the sign of the beatnote offsets to correct for the beatnote polarity.
```

### Data from LISA GW Response

Load the response to one or more sources, written to a file by [LISA GW Response](https://gitlab.in2p3.fr/lisa-simulation/gw-response), using the {meth}`pytdi.Data.from_gws` method.

```python
from pytdi import Data
from lisagwresponse import GalacticBinary

galbin = GalacticBinary(...)
galbin.write('gws.h5')

data = Data.from_gws('gws.h5', 'my-orbits.h5')
```

All measurements are initialized to zero except for the inter-spacecraft beatnotes, which take the value of the link responses in units of fractional frequency deviations (i.e., Doppler shift, or strain units).

By default, proper pseudoranges (PPRs) in the associated spacecraft proper time (TPS) frames are used as delays. They are read from an [orbit file](https://gitlab.in2p3.fr/lisa-simulation/orbits), passed as argument. See {ref}`quickstart:delays from orbits` for more information.

```{admonition} Units
Since the link responses are expressed in fractional frequency deviations, so are the resulting combinations computed from LISA GW Response.
```

### Delays from orbits

Load delays from an orbit file, created with [LISA Orbits](https://gitlab.in2p3.fr/lisa-simulation/orbits), using the {meth}`pytdi.Data.from_orbits` method. All measurements are initialized to zero except those passed as keyword arguments.

```python
from pytdi import Data

fs = 4 # Hz
sci_12 = np.array(...)
tmi_31 = np.array(...)
data = Data.from_orbits('my-orbits.h5', fs, sci_12=sci_12, tmi_31=tmi_31)
```

Use this method to inject your own signals in a combination. As an example, you might want to study the propagation of a glitch in the inter-spacecraft interferometer.

By default, delays are taken as the orbit file's proper pseudoranges (PPRs) in the associated spacecraft proper time (TPS). Set `dataset='tcb/ltt'` to use the light travel times (LTTs) in the barycentric time frame (TCB) instead.

## Defining custom combinations

Create an instance of the class {class}`pytdi.TDICombination` to define your own combination. You can either use the main constructor and specify the delays applied to the measurements (components) or build your combination from virtual photon paths.

```{admonition} Combinations for LISA
If you plan to build combinations for the [LISA mission](https://www.lisamission.org), we recommend that you use {class}`pytdi.LISATDICombination` instead. You will be able to apply LISA symmetry transformations to define related combinations with {meth}`pytdi.LISATDICombination.reflected` and {meth}`pytdi.LISATDICombination.rotated`.

As an example, Michelson $Y_2$ and $Z_2$ can be deduced from $X_2$ by rotations.

```python
Y2 = X2.rotated()
Z2 = Y2.rotated()
```

### From components

Pass a dictionary containing the beatnotes as keys, and associated time-shift polynomials as values. A time-shift polynomial is list of tuples consisting of a factor and chained time-shift operators (itself as a list).

Delay operators are represented by the string `D_ij`, where *ij* are indices following the standard [LISA conventions](lisa-conventions). Advancement operators are labelled `A_ij`, with *ij* the same indices.

An example is worth a thousand words! Let us define the fictitious LISA combination

```{math}
\delay_{12} \delay_{23} y_{12} - \adv_{12} y_{12} + \frac{1}{2} \adv_{23} \delay_{31} y_{21} + y_{31} \qs
```

You may write

```python
mytdi = LISATDICombination({
    'y_12': [(1, ['D_12', 'D_23']), (-1, ['A_12'])],
    'y_21': [(0.5, ['A_23', 'D_31'])],
    'y_31': [(1, [])],
})
```

### From virtual photon paths

Following the geometrical interpretation of TDI[^2], you can create a combination from the interference of virtual photons. Use {meth}`pytdi.TDICombination.from_string` and pass a string representing the path of different virtual photons propagating along the constellation.

[^2]: M. Vallisneri, *Geometric Time Delay Interferometry*, Phys.Rev.D72:042003, 2005. [arXiv:gr-qc/0504145](https://arxiv.org/abs/gr-qc/0504145).

The first-generation Michelson $X_1$ combination is the interference between two virtual photons, one travelling through spacecraft 1, then 3, 1, 2, back to 1; and another photon going 1, 2, 1, 3, and finally back to 1. Therefore, it can be defined as

```python
X1 = LISATDICombination.from_string('13121 -13121')
```

*Plus signs* represent a path that follows a photon from the event of emission
from the spacecraft indicated by the leftmost index to the event of reception indicated
by the rightmost index. This is computed using advancements. Conversely, *minus signs* represent a path that follows a photon from the event of reception at the spacecraft indicated by the leftmost index to the event of emission indicated by the rightmost index. It is computed using delays. Refer to [](tdi-combination) for an in-depth description of the algorithm used to build the combination.

## Operations on combinations

You can simplify combinations with {meth}`pytdi.TDICombination.simplified`. Similar beatnotes will be factorized, unused beatnotes are removed, delays and advancements that cancel out will be removed.

Most arithmetic operators are implemented as you would expect.

* You can add and subtract two combinations (`A + B` or `A - C`)
* You can multiply and divide a combination by a scalar (`2 * A` or `A / 2`), this will scale the combination
* You can multiply a combination by a list of time-shift operators (`['D_12', 'A_32'] * A`), this will apply a global time shift to the combination
* You can multiply a combination by a 2-tuple consisting of a number and a list of time-shift operators (`(2.0, ['D_12', 'A_32']) * A`), this will scale and time shift the combination
* You can compose a combination and a dictionary of combinations (`A @ {'y_12': B, 'y_21': C}`), this will replace the measurements in the combination by their respective definition given in the dictionary

Refer to [](tdi-combination) for more information.

## Interpolation

PyTDI uses [Lagrange interpolating polynomials](https://en.wikipedia.org/wiki/Lagrange_polynomial) as [fractional delay filters](https://www.intechopen.com/chapters/18566).

For numerical stability in the case of *N* chained delays, the total delay is first computed from *N-1* interpolation processes and then applied to the measurement as a last step. You can set independently the interpolation order for interpolating the delays (when calling {meth}`pytdi.TDICombination.build`) and for interpolating the measurements (when calling the build combination).

```python
data = ...
comb_built = my_comb.build(**data.args, order=5)
results = comb_built(data.measurements, order=21)
```

You must use odd interpolation orders. Using greater orders increases the quality of the interpolation at high frequencies but has an impact on the runtime.
