Digital Marketplace Content Loader
==================================

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

## Licence

Unless stated otherwise, the codebase is released under [the MIT License][mit].
This covers both the codebase and any sample code in the documentation.

The documentation is [&copy; Crown copyright][copyright] and available under the terms
of the [Open Government 3.0][ogl] licence.

[mit]: LICENCE
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
