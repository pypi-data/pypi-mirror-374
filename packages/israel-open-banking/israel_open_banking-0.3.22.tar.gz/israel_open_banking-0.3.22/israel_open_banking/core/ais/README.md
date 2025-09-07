# PSD2 AIS Core Module

This module provides the core types, enums, base classes, and interfaces for implementing PSD2-compliant Account Information Services (AIS) based on the Berlin Group NextGenPSD2 Framework v1.3.14 specification.

## Overview

The AIS core module is designed to provide a standardized foundation for all banks and credit card providers implementing PSD2-compliant APIs. It includes:

- **Enums**: All PSD2-specific enumerations (account status, transaction status, consent status, etc.)
- **Models**: Pydantic models for all PSD2 data structures
- **Base Classes**: Abstract base classes defining the interface for AIS operations
- **Exceptions**: AIS-specific exception classes for error handling

## Structure

```
src/core/ais/
├── __init__.py          # Main module exports
├── enums.py            # PSD2 enums and constants
├── models.py           # Pydantic data models
├── base.py             # Abstract base classes
├── exceptions.py       # AIS-specific exceptions
└── README.md           # This file
```

## Key Components

### Enums (`enums.py`)

All PSD2-specific enumerations including:

- `AccountStatus`: Account status values (enabled, deleted, blocked)
- `AccountUsage`: Account usage types (private, professional)
- `AuthenticationType`: Authentication methods (SMS_OTP, CHIP_OTP, etc.)
- `BookingStatus`: Transaction booking status (booked, pending, both)
- `CashAccountType`: Account types (current, savings, loan, etc.)
- `ConsentStatus`: Consent lifecycle status
- `TransactionStatus`: Transaction status based on ISO 20022
- `BalanceType`: Balance types (closing booked, expected, etc.)

### Models (`models.py`)

Pydantic models for all PSD2 data structures:

#### Account Models
- `AccountDetails`: Complete account information
- `AccountList`: List of accounts
- `AccountOwner`: Account owner information
- `AccountReference`: Account reference (IBAN, BBAN, PAN, etc.)

#### Transaction Models
- `Transaction`: Transaction details
- `TransactionList`: List of transactions with booked/pending separation
- `TransactionDetails`: Detailed transaction information
- `CardTransaction`: Card-specific transaction data

#### Balance Models
- `Balance`: Balance information with type and amount
- `BalanceList`: List of balances

#### Consent Models
- `Consent`: Complete consent information
- `ConsentStatusResponse`: Consent status response
- `ConsentAccess`: Consent access configuration
- `ConsentAccountAccess`: Account-specific consent access
- `ConsentCardAccountAccess`: Card account-specific consent access

#### Authentication Models
- `AuthenticationObject`: Authentication method information
- `ChallengeData`: Challenge data for SCA
- `ScaMethods`: List of available SCA methods

#### Common Models
- `Amount`: Monetary amount with currency
- `Address`: Address information
- `Links`: Navigation links (HATEOAS)
- `TppMessage`: TPP message for error handling

### Base Classes (`base.py`)

Abstract base classes defining the interface for AIS operations:

#### `AISBaseClient`
Main abstract class that all AIS clients must implement:

```python
class AISBaseClient(ABC):
    @abstractmethod
    def get_accounts(self, with_balance: bool = False) -> AccountList:
        """Get list of accounts."""
        pass

    @abstractmethod
    def get_account_details(self, account_id: str, with_balance: bool = False) -> AccountDetails:
        """Get account details."""
        pass

    @abstractmethod
    def get_balances(self, account_id: str) -> BalanceList:
        """Get account balances."""
        pass

    @abstractmethod
    def get_transactions(self, account_id: str, ...) -> TransactionList:
        """Get account transactions."""
        pass

    @abstractmethod
    def get_transaction_details(self, account_id: str, transaction_id: str) -> TransactionDetails:
        """Get transaction details."""
        pass
```

#### Manager Classes
Specialized managers for different AIS operations:

- `AISConsentManager`: Consent creation, status checking, authorization
- `AISAccountManager`: Account listing and details
- `AISTransactionManager`: Transaction listing and details
- `AISBalanceManager`: Balance retrieval

### Exceptions (`exceptions.py`)

AIS-specific exception hierarchy:

- `AISException`: Base exception for all AIS operations
- `AISConsentException`: Consent-related errors
- `AISAccountException`: Account-related errors
- `AISTransactionException`: Transaction-related errors
- `AISAuthenticationException`: Authentication errors
- `AISAuthorizationException`: Authorization errors
- `AISValidationException`: Validation errors
- `AISRateLimitException`: Rate limiting errors

Specialized exceptions:
- `AISConsentExpiredException`: When consent has expired
- `AISConsentRevokedException`: When consent has been revoked
- `AISAccountNotFoundException`: When account is not found
- `AISTransactionNotFoundException`: When transaction is not found

## Usage

### For Provider Implementations

All banks and credit card providers should implement the abstract base classes:

```python
from core.ais import AISBaseClient, AccountList, AccountDetails

class MyBankAISClient(AISBaseClient):
    def get_accounts(self, with_balance: bool = False) -> AccountList:
        # Implement account listing logic
        pass

    def get_account_details(self, account_id: str, with_balance: bool = False) -> AccountDetails:
        # Implement account details logic
        pass

    # ... implement other abstract methods
```

### For Consumers

Consumers can use the models and enums for type safety:

```python
from core.ais import AccountDetails, TransactionList, BookingStatus

# Use enums for type safety
transactions = client.get_transactions(
    account_id="123",
    booking_status=BookingStatus.BOOKED,
    with_balance=True
)

# Use models for data validation
account: AccountDetails = client.get_account_details("123")
print(f"Account: {account.name}, Balance: {account.balances}")
```

## PSD2 Compliance

This module ensures PSD2 compliance by:

1. **Following Berlin Group Standards**: All models and enums are based on the official NextGenPSD2 Framework v1.3.14
2. **Complete Coverage**: Includes all AIS endpoints and data structures
3. **Type Safety**: Uses Pydantic for data validation and type checking
4. **Error Handling**: Comprehensive exception hierarchy for proper error handling
5. **Extensibility**: Abstract base classes allow for provider-specific implementations

## Integration with Existing Providers

The AIS core module is designed to work seamlessly with existing providers:

- **Isracard**: Can be updated to use AIS base classes
- **Max**: Can implement AIS interfaces
- **Cal**: Can implement AIS interfaces
- **Future Providers**: Can easily implement the standard interfaces

## Testing

The module includes comprehensive type hints and validation, making it easy to test:

```python
from core.ais import AccountDetails, Amount, BalanceList, Balance, BalanceType

# Create test data
amount = Amount(currency="EUR", amount="100.00")
balance = Balance(
    balance_amount=amount,
    balance_type=BalanceType.CLOSING_BOOKED
)
balance_list = BalanceList(balances=[balance])

# Pydantic validation ensures data integrity
account = AccountDetails(
    currency="EUR",
    balances=balance_list
)
```

## Contributing

When adding new providers or extending the AIS functionality:

1. **Follow PSD2 Standards**: Always refer to the Berlin Group specification
2. **Use Type Hints**: Maintain comprehensive type annotations
3. **Add Tests**: Include tests for new functionality
4. **Update Documentation**: Keep this README and docstrings current
5. **Validate Models**: Ensure all Pydantic models are properly validated

## References

- [Berlin Group NextGenPSD2 Framework v1.3.14](https://www.berlin-group.org/nextgenpsd2-downloads)
- [PSD2 Directive](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015L2366)
- [ISO 20022 Standards](https://www.iso20022.org/)
