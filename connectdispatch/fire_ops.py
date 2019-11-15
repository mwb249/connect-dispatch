"""
To be completed...
"""

from datetime import timedelta
import pandas as pd


def kelly_shift(check_date, pattern_start_date, shift_start_time):
    """
    To be completed...
    """

    # Check shift start time to correct date if necessary
    if 0 <= check_date.hour < shift_start_time:
        check_date = check_date - timedelta(days=1)
    else:
        pass

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

    # Find shift
    check_date = check_date.date()
    if check_date in s1d1 or check_date in s1d2 or check_date in s1d3:
        shift = '1'
    elif check_date in s2d1 or check_date in s2d2 or check_date in s2d3:
        shift = '2'
    elif check_date in s3d1 or check_date in s3d2 or check_date in s3d3:
        shift = '3'
    else:
        shift = 'out of range'
    return shift
