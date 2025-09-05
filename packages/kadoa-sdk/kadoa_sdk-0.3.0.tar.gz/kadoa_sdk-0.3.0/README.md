# Kadoa SDK for Python

Official Python SDK for the Kadoa API, providing easy integration with Kadoa's web data extraction platform.

## Getting Started

### Obtaining an API Key

To use the Kadoa SDK, you'll need an API key:

1. Register at [https://www.kadoa.com/](https://www.kadoa.com/)
2. Navigate to [https://www.kadoa.com/account](https://www.kadoa.com/account)
3. Copy your API key from the account page

### Installation

```bash
pip install kadoa-sdk
```

For development:
```bash
pip install -e .
```

## Quick Start

```python
from kadoa_sdk import initialize_app, run_extraction, KadoaConfig, ExtractionOptions

# Initialize the SDK
app = initialize_app(KadoaConfig(
    api_key="your-api-key",
    base_url="https://api.kadoa.com"  # optional, defaults to production
))

# Run an extraction
result = run_extraction(app, ExtractionOptions(
    urls=["https://example.com"],
    name="My Extraction Workflow"
))

if result:
    print(f"Workflow created with ID: {result.workflow_id}")
```

## Configuration

The SDK can be configured using environment variables or directly in code:

### Environment Variables

Create a `.env` file:
```env
KADOA_API_KEY=your-api-key
KADOA_API_URL=https://api.kadoa.com
KADOA_TIMEOUT=30
```

Then load them in your code:
```python
import os
from dotenv import load_dotenv
from kadoa_sdk import initialize_app, KadoaConfig

load_dotenv()

app = initialize_app(KadoaConfig(
    api_key=os.environ["KADOA_API_KEY"],
    base_url=os.environ.get("KADOA_API_URL", "https://api.kadoa.com"),
    timeout=int(os.environ.get("KADOA_TIMEOUT", "30"))
))
```
## Development

### Project Structure

```
sdks/python/
├── kadoa_sdk/
│   ├── __init__.py          # Public API exports
│   ├── app.py               # Application initialization
│   ├── extraction/          # Extraction module
│   │   ├── __init__.py
│   │   ├── extraction.py    # Core extraction logic
│   │   └── client.py        # API client helpers
│   └── generated/           # Auto-generated API client
├── tests/
│   └── e2e/
│       └── test_run_extraction.py
├── examples/
│   └── run_extraction.py
├── pyproject.toml
├── pytest.ini
└── Makefile
```

### Running Tests

```bash
# Run all tests
make test

# Run E2E tests only
make test-e2e

# Run with coverage
make test-coverage
```

### Installing Development Dependencies

```bash
make install-dev
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format
```

## License

MIT

## Support

For support, please visit [Kadoa Support](https://support.kadoa.com) or contact support@kadoa.com.