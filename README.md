# Water filling

This site demonstrates the water-filling problem: Given an uneven tub defined by
a list of **heights** and a certain **volume** of water, what will the **level**
of the water be once it has sloshed around and stabilized?

The water-filling problem can be solved by deriving the function for
`volume(heights, level)`, the volume of water present when the level is at a
given value. Since this function is monotonically increasing in `level`, we can
find the level that contains the target volume from the original problem using a
root-finding algorithm like bisection or the [secant
method](https://en.wikipedia.org/wiki/Secant_method) used here.

The main purpose of this project is to play with the
[Microdot](https://microdot.readthedocs.io/en/latest/index.html) framework and
practice some standard routing and caching patterns.

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

- Organize `interface.py` into a `routes.py` with just the routes and a new file
  with the parsing/error handling/caching logic.
- Test caching behavior. Use Pytest monkeypatch to start tests with no cache
  and then test that it is populated and used.
