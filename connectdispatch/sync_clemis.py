#!/home/administrator/anaconda3/bin/python3

import pickle
import logging
import config
import xmlutils
from clemis import clemis

# Get XML object containing the CLEMIS CAD incident data for the last 6 hours
incident_tree = clemis.getxml(6)

# Get lists of dictionaries for incidents and comments based on returned XML
incident_list_full = xmlutils.xmltolist(incident_tree, 'Incident')
unit_list_full = xmlutils.xmltolist(incident_tree, 'Unit')

# Update incident_sync file
incident_sync = []
for i in incident_list_full:
    i = clemis.inc_list_correct(i, unit_list_full)
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
    logging.info('incident_sync updated by webservice_clemis')
    pass
