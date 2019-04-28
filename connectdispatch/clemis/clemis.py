"""
The clemis module contains functions related to obtaining and manipulating incident data received through the CLEMIS
CAD web service or D-Card web page.
"""

from datetime import datetime, timedelta
import pytz
import requests
import re
import config
import xmlutils
from clemis import timeutils
from xml.etree import ElementTree


def getxml(hrs):
    """
    Makes a SOAP request to CLEMIS CAD web service and returns an XML object containing the CAD incident data for the
    past number of hours specified in the parameters.
    """

    # Get datetime string for the specified previous hours
    time = datetime.now() - timedelta(hours=hrs)
    last_update_datetime = time.strftime('%Y%m%d%H%M%S')

    # Headers
    headers = {'content-type': 'application/soap+xml; charset=utf-8'}

    # Body
    body1 = '''<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
      <soap12:Body>
        <getIncidentDataByLastUpdatedDate xmlns="http://tempuri.org/">
          <sUserName>'''
    body2 = '''</sUserName>
          <sPassword>'''
    body3 = '''</sPassword>
          <sStartDate>'''
    body4 = '''</sStartDate>
          <sEndDate></sEndDate>
          <sAgencyCd></sAgencyCd>
        </getIncidentDataByLastUpdatedDate>
      </soap12:Body>
    </soap12:Envelope>'''
    body = body1 + config.cad_user_clemis + body2 + config.cad_pass_clemis + body3 + last_update_datetime + body4

    # Request
    r = requests.post(config.cad_url_clemis, data=body, headers=headers, timeout=2)

    # Parse XML return with ElementTree
    full_xml = ElementTree.fromstring(r.content)
    xmlutils.strip_xml_ns(full_xml)
    return full_xml


def incidentlist(xml):
    """
    Takes the full incident XML and returns a list of dictionaries with 'agency code' and 'incident number' tag and
    text elements.
    """
    i_list = []
    for i in xml.iter('Incident'):
        i_dict = dict()
        i_dict['agency_code'] = i[2].text
        i_dict['incident_number'] = i[3].text
        i_list.append(i_dict)
    return i_list


def comparelists(i_list, i_list_check):
    """
    Compares current and previous incident lists and returns a list of dictionaries with incidents not found in the
    previous list.
    """
    new_i_list = []
    for i in i_list:
        if i not in i_list_check:
            new_i_list.append(i)
    return new_i_list


def listfromtable(s, index):
    table = s.find_all('table')[index]
    table_rows = table.find_all('tr')
    table_list = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        table_list.append(row)
    return table_list


def comment_search(search_str, comments):
    for l in comments:
        for i in l:
            if search_str in i:
                return i


def inc_code_correct(inc_type_code, inc_type_desc):
    """
    Parses and corrects OC CAD Incident Type Description.
    """
    if inc_type_code == 'BOX_CO':
        inc_type_code = 'BOX_COM'
    elif inc_type_code == 'BOX_RE':
        inc_type_code = 'BOX_RES'
    elif inc_type_code == 'FULL_C':
        inc_type_code = 'FULL_COM'
    elif inc_type_code == 'FULL_R':
        inc_type_code = 'FULL_RES'
    elif inc_type_desc == 'COMMERCIAL FIRE STIL':
        inc_type_code = 'STILL_COM'
    elif inc_type_desc == 'RESD FIRE STILL RESP':
        inc_type_code = 'STILL_RES'
    elif inc_type_code == 'WATERE':
        inc_type_code = 'WATERES'
    else:
        pass
    return inc_type_code


