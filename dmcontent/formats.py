# -*- coding: utf-8 -*-
from typing import Optional, Union


def comma_format(number: Union[str, float, int]) -> str:
    """
    Format a number with commas if it's greater than 999.
    eg: `1000 -> '1,000'
        123456.78 -> '123,456.78'
        '1000000' -> '1,000,000'
        500 -> '500'

    :param number: The number to be formatted. Either an int, a float or a str.
    :return: A string of the comma formatted number
    """
    if type(number) == str:
        try:
            number = int(number)
        except ValueError:
            number = float(number)

    if type(number) == int:
        # Don't need to add decimal places to an int
        return f"{number:,}"
    else:
        return f"{number:,.2f}"


def format_price(min_price: Optional[Union[str, float]],
                 max_price: Optional[Union[str, float]],
                 unit: Optional[str],
                 interval: Optional[str],
                 hours_for_price: Optional[str] = None):
    """Format a price string"""
    if min_price is not None and min_price != '':
        min_price = comma_format(min_price)
    if max_price is not None and max_price != '':
        max_price = comma_format(max_price)

    if not (min_price or max_price):
        raise TypeError('One of min_price or max_price should be number or non-empty string, not None')

    if hours_for_price:
        return u'{} for £{}'.format(hours_for_price, min_price or max_price)

    formatted_price = ""
    if min_price:
        formatted_price += u'£{}'.format(min_price)
    if min_price and max_price:
        formatted_price += u' to '
    if max_price:
        formatted_price += u'£{}'.format(max_price)
    if unit:
        formatted_price += ' a ' + unit.lower()
    if interval:
        formatted_price += ' a ' + interval.lower()
    return formatted_price


def format_service_price(service):
    """Format a price string from a service dictionary

    :param service: a service dictionary, returned from data API

    :return: a formatted price string if the required
             fields are set in the service dictionary.
    """
    if not service.get('priceMin'):
        return ''
    return format_price(
        service.get('priceMin'),
        service.get('priceMax'),
        service.get('priceUnit'),
        service.get('priceInterval'))
