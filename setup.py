import os
import json
from setuptools import setup

PROJECT_DIR = "bgpip_tools"

with open(os.path.join(os.path.dirname(__file__), PROJECT_DIR, 'project.json')) as f:
    pcfg = json.load(f)

pcfg = pcfg['global']['project']

with open('requirements.txt') as f:
    requires = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(
    name=pcfg['name'],
    version=pcfg['version'],
    description=pcfg['description'],
    long_description=readme,
    author=pcfg['author'],
    author_email=pcfg['email'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bgpip-tools = bgpip_tools.__main__:cli",
        ],
    },
    install_requires=requires,
)
