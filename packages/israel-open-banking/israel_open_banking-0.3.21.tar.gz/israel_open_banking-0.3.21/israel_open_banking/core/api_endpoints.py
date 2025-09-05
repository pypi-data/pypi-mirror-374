# ──────────────────────────────
# CONSENTS
# ──────────────────────────────
CONSENTS_ENDPOINT = "consents"
CONSENT_BY_ID_ENDPOINT = "consents/{consent_id}"
CONSENT_STATUS_ENDPOINT = "consents/{consent_id}/status"

# ──────────────────────────────
# ACCOUNTS
# ──────────────────────────────
ACCOUNTS_ENDPOINT = "accounts"
ACCOUNT_BY_ID_ENDPOINT = "accounts/{account_id}"
ACCOUNT_BALANCES_ENDPOINT = "accounts/{account_id}/balances"
ACCOUNT_TRANSACTIONS_ENDPOINT = "accounts/{account_id}/transactions"
TRANSACTION_DETAILS_ENDPOINT = "accounts/{account_id}/transactions/{transaction_id}"

# ──────────────────────────────
# PAYMENTS
# ──────────────────────────────
PAYMENTS_ENDPOINT = "payments"
PAYMENT_BY_ID_ENDPOINT = "payments/{payment_product}/{payment_id}"
PAYMENT_STATUS_ENDPOINT = "payments/{payment_product}/{payment_id}/status"

# ────────────────────────────── Savings and Loans Accounts ─────────────────────────────

# ──────────────────────────────
# SAVING ACCOUNTS
# ──────────────────────────────
SAVINGS_ACCOUNTS_ENDPOINT = "savings"
SAVINGS_ACCOUNT_BY_ID_ENDPOINT = "savings/{savings_account_id}"
SAVINGS_ACCOUNT_BALANCES_ENDPOINT = "savings/{savings_account_id}/balances"
SAVINGS_ACCOUNT_TRANSACTIONS_ENDPOINT = "savings/{savings_account_id}/transactions"

# ──────────────────────────────
# LOAN ACCOUNTS
# ──────────────────────────────
LOAN_ACCOUNTS_ENDPOINT = "loans"
LOAN_ACCOUNT_BY_ID_ENDPOINT = "loans/{loan_account_id}"
LOAN_ACCOUNT_BALANCES_ENDPOINT = "loans/{loan_account_id}/balances"
LOAN_ACCOUNT_TRANSACTIONS_ENDPOINT = "loans/{loan_account_id}/transactions"


# ────────────────────────────── Single Cards ──────────────────────────────

# ──────────────────────────────
# CARDS
# ──────────────────────────────
SINGLE_CARDS_ENDPOINT = "cards"
SINGLE_CARD_BY_ID_ENDPOINT = "cards/{card_account_id}"
SINGLE_CARDS_BALANCES_ENDPOINT = "cards/{card_account_id}/balances"
SINGLE_CARDS_TRANSACTIONS_ENDPOINT = "cards/{card_account_id}/transactions"


# ────────────────────────────── Securities ──────────────────────────────
# ──────────────────────────────
# ACCOUNTS
# ──────────────────────────────
SECURITIES_ACCOUNTS_ENDPOINT = "securities-accounts"
SECURITIES_ACCOUNT_BY_ID_ENDPOINT = "securities-accounts/{securities_account_id}"
SECURITIES_ACCOUNT_POSITIONS_ENDPOINT = "securities-accounts/{securities_account_id}/positions"
SECURITIES_ACCOUNT_TRANSACTIONS_ENDPOINT = "securities-accounts/{securities_account_id}/transactions"
SECURITIES_ACCOUNTS_TRANSACTION_DETAILS_ENDPOINT = "securities-accounts/{securities_account_id}/transactions/{transaction_id}"
SECURITIES_ACCOUNT_ORDERS_ENDPOINT = "securities-accounts/{securities_account_id}/orders"
SECURITIES_ACCOUNTS_ORDER_DETAILS_ENDPOINT = "securities-accounts/{securities_account_id}/orders/{order_id}"
