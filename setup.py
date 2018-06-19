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
    include_package_data=True,
    install_requires=[
        'Flask==0.10.1',
        'Jinja2==2.10',
        'Markdown==2.6.7',
        'PyYAML==3.11',
        'Werkzeug==0.14.1',
        'inflection==0.3.1',
        'six==1.11.0',
        'digitalmarketplace-utils>=30.0.0',
    ]
)
