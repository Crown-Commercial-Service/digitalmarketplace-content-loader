# coding=utf-8

import yaml
import inflection
import re
import os
import copy

from typing import Optional

from collections import defaultdict, OrderedDict
from functools import partial
from werkzeug.datastructures import ImmutableMultiDict

from .errors import ContentNotFoundError, QuestionNotFoundError
from .questions import Question, ContentQuestion
from .messages import ContentMessage
from .metadata import ContentMetadata
from .utils import TemplateField, template_all, drop_followups


class ContentManifest(object):
    """An ordered set of sections each made up of one or more questions.

    Example::
        # Get hold of a section
        content = ContentManifest(sections)
        section = content.get_section(section_id)

        # Extract data from form data
        section.get_data(form_data)
    """
    def __init__(self, sections):
        self.sections = [ContentSection.create(section) for section in sections]
        self._assign_question_numbers()

    def _assign_question_numbers(self):
        question_index = 0
        for section in self.sections:
            for question in section.questions:
                question_index += 1
                question.number = question_index

    def __iter__(self):
        return self.sections.__iter__()

    def summary(self, service_data, inplace_allowed: bool = False) -> "ContentManifest":
        """Create a manifest instance for service summary display

        Return a new :class:`ContentManifest` instance with all
        questions replaced with :class:`ContentQuestionSummary`.

        :class:`ContentQuestionSummary` instances in addition to
        question data contain a reference to the service data
        dictionary and so have additional properties used by the
        summary tables.

        """
        new_sections = [section.summary(service_data, inplace_allowed=inplace_allowed) for section in self.sections]
        if inplace_allowed:
            self.sections[:] = new_sections
            self._assign_question_numbers()
            return self
        else:
            return ContentManifest(new_sections)

    def get_section(self, section_id):
        """Return a section by ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None

    def get_all_data(self, form_data):
        """Extract data for all sections from a submitted form

        :param form_data: the submitted form data
        :type form_data: :class:`werkzeug.ImmutableMultiDict`
        :return: parsed and filtered data

        See :func:`SectionContent.get_data` for more details.
        """
        all_data = {}
        for section in self.sections:
            all_data.update(section.get_data(form_data))
        return all_data

    def get_next_section_id(self, section_id=None, only_editable=False, only_edit_questions=False):
        previous_section_is_current = section_id is None

        for section in self.sections:
            if only_editable:
                if previous_section_is_current and section.editable:
                    return section.id
            elif only_edit_questions:
                if previous_section_is_current and section.edit_questions:
                    return section.id
            else:
                if previous_section_is_current:
                    return section.id

            if section.id == section_id:
                previous_section_is_current = True

        return None

    def get_next_editable_section_id(self, section_id=None):
        return self.get_next_section_id(section_id, only_editable=True)

    def get_next_edit_questions_section_id(self, section_id=None):
        return self.get_next_section_id(section_id, only_edit_questions=True)

    def filter(self, context, dynamic=True, inplace_allowed: bool = False) -> "ContentManifest":
        """Return a new :class:`ContentManifest` filtered by service data

        Only includes the questions that should be shown for the provided
        service data. This is calculated by resolving the dependencies
        described by the `depends` section."""
        new_sections = filter(None, [
            section.filter(context, dynamic=dynamic, inplace_allowed=inplace_allowed)
            for section in self.sections
        ])

        if inplace_allowed:
            self.sections[:] = new_sections
            self._assign_question_numbers()
            return self
        else:
            return ContentManifest(new_sections)

    def get_question(self, field_name):
        for section in self.sections:
            question = section.get_question(field_name)
            if question:
                return question

    def get_question_by_slug(self, question_slug):
        for section in self.sections:
            question = section.get_question_by_slug(question_slug)
            if question:
                return question


class ContentSection(object):
    TEMPLATE_FIELDS = ['name', 'description', 'summary_page_description']

    @classmethod
    def create(cls, section):
        if isinstance(section, ContentSection):
            return section.copy()
        else:
            return ContentSection(
                slug=section['slug'],
                name=section['name'],
                prefill=section.get('prefill'),
                editable=section.get('editable'),
                edit_questions=section.get('edit_questions'),
                questions=[ContentQuestion(question) for question in section.get('questions', [])],
                description=section.get('description'),
                summary_page_description=section.get('summary_page_description'),
                step=section.get('step'))

    def __init__(
            self,
            slug,
            name,
            prefill,
            editable,
            edit_questions,
            questions,
            description=None,
            summary_page_description=None,
            step=None,
            _context=None,
    ):
        self.id = slug  # TODO deprecated, use `.slug` instead
        self.slug = slug
        self.name = name
        self.prefill = prefill
        self.editable = editable
        self.edit_questions = edit_questions
        self.questions = questions
        self.description = description
        self.summary_page_description = summary_page_description
        self.step = step
        self._context = _context

    def __getattribute__(self, key):
        context = object.__getattribute__(self, '_context')
        field = object.__getattribute__(self, key)
        if isinstance(field, TemplateField):
            return field.render(context)
        else:
            return field

    def __getitem__(self, key):
        return getattr(self, key)

    def copy(self):
        return ContentSection(
            **{key: copy.copy(value)
               for key, value in object.__getattribute__(self, '__dict__').items()
               if key not in ['id']})

    def summary(self, service_data, inplace_allowed: bool = False) -> "ContentManifest":
        summary_section = self if inplace_allowed else self.copy()
        summary_section.questions = [
            question.summary(service_data, inplace_allowed=inplace_allowed) for question in summary_section.questions
        ]

        return summary_section

    def get_question_as_section(self, question_slug):
        question = self.get_question_by_slug(question_slug)
        if not question:
            return None

        return ContentSection(
            slug=question.slug,
            name=question.label,
            prefill=self.prefill,
            editable=self.edit_questions,
            edit_questions=False,
            questions=question.get('questions', [question]),
            description=question.get('hint') if question.get('questions') else '',
            _context=self._context
        )

    def get_field_names(self):
        """Return a list of field names that this section returns

        This list of field names corresponds to the keys of the data returned
        by :func:`ContentSection.get_data`.
        """
        return [
            form_field for question in self.questions for form_field in question.form_fields
        ]

    def get_question_ids(self, type=None):
        # FIXME should this ever return self.id?
        return [
            question_id for question in self.questions for question_id in question.get_question_ids(type)
        ]

    def get_next_question_id(self, question_id=None):
        """Return the next question id

        If no question_id provided will return the first question
        If last question_id provided will return `None`
        Will ignore any questions that are questions attributed to a multiquestion
        """
        return_next_questions_id = question_id is None

        for question in self.questions:
            if return_next_questions_id:
                return question.id

            if question.id == question_id:
                return_next_questions_id = True

        return None

    def get_previous_question_id(self, question_id):
        """Return the previous question id

        If first question_id provided will return `None`
        If question id does not exist in self.questions will return `None`
        Will ignore any questions that are questions attributed to a multiquestion
        """
        return_next_questions_id = False
        for question in reversed(self.questions):
            if return_next_questions_id:
                return question.id

            if question.id == question_id:
                return_next_questions_id = True

        return None

    def get_next_question_slug(self, question_slug=None):
        """Return the next question slug

        If no question_slug provided will return the first question
        If last question slug provided will return `None`
        Will ignore any questions that are questions attributed to a multiquestion
        """
        return_next_questions_slug = question_slug is None

        for question in self.questions:
            if return_next_questions_slug:
                return question.slug

            if question.slug == question_slug:
                return_next_questions_slug = True

        return None

    def get_previous_question_slug(self, question_slug):
        """Return the previous question slug

        If first question_slug provided will return `None`
        If question slug does not exist in self.questions will return `None`
        Will ignore any questions that are questions attributed to a multiquestion
        """
        return_next_questions_slug = False
        for question in reversed(self.questions):
            if return_next_questions_slug:
                return question.slug

            if question.slug == question_slug:
                return_next_questions_slug = True

        return None

    def get_data(self, form_data):
        """Extract data for a section from a submitted form

        :param form_data: the submitted form data
        :type form_data: :class:`werkzeug.ImmutableMultiDict`
        :return: parsed and filtered data

        This parses the provided form data against the expected fields for this
        section. Any fields provided in the form data that are not described
        in the section are dropped. Any fields in the section that are not
        in the form data are ignored. Fields in the form data are parsed according
        to their type in the section data.
        """
        # strip trailing and leading whitespace from form values
        form_data = ImmutableMultiDict((k, v.strip()) for k, v in form_data.items(multi=True))

        section_data = {}
        for question in self.questions:
            section_data.update(question.get_data(form_data))

        section_data = drop_followups(self, section_data)

        return section_data

    def has_changes_to_save(self, service, update_data):
        """Test whether an update includes changes to save

        :param service: the service that is to be updated
        :param update_data: the update that is going to be applied
        :return: whether there are changes that need saving

        If there are any keys in the update data that have different values
        the service data then a save is required.

        If there any questions in this section that are not yet present in
        the service data then a save is required (to generate the appropriate
        validation error from the API).
        """
        return any([
            any(service.get(key) != update_data[key] for key in update_data),
            any(form_field not in service for form_field in self.get_field_names())
        ])

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        """Convert API error keys into error messages

        :param errors: error dictionary as returned by the data API
        :return: error dictionary with human readable error messages
        """
        if set(errors.keys()) - set(self.get_field_names()):
            raise QuestionNotFoundError(errors.keys())

        errors_map = OrderedDict()
        for question in self.questions:
            errors_map.update(question.get_error_messages(errors, question_descriptor_from=question_descriptor_from))

        return errors_map

    @property
    def is_empty(self):
        return all(question.is_empty for question in self.questions)

    @staticmethod
    def unformat_assurance(key, data):
        return {
            key + '--assurance': data[key].get('assurance', None),
            key: data[key].get('value', None)
        }

    def unformat_data(self, data):
        """Method to process data into format for form, special assurance case or individual question level unformat.

        :param data: the service data as returned from the data API
        :type data: dict
        :return: service data with unpacked assurance

        Unpack fields from service JSON that have assurance information. In the
        data API response the field would be::

            {"field": {"assurance": "some assurance", "value": "some value"}}

        This then gets unpacked into two fields::

            {"field": "some value", "field--assurance": "some assurance"}
        """
        result = {}
        for key in data:
            if self._has_assurance(key):
                # If it's an assurance question do the unformatting here.
                result.update(self.unformat_assurance(key, data))
            else:
                question = self.get_question(key)
                if question:
                    # Otherwise if it is a legitimate question use the unformat method on the question.
                    result.update(question.unformat_data(data))
                else:
                    # Otherwise it's not a question, default to returning the k: v pair.
                    result[key] = data[key]
        return result

    def get_question(self, field_name):
        """Return a question dictionary by question ID"""

        for question in self.questions:
            field_question = question.get_question(field_name)
            if field_question:
                return field_question

    def get_question_by_slug(self, question_slug):
        for question in self.questions:
            if question.get('slug') == question_slug:
                return question

    def inject_brief_questions_into_boolean_list_question(self, brief):
        for question in self.questions:
            question.inject_brief_questions_into_boolean_list_question(brief)

    def filter(self, context, dynamic=True, inplace_allowed: bool = False) -> Optional["ContentSection"]:
        section = self if inplace_allowed else self.copy()
        section._context = context

        filtered_questions = list(filter(None, [
            question.filter(context, dynamic=dynamic, inplace_allowed=inplace_allowed)
            for question in self.questions
        ]))

        section.questions = filtered_questions

        if not filtered_questions:
            return None

        return section

    # Type checking

    def _has_assurance(self, key):
        """Return True if a question has an assurance component"""
        question = self.get_question(key)
        return bool(question) and question.has_assurance()

    @property
    def has_summary_page(self):
        return len(self.questions) > 1 or self.description is not None


class ContentLoader(object):
    """Load the frameworks content files

    Usage:
    >>> loader = ContentLoader('path/to/digitalmarketplace-frameworks')
    >>> # pre-load manifests
    >>> loader.load_manifest('framework-1', 'question-set-1', 'manifest-1')
    >>> loader.load_manifest('framework-1', 'question-set-1', 'manifest-2')
    >>> loader.load_manifest('framework-1', 'question-set-2', 'manifest-3')
    >>> loader.load_manifest('framework-2', 'question-set-1', 'manifest-1')
    >>>
    >>> # preload messages
    >>> loader.load_messages('framework-1', ['homepage_sidebar', 'dashboard'])
    >>>
    >>> # preload metadata
    >>> loader.load_metadata('framework-1', ['copy_services'])
    >>>
    >>> # get a manifest
    >>> loader.get_manifest('framework-1', 'manifest-1')
    >>>
    >>> # get a message
    >>> loader.get_message('framework-1', 'homepage_sidebar', 'in_review')
    >>>
    >>> # get some metadata
    >>> loader.get_message('framework-1', 'copy_services', 'source_framework')

    """
    def __init__(self, content_path):
        self.content_path = content_path
        self._content = defaultdict(dict)
        self._messages = defaultdict(dict)
        self._metadata = defaultdict(dict)

        # A defaultdict that defaults to a defaultdict of dicts
        self._questions = defaultdict(partial(defaultdict, dict))

    def get_manifest(self, framework_slug, manifest):
        try:
            manifest = self._content[framework_slug][manifest]
        except KeyError:
            raise ContentNotFoundError("Content not found for {} and {}".format(framework_slug, manifest))

        return ContentManifest(manifest)

    get_builder = get_manifest  # TODO remove once apps have switched to .get_manifest

    def load_manifest(self, framework_slug, question_set, manifest):
        if manifest in self._content[framework_slug]:
            return

        try:
            manifest_path = os.path.join(self._root_path(framework_slug), 'manifests', '{}.yml'.format(manifest))
            manifest_sections = read_yaml(manifest_path)
        except IOError:
            raise ContentNotFoundError("No manifest at {}".format(manifest_path))

        self._content[framework_slug][manifest] = [
            self._process_section(framework_slug, question_set, section) for section in manifest_sections
        ]

        return self._content[framework_slug][manifest]

    def _process_section(self, framework_slug, question_set, section):
        section = self._load_nested_questions(framework_slug, question_set, section)

        for field in ContentSection.TEMPLATE_FIELDS:
            if field in section:
                section[field] = TemplateField(section[field])

        return section

    def get_question(self, framework_slug, question_set, question):
        if question in self._questions.get(framework_slug, {}).get(question_set, {}):
            return self._questions[framework_slug][question_set][question].copy()

        try:
            questions_path = self._questions_path(framework_slug, question_set)
            question_data = self._load_nested_questions(
                framework_slug, question_set,
                _load_question(question, questions_path)
            )
        except IOError:
            raise ContentNotFoundError("No question {} at {}".format(question, questions_path))

        for field in Question.TEMPLATE_FIELDS:
            if field in question_data:
                question_data[field] = TemplateField(question_data[field])

        for field in Question.MARKDOWN_FIELDS:
            if field in question_data:
                question_data[field] = TemplateField(question_data[field], markdown=True)

        """
        We want to support TemplateFields as keys of list items, for example:
        - {options: [{description: '{{ "jinja" }}'}]} in the lot question
        - {validations: [{message: '{{ "jinja" }}'}]} in some declaration questions
        """
        for field, subfield in Question.TEMPLATE_OPTIONS_FIELDS:
            if field in question_data:
                for i, option in enumerate(question_data[field]):
                    if subfield in option:
                        question_data[field][i][subfield] = TemplateField(question_data[field][i][subfield])

        self._questions[framework_slug][question_set][question] = question_data

        return self._questions[framework_slug][question_set][question].copy()

    def get_message(self, framework_slug, block, key=None):
        """
        `block` corresponds to
          - a file in the frameworks directory
          - the place where the message will be used, eg homepage sidebar, lot page

        `key` and `sub_key` are used to look up a specific message, for example a message might depend on:
          - the status of a framework
          - the status of a supplier’s application to a framework
          - the context in which the message will be displayed
        """
        if block not in self._messages[framework_slug]:
            raise ContentNotFoundError(
                "Message file at {} not loaded".format(self._message_path(framework_slug, block))
            )

        message = ContentMessage(self._messages[framework_slug][block])

        if key is None:
            return message
        else:
            return message.get(key, None)

    def load_messages(self, framework_slug, blocks):
        if not isinstance(blocks, list):
            raise TypeError('Content blocks must be a list')

        for block in blocks:
            try:
                self._messages[framework_slug][block] = self._load_message(framework_slug, block)
            except IOError:
                raise ContentNotFoundError(
                    "No message file at {}".format(self._message_path(framework_slug, block))
                )

    def _load_message(self, framework_slug, message_name):
        return template_all(read_yaml(self._message_path(framework_slug, message_name)))

    def get_metadata(self, framework_slug, block, key=None):
        """
        `block` corresponds to
          - a file in the frameworks directory

        `key` and `sub_key` are used to look up a specific metadata:
          - the framework which services can be copied from
        """
        if block not in self._metadata[framework_slug]:
            raise ContentNotFoundError(
                "Message file at {} not loaded".format(self._metadata_path(framework_slug, block))
            )

        metadata = ContentMetadata(self._metadata[framework_slug][block])

        if key is None:
            return metadata
        else:
            return metadata.get(key, None)

    def load_metadata(self, framework_slug, blocks):
        if not isinstance(blocks, list):
            raise TypeError('Content blocks must be a list')

        for block in blocks:
            try:
                self._metadata[framework_slug][block] = self._load_metadata(framework_slug, block)
            except IOError:
                raise ContentNotFoundError(
                    "No metadata file at {}".format(self._metadata_path(framework_slug, block))
                )

    def _load_metadata(self, framework_slug, metadata_name):
        return read_yaml(self._metadata_path(framework_slug, metadata_name))

    def _root_path(self, framework_slug):
        return os.path.join(self.content_path, 'frameworks', framework_slug)

    def _questions_path(self, framework_slug, question_set):
        return os.path.join(self._root_path(framework_slug), 'questions', question_set)

    def _message_path(self, framework_slug, message):
        return os.path.join(self._root_path(framework_slug), 'messages', '{}.yml'.format(message))

    def _metadata_path(self, framework_slug, metadata):
        return os.path.join(self._root_path(framework_slug), 'metadata', '{}.yml'.format(metadata))

    def _load_nested_questions(self, framework_slug, question_set, section_or_question):
        if 'questions' in section_or_question:
            section_or_question['questions'] = [
                self.get_question(framework_slug, question_set, question)
                for question in section_or_question['questions']
            ]
            if not section_or_question.get('slug'):
                section_or_question['slug'] = _make_slug(section_or_question['name'])

        else:
            if not section_or_question.get('slug'):
                section_or_question['slug'] = _make_slug(section_or_question['id'])

        return section_or_question


def _load_question(question, directory):
    question_content = read_yaml(
        os.path.join(directory, '{}.yml'.format(question))
    )

    question_content["id"] = question_content.get("id", question)

    return question_content


def _make_slug(name):
    return inflection.underscore(
        re.sub(r"[^\w]+", "_", name, flags=re.UNICODE).strip("_")
    ).replace('_', '-')


def read_yaml(yaml_file):
    with open(yaml_file, "r") as file:
        return yaml.safe_load(file)
