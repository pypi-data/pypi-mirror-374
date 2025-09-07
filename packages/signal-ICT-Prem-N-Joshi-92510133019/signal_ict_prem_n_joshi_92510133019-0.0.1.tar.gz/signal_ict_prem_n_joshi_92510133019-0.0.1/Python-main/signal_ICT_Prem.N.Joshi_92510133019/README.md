
# signal_ICT_Prem.N.Joshi_92510133019

A teaching package demonstrating basic **Signals & Systems** concepts in Python.

## Package Structure

```
signal_ICT_Prem.N.Joshi_92510133019/
├─ __init__.py
├─ unitary_signals.py
├─ trigonometric_signals.py
├─ operations.py
main.py
```

## Installation (from source)

```bash
pip install -r requirements.txt  # optional; only numpy, matplotlib required
```

Or simply run `python main.py` from the project root.

## Usage

See `main.py` for a complete demonstration:
- Unit step & impulse
- Sine wave
- Time shift
- Addition (step + ramp)
- Multiplication (sine × cosine)

Plots will be saved in `./plots/`.

## Building Distributions (Wheel & sdist)

Ensure you have packaging tools:

```bash
python -m pip install --upgrade build twine
python -m build
```

This will produce `.whl` and `.tar.gz` in `dist/`.
Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Install from TestPyPI (example):

```bash
python -m pip install -i https://test.pypi.org/simple/ signal_ICT_Prem.N.Joshi_92510133019 --no-deps
```

## Notes

- `time_shift` keeps output length same as input, padding with zeros.
- `time_scale` uses interpolation to preserve length.
- All functions can plot (`show=True`) and also return NumPy arrays for further processing.