def inc_desc_correct(inc_type_desc):
    """
    Parses and corrects the OC CAD Incident Type Code.
    """
    if inc_type_desc == 'COMMERCIAL FIRE BOX':
        inc_type_desc = 'COMMERCIAL FIRE (BOX ALARM)'
    elif inc_type_desc == 'RESIDENTIAL FIRE BOX':
        inc_type_desc = 'RESIDENTIAL FIRE (BOX ALARM)'
    elif inc_type_desc == 'FIRE ALARM COMMERCIA':
        inc_type_desc = 'COMMERCIAL FIRE ALARM'
    elif inc_type_desc == 'FIRE ALARM RESIDENTI':
        inc_type_desc = 'RESIDENTIAL FIRE ALARM'
    elif inc_type_desc == 'COMMERCIAL FIRE FULL':
        inc_type_desc = 'COMMERCIAL FIRE (FULL RESPONSE)'
    elif inc_type_desc == 'RESIDENTIAL FIRE FUL':
        inc_type_desc = 'RESIDENTIAL FIRE (FULL RESPONSE)'
    elif inc_type_desc == 'GASLK':
        inc_type_desc = 'GAS LEAK'
    elif inc_type_desc == 'MEDICAL OMEGA':
        inc_type_desc = 'OMEGA MEDICAL'
    elif inc_type_desc == 'HOSP TRANSFER':
        inc_type_desc = 'HOSPITAL TRANSFER'
    elif inc_type_desc == 'MUTAID':
        inc_type_desc = 'MUTUAL-AID'
    elif inc_type_desc == 'PIA':
        inc_type_desc = 'INJURY ACCIDENT'
    elif inc_type_desc == 'RESIDENTIAL STRUCTUR':
        inc_type_desc = 'RESIDENTIAL STRUCTURE FIRE'
    elif inc_type_desc == 'COMMERCIAL STRUCTURE':
        inc_type_desc = 'COMMERCIAL STRUCTURE FIRE'
    elif inc_type_desc == 'COMMERCIAL FIRE STIL':
        inc_type_desc = 'COMMERCIAL FIRE (STILL RESPONSE)'
    elif inc_type_desc == 'RESD FIRE STILL RESP':
        inc_type_desc = 'RESIDENTIAL FIRE (STILL RESPONSE)'
    else:
        pass
    if inc_type_desc == 'CO INVESTIGATION':
        inc_type_desc = 'CO Investigation'
    else:
        inc_type_desc = inc_type_desc.title()
    return inc_type_desc


def inc_cat_find(inc_type_desc):
    """
    Determines the incident category based on the incident type description.
    """
    fire = ['Residential Structure Fire', 'Commercial Structure Fire', 'Residential Fire (Full Response)',
            'Commercial Fire (Full Response)', 'Residential Fire (Box Alarm)', 'Commercial Fire (Box Alarm)',
            'Vehicle Fire', 'Residential Fire (Still Response)']
    fire_alarm = ['Commercial Fire Alarm', 'Residential Fire Alarm']
    fire_hazard = ['Burning Complaint', 'Gas Leak', 'Outdoor Fire/Other', 'Smoke Investigation', 'Odor Investigation']
    injury_accident = ['Injury Accident']
    medical = ['Alpha Medical', 'Bravo Medical', 'Charlie Medical', 'Delta Medical', 'Echo Medical', 'Omega Medical',
               'Medical Emergency', 'Medical Alarm']
    assist_citizen = ['Assist Citizen', 'Lift Assist']
    haz_condition = ['Tree Down', 'CO Investigation', 'Wires Down', 'Fuel Spill', 'Technical Rescue',
                     'Road Hazard Fire']
    mutaid = ['Mutual-Aid']
    police_assist = ['Police Assist']
    if inc_type_desc in fire:
        category = 'Fire'
    elif inc_type_desc in fire_alarm:
        category = 'Fire Alarm'
    elif inc_type_desc in fire_hazard:
        category = 'Fire Hazard'
    elif inc_type_desc in injury_accident:
        category = 'Injury Accident'
    elif inc_type_desc in medical:
        category = 'Medical'
    elif inc_type_desc in assist_citizen:
        category = 'Assist Citizen'
    elif inc_type_desc in haz_condition:
        category = 'Hazardous Condition'
    elif inc_type_desc in mutaid:
        category = 'Mutual-Aid'
    elif inc_type_desc in police_assist:
        category = 'Police Assist'
    else:
        category = 'Other'
    return category


