# -*- coding: utf-8 -*-

import datetime
import re
import traceback
from pathlib import Path
from typing import List

import albert

from dates import format_date, parse_date

__doc__ = """
Extension for converting between timezones

Synopsis: `<from_time> [to|in] <to_tz>`

Examples:
`10pm PST to CST`
`8am MST in New York`

24-hour time and timezone aliases can be set in config.py
"""
__title__ = "Timezone Convert"
__version__ = "0.0.1"
__authors__ = "Jonah Lawrence"
__py_deps__ = ["dateparser"]

local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

timezone_regex = re.compile(
    r"(?P<from_time>.*(?:pm|am|\d:\d).*)\s(?P<seperator>to|in)\s(?P<to_tz>.*)", re.I
)


def get_icon_path() -> str:
    """
    Get the path to the icon

    Returns:
        str: The path to the icon.
    """
    return str(Path(__file__).parent / "icons" / "clock.svg")


def get_item(text: str, subtext: str) -> albert.Item:
    """
    Create an albert.Item from a text and subtext.

    Args:
        text (str): The text to display.
        subtext (str): The subtext to display.

    Returns:
        albert.Item: The item to be added to the list of results.
    """
    return albert.Item(
        id=__title__,
        icon=get_icon_path(),
        text=text,
        subtext=subtext,
        actions=[albert.ClipAction("Copy result to clipboard", text)],
    )


def get_items(from_time: str, to_tz: str) -> List[albert.Item]:
    """
    Generate the Albert items to display for the query.

    Args:
        query_string (str): The query string to be parsed.

    Returns:
        List[albert.Item]: The list of items to display.
    """
    # parse from_time by itself
    from_dt = parse_date(from_time)
    if not from_dt:
        return [get_item(f"Error: Could not parse date: {from_time}", "")]
    # parse time with target timezone
    result_dt = parse_date(from_time, to_tz=to_tz)
    if not result_dt:
        return [get_item(f"Error: Could not parse timezone: {to_tz}", "")]
    # format the results
    from_str = format_date(from_dt)
    result_str = format_date(result_dt)
    from_tz = from_dt.tzname() or local_timezone.tzname(from_dt) or ""
    result_tz = result_dt.tzname() or ""
    return [
        get_item(
            f"{result_str} {result_tz}",
            f"Converted from {from_str} {from_tz}",
        )
    ]


def handleQuery(query: albert.Query) -> List[albert.Item]:
    """
    Handler for a query received from Albert.
    """
    query_string = query.string.strip()
    match = timezone_regex.fullmatch(query_string)
    if match:
        try:
            return get_items(match.group("from_time"), match.group("to_tz"))
        except Exception as error:
            albert.warning(f"Error: {error}")
            tb = "".join(
                traceback.format_exception(error.__class__, error, error.__traceback__)
            )
            albert.warning(tb)
            albert.info(
                "Something went wrong. Make sure you're using the correct format."
            )
