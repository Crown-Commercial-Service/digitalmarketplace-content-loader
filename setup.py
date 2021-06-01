import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('dmcontent/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='digitalmarketplace-content-loader',
    version=version,
    url='https://github.com/alphagov/digitalmarketplace-content-loader',
    license='MIT',
    author='GDS Developers',
    description='Digital Marketplace Content Loader',
    long_description=__doc__,
    packages=find_packages(),
    package_data={'dmcontent': ['py.typed']},
    include_package_data=True,
    install_requires=[
        'Flask~=1.0',
        'Jinja2~=2.10',
        'Markdown<4.0.0,>=2.6.7',
        'PyYAML<6.0,>=5.1.2',
        'inflection<1.0.0,>=0.3.1',
        'digitalmarketplace-utils>=59.0.0',
    ],
    python_requires="~=3.6",
)
