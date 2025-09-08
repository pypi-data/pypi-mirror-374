import time
from calendar import monthrange

def get_date() -> str:
    """
    Get the current date.

    Returns:
        str: The current date in the format 'YYYY-MM-DD'.
    Examples:
        >>> get_date()
        '2023-10-05'
    """
    return time.strftime("%Y-%m-%d")

def get_time() -> str:
    """
    Get the current time.

    Returns:
        str: The current time in the format 'HH:MM:SS'.

    Examples:
        >>> get_time()
        '14:23:45'
    """
    return time.strftime("%H:%M:%S")

def get_datetime() -> str:
    """
    Get the current date and time.

    Returns:
        str: The current date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    Examples:
        >>> get_datetime()
        '2023-10-05 14:23:45'
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def format_date(date: str, format: str) -> str:
    """
    Format a date string.

    Args:
        date (str): The date string to format.
        format (str): The desired format of the date. This should be a valid format string.

    Returns:
        str: The formatted date string.
        
    Examples:
        >>> format_date("2023-10-05", "%d/%m/%Y")
        '05/10/2023'
        >>> format_date("2023-10-05", "%B %d, %Y")
        'October 05, 2023'

    Format options:
        %a: Abbreviated weekday name (e.g., Sun, Mon, ...)
        %A: Full weekday name (e.g., Sunday, Monday, ...)
        %w: Weekday as a decimal number (0=Sunday, 6=Saturday)
        %d: Day of the month as a zero-padded decimal number (e.g., 01, 02, ..., 31)
        %b: Abbreviated month name (e.g., Jan, Feb, ...)
        %B: Full month name (e.g., January, February, ...)
        %m: Month as a zero-padded decimal number (e.g., 01, 02, ..., 12)
        %y: Year without century as a zero-padded decimal number (e.g., 00, 01, ..., 99)
        %Y: Year with century (e.g., 2023)
        %H: Hour (24-hour clock) as a zero-padded decimal number (e.g., 00, 01, ..., 23)
        %I: Hour (12-hour clock) as a zero-padded decimal number (e.g., 01, 02, ..., 12)
        %p: AM or PM
        %M: Minute as a zero-padded decimal number (e.g., 00, 01, ..., 59)
        %S: Second as a zero-padded decimal number (e.g., 00, 01, ..., 59)
        %f: Microsecond as a decimal number, zero-padded on the left (e.g., 000000, 000001, ..., 999999)
        %z: UTC offset in the form +HHMM or -HHMM (empty string if the object is naive)
        %Z: Time zone name (empty string if the object is naive)
        %j: Day of the year as a zero-padded decimal number (e.g., 001, 002, ..., 366)
        %U: Week number of the year (Sunday as the first day of the week) as a zero-padded decimal number (e.g., 00, 01, ..., 53)
        %W: Week number of the year (Monday as the first day of the week) as a zero-padded decimal number (e.g., 00, 01, ..., 53)
        %c: Locale’s appropriate date and time representation (e.g., Tue Aug 16 21:30:00 1988)
        %x: Locale’s appropriate date representation (e.g., 08/16/88)
        %X: Locale’s appropriate time representation (e.g., 21:30:00)


    """
    return time.strftime(format, time.strptime(date, "%Y-%m-%d"))

def calculate_age(birth_date: str) -> int:
    """
    Calculate the age based on the birth date.

    Args:
        birth_date (str): The birth date in the format 'YYYY-MM-DD'.

    Returns:
        int: The age in years.

    Examples:
        >>> calculate_age("2000-01-01")
        22
        >>> calculate_age("1995-12-31")
        26
    """
    today = time.localtime()
    birth = time.strptime(birth_date, "%Y-%m-%d")
    return today.tm_year - birth.tm_year - ((today.tm_mon, today.tm_mday) < (birth.tm_mon, birth.tm_mday))

def add_days_to_date(date: str, days: int) -> str:
    """
    Add a specified number of days to a date.

    Args:
        date (str): The date in the format 'YYYY-MM-DD'.
        days (int): The number of days to add.

    Returns:
        str: The new date in the format 'YYYY-MM-DD' after adding the specified number of days.

    Examples:
        >>> add_days_to_date("2023-10-05", 7)
        '2023-10-12'
        >>> add_days_to_date("2023-10-05", 30)
        '2023-11-04'
    """
    date_obj = time.strptime(date, "%Y-%m-%d")
    new_date = time.mktime(date_obj) + days * 86400
    return time.strftime("%Y-%m-%d", time.localtime(new_date))

def subract_dates(date1: str, date2: str) -> int:
    """
    Subtract two dates and return the difference in days.

    Args:
        date1 (str): The first date in the format 'YYYY-MM-DD'.
        date2 (str): The second date in the format 'YYYY-MM-DD'.

    Returns:
        int: The difference in days between the two dates.

    Examples:
        >>> subtract_dates("2023-10-05", "2023-10-12")
        7
        >>> subtract_dates("2023-10-05", "2023-11-04")
        30
    """
    date1_obj = time.strptime(date1, "%Y-%m-%d")
    date2_obj = time.strptime(date2, "%Y-%m-%d")
    diff = time.mktime(date1_obj) - time.mktime(date2_obj)
    return int(diff / 86400)

def check_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year.

    Args:
        year (int): The year to check.

    Returns:
        bool: True if the year is a leap year, False otherwise.

    Examples:
        >>> check_leap_year(2024)
        True
        >>> check_leap_year(2023)
        False
    """
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

def convert_timestamp_to_date(timestamp: int) -> str:
    """
    Convert a Unix timestamp to a date string.

    Args:
        timestamp (int): The Unix timestamp.

    Returns:
        str: The date in the format 'YYYY-MM-DD'.

    Examples:
        >>> convert_timestamp_to_date(1672531200)
        '2023-10-05'
        >>> convert_timestamp_to_date(1675113600)
        '2023-11-04'
    """
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))

def convert_date_to_timestamp(date: str) -> int:
    """
    Convert a date string to a Unix timestamp.

    Args:
        date (str): The date in the format 'YYYY-MM-DD'.

    Returns:
        int: The Unix timestamp.

    Examples:
        >>> convert_date_to_timestamp("2023-10-05")
        1672531200
        >>> convert_date_to_timestamp("2023-11-04")
        1675113600
    """
    return int(time.mktime(time.strptime(date, "%Y-%m-%d")))

def get_day_of_week(date: str) -> str:
    """
    Get the day of the week for a given date.

    Args:
        date (str): The date in the format 'YYYY-MM-DD'.

    Returns:
        str: The day of the week (e.g., Monday, Tuesday, ...).

    Examples:
        >>> get_day_of_week("2023-10-05")
        'Thursday'
        >>> get_day_of_week("2023-11-04")
        'Saturday'
    """
    return time.strftime("%A", time.strptime(date, "%Y-%m-%d"))

def get_days_in_month(month: int, year: int) -> int:
    """
    Get the number of days in a given month.

    Args:
        month (int): The month (1-12).
        year (int): The year.

    Returns:
        int: The number of days in the month.

    Examples:
        >>> get_days_in_month(2, 2024)
        29
        >>> get_days_in_month(2, 2023)
        28
    """
    return monthrange(year, month)[1]

