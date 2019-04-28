
"""Connect|DISPATCH: Connecting Computer-Aided Dispatch (CAD) Systems to ArcGIS.
The webservice_clemis script polls the CLEMIS CAD web service. When any update occurs, new data is written to files.
From there it is detected and managed by other scripts."""

__author__ = 'Doreen Groth and Mark Brown'
__email__ = 'support@connect-geo.com'
__copyright__ = 'Copyright (c) 2019, Connect Geospatial Solutions, LLC - All Rights Reserved'
__license__ = '''You may use, distribute, and modify this code under the terms of the Connect|DISPATCH On-Premises 
Deployment license. You should have received a copy of the Connect|DISPATCH On-Premises Deployment license with this 
file. If not, please email: support@connect-geo.com'''
__version__ = '1.1.0'
__status__ = 'Production'

import logging
import pickle
import config
import xmlutils
from clemis import clemis

# Logging
logging.basicConfig(filename='clemis.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Get XML object containing the CLEMIS CAD incident data for the last 6 hours
incident_tree = clemis.getxml(6)

# Get incident list (agency_code & incident_number)
incident_list = clemis.incidentlist(incident_tree)

# Open previous incident list
try:
    incident_list_check = open(config.watch_dir + '/clemis/ws_incident_list/incident_list.p', 'rb')
    incident_list_check = pickle.load(incident_list_check)
except FileNotFoundError:
    incident_list_check = open(config.watch_dir + '/clemis/ws_incident_list/incident_list.p', 'w+b')

# If incident list does not equal previous incident list, write the new version to file
if incident_list_check != incident_list:
    file_incident_list = open(config.watch_dir + '/clemis/ws_incident_list/incident_list.p', 'wb')
    pickle.dump(incident_list, file_incident_list)
    file_incident_list.close()
    pass

# Compare incident lists, return a list of 'new' incidents
incident_list_new = clemis.comparelists(incident_list, incident_list_check)

# Get lists of dictionaries for incidents and comments based on returned XML
incident_list_full = xmlutils.xmltolist(incident_tree, 'Incident')
unit_list_full = xmlutils.xmltolist(incident_tree, 'Unit')

# If there are 'new' incident(s), generate a list of dictionaries and write to incident_push file
incident_push = []
if incident_list_new:
    for i in incident_list_full:
        for new in incident_list_new:
            if i['incident_number'] == new['incident_number']:
                i = clemis.incidentdict_ws(i, unit_list_full, push=True)
                incident_push.append(i)
                pass
            pass
        pass
    # Write new incident(s) to incident_push file
    file_incident_push = open(config.watch_dir + '/incident_push/incident_push.p', 'wb')
    pickle.dump(incident_push, file_incident_push)
    file_incident_push.close()
    # Log update
    logging.info('incident_push updated by webservice_clemis')
    pass
