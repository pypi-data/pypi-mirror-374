# xarray-lmfit documentation

:::{only} format_html
**Date**: {sub-ref}`today`

[![Python Versions](https://img.shields.io/pypi/pyversions/xarray-lmfit?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/xarray-lmfit/)
[![PyPi](https://img.shields.io/pypi/v/xarray-lmfit?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/xarray-lmfit/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/xarray-lmfit?style=flat-square&logo=condaforge&logoColor=white)](https://anaconda.org/conda-forge/xarray-lmfit/)
[![Last Commit](https://img.shields.io/github/last-commit/kmnhan/xarray-lmfit?style=flat-square&logo=github&color=lightseagreen)](https://github.com/kmnhan/xarray-lmfit.git)

:::

xarray-lmfit is a Python package that bridges the power of [xarray](http://xarray.pydata.org) for handling multi-dimensional labeled arrays with the flexible fitting capabilities of [lmfit](https://lmfit.github.io/lmfit-py/).

With xarray-lmfit, [lmfit models](https://lmfit.github.io/lmfit-py/model.html) can be fit to xarray Datasets and DataArrays, automatically propagating across multiple dimensions. The fit results are stored as xarray Datasets, retaining the original coordinates and dimensions of the input data.

```{admonition} Disclaimer

Please note that this package is independent and not affiliated with the xarray or lmfit projects. If you encounter any issues, please report them on the [xarray-lmfit issue tracker](https://github.com/kmnhan/xarray-lmfit/issues).

```

```{toctree}
:caption: Contents
:maxdepth: 2
:hidden:

user-guide/index
api
changelog
```
