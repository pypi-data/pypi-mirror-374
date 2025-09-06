# Antares-Dotenv

A minimalistic and developer-friendly way to handle environment variables in Python. Just import `env` and start using it. No more boilerplate code for loading and parsing.

## Installation

```bash
pip install antares-dotenv
```

## Usage

Create a `.env` file in your project root:

```
# .env

# Strings
APP_NAME=My Awesome App

# Integers
PORT=8000

# Booleans
DEBUG=True

# Lists (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1

# JSON
DATABASE_CONFIG={"user": "admin", "password": "secret"}
```

Now you can access these variables in your Python code:

```python
# main.py

from antares_dotenv import env

# String
app_name = env("APP_NAME", default="My App")
print(f"App Name: {app_name}")

# Integer (auto-parsed)
port = env("PORT")
print(f"Port: {port} (type: {type(port).__name__})")

# Boolean (auto-parsed)
debug_mode = env("DEBUG")
print(f"Debug Mode: {debug_mode} (type: {type(debug_mode).__name__})")

# List (auto-parsed)
allowed_hosts = env("ALLOWED_HOSTS")
print(f"Allowed Hosts: {allowed_hosts} (type: {type(allowed_hosts).__name__})")

# JSON (auto-parsed to dict)
db_config = env("DATABASE_CONFIG")
print(f"Database User: {db_config['user']}")

# Using a default value for a missing key
secret_key = env("SECRET_KEY", default="a-very-secret-key")
print(f"Secret Key: {secret_key}")
```

## Why Antares-Dotenv?

`antares-dotenv` is designed to reduce boilerplate and simplify your code.

**Before (with `python-dotenv` and `os`):**

```python
import os
from dotenv import load_dotenv

load_dotenv()

port = int(os.getenv("PORT"))
debug = os.getenv("DEBUG").lower() == 'true'
hosts = os.getenv("ALLOWED_HOSTS").split(',')
```

**After (with `antares-dotenv`):**

```python
from antares_dotenv import env

port = env("PORT")
debug = env("DEBUG")
hosts = env("ALLOWED_HOSTS")
```

`antares-dotenv` automatically handles the type casting for you, making your code cleaner and more readable.


*-- For personnal purposes*