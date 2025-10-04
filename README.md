# Water filling

A demonstration of the water-filling problem: Given an uneven tub defined by a
list of **heights** and a certain **volume** of water, what will the **level**
of the water be once it has sloshed around and stabilized?

The water-filling problem can be solved by analyzing the function
`volume(heights, level)`, the volume of water present when the level is at a
given value. Since this function is piecewise linear and increasing in `level`,
we can invert it using linear interpolation (see
`water_filling/water_filling.py` in the source code).

The purpose of this project is to practice standard routing and caching patterns
using the [Microdot](https://microdot.readthedocs.io/en/latest/index.html)
framework.

<!-- end_site_header -->

## Usage

```shell
# Create/activate a venv
python -m venv venv
source ./venv/bin/activate.fish  # or appropriate command for your shell
python -m pip install --editable .[dev]
python -m pytest  # run tests
python -m water_filling  # serve to localhost
```

## Ideas

- Add `created_at`, `accessed_at` columns to cache database and periodically
  purge old records
