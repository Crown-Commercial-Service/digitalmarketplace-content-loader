Digital Marketplace Content Loader
==================================

[![Coverage Status](https://coveralls.io/repos/alphagov/digitalmarketplace-content-loader/badge.svg?branch=master&service=github)](https://coveralls.io/github/alphagov/digitalmarketplace-content-loader?branch=master)
![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)


## What's in here?

Content loader for Digital Marketplace.

Originally was part of [Digital Marketplace Utils](https://github.com/alphagov/digitalmarketplace-utils).


## Running the tests

Install Python dependencies

```
make requirements-dev
```

Run the tests

```
make test
```


## Releasing a new version

To update the package version, edit the `__version__ = ...` string in `dmcontent/__init__.py`,
commit and push the change and wait for CI to create a new version tag.

Once the tag is available on GitHub, the new version can be used by the apps by adding the following
line to the app `requirements.txt` (replacing `X.Y.Z` with the current version number):

```
git+https://github.com/alphagov/digitalmarketplace-content-loader.git@X.Y.Z#egg=digitalmarketplace-content-loader==X.Y.Z
```

When changing a major version number consider adding a record to the `CHANGELOG.md` with a
description of the change and an example of the upgrade process for the client apps.
