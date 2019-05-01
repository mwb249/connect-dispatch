"""
Connect|DISPATCH: Connecting Computer-Aided Dispatch (CAD) Systems to ArcGIS.

The push_clemis_email script ...
"""

import connectdispatch
import logging
import os
import sys
import re
import requests
from bs4 import BeautifulSoup
import email
import pickle

# Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Directories
cwd = os.getcwd()
watch_dir = cwd + '/watch'

# Assign variable to email message and subject
msg = email.message_from_file(sys.stdin)
subject = msg['Subject']

# Parse incident URL from email subject
match = re.search(r'(https://.*?/.*?/.*?)/', subject)
incident_temp_url = str(match.group(1) if match else None)
incident_temp_url = incident_temp_url.strip()

# Make Get request and parse HTML return with BeautifulSoup
inc_page = requests.get(incident_temp_url)
soup = BeautifulSoup(inc_page.text, 'html.parser')

# Build lists from HTML tables
inc_details = connectdispatch.clemis.listfromtable(soup, 2)
unit_details = connectdispatch.clemis.listfromtable(soup, 3)
comments = connectdispatch.clemis.listfromtable(soup, 4)

# Construct empty incident_push list
incident_push = []

# Use incidentlist_email function to construct incident_push list
incident_dict = connectdispatch.clemis.incidentdict_email(inc_details, unit_details, comments, incident_temp_url,
                                                          push=True)

# Append incident_dict to incident_push
incident_push.append(incident_dict)

# Write new incident to incident_push file
file_incident_push = open(watch_dir + '/incident_push/incident_push.p', 'wb')
pickle.dump(incident_push, file_incident_push)
file_incident_push.close()
# Log update
logging.info('incident_push updated by email_clemis')

# Append new incident to email_incident_list (subset of key/value pairs)
try:
    file_incident_list = open(watch_dir + '/clemis/email_incident_list/incident_list.p', 'rb')
    incident_list = pickle.load(file_incident_list)
except FileNotFoundError:
    incident_list = []

# Construct 'new' incident subset dictionary
incident_list_dict = dict()
incident_list_dict['agency_code'] = incident_dict['agency_code']
incident_list_dict['incident_number'] = incident_dict['incident_number']
incident_list_dict['incident_temp_url'] = incident_dict['incident_temp_url']
incident_list_dict['datetime_created'] = incident_dict['datetime_created']
incident_list_dict['location'] = incident_dict['location']
incident_list.append(incident_list_dict)

# Write incident list to file
file_incident_list = open(watch_dir + '/clemis/email_incident_list/incident_list.p', 'wb')
pickle.dump(incident_list, file_incident_list)
file_incident_list.close()
