# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['antares_dotenv']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'antares-dotenv',
    'version': '1.0.1',
    'description': 'A minimal utility to load environment variables with automatic type casting.',
    'long_description': '# Antares-Dotenv\n\nA minimalistic and developer-friendly way to handle environment variables in Python. Just import `env` and start using it. No more boilerplate code for loading and parsing.\n\n## Installation\n\n```bash\npip install antares-dotenv\n```\n\n## Usage\n\nCreate a `.env` file in your project root:\n\n```\n# .env\n\n# Strings\nAPP_NAME=My Awesome App\n\n# Integers\nPORT=8000\n\n# Booleans\nDEBUG=True\n\n# Lists (comma-separated)\nALLOWED_HOSTS=localhost,127.0.0.1\n\n# JSON\nDATABASE_CONFIG={"user": "admin", "password": "secret"}\n```\n\nNow you can access these variables in your Python code:\n\n```python\n# main.py\n\nfrom antares_dotenv import env\n\n# String\napp_name = env("APP_NAME", default="My App")\nprint(f"App Name: {app_name}")\n\n# Integer (auto-parsed)\nport = env("PORT")\nprint(f"Port: {port} (type: {type(port).__name__})")\n\n# Boolean (auto-parsed)\ndebug_mode = env("DEBUG")\nprint(f"Debug Mode: {debug_mode} (type: {type(debug_mode).__name__})")\n\n# List (auto-parsed)\nallowed_hosts = env("ALLOWED_HOSTS")\nprint(f"Allowed Hosts: {allowed_hosts} (type: {type(allowed_hosts).__name__})")\n\n# JSON (auto-parsed to dict)\ndb_config = env("DATABASE_CONFIG")\nprint(f"Database User: {db_config[\'user\']}")\n\n# Using a default value for a missing key\nsecret_key = env("SECRET_KEY", default="a-very-secret-key")\nprint(f"Secret Key: {secret_key}")\n```\n\n## Why Antares-Dotenv?\n\n`antares-dotenv` is designed to reduce boilerplate and simplify your code.\n\n**Before (with `python-dotenv` and `os`):**\n\n```python\nimport os\nfrom dotenv import load_dotenv\n\nload_dotenv()\n\nport = int(os.getenv("PORT"))\ndebug = os.getenv("DEBUG").lower() == \'true\'\nhosts = os.getenv("ALLOWED_HOSTS").split(\',\')\n```\n\n**After (with `antares-dotenv`):**\n\n```python\nfrom antares_dotenv import env\n\nport = env("PORT")\ndebug = env("DEBUG")\nhosts = env("ALLOWED_HOSTS")\n```\n\n`antares-dotenv` automatically handles the type casting for you, making your code cleaner and more readable.\n\n\n*-- For personnal purposes*',
    'author': 'Antares Mugisho',
    'author_email': 'antaresmugisho@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
