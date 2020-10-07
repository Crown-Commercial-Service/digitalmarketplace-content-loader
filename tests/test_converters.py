import pytest

from dmcontent.converters import convert_to_boolean, convert_to_number


def test_convert_to_boolean_converts_strings_to_true_if_they_look_like_truthy():
    for truthy in ['true', 'on', 'yes', '1']:
        assert convert_to_boolean(truthy)


def test_convert_to_boolean_converts_strings_to_false_if_they_look_falsy():
    for falsy in ['false', 'off', 'no', '0']:
        assert not convert_to_boolean(falsy)


def test_convert_to_boolean_leaves_other_things_unchanged():
    for value in ['falsey', 'other', True, 0]:
        assert convert_to_boolean(value) == value


def test_convert_to_number_converts_integer_looking_strings_into_floats():
    for number in ['0', '1', '2', '9999']:
        assert isinstance(convert_to_number(number), int)


def test_convert_to_number_converts_floaty_looking_strings_into_floats():
    for number in ['0.99', '1.1', '1000.0000001']:
        assert isinstance(convert_to_number(number), float)


@pytest.mark.parametrize("text, prefix, number", (
    ("£0.99", "£", 0.99),
    ("£ 12000", "£", 12000),
))
def test_convert_to_number_can_remove_prefixes(text, prefix, number):
    assert convert_to_number(text, prefix=prefix) == number


@pytest.mark.parametrize("text, suffix, number", (
    ("98%", "%", 98),
    ("45 %", "%", 45),
    ("25.0%", "%", 25.0),
    ("3p", "p", 3),
    ("7 hours", "hours", 7),
))
def test_convert_to_number_can_remove_suffixes(text, suffix, number):
    assert convert_to_number(text, suffix=suffix) == number


def test_convert_to_number_leaves_other_things__unchanged():
    for value in [0, 'other', True, 123]:
        assert convert_to_number(value) == value
