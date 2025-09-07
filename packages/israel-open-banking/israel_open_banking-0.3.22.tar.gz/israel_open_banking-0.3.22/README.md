# Israel Open Banking SDK

[![CI](https://github.com/shavve/open-banking/workflows/CI/badge.svg)](https://github.com/shavve/open-banking/actions)
[![PyPI version](https://badge.fury.io/py/open-banking.svg)](https://badge.fury.io/py/open-banking)
[![Documentation](https://readthedocs.org/projects/open-banking/badge/?version=latest)](https://open-banking.readthedocs.io/en/latest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source Python SDK for Israeli Open Banking APIs, providing a unified interface for multiple financial service providers including Isracard, Max, and Cal.

## 🚀 Features

- **Multi-Provider Support**: Connect to multiple Israeli financial institutions
- **PSD2 AIS Core Module**: Standardized PSD2-compliant Account Information Services
- **Modular Design**: Each provider in its own package for easy maintenance
- **Type Safety**: Full type annotations and validation with Pydantic
- **Async Support**: Both synchronous and asynchronous API clients
- **Comprehensive Error Handling**: Detailed error messages and context
- **Configuration Management**: Environment-based configuration
- **Extensive Testing**: Full test coverage with pytest
- **Documentation**: Complete API documentation with examples

## 🏗️ PSD2 AIS Core Module

The SDK includes a comprehensive PSD2 AIS (Account Information Services) core module based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification. This provides:

- **Standardized Enums**: All PSD2-specific enumerations (account status, transaction status, consent status, etc.)
- **Pydantic Models**: Complete data models for all PSD2 data structures
- **Abstract Base Classes**: Interface definitions for PSD2-compliant implementations
- **Exception Hierarchy**: AIS-specific exception classes for proper error handling

### Using the AIS Core Module

```python
from core.ais import (
    AccountDetails, TransactionList, BookingStatus,
    Consent, ConsentStatus, AISBaseClient
)

# Use PSD2 enums for type safety
transactions = client.get_transactions(
    account_id="123",
    booking_status=BookingStatus.BOOKED,
    with_balance=True
)

# Use PSD2 models for data validation
account: AccountDetails = client.get_account_details("123")
print(f"Account: {account.name}, Balance: {account.balances}")

# Check consent status
if consent.consent_status == ConsentStatus.VALID:
    print("Consent is active")
```

For more details, see the [AIS Core Module Documentation](israel_open_banking/core/ais/README.md).

## 📦 Installation

### Using Poetry (Recommended)

```bash
poetry add open-banking
```

### Using pip

```bash
pip install israel-open-banking
```

## 🏃‍♂️ Quick Start

### Basic Usage

```python
from core.client import OpenBankingClient

# Initialize the client
client = OpenBankingClient()

# Get user accounts
accounts = client.get_accounts()

# Get transactions
transactions = client.get_transactions(
    account_id="12345",
    from_date="2024-01-01",
    to_date="2024-01-31"
)
```

### Provider-Specific Usage

```python
from isracard import IsracardClient

# Initialize Isracard client
isracard = IsracardClient()

# Get cards
cards = isracard.cards.get_cards()

# Get card transactions
transactions = isracard.cards.get_card_transactions(
    card_id="card_123",
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Manage consents
consent = isracard.consents.create_consent(
    user_id="user_123",
    permissions=["accounts", "transactions"]
)
```

## ⚙️ Configuration

The SDK uses environment variables for configuration. Copy `env.example` to `.env` and fill in your values:

```bash
# Required
OPEN_BANKING_API_BASE_URL=https://api.openbanking.gov.il
OPEN_BANKING_CLIENT_ID=your_client_id
OPEN_BANKING_CLIENT_SECRET=your_client_secret
OPEN_BANKING_REDIRECT_URI=https://your-app.com/callback

# Provider-specific
ISRACARD_API_URL=https://api.isracard.co.il/openbanking
ISRACARD_CLIENT_ID=your_isracard_client_id
ISRACARD_CLIENT_SECRET=your_isracard_client_secret
```

## 🏦 Supported Providers

| Provider | Status | Features |
|----------|--------|----------|
| **Isracard** | ✅ Implemented | Cards, Transactions, Consents, Loans |
| **Max** | 🚧 Planned | Credit cards, Financial services |
| **Cal** | 🚧 Planned | Credit cards, Banking services |

## 📚 Documentation

- **[Full Documentation](https://open-banking.readthedocs.io/)**
- **[API Reference](https://open-banking.readthedocs.io/en/latest/api/)**
- **[Examples](https://open-banking.readthedocs.io/en/latest/examples/)**
- **[Contributing Guide](CONTRIBUTING.md)**

## 🛠️ Development

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/shavve/open-banking.git
cd open-banking

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=israel_open_banking

# Run specific test file
poetry run pytest tests/test_core.py

# Run linting
poetry run ruff check israel_open_banking/ tests/

# Run type checking
poetry run mypy israel_open_banking/
```

### Code Quality

```bash
# Format code
poetry run black israel_open_banking/ tests/
poetry run isort israel_open_banking/ tests/

# Lint code
poetry run ruff check israel_open_banking/ tests/

# Type checking
poetry run mypy israel_open_banking/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`poetry run pytest`)
6. Run code quality checks (`poetry run ruff check src/ tests/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **Ruff** for linting
- **MyPy** for type checking
- **Pre-commit** hooks for automated checks

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for testing
- Use pytest-cov for coverage reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://open-banking.readthedocs.io](https://open-banking.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/shavve/open-banking/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shavve/open-banking/discussions)
- **Email**: admin@shavve.io

## 🙏 Acknowledgments

- Israeli Open Banking Initiative
- All contributors and maintainers
- The open-source community

## 📈 Roadmap

- [ ] Max provider implementation
- [ ] Cal provider implementation
- [ ] Additional financial institutions
- [ ] Webhook support
- [ ] Rate limiting improvements
- [ ] Caching layer
- [ ] GraphQL support
- [ ] Mobile SDK

---

**Note**: This SDK is in active development. Please check the [documentation](https://open-banking.readthedocs.io/) for the latest updates and breaking changes.
