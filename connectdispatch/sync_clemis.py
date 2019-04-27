#!/home/administrator/anaconda3/bin/python3

import pickle
import logging
from datetime import datetime, timedelta
import pytz
import re
from bs4 import BeautifulSoup
import requests
import config
import xmlutils
from clemis import clemis, timeutils

if config.use_cad_ws:
    # Get XML object containing the CLEMIS CAD incident data for the last 6 hours
    incident_tree = clemis.getxml(6)

    # Get lists of dictionaries for incidents and comments based on returned XML
    incident_list_full = xmlutils.xmltolist(incident_tree, 'Incident')
    unit_list_full = xmlutils.xmltolist(incident_tree, 'Unit')

    # Update incident_sync file
    incident_sync = []
    for i in incident_list_full:
        i = clemis.incidentlist_ws(i, unit_list_full)
        incident_sync.append(i)
        pass

    try:
        incident_sync_check = open(config.watch_dir + '/incident_sync/incident_sync.p', 'rb')
        incident_sync_check = pickle.load(incident_sync_check)
    except FileNotFoundError:
        incident_sync_check = open(config.watch_dir + '/incident_sync/incident_sync.p', 'w+b')

    # If the incident_list_full does not equal the previous incident_list_full, write the new version to file
    if incident_sync_check != incident_sync:
        file_incident_sync = open(config.watch_dir + '/incident_sync/incident_sync.p', 'wb')
        pickle.dump(incident_sync, file_incident_sync)
        file_incident_sync.close()
        # Log update
        logging.info('incident_sync updated by sync_clemis')
        pass
    pass
else:
    # Open email incident list file
    try:
        file_incident_list = open(config.watch_dir + '/clemis/email_incident_list/incident_list.p', 'rb')
        incident_list = pickle.load(file_incident_list)
    except FileNotFoundError:
        incident_list = []
    if incident_list:
        for i in incident_list:
            six_hrs_ago = datetime.now(pytz.utc) - timedelta(hours=6)
            if i['datetime_created'] < six_hrs_ago:

                # Construct variable for incident URL
                incident_temp_url = i['incident_temp_url']

                # Make Get request and parse HTML return with BeautifulSoup
                inc_page = requests.get(incident_temp_url)
                soup = BeautifulSoup(inc_page.text, 'html.parser')

                # Build lists from HTML tables
                inc_details = clemis.listfromtable(soup, 2)
                unit_details = clemis.listfromtable(soup, 3)
                comments = clemis.listfromtable(soup, 4)

                # Incident Number
                incident_number = inc_details[1][1]

                # Agency Code
                agency_code = inc_details[2][1]

                # Incident Type & Description
                inc_type_and_desc = inc_details[3][1]
                inc_type_and_desc = inc_type_and_desc.split(' ', 1)
                incident_type_code = inc_type_and_desc[0]
                incident_type_desc = inc_type_and_desc[1]
                incident_type_code = clemis.inc_code_correct(incident_type_code, incident_type_desc)
                incident_type_desc = clemis.inc_desc_correct(incident_type_desc)

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

                # Datetime created
                datetime_created = datetime.now(pytz.utc)

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
                chief_complaint = clemis.comment_search('CC:', comments)
                if not chief_complaint:
                    chief_complaint = ''
                    pass
                match = re.search(r'CC: (.*)', chief_complaint)
                chief_complaint = str(match.group(1) if match else None)
                chief_complaint = str(chief_complaint.strip()).title()

                # ProQA Code
                proqa_code = clemis.comment_search('DISPATCH CODE:', comments)
                if not proqa_code:
                    proqa_code = ''
                    pass
                match = re.search(r'DISPATCH CODE: (.*?)\(', proqa_code)
                proqa_code = str(match.group(1) if match else None)
                proqa_code = proqa_code.strip()

                # ProQA Suffix Code
                proqa_suffix_code = clemis.comment_search('SUFFIX:', comments)
                if not proqa_suffix_code:
                    proqa_suffix_code = ''
                    pass
                match = re.search(r'SUFFIX: (.*?)\(', proqa_suffix_code)
                proqa_suffix_code = str(match.group(1) if match else None)
                proqa_suffix_code = proqa_suffix_code.strip()

                # ProQA Code Description
                proqa_desc = clemis.comment_search('DISPATCH CODE:', comments)
                if not proqa_desc:
                    proqa_desc = ''
                    pass
                match = re.search(r'DISPATCH CODE:.*?\((.*)\)', proqa_desc)
                proqa_desc = str(match.group(1) if match else None)
                proqa_desc = str(proqa_desc.strip()).title()

                # ProQA Suffix Code Description
                proqa_suffix_desc = clemis.comment_search('SUFFIX:', comments)
                if not proqa_suffix_desc:
                    proqa_suffix_desc = ''
                    pass
                match = re.search(r'SUFFIX:.*?\((.*)\)', proqa_suffix_desc)
                proqa_suffix_desc = str(match.group(1) if match else None)
                proqa_suffix_desc = str(proqa_suffix_desc.strip()).title()

                # Incident Category
                incident_category = clemis.inc_cat_find(incident_type_desc)

                # Construct a list of incident dictionaries
                incident_sync = []
                incident_dict = {
                    'incident_number': incident_number,
                    'incident_type_code': incident_type_code,
                    'incident_type_desc': incident_type_desc,
                    'incident_category': incident_category,
                    'incident_temp_url': incident_temp_url,
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
                    'datetime_created': datetime_created,
                    'units_assigned': units_assigned,
                    'chief_complaint': chief_complaint,
                    'proqa_code': proqa_code,
                    'proqa_suffix_code': proqa_suffix_code,
                    'proqa_desc': proqa_desc,
                    'proqa_suffix_desc': proqa_suffix_desc,
                    'source_cad': 'clemis'
                }
                incident_sync.append(incident_dict)

                # Write new incident(s) to incident_push file
                file_incident_sync = open(config.watch_dir + '/incident_sync/incident_sync.p', 'wb')
                pickle.dump(incident_sync, file_incident_sync)
                file_incident_sync.close()
                pass
            else:
                del i
        # Write incident list to incident_list file
        file_incident_list = open(config.watch_dir + '/clemis/email_incident_list/incident_list.p', 'wb')
        pickle.dump(incident_list, file_incident_list)
        file_incident_list.close()
    pass
