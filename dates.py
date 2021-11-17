import re
from datetime import datetime
from typing import Any, Dict, Optional

import albert
import dateparser
import pytz

import config


def __replace_tz_aliases(input_tz: str) -> str:
    """
    Note: The dateparser library handles most timezones automatically but this is to fill in the gaps.

    This function replaces certain timezones with more relevant ones.
    Eg. "BST" can refer to "Bougainville Standard Time," but "British Summer Time" is more commonly used.

    Additionally, more words such as cities can be added to the list of replacements to use as aliases.

    Args:
        input_tz (str): The timezone or text containing the timezone to check.

    Returns:
        str: The new timezone name if it was found in the overrides dictionary, otherwise the original timezone name.
    """
    return config.aliases.get(input_tz.lower().strip(), input_tz)


def parse_date(
    date_str: Optional[str] = None,
    from_tz: Optional[str] = None,
    to_tz: Optional[str] = None,
    future: bool = False,
    base: Optional[datetime] = None,
) -> Optional[datetime]:
    """
    Returns datetime object for given date string

    Args:
        date_str (Optional[str]): The date string to be parsed.
        from_tz (Optional[str]): The timezone to interpret the date as.
        to_tz (Optional[str]): The timezone to return the date in.
        future (Optional[bool]): Set to true to prefer dates from the future when parsing.
        base (datetime): datetime representing where dates should be parsed relative to.

    Returns:
        Optional[datetime]: The parsed date or None if the date could not be parsed.
    """
    # if no date string is given, return None
    if date_str is None:
        return None
    # set default base datetime if none is given
    base = base or datetime.now()
    # set from_tz if date_str contains a timezone alias
    pytz_timezones = list(zip(pytz.all_timezones, pytz.all_timezones))
    for alias, tz_name in list(config.aliases.items()) + pytz_timezones:
        if re.search(fr"(^|\b){alias}(\b|$)", date_str, re.I):
            from_tz = tz_name
            to_tz = to_tz or from_tz
            date_str = re.sub(fr"(^|\b){alias}(\b|$)", "", date_str, flags=re.I)
            break
    albert.info(f"Using timezone {from_tz} for {date_str}")
    # set dateparser settings
    settings: Dict[str, Any] = {
        "RELATIVE_BASE": base.replace(tzinfo=None),
        **({"TIMEZONE": __replace_tz_aliases(from_tz)} if from_tz else {}),
        **({"TO_TIMEZONE": __replace_tz_aliases(to_tz)} if to_tz else {}),
        **({"PREFER_DATES_FROM": "future"} if future else {}),
    }
    # parse the date
    date = None
    try:
        # parse the date with dateparser
        date = dateparser.parse(date_str, settings=settings)
        assert date is not None
        # convert the date to the specified timezone
        if not date.tzname() and to_tz:
            date = pytz.timezone(__replace_tz_aliases(to_tz)).localize(date)
    except pytz.exceptions.UnknownTimeZoneError as error:
        albert.warning(f"Unknown timezone: {error}")
    except AssertionError as error:
        albert.warning(f"Could not parse date: {date_str}")
    # return the datetime object
    return date


def format_date(
    date: datetime,
    base: Optional[datetime] = None,
) -> str:
    """
    Convert dates to a specified format

    Args:
        date (datetime): The date to format
        base (datetime): When the date or time matches the info from base, it will be skipped.
            This helps avoid repeated info when formatting time ranges.

    Returns:
        str: The formatted date
    """
    # set default base datetime if none is given
    base = base or datetime.now()
    # %a = Weekday (eg. "Mon"), %d = Day (eg. "01"), %b = Month (eg. "Sep")
    date_format = "%a %d %b"
    # include the year if the date is in a different year
    if date.year != base.year:
        # %Y = Year (eg. "2021")
        date_format += " %Y"
    # include the time if it is not an all day event and not the same as the base
    if date != base:
        # %H = Hours (24-hour clock), %M = Minutes, %I = Hours (12-hour clock), %p = AM/PM
        date_format += " %H:%M" if config.hr24 else " %I:%M %p"
    # format the date and remove leading zeros and trailing spaces
    return (
        date.strftime(date_format)
        .replace(" 0", " ", 1)
        .replace(" AM", " am")
        .replace(" PM", " pm")
        .strip()
    )
