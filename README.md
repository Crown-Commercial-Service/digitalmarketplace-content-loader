Digital Marketplace Content Loader
==================================

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)


## What's in here?

Content loader for Digital Marketplace.

Originally was part of [Digital Marketplace Utils](https://github.com/alphagov/digitalmarketplace-utils).


## Running the tests

Install Python dependencies

```
make bootstrap
invoke requirements-dev
```

Run the tests

```
invoke test
```


## Releasing a new version

To update the package version, edit the `__version__ = ...` string in `dmcontent/__init__.py`,
once merged the new version will be released and published to [PyPI](https://pypi.org/project/digitalmarketplace-content-loader/) by [Github Actions](./.github/workflows).

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