def incidentlist_ws(i_dict, unit_list, push=False):
    """
    This function takes a 'raw' incident dictionary and unit list XML tree from the CLEMIS web service, and returns a
    modified version of the incident dictionary. The 'push' boolean parameter specifies whether the list will be used
    in a 'push' capacity (certain key/value pairs are only pushed to the GIS during the initial append).
    """
    # Correct incident_type_code and incident_type_desc
    i_dict['incident_type_desc'] = i_dict.pop('incident_type_description')
    incident_type_code = i_dict['incident_type_code']
    incident_type_desc = i_dict['incident_type_desc']
    i_dict['incident_type_code'] = inc_code_correct(incident_type_code, incident_type_desc)
    i_dict['incident_type_desc'] = inc_desc_correct(incident_type_desc)

    # Update keys
    i_dict['address'] = i_dict.pop('incident_address')
    i_dict['apt_number'] = i_dict.pop('apartment_number')
    i_dict['city_desc'] = i_dict.pop('incident_city_name')
    i_dict['state'] = i_dict.pop('incident_state_code')
    i_dict['low_street'] = i_dict.pop('low_xstreet')
    i_dict['high_street'] = i_dict.pop('high_xstreet')
    i_dict['datetime_call'] = i_dict.pop('call_date')
    i_dict['datetime_clear'] = i_dict.pop('clear_date')

    # Remove unnecessary key/value pairs
    i_dict.pop('incident_city_code')
    i_dict.pop('caller_name')
    i_dict.pop('caller_phone_number')
    i_dict.pop('operator_name')
    i_dict.pop('mapindex')
    i_dict.pop('Incident')
    i_dict.pop('Units')
    i_dict.pop('Unit')
    i_dict.pop('unit_area_code')
    i_dict.pop('unit_code')
    i_dict.pop('unit_dispatch_date')
    i_dict.pop('unit_enroute_date')
    i_dict.pop('unit_enroute_hospital_date')
    i_dict.pop('unit_arrive_date')
    i_dict.pop('unit_arrive_hospital_date')
    i_dict.pop('unit_clear_date')
    i_dict.pop('Comments')
    i_dict.pop('Comment')

    # Add key/value pairs that are only available through the email push
    i_dict['incident_temp_url'] = None
    i_dict['location'] = None

    # Incident category
    i_dict['incident_category'] = inc_cat_find(i_dict['incident_type_desc'])

    # Call datetime
    i_dict['datetime_call'] = timeutils.incident_dt_ws(i_dict['datetime_call'])

    # Dispatch datetime
    i_dict['datetime_dispatched'] = timeutils.unit_dt_from_dict(unit_list, i_dict, 'unit_dispatch_date')

    # En Route datetime
    i_dict['datetime_enroute'] = timeutils.unit_dt_from_dict(unit_list, i_dict, 'unit_enroute_date')

    # Arrival datetime
    i_dict['datetime_arrival'] = timeutils.unit_dt_from_dict(unit_list, i_dict, 'unit_arrive_date')

    # Clear datetime
    i_dict['datetime_clear'] = timeutils.incident_dt_ws(i_dict['datetime_clear'])

    # Chief Complaint
    match = re.search(r'CC: (.*)', i_dict['comments_text'])
    chief_complaint = str(match.group(1) if match else None)
    i_dict['chief_complaint'] = str(chief_complaint.strip()).title()

    # ProQA Code
    match = re.search(r'DISPATCH CODE: (.*?)\(', i_dict['comments_text'])
    proqa_code = str(match.group(1) if match else None)
    i_dict['proqa_code'] = proqa_code.strip()

    # Proqa Suffix Code
    match = re.search(r'SUFFIX: (.*?)\(', i_dict['comments_text'])
    proqa_suffix_code = str(match.group(1) if match else None)
    i_dict['proqa_suffix_code'] = proqa_suffix_code.strip()

    # ProQA Description
    match = re.search(r'DISPATCH CODE:.*?\((.*)\)', i_dict['comments_text'])
    proqa_desc = str(match.group(1) if match else None)
    i_dict['proqa_desc'] = str(proqa_desc.strip()).title()

    # ProQA Suffix description
    match = re.search(r'SUFFIX:.*?\((.*)\)', i_dict['comments_text'])
    proqa_suffix_desc = str(match.group(1) if match else None)
    i_dict['proqa_suffix_desc'] = str(proqa_suffix_desc.strip()).title()

    # Remove 'comments_text' key/value
    i_dict.pop('comments_text')

    # Push only key/values
    if push:
        # Source CAD system
        i_dict['source_cad'] = 'clemis'
        # Created datetime
        i_dict['datetime_created'] = datetime.now(pytz.utc)
    return i_dict


