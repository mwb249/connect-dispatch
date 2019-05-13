"""To be completed..."""

import logging
import os
import yaml
import pickle
import csv
from arcgis.gis import GIS

# Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Directories
cwd = os.getcwd()
watch_dir = cwd + '/watch'
config_dir = cwd + '/config'

# Open config file, construct clemis object
with open(config_dir + '/config.yml', 'r') as yamlfile:
    cfg = yaml.load(yamlfile)

# Open incident_sync file
file_incident_sync = open(watch_dir + '/incident_sync/incident_sync.p', 'rb')
incident_sync = pickle.load(file_incident_sync)

# Agency codes dictionary
file_agency_codes = csv.DictReader(open(config_dir + '/agency_codes.csv'))
agency_codes = {rows['agency_code']: rows['city_desc'] for rows in file_agency_codes}

for i in incident_sync:
    for agency in cfg['agencies'].keys():
        if i['agency_code'] == cfg['agencies'][agency]['agency_code']:
            # Assign variable to web GIS
            ago_portal = cfg['agencies'][agency]['ago_portal']
            ago_user = cfg['agencies'][agency]['ago_user']
            ago_pass = cfg['agencies'][agency]['ago_pass']
            gis = GIS(ago_portal, ago_user, ago_pass)

            # Assign variable to feature layer
            fl_fireincidents = gis.content.get(cfg['agencies'][agency]['flc_fireincidents']).layers[0]

            # Query feature layer to find any active incidents
            fset_fireincidents = fl_fireincidents.query(where='datetime_clear IS NULL')
            if not fset_fireincidents:
                pass
            else:
                features_to_update = []
                for f in fset_fireincidents:
                    if i['incident_number'] == f.attributes['incident_number']:
                        f.attributes['incident_type_code'] = i['incident_type_code']
                        f.attributes['incident_type_desc'] = i['incident_type_desc']
                        f.attributes['incident_temp_url'] = i['incident_temp_url']
                        f.attributes['address'] = i['address']
                        f.attributes['location'] = i['location']
                        f.attributes['apt_number'] = i['apt_number']
                        f.attributes['city_code'] = i['city_code']
                        f.attributes['city_desc'] = i['city_desc']
                        f.attributes['state'] = ['state']
                        f.attributes['map_index'] = i['map_index']
                        f.attributes['low_street'] = i['low_street']
                        f.attributes['high_street'] = i['high_street']
                        f.attributes['datetime_call'] = i['datetime_call']
                        f.attributes['datetime_dispatched'] = i['datetime_dispatched']
                        f.attributes['datetime_enroute'] = i['datetime_enroute']
                        f.attributes['datetime_arrival'] = i['datetime_arrival']
                        f.attributes['datetime_clear'] = i['datetime_clear']
                        f.attributes['units_assigned'] = i['incident_units']
                        f.attributes['chief_complaint'] = i['chief_complaint']
                        f.attributes['proqa_code'] = i['proqa_code']
                        f.attributes['proqa_suffix_code'] = i['proqa_code_suf']
                        f.attributes['proqa_desc'] = i['proqa_desc']
                        f.attributes['proqa_suffix_desc'] = i['proqa_desc_suf']
                        features_to_update.append(f)
                        pass
                    pass
                fl_fireincidents.edit_features(updates=features_to_update)
