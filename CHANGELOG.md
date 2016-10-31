# Digital Marketplace Content Loader changelog

Records breaking changes from major version bumps

## 2.0.0

PR: [#8](https://github.com/alphagov/digitalmarketplace-apiclient/pull/8)

### What changed

Before, all values in YAML files were stored as strings and then printed out
directly by jinja in the frontend apps.  Now, we're creating [TemplateField](https://github.com/alphagov/digitalmarketplace-content-loader/blob/474d9adce0f422700cbf2dfc8815a7503ab368bc/dmcontent/utils.py#L8)s
for specific attibutes of questions and sections.  TemplateFields are wrappers
around jinja [Templates](http://jinja.pocoo.org/docs/dev/api/#jinja2.Template) that are passed an initial string and then are rendered
with a context.
The result of all this is that we can pass variables to our content which
come from briefs or lots or service data or whatever else, either to be
printed as part of the content or evaluated as part of some logic operation.

These are the fields that are turned into TemplateFields when the YAML files are loaded:

| ContentSection                    | Question                                           |
|-----------------------------------|----------------------------------------------------|
| [`name`, `description`](https://github.com/alphagov/digitalmarketplace-content-loader/blob/474d9adce0f422700cbf2dfc8815a7503ab368bc/dmcontent/content_loader.py#L123) | [`question`, `name`, `question_advice`, `hint`](https://github.com/alphagov/digitalmarketplace-content-loader/blob/474d9adce0f422700cbf2dfc8815a7503ab368bc/dmcontent/questions.py#L10) |

[ContentTemplateError](https://github.com/alphagov/digitalmarketplace-content-loader/blob/474d9adce0f422700cbf2dfc8815a7503ab368bc/dmcontent/errors.py#L8)s are raised if a TemplateField is accessed (ie, [rendered](https://github.com/alphagov/digitalmarketplace-content-loader/blob/474d9adce0f422700cbf2dfc8815a7503ab368bc/dmcontent/content_loader.py#L166-L167)) without
the variables it needs.  Although we don't have a way to verify that every templated
field gets all of the variables it expects in every case (we would only know
this for sure in the view logic in the frontend apps), we have tests to make sure
HTML and jinja logic is escaped before it is presented to the user.

Nothing that is currently working will break with this update, so the example
below shows how a previously static field can now be given a variable.

### Example app change

#### Old
```yml
# digitalmarketplace-frameworks/frameworks/digital-outcomes-and-specialists/manifests/edit_brief_response.yml
name: Apply for this opportunity
```

```python
# digitalmarketplace-supplier-frontend/app/main/views/briefs.py
def create_brief_response(brief_id):
  section = manifest.get_section('apply').filter({})
  return render_template(section=section)
```

```jinja
<!-- digitalmarketplace-supplier-frontend/app/templates/briefs/brief_response.html -->
<h1>{{ section.name }}</h1>
```

```html
<!-- Output -->
<h1>Apply for this opportunity</h1>
```

#### New
```yml
# digitalmarketplace-frameworks/frameworks/digital-outcomes-and-specialists/manifests/edit_brief_response.yml
name: Apply for ‘{{ brief.title }}’
```

```python
# digitalmarketplace-supplier-frontend/app/main/views/briefs.py
def create_brief_response(brief_id):
  section = manifest.get_section('apply').filter({'brief': brief})
  return render_template(section=section)
```

```jinja
<!-- digitalmarketplace-supplier-frontend/app/templates/briefs/brief_response.html -->
<h1>{{ section.name }}</h1>
```

```html
<!-- Output -->
<h1>Apply for ‘Home Office IPT Programme Caseworking and DPM Delivery Partner’</h1>
```

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
