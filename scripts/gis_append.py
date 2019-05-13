"""To be completed..."""

from connectdispatch import fireops
import logging
import os
import yaml
import pickle
import csv
import mgrs
from datetime import datetime
from arcgis.gis import GIS
from arcgis.geocoding import Geocoder, geocode
from arcgis.geometry import filters, Point
from pyproj import Proj, transform
from copy import deepcopy

# Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Directories
cwd = os.getcwd()
watch_dir = cwd + '/watch'
config_dir = cwd + '/config'

# Open config file
with open(config_dir + '/config.yml', 'r') as yamlfile:
    cfg = yaml.load(yamlfile)

# Open incident push file
file_incident_push = open(watch_dir + '/incident_push/incident_push.p', 'rb')
incident_push = pickle.load(file_incident_push)

# Open agency codes table
file_agency_codes = csv.DictReader(open(config_dir + '/agency_codes.csv'))
agency_codes = {rows['agency_code']: rows['city_desc'] for rows in file_agency_codes}

# Define projections
mi_south = Proj(init='epsg:3593', preserve_units=True)  # NAD 1983 StatePlane Michigan South, FIPS 2113 IntlFeet
web_mercator = Proj(init='epsg:3857')  # WGS 1984 Web Mercator Auxiliary Sphere
wgs84 = Proj(init='epsg:4326')  # WGS84

