# -*- coding: utf-8 -*-

import datetime
import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import albert
import dateparser
import pytz

__doc__ = """
Extension for converting between timezones

Synopsis: `<from_time> [to|in] <to_tz>`

Examples:
`10pm PST to CST`
`8am MST in New York`
`Time in IST`

Date formats and timezone aliases can be set in config.jsonc
"""
__title__ = "Timezone Convert"
__version__ = "0.0.1"
__authors__ = "Jonah Lawrence"
__py_deps__ = ["dateparser"]

timezone_regex = re.compile(
    r"(?P<from_time>.*(?:pm|am|\d:\d|time|now|current|noon|midnight).*)\s(?:to|in)\s(?P<to_tz>.*)",
    re.I,
)


def load_config(config_path: Path) -> str:
    """
    Strip comments and load the config from the config file.
    """
    with config_path.open("r") as config_file:
        contents = config_file.read()
    contents = re.sub(r"^\s*//.*$", "", contents, flags=re.MULTILINE)
    return json.loads(contents)


config_path = Path(__file__).parent / "config.jsonc"
config = load_config(config_path)


class ConversionResult:
    """
    Class to hold the result of a timezone conversion.
    """

    def __init__(
        self,
        from_time: Optional[datetime] = None,
        result_time: Optional[datetime] = None,
    ):
        self.from_time = from_time
        self.result_time = result_time

    def __format_date(self, date: datetime) -> str:
        """
        Convert dates to a specified format

        Args:
            date (datetime): The date to format

        Returns:
            str: The formatted date
        """
        # %a = Weekday (eg. "Mon"), %d = Day (eg. "01"), %b = Month (eg. "Sep")
        date_format = config.get("date_format", "%a %d %b")
        # %H = Hours (24-hour clock), %M = Minutes, %I = Hours (12-hour clock), %p = AM/PM
        time_format = config.get("time_format", "%I:%M %p")
        # format the date and remove leading zeros and trailing spaces
        formatted = date.strftime(f"{date_format} {time_format}")
        if config.get("remove_leading_zeros", True):
            formatted = re.sub(r" 0(\d)", r" \1", formatted)
        if config.get("lowercase_am_pm", True):
            formatted = formatted.replace("AM", "am").replace("PM", "pm")
        return f"{formatted.strip()} {self.__get_timezone(date)}".strip()

    def __get_timezone(self, date: datetime) -> str:
        """
        Get the timezone of the given date.

        Args:
            date (datetime): The date to get the timezone of

        Returns:
            str: The timezone of the given date
        """
        tz = date.tzname() or date.strftime("%Z")
        # remove '\' from timezone name if it appears
        return tz.replace("\\", "")

    @property
    def formatted_from_time(self) -> Optional[str]:
        """Returns the from_time as a formatted string"""
        return self.__format_date(self.from_time) if self.from_time else None

    @property
    def formatted_result_time(self) -> Optional[str]:
        return self.__format_date(self.result_time) if self.result_time else None

    def __str__(self) -> str:
        return (
            f"{self.formatted_result_time} (Converted from {self.formatted_from_time})"
        )

    def __repr__(self) -> str:
        return str(self)


