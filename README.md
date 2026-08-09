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
git clone https://github.com/ChocoTonic/empower_personal_capital.git
cd empower_personal_capital
```

Install dependencies and the package:

```bash
pip install .
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

You can avoid having to enter 2FA every time by storing your session. The
session file contains authentication cookies, so keep it private and never
commit it:

```python
pc.save_session("session.json")

# Later...
pc.load_session("session.json")
```

Session files use versioned JSON and include both the cookies and CSRF token.
New files are created with owner-only permissions on platforms that support
POSIX file modes.

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

Absolutely. Here’s a clear section you can add to your README that explains the `.env` file usage and lists the required variables.

## Environment Variables and the .env File

You can define your credentials in a `.env` file at the root of your project to avoid entering your email and password every time you run the script. The package will automatically load these using [`python-dotenv`](https://pypi.org/project/python-dotenv/).

Create a file named `.env` and add your credentials:

```
PEW_EMAIL=your_email@example.com
PEW_PASSWORD=your_password
```

`.env.example` is included as a template. Never commit your real `.env` file with credentials to version control.

If these variables are set, the script will use them and will not prompt for your email or password.

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
