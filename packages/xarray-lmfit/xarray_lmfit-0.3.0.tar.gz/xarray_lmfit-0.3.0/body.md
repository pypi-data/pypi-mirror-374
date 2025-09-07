## v0.3.0 (2025-09-07)

### 💥 Breaking Changes

- Using `modelfit` with `progress=True` now requires the package to be installed with the `progress` optional dependency group, like `pip install xarray-lmfit[progress]`. ([d7324c9](https://github.com/kmnhan/xarray-lmfit/commit/d7324c94b483527bd4540c1328b32d9f4054d2b4))

- While adding dask support, this release drops support for rudimentary joblib-based parallelization across multiple data variables; this removes the `parallel` and `parallel_kw` arguments to `modelfit`. Use dask arrays as an alternative. ([d3f90df](https://github.com/kmnhan/xarray-lmfit/commit/d3f90dffb226fab71e96309f41da35e0a929adc5))

### ✨ Features

- **modelfit:** Add `rsquared` to `modelfit_stats` by @newton-per-sqm (#19) ([e5a8a1e](https://github.com/kmnhan/xarray-lmfit/commit/e5a8a1e8a515627a3b5b6dd2c8fad83b9d15c3d7))

  Co-authored-by: Pascal Muster <Pascal.Muster@infineon.com>

- **modelfit:** properly support dask and drop support for joblib-based parallelization ([d3f90df](https://github.com/kmnhan/xarray-lmfit/commit/d3f90dffb226fab71e96309f41da35e0a929adc5))

  `modelfit` now supports dask arrays properly with minimal serialization overhead.

### ♻️ Code Refactor

- **modelfit:** make `tqdm` an optional dependency (#20) ([d7324c9](https://github.com/kmnhan/xarray-lmfit/commit/d7324c94b483527bd4540c1328b32d9f4054d2b4))

  The `tqdm` package which provides the progress bar when `progress=True` is now an optional dependency. If not installed, passing `progress=True` to `modelfit` will now result in an error.

[main 1f8eb91] bump: version 0.2.3 → 0.3.0
 3 files changed, 15 insertions(+), 3 deletions(-)

