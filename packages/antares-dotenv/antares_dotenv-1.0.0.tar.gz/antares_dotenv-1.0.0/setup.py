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
    'version': '1.0.0',
    'description': 'A minimal utility to load environment variables with automatic type casting.',
    'long_description': '# My Dotenv\n\nA minimal utility to load environment variables with automatic type casting (bool, list, int, float, JSON).\n\n__For personnal use__',
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
