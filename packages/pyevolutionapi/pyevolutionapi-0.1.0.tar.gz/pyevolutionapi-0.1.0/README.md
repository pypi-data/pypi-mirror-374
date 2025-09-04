# 🚀 PyEvolution

**Python client for Evolution API - WhatsApp integration made simple**

[![CI](https://github.com/lpcoutinho/pyevolution/workflows/CI/badge.svg)](https://github.com/lpcoutinho/pyevolution/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lpcoutinho/pyevolution/branch/main/graph/badge.svg)](https://codecov.io/gh/lpcoutinho/pyevolution)
[![PyPI version](https://badge.fury.io/py/pyevolutionapi.svg)](https://badge.fury.io/py/pyevolutionapi)
[![Python Version](https://img.shields.io/pypi/pyversions/pyevolutionapi.svg)](https://pypi.org/project/pyevolutionapi/)
[![Downloads](https://pepy.tech/badge/pyevolutionapi)](https://pepy.tech/project/pyevolutionapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

PyEvolution is a modern, type-safe Python library that provides an intuitive interface to the Evolution API, making WhatsApp integration effortless for developers.

## ✨ Features

- 🎯 **Type-safe**: Complete type hints with Pydantic models
- 🔄 **Async/Sync**: Full support for both synchronous and asynchronous operations
- 🛡️ **Error Handling**: Comprehensive exception hierarchy with detailed error information
- 📱 **Complete API Coverage**: Support for messages, media, groups, instances, and more
- 🔧 **Easy Configuration**: Environment variables and multiple authentication methods
- 📚 **Well Documented**: Extensive documentation and examples
- ✅ **Tested**: Comprehensive test suite with high coverage
- 🔌 **Webhook Support**: Built-in webhook configuration and event handling

## 🚀 Quick Start

### Installation

```bash
pip install pyevolutionapi
```

### Basic Usage

```python
from pyevolutionapi import EvolutionClient

# Create client
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key-here"
)

# Create an instance
instance = client.instance.create(
    instance_name="my-whatsapp-bot",
    qrcode=True
)

# Send a message
response = client.messages.send_text(
    instance="my-whatsapp-bot",
    number="5511999999999",
    text="Hello from PyEvolution! 🎉"
)

print(f"Message sent! ID: {response.message_id}")
```

### Async Usage

```python
import asyncio
from pyevolutionapi import EvolutionClient

async def main():
    client = EvolutionClient()

    async with client:
        # Create instance
        instance = await client.instance.acreate(
            instance_name="async-bot",
            qrcode=True
        )

        # Send multiple messages concurrently
        tasks = [
            client.messages.asend_text(
                instance="async-bot",
                number="5511999999999",
                text=f"Message {i}"
            )
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)
        print(f"Sent {len(results)} messages!")

asyncio.run(main())
```

## 📋 Supported Operations

### 🏠 Instance Management

- Create and manage WhatsApp instances
- QR code generation and connection status
- Instance restart, logout, and deletion

### 💬 Messages

- Send text messages with formatting
- Send media (images, videos, documents, audio)
- Send location, contacts, and stickers
- Interactive messages (polls, lists, buttons)
- Status/Stories publishing

### 👥 Groups

- Create and manage WhatsApp groups
- Add/remove participants and manage permissions
- Update group info (name, description, picture)
- Generate and manage invite links

### 💬 Chat Operations

- Manage conversations and contacts
- Mark messages as read
- Send presence indicators (typing, recording)
- Block/unblock contacts

### 👤 Profile Management

- Update profile information
- Manage profile picture and status
- Configure privacy settings

### 🔗 Webhooks & Events

- Configure webhooks for real-time events
- Support for WebSocket, RabbitMQ, and AWS SQS
- Comprehensive event handling

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your-global-api-key

# Optional
EVOLUTION_INSTANCE_NAME=default-instance
EVOLUTION_DEBUG=false
EVOLUTION_REQUEST_TIMEOUT=30
EVOLUTION_MAX_RETRIES=3
```

### Client Configuration

```python
from pyevolutionapi import EvolutionClient

client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key",
    default_instance="my-instance",
    timeout=30.0,
    max_retries=3,
    debug=False
)
```

## 📖 Examples

### Send Different Message Types

```python
# Text message
client.messages.send_text(
    instance="my-bot",
    number="5511999999999",
    text="Hello *World*! _Italic_ ~strikethrough~"
)

# Image with caption
client.messages.send_media(
    instance="my-bot",
    number="5511999999999",
    mediatype="image",
    media="https://example.com/image.jpg",
    caption="Check out this image! 📸"
)

# Location
client.messages.send_location(
    instance="my-bot",
    number="5511999999999",
    name="Times Square",
    address="New York, NY",
    latitude=40.7589,
    longitude=-73.9851
)

# Poll
client.messages.send_poll(
    instance="my-bot",
    number="5511999999999",
    name="What's your favorite language?",
    values=["Python", "JavaScript", "Go", "Rust"]
)
```

## 🚀 Development & Contributing

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/lpcoutinho/pyevolution.git
cd pyevolution

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyevolution --cov-report=html

# Run specific test files
pytest tests/unit/test_client.py

# Run tests with verbose output
pytest -v
```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for quality checks

```bash
# Format code
black pyevolution tests examples

# Lint code
ruff check pyevolution tests examples

# Type check
mypy pyevolution

# Run all quality checks
pre-commit run --all-files
```

### CI/CD Pipeline

The project uses GitHub Actions for:

- **Continuous Integration**: Automated testing across Python 3.8-3.12 on multiple OS
- **Code Quality**: Automated formatting, linting, and type checking
- **Security**: CodeQL analysis and dependency scanning
- **Documentation**: Automatic deployment to GitHub Pages
- **Publishing**: Automated releases to PyPI on tag push

### Release Process

1. Update version in `pyproject.toml`
2. Create a git tag: `git tag v0.1.1`
3. Push tag: `git push origin v0.1.1`
4. GitHub Actions will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Evolution API](https://github.com/EvolutionAPI/evolution-api) - The powerful
  WhatsApp API that makes this possible
- [Pydantic](https://github.com/pydantic/pydantic) - For excellent data
  validation
- [httpx](https://github.com/encode/httpx) - For modern HTTP client
  capabilities

## 📞 Support

- 🐛 **Bug Reports**:
  [GitHub Issues](https://github.com/lpcoutinho/pyevolution/issues)
- 💬 **Discussions**:
  [GitHub Discussions](https://github.com/lpcoutinho/pyevolution/discussions)
- 📧 **Email**: your.email@example.com

## 🔗 Links

- [PyPI Package](https://pypi.org/project/pyevolutionapi/) (Coming Soon)
- [GitHub Repository](https://github.com/lpcoutinho/pyevolution)
- [Evolution API](https://evolution-api.com/)

---

Made with ❤️ by [Luiz Paulo Coutinho](https://www.linkedin.com/in/luizpaulocoutinho/)

**PyEvolution** - Making WhatsApp integration simple, powerful, and fun! 🚀
