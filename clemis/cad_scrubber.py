"""
The CADScrubber module contains functions to assist in transforming and preparing CLEMIS CAD
incident data for geocoding and analysis.
"""

import csv

# Create "cities" list. This list is used in the "split" functions to properly parse the city field.
# The values in the list are municipalities that are one word, the others are two or three.
cities = ['CLARKSTON', 'ROCHESTER', 'TROY', 'ORTONVILLE', 'OXFORD', 'PONTIAC', 'LEONARD', 'MILFORD',
          'BIRMINGHAM', 'NOVI', 'FARMINGTON', 'SOUTHFIELD', 'FERNDALE', 'CLAWSON', 'NORTHVILLE',
          'WIXOM', 'BERKLEY', 'HOLLY']

# Create "inc_desc_dict" dictionary using the inc_disc_dict.csv file.
with open('inc_desc_dict.csv', mode='r') as infile:
    reader = csv.reader(infile)
    inc_desc_dict = {rows[0]: rows[1] for rows in reader}


def split_address(field):
    """
    Parses the ADDRESS field (<site address>, <apt number> <municipality>) from the CLEMIS CFS Report
    and returns the address number and street name.
    """

    f = field.split(' ')
    f_len = len(f)
    wl_check = f[f_len - 3] + ' ' + f[f_len - 2] + ' ' + f[f_len - 1]
    if f[f_len - 1] in cities:
        del f[-1]
    elif wl_check == 'WHITE LAKE TWP':
        del f[-3:]
    else:
        del f[-2:]
    a = ' '.join(f)
    if ',' in a:
        a = a.split(', ')
        a = a[0]
    a = a.replace(' NO ', ' & ')
    a = a.replace(' SO ', ' & ')
    a = a.title()
    return a


def split_apt(field):
    """
    Parses the ADDRESS field (<site address>, <apt number> <municipality>) from the CLEMIS CFS Report
    and returns the apartment number.
    """

    if ',' in field:
        f = field.split(', ')
        f = f[1]
        f = f.split(' ')
        apt = f[0]
    else:
        apt = None
    return apt


def split_city(field):
    """
    Parses the ADDRESS field (<site address>, <apt number> <municipality>) from the CLEMIS CFS Report
    and returns the city.
    """

    f = field.split(' ')
    f_len = len(f)
    wl_check = f[f_len - 3] + ' ' + f[f_len - 2] + ' ' + f[f_len - 1]
    if f[f_len - 1] in cities:
        city = f[f_len - 1]
    elif wl_check == 'WHITE LAKE TWP':
        city = 'WHITE LAKE TWP'
    else:
        city = f[f_len - 2] + ' ' + f[f_len - 1]
    city = city.replace('TWP', 'TOWNSHIP')
    city = city.title()
    return city


def inc_desc_correct(field):
    """
    Parses and corrects the OC CAD Incident Type Code.
    """

    f = field.upper()
    f = inc_desc_dict.get(f, f)
    if f == 'CO INVESTIGATION':
        f = 'CO Investigation'
    elif f == 'MABAS CALL':
        f = 'MABAS Call'
    else:
        f = f.title()
    return f
