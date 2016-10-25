from dmcontent.questions import Question
from dmcontent.content_loader import ContentSection


class TestFilterContentSection(object):
    def test_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name='Section',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).name == 'Section'

    def test_question_fields_without_template_tags_are_unchanged(self):
        section = ContentSection(
            slug='section',
            name='Section',
            editable=False,
            edit_questions=False,
            questions=[Question({'name': 'Question'})]
        )

        assert section.filter({}).questions[0].name == 'Question'

    def test_not_all_fields_are_templated(self):
        section = ContentSection(
            slug='# {{ section }}',
            name='Section',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({}).slug == '# {{ section }}'

    def test_section_name_is_templated(self):
        section = ContentSection(
            slug='section',
            name='Section {{ name }}',
            editable=False,
            edit_questions=False,
            questions=[Question({})]
        )

        assert section.filter({'name': 'one'}).name == 'Section one'

    def test_section_description_is_templated(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description="This is the {{ name }} section"
        )

        assert section.filter({'name': 'first'}).description == 'This is the first section'

    def test_section_description_is_not_set(self):
        section = ContentSection(
            slug='section',
            name='Section one',
            editable=False,
            edit_questions=False,
            questions=[Question({})],
            description=None
        )

        assert section.filter({}).description == None
