# Water filling

A demonstration of the water-filling problem: Given an uneven tub defined by a
list of **heights** and a certain **volume** of water, what will the **level**
of the water be once it has sloshed around and stabilized?

The water-filling problem can be solved by analyzing the function
`volume(heights, level)`, the volume of water present when the level is at a
given value. Since this function is piecewise linear and increasing in `level`,
we can invert it using linear interpolation (see `water_filling/numerics.py` in
the source code).

The purpose of this project is to practice standard routing and caching patterns
using the [Microdot](https://microdot.readthedocs.io/en/latest/index.html)
framework.

<!-- end_site_header -->

## Preview

The design goal here is to render everything on the backend, so you should
follow the instructions below to serve locally if you want to play with all the
API options and test the caching behavior. Nonetheless, the repo also includes a
script to build a nerfed version of the project to a fully static site so you
can preview the stylesheets [here on GitHub
Pages](https://maxkapur.com/water_filling.py/).

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

- Add `config.toml` with options
- Add `created_at`, `accessed_at` columns to cache database and periodically
  purge old records
