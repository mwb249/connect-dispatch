"""To be completed..."""

import logging
import os
import yaml
import pickle
import csv
from arcgis.gis import GIS
from arcgis.geocoding import Geocoder, geocode
from arcgis.geometry import filters, Point
from pyproj import Proj, transform
import mgrs
from copy import deepcopy

# Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Directories
cwd = os.getcwd()
watch_dir = cwd + '/watch'
config_dir = cwd + '/config'

# Open config file, construct clemis object
with open(config_dir + '/config.yaml', 'r') as yamlfile:
    cfg = yaml.load(yamlfile)

# Open incident_sync file
file_incident_sync = open('/incident_sync/incident_sync.p', 'rb')
incident_sync = pickle.load(file_incident_sync)

# Agency codes dictionary
file_agency_codes = csv.DictReader(open(cwd + '/config/agency_codes.csv'))
agency_codes = {rows['agency_code']: rows['city_desc'] for rows in file_agency_codes}

for i in incident_sync:
    for agency in cfg['agencies'].keys():
        if i['agency_code'] == cfg['agencies'][agency]['agency_code']:
            # Construct Web GIS objects
            ago_portal = cfg['agencies'][agency]['ago_portal']
            ago_user = cfg['agencies'][agency]['ago_user']
            ago_pass = cfg['agencies'][agency]['ago_pass']
            gis = GIS(ago_portal, ago_user, ago_pass)

            # Construct feature layer objects
            flc_fireincidents = gis.content.get(cfg['agencies'][agency]['flc_fireincidents'])
            fl_fireincidents = flc_fireincidents.layers[0]

            # Query feature layer to find any active incidents
            fset_fireincidents = fl_fireincidents.query(where='datetime_clear IS NULL')
            if not fset_fireincidents:
                pass
