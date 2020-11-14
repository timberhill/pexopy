# PEXOpy v0.2 Beta

A python wrapper for [PEXO](https://github.com/phillippro/pexo) software.

**NOTE** : this is an early alpha and is under development.

## Requirements

- Python 3.6 or higher. It should work with 2.7, but it is not recommended.
- numpy
- rpy2
- [PEXO](https://github.com/phillippro/pexo) and its dependencies, see [documentation](http://rpubs.com/Fabo/pexo) for installation guidance.

## Installation

Install the dependencies and set an environment variable `$PEXODIR` to a path to the PEXO repository. Add `export PEXODIR=/example/path/to/pexo` to your `~/.bashrc` or `~/.bash_profile` if you’re using bash, or `setenv PEXODIR /example/path/to/pexo`to `~/.tcshrc` if you’re using tcsh.

### from this repository

```sh
git clone https://github.com/timberhill/pexopy.git
cd pexopy
python setup.py install
```

or

```sh
pip install git+https://github.com/timberhill/pexopy.git -U
```

### uninstall

```sh
pip uninstall pexopy
```

## Usage

PEXO needs to run in a pexo environment (see [readme](https://github.com/phillippro/pexo#local-installation)).

The package contains a python class `Pexo` that is used to run PEXO.
Optional arguments:

`Rscript`: path to Rscript executable (uses output of `which Rscript` if None)

`pexodir`: path to PEXO directory (uses `PEXODIR` environment variable if None)

`verbose`: whether to show the PEXO stdout (default: True)

The function to start PEXO is `Pexo().run()`. The arguments are consistent with the command line arguments of PEXO (see [documentation](http://rpubs.com/Fabo/pexo2)).

## Examples

### Emulation

```python
from pexopy import Pexo

output = Pexo(verbose=False).run(
    mode="emulate",
    primary="HD128621",
    ins="HARPS",
    time="2450000 2453000 10"
)
```

Here, `output` is a type of `EmulationOutput`:

`output.contents` contains a `numpy.ndarray` with the output results

`output.path` is a PEXO output file path

`output.saveto(path=...)` saves the output table to the specified path

### Fitting

```python
from pexopy import Pexo

output = Pexo(verbose=False).run(
    primary="HD239960",
    mode="fit",
    N=100,
    ncore=4,
    C=1,
    o="HD239960-fit.Robj"
)
```

Here, `output` is a type of `FitOutput`:

`output.contents` contains a `rpy2` object with all the fitting results

`output.path` is a PEXO output file path

`output.saveto(path=...)` saves the output `Robj` file to the specified path

`output.parstat` contains the fit parameters, their values, and some key statistical parameters of the MCMC fit, e.g. `output.raOff.mean` and `output.raOff.sd` being the mean value and standard deviation of the right ascension offset

`output.mc` contains the markov chains of each of the parameters.

`output.data` is a table of data points with columns `utc`,`V1`,`eV1`,`V2`,`eV2`,`star`,`type`,`instrument`,`wavelength`

`output.model` is the same table, but with the fitted model values
