"""To be completed..."""


import datetime
import pytz
import re


def unit_dt_from_xml(xmltag, xmltree, local_tz='America/Detroit'):
    """
    Iterate through unit string datetime objects (dispatched, en route, arrival) and return the earliest datetime as a
    'timezone aware' datetime object.
    """
    datetime_list = []
    timezone = pytz.timezone(local_tz)
    for unit_time in xmltree.iter(xmltag):
        unit_time = unit_time.text
        if not unit_time:
            pass
        else:
            match = re.search(r'(.*?)/', unit_time)
            try:
                month = int(match.group(1))
            except ValueError:
                month = int()
            match = re.search(r'.*?/(.*?)/', unit_time)
            try:
                day = int(match.group(1))
            except ValueError:
                day = int()
            match = re.search(r'.*?/.*?/(.*?) ', unit_time)
            try:
                year = int(match.group(1))
            except ValueError:
                year = int()
            match = re.search(r'(..)$', unit_time)
            try:
                am_pm = str(match.group(1))
            except ValueError:
                am_pm = str('')
            match = re.search(r'.*?/.*?/.*? (.*?):', unit_time)
            try:
                hour = int(match.group(1))
                if am_pm == 'PM' and hour != 12:
                    hour = hour + 12
                elif am_pm == 'AM' and hour == 12:
                    hour = 0
                else:
                    pass
            except ValueError:
                hour = int()
            match = re.search(r'.*?/.*?/.*? .*?:(.*?):', unit_time)
            try:
                minute = int(match.group(1))
            except ValueError:
                minute = int()
            match = re.search(r'.*?/.*?/.*? .*?:.*?:(.*?) ', unit_time)
            try:
                second = int(match.group(1))
            except ValueError:
                second = int()
            unit_time = datetime.datetime(year, month, day, hour, minute, second)
            unit_time = timezone.localize(unit_time)
            datetime_list.append(unit_time)
            datetime_list.sort()
    if not datetime_list:
        pass
    else:
        return datetime_list[0]


def unit_dt_from_dict(unit_list, incident, unit_key, local_tz='America/Detroit'):
    """
    Obtain unit datetime...
    """
    datetime_list = []
    timezone = pytz.timezone(local_tz)
    for unit in unit_list:
        if unit['incident_number'] == incident['incident_number']:
            unit_time = unit[unit_key]
            if not unit_time:
                pass
            else:
                match = re.search(r'(.*?)/', unit_time)
                try:
                    month = int(match.group(1))
                except ValueError:
                    month = int()
                match = re.search(r'.*?/(.*?)/', unit_time)
                try:
                    day = int(match.group(1))
                except ValueError:
                    day = int()
                match = re.search(r'.*?/.*?/(.*?) ', unit_time)
                try:
                    year = int(match.group(1))
                except ValueError:
                    year = int()
                match = re.search(r'(..)$', unit_time)
                try:
                    am_pm = str(match.group(1))
                except ValueError:
                    am_pm = str('')
                match = re.search(r'.*?/.*?/.*? (.*?):', unit_time)
                try:
                    hour = int(match.group(1))
                    if am_pm == 'PM' and hour != 12:
                        hour = hour + 12
                    elif am_pm == 'AM' and hour == 12:
                        hour = 0
                    else:
                        pass
                except ValueError:
                    hour = int()
                match = re.search(r'.*?/.*?/.*? .*?:(.*?):', unit_time)
                try:
                    minute = int(match.group(1))
                except ValueError:
                    minute = int()
                match = re.search(r'.*?/.*?/.*? .*?:.*?:(.*?) ', unit_time)
                try:
                    second = int(match.group(1))
                except ValueError:
                    second = int()
                unit_time = datetime.datetime(year, month, day, hour, minute, second)
                unit_time = timezone.localize(unit_time)
                datetime_list.append(unit_time)
                datetime_list.sort()
        if not datetime_list:
            pass
        else:
            return datetime_list[0]


def incident_dt_ws(datetime_str, local_tz='America/Detroit'):
    """
    Parse a datetime string returned from the OC CAD web service and return a 'timezone aware' datetime object.
    """
    timezone = pytz.timezone(local_tz)
    if not datetime_str:
        datetime_corrected = None
    else:
        match = re.search(r'(.*?)/', datetime_str)
        try:
            month = int(match.group(1))
        except ValueError:
            month = int()
        match = re.search(r'.*?/(.*?)/', datetime_str)
        try:
            day = int(match.group(1))
        except ValueError:
            day = int()
        match = re.search(r'.*?/.*?/(.*?) ', datetime_str)
        try:
            year = int(match.group(1))
        except ValueError:
            year = int()
        match = re.search(r'(..)$', datetime_str)
        try:
            am_pm = str(match.group(1))
        except ValueError:
            am_pm = str('')
        match = re.search(r'.*?/.*?/.*? (.*?):', datetime_str)
        try:
            hour = int(match.group(1))
            if am_pm == 'PM' and hour != 12:
                hour = hour + 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            else:
                pass
        except ValueError:
            hour = int()
        match = re.search(r'.*?/.*?/.*? .*?:(.*?):', datetime_str)
        try:
            minute = int(match.group(1))
        except ValueError:
            minute = int()
        match = re.search(r'.*?/.*?/.*? .*?:.*?:(.*?) ', datetime_str)
        try:
            second = int(match.group(1))
        except ValueError:
            second = int()
        datetime_corrected = datetime.datetime(year, month, day, hour, minute, second)
        datetime_corrected = timezone.localize(datetime_corrected)
    return datetime_corrected


def incident_dt_email(datetime_str, local_tz='America/Detroit'):
    """
    Parse a datetime string returned from the OC CAD email link and return a 'timezone aware' datetime object.
    """
    timezone = pytz.timezone(local_tz)
    if not datetime_str:
        datetime_corrected = None
    else:
        match = re.search(r'(.*?)/', datetime_str)
        try:
            month = int(match.group(1))
        except ValueError:
            month = int()
        match = re.search(r'.*?/(.*?)/', datetime_str)
        try:
            day = int(match.group(1))
        except ValueError:
            day = int()
        match = re.search(r'.*?/.*?/(.*?) ', datetime_str)
        try:
            year = int('20' + match.group(1))
        except ValueError:
            year = int()
        match = re.search(r'.*?/.*?/.*? (.*?):', datetime_str)
        try:
            hour = int(match.group(1))
        except ValueError:
            hour = int()
        match = re.search(r'.*?/.*?/.*? .*?:(.*?):', datetime_str)
        try:
            minute = int(match.group(1))
        except ValueError:
            minute = int()
        match = re.search(r'.*?/.*?/.*? .*?:.*?:(..)', datetime_str)
        try:
            second = int(match.group(1))
        except ValueError:
            second = int()
        datetime_corrected = datetime.datetime(year, month, day, hour, minute, second)
        datetime_corrected = timezone.localize(datetime_corrected)
    return datetime_corrected
