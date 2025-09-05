# Marvelpy

[![PyPI version](https://badge.fury.io/py/marvelpy.svg)](https://badge.fury.io/py/marvelpy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://jlgranof.github.io/marvelpy/)

A fully-typed Python client for the Marvel Comics API.

## Features

- 🚀 **Async-first design** - Built with modern async/await patterns
- 🔒 **Fully typed** - Complete type hints for better IDE support
- 📚 **Comprehensive** - Full coverage of the Marvel Comics API
- 🛡️ **Enterprise-ready** - Production-grade error handling and retry logic
- 📖 **Well documented** - Extensive documentation and examples

## Quick Start

### Installation

```bash
pip install marvelpy
```

### Basic Usage

```python
import marvelpy

# Get a hello message
message = marvelpy.hello_world()
print(message)  # "Hello from Marvelpy!"
```

## What's Available

Currently, Marvelpy v0.1.0 includes:

- **Hello World Function** - Basic demonstration functionality
- **Complete test suite** - 100% test coverage
- **Type safety** - Full type hints throughout
- **Documentation** - Comprehensive docs with examples

## Coming Soon

The full Marvel Comics API client will include:

- **Characters** - Search and retrieve character information
- **Comics** - Access comic book data and metadata
- **Events** - Marvel universe events and storylines
- **Series** - Comic series information
- **Stories** - Individual story details
- **Creators** - Creator and artist information

## Example Future Usage

```python
# This is planned functionality - not yet implemented
import marvelpy

# Initialize the client
client = marvelpy.MarvelClient(api_key="your_key", private_key="your_private_key")

# Search for characters
characters = await client.characters.search("spider-man")

# Get character details
spiderman = await client.characters.get(1009610)

# Search comics
comics = await client.comics.search("amazing spider-man")
```

## Requirements

- Python 3.8 or higher
- httpx>=0.23.0
- pydantic>=1.10.0
- typing-extensions>=4.9.0
- click>=8.1.0

## Development

### Setup

```bash
git clone https://github.com/jlgranof/marvelpy.git
cd marvelpy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing

```bash
pytest
pytest --cov=marvelpy --cov-report=html
```

### Documentation

```bash
mkdocs serve  # Serve docs locally
mkdocs build  # Build docs
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://jlgranof.github.io/marvelpy/contributing/) for details.

## Documentation

- 📖 [Full Documentation](https://jlgranof.github.io/marvelpy/)
- 🚀 [Quick Start Guide](https://jlgranof.github.io/marvelpy/quickstart/)
- 📚 [API Reference](https://jlgranof.github.io/marvelpy/api/hello/)
- 🔧 [Installation Guide](https://jlgranof.github.io/marvelpy/installation/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **PyPI**: https://pypi.org/project/marvelpy/
- **GitHub**: https://github.com/jlgranof/marvelpy
- **Documentation**: https://jlgranof.github.io/marvelpy/
- **Issues**: https://github.com/jlgranof/marvelpy/issues

---

**Note**: This package is currently in early development. The initial release (v0.1.0) includes basic functionality with a hello world example. Full Marvel API integration is coming soon!