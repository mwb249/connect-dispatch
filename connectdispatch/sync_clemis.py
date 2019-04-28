
import pickle
import logging
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import requests
import config
import xmlutils
from clemis import clemis

if config.use_cad_ws:
    # Get XML object containing the CLEMIS CAD incident data for the last 6 hours
    incident_tree = clemis.getxml(6)

    # Get lists of dictionaries for incidents and comments based on returned XML
    incident_list_full = xmlutils.xmltolist(incident_tree, 'Incident')
    unit_list_full = xmlutils.xmltolist(incident_tree, 'Unit')

    # Update incident_sync file
    incident_sync = []
    for i in incident_list_full:
        i = clemis.incidentdict_ws(i, unit_list_full)
        # TODO - Add code with boolean from config.py that adds incident_temp_url & location key/value pairs to dict
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
        incident_sync = []
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

                # Use incidentlist_email function to construct incident_push list
                incident_dict = clemis.incidentdict_email(inc_details, unit_details, comments, incident_temp_url)

                # Append incident_dict to incident_sync
                incident_sync.append(incident_dict)
                pass
            else:
                del i
                pass
            pass
        # Write new incident(s) to incident_sync file
        file_incident_sync = open(config.watch_dir + '/incident_sync/incident_sync.p', 'wb')
        pickle.dump(incident_sync, file_incident_sync)
        file_incident_sync.close()

        # Write incident list to incident_list file
        file_incident_list = open(config.watch_dir + '/clemis/email_incident_list/incident_list.p', 'wb')
        pickle.dump(incident_list, file_incident_list)
        file_incident_list.close()
    pass
