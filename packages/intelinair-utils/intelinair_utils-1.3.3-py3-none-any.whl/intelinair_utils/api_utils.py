"""
Helper utilities for api.
"""
from datetime import datetime


def validate_date(date_to_validate: str):
    """
    Date string validation method.
    Currently supported formats are:
    '%Y-%m-%d'              -> 2021-10-27
    '%Y-%m-%dT%H:%M:%SZ'    -> 2022-08-13T10:37:23Z
    Args:
        date_to_validate: input date string to validate
    Raises:
        ValueError: In case of invalid input date format
    """
    valid_date_formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ']
    for date_format in valid_date_formats:
        try:
            datetime.strptime(date_to_validate, date_format)
        except ValueError:
            continue
        break
    else:
        raise ValueError(f'Invalid date string:"{date_to_validate}" valid formats are: {", ".join(valid_date_formats)}')
