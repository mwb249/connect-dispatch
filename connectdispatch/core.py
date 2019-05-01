"""To be completed..."""


class Agency(object):
    registry = []

    def __init__(self, agency_code, county_code, state_code, ago_portal, ago_user, ago_pass, flc_fireincidents,
                 flc_responsedistricts, flc_serviceareas, flc_boxalarmareas):
        self.registry.append(self)
        self.agency_code = agency_code
        self.county_code = county_code
        self.state_code = state_code
        self.ago_portal = ago_portal
        self.ago_user = ago_user
        self.ago_pass = ago_pass
        self.flc_fireincidents = flc_fireincidents
        self.flc_responsedistricts = flc_responsedistricts
        self.flc_serviceareas = flc_serviceareas
        self.flc_boxalarmareas = flc_boxalarmareas


class Incident(object):

    def __init__(self):
        pass
