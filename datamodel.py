import datetime
from google.appengine.ext import ndb
from google.appengine.api import users

class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty(required=True)
    description = ndb.TextProperty(required=True)
    impact = ndb.TextProperty(required=True)
    documentation = ndb.TextProperty(required=True)
    rationale  = ndb.TextProperty(required=True)
    implementation_steps = ndb.TextProperty(required=True)    
    # tests_conducted  = ndb.TextProperty(required=True)
    # risks  = ndb.TextProperty(required=True)
    # backout_plan  = ndb.TextProperty(required=True)
    # communication_plan  = ndb.TextProperty(required=True)
    # layman_description  = ndb.TextProperty(required=True)
    # verification_steps  = ndb.TextProperty(required=True)
    # status = ndb.StringProperty(required=True,
    #                            choices=set(["approved", "awaiting approval", "complete"]))
    # approver = ndb.StringProperty(required=True)
    # sync_to_helpdesk  = ndb.BooleanProperty(required=True)
     priority = ndb.StringProperty(required=True,
                                choices=set(["sensitive", "low", "none"]))
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    # timezone = ndb.StringProperty(required=True,
    #                              choices-set([...]))
    # start_time = DateTimeProperty()
    # end_time = DateTimeProperty()
    # blackout_duration = ndb.StringProperty()
    # group = ndb.StringProperty()
    # cc_list = ndb.ListProperty(ndb.StringProperty())
    technician = ndb.StringProperty()
    # peer_reviewer = ndb.StringProperty()
    # services_affected = ndb.StringProperty()
    # locations_affected = ndb.StringProperty()
    # components = ...
    # users_affected = ndb.StringProperty(required=True,
    #                            choices=set(["large > 1000" ...]))
    # region_affected_low_impact_time = ndb.BooleanProperty()
    # worklog = ...
    # audit_trail = ...
                                       
                                   

    
    