for i in incident_push:
    for agency in cfg['agencies'].keys():
        if i['agency_code'] == cfg['agencies'][agency]['agency_code']:
            # Create/assign web GIS variable
            ago_portal = cfg['agencies'][agency]['ago_portal']
            ago_user = cfg['agencies'][agency]['ago_user']
            ago_pass = cfg['agencies'][agency]['ago_pass']
            gis = GIS(ago_portal, ago_user, ago_pass)

            # Create/assign feature layer variables
            fl_fireincidents = gis.content.get(cfg['agencies'][agency]['flc_fireincidents']).layers[0]
            fl_serviceareas = gis.content.get(cfg['agencies'][agency]['flc_serviceareas']).layers[0]
            fl_firedistricts = gis.content.get(cfg['agencies'][agency]['flc_firedistricts']).layers[0]
            fl_boxalarmareas = gis.content.get(cfg['agencies'][agency]['flc_boxalarmareas']).layers[0]
            fl_taxparcels = gis.content.get(cfg['agencies'][agency]['flc_taxparcels']).layers[0]

            # If incident is mutual-aid, find agency_code
            mutaid_agency_code = ''
            if i['inc_type_code'] == 'MUTAID':
                if i['city_desc'] == agency_codes['city_desc']:
                    mutaid_agency_code = agency_codes['agency_code']
                else:
                    mutaid_agency_code = i['agency_code']

            # Query feature layer and create search extent dictionary
            if i['inc_type_code'] == 'MUTAID':
                where_statement = i['agency_code'] + " LIKE '" + mutaid_agency_code + "'"
            else:
                where_statement = i['agency_code'] + " LIKE '" + i['agency_code'] + "'"
            f_servicearea = fl_serviceareas.query(where=where_statement).features[0]
            sa_xmax = f_servicearea.attributes['xmax_fips2113_ftintl']
            sa_xmin = f_servicearea.attributes['xmin_fips2113_ftintl']
            sa_ymax = f_servicearea.attributes['ymax_fips2113_ftintl']
            sa_ymin = f_servicearea.attributes['ymin_fips2113_ftintl']
            search_area = {'xmax': sa_xmax, 'xmin': sa_xmin, 'ymax': sa_ymax, 'ymin': sa_ymin}

            # Determine geocoder, default is the 'World Geocoder for ArcGIS'
            if cfg['agencies'][agency]['use_oc_geocoder']:
                geocoder = Geocoder(cfg['geocoders']['oc_geocoder'])
            else:
                geocoder = None

            # Geocode address
            geocode_result = geocode(i['address'], search_extent=search_area, geocoder=geocoder)
            if not geocode_result:
                # Create agency specific default location
                geocode_result = geocode(cfg['agencies'][agency]['default_location'], geocoder=geocoder)
                geocode_success = 'N'
            else:
                geocode_success = 'Y'
                pass

            # Transform coordinates
            x, y = transform(mi_south, web_mercator, geocode_result[0]['location']['x'],
                             geocode_result[0]['location']['y'])
            long, lat = transform(mi_south, wgs84, geocode_result[0]['location']['x'],
                                  geocode_result[0]['location']['y'])

            # Round Lat/Long
            lat = round(lat, 6)
            long = round(long, 6)

            # Convert Lat/Long to USNG
            m = mgrs.MGRS()
            usng_raw = m.toMGRS(lat, long)
            u = str(usng_raw.decode('utf-8'))
            usng = u[0:3] + ' ' + u[3:5] + ' ' + u[5:10] + ' ' + u[10:15]

            # Construct point feature
            xy_dict = {'x': x, 'y': y}
            geocode_xy = Point(xy_dict)

            # Feature layer query to find box alarm areas
            fset_boxalarmareas = fl_boxalarmareas.query(geometry_filter=filters.intersects(geocode_xy))

            # Assign box alarm variables
            boxalarm_fire = None
            boxalarm_medical = None
            boxalarm_wildland = None

            # Loop to populate Box Alarm Variables
            for boxalarmarea in fset_boxalarmareas:
                if boxalarmarea.attributes['BoxAlarmType'] == 'FIRE':
                    boxalarm_fire = boxalarmarea.attributes['BoxAlarmNumber']
                elif boxalarmarea.attributes['BoxAlarmType'] == 'MEDICAL':
                    boxalarm_medical = boxalarmarea.attributes['BoxAlarmNumber']
                elif boxalarmarea.attributes['BoxAlarmType'] == 'WILDLAND':
                    boxalarm_wildland = boxalarmarea.attributes['BoxAlarmNumber']

            # Determine agency district
            fset_firedistricts = fl_firedistricts.query(geometry_filter=filters.intersects(geocode_xy),
                                                        return_geometry=False)
            agency_district = None
            if fset_firedistricts:
                agency_district = fset_firedistricts.features[0].attributes['primarystation']
            else:
                pass

            # Determine shift on duty at time of call
            pattern_start = datetime.strptime(cfg['agencies'][agency]['shift_start_date'], '%m-%d-%Y')
            shift_start = cfg['agencies'][agency]['shift_start_time']
            agency_shift = fireops.kellyshift(i['datetime_call'], pattern_start, shift_start)

            # Query tax parcel layer to get structure data
            fset_taxparcels = fl_taxparcels.query(where="SITEADDRESS LIKE  '" + i['address'] + "'",
                                                  return_geometry=False, result_record_count=1)
            parcel_id = None
            map_index = None
            structure_desc = None
            structure_livingarea = None
            structure_numbbeds = None
            structure_assessvalue = None
            structure_taxvalue = None
            if fset_taxparcels and geocode_success == 'Y':
                parcel_id = fset_taxparcels.features[0].attributes['PIN']
                map_index = fset_taxparcels.features[0].attributes['PIN'][2:4]
                structure_desc = fset_taxparcels.features[0].attributes['STRUCTURE_DESC']
                structure_livingarea = fset_taxparcels.features[0].attributes['LIVING_AREA_SQFT']
                structure_numbbeds = fset_taxparcels.features[0].attributes['NUM_BEDS']
                structure_assessvalue = fset_taxparcels.features[0].attributes['ASSESSEDVALUE']
                structure_taxvalue = fset_taxparcels.features[0].attributes['TAXABLEVALUE']
            else:
                pass

            # Create new feature based on template
            fset_fireincidents = fl_fireincidents.query(result_record_count=1)
            f = deepcopy(fset_fireincidents.features[0])

            # Assign geometry & attributes to new feature
            f.geometry = geocode_xy
            f.attributes['incident_number'] = i['incident_number']
            f.attributes['incident_type_code'] = i['incident_type_code']
            f.attributes['incident_type_desc'] = i['incident_type_desc']
            f.attributes['incident_temp_url'] = i['incident_temp_url']
            f.attributes['agency_code'] = i['agency_code']
            f.attributes['agency_district'] = agency_district
            f.attributes['agency_shift'] = agency_shift
            f.attributes['parcel_id'] = parcel_id
            f.attributes['address'] = i['address']
            f.attributes['location'] = i['location']
            f.attributes['apt_number'] = i['apt_number']
            f.attributes['city_code'] = i['city_code']
            f.attributes['city_desc'] = i['city_desc']
            f.attributes['state'] = ['state']
            f.attributes['map_index'] = map_index
            f.attributes['latitude'] = lat
            f.attributes['longitude'] = long
            f.attributes['usng'] = usng
            f.attributes['low_street'] = i['low_street']
            f.attributes['high_street'] = i['high_street']
            f.attributes['geocode_success'] = geocode_success
            f.attributes['datetime_call'] = i['datetime_call']
            f.attributes['datetime_dispatched'] = None
            f.attributes['datetime_enroute'] = None
            f.attributes['datetime_arrival'] = None
            f.attributes['datetime_clear'] = None
            f.attributes['units_assigned'] = i['incident_units']
            f.attributes['chief_complaint'] = i['chief_complaint']
            f.attributes['proqa_code'] = i['proqa_code']
            f.attributes['proqa_suffix_code'] = i['proqa_code_suf']
            f.attributes['proqa_desc'] = i['proqa_desc']
            f.attributes['proqa_suffix_desc'] = i['proqa_desc_suf']
            f.attributes['boxalarm_fire'] = boxalarm_fire
            f.attributes['boxalarm_medical'] = boxalarm_medical
            f.attributes['boxalarm_wildland'] = boxalarm_wildland
            f.attributes['structure_desc'] = structure_desc
            f.attributes['structure_livingarea'] = structure_livingarea
            f.attributes['structure_numbbeds'] = structure_numbbeds
            f.attributes['structure_assessvalue'] = structure_assessvalue
            f.attributes['structure_taxvalue'] = structure_taxvalue

            # Create empty list for new GIS features
            feature_list = [f]

            # Add features to feature layer
            fl_fireincidents.edit_features(adds=feature_list)
