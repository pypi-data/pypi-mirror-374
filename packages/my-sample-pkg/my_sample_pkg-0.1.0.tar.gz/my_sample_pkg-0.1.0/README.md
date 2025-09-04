# my-sample-pkg

A simple sample Python package for PyPI demonstration.

## Installation

```bash
pip install my-sample-pkg
```

## Usage

```python
from my_sample_pkg import hello

hello()  # Prints "Hello, PyPI!"
```

## Requirements

- Python 3.8 or higher

## Build and Upload

### Build the package

```bash
pip install build twine
python -m build
```

### Upload to PyPI

```bash
# Upload to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```



## License

MIT License