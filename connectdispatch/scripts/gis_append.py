from connectdispatch import *
from connectdispatch import config
import logging
import os
import pickle
from arcgis.geocoding import geocode
from arcgis.geometry import filters, Point
from pyproj import Proj, transform
import mgrs
from copy import deepcopy

# Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# Define projections
mi_south = Proj(init='epsg:3593', preserve_units=True)  # NAD 1983 StatePlane Michigan South, FIPS 2113 IntlFeet
web_mercator = Proj(init='epsg:3857')  # WGS 1984 Web Mercator Auxiliary Sphere
wgs84 = Proj(init='epsg:4326')  # WGS84

# Open incident_push file
file_incident_push = open('/incident_push/incident_push.p', 'rb')
incident_push = pickle.load(file_incident_push)

for i in incident_push:
    for agency in Agency.registry:
        if i['agency_code'] == agency.agency_code:
            # Construct Web GIS object
            gis = agency.webgis()

            # Construct feature layer objects
            flc_fireincidents = gis.content.get(agency.flc_fireincidents)
            fl_fireincidents = flc_fireincidents.layers[0]

            flc_serviceareas = gis.content.get(agency.flc_serviceareas)
            fl_serviceareas = flc_serviceareas.layers[0]

            flc_responsedistricts = gis.content.get(agency.flc_responsedistricts)
            fl_responsedisctricts = flc_responsedistricts.layers[0]

            flc_boxalarmareas = gis.content.get(agency.flc_boxalarmareas)
            fl_boxalarmareas = flc_boxalarmareas.layers[0]

            # If incident is mutual-aid, find agency_code
            if i['inc_type_code'] == 'MUTAID':
                fset_mutaid_table = fl_mutaid_table.query(where="city_desc LIKE '" + i['inc_city_desc'] + "'")
                f_mutaid = fset_mutaid_table.features[0]
                mutaid_agency_code = f_mutaid.attributes['agency_code']
                pass

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

            # Geocode address
            geocode_result = geocode(i['address'], search_extent=search_area, geocoder=config.oc_geocoder)
            if not geocode_result:
                # Create agency specific default location
                geocode_result = geocode('6500 Citation Dr', geocoder=config.oc_geocoder)
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
            geocode_xy = Point(x=x, y=y)
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
            # Create new feature based on template
            fset_fireincidents = fl_fireincidents.query()
            f = deepcopy(fset_fireincidents.features[0])

            # Create empty list for new GIS features
            feature_list = []

            # Assign geometry & attributes to new feature
            f.geometry = geocode_xy
            f.attributes['incident_number'] = i['incident_number']
            f.attributes['incident_type_code'] = i['incident_type_code']
            f.attributes['incident_type_desc'] = i['incident_type_desc']
            f.attributes['incident_temp_url'] = None
            f.attributes['agency_code'] = i['agency_code']
            f.attributes['agency_district'] = None
            f.attributes['address'] = i['address']
            f.attributes['location'] = None
            f.attributes['apt_number'] = i['apt_number']
            f.attributes['city_code'] = i['city_code']
            f.attributes['city_desc'] = i['city_desc']
            f.attributes['state'] = ['state']
            f.attributes['map_index'] = i['map_index']
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

            # Append feature to list
            feature_list.append(f)

            # Add features to feature layer
        fl_fireincidents.edit_features(adds=feature_list)
