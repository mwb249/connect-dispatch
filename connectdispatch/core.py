class Agency(object):
    registry = []

    def __init__(self, agency_code, county_code, state_code, ago_portal, ago_user, ago_pass):
        self.registry.append(self)
        self.agency_code = agency_code
        self.county_code = county_code
        self.state_code = state_code
        self.ago_portal = ago_portal
        self.ago_user = ago_user
        self.ago_pass = ago_pass

    def ago_login(self):
        pass


class Incident(object):

    def __init__(self):
        pass
