"""
Helper functions that work with the Python standard library, e.g. that
do not require importing any third party or custom modules
"""
import calendar
import datetime
from typing import Any


def dict_contains_other_values(d: dict, types: tuple[Any]) -> bool:
    if not isinstance(d, dict):
        raise TypeError(
            "Can only check for values in a dict if given a dict!"
        )

    for _, value in d.items():
        if not isinstance(value, types):
            return True
    return False


def datetime_to_day_of_week(date_time: datetime) -> str:
    return calendar.day_name[date_time.weekday()]
