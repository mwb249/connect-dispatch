"""
To be completed...
"""

from datetime import datetime, timedelta
import pytz
import pandas as pd


def kelly_shift(check_date, pattern_start_date, local_timezone, shift_start_time=8):
    """
    @param check_date: integer, use an ArcGIS date field or a 13-digit Unix timestamp (millisecond precision).
    @param pattern_start_date: string, use MM-DD-YYYY format. This date will be the first day of the first shift's
    cycle. Use a date that is before any incidents stored in the feature service occurred.
    @param local_timezone: string, Use a standard timezone name (eg., US/Eastern). This should be the agency's local
    timezone.
    @param shift_start_time: integer, The hour the agency's shifts start, 1-24 (default: 8).
    :return string, The shift that was on-duty when the incident initially occurred (possibilities: '1', '2', '3', or
    'out of range').
    """

    # Create datetime objects from timestamp and date string
    check_date = datetime.fromtimestamp(int(check_date / 1000), tz=pytz.utc)
    check_date = check_date.astimezone(pytz.timezone(local_timezone))
    pattern_start_date = datetime.strptime(pattern_start_date, '%m-%d-%Y')

    # Check shift start time to correct date if necessary
    if 0 <= check_date.hour < shift_start_time:
        check_date = check_date - timedelta(days=1)

    # Shift pattern in relation to shift 1, day 1
    s_s1d1 = pattern_start_date
    s_s1d2 = pattern_start_date + timedelta(days=2)
    s_s1d3 = pattern_start_date + timedelta(days=4)
    s_s2d1 = pattern_start_date + timedelta(days=3)
    s_s2d2 = pattern_start_date + timedelta(days=5)
    s_s2d3 = pattern_start_date + timedelta(days=7)
    s_s3d1 = pattern_start_date + timedelta(days=6)
    s_s3d2 = pattern_start_date + timedelta(days=8)
    s_s3d3 = pattern_start_date + timedelta(days=1)

    # End date for date range
    end_date = check_date.date() + timedelta(days=10)

    # Repeat cycle for each day in pattern
    s1d1 = pd.date_range(start=s_s1d1, end=end_date, freq='9D')
    s1d2 = pd.date_range(start=s_s1d2, end=end_date, freq='9D')
    s1d3 = pd.date_range(start=s_s1d3, end=end_date, freq='9D')
    s2d1 = pd.date_range(start=s_s2d1, end=end_date, freq='9D')
    s2d2 = pd.date_range(start=s_s2d2, end=end_date, freq='9D')
    s2d3 = pd.date_range(start=s_s2d3, end=end_date, freq='9D')
    s3d1 = pd.date_range(start=s_s3d1, end=end_date, freq='9D')
    s3d2 = pd.date_range(start=s_s3d2, end=end_date, freq='9D')
    s3d3 = pd.date_range(start=s_s3d3, end=end_date, freq='9D')

    # Combine dataframes
    shift_1 = s1d1.union(s1d2).union(s1d3)
    shift_2 = s2d1.union(s2d2).union(s2d3)
    shift_3 = s3d1.union(s3d2).union(s3d3)

    # Find shift
    check_date = check_date.strftime('%Y-%m-%d')
    if check_date in shift_1:
        shift = '1'
    elif check_date in shift_2:
        shift = '2'
    elif check_date in shift_3:
        shift = '3'
    else:
        shift = 'out of range'
    return shift


def day_of_week(check_datetime, local_timezone):
    """
    @param check_datetime: integer, use an ArcGIS date field or a 13-digit Unix timestamp (millisecond precision).
    @param local_timezone: string, Use a standard timezone name (eg., US/Eastern). This should be the agency's local
    timezone.
    :return Day of the week as a string.
    """

    if check_datetime:
        # Days of the week
        weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

        check_datetime = datetime.fromtimestamp(int(check_datetime / 1000), tz=pytz.utc)
        check_datetime = check_datetime.astimezone(pytz.timezone(local_timezone))
        check_datetime = check_datetime.weekday()

        # Convert weekday to string
        weekday = weekdays[check_datetime]
    else:
        weekday = None

    return weekday


def incident_status(call_dt, enroute_dt, arrival_dt, clear_dt):

    # Find time difference between call date and now
    call_date = datetime.fromtimestamp(int(call_dt / 1000))
    time_difference = datetime.now() - call_date

    # Determine status
    if time_difference.days > 7:
        status = 'Clear'
    elif clear_dt:
        status = 'Clear'
    elif arrival_dt:
        status = 'Arrival'
    elif enroute_dt:
        status = 'Responding'
    else:
        status = 'Dispatched'
    return status