def incidentdict_email(inc_details, unit_details, comments, inc_url, push=False):
    """
    This function takes the three sections of a CLEMIS D-Card along with the incident URL, and returns an incident
    dictionary. The 'push' boolean parameter specifies whether the list will be used in a 'push' capacity (certain
    key/value pairs are only pushed to the GIS during the initial append).
    """
    # Incident Number
    incident_number = inc_details[1][1]

    # Agency Code
    agency_code = inc_details[2][1]

    # Incident Type & Description
    inc_type_and_desc = inc_details[3][1]
    inc_type_and_desc = inc_type_and_desc.split(' ', 1)
    incident_type_code = inc_type_and_desc[0]
    incident_type_desc = inc_type_and_desc[1]
    incident_type_code = inc_code_correct(incident_type_code, incident_type_desc)
    incident_type_desc = inc_desc_correct(incident_type_desc)

    # Address
    inc_address_full = inc_details[4][1]
    inc_address_list = inc_address_full.split(', ', 1)
    address = inc_address_list[0].title()
    # Remove 'Apt' from Address, if necessary
    if 'Apt' in address:
        match = re.search(r'(.*) Apt', address)
        address = str(match.group(1) if match else None)
        pass

    # Apt Number
    match = re.search(r'apt(.*),', inc_address_full, flags=re.IGNORECASE)
    apt_number = str(match.group(1) if match else None)
    apt_number = apt_number.strip()

    # Location
    location = inc_details[5][1]

    # City Description
    inc_address_list = inc_address_full.split(', ', 1)
    city_desc = inc_address_list[1].title()
    # Remove State from City Description, if necessary
    if 'Mi' in city_desc:
        match = re.search(r'(.*) Mi', city_desc)
        city_desc = str(match.group(1) if match else None)
        pass

    # State
    state = ''
    for agency_dict in config.agency_list:
        if agency_dict['agency_code'] == agency_code:
            state = agency_dict['state_code']
        else:
            state = None

    # Incident Times
    datetime_call = timeutils.incident_dt_email(inc_details[6][1])
    datetime_dispatched = timeutils.incident_dt_email(inc_details[7][1])
    datetime_enroute = timeutils.incident_dt_email(inc_details[8][1])
    datetime_arrival = timeutils.incident_dt_email(inc_details[9][1])
    datetime_clear = timeutils.incident_dt_email(inc_details[10][1])

    # Units Assigned
    units_assigned = []
    for unit in unit_details:
        try:
            unit = unit[0]
            units_assigned.append(unit)
        except IndexError:
            pass
    units_assigned = ' '.join(units_assigned)

    # Chief Complaint
    chief_complaint = comment_search('CC:', comments)
    if not chief_complaint:
        chief_complaint = ''
        pass
    match = re.search(r'CC: (.*)', chief_complaint)
    chief_complaint = str(match.group(1) if match else None)
    chief_complaint = str(chief_complaint.strip()).title()

    # ProQA Code
    proqa_code = comment_search('DISPATCH CODE:', comments)
    if not proqa_code:
        proqa_code = ''
        pass
    match = re.search(r'DISPATCH CODE: (.*?)\(', proqa_code)
    proqa_code = str(match.group(1) if match else None)
    proqa_code = proqa_code.strip()

    # ProQA Suffix Code
    proqa_suffix_code = comment_search('SUFFIX:', comments)
    if not proqa_suffix_code:
        proqa_suffix_code = ''
        pass
    match = re.search(r'SUFFIX: (.*?)\(', proqa_suffix_code)
    proqa_suffix_code = str(match.group(1) if match else None)
    proqa_suffix_code = proqa_suffix_code.strip()

    # ProQA Code Description
    proqa_desc = comment_search('DISPATCH CODE:', comments)
    if not proqa_desc:
        proqa_desc = ''
        pass
    match = re.search(r'DISPATCH CODE:.*?\((.*)\)', proqa_desc)
    proqa_desc = str(match.group(1) if match else None)
    proqa_desc = str(proqa_desc.strip()).title()

    # ProQA Suffix Code Description
    proqa_suffix_desc = comment_search('SUFFIX:', comments)
    if not proqa_suffix_desc:
        proqa_suffix_desc = ''
        pass
    match = re.search(r'SUFFIX:.*?\((.*)\)', proqa_suffix_desc)
    proqa_suffix_desc = str(match.group(1) if match else None)
    proqa_suffix_desc = str(proqa_suffix_desc.strip()).title()

    # Incident Category
    incident_category = inc_cat_find(incident_type_desc)

    # Construct an incident dictionary
    i_dict = {
        'incident_number': incident_number,
        'incident_type_code': incident_type_code,
        'incident_type_desc': incident_type_desc,
        'incident_category': incident_category,
        'incident_temp_url': inc_url,
        'agency_code': agency_code,
        'address': address,
        'location': location,
        'apt_number': apt_number,
        'city_desc': city_desc,
        'state': state,
        'low_street': None,
        'high_street': None,
        'datetime_call': datetime_call,
        'datetime_dispatched': datetime_dispatched,
        'datetime_enroute': datetime_enroute,
        'datetime_arrival': datetime_arrival,
        'datetime_clear': datetime_clear,
        'units_assigned': units_assigned,
        'chief_complaint': chief_complaint,
        'proqa_code': proqa_code,
        'proqa_suffix_code': proqa_suffix_code,
        'proqa_desc': proqa_desc,
        'proqa_suffix_desc': proqa_suffix_desc
    }
    # Push only additional key/values
    if push:
        # Created datetime
        i_dict['datetime_created'] = datetime.now(pytz.utc)
        # Source CAD system
        i_dict['source_cad'] = 'clemis'
        pass
    return i_dict
