# -*- coding: utf-8 -*-
from dmcontent.formats import format_price, format_service_price
import pytest


@pytest.mark.parametrize('args, formatted_price', [
    ((u'12', None, 'Unit', None), u'£12 per unit'),
    (('12', '13', 'Unit', None), u'£12 to £13 per unit'),
    (('12', '13', 'Unit', 'Second'), u'£12 to £13 per unit per second'),
    (('12', None, 'Unit', 'Second'), u'£12 per unit per second'),
    ((12, 13, 'Unit', None), u'£12 to £13 per unit'),
    (('34', None, 'Lab', None, '4 hours'), u'4 hours for £34'),
    (('12', None, None, None), u'£12'),
])
def test_format_price(args, formatted_price):
    assert format_price(*args) == formatted_price


def test_format_price_errors():
    with pytest.raises((TypeError, AttributeError)):
        format_price(*(None, None, None, None))


@pytest.mark.parametrize('price_min, formatted_price', [
    ('12.12', u'£12.12 to £13.13 per unit per second'),
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
