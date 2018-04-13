import pytest

from dmcontent.metadata import ContentMetadata
from dmcontent.utils import TemplateField


class TestContentMetadata(object):
    def test_content_metadata_getattr(self):
        metadata = ContentMetadata({'name': "Name"})

        assert metadata.name == 'Name'

    def test_content_metadata_getattr_raises_attribute_error_if_missing(self):
        metadata = ContentMetadata({'name': "Name"})

        with pytest.raises(AttributeError):
            assert metadata.foo == 'missing'

    def test_get_missing_field(self):
        metadata = ContentMetadata({})

        assert metadata.get('key', 'default') == 'default'

    def test_metadata_eq(self):
        metadata = ContentMetadata({"name": "value"})

        assert metadata == ContentMetadata({"name": "value"})
        assert metadata != {"name": "value"}

    def test_metadata_get_item(self):
        metadata = ContentMetadata({"name": "value"})

        assert metadata['name'] == 'value'

    def test_metadata_repr(self):
        metadata = ContentMetadata({"name": "value"})

        assert metadata.__repr__() == "<ContentMetadata: data={'name': 'value'}>"

    def test_content_metadata_does_not_render_template_fields(self):
        metadata = ContentMetadata({'name': TemplateField("Field {{ name }}")})

        assert metadata.name == TemplateField('Field {{ name }}')

    def test_content_metadata_dict_field_returns_content_metadata(self):
        metadata = ContentMetadata({'nested': {'name': 'Name'}})

        assert isinstance(metadata.nested, ContentMetadata)
        assert metadata.nested.name == 'Name'

    def test_content_metadata_list_field_does_not_render_template_fields(self):
        metadata = ContentMetadata({'nested': [TemplateField('Name'), TemplateField('{{ name }}')]})

        assert metadata.nested == [TemplateField('Name'), TemplateField('{{ name }}')]
