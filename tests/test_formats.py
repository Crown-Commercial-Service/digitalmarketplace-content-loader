# -*- coding: utf-8 -*-
from dmcontent.formats import format_price, format_service_price, comma_format
import pytest


@pytest.mark.parametrize('args, formatted_price', [
    ((u'12', None, 'Unit', None), u'£12 a unit'),
    ((u'12', None, 'Hour', None), u'£12 an hour'),
    (('12', '13', 'Unit', None), u'£12 to £13 a unit'),
    (('12', '13', 'Unit', 'Second'), u'£12 to £13 a unit a second'),
    (('12', None, 'Unit', 'Second'), u'£12 a unit a second'),
    (('12', None, 'Instance', 'Hour'), u'£12 an instance an hour'),
    ((12, 13, 'Unit', None), u'£12 to £13 a unit'),
    (('34', None, 'Lab', None, '4 hours'), u'4 hours for £34'),
    (('12', None, None, None), u'£12'),
    ((0, None, None, None), u'£0'),
    (('12', "", None, None), u'£12'),
    (('12', None, None, 'Second'), '£12 a second'),
    ((None, '12', None, None), '£12'),
    ((None, 0, None, None), '£0'),
    (("", '12', None, None), '£12'),
])
def test_format_price(args, formatted_price):
    assert format_price(*args) == formatted_price


@pytest.mark.parametrize('args', [
    (None, None, None, None),
    (None, None, 'Unit', 'Second'),
    (None, "", 'Unit', 'Second'),
    ("", None, 'Unit', 'Second'),
])
def test_format_price_errors(args):
    with pytest.raises(TypeError):
        format_price(*args)


@pytest.mark.parametrize('price_min, formatted_price', [
    ('12.12', u'£12.12 to £13.13 a unit a second'),
    ('', ''),
    (None, ''),
])
def test_format_service_price(price_min, formatted_price):
    service = {
        'priceMin': price_min,
        'priceMax': '13.13',
        'priceUnit': 'Unit',
        'priceInterval': 'Second',
    }

    assert format_service_price(service) == formatted_price


@pytest.mark.parametrize('number, formatted_number', [
    (1000, '1,000'),
    (123456.78, '123,456.78'),
    ('1000000', '1,000,000'),
    (500, '500'),
    (0.12, '0.12'),
    (999.99, '999.99'),
])
def test_comma_format(number, formatted_number):
    assert comma_format(number) == formatted_number
