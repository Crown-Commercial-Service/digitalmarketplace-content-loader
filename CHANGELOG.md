# Digital Marketplace Content Loader changelog

Records breaking changes from major version bumps

## 1.0.0

PR: [#1](https://github.com/alphagov/digitalmarketplace-apiclient/pull/1)

### What changed

Extracted content_loader from dmutils to this package. The package name is now dmcontent
instead of dmutis.content_loader.

Converters for strings to booleans and numbers were copied from utils as dmcontent
is dependent on them. format_price and format_service_price were moved from
utils to dmcontent. Imports of format_service_price will need to be updated to import
from the new package name (eg 'from dmcontent.content_loader').

### Example app change

Old
```
from dmutils.content_loader import ContentSection
```

New
```
from dmcontent.content_loader import ContentSection
```