class TimezoneConverter:
    def __replace_tz_aliases(self, input_tz: str) -> str:
        """
        Note: The dateparser library handles most timezones automatically but this is just to fill in the gaps.

        Keywords such as cities can be added to the list of replacements to use as aliases in the config.jsonc file.

        Args:
            input_tz (str): The timezone or text containing the timezone to check.

        Returns:
            str: The new timezone name if it was found in the overrides dictionary, otherwise the original timezone name.
        """
        tz_aliases = config.get("tz_aliases", {})
        return tz_aliases.get(input_tz.lower().strip(), input_tz)

    def __parse_date(
        self,
        date_str: str,
        from_tz: Optional[str] = None,
        to_tz: Optional[str] = None,
        future: bool = True,
        base: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """
        Returns datetime object for given date string

        Args:
            date_str (str): The date string to be parsed.
            from_tz (Optional[str]): The timezone to interpret the date as.
            to_tz (Optional[str]): The timezone to return the date in.
            future (Optional[bool]): Set to true to prefer dates from the future when parsing.
            base (datetime): datetime representing where dates should be parsed relative to.

        Returns:
            Optional[datetime]: The parsed date or None if the date could not be parsed.
        """
        # set default base datetime if none is given
        base = base or datetime.now()
        # set from_tz if date_str contains a timezone alias
        tz_aliases = list(config.get("tz_aliases", {}).items())
        pytz_timezones = list(zip(pytz.all_timezones, pytz.all_timezones))
        for alias, tz_name in tz_aliases + pytz_timezones:
            alias = re.escape(alias)
            if re.search(fr"(^|\s){alias}(\s|$)", date_str, re.I):
                from_tz = tz_name
                to_tz = to_tz or from_tz
                date_str = re.sub(fr"(^|\s){alias}(\s|$)", r"\1", date_str, flags=re.I)
                break
        albert.info(f"Using timezone {from_tz} for {date_str}")
        albert.info(f"Target timezone is {to_tz}")
        # set dateparser settings
        settings: Dict[str, Any] = {
            "RELATIVE_BASE": base.replace(tzinfo=None),
            "RETURN_AS_TIMEZONE_AWARE": True,
            **({"TIMEZONE": self.__replace_tz_aliases(from_tz)} if from_tz else {}),
            **({"TO_TIMEZONE": self.__replace_tz_aliases(to_tz)} if to_tz else {}),
            **({"PREFER_DATES_FROM": "future"} if future else {}),
        }
        # parse the date
        date = None
        try:
            albert.info(f'Parsing date "{date_str}" with settings {settings}')
            # parse the date with dateparser
            date = dateparser.parse(date_str, settings=settings)
            assert date is not None
            # convert the date to the specified timezone
            if not date.tzinfo and to_tz:
                date = pytz.timezone(self.__replace_tz_aliases(to_tz)).localize(date)
        except pytz.exceptions.UnknownTimeZoneError as error:
            albert.warning(f"Unknown timezone: {error}")
        except AssertionError as error:
            albert.warning(f"Could not parse date: {date_str}")
        # return the datetime object
        return date

    def convert_time(self, from_time_input: str, to_tz: str) -> ConversionResult:
        """
        Convert a time from one timezone to another

        Args:
            from_time_input (str): The time to convert
            to_tz (str): The timezone to convert the time to

        Returns:
            TzResult: The resulting time and the time converted from
        """
        # parse the input time by itself
        from_time = self.__parse_date(from_time_input)
        # parse time with target timezone
        result_time = self.__parse_date(from_time_input, to_tz=to_tz)
        # make sure the date is correct for the from_time
        if from_time and result_time and from_time.tzinfo and result_time.tzinfo:
            from_time = (
                result_time - result_time.utcoffset() + from_time.utcoffset()
            ).replace(tzinfo=from_time.tzinfo)
        # return the result
        return ConversionResult(from_time, result_time)


def create_item(text: str, subtext: str) -> albert.Item:
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
        icon=str(Path(__file__).parent / "icons" / "clock.svg"),
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
    tc = TimezoneConverter()
    # use the current time if no time is given
    if from_time.lower().strip() in ("now", "current", "current time", "time"):
        from_time = datetime.now().isoformat()
    # convert the time
    result = tc.convert_time(from_time, to_tz)
    # display error messages if unsuccessful
    if result.from_time is None:
        return [create_item(f"Could not parse date: {from_time}", "")]
    if result.result_time is None:
        return [create_item(f"Could not parse timezone: {to_tz}", "")]
    # return the result
    return [
        create_item(
            result.formatted_result_time, f"Converted from {result.formatted_from_time}"
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
