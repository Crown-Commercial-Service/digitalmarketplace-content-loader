import pytest

from dmcontent.messages import ContentMessage
from dmcontent.utils import TemplateField
from dmcontent import ContentTemplateError


class TestContentMessage(object):
    def test_content_message_field(self):
        message = ContentMessage({'name': "Name"})

        assert message.name == 'Name'

    def test_get_missing_field(self):
        message = ContentMessage({})

        assert message.get('key', 'default') == 'default'

    def test_message_eq(self):
        message = ContentMessage({"name": "value"})

        assert message == ContentMessage({"name": "value"})
        assert not (message == {"name": "value"})

    def test_message_get_item(self):
        message = ContentMessage({"name": "value"})

        assert message['name'] == 'value'

    def test_message_repr(self):
        message = ContentMessage({"name": "value"})

        assert message.__repr__()

    def test_content_message_template_field(self):
        message = ContentMessage({'name': TemplateField("Name")})

        assert message.name == 'Name'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_content_message_template_field_with_context(self, filter_inplace_allowed):
        message = ContentMessage({'name': TemplateField("Field {{ name }}")})

        with pytest.raises(ContentTemplateError):
            assert message.name

        assert message.filter({'name': 'one'}, inplace_allowed=filter_inplace_allowed).name == 'Field one'

    def test_content_message_dict_field_returns_content_message(self):
        message = ContentMessage({'nested': {'name': TemplateField('Name')}})

        assert isinstance(message.nested, ContentMessage)
        assert message.nested.name == 'Name'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_content_message_list_field_returns_rendered_fields(self, filter_inplace_allowed):
        message = ContentMessage({'nested': [TemplateField('Name'), TemplateField('{{ name }}')]})

        assert message.filter({'name': 'Other'}, inplace_allowed=filter_inplace_allowed).nested == ['Name', 'Other']

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_content_message_list_field_returns_content_messages(self, filter_inplace_allowed):
        message = ContentMessage({'nested': [{'name': 'Name'}, {'name': TemplateField('{{ name }}')}]})

        nested = message.filter({'name': 'Other'}, inplace_allowed=filter_inplace_allowed).nested
        assert nested == [
            ContentMessage({'name': 'Name'}, {'name': 'Other'}),
            ContentMessage({'name': TemplateField('{{ name }}')}, {'name': 'Other'})
        ]
        assert nested[1].name == 'Other'

    @pytest.mark.parametrize("filter_inplace_allowed", (False, True,))
    def test_nested_content_message_preserves_context(self, filter_inplace_allowed):
        message = ContentMessage({'nested': {'name': TemplateField('Nested {{ name }}')}})

        assert message.filter(
            {'name': "message"},
            inplace_allowed=filter_inplace_allowed,
        ).nested.name == 'Nested message'
