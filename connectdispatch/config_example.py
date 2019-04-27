"""The config.py module holds global variables"""

import os

"""CAD web service"""
# Web service URLs
cad_url_clemis = 'https://apps.clemis.org/CDEWebService/CDEService.asmx'

# Use CAD web service
use_cad_ws = False

# CAD credentials
cad_user_clemis = 'example_caduser'
cad_pass_clemis = 'example_cadpass'

# Directories
cwd = os.getcwd()
watch_dir = cwd + '/watch'

# Construct a list of dictionaries for each agency
agency_list = []

example_fd = {
    'agency_code': 'example_agency',
    'county_code': 'example_county',
    'state_code': 'example_state',
    'arcgis_portal': 'https://example_org.maps.arcgis.com',
    'arcgis_user': 'example_gisuser',
    'arcgis_pass': 'example_gispass',
}

# agency_list.append(example_fd)  # Uncomment if single agency
# agency_list.extend((example_fd, example_fd2))  # Uncomment if multiple agencies
