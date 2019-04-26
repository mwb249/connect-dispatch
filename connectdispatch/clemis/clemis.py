"""The clemis module contains functions related to obtaining and manipulating incident data received through the CLEMIS
CAD web service."""

import datetime
import requests
import re
import config
import xmlutils
from clemis import timeutils
from xml.etree import ElementTree


def getxml(hrs):
    """Makes a SOAP request to CLEMIS CAD web service and returns an XML object containing the CAD incident data for the
    past number of hours specified in the parameters."""

    # Get datetime string for the specified previous hours
    time = datetime.datetime.now() - datetime.timedelta(hours=hrs)
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
    """Takes the full incident XML and returns a list of dictionaries with 'agency code' and 'incident number' tag and
    text elements."""
    i_list = []
    for i in xml.iter('Incident'):
        i_dict = dict()
        i_dict['agency_code'] = i[2].text
        i_dict['incident_number'] = i[3].text
        i_list.append(i_dict)
    return i_list


def comparelists(i_list, i_list_check):
    """Compares current and previous incident lists and returns a list of dictionaries with incidents not found in the
    previous list."""
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
    """Parses and corrects OC CAD Incident Type Description."""
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
    """Parses and corrects the OC CAD Incident Type Code."""
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
    """Determines the incident category based on the incident type description."""
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


def inc_list_correct(inc_dict, unit_list):
    """
    Correct a list of incident dictionaries.
    """
    # Correct incident_type_code and incident_type_desc
    inc_dict['incident_type_desc'] = inc_dict.pop('incident_type_description')
    incident_type_code = inc_dict['incident_type_code']
    incident_type_desc = inc_dict['incident_type_desc']
    inc_dict['incident_type_code'] = inc_code_correct(incident_type_code, incident_type_desc)
    inc_dict['incident_type_desc'] = inc_desc_correct(incident_type_desc)

    # Update keys
    inc_dict['address'] = inc_dict.pop('incident_address')
    inc_dict['apt_number'] = inc_dict.pop('apartment_number')
    inc_dict['city_desc'] = inc_dict.pop('incident_city_name')
    inc_dict['state'] = inc_dict.pop('incident_state_code')
    inc_dict['low_street'] = inc_dict.pop('low_xstreet')
    inc_dict['high_street'] = inc_dict.pop('high_xstreet')
    inc_dict['datetime_call'] = inc_dict.pop('call_date')
    inc_dict['datetime_clear'] = inc_dict.pop('clear_date')

    # Remove unnecessary key/value pairs
    inc_dict.pop('incident_city_code')
    inc_dict.pop('caller_name')
    inc_dict.pop('caller_phone_number')
    inc_dict.pop('operator_name')
    inc_dict.pop('mapindex')
    inc_dict.pop('Incident')
    inc_dict.pop('Units')
    inc_dict.pop('Unit')
    inc_dict.pop('unit_area_code')
    inc_dict.pop('unit_code')
    inc_dict.pop('unit_dispatch_date')
    inc_dict.pop('unit_enroute_date')
    inc_dict.pop('unit_enroute_hospital_date')
    inc_dict.pop('unit_arrive_date')
    inc_dict.pop('unit_arrive_hospital_date')
    inc_dict.pop('unit_clear_date')
    inc_dict.pop('Comments')
    inc_dict.pop('Comment')

    # Add key/value pairs that are only available through the email push
    inc_dict['incident_temp_url'] = None
    inc_dict['location'] = None

    # Incident category
    inc_dict['incident_category'] = inc_cat_find(inc_dict['incident_type_desc'])

    # Call datetime
    inc_dict['datetime_call'] = timeutils.incident_dt_ws(inc_dict['datetime_call'])

    # Dispatch datetime
    inc_dict['datetime_dispatched'] = timeutils.unit_dt_from_dict(unit_list, inc_dict, 'unit_dispatch_date')

    # En Route datetime
    inc_dict['datetime_enroute'] = timeutils.unit_dt_from_dict(unit_list, inc_dict, 'unit_enroute_date')

    # Arrival datetime
    inc_dict['datetime_arrival'] = timeutils.unit_dt_from_dict(unit_list, inc_dict, 'unit_arrive_date')

    # Clear datetime
    inc_dict['datetime_clear'] = timeutils.incident_dt_ws(inc_dict['datetime_clear'])

    # Chief Complaint
    match = re.search(r'CC: (.*)', inc_dict['comments_text'])
    chief_complaint = str(match.group(1) if match else None)
    inc_dict['chief_complaint'] = str(chief_complaint.strip()).title()

    # ProQA Code
    match = re.search(r'DISPATCH CODE: (.*?)\(', inc_dict['comments_text'])
    proqa_code = str(match.group(1) if match else None)
    inc_dict['proqa_code'] = proqa_code.strip()

    # Proqa Suffix Code
    match = re.search(r'SUFFIX: (.*?)\(', inc_dict['comments_text'])
    proqa_suffix_code = str(match.group(1) if match else None)
    inc_dict['proqa_suffix_code'] = proqa_suffix_code.strip()

    # ProQA Description
    match = re.search(r'DISPATCH CODE:.*?\((.*)\)', inc_dict['comments_text'])
    proqa_desc = str(match.group(1) if match else None)
    inc_dict['proqa_desc'] = str(proqa_desc.strip()).title()

    # ProQA Suffix description
    match = re.search(r'SUFFIX:.*?\((.*)\)', inc_dict['comments_text'])
    proqa_suffix_desc = str(match.group(1) if match else None)
    inc_dict['proqa_suffix_desc'] = str(proqa_suffix_desc.strip()).title()

    # Remove 'comments_text' key/value
    inc_dict.pop('comments_text')
    return inc_dict
