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
import asyncio
from marvelpy import MarvelClient

async def main():
    async with MarvelClient("your_public_key", "your_private_key") as client:
        # Get characters
        characters = await client.get_characters(params={"limit": 5})
        print(f"Found {characters['data']['count']} characters")

        # Search for specific characters
        iron_man = await client.get_characters(params={"name": "iron man"})
        print(f"Iron Man: {iron_man['data']['results'][0]['name']}")

asyncio.run(main())
```

## What's Available

Currently, Marvelpy v0.2.1 includes:

- **MarvelClient** - Full-featured async client for Marvel API
- **Authentication** - Automatic Marvel API authentication
- **Character Access** - Search and retrieve character information
- **Error Handling** - Robust retry logic and error management
- **Type Safety** - Complete type hints throughout
- **Test Suite** - Comprehensive tests with 85% coverage
- **Documentation** - Full API documentation with examples

## Coming Soon

Future versions will include:

- **Comics** - Access comic book data and metadata
- **Events** - Marvel universe events and storylines
- **Series** - Comic series information
- **Stories** - Individual story details
- **Creators** - Creator and artist information
- **Advanced Search** - More sophisticated filtering options
- **Caching** - Built-in response caching
- **Rate Limiting** - Automatic rate limit management

## Current Usage Examples

```python
import asyncio
from marvelpy import MarvelClient

async def main():
    async with MarvelClient("your_public_key", "your_private_key") as client:
        # Get all characters (with pagination)
        characters = await client.get_characters(params={"limit": 10})

        # Search for specific characters
        heroes = await client.get_characters(params={"name": "iron man"})

        # Get character by ID
        character = await client.get("characters/1009368")

        # Health check
        status = await client.health_check()

asyncio.run(main())
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

This project is licensed under the MIT License.

## Links

- **PyPI**: https://pypi.org/project/marvelpy/
- **GitHub**: https://github.com/jlgranof/marvelpy
- **Documentation**: https://jlgranof.github.io/marvelpy/
- **Issues**: https://github.com/jlgranof/marvelpy/issues

---

**Note**: This package is actively developed. Version 0.2.1 includes a fully functional MarvelClient with character access, authentication, and comprehensive error handling. More endpoints and features are coming in future versions!
