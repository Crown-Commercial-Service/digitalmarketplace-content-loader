# -*- coding: utf-8 -*-
from dmcontent.formats import format_price, format_service_price
import pytest


def test_format_price():
    cases = [
        ((u'12', None, 'Unit', None), u'£12 per unit'),
        (('12', '13', 'Unit', None), u'£12 to £13 per unit'),
        (('12', '13', 'Unit', 'Second'), u'£12 to £13 per unit per second'),
        (('12', None, 'Unit', 'Second'), u'£12 per unit per second'),
        ((12, 13, 'Unit', None), u'£12 to £13 per unit'),
        (('34', None, 'Lab', None, '4 hours'), u'4 hours for £34'),
        (('12', None, None, None), u'£12'),
    ]

    def check_price_formatting(args, formatted_price):
        assert format_price(*args) == formatted_price

    for args, formatted_price in cases:
        yield check_price_formatting, args, formatted_price


def test_format_price_errors():
    cases = [
        (None, None, None, None),
    ]

    def check_price_formatting(case):
        with pytest.raises((TypeError, AttributeError)):
            format_price(*case)

    for case in cases:
        yield check_price_formatting, case


def test_format_service_price():
    service = {
        'priceMin': '12.12',
        'priceMax': '13.13',
        'priceUnit': 'Unit',
        'priceInterval': 'Second',
    }

    cases = [
        ('12.12', u'£12.12 to £13.13 per unit per second'),
        ('', ''),
        (None, ''),
    ]

    def check_service_price_formatting(price_min, formatted_price):
        service['priceMin'] = price_min
        assert format_service_price(service) == formatted_price

    for price_min, formatted_price in cases:
        yield check_service_price_formatting, price_min, formatted_price
