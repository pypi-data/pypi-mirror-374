# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['horusdemodlib']

package_data = \
{'': ['*']}

install_requires = \
['crcmod>=1.7,<2.0',
 'numpy>=1.17,<2.0',
 'python-dateutil>=2.8,<3.0',
 'requests>=2.24.0,<3.0.0']

extras_require = \
{':python_version >= "3.13" and python_version < "4.0"': ['audioop-lts']}

setup_kwargs = {
    'name': 'horusdemodlib',
    'version': '0.4.0',
    'description': 'Project Horus HAB Telemetry Demodulators',
    'long_description': None,
    'author': 'Mark Jessop',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
