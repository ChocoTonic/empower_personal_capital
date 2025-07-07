# Empower Personal Capital

A modern Python library for accessing your Personal Capital (Empower) data, with built-in support for session persistence, two-factor authentication, and convenient account and transaction retrieval.

## Features

- Simple login: Email/password authentication
- Two-factor authentication: SMS and email support
- Session persistence: Avoids 2FA every run
- Fetch financial data: Account details, transactions, net worth
- Easy automation: Ideal for scripts and data analysis

## Installation

### With pip

```bash
pip install empower_personal_capital
```

### From Source

Clone the repo:

```bash
git clone https://github.com/ChocoTonic/personalcapital-py.git
cd personalcapital-py
```

Install dependencies and the package:

```bash
pip install -r requirements.txt
python setup.py install
```

## Usage

### Quick Example

```python
from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum

pc = PersonalCapital()
email, password = "you@example.com", "your_password"

try:
    pc.login(email, password)
except RequireTwoFactorException:
    pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
    code = input("Enter 2FA code: ")
    pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, code)
    pc.authenticate_password(password)

accounts_response = pc.fetch('/newaccount/getAccounts')
accounts = accounts_response.json()['spData']
print('Net worth:', accounts['networth'])
```

### Session Persistence

You can avoid having to enter 2FA every time by storing your session:

```python
session = pc.get_session()
# Save session to a file

# Later...
pc.set_session(session)
```

See `main.py` for a complete script with persistent sessions.

### Running the Example Script

The included [`main.py`](main.py) script provides a full working example with session saving/loading.

To run:

```bash
python main.py
```

You can also set environment variables to avoid entering your email and password each time:

```bash
PEW_EMAIL="you@example.com" PEW_PASSWORD="your_password" python main.py
```

If you do not set environment variables, the script will prompt for your credentials.

### Fetching Transactions

You can fetch transactions by making an API call. For example, to get transactions from the past 90 days (as shown in `main.py`):

```python
from datetime import datetime, timedelta

now = datetime.now()
start_date = (now - timedelta(days=91)).strftime('%Y-%m-%d')
end_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')

transactions_response = pc.fetch(
    '/transaction/getUserTransactions',
    {
        "sort_cols": "transactionTime",
        "sort_rev": "true",
        "page": "0",
        "rows_per_page": "100",
        "startDate": start_date,
        "endDate": end_date,
        "component": "DATAGRID",
    },
)
transactions = transactions_response.json()['spData']['transactions']
print(f"Found {len(transactions)} transactions")
```

## Advanced Usage

- Handling two-factor via Email:
  Replace `TwoFactorVerificationModeEnum.SMS` with `TwoFactorVerificationModeEnum.EMAIL` in the challenge and authenticate methods.

- Other API endpoints:
  You can inspect your browser’s network requests while using Personal Capital, or refer to the code and experiment with additional endpoints using `pc.fetch(endpoint, data)`.
