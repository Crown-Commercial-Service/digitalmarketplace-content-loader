from collections import OrderedDict

from .converters import convert_to_boolean, convert_to_number
from .errors import ContentNotFoundError
from .formats import format_price


class Question(object):
    def __init__(self, data, number=None):
        self.number = number
        self._data = data.copy()

        if 'questions' in data:
            self.questions = [
                question if isinstance(question, ContentQuestion) else ContentQuestion(question)
                for question in data['questions']
            ]
        else:
            self.questions = None

        if 'fields' in data:
            self.fields = data['fields']
        else:
            self.fields = {}

    def summary(self, service_data):
        return ContentQuestionSummary(
            self, service_data
        )

    def get_question(self, field_name):
        if field_name in self.fields.values():
            return self
        if self.id == field_name:
            return self
        elif self.questions:
            return next(
                (question for question in self.questions if question.id == field_name),
                None
            )

    def get_data(self, form_data):
        if self.fields:
            return {
                key: form_data[key] if form_data[key] else None
                for key in self.fields.values()
                if key in form_data
            }
        elif self.questions:
            questions_data = {}
            for question in self.questions:
                questions_data.update(question.get_data(form_data))
            return questions_data
        else:
            return self._get_single_question_data(form_data)

    def _get_single_question_data(self, form_data):
        if self.id not in form_data and self.type != 'boolean_list':
            if self.get('assuranceApproach'):
                if '{}--assurance'.format(self.id) in form_data:
                    return {self.id: {'assurance': form_data.get('{}--assurance'.format(self.id))}}
                else:
                    return {self.id: {}}
            elif self.type in ['list', 'checkboxes']:
                return {self.id: None}
            else:
                return {}

        if self.type in ['list', 'checkboxes']:
            value = form_data.getlist(self.id)
        elif self.type == 'boolean_list':

            # if self.id is 'q5', form keys will come back as ('q5-0', 'true'), ('q5-1', 'false'), ('q5-3', 'true'), ...
            # here, we build a dict with keys as indices and values converted to boolean, eg {0: True, 1: False, 3: True, ...}  # noqa
            boolean_indices_and_values = {
                int(k.split('-')[-1]): convert_to_boolean(v) for k, v in form_data.items()
                if k.startswith("{}-".format(self.id)) and
                k.split('-')[-1].isdigit()
            }

            if not len(boolean_indices_and_values):
                return {}

            value = [None] * (max(boolean_indices_and_values.keys()) + 1)
            for k, v in boolean_indices_and_values.items():
                value[k] = v

        elif self.type == 'boolean':
            value = convert_to_boolean(form_data[self.id])
        elif self.type == 'number':
            value = convert_to_number(form_data[self.id])
        elif self.type != 'upload':
            value = form_data[self.id]
        else:
            return {}

        if self.get('assuranceApproach'):
            value = {"value": value}
            if form_data.get(self.id + '--assurance'):
                value["assurance"] = form_data.get(self.id + '--assurance')

        if self.type not in ['boolean', 'number']:
            value = value if value else None

        return {self.id: value}

    def get_error_messages(self, errors):
        error_fields = set(errors.keys()) & set(self.form_fields)
        if not error_fields:
            return {}

        question_errors = {}
        for field_name in sorted(error_fields):
            question = self.get_question(field_name)
            message_key = errors[field_name]

            validation_message = question.get_error_message(message_key, field_name)

            error_key = question.id
            if message_key == 'assurance_required':
                error_key = '{}--assurance'.format(error_key)

            question_errors[error_key] = {
                'input_name': error_key,
                'question': question.label,
                'message': validation_message,
            }

        return question_errors

    def get_error_message(self, message_key, field_name=None):
        """Return a single error message.

        :param message_key: error message key as returned by the data API
        :param field_name:
        """
        if field_name is None:
            field_name = self.id
        for validation in self.get_question(field_name).get('validations', []):
            if validation['name'] == message_key:
                if validation.get('field', field_name) == field_name:
                    return validation['message']
        return 'There was a problem with the answer to this question'

    @property
    def label(self):
        return self.get('name') or self.question

    @property
    def form_fields(self):
        if self.fields:
            return sorted(self.fields.values())
        elif self.questions:
            return [form_field for question in self.questions for form_field in question.form_fields]
        else:
            # pricing fields should have fields.
            # throw an assertion error if they don't.
            # TODO: maybe we can check this elsewhere?
            assert self.type != "pricing"
            return [self.id]

    @property
    def required_form_fields(self):
        return list(set(self.form_fields) - set(self._optional_form_fields))

    @property
    def _optional_form_fields(self):
        if self.get('optional'):
            return self.form_fields
        elif self.get('optional_fields'):
            return [self.fields[key] for key in self['optional_fields']]
        elif self.questions:
            return [form_field for question in self.questions for form_field in question._optional_form_fields]
        else:
            return []

    def inject_brief_questions_into_boolean_list_question(self, brief):
        if self.type == 'boolean_list':
            if self.id not in brief.keys() and not self.get('optional'):
                raise ContentNotFoundError("No {} found for brief {}".format(self.id, brief['id']))

            # briefs might not have optional boolean_list questions
            self.boolean_list_questions = brief.get(self.id, [])

    def has_assurance(self):
        return True if self.get('assuranceApproach') else False

    def get_question_ids(self, type=None):
        if self.questions:
            return [question.id for question in self.questions if type in [question.type, None]]
        else:
            return [self.id] if type in [self.type, None] else []

    def get(self, key, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return '<{0.__class__.__name__}: number={0.number}, data={0._data}>'.format(self)


class ContentQuestionSummary(Question):
    def __init__(self, question, service_data):
        self.number = question.number
        self._data = question._data
        self._service_data = service_data

        self.questions = question.questions
        if self.questions:
            self.questions = [q.summary(service_data) for q in self.questions]
        self.fields = question.fields

        if question.get('boolean_list_questions'):
            self.boolean_list_questions = question.boolean_list_questions

    def _default_for_field(self, field_key):
        return self.get('field_defaults', {}).get(field_key)

    def get_error_messages(self, errors):

        question_errors = super(ContentQuestionSummary, self).get_error_messages(errors)

        boolean_list_questions = self.get('boolean_list_questions')
        boolean_list_values = self.get('value') or []

        if self.id in question_errors and self.type == 'boolean_list' and boolean_list_questions:
            # pad list of values to same length as boolean_list_questions
            boolean_list_values.extend([None] * (len(boolean_list_questions) - len(boolean_list_values)))

            for index, boolean_list_question in enumerate(boolean_list_questions):
                if not isinstance(boolean_list_values[index], bool):
                    # Each non-boolean value is an error
                    boolean_question_id = "{}-{}".format(self.id, index)
                    question_errors[boolean_question_id] = {
                        'input_name': boolean_question_id,
                        'message': question_errors[self.id]['message'],
                        'question': boolean_list_question
                    }

            question_errors[self.id] = True
            question_errors = OrderedDict([
                (k, question_errors[k]) for k in sorted(question_errors.keys())
            ])

        return question_errors

    @property
    def is_empty(self):
        return self.value in ['', [], None]

    @property
    def value(self):
        if self.questions:
            return [question for question in self.questions if not question.is_empty]
        if self.type == "pricing":
            price = self._service_data.get(self.fields.get('price'))
            minimum_price = self._service_data.get(self.fields.get('minimum_price'))
            maximum_price = self._service_data.get(self.fields.get('maximum_price'))
            price_unit = self._service_data.get(self.fields.get('price_unit'),
                                                self._default_for_field('price_unit'))
            price_interval = self._service_data.get(self.fields.get('price_interval'),
                                                    self._default_for_field('price_interval'))
            hours_for_price = self._service_data.get(self.fields.get('hours_for_price'),
                                                     self._default_for_field('hours_for_price'))

            if price or minimum_price:
                return format_price(price or minimum_price, maximum_price, price_unit, price_interval, hours_for_price)
            else:
                return ''

        # Look up display values for options that have different labels from values
        options = self.get('options')
        if self.has_assurance():
            value = self._service_data.get(self.id, {}).get('value', '')
        else:
            value = self._service_data.get(self.id, '')
        if value != '' and self.type == "number" and self.get('unit'):
            if self.unit_position == "after":
                value = u"{}{}".format(value, self.unit)
            else:
                return u"{}{}".format(self.unit, value)
        if options and value:
            for option in options:
                if 'label' in option and 'value' in option and option['value'] == value:
                    return option['label']

        return value

    @property
    def assurance(self):
        if self.has_assurance():
            return self._service_data.get(self.id, {}).get('assurance', '')
        return ''

    @property
    def answer_required(self):
        if self.get('optional'):
            return False
        elif self.questions:
            return any(question.answer_required for question in self.questions)
        else:
            return self.is_empty


QUESTION_TYPES = {}


class ContentQuestion(object):
    def __new__(cls, data, *args, **kwargs):
        if data.get('type') in QUESTION_TYPES:
            return QUESTION_TYPES[data['type']](data, *args, **kwargs)
        else:
            return Question(data, *args, **kwargs)
