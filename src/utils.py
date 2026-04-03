"""Shared utility functions."""

from datetime import date


def get_current_season() -> str:
    """Return current season based on month."""
    month = date.today().month
    if month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    else:
        return "winter"


def get_weekday_name() -> str:
    """Return current weekday name (e.g. 'Monday')."""
    return date.today().strftime("%A")
